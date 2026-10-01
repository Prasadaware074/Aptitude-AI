import pytest
from app.agents.tutor_agent import TutorAgent
from app.graph.workflow import run_aptitude_workflow

def test_tutor_agent_greetings_and_replies():
    # 1. Test greeting
    reply_greet = TutorAgent.generate_chat_reply(user_id="default_user", query="Hi there!")
    assert "Aptitude AI" in reply_greet

    # 2. Test performance doubt query
    reply_perf = TutorAgent.generate_chat_reply(user_id="default_user", query="What are my weak topics?")
    assert "Overall Accuracy" in reply_perf or "Performance" in reply_perf

    # 3. Test topic query
    reply_topic = TutorAgent.generate_chat_reply(user_id="default_user", query="Explain profit and loss formula", topic="Profit and Loss")
    assert "Profit and Loss" in reply_topic

def test_tutor_agent_general_chat_restriction():
    # Test off-topic general coding, trivia, movies queries get declined
    off_topic_queries = [
        "What is Python?",
        "Write a Java program for binary search",
        "Write a python script to scrape a website using BeautifulSoup",
        "What is the capital of France and its population?",
        "Who won the 2022 FIFA World Cup?",
        "Tell me a story about a flying dragon",
        "How do I bake a chocolate cake?"
    ]
    for q in off_topic_queries:
        reply = TutorAgent.generate_chat_reply(user_id="default_user", query=q)
        assert "AptitudeAI" in reply
        assert "aptitude-focused tutor" in reply or "restricted" in reply.lower() or "quantitative aptitude" in reply.lower()

def test_workflow_chat_routing():
    # Verify greetings route to CHAT node
    state_greet = run_aptitude_workflow("Hello!", user_id="default_user")
    assert state_greet["intent"] == "CHAT"
    assert "Aptitude AI" in state_greet["final_response"]

    # Verify concept lessons route to LEARN node
    state_learn = run_aptitude_workflow("Teach me profit and loss", user_id="default_user")
    assert state_learn["intent"] == "LEARN"
    assert "Lesson" in state_learn["final_response"]

    # Verify out of scope workflow execution
    state_oos = run_aptitude_workflow("What is Python?", user_id="default_user")
    assert state_oos["intent"] == "OUT_OF_SCOPE"
    assert "AptitudeAI" in state_oos["final_response"]
