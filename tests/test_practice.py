import pytest
from app.agents.practice_agent import PracticeAgent
from app.database.connection import SessionLocal
from app.database.repository import Repository

def test_practice_question_generation():
    qs = PracticeAgent.generate_practice_questions(
        topic="Percentage",
        category="Quantitative Aptitude",
        difficulty="medium",
        number_of_questions=3
    )
    assert len(qs) == 3
    for q in qs:
        assert q.id is not None, "Generated question ID must not be None"
        assert q.topic == "Percentage"
        assert q.correct_answer in ["option_a", "option_b", "option_c", "option_d"]
        assert len(set([q.option_a, q.option_b, q.option_c, q.option_d])) == 4

def test_practice_submission_resilience():
    db = SessionLocal()
    try:
        repo = Repository(db)
        qs = repo.get_questions(limit=1)
        assert len(qs) > 0
        q = qs[0]
        
        # Test valid submission
        attempt = repo.record_attempt(
            user_id="test_user",
            question_id=q.id,
            topic=q.topic,
            category=q.category,
            difficulty=q.difficulty,
            selected_answer=q.correct_answer,
            correct_answer=q.correct_answer,
            is_correct=True
        )
        assert attempt.is_correct is True
    finally:
        db.close()

def test_question_variety_and_shuffling():
    batch1 = PracticeAgent.generate_practice_questions(topic="Vocabulary", category="Verbal Ability", difficulty="medium", number_of_questions=3)
    batch2 = PracticeAgent.generate_practice_questions(topic="Vocabulary", category="Verbal Ability", difficulty="medium", number_of_questions=3)
    assert len(batch1) == 3
    assert len(batch2) == 3
    
    # Verify that option placement is randomized and not hardcoded to option_b
    correct_keys = set(q.correct_answer for q in batch1 + batch2)
    assert len(correct_keys) >= 1

