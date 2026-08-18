import logging
import random
import time
from typing import List, Optional
from app.models.schemas import QuestionSchema, PracticeGenerateRequest
from app.tools.question_validator import QuestionValidator
from app.tools.calculator import SafeCalculator
from app.rag.topic_knowledge import get_topic_details
from app.agents.llm_factory import get_llm
from app.database.connection import SessionLocal
from app.database.repository import Repository

logger = logging.getLogger(__name__)

VOCAB_ITEMS = [
    {"word": "CANDID", "type": "OPPOSITE", "target": "Deceitful", "distractors": ["Frank", "Honest", "Open"], "exp": "'Candid' means truthful and straightforward. The opposite is 'Deceitful'."},
    {"word": "METICULOUS", "type": "SIMILAR", "target": "Thorough and precise", "distractors": ["Careless", "Hasty", "Aggressive"], "exp": "'Meticulous' means showing great attention to detail; very careful and precise."},
    {"word": "PRAGMATIC", "type": "SIMILAR", "target": "Practical and realistic", "distractors": ["Idealistic", "Impractical", "Theoretical"], "exp": "'Pragmatic' means dealing with things sensibly and realistically."},
    {"word": "LUCID", "type": "SIMILAR", "target": "Clear and easily understood", "distractors": ["Confusing", "Vague", "Obscure"], "exp": "'Lucid' means expressed clearly; easy to understand."},
    {"word": "TENACIOUS", "type": "SIMILAR", "target": "Persistent and firm", "distractors": ["Yielding", "Weak", "Irresolute"], "exp": "'Tenacious' means tending to keep a firm hold of something; persistent."},
    {"word": "AUDACIOUS", "type": "OPPOSITE", "target": "Timid and cautious", "distractors": ["Bold", "Daring", "Fearless"], "exp": "'Audacious' means showing a willingness to take surprisingly bold risks. The opposite is 'Timid'."},
    {"word": "BENEVOLENT", "type": "OPPOSITE", "target": "Malevolent and harsh", "distractors": ["Kind", "Generous", "Charitable"], "exp": "'Benevolent' means well meaning and kindly. The opposite is 'Malevolent'."},
    {"word": "FASTIDIOUS", "type": "SIMILAR", "target": "Very attentive to accuracy and detail", "distractors": ["Careless", "Sloppy", "Unconcerned"], "exp": "'Fastidious' means very attentive to and concerned about accuracy and detail."},
    {"word": "GARRULOUS", "type": "OPPOSITE", "target": "Taciturn and silent", "distractors": ["Talkative", "Loquacious", "Voluble"], "exp": "'Garrulous' means excessively talkative. The opposite is 'Taciturn'."},
    {"word": "SAGACIOUS", "type": "SIMILAR", "target": "Wise and insightful", "distractors": ["Foolish", "Ignorant", "Naive"], "exp": "'Sagacious' means having or showing keen mental discernment and good judgment."}
]

