from typing import Dict, Any, Optional
from app.models.schemas import LessonResponse, QuestionSchema
from app.rag.retriever import retrieve_aptitude_context
from app.rag.topic_knowledge import get_topic_details
from app.agents.llm_factory import get_llm

class LearningAgent:
    """Agent responsible for explaining aptitude topics in a rich, structured lesson format."""

    @staticmethod
    def generate_lesson(topic: str, difficulty: str = "medium", user_query: Optional[str] = None) -> LessonResponse:
        # Retrieve background knowledge context via RAG
        search_query = f"{topic} definition formulas concepts shortcuts worked examples {user_query or ''}"
        rag_context = retrieve_aptitude_context(search_query, top_k=3)

        # Try Gemini LLM generation if available
        llm = get_llm(temperature=0.3, structured_output_schema=LessonResponse)
        if llm:
            prompt = f"""You are a master Aptitude Learning Tutor. Teach the topic '{topic}' at a '{difficulty}' level.
User query: {user_query or 'Teach me this topic.'}

Use the following background knowledge context:
{rag_context}

Provide a comprehensive, structured lesson covering:
1. Topic overview
2. Clear definition
3. Core concepts
4. Important formulas
5. Step-by-step explanation
6. Worked examples with detailed solutions
7. Useful shortcuts
8. Common mistakes to avoid
9. Exam tips
10. Practice questions (at least 2 MCQs with 4 options option_a..option_d, correct_answer key, explanation)
11. Follow-up suggestions for deeper learning.
"""
            try:
                response = llm.invoke(prompt)
                if isinstance(response, LessonResponse):
                    return response
            except Exception:
                pass

        # High-quality topic-specific fallback lesson generator
        return LearningAgent._fallback_lesson(topic, difficulty, rag_context)

    @staticmethod
    def _fallback_lesson(topic: str, difficulty: str, rag_context: str) -> LessonResponse:
        details = get_topic_details(topic)

        return LessonResponse(
            topic=topic,
            category=details["category"],
            topic_overview=f"Comprehensive mastery lesson on {topic} for competitive aptitude exams.",
            definition=details["definition"],
            core_concepts=details["core_concepts"],
            important_formulas=details["important_formulas"],
            explanation=details["explanation"],
            worked_examples=details["worked_examples"],
            shortcuts=details["shortcuts"],
            common_mistakes=details["common_mistakes"],
            exam_tips=details["exam_tips"],
            practice_questions=details["sample_questions"],
            follow_up_suggestions=[
                f"Solve 10 practice questions on {topic}.",
                f"Review formula flashcards for {topic}.",
                f"Take a timed mock test covering {topic}."
            ]
        )
