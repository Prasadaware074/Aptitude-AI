from typing import List, Dict, Any
from app.rag.vector_store import VectorStoreManager

_vector_store_instance = None

def get_vector_store() -> VectorStoreManager:
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = VectorStoreManager()
        _vector_store_instance.initialize_index_if_empty()
    return _vector_store_instance

def retrieve_aptitude_context(query: str, top_k: int = 3) -> str:
    """Retrieve formatted context string for agents given a user query."""
    store = get_vector_store()
    results = store.search(query, top_k=top_k)
    
    if not results:
        return "No relevant background knowledge context found."

    context_blocks = []
    for i, item in enumerate(results, 1):
        topic = item.get("metadata", {}).get("topic", "General")
        category = item.get("metadata", {}).get("category", "")
        content = item.get("content", "")
        context_blocks.append(f"--- Context Source {i} [{category} > {topic}] ---\n{content}")

    return "\n\n".join(context_blocks)
