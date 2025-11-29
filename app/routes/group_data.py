"""
Aggregates metadata JSON files from Audio, Text, and Video metadata directories
into grouped multimodal JSON files. Each grouped file will contain a list of objects,
not wrapped under the key 'resources'.
"""

from fastapi import APIRouter
import json
from app.config.core_config import (
    AUDIO_META_DIR, TEXT_META_DIR, VIDEO_META_DIR,
    GROUPED_AUDIO_FILE, GROUPED_TEXT_FILE, GROUPED_VIDEO_FILE, GROUPED_DIR
)
from app.services.logging_service import get_logger
from pathlib import Path

logger = get_logger(__name__)
router = APIRouter(prefix="/group_data", tags=["Group Data"])


def load_existing_grouped_data(grouped_file: Path) -> list:
    """Safely load an existing grouped JSON file (expects a list)."""
    if grouped_file.exists():
        try:
            with open(grouped_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and "resources" in data:
                    # backward compatibility for old structure
                    return data["resources"]
        except json.JSONDecodeError:
            logger.warning(f"Corrupted JSON in {grouped_file}, reinitializing.")
    return []


def collect_new_metadata(src_dir: Path, grouped_file: Path) -> int:
    """
    Collect new metadata JSON files from a source directory and
    append them to the grouped file, avoiding duplicates.
    """
    existing_data = load_existing_grouped_data(grouped_file)
    existing_files = {meta.get("file_name") for meta in existing_data if isinstance(meta, dict)}

    new_resources = []
    for meta_file in src_dir.glob("*.json"):
        try:
            with open(meta_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Handle both single dict and wrapped {"resources": [...]}
            if isinstance(data, dict) and "resources" in data:
                data_list = data["resources"]
            elif isinstance(data, dict):
                data_list = [data]
            elif isinstance(data, list):
                data_list = data
            else:
                data_list = []

            for item in data_list:
                file_name = item.get("file_name")
                if file_name and file_name not in existing_files:
                    new_resources.append(item)
                    existing_files.add(file_name)
        except Exception as e:
            logger.error(f"Failed to read {meta_file}: {e}")

    if not new_resources:
        return 0

    # Append new items directly to the list
    updated_data = existing_data + new_resources

    with open(grouped_file, "w", encoding="utf-8") as f:
        json.dump(updated_data, f, indent=4)

    return len(new_resources)


@router.post("/")
async def group_data():
    """
    Aggregate new metadata from Audio, Text, and Video metadata folders
    into the Grouped_multi_modal_data directory.
    Output JSON files will contain arrays of objects (no 'resources' wrapper).
    """
    logger.info("Starting grouping of multimodal metadata...")

    added_audio = collect_new_metadata(AUDIO_META_DIR, GROUPED_AUDIO_FILE)
    added_text = collect_new_metadata(TEXT_META_DIR, GROUPED_TEXT_FILE)
    added_video = collect_new_metadata(VIDEO_META_DIR, GROUPED_VIDEO_FILE)

    logger.info(f"Grouping completed. Added: audio={added_audio}, text={added_text}, video={added_video}")

    return {
        "message": "Metadata grouping completed successfully.",
        "audio_added": added_audio,
        "text_added": added_text,
        "video_added": added_video,
        "output_dir": str(GROUPED_DIR),
    }
