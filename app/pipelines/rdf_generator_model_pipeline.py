"""
RDF Model Pipeline Orchestration
Integrates the JSON→RDF transformation into a structured pipeline.

Responsibilities:
 - Load YAML config (GraphDB endpoints, namespaces)
 - Locate multimodal metadata JSON files
 - Call RDF transformation functions (from transform_to_ttl.py)
 - Manage output .ttl files in knowledge_graph/instances/

This allows other components (e.g., API routes, cron jobs)
to trigger RDF graph generation with one function call.
"""

from pathlib import Path
from typing import Dict

from app.utils.rdf_utils import load_rdf_config
from app.services.transform_to_ttl import transform_modality
from app.services.logging_service import get_logger

logger = get_logger(__name__)


class RDFModelPipeline:
    """
    High-level orchestration class for the RDF model building pipeline.
    """

    def __init__(
        self,
        config_path: str = "app/config/graphdb_config.yaml",
        metadata_base_dir: str = "Grouped_multi_modal_data",
        output_dir: str = "knowledge_graph/instances"
    ):
        self.config_path = config_path
        self.metadata_base_dir = Path(metadata_base_dir)
        self.output_dir = Path(output_dir)
        self.config = load_rdf_config(config_path)
        self.namespaces = self.config.get("namespaces", {})

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Initialized RDFModelPipeline with config: %s", config_path)

    def run(self) -> Dict[str, str]:
        """
        Execute the full RDF pipeline across all modalities (audio, video, text).
        Returns mapping of modality → output TTL file path (as string).
        """
        logger.info("Starting RDF model pipeline...")

        outputs = {}
        modalities = ["audio", "video", "text"]

        for modality in modalities:
            json_path = self._find_metadata_file(modality)
            if not json_path:
                logger.warning("No metadata found for %s", modality)
                continue

            ttl_output = self.output_dir
            logger.info("Transforming %s metadata → %s", modality, ttl_output)

            transform_modality(
                json_path=json_path,
                modality=modality,
                output_dir=str(ttl_output),
            )

            # Convert Path to str to satisfy Pydantic response validation
            outputs[modality] = str(ttl_output)

        logger.info("RDF model pipeline complete.")
        return outputs

    def _find_metadata_file(self, modality: str) -> Path:
        """
        Search for a metadata JSON file (audio/video/text) directly inside metadata_base_dir.
        """
        expected_file = self.metadata_base_dir / f"{modality.lower()}_metadata.json"
        if not expected_file.exists():
            logger.warning("Metadata file not found for %s: %s", modality, expected_file)
            return None
        return expected_file

    def get_existing_ttl_files(self) -> Dict[str, str]:
        """
        Returns a mapping of modality → existing TTL file paths if available.
        """
        base_dir = Path("knowledge_graph/instances")
        files = {
            "audio": str(base_dir / "audio_data.ttl"),
            "video": str(base_dir / "video_data.ttl"),
            "text": str(base_dir / "text_data.ttl"),
        }
        existing = {k: v for k, v in files.items() if Path(v).exists()}
        return existing


if __name__ == "__main__":
    pipeline = RDFModelPipeline()
    result = pipeline.run()
    for mod, path in result.items():
        print(f"{mod.capitalize()} RDF file created → {path}")
