import pytest
from app.agents.router_agent import RouterAgent
from app.graph.workflow import run_aptitude_workflow

def test_router_intent_classification():
    # CHAT
    res_chat = RouterAgent.classify_intent("Hello, who are you?")
    assert res_chat["intent"] == "CHAT"

    # LEARN
    res_learn = RouterAgent.classify_intent("Teach me percentage")
    assert res_learn["intent"] == "LEARN"
    assert res_learn["topic"] == "Percentage"

    res_syn = RouterAgent.classify_intent("teach me synonyms")
    assert res_syn["intent"] == "LEARN"
    assert res_syn["topic"] == "Vocabulary"

    # PRACTICE
    res_prac = RouterAgent.classify_intent("Give me 5 hard questions on ratio and proportion")
    assert res_prac["intent"] == "PRACTICE"
    assert res_prac["topic"] == "Ratio and Proportion"
    assert res_prac["difficulty"] == "hard"
    assert res_prac["number_of_questions"] == 5

    # MOCK
    res_mock = RouterAgent.classify_intent("Start a 20 question mock test")
    assert res_mock["intent"] == "MOCK"
    assert res_mock["number_of_questions"] == 20

    # CARDS
    res_cards = RouterAgent.classify_intent("Give me percentage formula cards")
    assert res_cards["intent"] == "CARDS"

    # PERFORMANCE
    res_perf = RouterAgent.classify_intent("Which topics am I weak at?")
    assert res_perf["intent"] == "PERFORMANCE"

    # STUDY PLAN
    res_plan = RouterAgent.classify_intent("What should I study today?")
    assert res_plan["intent"] == "STUDY_PLAN"

def test_langgraph_workflow_execution():
    state = run_aptitude_workflow("Teach me profit and loss")
    assert state["intent"] == "LEARN"
    assert "Profit and Loss" in state["topic"]
    assert len(state["final_response"]) > 20