class PracticeAgent:
    """Agent responsible for generating, validating, and retrieving practice MCQs."""

    @staticmethod
    def generate_practice_questions(
        topic: str,
        category: str = "Quantitative Aptitude",
        difficulty: str = "medium",
        number_of_questions: int = 5
    ) -> List[QuestionSchema]:
        db = SessionLocal()
        try:
            repo = Repository(db)
            validated_questions: List[QuestionSchema] = []
            seen_texts = set()

            # Attempt random sampling from existing database questions
            existing_qs = repo.get_questions(topic=topic, category=category, difficulty=difficulty, limit=50)
            if existing_qs:
                random.shuffle(existing_qs)
                for q in existing_qs:
                    if q.question not in seen_texts:
                        seen_texts.add(q.question)
                        validated_questions.append(
                            QuestionSchema(
                                id=q.id,
                                question=q.question,
                                option_a=q.option_a,
                                option_b=q.option_b,
                                option_c=q.option_c,
                                option_d=q.option_d,
                                correct_answer=q.correct_answer,
                                explanation=q.explanation,
                                topic=q.topic,
                                category=q.category,
                                difficulty=q.difficulty
                            )
                        )
                    if len(validated_questions) >= number_of_questions:
                        return validated_questions[:number_of_questions]

            # Otherwise use LLM pipeline or dynamic generator to fulfill remaining question count
            needed = number_of_questions - len(validated_questions)
            max_attempts_per_q = 3
            llm = get_llm(temperature=0.7, structured_output_schema=QuestionSchema)

            for i in range(needed):
                q_generated = False
                for attempt in range(max_attempts_per_q):
                    if llm:
                        seed = random.randint(1000, 999999)
                        prompt = f"""Generate a unique, mathematically precise multiple-choice question for competitive aptitude preparation.
Topic: {topic}
Category: {category}
Difficulty: {difficulty}
Random Seed: {seed}

Requirements:
- Exactly 4 unique options: option_a, option_b, option_c, option_d.
- Exactly 1 correct option key ('option_a', 'option_b', 'option_c', or 'option_d').
- Ensure this question is unique and uses distinct numbers or vocabulary from standard examples.
- Provide step-by-step mathematical explanation proving the answer.
"""
                        try:
                            candidate_q = llm.invoke(prompt)
                            if isinstance(candidate_q, QuestionSchema) and candidate_q.question not in seen_texts:
                                val_result = QuestionValidator.validate(candidate_q)
                                if val_result.is_valid:
                                    db_model = repo.add_question(candidate_q)
                                    candidate_q.id = db_model.id
                                    validated_questions.append(candidate_q)
                                    seen_texts.add(candidate_q.question)
                                    q_generated = True
                                    break
                        except Exception as e:
                            logger.warning(f"LLM generation exception: {e}")

                if not q_generated:
                    # Dynamic fallback question generator with randomized parameters
                    fallback_q = PracticeAgent._create_dynamic_fallback_q(topic, category, difficulty, i, seen_texts)
                    db_model = repo.add_question(fallback_q)
                    fallback_q.id = db_model.id
                    validated_questions.append(fallback_q)
                    seen_texts.add(fallback_q.question)

            return validated_questions[:number_of_questions]
        finally:
            db.close()

    @staticmethod
    def _create_dynamic_fallback_q(topic: str, category: str, difficulty: str, index: int, seen_texts: set) -> QuestionSchema:
        """Create a dynamic, randomized, topic-specific aptitude question with shuffled options."""
        topic_lower = topic.lower()

        if "profit" in topic_lower or "loss" in topic_lower:
            cp = random.randint(6, 40) * 10
            profit_pct = random.choice([10, 15, 20, 25, 30])
            sp = int(cp * (1 + profit_pct / 100.0))
            q_text = f"A trader buys a product for ${cp}. If he sells it at a profit of {profit_pct}%, what is the selling price?"
            correct = f"${sp}"
            d1, d2, d3 = f"${sp - 15}", f"${sp + 15}", f"${sp + 30}"
            exp = f"Selling Price = CP * (1 + Profit%/100) = ${cp} * (1 + {profit_pct}/100) = ${sp}."
            return PracticeAgent._format_shuffled_question(q_text, correct, d1, d2, d3, exp, topic, category, difficulty)

        elif "work" in topic_lower or "time" in topic_lower:
            days1 = random.choice([6, 8, 10, 12, 15])
            days2 = random.choice([12, 15, 20, 24, 30])
            combined = round((days1 * days2) / (days1 + days2), 1)
            q_text = f"Worker A can complete a project in {days1} days and Worker B in {days2} days. How many days will they take together?"
            correct = f"{combined} days"
            d1, d2, d3 = f"{round(combined + 1.5, 1)} days", f"{round(max(1.0, combined - 1.5), 1)} days", f"{days1 + days2} days"
            exp = f"Combined time = (A * B) / (A + B) = ({days1} * {days2}) / ({days1} + {days2}) = {combined} days."
            return PracticeAgent._format_shuffled_question(q_text, correct, d1, d2, d3, exp, topic, category, difficulty)

        elif "ratio" in topic_lower or "proportion" in topic_lower:
            r1, r2 = random.choice([(2, 3), (3, 5), (4, 5), (5, 7)])
            total = (r1 + r2) * random.randint(10, 40)
            share_a = int((r1 / (r1 + r2)) * total)
            q_text = f"A sum of ${total} is divided between Person A and Person B in the ratio {r1}:{r2}. What is Person A's share?"
            correct = f"${share_a}"
            d1, d2, d3 = f"${share_a - 20}", f"${share_a + 20}", f"${total - share_a}"
            exp = f"Person A Share = [{r1} / ({r1} + {r2})] * ${total} = ${share_a}."
            return PracticeAgent._format_shuffled_question(q_text, correct, d1, d2, d3, exp, topic, category, difficulty)

        elif "series" in topic_lower or "coding" in topic_lower or "reasoning" in topic_lower:
            start = random.randint(2, 15)
            step = random.randint(3, 8)
            seq = [start + k * step for k in range(4)]
            next_val = start + 4 * step
            q_text = f"Find the next term in the logical series: {seq[0]}, {seq[1]}, {seq[2]}, {seq[3]}, ?"
            correct = str(next_val)
            d1, d2, d3 = str(next_val - step + 1), str(next_val + step), str(next_val + 2)
            exp = f"Arithmetic progression with common difference of +{step}. Next term = {seq[3]} + {step} = {next_val}."
            return PracticeAgent._format_shuffled_question(q_text, correct, d1, d2, d3, exp, topic, category, difficulty)

        elif "vocab" in topic_lower or "grammar" in topic_lower or "verbal" in topic_lower:
            item = random.choice(VOCAB_ITEMS)
            q_text = f"Choose the word most NEARLY {item['type']} in meaning to '{item['word']}':"
            correct = item["target"]
            d1, d2, d3 = item["distractors"][0], item["distractors"][1], item["distractors"][2]
            exp = item["exp"]
            return PracticeAgent._format_shuffled_question(q_text, correct, d1, d2, d3, exp, topic, "Verbal Ability", difficulty)

        else: # Percentage default
            base_val = random.randint(4, 50) * 20
            pct = random.choice([10, 15, 20, 25, 30, 40, 50])
            ans = int((pct / 100.0) * base_val)
            q_text = f"What is {pct}% of {base_val} in {topic}?"
            correct = str(ans)
            d1, d2, d3 = str(ans - 10), str(ans + 10), str(ans + 20)
            exp = f"{pct}% of {base_val} = ({pct} / 100) * {base_val} = {ans}."
            return PracticeAgent._format_shuffled_question(q_text, correct, d1, d2, d3, exp, topic, category, difficulty)

    @staticmethod
    def _format_shuffled_question(q_text, correct_val, d1, d2, d3, exp, topic, category, difficulty) -> QuestionSchema:
        opts = [correct_val, d1, d2, d3]
        random.shuffle(opts)
        keys = ["option_a", "option_b", "option_c", "option_d"]
        opt_map = {keys[i]: str(opts[i]) for i in range(4)}
        correct_key = keys[opts.index(correct_val)]
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
