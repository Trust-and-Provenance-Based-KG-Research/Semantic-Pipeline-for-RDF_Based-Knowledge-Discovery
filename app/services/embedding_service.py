"""
Embedding service for creating and storing resource embeddings in ChromaDB.
Each embedding is isolated by its unique namespace derived from metadata.
Now supports large documents via chunked embedding with batch processing.
"""

from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from pathlib import Path
from app.config.core_config import CHROMA_PERSIST_DIR, EMBEDDING_MODEL_NAME
from app.services.metadata_service import MetadataService
from app.utils.utils import chunk_text
import json
from typing import List
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self):
        # Load embedding model (cached automatically by SentenceTransformers)
        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)

        # Persistent Chroma client (stored on disk)
        self.client = chromadb.PersistentClient(path=str(CHROMA_PERSIST_DIR))
        self.metadata_service = MetadataService()

    def embed_resource(self, resource_path: Path, metadata_path: Path, text_content: str):
        """
        Create embeddings for the given text content in chunks, storing them in a ChromaDB
        collection under the namespace derived from the resource metadata.

        Args:
            resource_path: Path to the resource file (text, transcript, etc.)
            metadata_path: Path to the associated metadata JSON
            text_content: Pre-extracted textual content for embedding
        """
        namespace = self.metadata_service.get_namespace(metadata_path)
        if not namespace:
            raise ValueError(f"No namespace found in metadata {metadata_path}")

        if not text_content or not text_content.strip():
            raise ValueError(f"No textual content extracted from {resource_path}")

        # Create or get the collection for this namespace
        collection = self.client.get_or_create_collection(name=namespace)

        # Chunk the document
        chunks = chunk_text(text_content, chunk_size=1000, overlap=100)
        logger.info(f"Chunking complete: {len(chunks)} chunks created for {resource_path.name}")

        # Encode chunks in batches
        logger.info(f"Encoding {len(chunks)} chunks using {EMBEDDING_MODEL_NAME}...")
        embeddings = self.model.encode(chunks, batch_size=8, show_progress_bar=True)

        # Add all embeddings to ChromaDB
        ids = [f"{resource_path.stem}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"source": str(resource_path), "chunk_id": i} for i in range(len(chunks))]

        collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas,
        )

        # Update metadata to indicate embedding completion
        self.metadata_service.update_metadata_field(metadata_path, "embedding_status", "completed")
        self.metadata_service.update_metadata_field(metadata_path, "embedding_model", EMBEDDING_MODEL_NAME)
        self.metadata_service.update_metadata_field(metadata_path, "chunk_count", len(chunks))

        logger.info(f"Embedding completed for {resource_path.name} ({len(chunks)} chunks)")

        return {
            "namespace": namespace,
            "status": "embedded",
            "file": str(resource_path),
            "chunks": len(chunks),
            "embedding_model": EMBEDDING_MODEL_NAME,
            "chroma_collection": namespace,
        }

    def query_top_k(self, namespace: str, query_text: str, k: int = 1) -> List[str]:
        """
        Query the ChromaDB collection for `namespace` using `query_text` and return
        the top-k documents (text chunks). Returns a list of strings (may be empty).
        """
        if not namespace:
            return []

        collection = self.client.get_or_create_collection(name=namespace)
        res = collection.query(
            query_texts=[query_text],
            n_results=k,
            include=["documents", "metadatas", "distances"]
        )

        docs_for_query = []
        try:
            docs_for_query = res.get("documents", [[]])[0]
        except Exception:
            docs_for_query = []

        return [d for d in docs_for_query if isinstance(d, str) and d.strip()]

    def retrieve_top_context(self, metadata_path: Path, top_k: int = 1):
        """
        Retrieve the top-K most relevant text chunks from ChromaDB
        based on the namespace in the metadata JSON.

        Args:
            metadata_path (Path): Path to the metadata JSON file.
            top_k (int): Number of relevant chunks to retrieve.

        Returns:
            dict: Retrieved context text and associated namespace.
        """
        # Load metadata to extract namespace and query text
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        namespace = metadata.get("namespace")
        query_text = metadata.get("title") or metadata.get("filename") or namespace
        if not namespace:
            raise ValueError("Namespace missing from metadata; cannot retrieve context.")

        logger.info(f"Retrieving top-{top_k} context for namespace '{namespace}' using query '{query_text}'.")

        # Perform query using existing helper
        top_docs = self.query_top_k(namespace, query_text, k=top_k)
        context_text = "\n".join(top_docs) if top_docs else ""

        return {
            "namespace": namespace,
            "context": context_text,
        }
