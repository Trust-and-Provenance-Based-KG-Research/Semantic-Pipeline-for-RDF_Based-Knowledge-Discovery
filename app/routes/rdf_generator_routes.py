"""
Endpoints for RDF pipeline operations:
 - Generate RDF triples from multimodal metadata
 - Upload all generated TTL files to GraphDB
"""

"""
FastAPI route to trigger RDF generation pipeline.

Endpoint:
 - POST /rdf/generate : Run RDFModelPipeline to transform multimodal metadata into RDF TTL files
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.pipelines.rdf_generator_model_pipeline import RDFModelPipeline
from app.services.logging_service import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/rdf",
    tags=["RDF Generation"]
)


@router.post("/generate")
async def generate_rdf_models():
    """
    Trigger RDF generation for all available modalities (audio, video, text).

    Returns:
        JSON summary with modality → generated TTL file paths
    """
    try:
        logger.info("Starting RDF model generation via API...")

        pipeline = RDFModelPipeline()
        result = pipeline.run()

        if not result:
            raise HTTPException(status_code=404, detail="No metadata files found for any modality.")

        logger.info("RDF generation completed successfully.")
        return JSONResponse(content=result)

    except Exception as e:
        logger.error(f"RDF generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
