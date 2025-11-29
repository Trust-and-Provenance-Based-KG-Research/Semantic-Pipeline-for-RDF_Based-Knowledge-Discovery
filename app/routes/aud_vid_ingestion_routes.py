"""
Provides API endpoints to trigger multimodal ingestion pipelines.

- /ingest/all → Runs both video and audio pipelines
- /ingest/audio → Runs only the audio pipeline
- /ingest/video → Runs only the video pipeline
"""

from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse
from app.services.logging_service import get_logger
from app.pipelines.pipeline_manager import PipelineManager

router = APIRouter(prefix="/ingest", tags=["Ingestion"])
logger = get_logger(__name__)
pipeline_manager = PipelineManager()


@router.post("/all")
async def run_all_pipelines(background_tasks: BackgroundTasks):
    """
    Run all ingestion pipelines (video + audio) in the background.
    """
    logger.info("API Trigger: Running all ingestion pipelines.")
    background_tasks.add_task(pipeline_manager.run_all)
    return JSONResponse(content={"message": "All ingestion pipelines started."}, status_code=202)


@router.post("/audio")
async def run_audio_pipeline(background_tasks: BackgroundTasks):
    """
    Run only the audio ingestion pipeline.
    """
    logger.info("API Trigger: Running audio-only pipeline.")
    background_tasks.add_task(pipeline_manager.run_audio_only)
    return JSONResponse(content={"message": "Audio ingestion pipeline started."}, status_code=202)


@router.post("/video")
async def run_video_pipeline(background_tasks: BackgroundTasks):
    """
    Run only the video ingestion pipeline.
    """
    logger.info("API Trigger: Running video-only pipeline.")
    background_tasks.add_task(pipeline_manager.run_video_only)
    return JSONResponse(content={"message": "Video ingestion pipeline started."}, status_code=202)
