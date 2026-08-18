import pytest
import uuid
from datetime import datetime, timedelta
from app.database.connection import SessionLocal
from app.database.repository import Repository
from app.models.database_models import UserModel
from app.agents.performance_agent import PerformanceAgent
from app.agents.study_plan_agent import StudyPlanAgent
from app.models.schemas import OnboardingSubmitRequest, UserAnswerSubmission

def test_streak_tracking_and_date_progression():
    db = SessionLocal()
    try:
        repo = Repository(db)
        email = f"streak_{uuid.uuid4().hex[:6]}@example.com"
        user = repo.create_user("Streak Learner", email, "password123")
        user_id = user.id

        # Initial registration streak
        assert user.current_streak >= 1
        assert user.longest_streak >= 1

        # Simulate same day activity: streak should stay 1
        repo.update_user_streak(user_id)
        u_same = repo.db.query(UserModel).filter(UserModel.id == user_id).first()
        assert u_same.current_streak == 1

        # Simulate consecutive day activity
        yesterday_str = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
        u_same.last_active_date = yesterday_str
        db.commit()

        repo.update_user_streak(user_id)
        u_next = repo.db.query(UserModel).filter(UserModel.id == user_id).first()
        assert u_next.current_streak == 2
        assert u_next.longest_streak == 2

        # Simulate missed days (>1 day): streak should reset to 1
        past_str = (datetime.utcnow() - timedelta(days=3)).strftime("%Y-%m-%d")
        u_next.last_active_date = past_str
        db.commit()

        repo.update_user_streak(user_id)
        u_reset = repo.db.query(UserModel).filter(UserModel.id == user_id).first()
        assert u_reset.current_streak == 1
        assert u_reset.longest_streak == 2

    finally:
        db.close()

def test_onboarding_diagnostic_assessment_and_level_detection():
    db = SessionLocal()
    try:
        repo = Repository(db)
        email = f"onboard_{uuid.uuid4().hex[:6]}@example.com"
        user = repo.create_user("Onboard Learner", email, "password123")
        user_id = user.id

        assert user.is_onboarded is False
        assert user.user_level == "Beginner"

        # Simulate diagnostic assessment with 100% accuracy -> Advanced level
        q1 = repo.get_questions(limit=1)
        q_id = q1[0].id if q1 else "diag_1"
        correct_ans = q1[0].correct_answer if q1 else "option_c"

        submissions = [
            UserAnswerSubmission(question_id=q_id, selected_answer=correct_ans, topic="Percentage", category="Quantitative Aptitude", difficulty="easy", time_taken=5.0),
            UserAnswerSubmission(question_id=q_id, selected_answer=correct_ans, topic="Profit and Loss", category="Quantitative Aptitude", difficulty="medium", time_taken=6.0),
            UserAnswerSubmission(question_id=q_id, selected_answer=correct_ans, topic="Number Series", category="Logical Reasoning", difficulty="easy", time_taken=4.0),
            UserAnswerSubmission(question_id=q_id, selected_answer=correct_ans, topic="Syllogism", category="Logical Reasoning", difficulty="medium", time_taken=7.0)
        ]

        from app.api.routes import submit_onboarding_endpoint
        req = OnboardingSubmitRequest(user_id=user_id, submissions=submissions)
        res = submit_onboarding_endpoint(req)

        assert res.is_onboarded is True
        assert res.accuracy == 100.0
        assert res.detected_level == "Advanced"

        # Verify database updated
        repo.db.expire_all()
        u_updated = repo.db.query(UserModel).filter(UserModel.id == user_id).first()
        assert u_updated.is_onboarded is True
        assert u_updated.user_level == "Advanced"

        # Verify personalized study plan generated for Advanced level
        plan = StudyPlanAgent.generate_study_plan(user_id, days=5)
        assert plan is not None
        assert "Advanced" in plan.summary or len(plan.plan_items) > 0

    finally:
        db.close()
