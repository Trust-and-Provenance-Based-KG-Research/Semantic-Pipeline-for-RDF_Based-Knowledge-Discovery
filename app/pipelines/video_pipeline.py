"""
1. Finds all videos in VIDEO_FILE_DIR.
2. Locates corresponding metadata JSON in VIDEO_META_DIR.
3. Extracts audio using FFmpeg.
4. Runs Whisper on extracted audio.
5. Updates metadata with transcript reference.
"""

from pathlib import Path
from app.config.core_config import VIDEO_FILE_DIR, VIDEO_META_DIR, VIDEO_AUDIO_DIR, VIDEO_TRANSCRIPT_DIR
from app.services.ffmpeg_service import FFmpegService
from app.services.whisper_service import WhisperService
from app.services.metadata_service import MetadataService
from app.services.logging_service import get_logger

logger = get_logger(__name__)


class VideoPipeline:
    """Processes and transcribes all uploaded video files."""

    def __init__(self):
        self.ffmpeg_service = FFmpegService()
        self.transcriber = WhisperService()
        self.metadata_service = MetadataService()

    def run(self):
        logger.info("Starting Video Pipeline...")

        for video_path in VIDEO_FILE_DIR.iterdir():
            if not video_path.is_file():
                continue

            orig_name = video_path.name
            base_stem = Path(orig_name).stem
            transcript_name = f"{base_stem}_transcript.txt"
            transcript_path = VIDEO_TRANSCRIPT_DIR / transcript_name

            if transcript_path.exists():
                logger.info(f"Transcript already exists for {orig_name}, skipping.")
                continue

            metadata_path = self.metadata_service.find_metadata_for_file(orig_name, VIDEO_META_DIR)
            if not metadata_path:
                logger.warning(f"No metadata found for {orig_name}, skipping.")
                continue

            metadata = self.metadata_service.load_metadata(metadata_path)
            if not metadata:
                logger.warning(f"Failed to load metadata for {orig_name}, skipping.")
                continue

            try:
                # Correct: pass directory only
                extracted_audio_path = self.ffmpeg_service.extract_audio(video_path, VIDEO_AUDIO_DIR)

                # Run Whisper transcription
                transcript_text = self.transcriber.transcribe_audio(extracted_audio_path)

                # Save transcript
                VIDEO_TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)
                with open(transcript_path, "w", encoding="utf-8") as f:
                    f.write(transcript_text)

                # Update metadata
                self.metadata_service.update_metadata_field(metadata_path, "transcript_name", transcript_name)

                logger.info(f"Video transcription completed for {orig_name} → {transcript_name}")

            except Exception as e:
                logger.error(f"Video pipeline failed for {orig_name}: {e}")

        logger.info("Video Pipeline finished successfully.")
