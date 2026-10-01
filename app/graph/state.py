from typing import TypedDict, List, Dict, Any, Optional

class AptitudeState(TypedDict):
    user_id: str
    user_query: str
    intent: str # LEARN, PRACTICE, MOCK, CARDS, PERFORMANCE, STUDY_PLAN, CHAT, OUT_OF_SCOPE
    category: str
    topic: Optional[str]
    difficulty: str
    number_of_questions: int
    questions: List[Dict[str, Any]]
    answers: List[Dict[str, Any]]
    score: float
    performance: Dict[str, Any]
    retrieved_context: List[str]
    final_response: str
