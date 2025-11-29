"""
Centralized configuration and directory setup for the multimodal ingestion system.

This file defines all core paths (audio, video, text, transcripts, metadata, and grouped outputs)
and ensures they exist before runtime.
"""


from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from the project root .env file
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent.parent / ".env")


# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DATA_DIR = BASE_DIR / "Raw_Multi_Modal_Data"
GROUPED_DIR = BASE_DIR / "Grouped_multi_modal_data"

# AUDIO PATHS
AUDIO_BASE_DIR = RAW_DATA_DIR / "Audio_file"
AUDIO_FILE_DIR = AUDIO_BASE_DIR / "Audio_file"
AUDIO_TRANSCRIPT_DIR = AUDIO_BASE_DIR / "Audio_transcript"
AUDIO_META_DIR = RAW_DATA_DIR / "Audio_file_metadata"

# TEXT PATHS
TEXT_DIR = RAW_DATA_DIR / "Text_file"
TEXT_META_DIR = RAW_DATA_DIR / "Text_file_metadata"

# VIDEO PATHS
VIDEO_BASE_DIR = RAW_DATA_DIR / "Video_file"
VIDEO_FILE_DIR = VIDEO_BASE_DIR / "Video_file"
VIDEO_AUDIO_DIR = VIDEO_BASE_DIR / "Audios_from_video"
VIDEO_TRANSCRIPT_DIR = VIDEO_BASE_DIR / "video_transcripts"
VIDEO_META_DIR = RAW_DATA_DIR / "Video_file_metadata"

# GROUPED METADATA OUTPUT PATHS
GROUPED_AUDIO_FILE = GROUPED_DIR / "audio_metadata.json"
GROUPED_TEXT_FILE = GROUPED_DIR / "text_metadata.json"
GROUPED_VIDEO_FILE = GROUPED_DIR / "video_metadata.json"

# Folder initialization
FOLDERS = [
    AUDIO_FILE_DIR, AUDIO_TRANSCRIPT_DIR, AUDIO_META_DIR,
    TEXT_DIR, TEXT_META_DIR,
    VIDEO_FILE_DIR, VIDEO_AUDIO_DIR, VIDEO_TRANSCRIPT_DIR, VIDEO_META_DIR,
    GROUPED_DIR
]
for folder in FOLDERS:
    folder.mkdir(parents=True, exist_ok=True)

# Whisper and FFmpeg Config
FFMPEG_AUDIO_FORMAT = "wav"
WHISPER_MODEL_NAME = "base"

# Embedding + LLM Configuration
CHROMA_PERSIST_DIR = BASE_DIR / "ChromaDB"
CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Groq LLM Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
#GROQ_MODEL_NAME = "llama-3.3-70b-versatile"
GROQ_MODEL_NAME = "openai/gpt-oss-120b"
