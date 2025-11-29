"""
Handles transcription of audio files using OpenAI Whisper.

This module wraps the Whisper API (via `openai` or `whisper` package)
to convert audio into plain text transcripts. It’s designed to work
seamlessly with the metadata and logging services.
"""

from pathlib import Path
import whisper
from app.services.logging_service import get_logger
from app.config.core_config import WHISPER_MODEL_NAME

logger = get_logger(__name__)


class WhisperService:
    """
    Provides audio-to-text transcription using OpenAI Whisper.
    """

    def __init__(self, model_name: str = WHISPER_MODEL_NAME):
        """
        Loads the Whisper model (default: 'base').
        """
        self.model = whisper.load_model(model_name)
        logger.info(f"Whisper model '{model_name}' loaded successfully.")

    def transcribe_audio(self, audio_path: Path) -> str:
        """
        Transcribes the given audio file into text.
        Returns the transcribed plain text string.
        """
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        logger.info(f"Starting transcription for: {audio_path.name}")

        try:
            result = self.model.transcribe(str(audio_path), fp16=False, language="en")
            text = result.get("text", "").strip()

            if not text:
                logger.warning(f"No text extracted from {audio_path.name}")
                return ""

            logger.info(f"Transcription complete for {audio_path.name}")
            return text
        except Exception as e:
            logger.error(f"Whisper transcription failed for {audio_path.name}: {e}")
            raise RuntimeError(f"Transcription failed for {audio_path.name}")
