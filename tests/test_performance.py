import pytest
from app.agents.performance_agent import PerformanceAgent
from app.agents.study_plan_agent import StudyPlanAgent

def test_performance_summary_and_study_plan():
    # Test performance analytics
    perf = PerformanceAgent.get_user_performance("default_user")
    assert perf.user_id == "default_user"
    assert perf.total_questions_attempted >= 0

    # Test study plan generation based on performance
    plan = StudyPlanAgent.generate_study_plan("default_user", days=5)
    assert plan.user_id == "default_user"
    assert len(plan.plan_items) == 5
    assert any(item.priority == "High" for item in plan.plan_items)
