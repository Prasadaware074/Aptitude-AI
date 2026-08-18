from app.agents.tutor_agent import TutorAgent
from app.graph.state import AptitudeState
from app.agents.router_agent import RouterAgent
from app.agents.learning_agent import LearningAgent
from app.agents.practice_agent import PracticeAgent
from app.agents.mock_agent import MockAgent
from app.agents.card_agent import CardAgent
from app.agents.performance_agent import PerformanceAgent
from app.agents.study_plan_agent import StudyPlanAgent
from app.rag.retriever import retrieve_aptitude_context

def chat_node(state: AptitudeState) -> AptitudeState:
    """Executes Tutor Agent logic for conversational Q&A, greetings, and dynamic assistance."""
    user_id = state.get("user_id", "default_user")
    query = state.get("user_query", "")
    topic = state.get("topic", None)

    reply = TutorAgent.generate_chat_reply(user_id=user_id, query=query, topic=topic)
    state["final_response"] = reply
    return state

def router_node(state: AptitudeState) -> AptitudeState:
    """Classifies user intent and populates routing metadata in graph state."""
    query = state.get("user_query", "")
    classified = RouterAgent.classify_intent(query)
    
    state["intent"] = classified["intent"]
    state["topic"] = classified["topic"]
    state["category"] = classified["category"]
    state["difficulty"] = classified["difficulty"]
    state["number_of_questions"] = classified["number_of_questions"]
    return state

def learning_node(state: AptitudeState) -> AptitudeState:
    """Executes Learning Agent logic with RAG context retrieval."""
    query = state.get("user_query", "")
    topic = state.get("topic")
    if not topic:
        import re
        m = re.search(r'(?:teach|explain|lesson|concept|about)\s+(?:me\s+)?(?:on\s+)?([a-zA-Z\s]+)', query, re.IGNORECASE)
        topic = m.group(1).strip().title() if m else "Vocabulary"

    difficulty = state.get("difficulty") or "medium"

    # Retrieve context
    context = retrieve_aptitude_context(f"{topic} {query}", top_k=2)
    state["retrieved_context"] = [context]

    lesson = LearningAgent.generate_lesson(topic, difficulty, query)
    state["final_response"] = f"# Lesson: {lesson.topic}\n\n" \
                             f"### Overview\n{lesson.topic_overview}\n\n" \
                             f"### Definition\n{lesson.definition}\n\n" \
                             f"### Explanation\n{lesson.explanation}\n\n" \
                             f"### Core Formulas\n- " + "\n- ".join(lesson.important_formulas) + "\n\n" \
                             f"### Shortcuts\n- " + "\n- ".join(lesson.shortcuts)
    state["performance"] = lesson.model_dump()
    return state

def practice_node(state: AptitudeState) -> AptitudeState:
    """Executes Practice Agent logic to generate and validate MCQs."""
    topic = state.get("topic") or "Percentage"
    category = state.get("category") or "Quantitative Aptitude"
    difficulty = state.get("difficulty") or "medium"
    count = state.get("number_of_questions") or 5

    qs = PracticeAgent.generate_practice_questions(topic, category, difficulty, count)
    q_dicts = [q.model_dump() for q in qs]
    
    state["questions"] = q_dicts
    state["final_response"] = f"Generated {len(q_dicts)} practice questions for {topic} ({difficulty} difficulty)."
    return state

def mock_node(state: AptitudeState) -> AptitudeState:
    """Executes Mock Test Agent logic."""
    user_id = state.get("user_id", "default_user")
    topic = state.get("topic") or "All"
    category = state.get("category") or "All"
    difficulty = state.get("difficulty") or "medium"
    count = state.get("number_of_questions") or 10

    test_data = MockAgent.create_mock_test(
        user_id=user_id,
        category=category,
        topic=topic,
        difficulty=difficulty,
        number_of_questions=count
    )
    state["questions"] = test_data["questions"]
    state["final_response"] = f"Created mock test '{test_data['title']}' with ID {test_data['mock_test_id']} ({count} questions)."
    state["performance"] = test_data
    return state

def cards_node(state: AptitudeState) -> AptitudeState:
    """Executes Card Agent logic."""
    user_id = state.get("user_id", "default_user")
    topic = state.get("topic") or "Percentage"
    cards = CardAgent.generate_cards_for_topic(topic, "formula", user_id)
    card_dicts = [c.model_dump() for c in cards]

    state["questions"] = card_dicts
    state["final_response"] = f"Retrieved {len(card_dicts)} flashcards for {topic}."
    return state

def performance_node(state: AptitudeState) -> AptitudeState:
    """Executes Performance Agent analytics."""
    user_id = state.get("user_id", "default_user")
    summary = PerformanceAgent.get_user_performance(user_id)
    summary_dict = summary.model_dump()

    state["performance"] = summary_dict
    state["score"] = summary.overall_accuracy
    state["final_response"] = f"Overall Accuracy: {summary.overall_accuracy}%. Weak Topics: {', '.join(summary.weak_topics) if summary.weak_topics else 'None'}."
    return state

def study_plan_node(state: AptitudeState) -> AptitudeState:
    """Executes Study Plan Agent."""
    user_id = state.get("user_id", "default_user")
    plan = StudyPlanAgent.generate_study_plan(user_id)
    plan_dict = plan.model_dump()

    state["performance"] = plan_dict
    state["final_response"] = plan.summary
    return state
