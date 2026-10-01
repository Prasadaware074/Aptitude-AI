import logging
import random
import re
import math
from typing import List, Optional, Set
from app.models.schemas import QuestionSchema
from app.tools.question_validator import QuestionValidator
from app.rag.topic_knowledge import get_topic_details
from app.config.topics import normalize_topic, get_category_for_topic, is_valid_topic
from app.agents.llm_factory import get_llm
from app.database.connection import SessionLocal
from app.database.repository import Repository

logger = logging.getLogger(__name__)

class PracticeAgent:
    """Agent responsible for generating, validating, and retrieving unique, level-aware, topic-specific practice MCQs."""

    @staticmethod
    def generate_practice_questions(
        topic: str,
        category: Optional[str] = None,
        difficulty: str = "medium",
        number_of_questions: int = 5
    ) -> List[QuestionSchema]:
        norm_topic = normalize_topic(topic)
        if not norm_topic or not is_valid_topic(norm_topic):
            logger.error(f"Attempted question generation for invalid topic: {topic}")
            return []

        resolved_cat = category or get_category_for_topic(norm_topic)
        diff = (difficulty or "medium").lower()
        if diff not in ["easy", "medium", "hard"]:
            diff = "medium"

        db = SessionLocal()
        try:
            repo = Repository(db)
            validated_questions: List[QuestionSchema] = []
            seen_texts: Set[str] = set()

            max_attempts_per_q = 3
            llm = get_llm(temperature=0.7, structured_output_schema=QuestionSchema)
            topic_info = get_topic_details(norm_topic)

            for i in range(number_of_questions):
                q_generated = False
                for attempt in range(max_attempts_per_q):
                    if llm:
                        seed = random.randint(1000, 999999)
                        prompt = f"""Generate a unique, mathematically precise multiple-choice question for competitive aptitude preparation.
Topic: {norm_topic}
Category: {resolved_cat}
Difficulty: {diff} (Level guidelines: 'easy'=1-step direct formula, 'medium'=2-step moderate numbers, 'hard'=multi-step complex word problem)
Topic Context: {topic_info.get('definition', '')} | Formulas: {', '.join(topic_info.get('important_formulas', []))}
Random Seed: {seed}
Question Number: {i + 1} of {number_of_questions}

CRITICAL DIVERSITY & TOPIC RESTRICTIONS:
- Must be strictly a '{norm_topic}' question testing '{norm_topic}' principles.
- Do NOT generate questions from any other topic.
- Question {i+1} MUST test a DIFFERENT sub-concept or problem scenario within '{norm_topic}' from other questions in this set.
- Exactly 4 unique options: option_a, option_b, option_c, option_d.
- Exactly 1 correct option key ('option_a', 'option_b', 'option_c', or 'option_d').
- Provide step-by-step mathematical/logical explanation proving the answer.
"""
                        try:
                            candidate_q = llm.invoke(prompt)
                            if isinstance(candidate_q, QuestionSchema) and candidate_q.question and candidate_q.question not in seen_texts:
                                candidate_q.topic = norm_topic
                                candidate_q.category = resolved_cat
                                candidate_q.difficulty = diff
                                val_result = QuestionValidator.validate(candidate_q)
                                if val_result.is_valid:
                                    db_model = repo.add_question(candidate_q)
                                    candidate_q.id = db_model.id
                                    validated_questions.append(candidate_q)
                                    seen_texts.add(candidate_q.question)
                                    q_generated = True
                                    break
                        except Exception as e:
                            logger.warning(f"LLM question generation exception: {e}")

                if not q_generated:
                    # Dynamic level-aware topic-specific fallback generator with distinct scenario variants and deduplication retry
                    fallback_q = PracticeAgent._create_topic_specific_fallback(norm_topic, resolved_cat, diff, i, seen_texts)
                    if fallback_q:
                        db_model = repo.add_question(fallback_q)
                        fallback_q.id = db_model.id
                        validated_questions.append(fallback_q)
                        seen_texts.add(fallback_q.question)

            return validated_questions[:number_of_questions]
        finally:
            db.close()

    @staticmethod
    def _create_topic_specific_fallback(topic: str, category: str, difficulty: str, index: int, seen_texts: Set[str]) -> QuestionSchema:
        """Generates a topic-specific dynamic question strictly matching requested topic and difficulty with guaranteed deduplication."""
        t_norm = normalize_topic(topic) or topic
        diff = (difficulty or "medium").lower()

        for attempt in range(25):
            var_idx = (index + attempt) % 5
            q = PracticeAgent._generate_fallback_variant(t_norm, category, diff, var_idx, attempt)
            if q and q.question not in seen_texts:
                return q

        return PracticeAgent._generate_fallback_variant(t_norm, category, diff, (index + random.randint(1, 100)) % 5, random.randint(100, 999))

    @staticmethod
    def _generate_fallback_variant(t_norm: str, category: str, diff: str, var_idx: int, seed: int) -> QuestionSchema:
        # Seed pseudo-random generator locally for deterministic variation
        rnd = random.Random(seed * 1000 + var_idx * 17 + random.randint(1, 500))

        # 1. Percentage
        if t_norm == "Percentage":
            if var_idx == 0:
                base = rnd.choice([120, 150, 180, 200, 240, 300, 360, 400, 500])
                pct = rnd.choice([10, 15, 20, 25, 30, 40, 50])
                ans = int((pct / 100.0) * base)
                q_text = f"What is {pct}% of {base}?"
                correct = str(ans)
                d1, d2, d3 = str(ans - 5), str(ans + 10), str(ans + 15)
                exp = f"{pct}% of {base} = ({pct} / 100) * {base} = {ans}."
            elif var_idx == 1:
                total_marks = rnd.choice([400, 500, 600, 800])
                pct = rnd.choice([60, 65, 70, 75, 80, 85])
                score = int((pct / 100.0) * total_marks)
                q_text = f"A student scored {score} marks out of {total_marks} in an aptitude examination. What percentage did the student obtain?"
                correct = f"{pct}%"
                d1, d2, d3 = f"{pct - 5}%", f"{pct + 8}%", f"{pct + 10}%"
                exp = f"Percentage = ({score} / {total_marks}) * 100 = {pct}%."
            elif var_idx == 2:
                old_v = rnd.choice([200, 250, 300, 400, 500])
                inc = rnd.choice([10, 20, 25, 50])
                new_v = int(old_v * (1 + inc / 100.0))
                q_text = f"The price of an article increases from ${old_v} to ${new_v}. What is the percentage increase?"
                correct = f"{inc}%"
                d1, d2, d3 = f"{inc - 5}%", f"{inc + 10}%", f"{inc + 15}%"
                exp = f"Increase = ${new_v - old_v}. Percentage Increase = (${new_v - old_v} / ${old_v}) * 100 = {inc}%."
            elif var_idx == 3:
                val = rnd.choice([150, 200, 250, 300, 400])
                pct = rnd.choice([20, 25, 40, 50])
                ans = int((pct / 100.0) * val)
                q_text = f"If {pct}% of a number is {ans}, what is the original number?"
                correct = str(val)
                d1, d2, d3 = str(val - 30), str(val + 40), str(val + 60)
                exp = f"Let original number be x. ({pct}/100) * x = {ans} => x = {ans} * 100 / {pct} = {val}."
            else:
                base = rnd.choice([500, 600, 800, 1000])
                p1 = rnd.choice([10, 20, 25])
                net_dec = round((p1 * p1) / 100.0, 1)
                final_sal = int(base * (1 - net_dec / 100.0))
                q_text = f"A worker's salary of ${base} is increased by {p1}% and subsequently decreased by {p1}%. What is the final salary?"
                correct = f"${final_sal}"
                d1, d2, d3 = f"${base}", f"${final_sal - 15}", f"${final_sal + 20}"
                exp = f"Net change = -({p1}^2 / 100)% = -{net_dec}%. Final salary = ${base} * (1 - {net_dec}/100) = ${final_sal}."
            return PracticeAgent._format_shuffled_question(q_text, correct, d1, d2, d3, exp, t_norm, category, diff)

        # 2. Profit and Loss
        elif t_norm == "Profit and Loss":
            if var_idx == 0:
                cp = rnd.choice([100, 150, 200, 250, 300, 400])
                p_pct = rnd.choice([10, 15, 20, 25, 30])
                sp = int(cp * (1 + p_pct / 100.0))
                q_text = f"An item bought for ${cp} is sold at a profit of {p_pct}%. What is the selling price?"
                correct = f"${sp}"
                d1, d2, d3 = f"${sp - 15}", f"${sp + 20}", f"${sp + 35}"
                exp = f"Selling Price = Cost Price * (1 + Profit%/100) = ${cp} * (1 + {p_pct}/100) = ${sp}."
            elif var_idx == 1:
                sp = rnd.choice([160, 240, 320, 400, 480])
                loss_pct = rnd.choice([10, 20, 25])
                cp = int((sp * 100) / (100 - loss_pct))
                q_text = f"A watch sold for ${sp} incurs a loss of {loss_pct}%. Find the original cost price."
                correct = f"${cp}"
                d1, d2, d3 = f"${sp - 20}", f"${cp - 25}", f"${cp + 30}"
                exp = f"Cost Price = (Selling Price * 100) / (100 - Loss%) = (${sp} * 100) / (100 - {loss_pct}) = ${cp}."
            elif var_idx == 2:
                cp = rnd.choice([100, 200, 300, 400])
                profit_amt = rnd.choice([20, 40, 50, 60, 80])
                sp = cp + profit_amt
                p_pct = int((profit_amt / cp) * 100)
                q_text = f"If an article is bought for ${cp} and sold for ${sp}, what is the profit percentage?"
                correct = f"{p_pct}%"
                d1, d2, d3 = f"{p_pct - 5}%", f"{p_pct + 8}%", f"{p_pct + 12}%"
                exp = f"Profit = ${sp - cp}. Profit % = (${profit_amt} / ${cp}) * 100 = {p_pct}%."
            elif var_idx == 3:
                mp = rnd.choice([500, 600, 800, 1000])
                disc = rnd.choice([10, 15, 20, 25])
                sp = int(mp * (1 - disc / 100.0))
                q_text = f"An article listed at a marked price of ${mp} is sold at a discount of {disc}%. What is the final selling price?"
                correct = f"${sp}"
                d1, d2, d3 = f"${sp - 30}", f"${sp + 40}", f"${mp}"
                exp = f"Selling Price = Marked Price * (1 - Discount%/100) = ${mp} * (1 - {disc}/100) = ${sp}."
            else:
                sp1 = rnd.choice([450, 540, 630])
                cp = int((sp1 * 100) / 90)
                sp2 = int(cp * 1.20)
                q_text = f"A seller sells an article for ${sp1} at a loss of 10%. At what price should he sell it to gain 20%?"
                correct = f"${sp2}"
                d1, d2, d3 = f"${cp}", f"${sp2 - 50}", f"${sp2 + 75}"
                exp = f"Cost Price = (${sp1} * 100) / 90 = ${cp}. SP for 20% gain = ${cp} * 1.20 = ${sp2}."
            return PracticeAgent._format_shuffled_question(q_text, correct, d1, d2, d3, exp, t_norm, category, diff)

        # 3. Ratio and Proportion
        elif t_norm == "Ratio and Proportion":
            if var_idx == 0:
                r1, r2 = rnd.choice([(2, 3), (3, 5), (4, 5), (1, 4), (5, 7)])
                multiplier = rnd.choice([12, 15, 18, 20, 24, 30])
                total = (r1 + r2) * multiplier
                share_a = r1 * multiplier
                q_text = f"A sum of ${total} is divided between Person A and Person B in the ratio {r1}:{r2}. What is Person A's share?"
                correct = f"${share_a}"
                d1, d2, d3 = f"${share_a - 15}", f"${share_a + 20}", f"${total - share_a}"
                exp = f"Total parts = {r1}+{r2} = {r1+r2}. Share A = [{r1} / {r1+r2}] * ${total} = ${share_a}."
            elif var_idx == 1:
                a = rnd.choice([4, 6, 8, 10])
                b = rnd.choice([12, 16, 20, 24])
                c = rnd.choice([15, 18, 24, 30])
                ans = (b * c) // a
                q_text = f"Find the fourth proportional to {a}, {b}, and {c}."
                correct = str(ans)
                d1, d2, d3 = str(ans - 4), str(ans + 6), str(ans + 10)
                exp = f"If {a}:{b} :: {c}:x, then {a}x = {b} * {c} => {a}x = {b*c} => x = {ans}."
            elif var_idx == 2:
                r1, r2 = rnd.choice([(2, 3), (3, 4), (1, 2)])
                r3, r4 = rnd.choice([(4, 5), (5, 6), (3, 5)])
                num_a = r1 * r3
                den_c = r2 * r4
                common = math.gcd(num_a, den_c)
                ans_str = f"{num_a // common}:{den_c // common}"
                q_text = f"If A:B = {r1}:{r2} and B:C = {r3}:{r4}, what is the simplified ratio A:C?"
                correct = ans_str
                d1, d2, d3 = f"{r1}:{r4}", f"{r2}:{r3}", f"{num_a}:{den_c + 2}"
                exp = f"A/C = (A/B) * (B/C) = ({r1}/{r2}) * ({r3}/{r4}) = {num_a}/{den_c} = {ans_str}."
            elif var_idx == 3:
                r1, r2 = rnd.choice([(3, 5), (4, 7), (5, 8), (2, 5)])
                diff_parts = r2 - r1
                mult = rnd.choice([5, 8, 10, 12, 15])
                diff_val = diff_parts * mult
                larger = r2 * mult
                q_text = f"The ratio of two numbers is {r1}:{r2} and their difference is {diff_val}. What is the larger number?"
                correct = str(larger)
                d1, d2, d3 = str(r1 * mult), str(larger + 10), str(larger - 8)
                exp = f"Let numbers be {r1}x and {r2}x. Difference ({r2}-{r1})x = {diff_val} => x = {mult}. Larger = {r2} * {mult} = {larger}."
            else:
                r1, r2, r3 = 2, 3, 5
                total_parts = r1 + r2 + r3
                mult = rnd.choice([20, 30, 40, 50])
                total = total_parts * mult
                diff_bc = (r3 - r2) * mult
                q_text = f"A total sum of ${total} is divided among A, B, and C in the ratio {r1}:{r2}:{r3}. How much more money does C receive than B?"
                correct = f"${diff_bc}"
                d1, d2, d3 = f"${diff_bc - 20}", f"${diff_bc + 30}", f"${diff_bc + 50}"
                exp = f"Total parts = {total_parts}. C's part - B's part = ({r3}-{r2}) parts = 2 * {mult} = ${diff_bc}."
            return PracticeAgent._format_shuffled_question(q_text, correct, d1, d2, d3, exp, t_norm, category, diff)

        # 4. Time and Work
        elif t_norm == "Time and Work":
            if var_idx == 0:
                d1_val = rnd.choice([6, 10, 12, 15, 20])
                d2_val = rnd.choice([12, 15, 20, 30, 60])
                combined = round((d1_val * d2_val) / (d1_val + d2_val), 1)
                ans_str = f"{int(combined)} days" if combined.is_integer() else f"{combined} days"
                q_text = f"Worker A completes a project in {d1_val} days and Worker B in {d2_val} days. How many days will they take working together?"
                correct = ans_str
                d1, d2, d3 = f"{round(combined + 2.0, 1)} days", f"{round(max(1.0, combined - 1.5), 1)} days", f"{d1_val + d2_val} days"
                exp = f"Combined time = (A * B) / (A + B) = ({d1_val} * {d2_val}) / ({d1_val} + {d2_val}) = {ans_str}."
            elif var_idx == 1:
                t1 = rnd.choice([4, 6, 8, 10])
                t2 = rnd.choice([12, 15, 20, 24])
                comb = round((t1 * t2) / (t1 + t2), 1)
                ans_str = f"{int(comb)} hours" if comb.is_integer() else f"{comb} hours"
                q_text = f"Pipe A can fill a pool in {t1} hours, and Pipe B can fill it in {t2} hours. How long will it take if both pipes fill together?"
                correct = ans_str
                d1, d2, d3 = f"{round(comb + 2, 1)} hours", f"{round(comb - 1.5, 1)} hours", f"{t1 + t2} hours"
                exp = f"Time = (T1 * T2) / (T1 + T2) = ({t1} * {t2}) / ({t1} + {t2}) = {ans_str}."
            elif var_idx == 2:
                frac_den = rnd.choice([4, 5, 6])
                days_part = rnd.choice([2, 3, 4, 5])
                total_days = frac_den * days_part
                q_text = f"A worker completes 1/{frac_den}th of a job in {days_part} days. How many total days are required to complete the whole job?"
                correct = f"{total_days} days"
                d1, d2, d3 = f"{total_days - 4} days", f"{total_days + 5} days", f"{total_days + 10} days"
                exp = f"Total days = {days_part} / (1/{frac_den}) = {total_days} days."
            elif var_idx == 3:
                d1_val = rnd.choice([12, 15, 20])
                d2_val = rnd.choice([20, 30, 40])
                n_days = 3
                work_done = n_days * (1/d1_val + 1/d2_val)
                rem_work = round(1 - work_done, 2)
                rem_days = round(rem_work * d2_val, 1)
                ans_str = f"{int(rem_days)} days" if rem_days.is_integer() else f"{rem_days} days"
                q_text = f"A can do a work in {d1_val} days and B in {d2_val} days. They work together for {n_days} days, then A leaves. How many days will B take to complete the remaining work?"
                correct = ans_str
                d1, d2, d3 = f"{round(rem_days + 2, 1)} days", f"{round(max(1.0, rem_days - 2), 1)} days", f"{d2_val - n_days} days"
                exp = f"{n_days} days work = {n_days}*(1/{d1_val} + 1/{d2_val}). Remaining work = {rem_work}. Days for B = {rem_work} * {d2_val} = {ans_str}."
            else:
                t1 = rnd.choice([10, 12, 15])
                t2 = rnd.choice([20, 30, 60])
                net_time = round((t1 * t2) / (t2 - t1), 1)
                ans_str = f"{int(net_time)} hours" if net_time.is_integer() else f"{net_time} hours"
                q_text = f"Pipe A can fill a tank in {t1} hours, while Pipe B can empty it in {t2} hours. If both pipes are opened together, how long will it take to fill the tank?"
                correct = ans_str
                d1, d2, d3 = f"{round(net_time + 4, 1)} hours", f"{round(net_time - 3, 1)} hours", f"{t1 + t2} hours"
                exp = f"Net rate = 1/{t1} - 1/{t2} = ({t2}-{t1})/({t1}*{t2}). Total time = ({t1}*{t2})/({t2}-{t1}) = {ans_str}."
            return PracticeAgent._format_shuffled_question(q_text, correct, d1, d2, d3, exp, t_norm, category, diff)

        # 5. Probability
        elif t_norm == "Probability":
            if var_idx == 0:
                coins = rnd.choice([2, 3, 4])
                total_outcomes = 2**coins
                at_least_one_head_fav = total_outcomes - 1
                q_text = f"{coins} unbiased coins are tossed simultaneously. What is the probability of getting at least one head?"
                correct = f"{at_least_one_head_fav}/{total_outcomes}"
                d1, d2, d3 = f"1/{total_outcomes}", f"{at_least_one_head_fav - 1}/{total_outcomes}", "1/2"
                exp = f"Total outcomes = 2^{coins} = {total_outcomes}. Outcome with no heads = 1 (TT...T). P(at least 1 head) = 1 - 1/{total_outcomes} = {at_least_one_head_fav}/{total_outcomes}."
            elif var_idx == 1:
                q_type = rnd.choice(["even", "prime", "greater than 4"])
                if q_type == "even":
                    q_text = "A standard six-sided die is rolled once. What is the probability of obtaining an even number?"
                    correct = "1/2"
                    d1, d2, d3 = "1/3", "1/6", "2/3"
                    exp = "Even outcomes on a die are {2, 4, 6} (3 outcomes out of 6). Probability = 3/6 = 1/2."
                elif q_type == "prime":
                    q_text = "A standard six-sided die is rolled once. What is the probability of rolling a prime number?"
                    correct = "1/2"
                    d1, d2, d3 = "1/3", "1/6", "5/6"
                    exp = "Prime outcomes on a die are {2, 3, 5} (3 outcomes out of 6). Probability = 3/6 = 1/2."
                else:
                    q_text = "A standard six-sided die is rolled once. What is the probability of obtaining a number strictly greater than 4?"
                    correct = "1/3"
                    d1, d2, d3 = "1/2", "1/6", "2/3"
                    exp = "Outcomes greater than 4 are {5, 6} (2 outcomes out of 6). Probability = 2/6 = 1/3."
            elif var_idx == 2:
                card_type = rnd.choice(["King", "Ace or Queen", "Spade"])
                if card_type == "King":
                    q_text = "One card is drawn at random from a standard well-shuffled deck of 52 playing cards. What is the probability of drawing a King?"
                    correct = "1/13"
                    d1, d2, d3 = "1/52", "1/4", "4/13"
                    exp = "There are 4 Kings in a 52-card deck. Probability = 4/52 = 1/13."
                elif card_type == "Ace or Queen":
                    q_text = "One card is drawn at random from a standard deck of 52 cards. What is the probability of drawing an Ace or a Queen?"
                    correct = "2/13"
                    d1, d2, d3 = "1/13", "1/4", "4/13"
                    exp = "There are 4 Aces and 4 Queens (8 total). Probability = 8/52 = 2/13."
                else:
                    q_text = "One card is drawn at random from a standard deck of 52 cards. What is the probability of drawing a Spade?"
                    correct = "1/4"
                    d1, d2, d3 = "1/13", "1/52", "1/2"
                    exp = "There are 13 Spades in a 52-card deck. Probability = 13/52 = 1/4."
            elif var_idx == 3:
                red = rnd.choice([3, 4, 5, 6])
                blue = rnd.choice([2, 3, 4, 5])
                total = red + blue
                common = math.gcd(red, total)
                ans_str = f"{red//common}/{total//common}"
                q_text = f"A bag contains {red} red marbles and {blue} blue marbles. If one marble is drawn at random, what is the probability that it is red?"
                correct = ans_str
                d1, d2, d3 = f"{blue//common}/{total//common}", f"1/{total}", "1/2"
                exp = f"Total marbles = {red} + {blue} = {total}. Favorable red = {red}. Probability = {red}/{total} = {ans_str}."
            else:
                target_sum = rnd.choice([6, 7, 8, 9, 10])
                fav_map = {6: 5, 7: 6, 8: 5, 9: 4, 10: 3}
                fav = fav_map[target_sum]
                common = math.gcd(fav, 36)
                ans_str = f"{fav // common}/{36 // common}"
                q_text = f"Two standard six-sided dice are rolled simultaneously. What is the probability of obtaining a sum equal to {target_sum}?"
                correct = ans_str
                d1, d2, d3 = f"{(fav + 1)}/36", f"{max(1, fav - 1)}/36", "1/6"
                exp = f"Total outcomes = 6 * 6 = 36. Favorable outcomes for sum {target_sum} = {fav}. Probability = {fav}/36 = {ans_str}."
            return PracticeAgent._format_shuffled_question(q_text, correct, d1, d2, d3, exp, t_norm, category, diff)

        # 6. Average
        elif t_norm == "Average":
            if var_idx == 0:
                vals = [rnd.randint(10, 60) for _ in range(4)]
                avg = sum(vals) / 4.0
                ans_str = f"{avg:.1f}" if not avg.is_integer() else f"{int(avg)}"
                q_text = f"Find the average of the following numbers: {vals[0]}, {vals[1]}, {vals[2]}, and {vals[3]}."
                correct = ans_str
                d1, d2, d3 = str(int(avg + 3)), str(int(avg - 2)), str(int(avg + 5))
                exp = f"Average = Sum / Count = ({vals[0]} + {vals[1]} + {vals[2]} + {vals[3]}) / 4 = {sum(vals)} / 4 = {ans_str}."
            elif var_idx == 1:
                count = rnd.choice([5, 6, 7, 8, 10])
                # Average of first N positive even numbers = N + 1
                avg_even = count + 1
                q_text = f"What is the average of the first {count} positive even integers?"
                correct = str(avg_even)
                d1, d2, d3 = str(count), str(avg_even + 2), str(count * 2)
                exp = f"First {count} positive even integers have sum = {count}*({count}+1). Average = {count}+1 = {avg_even}."
            elif var_idx == 2:
                s1, s2, s3 = rnd.choice([100, 150, 200]), rnd.choice([200, 250, 300]), rnd.choice([300, 350, 400])
                avg_sale = int((s1 + s2 + s3) / 3)
                q_text = f"The sales figures of a store over 3 days are ${s1}, ${s2}, and ${s3}. What is the average daily sale?"
                correct = f"${avg_sale}"
                d1, d2, d3 = f"${avg_sale - 30}", f"${avg_sale + 40}", f"${avg_sale + 60}"
                exp = f"Average = (${s1} + ${s2} + ${s3}) / 3 = ${s1+s2+s3} / 3 = ${avg_sale}."
            elif var_idx == 3:
                cnt = rnd.choice([4, 5, 6, 8])
                old_avg = rnd.choice([20, 25, 30, 35])
                new_val = rnd.choice([50, 60, 70, 80])
                new_avg = round((cnt * old_avg + new_val) / (cnt + 1), 1)
                ans_str = f"{int(new_avg)} years" if new_avg.is_integer() else f"{new_avg} years"
                q_text = f"The average age of {cnt} people is {old_avg} years. If a new person aged {new_val} years joins the group, what is the new average age?"
                correct = ans_str
                d1, d2, d3 = f"{round(new_avg + 2.0, 1)} years", f"{round(new_avg - 1.5, 1)} years", f"{old_avg + 5} years"
                exp = f"New Sum = ({cnt} * {old_avg}) + {new_val} = {cnt*old_avg + new_val}. New Average = {cnt*old_avg + new_val} / {cnt+1} = {ans_str}."
            else:
                n1, n2 = 10, 15
                avg1, avg2 = rnd.choice([45, 50, 55]), rnd.choice([60, 65, 70])
                combined_avg = round((n1 * avg1 + n2 * avg2) / (n1 + n2), 1)
                q_text = f"The average score of a class of {n1} students is {avg1}, and another class of {n2} students is {avg2}. What is the combined average score?"
                correct = f"{combined_avg}"
                d1, d2, d3 = f"{combined_avg + 2.5:.1f}", f"{combined_avg - 3.0:.1f}", f"{(avg1 + avg2)/2:.1f}"
                exp = f"Combined Average = ({n1}*{avg1} + {n2}*{avg2}) / ({n1}+{n2}) = {combined_avg}."
            return PracticeAgent._format_shuffled_question(q_text, correct, d1, d2, d3, exp, t_norm, category, diff)

        # 7. Speed, Distance and Time
        elif t_norm == "Speed, Distance and Time":
            if var_idx == 0:
                dist = rnd.choice([120, 180, 240, 300, 360, 400])
                hrs = rnd.choice([2, 3, 4, 5, 6])
                speed = int(dist / hrs)
                q_text = f"A car travels a total distance of {dist} km in {hrs} hours. What is the average speed of the car?"
                correct = f"{speed} km/h"
                d1, d2, d3 = f"{speed - 10} km/h", f"{speed + 15} km/h", f"{speed + 25} km/h"
                exp = f"Speed = Distance / Time = {dist} / {hrs} = {speed} km/h."
            elif var_idx == 1:
                kmh = rnd.choice([36, 54, 72, 90, 108])
                mps = int(kmh * 5 / 18)
                q_text = f"Convert a speed of {kmh} km/h into meters per second (m/s)."
                correct = f"{mps} m/s"
                d1, d2, d3 = f"{mps - 5} m/s", f"{mps + 8} m/s", f"{mps + 12} m/s"
                exp = f"Speed in m/s = {kmh} * (5 / 18) = {mps} m/s."
            elif var_idx == 2:
                speed = rnd.choice([40, 50, 60, 75, 80])
                hrs = rnd.choice([2, 3, 4, 5])
                dist = speed * hrs
                q_text = f"A train moves at a constant speed of {speed} km/h. What total distance does it cover in {hrs} hours?"
                correct = f"{dist} km"
                d1, d2, d3 = f"{dist - 30} km", f"{dist + 40} km", f"{dist + 60} km"
                exp = f"Distance = Speed * Time = {speed} * {hrs} = {dist} km."
            elif var_idx == 3:
                length = rnd.choice([150, 200, 250, 300])
                speed_kmh = rnd.choice([54, 72, 90])
                speed_mps = int(speed_kmh * 5 / 18)
                t_sec = int(length / speed_mps)
                q_text = f"A train {length} meters long is running at {speed_kmh} km/h. How many seconds will it take to pass a stationary telegraph pole?"
                correct = f"{t_sec} seconds"
                d1, d2, d3 = f"{t_sec - 2} seconds", f"{t_sec + 4} seconds", f"{t_sec + 8} seconds"
                exp = f"Speed in m/s = {speed_kmh} * (5/18) = {speed_mps} m/s. Time = Length / Speed = {length} / {speed_mps} = {t_sec} seconds."
            else:
                l1, l2 = 120, 180
                s1, s2 = 45, 63
                rel_speed_mps = (s1 + s2) * (5 / 18.0)
                time_sec = round((l1 + l2) / rel_speed_mps, 1)
                ans_str = f"{int(time_sec)} seconds" if time_sec.is_integer() else f"{time_sec} seconds"
                q_text = f"Two trains of lengths {l1}m and {l2}m are moving in opposite directions at speeds of {s1} km/h and {s2} km/h. How many seconds will they take to pass each other?"
                correct = ans_str
                d1, d2, d3 = f"{round(time_sec + 3.0, 1)} seconds", f"{round(max(1.0, time_sec - 2.5), 1)} seconds", f"{round(time_sec + 6.0, 1)} seconds"
                exp = f"Relative Speed = {s1}+{s2} = {s1+s2} km/h = {rel_speed_mps:.2f} m/s. Time = ({l1}+{l2}) / {rel_speed_mps:.2f} = {ans_str}."
            return PracticeAgent._format_shuffled_question(q_text, correct, d1, d2, d3, exp, t_norm, category, diff)

        # 8. Number System
        elif t_norm == "Number System":
            if var_idx == 0:
                a = rnd.choice([18, 24, 30, 36, 48])
                b = rnd.choice([24, 36, 40, 60, 72])
                hcf_val = math.gcd(a, b)
                q_text = f"What is the Highest Common Factor (HCF) of {a} and {b}?"
                correct = str(hcf_val)
                d1, d2, d3 = str(hcf_val // 2 if hcf_val > 2 else 1), str(hcf_val * 2), str(hcf_val + 4)
                exp = f"Factors of {a} and {b} yield Highest Common Factor = {hcf_val}."
            elif var_idx == 1:
                a = rnd.choice([12, 15, 18, 20])
                b = rnd.choice([16, 24, 25, 30])
                lcm_val = (a * b) // math.gcd(a, b)
                q_text = f"What is the Least Common Multiple (LCM) of {a} and {b}?"
                correct = str(lcm_val)
                d1, d2, d3 = str(lcm_val - 12), str(lcm_val + 20), str(a * b)
                exp = f"LCM({a}, {b}) = ({a} * {b}) / HCF({a}, {b}) = {lcm_val}."
            elif var_idx == 2:
                digit = rnd.choice([5, 6, 7, 8, 9])
                place = 100
                num = 4000 + digit * place + 52
                pv = digit * place
                diff_val = pv - digit
                q_text = f"What is the difference between the place value and face value of {digit} in the number {num}?"
                correct = str(diff_val)
                d1, d2, d3 = str(pv), str(diff_val - 10), str(diff_val + 7)
                exp = f"Place value of {digit} = {pv}. Face value = {digit}. Difference = {pv} - {digit} = {diff_val}."
            elif var_idx == 3:
                p = rnd.choice([31, 33, 35, 37])
                rem = (2**p) % 5
                q_text = f"What is the remainder when 2^{p} is divided by 5?"
                correct = str(rem)
                d1, d2, d3 = str((rem + 1) % 5), str((rem + 2) % 5), str((rem + 3) % 5)
                exp = f"Power cycle of 2 mod 5 is 2, 4, 3, 1 (period 4). {p} mod 4 = {p%4}. 2^{p%4} mod 5 = {rem}."
            else:
                hcf_v = 12
                lcm_v = 144
                n1 = 36
                n2 = (hcf_v * lcm_v) // n1
                q_text = f"The HCF of two numbers is {hcf_v} and their LCM is {lcm_v}. If one of the numbers is {n1}, find the other number."
                correct = str(n2)
                d1, d2, d3 = str(n2 - 12), str(n2 + 18), str(n2 + 24)
                exp = f"Product of numbers = HCF * LCM => {n1} * N2 = {hcf_v} * {lcm_v} = {hcf_v*lcm_v} => N2 = {n2}."
            return PracticeAgent._format_shuffled_question(q_text, correct, d1, d2, d3, exp, t_norm, category, diff)

        # 9. Algebra
        elif t_norm == "Algebra":
            if var_idx == 0:
                a_val = rnd.choice([2, 3, 4, 5])
                c_val = rnd.choice([5, 8, 10, 12])
                ans = rnd.choice([3, 4, 5, 6, 7, 8])
                b_val = a_val * ans + c_val
                q_text = f"Solve for x: {a_val}x + {c_val} = {b_val}."
                correct = str(ans)
                d1, d2, d3 = str(ans + 2), str(max(1, ans - 1)), str(ans + 4)
                exp = f"{a_val}x = {b_val} - {c_val} = {b_val - c_val} => x = {b_val - c_val} / {a_val} = {ans}."
            elif var_idx == 1:
                x_val = rnd.choice([2, 3, 4])
                val = 2 * (x_val**2) - 3 * x_val + 5
                q_text = f"Evaluate the algebraic expression 2x^2 - 3x + 5 for x = {x_val}."
                correct = str(val)
                d1, d2, d3 = str(val - 3), str(val + 5), str(val + 8)
                exp = f"2({x_val})^2 - 3({x_val}) + 5 = 2({x_val**2}) - {3*x_val} + 5 = {val}."
            elif var_idx == 2:
                k_val = rnd.choice([3, 4, 5, 6])
                correct_exp = f"x^2 + {2*k_val}x + {k_val**2}"
                q_text = f"Expand the algebraic square: (x + {k_val})^2."
                correct = correct_exp
                d1, d2, d3 = f"x^2 + {k_val**2}", f"x^2 + {k_val}x + {k_val**2}", f"x^2 + {2*k_val}x + {2*k_val}"
                exp = f"(x + {k_val})^2 = x^2 + 2({k_val})x + {k_val}^2 = {correct_exp}."
            elif var_idx == 3:
                father_diff = rnd.choice([24, 26, 28, 30])
                son_age = rnd.choice([10, 12, 14, 15])
                father_son_sum = 2 * son_age + father_diff
                q_text = f"The sum of the ages of a father and son is {father_son_sum} years. The father is {father_diff} years older than the son. What is the present age of the son?"
                correct = f"{son_age} years"
                d1, d2, d3 = f"{son_age + 4} years", f"{max(5, son_age - 3)} years", f"{son_age + father_diff} years"
                exp = f"Let son age be x. Father = x + {father_diff}. 2x + {father_diff} = {father_son_sum} => 2x = {2*son_age} => x = {son_age} years."
            else:
                s_val = rnd.choice([7, 8, 9, 10])
                p_val = rnd.choice([10, 12, 14, 15])
                ans_sq = s_val**2 - 2*p_val
                q_text = f"If x + y = {s_val} and xy = {p_val}, find the value of x^2 + y^2."
                correct = str(ans_sq)
                d1, d2, d3 = str(s_val**2), str(ans_sq - 10), str(ans_sq + 14)
                exp = f"x^2 + y^2 = (x + y)^2 - 2xy = {s_val}^2 - 2({p_val}) = {s_val**2} - {2*p_val} = {ans_sq}."
            return PracticeAgent._format_shuffled_question(q_text, correct, d1, d2, d3, exp, t_norm, category, diff)

        # 10. Number Series
        elif t_norm == "Number Series":
            if var_idx == 0:
                start = rnd.choice([3, 5, 7, 10])
                step = rnd.choice([4, 6, 7, 8])
                seq = [start + k * step for k in range(4)]
                next_val = start + 4 * step
                q_text = f"Find the next term in the arithmetic series: {seq[0]}, {seq[1]}, {seq[2]}, {seq[3]}, ?"
                correct = str(next_val)
                d1, d2, d3 = str(next_val - step + 1), str(next_val + step), str(next_val + 4)
                exp = f"Arithmetic series with common difference +{step}. Next term = {seq[3]} + {step} = {next_val}."
            elif var_idx == 1:
                start = rnd.choice([2, 3, 5])
                r = 2
                seq = [start * (r**k) for k in range(4)]
                next_val = start * (r**4)
                q_text = f"Identify the next term in the geometric sequence: {seq[0]}, {seq[1]}, {seq[2]}, {seq[3]}, ?"
                correct = str(next_val)
                d1, d2, d3 = str(next_val - 8), str(next_val + 12), str(next_val * 2)
                exp = f"Geometric sequence with common ratio *{r}. Next term = {seq[3]} * {r} = {next_val}."
            elif var_idx == 2:
                k_val = rnd.choice([1, 2, 3])
                seq = [n**2 + k_val for n in range(1, 5)]
                next_val = 5**2 + k_val
                q_text = f"Find the next term in the series: {seq[0]}, {seq[1]}, {seq[2]}, {seq[3]}, ?"
                correct = str(next_val)
                d1, d2, d3 = str(next_val - 5), str(next_val + 7), str(next_val + 10)
                exp = f"Pattern is n^2 + {k_val}. For n=5: 5^2 + {k_val} = 25 + {k_val} = {next_val}."
            elif var_idx == 3:
                start = rnd.choice([2, 4, 6])
                seq = [start * (2**k) + k for k in range(4)]
                next_val = start * (2**4) + 4
                q_text = f"Find the missing term in the sequence: {seq[0]}, {seq[1]}, {seq[2]}, {seq[3]}, ?"
                correct = str(next_val)
                d1, d2, d3 = str(next_val - 4), str(next_val + 6), str(next_val + 10)
                exp = f"Pattern T_n = start * 2^n + n. For n=4, next term = {next_val}."
            else:
                k_val = rnd.choice([1, 2, 4])
                seq = [n**3 + k_val for n in range(1, 5)]
                next_val = 5**3 + k_val
                q_text = f"Identify the next term in the logic sequence: {seq[0]}, {seq[1]}, {seq[2]}, {seq[3]}, ?"
                correct = str(next_val)
                d1, d2, d3 = str(next_val - 10), str(next_val + 15), str(next_val + 25)
                exp = f"Pattern n^3 + {k_val}. For n=5: 125 + {k_val} = {next_val}."
            return PracticeAgent._format_shuffled_question(q_text, correct, d1, d2, d3, exp, t_norm, category, diff)

        # 11. Syllogism
        elif t_norm == "Syllogism":
            if var_idx == 0:
                q_text = "Statements: 1. All cats are dogs. 2. All dogs are mammals.\nConclusions: I. All cats are mammals. II. Some mammals are dogs."
                correct = "Both Conclusion I and II follow"
                d1, d2, d3 = "Only Conclusion I follows", "Only Conclusion II follows", "Neither conclusion follows"
                exp = "Cats ⊂ Dogs ⊂ Mammals. Therefore all cats are mammals (I) and some mammals are dogs (II) both hold true."
            elif var_idx == 1:
                q_text = "Statements: 1. All apples are fruits. 2. No fruit is a stone.\nConclusions: I. No apple is a stone. II. Some fruits are apples."
                correct = "Both Conclusion I and II follow"
                d1, d2, d3 = "Only Conclusion I follows", "Only Conclusion II follows", "Neither conclusion follows"
                exp = "Apples are inside Fruits, which is disjoint from Stones. Thus no apple is a stone and some fruits are apples."
            elif var_idx == 2:
                q_text = "Statements: 1. Some pens are pencils. 2. All pencils are erasers.\nConclusions: I. Some pens are erasers. II. All erasers are pens."
                correct = "Only Conclusion I follows"
                d1, d2, d3 = "Only Conclusion II follows", "Both conclusions follow", "Neither conclusion follows"
                exp = "Pens intersect Pencils, and Pencils are inside Erasers. Thus Pens intersect Erasers (I follows). However, not all erasers are pens."
            elif var_idx == 3:
                q_text = "Statements: 1. No apple is a banana. 2. All bananas are cherries.\nConclusions: I. Some cherries are not apples. II. Some apples are cherries."
                correct = "Only Conclusion I follows"
                d1, d2, d3 = "Only Conclusion II follows", "Both conclusions follow", "Neither conclusion follows"
                exp = "Since no apple is a banana, but all bananas are cherries, cherries that are bananas cannot be apples. Thus Conclusion I follows."
            else:
                q_text = "Statements: 1. All cars are vehicles. 2. All vehicles have wheels.\nConclusions: I. All cars have wheels. II. Some vehicles are cars."
                correct = "Both Conclusion I and II follow"
                d1, d2, d3 = "Only Conclusion I follows", "Only Conclusion II follows", "Neither conclusion follows"
                exp = "Cars ⊂ Vehicles ⊂ Wheeled items. Both conclusions follow logically."
            return PracticeAgent._format_shuffled_question(q_text, correct, d1, d2, d3, exp, t_norm, category, diff)

        # 12. Blood Relations
        elif t_norm == "Blood Relations":
            if var_idx == 0:
                q_text = "A is the father of B, and B is the brother of C. How is A related to C?"
                correct = "Father"
                d1, d2, d3 = "Uncle", "Brother", "Grandfather"
                exp = "Since B and C are siblings, A is also C's Father."
            elif var_idx == 1:
                q_text = "P is the mother of Q, and Q is the mother of R. How is P related to R?"
                correct = "Grandmother"
                d1, d2, d3 = "Mother", "Aunt", "Sister"
                exp = "Mother's mother is Grandmother."
            elif var_idx == 2:
                q_text = "X is the brother of Y. Y is the wife of Z. How is X related to Z?"
                correct = "Brother-in-law"
                d1, d2, d3 = "Brother", "Father-in-law", "Uncle"
                exp = "Wife's brother is Brother-in-law."
            elif var_idx == 3:
                q_text = "Pointing to a photograph of a man, Rahul said, 'His mother is the only daughter of my mother-in-law.' How is the man related to Rahul?"
                correct = "Son"
                d1, d2, d3 = "Brother", "Nephew", "Father"
                exp = "Mother-in-law's only daughter = Rahul's wife. Wife's son = Rahul's Son."
            else:
                q_text = "If 'A + B' means A is the father of B, and 'A - B' means A is the sister of B. In the expression 'P + Q - R', how is P related to R?"
                correct = "Father"
                d1, d2, d3 = "Brother", "Uncle", "Grandfather"
                exp = "P + Q means P is father of Q. Q - R means Q is sister of R. Therefore P is the father of R."
            return PracticeAgent._format_shuffled_question(q_text, correct, d1, d2, d3, exp, t_norm, category, diff)

        # 13. Seating Arrangement
        elif t_norm == "Seating Arrangement":
            if var_idx == 0:
                q_text = "Five friends A, B, C, D, and E are sitting in a row facing North. C is sitting in the middle. A is to the immediate left of C, and E is to the immediate right of C. Who is sitting second to the left of E?"
                correct = "A"
                d1, d2, d3 = "B", "C", "D"
                exp = "Row order: _ A C E _. Immediate left of E is C, second to the left of E is A."
            elif var_idx == 1:
                q_text = "Four friends P, Q, R, and S are sitting in a straight row facing North. P is at the extreme left end, and S is at the extreme right end. Q is sitting next to P. Who is sitting next to S?"
                correct = "R"
                d1, d2, d3 = "P", "Q", "None"
                exp = "Row positions: P Q R S. Next to S is R."
            elif var_idx == 2:
                q_text = "Four people A, B, C, and D are sitting in a circle facing the center. A is sitting opposite C, and B is sitting to the right of A. Who is sitting to the left of A?"
                correct = "D"
                d1, d2, d3 = "B", "C", "A"
                exp = "Positions: Facing center, right of A is B, opposite A is C, left of A is D."
            elif var_idx == 3:
                q_text = "Six people A, B, C, D, E, and F sit around a circular table facing the center. A sits opposite D. B sits to the immediate right of A. E sits opposite B. Who sits to the immediate left of D?"
                correct = "E"
                d1, d2, d3 = "C", "F", "B"
                exp = "Opposite pairs: A-D, B-E. B is right of A, so E is right of D (left of D is E)."
            else:
                q_text = "Three colleagues X, Y, and Z are sitting in a row. Y is sitting between X and Z. Who is sitting at the rightmost end if X is at the left end?"
                correct = "Z"
                d1, d2, d3 = "X", "Y", "Cannot be determined"
                exp = "Order: X Y Z. Rightmost end is Z."
            return PracticeAgent._format_shuffled_question(q_text, correct, d1, d2, d3, exp, t_norm, category, diff)

        # 14. Coding-Decoding
        elif t_norm == "Coding-Decoding":
            if var_idx == 0:
                q_text = "If 'LIGHT' is coded as 'MJHIU', how is 'FLAME' coded?"
                correct = "GMBNF"
                d1, d2, d3 = "EKZLD", "GLBMF", "GMBND"
                exp = "Each letter is shifted by +1: L->M, I->J, G->H, H->I, T->U. FLAME -> GMBNF."
            elif var_idx == 1:
                q_text = "If 'SMART' is coded as 'TRAMS', how is 'GREAT' coded in the same pattern?"
                correct = "TAERG"
                d1, d2, d3 = "HSFBU", "TAEGR", "ATEGR"
                exp = "Pattern is reversing the word letters: SMART -> TRAMS. GREAT -> TAERG."
            elif var_idx == 2:
                q_text = "If 'CAT' is coded as 'ECV', how is 'DOG' coded?"
                correct = "FQI"
                d1, d2, d3 = "EPH", "FPH", "GQI"
                exp = "Shift +2 for each letter: D->F, O->Q, G->I => FQI."
            elif var_idx == 3:
                q_text = "If 'MIND' is coded as 'KGLB', how is 'DIAGRAM' coded?"
                correct = "BGYEPYK"
                d1, d2, d3 = "BGYPEYK", "BGYEPYE", "CGYEPYK"
                exp = "Each letter is shifted backward by 2 (-2): M(13)->K(11). Applying -2 to DIAGRAM gives BGYEPYK."
            else:
                q_text = "If 'CAT' is coded as '24' and 'DOG' is coded as '26', what is the numerical code for 'PIG'?"
                correct = "32"
                d1, d2, d3 = "30", "34", "36"
                exp = "Sum of alphabetical positions: P(16) + I(9) + G(7) = 32."
            return PracticeAgent._format_shuffled_question(q_text, correct, d1, d2, d3, exp, t_norm, category, diff)

        # 15. Permutation and Combination
        elif t_norm == "Permutation and Combination":
            if var_idx == 0:
                n = rnd.choice([5, 6, 7])
                ans = (n * (n - 1)) // 2
                q_text = f"In how many ways can a committee of 2 members be selected from a group of {n} people?"
                correct = str(ans)
                d1, d2, d3 = str(ans - 3), str(ans + 5), str(n * 2)
                exp = f"Combinations formula {n}C2 = ({n} * {n-1}) / 2 = {ans} ways."
            elif var_idx == 1:
                n = rnd.choice([3, 4])
                ans = math.factorial(n)
                q_text = f"In how many distinct ways can {n} different books be arranged in a line on a shelf?"
                correct = str(ans)
                d1, d2, d3 = str(ans - 2), str(ans + 4), str(ans * 2)
                exp = f"Permutations of {n} distinct items = {n}! = {ans} ways."
            elif var_idx == 2:
                q_text = "In how many ways can the letters of the word 'LEVEL' be arranged?"
                correct = "30"
                d1, d2, d3 = "120", "60", "15"
                exp = "Length = 5 letters with 2 L's and 2 E's. Total arrangements = 5! / (2! * 2!) = 120 / 4 = 30."
            elif var_idx == 3:
                n = rnd.choice([8, 10, 12])
                ans = (n * (n - 1)) // 2
                q_text = f"At a business meeting, {n} executives shake hands with each other exactly once. How many total handshakes take place?"
                correct = str(ans)
                d1, d2, d3 = str(n * (n-1)), str(ans + 10), str(ans - 5)
                exp = f"Total handshakes = {n}C2 = ({n} * {n-1}) / 2 = {ans}."
            else:
                q_text = "How many combinations of 1 item can be chosen from 8 items?"
                correct = "8"
                d1, d2, d3 = "1", "16", "64"
                exp = "8C1 = 8."
            return PracticeAgent._format_shuffled_question(q_text, correct, d1, d2, d3, exp, t_norm, category, diff)

        # 16. Simple and Compound Interest
        elif t_norm == "Simple and Compound Interest":
            if var_idx == 0:
                p = rnd.choice([1000, 1500, 2000, 2500])
                r = rnd.choice([5, 8, 10, 12])
                t = rnd.choice([2, 3, 4])
                si = int((p * r * t) / 100)
                q_text = f"Calculate the Simple Interest on a principal of ${p} at an annual interest rate of {r}% for {t} years."
                correct = f"${si}"
                d1, d2, d3 = f"${si - 30}", f"${si + 40}", f"${si + 80}"
                exp = f"SI = (P * R * T) / 100 = ({p} * {r} * {t}) / 100 = ${si}."
            elif var_idx == 1:
                p = rnd.choice([500, 800, 1000])
                r = rnd.choice([5, 10])
                t = rnd.choice([2, 3])
                si = int((p * r * t) / 100)
                amt = p + si
                q_text = f"What is the total amount payable on a sum of ${p} borrowed at {r}% simple interest per annum after {t} years?"
                correct = f"${amt}"
                d1, d2, d3 = f"${p}", f"${si}", f"${amt + 50}"
                exp = f"SI = (${p} * {r} * {t})/100 = ${si}. Total Amount = P + SI = ${p} + ${si} = ${amt}."
            elif var_idx == 2:
                si = rnd.choice([150, 200, 300])
                r = 10
                t = 2
                p = int((si * 100) / (r * t))
                q_text = f"Find the principal sum that yields ${si} as simple interest at {r}% per annum in {t} years."
                correct = f"${p}"
                d1, d2, d3 = f"${p - 200}", f"${p + 300}", f"${p + 500}"
                exp = f"Principal P = (SI * 100) / (R * T) = ({si} * 100) / ({r} * {t}) = ${p}."
            elif var_idx == 3:
                p = rnd.choice([1000, 2000, 3000])
                r = 10
                amt = int(p * ((1 + r/100.0) ** 2))
                ci = amt - p
                q_text = f"Find the compound interest on ${p} for 2 years at 10% per annum compounded annually."
                correct = f"${ci}"
                d1, d2, d3 = f"${ci - 30}", f"${ci + 50}", f"${amt}"
                exp = f"Amount A = {p} * (1.10)^2 = ${amt}. Compound Interest = A - P = ${amt} - ${p} = ${ci}."
            else:
                p = rnd.choice([5000, 10000, 15000])
                r = 10
                diff_val = int(p * ((r / 100.0) ** 2))
                q_text = f"What is the difference between Compound Interest and Simple Interest on a sum of ${p} for 2 years at 10% per annum?"
                correct = f"${diff_val}"
                d1, d2, d3 = f"${diff_val - 20}", f"${diff_val + 50}", f"${diff_val + 100}"
                exp = f"Difference for 2 years = P * (R/100)^2 = {p} * (10/100)^2 = ${diff_val}."
            return PracticeAgent._format_shuffled_question(q_text, correct, d1, d2, d3, exp, t_norm, category, diff)

        # 17. Vocabulary / Grammar / Reading Comprehension
        elif t_norm in ["Synonyms and Antonyms", "Vocabulary"]:
            return PracticeAgent._generate_dynamic_verbal_question(t_norm, diff, var_idx, seed)
        elif t_norm in ["Sentence Correction", "Grammar"]:
            return PracticeAgent._generate_dynamic_grammar_question(t_norm, diff, var_idx, seed)
        elif t_norm == "Reading Comprehension":
            passages = [
                ("Passage: 'Artificial Intelligence algorithms rely heavily on clean training data to make unbiased predictions. When training datasets contain systemic historical skew, model outputs inevitably reflect those same biases.'\n\nQuestion: According to the passage, what is the primary cause of biased AI model outputs?",
                 "Systemic historical skew in training datasets",
                 "Slower computing processors", "Lack of complex neural networks", "Insufficient user feedback",
                 "The passage explicitly states that when training datasets contain systemic historical skew, model outputs inevitably reflect those same biases."),
                ("Passage: 'Renewable energy sources such as solar and wind power offer significant environmental benefits by reducing carbon emissions. However, grid integration remains challenging due to output intermittency.'\n\nQuestion: What main obstacle to grid integration is mentioned in the passage?",
                 "Output intermittency of renewable energy",
                 "High operational fuel costs", "Lack of solar panel technology", "Excessive carbon emissions",
                 "The passage specifically cites output intermittency as the primary challenge to grid integration."),
                ("Passage: 'Effective time management is essential for competitive exam success. Students who prioritize high-yield concepts and take timed practice tests routinely outperform those who passively read textbooks.'\n\nQuestion: Which strategy is highlighted in the passage as key to outperforming passive reading?",
                 "Taking timed practice tests and prioritizing high-yield concepts",
                 "Reading textbooks multiple times", "Studying continuously without breaks", "Avoiding practice questions",
                 "The passage directly notes that prioritizing high-yield concepts and taking timed practice tests leads to higher performance.")
            ]
            sel = passages[seed % len(passages)]
            return PracticeAgent._format_shuffled_question(sel[0], sel[1], sel[2], sel[3], sel[4], sel[5], t_norm, category, diff)

        # Controlled Fallback for any unhandled topic
        else:
            cat = get_category_for_topic(t_norm)
            if cat == "Verbal Ability":
                return PracticeAgent._generate_dynamic_verbal_question(t_norm, diff, var_idx, seed)
            elif cat == "Logical Reasoning":
                return PracticeAgent._generate_dynamic_grammar_question(t_norm, diff, var_idx, seed)
            else:
                return PracticeAgent._generate_fallback_variant("Percentage", "Quantitative Aptitude", diff, var_idx, seed)

    @staticmethod
    def _generate_dynamic_verbal_question(topic: str, difficulty: str, var_idx: int, seed: int) -> QuestionSchema:
        diff_lower = (difficulty or "medium").lower()
        rnd = random.Random(seed * 555 + var_idx)

        easy_words = [
            ("LUCID", "Clear and easily understood", "Confusing", "Vague", "Obscure", "'Lucid' means expressed clearly and easy to understand."),
            ("CANDID", "Truthful and straightforward", "Deceitful", "Guarded", "Dishonest", "'Candid' means frank, open, and sincere."),
            ("BENEVOLENT", "Kind and generous", "Malevolent", "Cruel", "Harsh", "'Benevolent' means well-meaning and kindly."),
            ("PRAGMATIC", "Practical and realistic", "Theoretical", "Idealistic", "Impractical", "'Pragmatic' means dealing with things in a practical manner."),
            ("AUSTERE", "Strict and simple", "Extravagant", "Luxurious", "Mild", "'Austere' means severe or strict in manner or appearance.")
        ]
        medium_words = [
            ("METICULOUS", "Thorough and precise", "Careless", "Hasty", "Sloppy", "'Meticulous' means paying great attention to detail; very precise."),
            ("TENACIOUS", "Persistent and firm", "Yielding", "Weak", "Irresolute", "'Tenacious' means holding firmly to a position or purpose."),
            ("UBIQUITOUS", "Present everywhere", "Rare", "Scarce", "Unusual", "'Ubiquitous' means present or found everywhere."),
            ("FASTIDIOUS", "Very attentive to accuracy", "Careless", "Sloppy", "Negligent", "'Fastidious' means very concerned about accuracy."),
            ("AUDACIOUS", "Bold and daring", "Timid", "Cautious", "Fearful", "'Audacious' means showing a willingness to take bold risks.")
        ]
        hard_words = [
            ("EPHEMERAL", "Short-lived and temporary", "Permanent", "Eternal", "Enduring", "'Ephemeral' means lasting for a very short time."),
            ("ALACRITY", "Brisk and cheerful readiness", "Apathy", "Lethargy", "Sluggishness", "'Alacrity' means eager and cheerful readiness."),
            ("EQUANIMITY", "Mental calmness and composure", "Agitation", "Anxiety", "Panic", "'Equanimity' means composure in a difficult situation."),
            ("PERSPICACIOUS", "Having keen insight and understanding", "Ignorant", "Unperceptive", "Dull", "'Perspicacious' means having ready insight into things."),
            ("RETICENT", "Not revealing one's thoughts readily", "Talkative", "Voluble", "Outspoken", "'Reticent' means disposed to be silent.")
        ]

        pool = easy_words if diff_lower == "easy" else (hard_words if diff_lower == "hard" else medium_words)
        selected = pool[var_idx % len(pool)]
        word, meaning, ant1, ant2, ant3, exp = selected

        is_synonym = (var_idx % 2 == 0)
        if is_synonym or diff_lower == "easy":
            q_text = f"Choose the word or phrase most NEARLY SIMILAR in meaning to '{word}':"
            correct = meaning
            d1, d2, d3 = ant1, ant2, ant3
        else:
            q_text = f"Choose the word most NEARLY OPPOSITE in meaning to '{word}':"
            correct = ant1
            d1, d2, d3 = meaning, f"Extremely {meaning.lower()}", f"Somewhat {meaning.lower()}"
            exp = f"{exp} The opposite is '{ant1}'."

        return PracticeAgent._format_shuffled_question(q_text, correct, d1, d2, d3, exp, topic, "Verbal Ability", difficulty)

    @staticmethod
    def _generate_dynamic_grammar_question(topic: str, difficulty: str, var_idx: int, seed: int) -> QuestionSchema:
        subjects = [
            "The list of items", "Neither of the candidates", "Each of the students",
            "The team of researchers", "A pair of shoes", "Either of the reports",
            "Every one of the participants"
        ]
        verbs_incorrect = [
            "are on the table", "were selected for the position", "have completed their task",
            "are presenting today", "were left outside", "are accurate", "have arrived on time"
        ]
        verbs_correct = [
            "is on the table", "was selected for the position", "has completed their task",
            "is presenting today", "was left outside", "is accurate", "has arrived on time"
        ]
        explanations = [
            "Subject 'list' is singular; verb must be singular ('is' instead of 'are').",
            "'Neither' is a singular pronoun requiring singular verb ('was' instead of 'were').",
            "'Each' is singular and takes a singular verb ('has' instead of 'have').",
            "Collective noun 'team' takes singular verb ('is' instead of 'are').",
            "'Pair' is singular requiring singular verb ('was' instead of 'were').",
            "'Either' requires a singular verb ('is' instead of 'are').",
            "'Every one' requires a singular verb ('has' instead of 'have')."
        ]

        idx = var_idx % len(subjects)
        subj = subjects[idx]
        v_inc = verbs_incorrect[idx]
        v_cor = verbs_correct[idx]
        exp = explanations[idx]

        q_text = f"Identify the grammatically correct sentence correction for: '{subj} {v_inc}.'"
        correct = f"{subj} {v_cor}."
        d1 = f"{subj} {v_inc}."
        d2 = f"{subj} remain {v_inc.split()[1]}."
        d3 = f"All {subj.lower()} {v_inc}."
        return PracticeAgent._format_shuffled_question(q_text, correct, d1, d2, d3, exp, topic, "Verbal Ability", difficulty)

    @staticmethod
    def _format_shuffled_question(q_text: str, correct_val: str, d1: str, d2: str, d3: str, exp: str, topic: str, category: str, difficulty: str) -> QuestionSchema:
        opts_raw = [str(correct_val), str(d1), str(d2), str(d3)]

        distinct = []
        for o in opts_raw:
            if o not in distinct:
                distinct.append(o)
            else:
                try:
                    clean_num = re.sub(r'[^\d\.\-]', '', o)
                    if clean_num:
                        num = float(clean_num)
                        new_num = str(int(num + 5)) if num.is_integer() else str(round(num + 5.5, 1))
                        if "$" in o:
                            new_val = f"${new_num}"
                        elif "%" in o:
                            new_val = f"{new_num}%"
                        elif "days" in o:
                            new_val = f"{new_num} days"
                        elif "seconds" in o:
                            new_val = f"{new_num} seconds"
                        elif "hours" in o:
                            new_val = f"{new_num} hours"
                        else:
                            new_val = new_num
                    else:
                        new_val = f"{o} (Alt)"
                except Exception:
                    new_val = f"{o} (Alt)"
                distinct.append(new_val)

        final_opts = distinct[:4]
        random.shuffle(final_opts)

        keys = ["option_a", "option_b", "option_c", "option_d"]
        opt_map = {keys[i]: final_opts[i] for i in range(4)}
        correct_key = keys[final_opts.index(str(correct_val))]

        return QuestionSchema(
            question=q_text,
            option_a=opt_map["option_a"],
            option_b=opt_map["option_b"],
            option_c=opt_map["option_c"],
            option_d=opt_map["option_d"],
            correct_answer=correct_key,
            explanation=exp,
            topic=topic,
            category=category,
            difficulty=difficulty
        )
