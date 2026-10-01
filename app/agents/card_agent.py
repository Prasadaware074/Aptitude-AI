from typing import List, Optional
from app.models.schemas import FlashcardSchema
from app.database.connection import SessionLocal
from app.database.repository import Repository
from app.rag.topic_knowledge import get_topic_details
from app.agents.llm_factory import get_llm

class CardAgent:
    """Agent responsible for creating and fetching formula, shortcut, concept, vocabulary, and mistake cards."""

    @staticmethod
    def get_cards(user_id: str = "default_user", topic: Optional[str] = None, card_type: Optional[str] = None) -> List[FlashcardSchema]:
        db = SessionLocal()
        try:
            repo = Repository(db)
            cards = repo.get_flashcards(user_id=user_id, topic=topic, card_type=card_type)
            if not cards and topic and topic.lower() != "all":
                db.close()
                return CardAgent.generate_cards_for_topic(topic, card_type or "all", user_id)
            return [
                FlashcardSchema(
                    id=c.id,
                    card_type=c.card_type,
                    topic=c.topic,
                    category=c.category,
                    title=c.title,
                    content=c.content,
                    example=c.example,
                    user_id=c.user_id
                )
                for c in cards
            ]
        finally:
            db.close()

    @staticmethod
    def generate_cards_for_topic(topic: str, card_type: str = "all", user_id: str = "default_user") -> List[FlashcardSchema]:
        db = SessionLocal()
        try:
            repo = Repository(db)
            
            query_type = None if (not card_type or card_type.lower() == "all") else card_type
            existing = repo.get_flashcards(user_id=user_id, topic=topic, card_type=query_type)
            if existing and len(existing) >= 3:
                return [
                    FlashcardSchema(
                        id=c.id,
                        card_type=c.card_type,
                        topic=c.topic,
                        category=c.category,
                        title=c.title,
                        content=c.content,
                        example=c.example,
                        user_id=c.user_id
                    )
                    for c in existing
                ]

            details = get_topic_details(topic)
            category = details.get("category", "Quantitative Aptitude")

            card_data = CardAgent._get_default_card_template(topic, category, card_type or "all", details)
            created_cards = []
            for c_schema in card_data:
                c_schema.user_id = user_id
                model = repo.add_flashcard(c_schema)
                c_schema.id = model.id
                created_cards.append(c_schema)

            return created_cards
        finally:
            db.close()

    @staticmethod
    def _get_default_card_template(topic: str, category: str, card_type: str, details: dict) -> List[FlashcardSchema]:
        formulas = details.get("important_formulas", [f"{topic} Core Formula: Target = Base * Rate"])
        shortcuts = details.get("shortcuts", ["Use process of elimination."])
        concepts = details.get("core_concepts", [f"Understanding foundational principles of {topic}."])
        mistakes = details.get("common_mistakes", ["Misreading baseline values or units."])
        examples = details.get("worked_examples", [])

        cards: List[FlashcardSchema] = []
        c_type = (card_type or "all").lower()

        if c_type in ("formula", "all"):
            for idx, f in enumerate(formulas):
                ex = f"Problem: {examples[idx % len(examples)]['problem']} | Solution: {examples[idx % len(examples)]['solution']}" if examples else ""
                cards.append(FlashcardSchema(
                    card_type="formula",
                    topic=topic,
                    category=category,
                    title=f"{topic} Formula #{idx+1}",
                    content=f,
                    example=ex
                ))

        if c_type in ("shortcut", "all"):
            for idx, s in enumerate(shortcuts):
                ex = f"Problem: {examples[idx % len(examples)]['problem']} | Solution: {examples[idx % len(examples)]['solution']}" if examples else ""
                cards.append(FlashcardSchema(
                    card_type="shortcut",
                    topic=topic,
                    category=category,
                    title=f"{topic} Shortcut #{idx+1}",
                    content=s,
                    example=ex
                ))

        if c_type in ("concept", "all"):
            for idx, c in enumerate(concepts):
                ex = f"Problem: {examples[idx % len(examples)]['problem']} | Solution: {examples[idx % len(examples)]['solution']}" if examples else ""
                cards.append(FlashcardSchema(
                    card_type="concept",
                    topic=topic,
                    category=category,
                    title=f"{topic} Core Concept #{idx+1}",
                    content=c,
                    example=ex
                ))

        if c_type in ("mistake", "all"):
            for idx, m in enumerate(mistakes):
                ex = f"Problem: {examples[idx % len(examples)]['problem']} | Solution: {examples[idx % len(examples)]['solution']}" if examples else ""
                cards.append(FlashcardSchema(
                    card_type="mistake",
                    topic=topic,
                    category=category,
                    title=f"Common Mistake #{idx+1} in {topic}",
                    content=m,
                    example=ex
                ))

        if c_type == "vocabulary" or (category == "Verbal Ability" and c_type == "all"):
            v_topic = topic if topic != "All" else "Vocabulary"
            cards.append(FlashcardSchema(
                card_type="vocabulary",
                topic=v_topic,
                category="Verbal Ability",
                title=f"Vocabulary Focus: {v_topic}",
                content=f"Key terms and contextual usage rules for {v_topic}.",
                example=f"Review active vs passive contextual usage in competitive exams for {v_topic}."
            ))

        return cards
