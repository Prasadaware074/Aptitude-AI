import os
from pathlib import Path
from typing import List, Dict, Any
from app.config.settings import settings

def load_knowledge_base_documents() -> List[Dict[str, Any]]:
    """Scan knowledge_base directory and extract text documents with metadata."""
    base_dir = Path(settings.KNOWLEDGE_BASE_DIR)
    docs = []

    if not base_dir.exists():
        return docs

    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".md") or file.endswith(".txt"):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, base_dir)
                category = os.path.dirname(rel_path) or "General"
                topic = os.path.splitext(file)[0].replace("_", " ").title()

                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                docs.append({
                    "content": content,
                    "metadata": {
                        "source": rel_path,
                        "category": category,
                        "topic": topic
                    }
                })
    return docs

def split_text_into_chunks(content: str, metadata: Dict[str, Any], chunk_size: int = 500, overlap: int = 50) -> List[Dict[str, Any]]:
    """Split markdown text content into overlapping text chunks."""
    chunks = []
    lines = content.split("\n\n")
    current_chunk = ""

    for line in lines:
        if len(current_chunk) + len(line) <= chunk_size:
            current_chunk += line + "\n\n"
        else:
            if current_chunk.strip():
                chunks.append({
                    "text": current_chunk.strip(),
                    "metadata": metadata.copy()
                })
            # Start new chunk with overlap
            current_chunk = current_chunk[-overlap:] + line + "\n\n" if len(current_chunk) > overlap else line + "\n\n"

    if current_chunk.strip():
        chunks.append({
            "text": current_chunk.strip(),
            "metadata": metadata.copy()
        })
    return chunks
