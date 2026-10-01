import re
import json
from typing import Dict, Any, Tuple, Optional
from app.config.topics import TOPIC_REGISTRY, normalize_topic, get_category_for_topic
from app.tools.scope_validator import ScopeValidator
from app.agents.llm_factory import get_llm

class RouterAgent:
    """Agent responsible for classifying natural language intent, validating scope, and extracting metadata parameters."""

    @staticmethod
    def classify_intent(query: str) -> Dict[str, Any]:
        clean_q = query.strip()
        
        # Step 1: Strict Scope Validation BEFORE any LLM processing
        is_apt, canonical_topic = ScopeValidator.is_aptitude_query(clean_q)
        if not is_apt:
            return {
                "intent": "OUT_OF_SCOPE",
                "topic": None,
                "category": "General Aptitude",
                "difficulty": "medium",
                "number_of_questions": 5
            }

        # Step 2: Rule-based intent & parameter extraction
        intent, confidence = RouterAgent._keyword_classify(clean_q.lower())
        topic, category, difficulty, count = RouterAgent._extract_parameters(clean_q, canonical_topic)

        # Step 3: Optional LLM refinement if API key available and confidence is low
        llm = get_llm(temperature=0.0)
        if llm and confidence < 0.8:
            prompt = f"""Classify the user's intent into exactly ONE of the following categories:
- CHAT (User is greeting, asking an aptitude doubt, calculation, or having a conversation with the tutor)
- LEARN (User explicitly wants a structured lesson, syllabus overview, or detailed concept guide on a topic)
- PRACTICE (User wants practice questions, MCQs, or exercises on a topic)
- MOCK (User wants a timed mock test or test simulation)
- CARDS (User wants flashcards, formulas, shortcuts, vocabulary cards, or quick review cards)
- PERFORMANCE (User asks about accuracy, weak topics, progress, score history, or performance analysis)
- STUDY_PLAN (User asks what to study, schedule, study plan, or routine)
- OUT_OF_SCOPE (User asks non-aptitude questions like general programming, movies, sports, cooking, politics)

User Query: "{query}"
Supported Aptitude Topics: {list(TOPIC_REGISTRY.keys())}

Return ONLY a JSON object with keys:
"intent": "CHAT"|"LEARN"|"PRACTICE"|"MOCK"|"CARDS"|"PERFORMANCE"|"STUDY_PLAN"|"OUT_OF_SCOPE",
"topic": "<extracted aptitude topic from supported topics list or null>",
"category": "<extracted category or Quantitative Aptitude>",
"difficulty": "easy"|"medium"|"hard",
"number_of_questions": <integer>
"""
            try:
                raw_resp = llm.invoke(prompt)
                content = raw_resp.content if hasattr(raw_resp, "content") else str(raw_resp)
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group(0))
                    parsed_intent = parsed.get("intent", intent).upper()
                    if parsed_intent == "OUT_OF_SCOPE":
                        return {
                            "intent": "OUT_OF_SCOPE",
                            "topic": None,
                            "category": "General Aptitude",
                            "difficulty": "medium",
                            "number_of_questions": 5
                        }
                    
                    llm_topic = parsed.get("topic")
                    norm_llm_topic = normalize_topic(llm_topic) if llm_topic and llm_topic != "null" else None
                    final_topic = norm_llm_topic or topic
                    final_cat = get_category_for_topic(final_topic) if final_topic else category
                    final_diff = RouterAgent._normalize_difficulty(parsed.get("difficulty", difficulty))

                    return {
                        "intent": parsed_intent,
                        "topic": final_topic,
                        "category": final_cat,
                        "difficulty": final_diff,
                        "number_of_questions": int(parsed.get("number_of_questions", count))
                    }
            except Exception:
                pass

        return {
            "intent": intent,
            "topic": topic,
            "category": category,
            "difficulty": difficulty,
            "number_of_questions": count
        }

    @staticmethod
    def _keyword_classify(query: str) -> Tuple[str, float]:
        greetings = ["hi", "hello", "hey", "good morning", "good evening", "greetings", "who are you", "what can you do", "help me", "thanks", "thank you"]
        if any(re.search(rf'\b{re.escape(w)}\b', query) for w in greetings):
            return "CHAT", 0.95

        if any(w in query for w in ["study plan", "schedule", "routine", "what to study", "plan for today", "should i study"]):
            return "STUDY_PLAN", 0.95
        if any(w in query for w in ["card", "cards", "flashcard", "formula", "formulas", "shortcut"]):
            return "CARDS", 0.95
        if any(w in query for w in ["mock", "full test", "timed test", "test series"]):
            return "MOCK", 0.95
        if any(w in query for w in ["performance", "weak", "strong", "accuracy", "score", "progress", "trend"]):
            return "PERFORMANCE", 0.95
        if any(w in query for w in ["practice", "question", "questions", "mcq", "mcqs", "exercise", "solve"]):
            return "PRACTICE", 0.90
        if any(w in query for w in ["teach me", "lesson on", "explain concept", "full concept", "syllabus", "teach"]):
            return "LEARN", 0.95
        
        return "CHAT", 0.70

    @staticmethod
    def _extract_parameters(query: str, canonical_topic: Optional[str] = None) -> Tuple[Optional[str], str, str, int]:
        # Extract number of questions
        count_match = re.search(r'\b(\d+)\s*(?:[a-zA-Z\s,\-]*)(?:questions|mcqs|mcq|items|q|test|mock)', query, re.IGNORECASE)
        if not count_match:
            count_match = re.search(r'\b(\d+)\b', query)
        count = int(count_match.group(1)) if count_match else 5

        # Difficulty normalization
        difficulty = RouterAgent._normalize_difficulty(query)

        # Topic & Category mapping
        topic = canonical_topic or normalize_topic(query)
        category = get_category_for_topic(topic) if topic else "Quantitative Aptitude"

        return topic, category, difficulty, count

    @staticmethod
    def _normalize_difficulty(diff_input: Optional[str]) -> str:
        """Normalize any difficulty string to strictly easy, medium, or hard."""
        if not diff_input:
            return "medium"
        d_lower = str(diff_input).lower()
        if any(w in d_lower for w in ["easy", "beginner", "simple", "basic"]):
            return "easy"
        elif any(w in d_lower for w in ["hard", "difficult", "advanced", "complex"]):
            return "hard"
        else:
            return "medium"
