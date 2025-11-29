"""
Coordinates execution of all modality pipelines.

This module allows orchestration via:
- Command Line (run all pipelines)
- API trigger (future integration)

Ensures each modality runs independently and logs its own progress.
"""

from app.pipelines.audio_pipeline import AudioPipeline
from app.pipelines.video_pipeline import VideoPipeline
from app.services.logging_service import get_logger

logger = get_logger(__name__)


class PipelineManager:
    def __init__(self):
        self.audio_pipeline = AudioPipeline()
        self.video_pipeline = VideoPipeline()

    def run_all(self):
        """
        Run all ingestion pipelines sequentially.
        """
        logger.info("===== Starting Full Multimodal Ingestion Pipeline =====")

        try:
            self.video_pipeline.run()
            self.audio_pipeline.run()
        except Exception as e:
            logger.error(f"PipelineManager encountered an error: {e}")
        finally:
            logger.info("===== Ingestion Pipelines Completed =====")

    def run_audio_only(self):
        """Run only the audio ingestion pipeline."""
        logger.info("Running audio-only pipeline...")
        self.audio_pipeline.run()

    def run_video_only(self):
        """Run only the video ingestion pipeline."""
        logger.info("Running video-only pipeline...")
        self.video_pipeline.run()
