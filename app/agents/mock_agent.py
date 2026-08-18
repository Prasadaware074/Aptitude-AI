from typing import List, Dict, Any, Optional
from app.models.schemas import (
    MockTestCreateRequest, MockTestSubmitRequest, MockTestResultResponse,
    MockTestHistorySummarySchema, QuestionSchema, UserAnswerSubmission
)
from app.agents.practice_agent import PracticeAgent
from app.tools.scoring import TestScorer
from app.database.connection import SessionLocal
from app.database.repository import Repository

class MockAgent:
    """Agent responsible for creating timed mock tests and evaluating completed submissions."""

    @staticmethod
    def create_mock_test(
        user_id: str = "default_user",
        category: str = "All",
        topic: str = "All",
        difficulty: str = "medium",
        number_of_questions: int = 10,
        time_limit_minutes: int = 15
    ) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            repo = Repository(db)

            # Retrieve or generate questions
            questions = repo.get_questions(topic=topic, category=category, difficulty=difficulty, limit=number_of_questions)
            
            if len(questions) < number_of_questions:
                needed = number_of_questions - len(questions)
                gen_topic = topic if topic != "All" else "Percentage"
                gen_cat = category if category != "All" else "Quantitative Aptitude"
                gen_qs = PracticeAgent.generate_practice_questions(
                    topic=gen_topic,
                    category=gen_cat,
                    difficulty=difficulty,
                    number_of_questions=needed
                )
                questions = repo.get_questions(topic=topic, category=category, difficulty=difficulty, limit=number_of_questions)

            title = f"{category} ({topic}) Aptitude Mock Test - {number_of_questions} Questions"
            mock_model = repo.create_mock_test(
                user_id=user_id,
                title=title,
                category=category,
                topic=topic,
                difficulty=difficulty,
                questions=questions,
                time_limit_minutes=time_limit_minutes
            )

            # Strip correct answers & explanations for user presentation before test submission
            user_facing_questions = [
                {
                    "id": q.id,
                    "question": q.question,
                    "option_a": q.option_a,
                    "option_b": q.option_b,
                    "option_c": q.option_c,
                    "option_d": q.option_d,
                    "topic": q.topic,
                    "category": q.category,
                    "difficulty": q.difficulty
                }
                for q in questions
            ]

            return {
                "mock_test_id": mock_model.id,
                "title": mock_model.title,
                "total_questions": mock_model.total_questions,
                "time_limit_minutes": mock_model.time_limit_minutes,
                "questions": user_facing_questions
            }
        finally:
            db.close()

    @staticmethod
    def submit_mock_test(mock_test_id: str, submissions: List[UserAnswerSubmission], time_taken_seconds: float = 0.0) -> MockTestResultResponse:
        db = SessionLocal()
        try:
            repo = Repository(db)
            sub_dict = {s.question_id: s.selected_answer for s in submissions if s.selected_answer}
            
            # Save submission & update database models
            mock_model = repo.submit_mock_test(mock_test_id, sub_dict, time_taken_seconds)
            
            # Get full question schemas with answers & explanations
            db_questions = repo.get_mock_test_questions(mock_test_id)
            q_schemas = [
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
                for q in db_questions
            ]

            # Calculate detailed analytics breakdown
            return TestScorer.score_mock_test(
                mock_test_id=mock_test_id,
                questions=q_schemas,
                submissions=submissions,
                time_taken_seconds=time_taken_seconds
            )
        finally:
            db.close()

    @staticmethod
    def get_mock_history(user_id: str = "default_user") -> List[MockTestHistorySummarySchema]:
        from app.models.schemas import MockTestHistorySummarySchema
        db = SessionLocal()
        try:
            repo = Repository(db)
            mocks = repo.get_user_mock_tests(user_id)
            return [
                MockTestHistorySummarySchema(
                    mock_test_id=m.id,
                    title=m.title,
                    category=m.category,
                    topic=m.topic,
                    difficulty=m.difficulty,
                    total_questions=m.total_questions,
                    score=m.score or 0.0,
                    percentage=m.percentage or 0.0,
                    completed=m.completed,
                    completed_at=m.completed_at
                )
                for m in mocks
            ]
        finally:
            db.close()

    @staticmethod
    def get_mock_result(mock_test_id: str) -> Optional[MockTestResultResponse]:
        db = SessionLocal()
        try:
            repo = Repository(db)
            return repo.get_mock_test_result(mock_test_id)
        finally:
            db.close()
