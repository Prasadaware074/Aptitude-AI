import re
from typing import Dict, Any, Tuple, Optional
from app.agents.llm_factory import get_llm

class RouterAgent:
    """Agent responsible for classifying natural language intent and extracting metadata parameters."""

    @staticmethod
    def classify_intent(query: str) -> Dict[str, Any]:
        clean_q = query.lower().strip()

        # Step 1: Fast rule-based intent & parameter extraction
        intent, confidence = RouterAgent._keyword_classify(clean_q)
        topic, category, difficulty, count = RouterAgent._extract_parameters(clean_q)

        # Step 2: Try LLM classification if Gemini API key present
        llm = get_llm(temperature=0.0)
        if llm and confidence < 0.8:
            prompt = f"""Classify the user's intent into exactly ONE of the following categories:
- CHAT (User is greeting, asking a general question, asking a doubt, or having a conversation with the tutor)
- LEARN (User explicitly wants a structured lesson, syllabus overview, or detailed concept guide on a topic)
- PRACTICE (User wants practice questions, MCQs, or exercises on a topic)
- MOCK (User wants a timed mock test or test simulation)
- CARDS (User wants flashcards, formulas, shortcuts, vocabulary cards, or quick review cards)
- PERFORMANCE (User asks about accuracy, weak topics, progress, score history, or performance analysis)
- STUDY_PLAN (User asks what to study, schedule, study plan, or routine)

User Query: "{query}"

Return ONLY a JSON object with keys:
"intent": "CHAT"|"LEARN"|"PRACTICE"|"MOCK"|"CARDS"|"PERFORMANCE"|"STUDY_PLAN",
"topic": "<extracted topic or null>",
"category": "<extracted category or All>",
"difficulty": "easy"|"medium"|"hard",
"number_of_questions": <integer>
"""
            try:
                raw_resp = llm.invoke(prompt)
                content = raw_resp.content if hasattr(raw_resp, "content") else str(raw_resp)
                import json
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group(0))
                    return {
                        "intent": parsed.get("intent", intent).upper(),
                        "topic": parsed.get("topic") if parsed.get("topic") != "null" else topic,
                        "category": parsed.get("category", category),
                        "difficulty": parsed.get("difficulty", difficulty),
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

        if any(w in query for w in ["study plan", "schedule", "routine", "what to study", "plan for today", "should i study", "what should i"]):
            return "STUDY_PLAN", 0.95
        if any(w in query for w in ["card", "cards", "flashcard", "formula", "formulas", "shortcut", "vocabulary"]):
            return "CARDS", 0.95
        if any(w in query for w in ["mock", "full test", "timed test", "test series"]):
            return "MOCK", 0.95
        if any(w in query for w in ["performance", "weak", "strong", "accuracy", "score", "progress", "trend"]):
            return "PERFORMANCE", 0.95
        if any(w in query for w in ["practice", "question", "questions", "mcq", "solve"]):
            return "PRACTICE", 0.90
        if any(w in query for w in ["teach me", "lesson on", "full concept", "syllabus"]):
            return "LEARN", 0.95
        
        # Conversational Q&A fallback
        return "CHAT", 0.70

    @staticmethod
    def _extract_parameters(query: str) -> Tuple[Optional[str], str, str, int]:
        # Extract number of questions
        count_match = re.search(r'(\d+)\s*(?:questions|mcqs|items|q)', query)
        count = int(count_match.group(1)) if count_match else 5

        # Difficulty
        difficulty = "medium"
        if "easy" in query:
            difficulty = "easy"
        elif "hard" in query or "difficult" in query or "advanced" in query:
            difficulty = "hard"

        # Topic & Category mapping
        topic = None
        category = "Quantitative Aptitude"

        topics_map = {
            "percentage": ("Percentage", "Quantitative Aptitude"),
            "profit": ("Profit and Loss", "Quantitative Aptitude"),
            "loss": ("Profit and Loss", "Quantitative Aptitude"),
            "ratio": ("Ratio and Proportion", "Quantitative Aptitude"),
            "proportion": ("Ratio and Proportion", "Quantitative Aptitude"),
            "average": ("Average", "Quantitative Aptitude"),
            "time and work": ("Time and Work", "Quantitative Aptitude"),
            "work": ("Time and Work", "Quantitative Aptitude"),
            "speed": ("Speed, Distance and Time", "Quantitative Aptitude"),
            "distance": ("Speed, Distance and Time", "Quantitative Aptitude"),
            "number": ("Number System", "Quantitative Aptitude"),
            "probability": ("Probability", "Quantitative Aptitude"),
            "algebra": ("Algebra", "Quantitative Aptitude"),
            "syllogism": ("Syllogism", "Logical Reasoning"),
            "blood": ("Blood Relations", "Logical Reasoning"),
            "relation": ("Blood Relations", "Logical Reasoning"),
            "seating": ("Seating Arrangement", "Logical Reasoning"),
            "number series": ("Number Series", "Logical Reasoning"),
            "series": ("Number Series", "Logical Reasoning"),
            "coding": ("Coding-Decoding", "Logical Reasoning"),
            "decoding": ("Coding-Decoding", "Logical Reasoning"),
            "vocabulary": ("Vocabulary", "Verbal Ability"),
            "vocab": ("Vocabulary", "Verbal Ability"),
            "synonym": ("Vocabulary", "Verbal Ability"),
            "synonyms": ("Vocabulary", "Verbal Ability"),
            "antonym": ("Vocabulary", "Verbal Ability"),
            "antonyms": ("Vocabulary", "Verbal Ability"),
            "word": ("Vocabulary", "Verbal Ability"),
            "grammar": ("Grammar", "Verbal Ability"),
            "comprehension": ("Reading Comprehension", "Verbal Ability")
        }

        for k, (t, c) in topics_map.items():
            if k in query:
                topic = t
                category = c
                break

        if not topic:
            m = re.search(r'(?:teach|explain|lesson|concept|about)\s+(?:me\s+)?(?:on\s+)?([a-zA-Z\s]+)', query)
            if m:
                extracted = m.group(1).strip().title()
                if len(extracted) > 2 and extracted.lower() not in ["me", "the", "a", "an"]:
                    topic = extracted
                    category = "Verbal Ability" if any(w in query for w in ["word", "meaning", "synonym", "antonym", "grammar"]) else "General Aptitude"

        return topic, category, difficulty, count
