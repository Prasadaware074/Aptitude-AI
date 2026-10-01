from langgraph.graph import StateGraph, END
from app.graph.state import AptitudeState
from app.graph.nodes import (
    router_node, out_of_scope_node, chat_node, learning_node, practice_node,
    mock_node, cards_node, performance_node, study_plan_node
)

def route_intent(state: AptitudeState) -> str:
    """Conditional edge router function."""
    intent = state.get("intent", "CHAT").upper()
    if intent == "OUT_OF_SCOPE":
        return "out_of_scope"
    elif intent == "CHAT":
        return "chat"
    elif intent == "LEARN":
        return "learning"
    elif intent == "PRACTICE":
        return "practice"
    elif intent == "MOCK":
        return "mock"
    elif intent == "CARDS":
        return "cards"
    elif intent == "PERFORMANCE":
        return "performance"
    elif intent == "STUDY_PLAN":
        return "study_plan"
    else:
        return "chat"

def build_aptitude_graph() -> StateGraph:
    """Construct and compile the LangGraph multi-agent workflow graph."""
    workflow = StateGraph(AptitudeState)

    # Add Nodes
    workflow.add_node("router", router_node)
    workflow.add_node("out_of_scope", out_of_scope_node)
    workflow.add_node("chat", chat_node)
    workflow.add_node("learning", learning_node)
    workflow.add_node("practice", practice_node)
    workflow.add_node("mock", mock_node)
    workflow.add_node("cards", cards_node)
    workflow.add_node("performance", performance_node)
    workflow.add_node("study_plan", study_plan_node)

    # Set Entry Point
    workflow.set_entry_point("router")

    # Add Conditional Edges from Router
    workflow.add_conditional_edges(
        "router",
        route_intent,
        {
            "out_of_scope": "out_of_scope",
            "chat": "chat",
            "learning": "learning",
            "practice": "practice",
            "mock": "mock",
            "cards": "cards",
            "performance": "performance",
            "study_plan": "study_plan"
        }
    )

    # Add End Edges
    workflow.add_edge("out_of_scope", END)
    workflow.add_edge("chat", END)
    workflow.add_edge("learning", END)
    workflow.add_edge("practice", END)
    workflow.add_edge("mock", END)
    workflow.add_edge("cards", END)
    workflow.add_edge("performance", END)
    workflow.add_edge("study_plan", END)

    return workflow.compile()

# Singleton compiled graph instance
aptitude_graph = build_aptitude_graph()

def run_aptitude_workflow(user_query: str, user_id: str = "default_user") -> AptitudeState:
    """Execute natural language query through compiled LangGraph multi-agent workflow."""
    initial_state: AptitudeState = {
        "user_id": user_id,
        "user_query": user_query,
        "intent": "",
        "category": "Quantitative Aptitude",
        "topic": None,
        "difficulty": "medium",
        "number_of_questions": 5,
        "questions": [],
        "answers": [],
        "score": 0.0,
        "performance": {},
        "retrieved_context": [],
        "final_response": ""
    }
    return aptitude_graph.invoke(initial_state)
