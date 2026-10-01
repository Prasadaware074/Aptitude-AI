from typing import Dict, Any, Optional
from app.models.schemas import LessonResponse, QuestionSchema
from app.rag.retriever import retrieve_aptitude_context
from app.rag.topic_knowledge import get_topic_details
from app.config.topics import normalize_topic, get_category_for_topic, is_valid_topic
from app.agents.llm_factory import get_llm
from app.agents.practice_agent import PracticeAgent
from app.tools.scope_validator import RESTRICTION_MESSAGE

class LearningAgent:
    """Agent responsible for explaining aptitude topics in a rich, level-aware, structured lesson format."""

    @staticmethod
    def generate_lesson(topic: str, difficulty: str = "medium", user_query: Optional[str] = None) -> LessonResponse:
        norm_topic = normalize_topic(topic) or topic.strip().title()
        category = get_category_for_topic(norm_topic)
        
        diff = (difficulty or "medium").lower()
        if diff not in ["easy", "medium", "hard"]:
            diff = "medium"

        if not is_valid_topic(norm_topic):
            return LessonResponse(
                topic=norm_topic,
                category=category,
                topic_overview=RESTRICTION_MESSAGE,
                definition="Out-of-scope topic.",
                core_concepts=["Please select a valid aptitude topic."],
                important_formulas=["N/A"],
                explanation=RESTRICTION_MESSAGE,
                worked_examples=[],
                shortcuts=[],
                common_mistakes=[],
                exam_tips=[],
                practice_questions=[],
                follow_up_suggestions=["Choose an aptitude topic like Percentage, Probability, Profit and Loss, etc."]
            )

        # Retrieve background knowledge context via RAG
        search_query = f"{norm_topic} definition formulas concepts shortcuts worked examples {user_query or ''}"
        rag_context = retrieve_aptitude_context(search_query, top_k=3)

        # Try Gemini LLM generation if available
        llm = get_llm(temperature=0.3, structured_output_schema=LessonResponse)
        if llm:
            prompt = f"""You are a master Aptitude Learning Tutor.
Teach the topic '{norm_topic}' strictly at a '{diff}' difficulty level.
Category: {category}
User Query: {user_query or 'Teach me this topic.'}

Difficulty Level Rules:
- Easy: Focus on direct formulas, 1-step calculations, basic definitions, and simple numerical examples.
- Medium: Focus on 2-3 step reasoning, moderate calculations, combined concepts, and word problems.
- Hard: Focus on multi-step complex reasoning, tricky edge cases, and competitive-exam style problems (GATE, CAT, GRE, GMAT).

CRITICAL RESTRICTION RULE:
The lesson MUST be strictly about '{norm_topic}'. Do NOT generate generic or unrelated content.

Use the following background RAG context:
{rag_context}

Provide a comprehensive, structured lesson covering:
1. Topic name
2. Category name
3. Topic overview tailored to '{diff}' difficulty
4. Clear definition
5. Core concepts
6. Important formulas/rules
7. Detailed explanation
8. Worked examples with step-by-step solutions for '{diff}' level
9. Useful shortcuts/tricks
10. Common mistakes to avoid
11. Exam tips
12. Practice questions (at least 2 MCQs with 4 unique options, correct_answer key, explanation)
13. Follow-up suggestions for deeper learning.
"""
            try:
                response = llm.invoke(prompt)
                if isinstance(response, LessonResponse) and response.topic and response.explanation:
                    response.topic = norm_topic
                    response.category = category
                    response.difficulty = diff
                    return response
            except Exception:
                pass

        # High-quality level-aware topic-specific fallback lesson generator
        return LearningAgent._fallback_lesson(norm_topic, category, diff, rag_context)

    @staticmethod
    def _fallback_lesson(topic: str, category: str, difficulty: str, rag_context: str) -> LessonResponse:
        details = get_topic_details(topic)
        dynamic_qs = PracticeAgent.generate_practice_questions(
            topic=topic,
            category=category,
            difficulty=difficulty,
            number_of_questions=2
        )

        # Level-aware adjustments
        if difficulty == "easy":
            overview_text = f"Foundational mastery lesson on {topic} (Easy Level) focusing on direct formulas and 1-step problem solving."
            level_tips = f"For easy {topic} questions, memorize core formulas and identify given variables directly."
        elif difficulty == "hard":
            overview_text = f"Advanced competitive-exam lesson on {topic} (Hard Level) focusing on multi-step reasoning, complex word scenarios, and tricky edge cases."
            level_tips = f"For hard {topic} questions, break complex word problems into 2-3 algebraic equations before attempting calculations."
        else:
            overview_text = f"Comprehensive intermediate lesson on {topic} (Medium Level) covering 2-step calculations and common competitive exam patterns."
            level_tips = f"For medium {topic} questions, keep calculation steps organized to avoid arithmetic errors."

        worked_exs = details.get("worked_examples", [])
        if not worked_exs:
            worked_exs = [
                {
                    "problem": f"Sample problem on {topic} ({difficulty} level): Apply core rules to solve.",
                    "solution": "Follow step-by-step formula application."
                }
            ]

        return LessonResponse(
            topic=topic,
            category=category,
            difficulty=difficulty,
            topic_overview=overview_text,
            definition=details["definition"],
            core_concepts=details["core_concepts"],
            important_formulas=details["important_formulas"],
            explanation=details["explanation"],
            worked_examples=worked_exs,
            shortcuts=details["shortcuts"],
            common_mistakes=details["common_mistakes"],
            exam_tips=details["exam_tips"] + [level_tips],
            practice_questions=dynamic_qs,
            follow_up_suggestions=[
                f"Solve 10 practice MCQs on {topic} at {difficulty} level.",
                f"Review formula flashcards for {topic}.",
                f"Take a timed mock test covering {topic}."
            ]
        )
