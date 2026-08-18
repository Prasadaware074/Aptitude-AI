import os
import hashlib
import numpy as np
from typing import List
from app.config.settings import settings

class GeminiOrLocalEmbeddings:
    """Wrapper that attempts Google Gemini embeddings via langchain_google_genai, with deterministic fallback for offline/test environments."""

    def __init__(self):
        self.use_gemini = bool(settings.GOOGLE_API_KEY)
        if self.use_gemini:
            try:
                from langchain_google_genai import GoogleGenerativeAIEmbeddings
                self._embeddings = GoogleGenerativeAIEmbeddings(
                    model="models/text-embedding-004",
                    google_api_key=settings.GOOGLE_API_KEY
                )
            except Exception:
                self.use_gemini = False

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if self.use_gemini and hasattr(self, "_embeddings"):
            try:
                return self._embeddings.embed_documents(texts)
            except Exception:
                pass
        return [self._local_fallback_embedding(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        if self.use_gemini and hasattr(self, "_embeddings"):
            try:
                return self._embeddings.embed_query(text)
            except Exception:
                pass
        return self._local_fallback_embedding(text)

    def _local_fallback_embedding(self, text: str, dim: int = 384) -> List[float]:
        """Generate a normalized 384-dim pseudo-embedding vector based on text hash & n-grams."""
        text_clean = text.lower().strip()
        vec = np.zeros(dim, dtype=np.float32)
        words = text_clean.split()
        for i, word in enumerate(words):
            h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            idx = h % dim
            vec[idx] += 1.0 + (i * 0.01)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()
