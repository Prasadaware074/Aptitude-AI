import re
from typing import Optional
from app.rag.retriever import retrieve_aptitude_context
from app.agents.performance_agent import PerformanceAgent
from app.agents.llm_factory import get_llm
from app.database.connection import SessionLocal
from app.database.repository import Repository
from app.tools.scope_validator import ScopeValidator, RESTRICTION_MESSAGE

class TutorAgent:
    """Agent responsible for intelligent multi-turn conversational tutoring, doubt resolution, and personalized guidance."""

    @staticmethod
    def is_aptitude_related(query: str, topic: Optional[str] = None) -> bool:
        """Determines whether a user query is strictly related to aptitude, math, logic, verbal ability, exam prep, or study guidance."""
        is_apt, _ = ScopeValidator.is_aptitude_query(query, topic)
        return is_apt

    @staticmethod
    def generate_chat_reply(user_id: str = "default_user", query: str = "", topic: Optional[str] = None) -> str:
        clean_q = query.strip()
        if not clean_q:
            return "Hello! I am your Aptitude AI Tutor. How can I help you prepare today?"

        # Deterministic Scope Validation BEFORE any LLM call
        if not TutorAgent.is_aptitude_related(clean_q, topic):
            return RESTRICTION_MESSAGE

        # Fetch user performance profile
        perf = PerformanceAgent.get_user_performance(user_id)
        db = SessionLocal()
        user_name = "Learner"
        try:
            repo = Repository(db)
            user = repo.get_user_by_token(user_id) if len(user_id) > 20 else repo.get_or_create_user(user_id)
            if user and user.name:
                user_name = user.name
        except Exception:
            pass
        finally:
            db.close()

        weak_topics_str = ", ".join(perf.weak_topics) if perf.weak_topics else "None identified yet"
        rag_query = f"{topic or ''} {clean_q}"
        rag_context = retrieve_aptitude_context(rag_query, top_k=3)

        # Try Gemini LLM invocation if available
        llm = get_llm(temperature=0.7)
        if llm:
            prompt = f"""You are AptitudeAI Tutor, an empathetic, highly intelligent, and expert competitive exam coach (GATE, CAT, Bank PO, GRE, GMAT, Placement Exams).
User Name: {user_name}
User Overall Accuracy: {perf.overall_accuracy}%
User Weak Topics: {weak_topics_str}
RAG Background Knowledge Context:
{rag_context}

User Query: "{clean_q}"

CRITICAL RESTRICTION RULE:
You are RESTRICTED strictly to Aptitude (Quantitative Aptitude, Logical Reasoning, Verbal Ability) and Competitive Exam preparation topics.
Do NOT assist with general programming (e.g. Python, Java, React), movies, sports, politics, cooking, or trivia.
If the query is outside aptitude scope, output the exact restriction:
"I am AptitudeAI, an aptitude-focused tutor. I can help with Quantitative Aptitude, Logical Reasoning, Verbal Ability, aptitude questions, concepts, practice, and mock tests. Please ask an aptitude-related question."

Guidelines:
- Address the user naturally by name if appropriate.
- Provide a clear, engaging, step-by-step answer to the user's specific query.
- Include formulas, shortcut tricks, or worked examples when relevant to math/logic questions.
- Keep formatting clean using GitHub Markdown headers, bolding, and bullet points.
"""
            try:
                raw_resp = llm.invoke(prompt)
                reply = raw_resp.content if hasattr(raw_resp, "content") else str(raw_resp)
                if reply and len(reply.strip()) > 10:
                    return reply.strip()
            except Exception:
                pass

        # Dynamic Fallback Response Generator
        return TutorAgent._dynamic_fallback_reply(user_name, clean_q, topic, perf, rag_context)

    @staticmethod
    def _dynamic_fallback_reply(user_name: str, query: str, topic: Optional[str], perf, rag_context: str) -> str:
        q_lower = query.lower()

        # Check restriction in fallback
        if not TutorAgent.is_aptitude_related(query, topic):
            return RESTRICTION_MESSAGE

        # Direct Math Calculation check (e.g., "What is 15% of 240?")
        pct_match = re.search(r'(\d+(?:\.\d+)?)\%\s*of\s*(\d+(?:\.\d+)?)', query, re.IGNORECASE)
        if pct_match:
            pct_val = float(pct_match.group(1))
            base_val = float(pct_match.group(2))
            res = (pct_val / 100.0) * base_val
            res_str = f"{int(res)}" if res.is_integer() else f"{res:.2f}"
            return (
                f"### 🧮 Quantitative Calculation Solution\n\n"
                f"**Question:** What is {pct_match.group(1)}% of {pct_match.group(2)}?\n\n"
                f"**Step-by-Step Solution:**\n"
                f"1. Convert percentage to fraction: {pct_match.group(1)}% = {pct_val} / 100 = {pct_val/100.0}\n"
                f"2. Multiply by base value: ({pct_val} / 100) * {base_val} = **{res_str}**\n\n"
                f"✅ **Answer:** **{res_str}**"
            )

        # 1. Greetings
        if any(w in q_lower for w in ["hi", "hello", "hey", "good morning", "good evening", "greetings"]):
            return (
                f"Hello {user_name}! 👋 I am your **Aptitude AI Tutor**.\n\n"
                f"I am here to help you master **Quantitative Aptitude**, **Logical Reasoning**, and **Verbal Ability**.\n\n"
                f"📊 **Your Current Status:**\n"
                f"- **Overall Accuracy:** {perf.overall_accuracy}%\n"
                f"- **Weak Topics Needing Focus:** {', '.join(perf.weak_topics) if perf.weak_topics else 'None! Great job!'}\n\n"
                f"What would you like to work on right now? You can ask me to explain a concept, generate practice questions, or create a timed mock test!"
            )

        # 2. Performance & Weak Topics Questions
        if any(w in q_lower for w in ["weak", "performance", "accuracy", "progress", "score"]):
            weak_list = ", ".join(perf.weak_topics) if perf.weak_topics else "No weak topics identified yet! Keep practicing to maintain high accuracy."
            return (
                f"📈 **Performance Analysis for {user_name}**\n\n"
                f"- **Overall Accuracy:** {perf.overall_accuracy}%\n"
                f"- **Topics Needing Revision:** {weak_list}\n\n"
                f"💡 **Tutor Recommendation:**\n"
                f"1. Go to the **Learn Topics** tab to review concept formulas.\n"
                f"2. Take a 5-question **Practice MCQ** set on your weak topics.\n"
                f"3. Check your personalized **Study Plan** tab for daily targets."
            )

        # 3. Topic-Specific Explanation Queries
        if topic:
            return (
                f"### 💡 Concept Guide: {topic}\n\n"
                f"Here is key guidance for **{topic}** based on our exam repository:\n\n"
                f"{rag_context[:600] if rag_context else 'Mastering this topic requires understanding fundamental formulas and practicing shortcut methods.'}\n\n"
                f"🎯 **Quick Action Steps:**\n"
                f"- Click **Practice MCQs** in the sidebar to test your accuracy on {topic}.\n"
                f"- Check the **Flashcards** tab to review formulas and shortcut tricks for {topic}."
            )

        # 4. General Q&A / Platform Queries
        return (
            f"Thank you for reaching out, {user_name}! 🎓\n\n"
            f"You asked: *\"{query}\"*\n\n"
            f"Here is how I can assist your aptitude preparation:\n"
            f"1. 📚 **Learn Concepts:** Type *'Teach me [Topic Name]'* to get step-by-step explanations.\n"
            f"2. 📝 **Practice Questions:** Select **Practice MCQs** to solve interactive questions.\n"
            f"3. ⏱️ **Mock Tests:** Go to **Mock Tests** to simulate timed exam sessions with detailed score analysis.\n"
            f"4. 🗂️ **Flashcards:** Access formula cards, shortcuts, and vocabulary cards anytime.\n\n"
            f"Feel free to ask any specific math, logic, or verbal question!"
        )
