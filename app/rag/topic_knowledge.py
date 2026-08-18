"""Topic Knowledge Engine containing authoritative, topic-specific educational details
for Quantitative Aptitude, Logical Reasoning, and Verbal Ability topics.
"""

from typing import Dict, Any, List
from app.models.schemas import QuestionSchema

TOPIC_KNOWLEDGE_BASE: Dict[str, Dict[str, Any]] = {
    # --- QUANTITATIVE APTITUDE ---
    "Percentage": {
        "category": "Quantitative Aptitude",
        "definition": "Percentage is a fraction expressed per hundred (%). It represents relative proportions and rate of change.",
        "core_concepts": [
            "Baseline value selection for percentage changes.",
            "Fraction-to-percentage equivalences.",
            "Successive percentage change calculation."
        ],
        "important_formulas": [
            "Percentage = (Part / Whole) * 100",
            "Percentage Change = (|New - Original| / Original) * 100",
            "Consumption Reduction % = [r / (100 + r)] * 100 (when price increases by r%)",
            "Net % Change = a + b + (a * b) / 100"
        ],
        "explanation": "When calculating percentage increase or decrease, always use the initial (original) value as the denominator. Successive changes cannot be added directly; apply the successive percentage formula.",
        "worked_examples": [
            {
                "problem": "If the price of petrol increases by 25%, by what percentage should a driver reduce consumption so expenditure remains unchanged?",
                "solution": "Reduction % = [25 / (100 + 25)] * 100 = 25 / 125 * 100 = 20%."
            },
            {
                "problem": "What is 15% of 320?",
                "solution": "15% of 320 = (15 / 100) * 320 = 48."
            }
        ],
        "shortcuts": [
            "1/2=50%, 1/3=33.33%, 1/4=25%, 1/5=20%, 1/6=16.67%, 1/8=12.5%, 1/10=10%.",
            "a% of b is always equal to b% of a."
        ],
        "common_mistakes": [
            "Using the final value as the baseline denominator.",
            "Adding successive percentage changes linearly."
        ],
        "exam_tips": [
            "Convert complex percentage equations into simple fractions to speed up calculations."
        ],
        "sample_questions": [
            QuestionSchema(
                question="If salary is increased by 20% and then decreased by 20%, what is the net percentage change in salary?",
                option_a="No change",
                option_b="4% decrease",
                option_c="4% increase",
                option_d="2% decrease",
                correct_answer="option_b",
                explanation="Net % change = 20 - 20 + (20 * -20) / 100 = -400 / 100 = -4% (4% decrease).",
                topic="Percentage",
                category="Quantitative Aptitude",
                difficulty="medium"
            )
        ]
    },

    "Profit and Loss": {
        "category": "Quantitative Aptitude",
        "definition": "Profit and Loss measures financial gains or losses in buying and selling transactions involving Cost Price (CP), Selling Price (SP), and Marked Price (MP).",
        "core_concepts": [
            "Profit occurs when Selling Price > Cost Price.",
            "Loss occurs when Cost Price > Selling Price.",
            "Discounts are calculated on Marked Price (MP)."
        ],
        "important_formulas": [
            "Profit = SP - CP | Profit % = (Profit / CP) * 100",
            "Loss = CP - SP | Loss % = (Loss / CP) * 100",
            "CP = (SP * 100) / (100 + Profit %)",
            "Discount % = (Discount / MP) * 100"
        ],
        "explanation": "Profit or Loss percentage is ALWAYS calculated on Cost Price (CP) unless specifically stated otherwise in the problem.",
        "worked_examples": [
            {
                "problem": "An item bought for $200 is sold for $240. Find the profit percentage.",
                "solution": "Profit = 240 - 200 = $40. Profit % = (40 / 200) * 100 = 20%."
            }
        ],
        "shortcuts": [
            "If two items are sold at same SP, one at x% profit and one at x% loss, net loss = (x/10)^2 %.",
            "False weight trader gain % = [Error / (True Weight - Error)] * 100."
        ],
        "common_mistakes": [
            "Calculating profit percentage over Selling Price instead of Cost Price.",
            "Calculating discount on Cost Price instead of Marked Price."
        ],
        "exam_tips": [
            "Assume CP = 100 when working with percentage-based profit/loss questions."
        ],
        "sample_questions": [
            QuestionSchema(
                question="A shopkeeper sells an article for $450 at a loss of 10%. At what price should he sell it to gain 20%?",
                option_a="$500",
                option_b="$550",
                option_c="$600",
                option_d="$650",
                correct_answer="option_c",
                explanation="CP = (450 * 100) / 90 = $500. To gain 20%, SP = 500 * 1.20 = $600.",
                topic="Profit and Loss",
                category="Quantitative Aptitude",
                difficulty="medium"
            )
        ]
    },

    "Ratio and Proportion": {
        "category": "Quantitative Aptitude",
        "definition": "A ratio compares two quantities of the same unit by division (a:b). A proportion asserts that two ratios are equal (a:b = c:d).",
        "core_concepts": [
            "Comparison by division.",
            "Product of Extremes = Product of Means (a*d = b*c).",
            "Mean proportional between a and b is sqrt(a*b)."
        ],
        "important_formulas": [
            "a / b = c / d  =>  a * d = b * c",
            "Mean Proportional = sqrt(a * b)",
            "Share of A in ratio a:b with total T = [a / (a + b)] * T"
        ],
        "explanation": "To divide a total amount T among individuals in ratio a:b:c, compute the sum of ratio parts (a+b+c) and multiply the total by each fraction.",
        "worked_examples": [
            {
                "problem": "Divide $1200 between A and B in the ratio 3:5.",
                "solution": "Total parts = 3 + 5 = 8. A's share = (3/8)*1200 = $450. B's share = (5/8)*1200 = $750."
            }
        ],
        "shortcuts": [
            "If a:b and b:c are given, combine into a:b:c by equating the common term b."
        ],
        "common_mistakes": [
            "Adding ratios directly without multiplying by a common multiplier x."
        ],
        "exam_tips": [
            "Express ratios in lowest integer form before setting up equations."
        ],
        "sample_questions": [
            QuestionSchema(
                question="The ratio of two numbers is 4:5 and their sum is 180. What is the larger number?",
                option_a="80",
                option_b="90",
                option_c="100",
                option_d="110",
                correct_answer="option_c",
                explanation="Let numbers be 4x and 5x. 4x + 5x = 9x = 180 => x = 20. Larger number = 5(20) = 100.",
                topic="Ratio and Proportion",
                category="Quantitative Aptitude",
                difficulty="easy"
            )
        ]
    },

    "Time and Work": {
        "category": "Quantitative Aptitude",
        "definition": "Time and Work analyzes the relationship between workers, efficiency rate, and total time required to finish a job.",
        "core_concepts": [
            "Rate of work is inversely proportional to time.",
            "If A takes x days, A's 1-day work is 1/x.",
            "Total Work = Efficiency * Time."
        ],
        "important_formulas": [
            "Combined Time for A & B = (x * y) / (x + y) days",
            "Work = Rate * Time",
            "Chain Rule: (M1 * D1 * H1) / W1 = (M2 * D2 * H2) / W2"
        ],
        "explanation": "Convert individual completion times into daily work fractions (1/x). Add individual daily fractions to determine joint work done per day.",
        "worked_examples": [
            {
                "problem": "A can finish a job in 10 days, B in 15 days. How long will they take working together?",
                "solution": "A's 1-day work = 1/10, B's = 1/15. Combined = 1/10 + 1/15 = 5/30 = 1/6. Total time = 6 days."
            }
        ],
        "shortcuts": [
            "Use LCM of completion times as total units of work. A's efficiency = Total Units / A's days."
        ],
        "common_mistakes": [
            "Adding total completion days directly (e.g. 10 + 15 = 25 days) instead of rates."
        ],
        "exam_tips": [
            "The LCM method avoids fraction arithmetic and reduces calculation errors."
        ],
        "sample_questions": [
            QuestionSchema(
                question="A can complete a work in 12 days and B in 24 days. Working together, in how many days can they complete the work?",
                option_a="6 days",
                option_b="8 days",
                option_c="10 days",
                option_d="14 days",
                correct_answer="option_b",
                explanation="Combined time = (12 * 24) / (12 + 24) = 288 / 36 = 8 days.",
                topic="Time and Work",
                category="Quantitative Aptitude",
                difficulty="medium"
            )
        ]
    },

    "Probability": {
        "category": "Quantitative Aptitude",
        "definition": "Probability measures the likelihood of an event occurring, expressed as a number between 0 (impossible) and 1 (certain).",
        "core_concepts": [
            "Sample Space (S): Set of all possible outcomes.",
            "Favorable Outcomes (E): Outcomes satisfying the event condition.",
            "Complementary Event: P(not E) = 1 - P(E)."
        ],
        "important_formulas": [
            "P(E) = Favorable Outcomes / Total Outcomes",
            "0 <= P(E) <= 1",
            "P(A or B) = P(A) + P(B) - P(A and B)"
        ],
        "explanation": "Determine total possible outcomes first. Then count favorable outcomes satisfying the condition. Express as fraction P(E) = n(E) / n(S).",
        "worked_examples": [
            {
                "problem": "What is the probability of getting a sum of 7 when rolling two standard six-sided dice?",
                "solution": "Total outcomes = 6 * 6 = 36. Favorable = {(1,6), (2,5), (3,4), (4,3), (5,2), (6,1)} (6 pairs). P = 6 / 36 = 1/6."
            }
        ],
        "shortcuts": [
            "For 'at least one' questions, calculate 1 - P(none)."
        ],
        "common_mistakes": [
            "Miscounting total outcomes in multi-stage coin or die experiments."
        ],
        "exam_tips": [
            "Always verify that favorable outcomes are mutually exclusive when adding probabilities."
        ],
        "sample_questions": [
            QuestionSchema(
                question="A single card is drawn from a standard deck of 52 cards. What is the probability of drawing an Ace?",
                option_a="1/13",
                option_b="1/52",
                option_c="1/4",
                option_d="4/13",
                correct_answer="option_a",
                explanation="Number of Aces = 4, Total cards = 52. Probability = 4 / 52 = 1/13.",
                topic="Probability",
                category="Quantitative Aptitude",
                difficulty="easy"
            )
        ]
    },

    # --- LOGICAL REASONING ---
    "Number Series": {
        "category": "Logical Reasoning",
        "definition": "Number Series involves identifying mathematical pattern rules (addition, multiplication, squares, primes) governing a sequence of numbers.",
        "core_concepts": [
            "Difference pattern analysis (1st and 2nd level differences).",
            "Multiplication/division series.",
            "Square and cube sequences (n^2 + k, n^3 + k)."
        ],
        "important_formulas": [
            "Arithmetic Difference: T_n = T_{n-1} + d",
            "Geometric Progression: T_n = T_1 * r^(n-1)",
            "n*(n+1) Sequence: 2, 6, 12, 20, 30..."
        ],
        "explanation": "First check the difference between consecutive numbers. If differences grow rapidly, test for multiplication, squares, or cubes.",
        "worked_examples": [
            {
                "problem": "Find the next number in series: 3, 7, 15, 31, 63, ?",
                "solution": "Pattern: multiply by 2 and add 1. 63 * 2 + 1 = 127. (Or differences: 4, 8, 16, 32, 64 -> 63 + 64 = 127)."
            }
        ],
        "shortcuts": [
            "Look for alternating patterns if numbers increase and decrease repeatedly."
        ],
        "common_mistakes": [
            "Stopping after checking only the first two terms."
        ],
        "exam_tips": [
            "Write down differences between terms immediately."
        ],
        "sample_questions": [
            QuestionSchema(
                question="Find the next number in the series: 5, 11, 23, 47, ?",
                option_a="95",
                option_b="94",
                option_c="96",
                option_d="92",
                correct_answer="option_a",
                explanation="Pattern: (n * 2) + 1. 47 * 2 + 1 = 95.",
                topic="Number Series",
                category="Logical Reasoning",
                difficulty="medium"
            )
        ]
    },

    "Coding-Decoding": {
        "category": "Logical Reasoning",
        "definition": "Coding-Decoding tests the ability to decipher secret rules or letter position transformations used to encode words or numbers.",
        "core_concepts": [
            "Alphabetical positions (A=1 to Z=26).",
            "Reverse position numbers (A=26 to Z=1).",
            "Shift ciphers (+k or -k character shifting)."
        ],
        "important_formulas": [
            "EJOTY Rule: E=5, J=10, O=15, T=20, Y=25",
            "Opposite letter sum = 27 (e.g. A(1) + Z(26) = 27)"
        ],
        "explanation": "Map letters to numerical positions. Identify the mathematical transformation applied to each letter position.",
        "worked_examples": [
            {
                "problem": "If 'LIGHT' is coded as 'MJHIU', how is 'FLAME' coded?",
                "solution": "Each letter is shifted by +1: L->M, I->J, G->H, H->I, T->U. For FLAME: F->G, L->M, A->B, M->N, E->F => 'GMBNF'."
            }
        ],
        "shortcuts": [
            "Remember EJOTY for fast position retrieval."
        ],
        "common_mistakes": [
            "Mixing up forward and reverse alphabetical positions."
        ],
        "exam_tips": [
            "Jot down letter positions 1-26 on scratch paper at test start."
        ],
        "sample_questions": [
            QuestionSchema(
                question="If 'MIND' is coded as 'KGLB', how is 'DIAGRAM' coded?",
                option_a="BGYEPYK",
                option_b="BGYPEYK",
                option_c="BGYEPYE",
                option_d="CGYEPYK",
                correct_answer="option_a",
                explanation="Each letter is shifted backward by 2 (-2): M(13)->K(11), I(9)->G(7), N(14)->L(12), D(4)->B(2). Applying -2 to DIAGRAM gives BGYEPYK.",
                topic="Coding-Decoding",
                category="Logical Reasoning",
                difficulty="medium"
            )
        ]
    },

    # --- VERBAL ABILITY ---
    "Vocabulary": {
        "category": "Verbal Ability",
        "definition": "Vocabulary measures comprehension of word meanings, contextual usage, root origins, synonyms, and antonyms.",
        "core_concepts": [
            "Denotation (literal meaning) vs Connotation (emotional nuance).",
            "Etymology and Latin/Greek roots.",
            "Contextual clues in sentences."
        ],
        "important_formulas": [
            "Synonyms: Words with identical/similar meanings",
            "Antonyms: Words with opposite meanings"
        ],
        "explanation": "Analyze prefixes and roots to infer meanings of unfamiliar words. Substitute option choices into context sentences.",
        "worked_examples": [
            {
                "problem": "Find the synonym of 'PRAGMATIC'.",
                "solution": "'Pragmatic' means practical and realistic. Synonym = Practical."
            }
        ],
        "shortcuts": [
            "Use tone matching: if target word has positive connotation, eliminate negative options."
        ],
        "common_mistakes": [
            "Confusing synonyms with antonyms when reading quickly."
        ],
        "exam_tips": [
            "Eliminate options that belong to wrong parts of speech."
        ],
        "sample_questions": [
            QuestionSchema(
                question="Choose the word most NEARLY OPPOSITE in meaning to 'CANDID':",
                option_a="Frank",
                option_b="Deceitful",
                option_c="Honest",
                option_d="Open",
                correct_answer="option_b",
                explanation="'Candid' means truthful and straightforward. The opposite is 'Deceitful'.",
                topic="Vocabulary",
                category="Verbal Ability",
                difficulty="easy"
            )
        ]
    },

    "Grammar": {
        "category": "Verbal Ability",
        "definition": "Grammar tests rules governing sentence construction, agreement, verb tenses, and modifier placement.",
        "core_concepts": [
            "Subject-Verb Agreement.",
            "Tense Consistency.",
            "Correct use of Prepositions and Articles."
        ],
        "important_formulas": [
            "Singular Subject -> Singular Verb ('Neither of the candidates WAS selected')",
            "Parallel Structure in lists ('running, swimming, and cycling')"
        ],
        "explanation": "Identify the true subject of the sentence (strip prepositional phrases) to check subject-verb agreement.",
        "worked_examples": [
            {
                "problem": "Correct the error: 'The list of items are on the desk.'",
                "solution": "Subject is 'list' (singular), not 'items'. Correct: 'The list of items IS on the desk.'"
            }
        ],
        "shortcuts": [
            "Ignore words inside commas or prepositional phrases when finding the subject."
        ],
        "common_mistakes": [
            "Matching verb to nearest plural noun instead of true subject."
        ],
        "exam_tips": [
            "Read sentences aloud mentally to spot unnatural phrasing."
        ],
        "sample_questions": [
            QuestionSchema(
                question="Identify the error in: 'Each of the students have completed their assignment.'",
                option_a="Each of",
                option_b="the students",
                option_c="have completed",
                option_d="their assignment",
                correct_answer="option_c",
                explanation="'Each' is a singular indefinite pronoun. Verb must be singular: 'has completed' instead of 'have completed'.",
                topic="Grammar",
                category="Verbal Ability",
                difficulty="medium"
            )
        ]
    },

    "Vocabulary": {
        "category": "Verbal Ability",
        "definition": "Vocabulary & Word Power evaluates word meanings, synonyms (words with similar meanings), antonyms (opposite meanings), etymology, and sentence usage.",
        "core_concepts": [
            "Synonyms: Words sharing identical or closely related meanings (e.g., Meticulous = Precise, Ubiquitous = Omnipresent).",
            "Antonyms: Words expressing opposite semantic meanings (e.g., Candid vs Deceitful, Ephemeral vs Eternal).",
            "Root Words & Etymology: Bene (Good), Mal (Bad), Chron (Time), Phil (Love), Path (Feeling)."
        ],
        "important_formulas": [
            "Synonym Equivalence: Word A ≈ Word B (matching tone and degree).",
            "Antonym Opposite: Word A <-> Inverse Word B.",
            "Affix Analysis: Un-/Dis-/In- reverse meaning; -Ous/-Ic form adjectives."
        ],
        "explanation": "To solve vocabulary questions accurately, analyze the root word, identify positive vs negative connotation tone, and eliminate options with incorrect parts of speech.",
        "worked_examples": [
            {
                "problem": "Find the closest synonym for 'METICULOUS'. Options: A) Careless, B) Precise, C) Rapid, D) Secret.",
                "solution": "Meticulous means showing great attention to detail. The correct synonym is B) Precise."
            },
            {
                "problem": "Find the antonym of 'EPHEMERAL'. Options: A) Temporary, B) Transient, C) Eternal, D) Brief.",
                "solution": "Ephemeral means lasting for a very short time. The opposite antonym is C) Eternal."
            }
        ],
        "shortcuts": [
            "Root Word Decomposition: Break unknown words into Prefix + Root + Suffix.",
            "Connotation Tone Elimination: If target word is positive, discard negative choices.",
            "Contextual Substitution: Replace target word in a sentence to verify nuance."
        ],
        "common_mistakes": [
            "Confusing synonyms with antonyms under exam time pressure.",
            "Choosing secondary dictionary definitions that do not match context."
        ],
        "exam_tips": [
            "Learn 5 root words daily and practice contextual usage in competitive reading passages."
        ],
        "sample_questions": [
            QuestionSchema(
                question="What is the closest synonym for 'UBIQUITOUS'?",
                option_a="Rare",
                option_b="Omnipresent",
                option_c="Mysterious",
                option_d="Ancient",
                correct_answer="option_b",
                explanation="Ubiquitous means present or found everywhere. The closest synonym is B) Omnipresent.",
                topic="Vocabulary",
                category="Verbal Ability",
                difficulty="medium"
            )
        ]
    }
}

