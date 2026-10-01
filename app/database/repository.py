from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from app.models.database_models import (
    UserModel, TopicModel, QuestionModel, AttemptModel,
    MockTestModel, MockTestQuestionModel, FlashcardModel,
    PerformanceModel, StudyPlanModel, ConversationModel
)
from app.models.schemas import QuestionSchema, FlashcardSchema, MockTestResultResponse, UserAnswerSubmission

class Repository:
    def __init__(self, db: Session):
        self.db = db

    # --- User Management ---
    def get_or_create_user(self, user_id: str = "default_user", name: str = "Standard Learner") -> UserModel:
        user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            user = UserModel(id=user_id, name=name)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        return user

    def create_user(self, name: str, email: str, password: str) -> UserModel:
        from app.models.database_models import hash_password
        import secrets
        existing = self.db.query(UserModel).filter(func.lower(UserModel.email) == email.lower()).first()
        if existing:
            raise ValueError("Email is already registered")

        user_id = str(uuid.uuid4())
        token = secrets.token_hex(32)
        pw_hash = hash_password(password)

        today_str = datetime.utcnow().strftime("%Y-%m-%d")
        user = UserModel(
            id=user_id,
            name=name,
            email=email.lower(),
            password_hash=pw_hash,
            token=token,
            current_streak=1,
            longest_streak=1,
            last_active_date=today_str
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_by_email(self, email: str) -> Optional[UserModel]:
        return self.db.query(UserModel).filter(func.lower(UserModel.email) == email.lower()).first()

    def get_user_by_token(self, token: str) -> Optional[UserModel]:
        if not token:
            return None
        return self.db.query(UserModel).filter(UserModel.token == token).first()

    def authenticate_user(self, email: str, password: str) -> Optional[UserModel]:
        from app.models.database_models import verify_password
        import secrets
        user = self.get_user_by_email(email)
        if not user or not user.password_hash:
            return None
        if not verify_password(password, user.password_hash):
            return None

        user.token = secrets.token_hex(32)
        self.db.commit()
        self.db.refresh(user)
        self.update_user_streak(user.id)
        return user

    def update_user_streak(self, user_id: str) -> Optional[UserModel]:
        user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            return None

        today_str = datetime.utcnow().strftime("%Y-%m-%d")
        if user.last_active_date == today_str:
            return user

        if not user.last_active_date:
            user.current_streak = 1
        else:
            try:
                last_date = datetime.strptime(user.last_active_date, "%Y-%m-%d").date()
                today_date = datetime.utcnow().date()
                diff = (today_date - last_date).days
                if diff == 1:
                    user.current_streak = (user.current_streak or 0) + 1
                elif diff > 1:
                    user.current_streak = 1
                else:
                    if not user.current_streak:
                        user.current_streak = 1
            except Exception:
                user.current_streak = 1

        if (user.current_streak or 0) > (user.longest_streak or 0):
            user.longest_streak = user.current_streak

        user.last_active_date = today_str
        self.db.commit()
        self.db.refresh(user)
        return user

    def complete_onboarding(self, user_id: str, level: str, score: float) -> UserModel:
        user = self.get_or_create_user(user_id)
        user.is_onboarded = True
        user.user_level = level
        user.diagnostic_score = score
        self.db.commit()
        self.db.refresh(user)
        self.update_user_streak(user_id)
        return user

    # --- Questions ---
    def add_question(self, q: QuestionSchema) -> QuestionModel:
        q_id = q.id or str(uuid.uuid4())
        model = QuestionModel(
            id=q_id,
            question=q.question,
            option_a=q.option_a,
            option_b=q.option_b,
            option_c=q.option_c,
            option_d=q.option_d,
            correct_answer=q.correct_answer,
            explanation=q.explanation,
            topic=q.topic,
            category=q.category,
            difficulty=q.difficulty,
            is_validated=True
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def get_questions(self, topic: Optional[str] = None, category: Optional[str] = None, difficulty: Optional[str] = None, limit: int = 10) -> List[QuestionModel]:
        query = self.db.query(QuestionModel)
        if topic and topic.lower() != "all":
            query = query.filter(func.lower(QuestionModel.topic) == topic.lower())
        if category and category.lower() != "all":
            query = query.filter(func.lower(QuestionModel.category) == category.lower())
        if difficulty and difficulty.lower() != "all":
            query = query.filter(func.lower(QuestionModel.difficulty) == difficulty.lower())
        return query.order_by(func.random()).limit(limit).all()

    def get_question_by_id(self, question_id: str) -> Optional[QuestionModel]:
        return self.db.query(QuestionModel).filter(QuestionModel.id == question_id).first()

    # --- Attempts & Performance ---
    def record_attempt(self, user_id: str, question_id: Optional[str], topic: str, category: str, difficulty: str, selected_answer: str, correct_answer: str, is_correct: bool, time_taken: float = 0.0) -> AttemptModel:
        self.get_or_create_user(user_id)
        attempt = AttemptModel(
            user_id=user_id,
            question_id=question_id,
            topic=topic,
            category=category,
            difficulty=difficulty,
            selected_answer=selected_answer,
            correct_answer=correct_answer,
            is_correct=is_correct,
            time_taken=time_taken,
            timestamp=datetime.utcnow()
        )
        self.db.add(attempt)
        
        # Update topic performance table
        perf = self.db.query(PerformanceModel).filter(
            PerformanceModel.user_id == user_id,
            func.lower(PerformanceModel.topic) == topic.lower()
        ).first()

        if not perf:
            perf = PerformanceModel(
                user_id=user_id,
                topic=topic,
                total_attempted=1,
                total_correct=1 if is_correct else 0,
                accuracy=100.0 if is_correct else 0.0
            )
            self.db.add(perf)
        else:
            perf.total_attempted += 1
            if is_correct:
                perf.total_correct += 1
            perf.accuracy = round((perf.total_correct / perf.total_attempted) * 100.0, 2)
            perf.last_updated = datetime.utcnow()

        self.db.commit()
        self.db.refresh(attempt)
        return attempt

    def get_user_attempts(self, user_id: str = "default_user") -> List[AttemptModel]:
        return self.db.query(AttemptModel).filter(AttemptModel.user_id == user_id).order_by(desc(AttemptModel.timestamp)).all()

    def get_performance_by_user(self, user_id: str = "default_user") -> List[PerformanceModel]:
        return self.db.query(PerformanceModel).filter(PerformanceModel.user_id == user_id).all()

    # --- Mock Tests ---
    def create_mock_test(self, user_id: str, title: str, category: str, topic: str, difficulty: str, questions: List[QuestionModel], time_limit_minutes: int) -> MockTestModel:
        self.get_or_create_user(user_id)
        mock = MockTestModel(
            user_id=user_id,
            title=title,
            category=category,
            topic=topic,
            difficulty=difficulty,
            total_questions=len(questions),
            time_limit_minutes=time_limit_minutes,
            completed=False
        )
        self.db.add(mock)
        self.db.commit()
        self.db.refresh(mock)

        for q in questions:
            mtq = MockTestQuestionModel(
                mock_test_id=mock.id,
                question_id=q.id
            )
            self.db.add(mtq)
        self.db.commit()
        return mock

    def get_mock_test(self, mock_test_id: str) -> Optional[MockTestModel]:
        return self.db.query(MockTestModel).filter(MockTestModel.id == mock_test_id).first()

    def get_mock_test_questions(self, mock_test_id: str) -> List[QuestionModel]:
        mtqs = self.db.query(MockTestQuestionModel).filter(MockTestQuestionModel.mock_test_id == mock_test_id).all()
        q_ids = [mtq.question_id for mtq in mtqs]
        return self.db.query(QuestionModel).filter(QuestionModel.id.in_(q_ids)).all()

    def submit_mock_test(self, mock_test_id: str, submissions: Dict[str, str], total_time_seconds: float) -> MockTestModel:
        mock = self.get_mock_test(mock_test_id)
        if not mock:
            raise ValueError(f"Mock test {mock_test_id} not found")

        if mock.completed:
            return mock

        mtqs = self.db.query(MockTestQuestionModel).filter(MockTestQuestionModel.mock_test_id == mock_test_id).all()
        
        # Calculate server-side elapsed time if created_at is available
        actual_time = total_time_seconds
        if mock.created_at:
            server_elapsed = (datetime.utcnow() - mock.created_at).total_seconds()
            if server_elapsed > 0:
                actual_time = max(total_time_seconds, server_elapsed)

        correct_count = 0
        for mtq in mtqs:
            q = self.get_question_by_id(mtq.question_id)
            if not q:
                continue
            selected = submissions.get(mtq.question_id)
            mtq.user_selected = selected
            if selected and selected.lower() == q.correct_answer.lower():
                mtq.is_correct = True
                correct_count += 1
            else:
                mtq.is_correct = False

            # Record attempt in history
            if selected:
                self.record_attempt(
                    user_id=mock.user_id,
                    question_id=q.id,
                    topic=q.topic,
                    category=q.category,
                    difficulty=q.difficulty,
                    selected_answer=selected,
                    correct_answer=q.correct_answer,
                    is_correct=(selected.lower() == q.correct_answer.lower()),
                    time_taken=actual_time / max(len(mtqs), 1)
                )

        mock.score = float(correct_count)
        mock.percentage = round((correct_count / max(len(mtqs), 1)) * 100.0, 2)
        mock.completed = True
        mock.completed_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(mock)
        return mock

    def get_user_mock_tests(self, user_id: str = "default_user") -> List[MockTestModel]:
        return self.db.query(MockTestModel).filter(MockTestModel.user_id == user_id).order_by(desc(MockTestModel.created_at)).all()

    def get_mock_test_result(self, mock_test_id: str) -> Optional[MockTestResultResponse]:
        from app.tools.scoring import TestScorer
        mock = self.get_mock_test(mock_test_id)
        if not mock:
            return None

        mtqs = self.db.query(MockTestQuestionModel).filter(MockTestQuestionModel.mock_test_id == mock_test_id).all()
        q_map = {q.id: q for q in self.db.query(QuestionModel).filter(QuestionModel.id.in_([m.question_id for m in mtqs])).all()}

        questions: List[QuestionSchema] = []
        submissions: List[UserAnswerSubmission] = []

        for mtq in mtqs:
            q = q_map.get(mtq.question_id)
            if not q:
                continue
            questions.append(
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
            submissions.append(
                UserAnswerSubmission(
                    question_id=mtq.question_id,
                    selected_answer=mtq.user_selected,
                    time_taken=0.0
                )
            )

        return TestScorer.score_mock_test(
            mock_test_id=mock_test_id,
            questions=questions,
            submissions=submissions,
            time_taken_seconds=0.0
        )

    # --- Flashcards ---
    def add_flashcard(self, card: FlashcardSchema) -> FlashcardModel:
        model = FlashcardModel(
            id=card.id or str(uuid.uuid4()),
            user_id=card.user_id or "default_user",
            card_type=card.card_type,
            topic=card.topic,
            category=card.category,
            title=card.title,
            content=card.content,
            example=card.example
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def get_flashcards(self, user_id: str = "default_user", topic: Optional[str] = None, card_type: Optional[str] = None) -> List[FlashcardModel]:
        query = self.db.query(FlashcardModel).filter(FlashcardModel.user_id == user_id)
        if topic and topic.lower() != "all":
            query = query.filter(func.lower(FlashcardModel.topic) == topic.lower())
        if card_type and card_type.lower() != "all":
            query = query.filter(func.lower(FlashcardModel.card_type) == card_type.lower())
        return query.order_by(desc(FlashcardModel.created_at)).all()

    # --- Study Plans ---
    def save_study_plan(self, user_id: str, summary: str, plan_data: List[Dict[str, Any]]) -> StudyPlanModel:
        model = StudyPlanModel(
            user_id=user_id,
            summary=summary,
            plan_data=plan_data
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def get_latest_study_plan(self, user_id: str = "default_user") -> Optional[StudyPlanModel]:
        return self.db.query(StudyPlanModel).filter(StudyPlanModel.user_id == user_id).order_by(desc(StudyPlanModel.created_at)).first()

    # --- Conversations ---
    def log_conversation(self, user_id: str, user_message: str, agent_response: str, intent: str) -> ConversationModel:
        self.get_or_create_user(user_id)
        conv = ConversationModel(
            user_id=user_id,
            user_message=user_message,
            agent_response=agent_response,
            intent=intent
        )
        self.db.add(conv)
        self.db.commit()
        return conv
