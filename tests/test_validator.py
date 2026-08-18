import pytest
from app.models.schemas import QuestionSchema
from app.tools.question_validator import QuestionValidator

def test_valid_question():
    q = QuestionSchema(
        question="What is 15% of 320?",
        option_a="42",
        option_b="45",
        option_c="48",
        option_d="52",
        correct_answer="option_c",
        explanation="15% of 320 = 15/100 * 320 = 48.",
        topic="Percentage",
        category="Quantitative Aptitude",
        difficulty="easy"
    )
    val = QuestionValidator.validate(q)
    assert val.is_valid is True
    assert len(val.reasons) == 0

def test_invalid_duplicate_options():
    q = QuestionSchema(
        question="What is 10 + 10?",
        option_a="20",
        option_b="20",
        option_c="30",
        option_d="40",
        correct_answer="option_a",
        explanation="10 + 10 = 20",
        topic="Simplification",
        category="Quantitative Aptitude",
        difficulty="easy"
    )
    val = QuestionValidator.validate(q)
    assert val.is_valid is False
    assert any("duplicate" in r.lower() for r in val.reasons)

def test_invalid_correct_answer_key():
    q = QuestionSchema(
        question="What is 5 * 5?",
        option_a="20",
        option_b="25",
        option_c="30",
        option_d="35",
        correct_answer="option_e", # Invalid key
        explanation="5 * 5 = 25",
        topic="Simplification",
        category="Quantitative Aptitude",
        difficulty="easy"
    )
    val = QuestionValidator.validate(q)
    assert val.is_valid is False
    assert any("invalid correct_answer key" in r.lower() for r in val.reasons)

def test_math_calculation_mismatch():
    q = QuestionSchema(
        question="What is 10 + 10?",
        option_a="15",
        option_b="20",
        option_c="25",
        option_d="30",
        correct_answer="option_b",
        explanation="10 + 10 = 25.", # False calculation!
        topic="Simplification",
        category="Quantitative Aptitude",
        difficulty="easy"
    )
    val = QuestionValidator.validate(q)
    assert val.is_valid is False
    assert any("numerical calculation check failed" in r.lower() for r in val.reasons)
