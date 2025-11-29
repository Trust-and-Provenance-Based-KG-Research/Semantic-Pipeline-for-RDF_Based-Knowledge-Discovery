"""
Handles upload endpoints for all file types (audio, video, text).

Each upload:
1. Detects the file type automatically.
2. Saves the file to the correct directory.
3. Extracts and saves JSON metadata.
"""

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
import json
from pathlib import Path

from app.config.core_config import (
    AUDIO_FILE_DIR, AUDIO_META_DIR,
    TEXT_DIR, TEXT_META_DIR,
    VIDEO_FILE_DIR, VIDEO_META_DIR
)
from app.utils.utils import generate_namespace, detect_file_type, extract_basic_metadata
from app.services.metadata_service import MetadataService
from app.services.logging_service import get_logger

router = APIRouter(prefix="/upload", tags=["Upload"])
logger = get_logger(__name__)
metadata_service = MetadataService()


@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    """
    Uploads a single file (video, audio, or text).
    Automatically generates metadata and stores the file in the appropriate directory.
    """
    try:
        # Detect file type and namespace
        file_format = detect_file_type(file.filename)
        namespace_id = generate_namespace(file.filename)

        # Match directory
        if file_format == "audio":
            save_dir, meta_dir = AUDIO_FILE_DIR, AUDIO_META_DIR
        elif file_format == "video":
            save_dir, meta_dir = VIDEO_FILE_DIR, VIDEO_META_DIR
        elif file_format == "text":
            save_dir, meta_dir = TEXT_DIR, TEXT_META_DIR
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file format: {file_format}")

        # Save file
        file_path = save_dir / file.filename
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Generate and save metadata
        metadata = extract_basic_metadata(file_path, file_format, namespace_id)
        metadata_service.save_metadata(metadata, meta_dir)

        logger.info(f"{file_format.capitalize()} file uploaded successfully: {file.filename}")

        return JSONResponse(
            content={
                "message": f"{file_format.capitalize()} upload successful",
                "metadata": metadata
            },
            status_code=200
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Server Error: {e}")
