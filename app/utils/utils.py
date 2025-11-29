"""
Utility functions for file sanitization, namespace generation, and type detection.

All helpers here are compatible with the service layer and ingestion pipeline.
"""

import re
import uuid
import os
from datetime import datetime
from pathlib import Path


def sanitize_filename(file_name: str) -> str:
    """
    Clean a filename for use in a namespace or metadata label.
    Removes invalid characters and extensions.
    """
    return re.sub(r'[^a-zA-Z0-9_-]', '_', file_name.rsplit('.', 1)[0])


def generate_namespace(file_name: str) -> str:
    """
    Generate a unique namespace string for a file, combining:
    sanitized name + timestamp + short UUID.
    """
    clean_name = sanitize_filename(file_name)
    short_uuid = uuid.uuid4().hex[:6]
    time_str = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    return f"{clean_name}_{time_str}_{short_uuid}"


def detect_file_type(file_name: str) -> str:
    """
    Detect file type based on file extension.
    Returns one of: 'audio', 'video', 'text'.
    Raises ValueError if unsupported.
    """
    ext = file_name.lower().split(".")[-1]
    if ext in {"mp4", "mov", "avi", "mkv"}:
        return "video"
    elif ext in {"mp3", "wav", "aac", "ogg", "flac"}:
        return "audio"
    elif ext in {"txt", "pdf", "docx", "doc"}:
        return "text"
    else:
        raise ValueError(f"Unsupported file type: .{ext}")


def extract_basic_metadata(file_path: Path, file_format: str, namespace_id: str) -> dict:
    """
    Extract fundamental metadata for a given file.
    Output is JSON-serializable and aligns with MetadataService.
    """
    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    return {
        "file_name": file_path.name,
        "file_format": file_format,
        "file_size_MB": round(size_mb, 2),
        "upload_timestamp": datetime.utcnow().isoformat() + "Z",
        "namespace": namespace_id,
    }


def chunk_text(text: str, chunk_size=1000, overlap=100):
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks
