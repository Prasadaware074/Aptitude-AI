import logging
from app.database.connection import init_db_schema, SessionLocal
from app.database.repository import Repository
from app.models.schemas import QuestionSchema, FlashcardSchema

logger = logging.getLogger(__name__)

SAMPLE_QUESTIONS = [
    # Quantitative - Percentage
    QuestionSchema(
        question="If the price of sugar increases by 25%, by what percentage should a household reduce its consumption so that the expenditure remains the same?",
        option_a="15%",
        option_b="20%",
        option_c="25%",
        option_d="30%",
        correct_answer="option_b",
        explanation="Reduction % = [r / (100 + r)] * 100 = [25 / 125] * 100 = 20%.",
        topic="Percentage",
        category="Quantitative Aptitude",
        difficulty="medium"
    ),
    QuestionSchema(
        question="What is 15% of 320?",
        option_a="42",
        option_b="45",
        option_c="48",
        option_d="52",
        correct_answer="option_c",
        explanation="15% of 320 = (15 / 100) * 320 = 48.",
        topic="Percentage",
        category="Quantitative Aptitude",
        difficulty="easy"
    ),
    # Quantitative - Profit and Loss
    QuestionSchema(
        question="A shopkeeper sells an item for $240 at a profit of 20%. What was the cost price of the item?",
        option_a="$180",
        option_b="$200",
        option_c="$210",
        option_d="$220",
        correct_answer="option_b",
        explanation="CP = SP / (1 + Profit%/100) = 240 / 1.20 = $200.",
        topic="Profit and Loss",
        category="Quantitative Aptitude",
        difficulty="easy"
    ),
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
    ),
    # Quantitative - Ratio and Proportion
    QuestionSchema(
        question="The ratio of two numbers is 3:5. If 10 is added to both numbers, the ratio becomes 5:7. Find the original numbers.",
        option_a="9 and 15",
        option_b="12 and 20",
        option_c="15 and 25",
        option_d="18 and 30",
        correct_answer="option_c",
        explanation="(3x + 10) / (5x + 10) = 5 / 7 => 21x + 70 = 25x + 50 => 4x = 20 => x = 5. Numbers are 15 and 25.",
        topic="Ratio and Proportion",
        category="Quantitative Aptitude",
        difficulty="medium"
    ),
    QuestionSchema(
        question="The ratio of two numbers is 4:5 and their sum is 180. What is the larger number?",
        option_a="80",
        option_b="90",
        option_c="100",
        option_d="110",
        correct_answer="option_c",
        explanation="4x + 5x = 9x = 180 => x = 20. Larger number = 5(20) = 100.",
        topic="Ratio and Proportion",
        category="Quantitative Aptitude",
        difficulty="easy"
    ),
    # Quantitative - Time and Work
    QuestionSchema(
        question="A can complete a piece of work in 12 days, and B can complete it in 24 days. How many days will they take to complete the work working together?",
        option_a="6 days",
        option_b="8 days",
        option_c="9 days",
        option_d="10 days",
        correct_answer="option_b",
        explanation="Combined 1-day work = 1/12 + 1/24 = 3/24 = 1/8. Total time taken = 8 days.",
        topic="Time and Work",
        category="Quantitative Aptitude",
        difficulty="medium"
    ),
    QuestionSchema(
        question="Worker A completes a task in 10 days and Worker B in 15 days. Working together, in how many days will they finish?",
        option_a="5 days",
        option_b="6 days",
        option_c="7 days",
        option_d="8 days",
        correct_answer="option_b",
        explanation="Combined time = (10 * 15) / (10 + 15) = 150 / 25 = 6 days.",
        topic="Time and Work",
        category="Quantitative Aptitude",
        difficulty="easy"
    ),
    # Quantitative - Probability
    QuestionSchema(
        question="Two unbiased coins are tossed simultaneously. What is the probability of getting at least one head?",
        option_a="1/4",
        option_b="1/2",
        option_c="3/4",
        option_d="1",
        correct_answer="option_c",
        explanation="Sample space = {HH, HT, TH, TT}, total = 4. Favorable = {HH, HT, TH}, count = 3. P = 3/4.",
        topic="Probability",
        category="Quantitative Aptitude",
        difficulty="easy"
    ),
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
    ),
    # Logical Reasoning - Number Series
    QuestionSchema(
        question="Find the next number in the series: 2, 6, 12, 20, 30, ?",
        option_a="38",
        option_b="40",
        option_c="42",
        option_d="44",
        correct_answer="option_c",
        explanation="Pattern: 1*2, 2*3, 3*4, 4*5, 5*6, 6*7 = 42.",
        topic="Number Series",
        category="Logical Reasoning",
        difficulty="easy"
    ),
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
    ),
    # Logical Reasoning - Coding-Decoding
    QuestionSchema(
        question="If 'CAT' is coded as 3120 in a certain code language, how is 'DOG' coded?",
        option_a="4157",
        option_b="41515",
        option_c="41507",
        option_d="41407",
        correct_answer="option_a",
        explanation="Alphabetical positions: C=3, A=1, T=20 -> 3120. DOG: D=4, O=15, G=7 -> 4157.",
        topic="Coding-Decoding",
        category="Logical Reasoning",
        difficulty="easy"
    ),
    QuestionSchema(
        question="If 'MIND' is coded as 'KGLB', how is 'DIAGRAM' coded?",
        option_a="BGYEPYK",
        option_b="BGYPEYK",
        option_c="BGYEPYE",
        option_d="CGYEPYK",
        correct_answer="option_a",
        explanation="Each letter is shifted backward by 2 (-2). Applying -2 to DIAGRAM yields BGYEPYK.",
        topic="Coding-Decoding",
        category="Logical Reasoning",
        difficulty="medium"
    ),
    # Verbal Ability - Vocabulary
    QuestionSchema(
        question="Choose the word most SIMILAR in meaning to 'METICULOUS':",
        option_a="Careless",
        option_b="Thorough and precise",
        option_c="Hasty",
        option_d="Aggressive",
        correct_answer="option_b",
        explanation="'Meticulous' means showing great attention to detail; very careful and precise.",
        topic="Vocabulary",
        category="Verbal Ability",
        difficulty="easy"
    ),
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
    ),
    # Verbal Ability - Grammar
    QuestionSchema(
        question="Identify the error in the sentence: 'Neither of the candidate were qualified for the position.'",
        option_a="Neither of",
        option_b="the candidate",
        option_c="were qualified",
        option_d="for the position",
        correct_answer="option_c",
        explanation="'Neither' takes a singular verb. The correct phrase is 'was qualified' instead of 'were qualified'.",
        topic="Grammar",
        category="Verbal Ability",
        difficulty="medium"
    ),
    QuestionSchema(
        question="Identify the error in: 'Each of the students have completed their assignment.'",
        option_a="Each of",
        option_b="the students",
        option_c="have completed",
        option_d="their assignment",
        correct_answer="option_c",
        explanation="'Each' takes a singular verb: 'has completed' instead of 'have completed'.",
        topic="Grammar",
        category="Verbal Ability",
        difficulty="medium"
    )
]

