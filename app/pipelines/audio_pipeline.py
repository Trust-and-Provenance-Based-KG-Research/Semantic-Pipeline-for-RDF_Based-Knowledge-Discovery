"""
1. Finds all audio files in AUDIO_FILE_DIR.
2. Locates matching metadata JSON in AUDIO_META_DIR.
3. Runs transcription via Whisper.
4. Updates metadata with transcript info.
"""

from pathlib import Path
from app.config.core_config import AUDIO_FILE_DIR, AUDIO_META_DIR, AUDIO_TRANSCRIPT_DIR
from app.services.whisper_service import WhisperService
from app.services.metadata_service import MetadataService
from app.services.logging_service import get_logger

logger = get_logger(__name__)


class AudioPipeline:
    """Processes and transcribes all uploaded audio files."""

    def __init__(self):
        self.transcriber = WhisperService()
        self.metadata_service = MetadataService()

    def run(self):
        logger.info("Starting Audio Pipeline...")

        # Ensure directories exist
        AUDIO_FILE_DIR.mkdir(parents=True, exist_ok=True)
        AUDIO_TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)
        AUDIO_META_DIR.mkdir(parents=True, exist_ok=True)

        for audio_path in AUDIO_FILE_DIR.iterdir():
            if not audio_path.is_file():
                continue

            orig_name = audio_path.name
            transcript_name = f"{audio_path.stem}_transcript.txt"
            transcript_path = AUDIO_TRANSCRIPT_DIR / transcript_name

            # Check if transcript exists
            if transcript_path.exists():
                logger.info(f"Transcript already exists for {orig_name}, skipping.")
                continue

            # Locate metadata JSON
            metadata_path = self.metadata_service.find_metadata_for_file(orig_name, AUDIO_META_DIR)
            if not metadata_path or not Path(metadata_path).exists():
                logger.warning(f"No metadata found for {orig_name}, skipping.")
                continue

            # Load metadata
            metadata = self.metadata_service.load_metadata(metadata_path)
            if not metadata:
                logger.warning(f"Failed to load metadata for {orig_name}, skipping.")
                continue

            try:
                # Run Whisper transcription
                transcript_text = self.transcriber.transcribe_audio(audio_path)

                # Save transcript
                transcript_path.write_text(transcript_text, encoding="utf-8")

                # Update metadata
                self.metadata_service.update_metadata_field(
                    metadata_path, "transcript_name", transcript_name
                )

                logger.info(f"Transcription completed for {orig_name} → {transcript_name}")

            except Exception as e:
                logger.error(f"Transcription failed for {orig_name}: {e}")

        logger.info("Audio Pipeline finished successfully.")
