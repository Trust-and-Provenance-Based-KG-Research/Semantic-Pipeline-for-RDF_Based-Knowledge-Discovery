"""
Coordinates retrieval of resource metadata, embedding, and LLM-based
description generation for multimodal files (text, audio, video).
"""

from pathlib import Path
from typing import Dict, Any, Optional
from app.services.metadata_service import MetadataService
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
import logging

logger = logging.getLogger(__name__)


class DescriptionPipeline:
    """Pipeline for generating semantic descriptions of resources using embeddings and LLM summarization."""

    def __init__(self):
        self.metadata_service = MetadataService()
        self.embedding_service = EmbeddingService()
        self.llm_service = LLMService()

    def run(self, metadata_path: Path, resource_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes the streamlined description pipeline:
        1. Retrieve top context from ChromaDB
        2. Generate description via LLaMA (Groq)
        3. Update metadata with description
        """
        metadata_path = Path(metadata_path)
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

        if resource_path:
            resource_path = Path(resource_path)
            logger.info(f"Starting description pipeline for resource: {resource_path.name}")
        else:
            logger.info(f"Starting description pipeline using metadata only: {metadata_path.name}")

        # Step 1: Retrieve relevant context from ChromaDB
        logger.info("Retrieving top 5 relevant chunks from ChromaDB...")
        retrieval_result = self.embedding_service.retrieve_top_context(metadata_path, top_k=1)

        # Step 2: Generate a concise description using the LLM
        logger.info("Generating description via LLaMA (Groq)...")
        desc_result = self.llm_service.generate_description(metadata_path, retrieval_result=retrieval_result)


        # Step 3: Update metadata with the generated description
        self.metadata_service.update_metadata_field(metadata_path, "description", desc_result["description"])
        #self.metadata_service.update_description(metadata_path, desc_result["description"])


        logger.info(f"Description successfully generated and saved for {metadata_path.name}")
        return {
            "namespace": desc_result["namespace"],
            "description": desc_result["description"],
            "status": "completed",
        }