SAMPLE_FLASHCARDS = [
    # Percentage
    FlashcardSchema(
        card_type="formula",
        topic="Percentage",
        category="Quantitative Aptitude",
        title="Percentage Change Formula",
        content="Percentage Increase/Decrease = |New Value - Original Value| / Original Value * 100%",
        example="If price goes from 80 to 100: (20 / 80) * 100 = 25% increase."
    ),
    FlashcardSchema(
        card_type="shortcut",
        topic="Percentage",
        category="Quantitative Aptitude",
        title="Successive Percentage Change",
        content="Net % Change = a + b + (a * b) / 100 where a and b are successive percentage changes.",
        example="10% increase followed by 20% increase: 10 + 20 + (10*20)/100 = 32%."
    ),
    FlashcardSchema(
        card_type="concept",
        topic="Percentage",
        category="Quantitative Aptitude",
        title="Baseline Denominator Concept",
        content="Always place the original baseline initial value in the denominator when calculating percentage increase or decrease.",
        example="Comparing current revenue $120 to last year's $100: base is 100, gain is +20%."
    ),
    FlashcardSchema(
        card_type="mistake",
        topic="Percentage",
        category="Quantitative Aptitude",
        title="Linear Addition Mistake",
        content="Avoid adding successive percentage changes linearly (e.g. +20% then -20% does NOT return to original value).",
        example="100 + 20% = 120. 120 - 20% = 96 (net 4% loss)."
    ),

    # Profit and Loss
    FlashcardSchema(
        card_type="formula",
        topic="Profit and Loss",
        category="Quantitative Aptitude",
        title="Cost Price & Selling Price Formulas",
        content="Profit % = (SP - CP) / CP * 100 | CP = (SP * 100) / (100 + Profit %)",
        example="SP = 120, Profit = 20% => CP = (120 * 100) / 120 = 100."
    ),
    FlashcardSchema(
        card_type="shortcut",
        topic="Profit and Loss",
        category="Quantitative Aptitude",
        title="Equal SP Profit & Loss Loss % Rule",
        content="If two items are sold at the same Selling Price, one at x% profit and one at x% loss, net outcome is ALWAYS a loss of (x / 10)^2 %.",
        example="Selling two items at $500 each, one at 20% profit and one at 20% loss: net loss = (20/10)^2 = 4%."
    ),
    FlashcardSchema(
        card_type="concept",
        topic="Profit and Loss",
        category="Quantitative Aptitude",
        title="Marked Price & Discount Baseline",
        content="Profit/Loss % is always calculated on Cost Price (CP), whereas Discount % is always calculated on Marked Price (MP).",
        example="MP = 150, Discount = 10% => SP = 135."
    ),

    # Ratio and Proportion
    FlashcardSchema(
        card_type="formula",
        topic="Ratio and Proportion",
        category="Quantitative Aptitude",
        title="Share Distribution Formula",
        content="If sum S is divided in ratio a:b:c, share of A = [a / (a + b + c)] * S.",
        example="Divide $300 in ratio 2:3:5 => Share of B = (3 / 10) * 300 = $90."
    ),
    FlashcardSchema(
        card_type="shortcut",
        topic="Ratio and Proportion",
        category="Quantitative Aptitude",
        title="Compounded Ratio & Proportion Rule",
        content="In proportion a:b :: c:d, Product of Extremes (a * d) = Product of Means (b * c).",
        example="3:5 :: 9:x => 3x = 45 => x = 15."
    ),

    # Time and Work
    FlashcardSchema(
        card_type="formula",
        topic="Time and Work",
        category="Quantitative Aptitude",
        title="Combined Work Formula",
        content="If A takes x days and B takes y days, combined time = (x * y) / (x + y) days.",
        example="A=10, B=15 => (10*15)/(10+15) = 150/25 = 6 days."
    ),
    FlashcardSchema(
        card_type="shortcut",
        topic="Time and Work",
        category="Quantitative Aptitude",
        title="LCM Efficiency Method",
        content="Assume total units of work = LCM of days taken. Daily work = Total Units / Days.",
        example="A=10 days, B=15 days. Total work = 30 units. A=3 u/day, B=2 u/day. Combined = 30 / 5 = 6 days."
    ),

    # Speed Distance and Time
    FlashcardSchema(
        card_type="formula",
        topic="Speed Distance and Time",
        category="Quantitative Aptitude",
        title="Average Speed & Unit Conversion",
        content="Average Speed = 2xy / (x + y) for equal distances. Speed in m/s = Speed in km/h * (5 / 18).",
        example="72 km/h = 72 * 5 / 18 = 20 m/s."
    ),

    # Probability
    FlashcardSchema(
        card_type="concept",
        topic="Probability",
        category="Quantitative Aptitude",
        title="Basic Probability Definition",
        content="Probability P(E) = Number of Favorable Outcomes / Total Possible Outcomes. P(E) + P(Not E) = 1.",
        example="Probability of drawing an Ace from a deck of 52 = 4 / 52 = 1/13."
    ),

    # Logical Reasoning - Number Series & Coding
    FlashcardSchema(
        card_type="shortcut",
        topic="Number Series",
        category="Logical Reasoning",
        title="Difference Pattern Trick",
        content="Subtract consecutive terms to check for constant arithmetic difference or n*(n+1) patterns.",
        example="2, 6, 12, 20 (+4, +6, +8...) -> next term is 20 + 10 = 30."
    ),
    FlashcardSchema(
        card_type="shortcut",
        topic="Coding-Decoding",
        category="Logical Reasoning",
        title="EJOTY & Alphabet Opposites",
        content="E=5, J=10, O=15, T=20, Y=25. Sum of opposite alphabetical positions always equals 27.",
        example="A(1) + Z(26) = 27 | B(2) + Y(25) = 27."
    ),
    FlashcardSchema(
        card_type="concept",
        topic="Blood Relations",
        category="Logical Reasoning",
        title="Family Tree Diagramming",
        content="Use '+' for male, '-' for female, '=' for married couples, and vertical lines for generational descendants.",
        example="A+ = B- (Married pair), line down to C+ (Son)."
    ),

    # Verbal Ability - Vocabulary & Grammar
    FlashcardSchema(
        card_type="vocabulary",
        topic="Vocabulary",
        category="Verbal Ability",
        title="Meticulous",
        content="Meaning: Showing great attention to detail; very careful and precise. Antonym: Careless.",
        example="She was meticulous when double-checking calculations."
    ),
    FlashcardSchema(
        card_type="vocabulary",
        topic="Vocabulary",
        category="Verbal Ability",
        title="Candid",
        content="Meaning: Truthful and straightforward; frank. Antonym: Deceitful.",
        example="He gave a candid opinion on the proposed plan."
    ),
    FlashcardSchema(
        card_type="vocabulary",
        topic="Vocabulary",
        category="Verbal Ability",
        title="Pragmatic",
        content="Meaning: Dealing with things sensibly and realistically based on practical considerations.",
        example="Taking practice questions regularly is a pragmatic strategy."
    ),
    FlashcardSchema(
        card_type="concept",
        topic="Grammar",
        category="Verbal Ability",
        title="Subject-Verb Agreement",
        content="Singular subjects take singular verbs; plural subjects take plural verbs. Words like 'each', 'every', 'either' take singular verbs.",
        example="Each of the students HAS submitted the assignment."
    )
]

