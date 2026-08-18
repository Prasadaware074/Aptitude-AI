import pytest
from app.agents.card_agent import CardAgent

def test_flashcards_generation_and_retrieval():
    cards = CardAgent.generate_cards_for_topic("Percentage", card_type="all", user_id="test_cards_user")
    assert len(cards) >= 3, "Should generate multiple flashcards per topic"
    
    card_types = set(c.card_type for c in cards)
    assert "formula" in card_types or "shortcut" in card_types or "concept" in card_types
    
    fetched = CardAgent.get_cards(user_id="test_cards_user", topic="Percentage")
    assert len(fetched) >= 3
