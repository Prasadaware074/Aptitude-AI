from app.models.schemas import UserPerformanceSummary
from app.tools.performance import PerformanceAnalyzer
from app.database.connection import SessionLocal
from app.database.repository import Repository

class PerformanceAgent:
    """Agent responsible for aggregating historical attempt data and delivering analytical insights."""

    @staticmethod
    def get_user_performance(user_id: str = "default_user") -> UserPerformanceSummary:
        db = SessionLocal()
        try:
            repo = Repository(db)
            user = repo.update_user_streak(user_id) or repo.get_or_create_user(user_id)
            attempts = repo.get_user_attempts(user_id)
            perfs = repo.get_performance_by_user(user_id)
            summary = PerformanceAnalyzer.analyze_user_history(user_id, attempts, perfs)
            summary.current_streak = user.current_streak or 0
            summary.longest_streak = user.longest_streak or 0
            summary.is_onboarded = user.is_onboarded or False
            summary.user_level = user.user_level or "Beginner"
            return summary
        finally:
            db.close()

    @staticmethod
    def get_weak_topics(user_id: str = "default_user") -> list[str]:
        summary = PerformanceAgent.get_user_performance(user_id)
        return summary.weak_topics
