import pytest
from app.agents.tutor_agent import TutorAgent
from app.graph.workflow import run_aptitude_workflow

def test_tutor_agent_greetings_and_replies():
    # 1. Test greeting
    reply_greet = TutorAgent.generate_chat_reply(user_id="default_user", query="Hi there!")
    assert "Aptitude AI Tutor" in reply_greet
    assert "Percentage" not in reply_greet or "Lesson: Percentage" not in reply_greet

    # 2. Test performance doubt query
    reply_perf = TutorAgent.generate_chat_reply(user_id="default_user", query="What are my weak topics?")
    assert "Overall Accuracy" in reply_perf or "Performance" in reply_perf

    # 3. Test topic query
    reply_topic = TutorAgent.generate_chat_reply(user_id="default_user", query="Explain profit and loss formula", topic="Profit and Loss")
    assert "Profit and Loss" in reply_topic

def test_workflow_chat_routing():
    # Verify greetings route to CHAT node
    state_greet = run_aptitude_workflow("Hello!", user_id="default_user")
    assert state_greet["intent"] == "CHAT"
    assert "Aptitude AI Tutor" in state_greet["final_response"]

    # Verify concept lessons route to LEARN node
    state_learn = run_aptitude_workflow("Teach me profit and loss", user_id="default_user")
    assert state_learn["intent"] == "LEARN"
    assert "Lesson" in state_learn["final_response"]
