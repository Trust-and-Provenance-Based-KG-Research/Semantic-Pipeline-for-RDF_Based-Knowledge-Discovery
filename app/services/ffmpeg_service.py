"""
Handles audio extraction from video files using FFmpeg.
"""

import ffmpeg
from pathlib import Path
from app.services.logging_service import get_logger
from app.config.core_config import FFMPEG_AUDIO_FORMAT, VIDEO_FILE_DIR, VIDEO_AUDIO_DIR

logger = get_logger(__name__)

class FFmpegService:
    """Provides methods for extracting audio from video files."""

    @staticmethod
    def extract_audio(video_path: Path, output_dir: Path = VIDEO_AUDIO_DIR) -> Path:
        """Extracts the audio track from a video file and saves it as .wav (or configured format)."""
        if not video_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")

        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{video_path.stem}.{FFMPEG_AUDIO_FORMAT}"

        if output_file.exists():
            logger.info(f"Audio already exists for {video_path.name}, skipping extraction.")
            return output_file

        logger.info(f"Extracting audio from {video_path.name} → {output_file.name}")

        try:
            (
                ffmpeg
                .input(str(video_path))
                .output(
                    str(output_file),
                    format=FFMPEG_AUDIO_FORMAT,
                    acodec="pcm_s16le",
                    ac=1,
                    ar="16000"
                )
                .overwrite_output()
                .run(quiet=True)
            )

            if not output_file.exists() or output_file.stat().st_size == 0:
                raise RuntimeError(f"FFmpeg produced no output for {video_path.name}")

            logger.info(f"Successfully extracted audio to {output_file}")
            return output_file

        except ffmpeg.Error as e:
            logger.error(f"FFmpeg extraction failed for {video_path.name}: {e.stderr.decode() if e.stderr else e}")
            raise RuntimeError(f"Audio extraction failed for {video_path.name}") from e
