import random
from typing import List, Dict, Any, Optional
from app.models.schemas import (
    MockTestCreateRequest, MockTestSubmitRequest, MockTestResultResponse,
    MockTestHistorySummarySchema, QuestionSchema, UserAnswerSubmission
)
from app.agents.practice_agent import PracticeAgent
from app.tools.scoring import TestScorer
from app.config.topics import normalize_topic, get_category_for_topic, is_valid_topic, TOPIC_REGISTRY
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
        norm_topic = normalize_topic(topic) if topic != "All" else "All"
        diff = difficulty.lower() if difficulty.lower() in ["easy", "medium", "hard"] else "medium"

        db = SessionLocal()
        try:
            repo = Repository(db)
            generated_schemas: List[QuestionSchema] = []

            # 1. Specific Topic Selected -> NEVER MIX TOPICS
            if norm_topic != "All":
                target_cat = category if category != "All" else get_category_for_topic(norm_topic)
                generated_schemas = PracticeAgent.generate_practice_questions(
                    topic=norm_topic,
                    category=target_cat,
                    difficulty=diff,
                    number_of_questions=number_of_questions
                )

            # 2. Category Selected, All Topics
            elif category != "All":
                cat_topics = [t for t, info in TOPIC_REGISTRY.items() if info["category"].lower() == category.lower()]
                if not cat_topics:
                    cat_topics = ["Percentage", "Profit and Loss", "Probability"]

                q_per_topic = max(1, number_of_questions // len(cat_topics))
                for t in cat_topics:
                    if len(generated_schemas) >= number_of_questions:
                        break
                    needed = min(q_per_topic, number_of_questions - len(generated_schemas))
                    sub_qs = PracticeAgent.generate_practice_questions(
                        topic=t,
                        category=category,
                        difficulty=diff,
                        number_of_questions=needed
                    )
                    generated_schemas.extend(sub_qs)

                # Fill remaining if needed
                while len(generated_schemas) < number_of_questions:
                    t = random.choice(cat_topics)
                    extra = PracticeAgent.generate_practice_questions(
                        topic=t,
                        category=category,
                        difficulty=diff,
                        number_of_questions=1
                    )
                    generated_schemas.extend(extra)

            # 3. All Categories, All Topics
            else:
                all_topic_tuples = [(t, info["category"]) for t, info in TOPIC_REGISTRY.items()]
                sampled_tuples = list(all_topic_tuples)
                random.shuffle(sampled_tuples)

                for t, c in sampled_tuples:
                    if len(generated_schemas) >= number_of_questions:
                        break
                    sub_qs = PracticeAgent.generate_practice_questions(
                        topic=t,
                        category=c,
                        difficulty=diff,
                        number_of_questions=1
                    )
                    generated_schemas.extend(sub_qs)

                while len(generated_schemas) < number_of_questions:
                    t, c = random.choice(all_topic_tuples)
                    extra = PracticeAgent.generate_practice_questions(
                        topic=t,
                        category=c,
                        difficulty=diff,
                        number_of_questions=1
                    )
                    generated_schemas.extend(extra)

            gen_schemas = generated_schemas[:number_of_questions]

            # Retrieve DB models corresponding to the generated question IDs
            questions = []
            for qs in gen_schemas:
                if qs.id:
                    db_q = repo.get_question_by_id(qs.id)
                    if db_q:
                        questions.append(db_q)

            if not questions:
                questions = repo.get_questions(topic=norm_topic, category=category, difficulty=diff, limit=number_of_questions)

            title = f"{category} ({norm_topic}) Aptitude Mock Test - {number_of_questions} Questions ({diff.title()})"
            mock_model = repo.create_mock_test(
                user_id=user_id,
                title=title,
                category=category,
                topic=norm_topic,
                difficulty=diff,
                questions=questions,
                time_limit_minutes=time_limit_minutes
            )

            # User facing question objects strip correct_answer and explanation before submission
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
