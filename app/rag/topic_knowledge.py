"""Topic Knowledge Engine containing authoritative, topic-specific educational details
for Quantitative Aptitude, Logical Reasoning, and Verbal Ability topics.
"""

from typing import Dict, Any, List
from app.models.schemas import QuestionSchema
from app.config.topics import normalize_topic, get_category_for_topic

TOPIC_KNOWLEDGE_BASE: Dict[str, Dict[str, Any]] = {
    # --- QUANTITATIVE APTITUDE ---
    "Percentage": {
        "category": "Quantitative Aptitude",
        "definition": "Percentage is a fraction expressed per hundred (%). It represents relative proportions, rate of change, and base comparisons.",
        "core_concepts": [
            "Baseline value selection for percentage changes.",
            "Fraction-to-percentage equivalences (1/2=50%, 1/4=25%, 1/8=12.5%).",
            "Successive percentage change calculation using net change formula."
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
        ]
    },

    "Profit and Loss": {
        "category": "Quantitative Aptitude",
        "definition": "Profit and Loss measures financial gains or losses in transactions involving Cost Price (CP), Selling Price (SP), and Marked Price (MP).",
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
        "explanation": "Profit or Loss percentage is ALWAYS calculated on Cost Price (CP) unless specifically stated otherwise in the problem statement.",
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
        ]
    },

    "Time and Work": {
        "category": "Quantitative Aptitude",
        "definition": "Time and Work analyzes the relationship between worker efficiency, rate of work per day/hour, and total time required to finish a job.",
        "core_concepts": [
            "Rate of work is inversely proportional to completion time.",
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
        ]
    },

    "Probability": {
        "category": "Quantitative Aptitude",
        "definition": "Probability measures the likelihood of an outcome occurring, expressed as a fraction between 0 (impossible) and 1 (certain).",
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
            "Miscounting total outcomes in multi-stage experiments."
        ],
        "exam_tips": [
            "Always verify that favorable outcomes are mutually exclusive when adding probabilities."
        ]
    },

    "Average": {
        "category": "Quantitative Aptitude",
        "definition": "Average (Arithmetic Mean) is the single value that summarizes a collection of numbers by dividing total sum by count.",
        "core_concepts": [
            "Sum = Average * Count.",
            "Weighted average combines groups with different sizes and averages.",
            "Effect of adding, removing, or replacing an element on overall average."
        ],
        "important_formulas": [
            "Average = (Sum of all observations) / (Total number of observations)",
            "New Average after addition = (Old Sum + New Value) / (Old Count + 1)",
            "Combined Avg = (n1*A1 + n2*A2) / (n1 + n2)"
        ],
        "explanation": "To solve average problems, track the total sum before and after any change in group size or values.",
        "worked_examples": [
            {
                "problem": "The average of 5 numbers is 20. If one number 50 is added, what is the new average?",
                "solution": "Old Sum = 5 * 20 = 100. New Sum = 100 + 50 = 150. New Count = 6. New Average = 150 / 6 = 25."
            }
        ],
        "shortcuts": [
            "Deviation method: Assume a baseline average and sum deviations to find true mean."
        ],
        "common_mistakes": [
            "Averaging two averages directly without taking group sizes into account."
        ],
        "exam_tips": [
            "Always work with Total Sum = Average * N."
        ]
    },

    "Speed, Distance and Time": {
        "category": "Quantitative Aptitude",
        "definition": "Speed, Distance and Time analyzes motion, relative velocity between moving objects, train crossings, and river currents.",
        "core_concepts": [
            "Speed = Distance / Time.",
            "Conversion: 1 km/h = 5/18 m/s | 1 m/s = 18/5 km/h.",
            "Relative Speed: Opposite directions -> S1 + S2; Same direction -> |S1 - S2|."
        ],
        "important_formulas": [
            "Speed = Distance / Time",
            "Average Speed for equal distances = (2 * S1 * S2) / (S1 + S2)",
            "Time to cross stationary object of length L = (L_train + L_object) / Speed"
        ],
        "explanation": "Ensure units are consistent (convert km/h to m/s when distances are given in meters). Add train lengths for total distance when crossing.",
        "worked_examples": [
            {
                "problem": "A train 200m long passes a telegraph pole in 10 seconds. Find its speed in km/h.",
                "solution": "Speed = 200m / 10s = 20 m/s. In km/h = 20 * (18/5) = 72 km/h."
            }
        ],
        "shortcuts": [
            "Multiply km/h by 5/18 to convert to m/s instantly."
        ],
        "common_mistakes": [
            "Mixing meters and kilometers without converting units."
        ],
        "exam_tips": [
            "Draw a simple distance line to visualize train crossing scenarios."
        ]
    },

    "Number System": {
        "category": "Quantitative Aptitude",
        "definition": "Number System covers properties of integers, prime numbers, divisibility rules, LCM/HCF, and remainders.",
        "core_concepts": [
            "LCM (Least Common Multiple) and HCF (Highest Common Factor).",
            "Product of two numbers = LCM * HCF.",
            "Divisibility rules for 2, 3, 4, 5, 6, 8, 9, 11."
        ],
        "important_formulas": [
            "Number = (Divisor * Quotient) + Remainder",
            "HCF * LCM = Product of Two Numbers"
        ],
        "explanation": "Use prime factorization to find LCM and HCF efficiently.",
        "worked_examples": [
            {
                "problem": "Find the HCF of 24 and 36.",
                "solution": "24 = 2^3 * 3, 36 = 2^2 * 3^2. HCF = 2^2 * 3 = 12."
            }
        ],
        "shortcuts": [
            "For divisibility by 9, check if sum of digits is divisible by 9."
        ],
        "common_mistakes": [
            "Confusing LCM with HCF when setting up word problems."
        ],
        "exam_tips": [
            "Master prime factorization up to 100 for rapid decomposition."
        ]
    },

    "Algebra": {
        "category": "Quantitative Aptitude",
        "definition": "Algebra deals with variables, linear equations, quadratic equations, and algebraic identities.",
        "core_concepts": [
            "Solving linear equations with one or two variables.",
            "Quadratic equation roots using factoring or quadratic formula.",
            "Algebraic expansion identities."
        ],
        "important_formulas": [
            "(a + b)^2 = a^2 + 2ab + b^2",
            "(a - b)^2 = a^2 - 2ab + b^2",
            "x^2 + y^2 = (x + y)^2 - 2xy",
            "Quadratic Roots x = [-b ± sqrt(b^2 - 4ac)] / (2a)"
        ],
        "explanation": "Substitute given variable relationships systematically to simplify multi-variable word problems.",
        "worked_examples": [
            {
                "problem": "If x + y = 10 and xy = 21, find x^2 + y^2.",
                "solution": "x^2 + y^2 = (x+y)^2 - 2xy = 10^2 - 2(21) = 100 - 42 = 58."
            }
        ],
        "shortcuts": [
            "Use value substitution (e.g. let x=1, y=2) to quickly verify algebraic identity options."
        ],
        "common_mistakes": [
            "Sign errors when transferring terms across equality sign."
        ],
        "exam_tips": [
            "Check if options can be tested directly by substitution."
        ]
    },

    # --- LOGICAL REASONING ---
    "Number Series": {
        "category": "Logical Reasoning",
        "definition": "Number Series evaluates pattern recognition governing sequences of numbers (arithmetic difference, multiplication, squares, cubes).",
        "core_concepts": [
            "Difference pattern analysis (1st and 2nd order differences).",
            "Multiplication/division series.",
            "Square and cube sequences (n^2 + k, n^3 + k)."
        ],
        "important_formulas": [
            "Arithmetic Difference: T_n = T_{n-1} + d",
            "Geometric Progression: T_n = T_1 * r^(n-1)"
        ],
        "explanation": "First check the difference between consecutive numbers. If differences grow rapidly, test for multiplication, squares, or cubes.",
        "worked_examples": [
            {
                "problem": "Find the next number in series: 3, 7, 15, 31, 63, ?",
                "solution": "Pattern: multiply by 2 and add 1. 63 * 2 + 1 = 127."
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
        ]
    },

    "Syllogism": {
        "category": "Logical Reasoning",
        "definition": "Syllogism tests deductive reasoning by evaluating whether given conclusions logically follow from formal premises.",
        "core_concepts": [
            "Categorical statements: All A are B, No A is B, Some A are B, Some A are not B.",
            "Venn Diagram representation.",
            "Definite conclusions vs Possible conclusions."
        ],
        "important_formulas": [
            "All A are B + All B are C => All A are C",
            "Some A are B + All B are C => Some A are C"
        ],
        "explanation": "Draw minimal overlap Venn diagrams to test whether a conclusion MUST hold true under all possible interpretations.",
        "worked_examples": [
            {
                "problem": "Statements: All cats are dogs. All dogs are mammals. Conclusions: I. All cats are mammals.",
                "solution": "Cats ⊂ Dogs ⊂ Mammals. Therefore all cats are mammals holds true definitely."
            }
        ],
        "shortcuts": [
            "100/50 rule: 'All' distributes subject (100), 'Some' distributes neither (50)."
        ],
        "common_mistakes": [
            "Assuming real-world truth overrides given premises."
        ],
        "exam_tips": [
            "Always draw Venn diagrams for complex syllogism questions."
        ]
    },

    "Blood Relations": {
        "category": "Logical Reasoning",
        "definition": "Blood Relations involves analyzing family connections, genealogical trees, and relational puzzles.",
        "core_concepts": [
            "Gender designation (+ for male, - for female).",
            "Generational level mapping.",
            "Direct vs Indirect relations (e.g. maternal uncle, daughter-in-law)."
        ],
        "important_formulas": [
            "Father's/Mother's only son = Self (if male) or Brother",
            "Mother-in-law's only daughter = Wife"
        ],
        "explanation": "Build a generation family tree starting from the reference person mentioned in the prompt.",
        "worked_examples": [
            {
                "problem": "Pointing to a man, Rahul said 'His mother is the only daughter of my mother-in-law.' How is the man related to Rahul?",
                "solution": "Mother-in-law's only daughter = Rahul's wife. Man is wife's son = Rahul's Son."
            }
        ],
        "shortcuts": [
            "Trace backward from 'my' in pointing-to-photo statements."
        ],
        "common_mistakes": [
            "Assuming gender based on name without explicit statement."
        ],
        "exam_tips": [
            "Draw a vertical family tree with generations clearly separated."
        ]
    },

    "Seating Arrangement": {
        "category": "Logical Reasoning",
        "definition": "Seating Arrangement analyzes spatial positioning of individuals in linear rows or circular setups.",
        "core_concepts": [
            "Facing North/South (Left and Right directions).",
            "Circular arrangements facing center vs facing outward.",
            "Immediate left/right vs second/third to the left."
        ],
        "important_formulas": [
            "In linear row facing North: Left is West, Right is East.",
            "In circular arrangement facing center: Clockwise = Left, Counter-clockwise = Right."
        ],
        "explanation": "Start placing individuals with definite positions first, then fill conditional positions.",
        "worked_examples": [
            {
                "problem": "Five friends A, B, C, D, E sit in a row facing North. C is in middle. A is immediate left of C. Who is second to left of E if E is immediate right of C?",
                "solution": "Row: _ A C E _. Immediate left of E is C, second left of E is A."
            }
        ],
        "shortcuts": [
            "Always draw a blank line with position slots first."
        ],
        "common_mistakes": [
            "Confusing left and right when facing South or outward."
        ],
        "exam_tips": [
            "Lock in fixed anchor positions before placing variable members."
        ]
    },

    "Coding-Decoding": {
        "category": "Logical Reasoning",
        "definition": "Coding-Decoding tests the ability to decipher secret rules or letter position transformations used to encode words.",
        "core_concepts": [
            "Alphabetical positions (A=1 to Z=26).",
            "Shift ciphers (+k or -k shifting).",
            "Opposite letter pairs (sum of positions = 27)."
        ],
        "important_formulas": [
            "EJOTY Rule: E=5, J=10, O=15, T=20, Y=25",
            "Opposite position sum = 27"
        ],
        "explanation": "Map letters to numerical positions. Identify the mathematical transformation applied to each letter position.",
        "worked_examples": [
            {
                "problem": "If LIGHT is coded as MJHIU, how is FLAME coded?",
                "solution": "Shift +1: F->G, L->M, A->B, M->N, E->F => GMBNF."
            }
        ],
        "shortcuts": [
            "Remember EJOTY for fast position lookup."
        ],
        "common_mistakes": [
            "Mixing forward and reverse shifts."
        ],
        "exam_tips": [
            "Write down alphabet 1-26 on scratch paper at exam start."
        ]
    },

    # --- VERBAL ABILITY ---
    "Vocabulary": {
        "category": "Verbal Ability",
        "definition": "Vocabulary measures comprehension of word meanings, contextual usage, root origins, synonyms, and antonyms.",
        "core_concepts": [
            "Denotation (literal meaning) vs Connotation (tone).",
            "Synonyms (similar meaning) and Antonyms (opposite meaning).",
            "Root words (Bene, Mal, Chron, Phil, Path)."
        ],
        "important_formulas": [
            "Synonym: Word A ≈ Word B",
            "Antonym: Word A <-> Inverse Word B"
        ],
        "explanation": "Analyze prefixes and roots to infer meanings of unfamiliar words. Match tone and part of speech.",
        "worked_examples": [
            {
                "problem": "Find the closest synonym for METICULOUS.",
                "solution": "Meticulous means paying great attention to detail. Synonym = Precise."
            }
        ],
        "shortcuts": [
            "Connotation Tone Elimination: If target word is positive, discard negative choices."
        ],
        "common_mistakes": [
            "Confusing synonyms with antonyms under pressure."
        ],
        "exam_tips": [
            "Learn 5 root words daily to unlock dozens of vocabulary meanings."
        ]
    },

    "Grammar": {
        "category": "Verbal Ability",
        "definition": "Grammar evaluates rules governing sentence construction, subject-verb agreement, tenses, and modifier placement.",
        "core_concepts": [
            "Subject-Verb Agreement.",
            "Tense Consistency.",
            "Correct use of prepositions and singular pronouns (Each, Neither, Either)."
        ],
        "important_formulas": [
            "Singular Subject -> Singular Verb ('Neither of the candidates WAS selected')",
            "Parallel Structure in lists"
        ],
        "explanation": "Identify the true subject of the sentence (strip prepositional phrases) to check subject-verb agreement.",
        "worked_examples": [
            {
                "problem": "Correct: 'The list of items are on the desk.'",
                "solution": "Subject is 'list' (singular). Correct: 'The list of items IS on the desk.'"
            }
        ],
        "shortcuts": [
            "Ignore words inside commas or prepositional phrases when finding the true subject."
        ],
        "common_mistakes": [
            "Matching verb to nearest plural noun instead of true subject."
        ],
        "exam_tips": [
            "Read sentences aloud mentally to spot unnatural phrasing."
        ]
    },

    "Reading Comprehension": {
        "category": "Verbal Ability",
        "definition": "Reading Comprehension tests passage analysis, main idea identification, contextual inference, and tone assessment.",
        "core_concepts": [
            "Main Idea / Central Theme.",
            "Direct Factual Retrieval.",
            "Inference and Author Tone."
        ],
        "important_formulas": [
            "Inference must be strictly supported by passage text without external assumptions."
        ],
        "explanation": "Read questions first to target specific key facts in the passage efficiently.",
        "worked_examples": [
            {
                "problem": "What is the primary objective of a reading passage?",
                "solution": "Identify the main thesis expressed in the introductory and concluding paragraphs."
            }
        ],
        "shortcuts": [
            "Scan for keywords in questions before reading the entire passage."
        ],
        "common_mistakes": [
            "Choosing options that are true in real life but NOT mentioned in the passage."
        ],
        "exam_tips": [
            "Focus on transition words (However, Therefore, Although) to track author arguments."
        ]
    }
}

