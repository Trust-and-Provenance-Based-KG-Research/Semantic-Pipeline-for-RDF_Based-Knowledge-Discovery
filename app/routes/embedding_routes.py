"""
Embedding API routes for creating embeddings in ChromaDB based on resource files.
Supports multiple text-based formats including PDF, TXT, DOCX, MD, and JSON.
"""

from fastapi import APIRouter, HTTPException
from pathlib import Path
from app.services.embedding_service import EmbeddingService
from app.services.metadata_service import MetadataService
from pypdf import PdfReader
from docx import Document
import mimetypes
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resource_embedding", tags=["Embedding"])
embedding_service = EmbeddingService()
metadata_service = MetadataService()


def read_text_from_resource(resource_path: Path) -> str:
    """
    Extract textual content from a resource file.
    Supports: .pdf, .txt, .docx, .md, .json, and similar text formats.
    """
    if not resource_path.exists():
        raise FileNotFoundError(f"Resource not found: {resource_path}")

    suffix = resource_path.suffix.lower()
    mime_type, _ = mimetypes.guess_type(resource_path)
    text_content = ""

    try:
        # Handle PDF files
        if suffix == ".pdf" or (mime_type and "pdf" in mime_type):
            with open(resource_path, "rb") as f:
                reader = PdfReader(f)
                for page in reader.pages:
                    text_content += page.extract_text() or ""

        # Handle DOCX (Word) files
        elif suffix == ".docx" or (mime_type and "word" in mime_type):
            doc = Document(resource_path)
            text_content = "\n".join([p.text for p in doc.paragraphs])

        # Handle plain text, markdown, or JSON
        elif suffix in [".txt", ".md", ".json"]:
            with open(resource_path, "r", encoding="utf-8", errors="ignore") as f:
                raw_text = f.read()
                # If JSON, serialize content for embedding
                if suffix == ".json":
                    try:
                        json_data = json.loads(raw_text)
                        text_content = json.dumps(json_data, indent=2)
                    except Exception:
                        text_content = raw_text
                else:
                    text_content = raw_text

        else:
            raise ValueError(f"Unsupported file format for embedding: {suffix}")

        return text_content.strip()

    except Exception as e:
        raise RuntimeError(f"Failed to read file {resource_path.name}: {e}")


@router.post("/")
async def embed_resource(resource_path: str, metadata_path: str):
    """
    Create embeddings for a resource (text, audio transcript, or video transcript)
    based on its metadata namespace.
    """
    try:
        resource = Path(resource_path)
        metadata = Path(metadata_path)

        if not resource.exists():
            raise HTTPException(status_code=404, detail=f"Resource not found: {resource_path}")
        if not metadata.exists():
            raise HTTPException(status_code=404, detail=f"Metadata not found: {metadata_path}")

        # Extract textual content safely
        text_content = read_text_from_resource(resource)
        logger.info(f"Successfully extracted text from: {resource.name}")

        # Pass content to embedding service
        result = embedding_service.embed_resource(resource, metadata, text_content)

        return {"message": "Embedding created successfully", "details": result}

    except Exception as e:
        logger.error(f"Error embedding resource: {e}")
        raise HTTPException(status_code=500, detail=str(e))