def get_topic_details(topic: str) -> Dict[str, Any]:
    """Retrieve detailed topic knowledge data with fallback generation for any unlisted topic."""
    # Match exact or case-insensitive key
    for k, data in TOPIC_KNOWLEDGE_BASE.items():
        if k.lower() == topic.lower():
            return data

    # Dynamic fallback generator for any custom or new topic
    category = "Quantitative Aptitude"
    if any(w in topic.lower() for w in ["series", "coding", "analogy", "puzzle", "syllogism", "relation", "blood", "direction", "clock"]):
        category = "Logical Reasoning"
    elif any(w in topic.lower() for w in ["vocab", "synonym", "antonym", "grammar", "verbal", "preposition", "tense", "reading"]):
        category = "Verbal Ability"

    return {
        "category": category,
        "definition": f"{topic} is an essential module in {category}, evaluating core analytical principles and structured problem solving.",
        "core_concepts": [
            f"Understanding foundational rules of {topic}.",
            "Identifying given parameters and target variables.",
            "Applying systematic step-by-step transformations."
        ],
        "important_formulas": [
            f"Core {topic} Equation: Target = Base * Rate Factor",
            "General Transformation: Result = (Input / Standard Scale) * 100"
        ],
        "explanation": f"When approaching {topic} problems, break down the prompt into known inputs, state the governing equation, and compute step-by-step.",
        "worked_examples": [
            {
                "problem": f"Sample problem on {topic}: Calculate result when base input is 100 with a 20% growth rate.",
                "solution": "Result = 100 * (1 + 20/100) = 120."
            }
        ],
        "shortcuts": [
            f"Apply process of elimination to discard implausible choices in {topic}.",
            "Double-check units before finalizing calculations."
        ],
        "common_mistakes": [
            "Misinterpreting problem conditions or units.",
            "Rushing arithmetic without verifying intermediate steps."
        ],
        "exam_tips": [
            "Spend no more than 60-90 seconds per question."
        ],
        "sample_questions": [
            QuestionSchema(
                question=f"What is the evaluated output for a baseline value of 200 under a standard 25% {topic} rate?",
                option_a="220",
                option_b="250",
                option_c="270",
                option_d="300",
                correct_answer="option_b",
                explanation=f"200 * (1 + 25/100) = 200 * 1.25 = 250.",
                topic=topic,
                category=category,
                difficulty="medium"
            )
        ]
    }
