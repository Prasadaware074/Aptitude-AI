import pytest
from app.agents.router_agent import RouterAgent
from app.agents.tutor_agent import TutorAgent
from app.agents.practice_agent import PracticeAgent
from app.agents.learning_agent import LearningAgent
from app.agents.mock_agent import MockAgent
from app.graph.workflow import run_aptitude_workflow
from app.tools.scope_validator import ScopeValidator, RESTRICTION_MESSAGE

def test_scope_validation_and_chatbot_restriction():
    # Allowed queries
    assert ScopeValidator.is_aptitude_query("Teach me Percentage")[0] is True
    assert ScopeValidator.is_aptitude_query("Explain Probability at hard level")[0] is True
    assert ScopeValidator.is_aptitude_query("What is 15% of 240?")[0] is True
    assert ScopeValidator.is_aptitude_query("What are my weak topics?")[0] is True

    # Rejected queries
    assert ScopeValidator.is_aptitude_query("What is Python?")[0] is False
    assert ScopeValidator.is_aptitude_query("Write a Java program for binary search")[0] is False
    assert ScopeValidator.is_aptitude_query("Tell me a movie story")[0] is False
    assert ScopeValidator.is_aptitude_query("How to cook pasta?")[0] is False

    # Check TutorAgent response for rejected query
    reply = TutorAgent.generate_chat_reply(query="What is Python?")
    assert reply == RESTRICTION_MESSAGE

def test_acceptance_scenario_1_learn_probability_hard():
    query = "Teach me Probability at hard level."
    state = run_aptitude_workflow(query)
    assert state["intent"] == "LEARN"
    assert state["topic"] == "Probability"
    assert state["difficulty"] == "hard"
    assert "Probability" in state["final_response"]
    assert "Hard" in state["final_response"]

def test_acceptance_scenario_2_practice_profit_and_loss_easy():
    query = "Give me 10 easy Profit and Loss questions."
    state = run_aptitude_workflow(query)
    assert state["intent"] == "PRACTICE"
    assert state["topic"] == "Profit and Loss"
    assert state["difficulty"] == "easy"
    assert len(state["questions"]) == 10
    for q in state["questions"]:
        assert q["topic"] == "Profit and Loss"

def test_acceptance_scenario_3_practice_blood_relations_hard():
    query = "Give me 10 hard Blood Relations questions."
    state = run_aptitude_workflow(query)
    assert state["intent"] == "PRACTICE"
    assert state["topic"] == "Blood Relations"
    assert state["difficulty"] == "hard"
    assert len(state["questions"]) == 10
    for q in state["questions"]:
        assert q["topic"] == "Blood Relations"

def test_acceptance_scenario_4_mock_probability_medium():
    query = "Create a 20-question medium mock test on Probability."
    state = run_aptitude_workflow(query)
    assert state["intent"] == "MOCK"
    assert state["topic"] == "Probability"
    assert state["difficulty"] == "medium"
    assert len(state["questions"]) == 20
    for q in state["questions"]:
        assert q["topic"] == "Probability"
        assert "correct_answer" not in q or q.get("correct_answer") is None

def test_acceptance_scenario_5_out_of_scope_python():
    query = "What is Python?"
    state = run_aptitude_workflow(query)
    assert state["intent"] == "OUT_OF_SCOPE"
    assert state["final_response"] == RESTRICTION_MESSAGE

def test_acceptance_scenario_6_out_of_scope_java():
    query = "Write a Java program for binary search."
    state = run_aptitude_workflow(query)
    assert state["intent"] == "OUT_OF_SCOPE"
    assert state["final_response"] == RESTRICTION_MESSAGE

def test_acceptance_scenario_7_allowed_math_calculation():
    query = "What is 15% of 240?"
    state = run_aptitude_workflow(query)
    assert state["intent"] != "OUT_OF_SCOPE"
    assert "48" in state["final_response"] or "15%" in state["final_response"] or "240" in state["final_response"]