def get_topic_details(topic: str) -> Dict[str, Any]:
    """Retrieve detailed topic knowledge data with topic validation and resolution."""
    norm = normalize_topic(topic)
    if norm and norm in TOPIC_KNOWLEDGE_BASE:
        return TOPIC_KNOWLEDGE_BASE[norm]

    # Return topic details for the specified topic name without default topic substitution
    cat = get_category_for_topic(topic)
    return {
        "category": cat,
        "definition": f"{topic} is a core module in {cat}, evaluating problem-solving principles.",
        "core_concepts": [
            f"Understanding foundational rules of {topic}.",
            "Identifying given parameters and target variables.",
            "Applying systematic step-by-step transformations."
        ],
        "important_formulas": [
            f"Core {topic} Principle: Apply standard {cat} principles."
        ],
        "explanation": f"When approaching {topic} problems, break down the prompt into known inputs, state the governing equation, and compute step-by-step.",
        "worked_examples": [
            {
                "problem": f"Sample problem on {topic}: Solve standard step-by-step example.",
                "solution": "Compute result using fundamental principles."
            }
        ],
        "shortcuts": [
            f"Apply process of elimination to discard implausible choices in {topic}."
        ],
        "common_mistakes": [
            "Misinterpreting problem conditions or units."
        ],
        "exam_tips": [
            "Spend no more than 60-90 seconds per question."
        ]
    }
