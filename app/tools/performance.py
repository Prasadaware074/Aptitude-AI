from typing import List, Dict, Any
from app.models.schemas import UserPerformanceSummary
from app.models.database_models import AttemptModel, PerformanceModel
from app.config.settings import settings

class PerformanceAnalyzer:
    """Analyzes historical user attempts and updates performance profiles."""

    @staticmethod
    def analyze_user_history(user_id: str, attempts: List[AttemptModel], perfs: List[PerformanceModel]) -> UserPerformanceSummary:
        if not attempts:
            return UserPerformanceSummary(
                user_id=user_id,
                total_questions_attempted=0,
                overall_accuracy=0.0,
                category_accuracy={},
                topic_accuracy={},
                difficulty_accuracy={},
                recent_trend=[],
                weak_topics=[],
                strong_topics=[],
                topics_needing_revision=[]
            )

        total_attempted = len(attempts)
        total_correct = sum(1 for a in attempts if a.is_correct)
        overall_accuracy = round((total_correct / max(total_attempted, 1)) * 100.0, 2)

        # Topic aggregation
        topic_stats: Dict[str, Dict[str, int]] = {}
        category_stats: Dict[str, Dict[str, int]] = {}
        difficulty_stats: Dict[str, Dict[str, int]] = {}

        for a in attempts:
            t = a.topic
            c = a.category
            d = a.difficulty

            if t not in topic_stats:
                topic_stats[t] = {"total": 0, "correct": 0}
            if c not in category_stats:
                category_stats[c] = {"total": 0, "correct": 0}
            if d not in difficulty_stats:
                difficulty_stats[d] = {"total": 0, "correct": 0}

            topic_stats[t]["total"] += 1
            category_stats[c]["total"] += 1
            difficulty_stats[d]["total"] += 1

            if a.is_correct:
                topic_stats[t]["correct"] += 1
                category_stats[c]["correct"] += 1
                difficulty_stats[d]["correct"] += 1

        topic_accuracy = {
            t: round((s["correct"] / s["total"]) * 100.0, 2)
            for t, s in topic_stats.items()
        }

        category_accuracy = {
            c: round((s["correct"] / s["total"]) * 100.0, 2)
            for c, s in category_stats.items()
        }

        difficulty_accuracy = {
            d: round((s["correct"] / s["total"]) * 100.0, 2)
            for d, s in difficulty_stats.items()
        }

        # Apply configurable threshold to avoid classifying weak topics based on tiny sample sizes
        min_attempts = settings.MIN_ATTEMPTS_FOR_WEAK_ANALYSIS

        weak_topics = [
            t for t, acc in topic_accuracy.items()
            if acc < 60.0 and topic_stats[t]["total"] >= min_attempts
        ]

        strong_topics = [
            t for t, acc in topic_accuracy.items()
            if acc >= 75.0 and topic_stats[t]["total"] >= min_attempts
        ]

        topics_needing_revision = [
            t for t, acc in topic_accuracy.items()
            if acc < 70.0
        ]

        # Recent trend (last 10 attempts)
        sorted_attempts = sorted(attempts, key=lambda x: x.timestamp)
        recent_trend = [
            {
                "topic": a.topic,
                "is_correct": a.is_correct,
                "time_taken": a.time_taken,
                "timestamp": a.timestamp.isoformat() if a.timestamp else ""
            }
            for a in sorted_attempts[-10:]
        ]

        return UserPerformanceSummary(
            user_id=user_id,
            total_questions_attempted=total_attempted,
            overall_accuracy=overall_accuracy,
            category_accuracy=category_accuracy,
            topic_accuracy=topic_accuracy,
            difficulty_accuracy=difficulty_accuracy,
            recent_trend=recent_trend,
            weak_topics=weak_topics,
            strong_topics=strong_topics,
            topics_needing_revision=topics_needing_revision
        )
