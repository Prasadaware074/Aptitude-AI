from datetime import datetime, timedelta
from typing import List
from app.models.schemas import StudyPlanResponse, StudyPlanItem
from app.agents.performance_agent import PerformanceAgent
from app.agents.llm_factory import get_llm
from app.database.connection import SessionLocal
from app.database.repository import Repository

class StudyPlanAgent:
    """Agent responsible for creating personalized, adaptive daily study plans based on performance metrics."""

    @staticmethod
    def generate_study_plan(user_id: str = "default_user", days: int = 5) -> StudyPlanResponse:
        perf = PerformanceAgent.get_user_performance(user_id)
        
        user_level = getattr(perf, "user_level", "Beginner") or "Beginner"

        db = SessionLocal()
        try:
            repo = Repository(db)

            # Try LLM adaptive plan generation if Gemini configured
            llm = get_llm(temperature=0.3, structured_output_schema=StudyPlanResponse)
            if llm:
                prompt = f"""You are an Expert Aptitude Study Strategist.
Create a {days}-day personalized study schedule for user '{user_id}' at the '{user_level}' level.

User Performance & Level Snapshot:
- Detected User Level: {user_level}
- Overall Accuracy: {perf.overall_accuracy}%
- Weak Topics: {', '.join(perf.weak_topics) if perf.weak_topics else 'None identified yet'}
- Topics Needing Revision: {', '.join(perf.topics_needing_revision) if perf.topics_needing_revision else 'General practice'}
- Strong Topics: {', '.join(perf.strong_topics) if perf.strong_topics else 'Percentage'}

Rules:
1. Tailor target question difficulty and intensity to the '{user_level}' level.
2. Prioritize weak topics first with 'High' priority and specific learning/practice activities.
3. Schedule revision and formula flashcards for medium accuracy topics.
4. Include timed mock test practice for strong topics.
5. Set realistic estimated duration (25-60 mins) and question counts (5-15 questions).
"""
                try:
                    plan = llm.invoke(prompt)
                    if isinstance(plan, StudyPlanResponse):
                        repo.save_study_plan(user_id, plan.summary, [item.model_dump() for item in plan.plan_items])
                        return plan
                except Exception:
                    pass

            # High-quality level-tailored fallback plan generator
            items: List[StudyPlanItem] = []
            today = datetime.now()

            weak = perf.weak_topics or ["Probability", "Time and Work"]
            revision = perf.topics_needing_revision or ["Profit and Loss"]
            strong = perf.strong_topics or ["Percentage", "Vocabulary"]

            q_count = 5 if user_level == "Beginner" else (10 if user_level == "Intermediate" else 15)
            duration = 25 if user_level == "Beginner" else (35 if user_level == "Intermediate" else 45)

            day_idx = 0

            # Day 1 & Day 2: Focus on Weak Topics
            for wt in weak[:2]:
                target_date = (today + timedelta(days=day_idx)).strftime("%Y-%m-%d")
                items.append(
                    StudyPlanItem(
                        date=target_date,
                        topic=wt,
                        activity="Learn Concept & Solve Guided MCQs",
                        estimated_duration_minutes=duration,
                        number_of_questions=q_count,
                        priority="High",
                        reason=f"Detected as a weak topic in {user_level} assessment ({perf.overall_accuracy}% accuracy)."
                    )
                )
                day_idx += 1

            # Day 3: Revision & Flashcard Review
            for rt in revision[:1]:
                target_date = (today + timedelta(days=day_idx)).strftime("%Y-%m-%d")
                items.append(
                    StudyPlanItem(
                        date=target_date,
                        topic=rt,
                        activity="Revise Flashcards & Speed Practice",
                        estimated_duration_minutes=duration - 5,
                        number_of_questions=q_count,
                        priority="Medium",
                        reason=f"Consolidate core formulas and rules for {rt}."
                    )
                )
                day_idx += 1

            # Day 4 & Day 5: Timed Mock Simulation
            for st in strong[:2]:
                if day_idx >= days:
                    break
                target_date = (today + timedelta(days=day_idx)).strftime("%Y-%m-%d")
                items.append(
                    StudyPlanItem(
                        date=target_date,
                        topic=st,
                        activity="Timed Mock Test Simulation",
                        estimated_duration_minutes=duration + 10,
                        number_of_questions=q_count + 5,
                        priority="Low",
                        reason=f"Maintain mastery level on strong topic ({st})."
                    )
                )
                day_idx += 1

            while day_idx < days:
                target_date = (today + timedelta(days=day_idx)).strftime("%Y-%m-%d")
                items.append(
                    StudyPlanItem(
                        date=target_date,
                        topic="Mixed Aptitude Categories",
                        activity="Full Timed Exam Simulation",
                        estimated_duration_minutes=duration + 15,
                        number_of_questions=q_count + 5,
                        priority="High",
                        reason=f"Evaluate real-time speed, accuracy, and overall score readiness for {user_level} level."
                    )
                )
                day_idx += 1

            summary_text = f"Personalized {len(items)}-Day Adaptive Prep Plan ({user_level} Level) based on diagnostic assessment."
            repo.save_study_plan(user_id, summary_text, [item.model_dump() for item in items])

            return StudyPlanResponse(
                user_id=user_id,
                created_at=today.strftime("%Y-%m-%d %H:%M:%S"),
                summary=summary_text,
                plan_items=items
            )
        finally:
            db.close()