def seed_database():
    """Initialize database schema and populate initial seed data."""
    init_db_schema()
    db = SessionLocal()
    try:
        repo = Repository(db)
        repo.get_or_create_user("default_user", "Standard Learner")

        # Refresh questions if less than full sample count
        existing_q = repo.get_questions(limit=100)
        if len(existing_q) < len(SAMPLE_QUESTIONS):
            logger.info("Seeding sample aptitude questions across all topics...")
            for q in SAMPLE_QUESTIONS:
                repo.add_question(q)

        # Refresh flashcards if less than full sample count
        existing_cards = repo.get_flashcards()
        if len(existing_cards) < len(SAMPLE_FLASHCARDS):
            logger.info("Seeding sample flashcards across all topics...")
            for card in SAMPLE_FLASHCARDS:
                repo.add_flashcard(card)

        # Seed initial user attempts for performance calculation demonstration
        attempts = repo.get_user_attempts("default_user")
        if not attempts:
            logger.info("Seeding initial performance attempt history...")
            # Probability - low accuracy
            repo.record_attempt("default_user", None, "Probability", "Quantitative Aptitude", "easy", "option_a", "option_c", False, 45.0)
            repo.record_attempt("default_user", None, "Probability", "Quantitative Aptitude", "medium", "option_b", "option_d", False, 50.0)
            
            # Time and Work - medium accuracy
            repo.record_attempt("default_user", None, "Time and Work", "Quantitative Aptitude", "medium", "option_b", "option_b", True, 30.0)
            repo.record_attempt("default_user", None, "Time and Work", "Quantitative Aptitude", "hard", "option_a", "option_c", False, 60.0)

            # Percentage - high accuracy
            repo.record_attempt("default_user", None, "Percentage", "Quantitative Aptitude", "easy", "option_c", "option_c", True, 15.0)
            repo.record_attempt("default_user", None, "Percentage", "Quantitative Aptitude", "medium", "option_b", "option_b", True, 20.0)

        logger.info("Database seeded successfully across all topics.")
    finally:
        db.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed_database()
