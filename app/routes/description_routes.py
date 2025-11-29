"""
Description API routes for generating 150–200 word summaries of resources.
"""

from fastapi import APIRouter, HTTPException
from pathlib import Path
from app.pipelines.description_pipeline import DescriptionPipeline
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/description_retrieval", tags=["Description"])
description_pipeline = DescriptionPipeline()


@router.post("/")
async def generate_description(resource_path: str, metadata_path: str):

    """
    Generate a 150–200 word description for a resource using existing embeddings.

    Updated pipeline steps:
      1. Retrieve the resource namespace from metadata.
      2. Retrieve top 5 most relevant text chunks from ChromaDB.
      3. Generate a concise 150–200 word description using Groq LLaMA.
      4. Update the metadata JSON with the generated description.

    Args:
        metadata_path (str): Path to the metadata JSON file.
        resource_path (str, optional): Path to the resource (optional; kept for compatibility).

    Returns:
        dict: Contains success message and pipeline output details.
    """
    try:
        metadata = Path(metadata_path)
        if not metadata.exists():
            raise HTTPException(status_code=404, detail=f"Metadata not found: {metadata_path}")

        if resource_path:
            resource = Path(resource_path)
            if not resource.exists():
                raise HTTPException(status_code=404, detail=f"Resource not found: {resource_path}")
            logger.info(f"Running description pipeline for resource: {resource.name}")
        else:
            logger.info(f"Running description pipeline using metadata only: {metadata.name}")

        result = description_pipeline.run(metadata_path=metadata, resource_path=resource_path)

        return {
            "message": "Description generated and metadata updated successfully",
            "details": result,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating description: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating description: {str(e)}")