"""
Transforms multimodal metadata JSON files (audio, video, text)
into RDF triples using the schema and utilities, then serializes
each to Turtle (.ttl) files inside `knowledge_graph/instances/`.

Enhancements:
 - Integrated logging instead of print statements.
 - Added metadata validation (checks required fields).
 - Enforces lowercase modality naming for consistency.
 - Generates per-modality TTL files named with timestamps.
 - Handles missing or malformed JSON gracefully.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from rdflib import URIRef
from app.utils.rdf_utils import (
    new_graph_with_bindings,
    create_uri,
    create_resource_triple_set,
    serialize_graph_to_ttl,
    class_for_resource_type,
)

# Logging Configuration
LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "transform_to_ttl.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Utility Functions
def load_json_metadata(json_path: str):
    """Load and return a list of metadata entries from a JSON file."""
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            data = [data]
        return data
    except FileNotFoundError:
        logger.error(f"JSON file not found: {json_path}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON: {json_path} | Error: {e}")
        return []

def validate_item(item: dict, modality: str) -> bool:
    """Basic validation of required metadata fields."""
    required_fields = ["file_name", "file_format", "upload_timestamp"]
    missing = [f for f in required_fields if not item.get(f)]
    if missing:
        logger.warning(f"Skipping {modality} item due to missing fields: {missing}")
        return False
    return True

# Main RDF Transformation Logic
def transform_modality(json_path: str, modality: str, output_dir: str):
    """
    Convert a modality's JSON metadata to RDF and save to Turtle.
    Args:
        json_path: path to the input metadata JSON file.
        modality: one of 'audio', 'video', 'text'.
        output_dir: folder to save TTL outputs.
    """
    modality = modality.lower()
    items = load_json_metadata(json_path)
    if not items:
        logger.warning(f"No valid data to process for {modality}.")
        return

    g = new_graph_with_bindings()
    cls = class_for_resource_type(modality)

    for item in items:
        if not validate_item(item, modality):
            continue

        identifier = (
            item.get("namespace")
            or item.get("file_name")
            or item.get("id")
            or f"{modality}_unknown"
        )
        resource_uri = create_uri(modality, identifier)

        props = {
            "dcterms:title": item.get("title") or item.get("file_name"),
            "dcterms:description": item.get("description") or f"{modality.capitalize()} resource.",
            "flow:uploadTimestamp": item.get("upload_timestamp") or item.get("date") or "",
            "flow:namespace": item.get("namespace", ""),
            "flow:fileFormat": item.get("file_format", modality),
            "flow:fileSizeMB": item.get("file_size_MB") or item.get("size_mb") or "",
            "flow:chunkCount": item.get("chunk_count", ""),
            "flow:embeddingStatus": item.get("embedding_status", ""),
            "flow:embeddingModel": item.get("embedding_model", ""),
        }

        create_resource_triple_set(g, URIRef(resource_uri), cls, props)

    # Generate output TTL path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ttl_path = Path(output_dir) / f"{modality}_metadata_{timestamp}.ttl"

    # Serialize RDF Graph to Turtle
    serialize_graph_to_ttl(g, str(ttl_path))
    logger.info(f"{modality.capitalize()} triples written to: {ttl_path} ({len(g)} triples)")

# Main Entry Point
def main():
    """
    Transforms all three modality metadata files (if found) into TTL.
    Example expected structure:
        Grouped_multi_modal_data/
            audio_metadata.json
            video_metadata.json
            text_metadata.json
    """
    base_output = Path("knowledge_graph/instances")
    base_output.mkdir(parents=True, exist_ok=True)

    sources = {
        "audio": Path("Grouped_multi_modal_data/audio_metadata.json"),
        "video": Path("Grouped_multi_modal_data/video_metadata.json"),
        "text": Path("Grouped_multi_modal_data/text_metadata.json"),
    }

    for modality, path in sources.items():
        if path.exists():
            logger.info(f"Processing {modality} metadata: {path}")
            transform_modality(str(path), modality, str(base_output))
        else:
            logger.warning(f"Skipped {modality}: {path} not found.")

    logger.info("All modality transformations completed successfully.")

if __name__ == "__main__":
    main()
