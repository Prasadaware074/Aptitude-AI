import pytest
from app.agents.mock_agent import MockAgent
from app.models.schemas import UserAnswerSubmission

def test_mock_test_creation_and_submission():
    # 1. Create mock test
    mock = MockAgent.create_mock_test(
        user_id="test_user",
        category="Quantitative Aptitude",
        topic="Percentage",
        difficulty="medium",
        number_of_questions=5,
        time_limit_minutes=10
    )
    assert mock["total_questions"] == 5
    assert len(mock["questions"]) == 5
    
    # Verify answers are hidden in initial output
    for q in mock["questions"]:
        assert "correct_answer" not in q

    # 2. Submit answers
    mock_id = mock["mock_test_id"]
    submissions = [
        UserAnswerSubmission(question_id=q["id"], selected_answer="option_b", time_taken=12.0)
        for q in mock["questions"]
    ]

    result = MockAgent.submit_mock_test(mock_id, submissions, time_taken_seconds=60.0)
    assert result.mock_test_id == mock_id
    assert result.total_questions == 5
    assert result.attempted == 5
    assert result.score >= 0
    assert result.accuracy >= 0.0
    assert len(result.detailed_questions) == 5
    for dq in result.detailed_questions:
        assert dq.question is not None
        assert dq.correct_answer in ["option_a", "option_b", "option_c", "option_d"]
        assert dq.explanation is not None

    # 3. Test mock history retrieval
    history = MockAgent.get_mock_history("test_user")
    assert len(history) >= 1
    found = any(h.mock_test_id == mock_id for h in history)
    assert found is True

    # 4. Test revisiting past mock test result
    revisited = MockAgent.get_mock_result(mock_id)
    assert revisited is not None
    assert revisited.mock_test_id == mock_id
    assert len(revisited.detailed_questions) == 5
