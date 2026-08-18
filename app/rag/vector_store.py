import os
import logging
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config.settings import settings
from app.rag.embeddings import GeminiOrLocalEmbeddings
from app.rag.loader import load_knowledge_base_documents, split_text_into_chunks

logger = logging.getLogger(__name__)

class VectorStoreManager:
    """Manages persistent ChromaDB vector collection for RAG context retrieval."""

    def __init__(self):
        self.chroma_path = settings.VECTOR_DB_PATH
        os.makedirs(self.chroma_path, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.chroma_path)
        self.embedder = GeminiOrLocalEmbeddings()
        self.collection_name = "aptitude_knowledge"
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def initialize_index_if_empty(self, force_reload: bool = False):
        """Index knowledge base documents into vector store if empty."""
        count = self.collection.count()
        if count == 0 or force_reload:
            logger.info("Initializing vector store index from knowledge base...")
            raw_docs = load_knowledge_base_documents()
            all_chunks = []
            for doc in raw_docs:
                chunks = split_text_into_chunks(
                    doc["content"],
                    doc["metadata"],
                    chunk_size=settings.CHUNK_SIZE,
                    overlap=settings.CHUNK_OVERLAP
                )
                all_chunks.extend(chunks)

            if not all_chunks:
                logger.warning("No knowledge base documents found to index.")
                return

            ids = [f"doc_{i}" for i in range(len(all_chunks))]
            texts = [c["text"] for c in all_chunks]
            metadatas = [c["metadata"] for c in all_chunks]
            embeddings = self.embedder.embed_documents(texts)

            self.collection.add(
                ids=ids,
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas
            )
            logger.info(f"Successfully indexed {len(all_chunks)} chunks into vector store.")

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search vector store for most relevant context chunks matching user query."""
        if self.collection.count() == 0:
            self.initialize_index_if_empty()

        query_emb = self.embedder.embed_query(query)
        results = self.collection.query(
            query_embeddings=[query_emb],
            n_results=min(top_k, max(self.collection.count(), 1))
        )

        output = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
            dists = results["distances"][0] if "distances" in results else [0.0] * len(docs)

            for doc, meta, dist in zip(docs, metas, dists):
                output.append({
                    "content": doc,
                    "metadata": meta,
                    "distance": dist
                })
        return output
