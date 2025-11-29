"""
RDF Validator Engine

Responsibilities:
 - Load RDF (.ttl) files from instances directory
 - Validate RDF syntax
 - Run SHACL validation using pySHACL against audio, text, video, and common shapes
 - Generate validation reports (JSON) and log actions

Dependencies:
 - rdflib
 - pyshacl
 - json, logging, pathlib
 - rdf_schema for paths, namespaces, and SHACL config
"""

import json
import logging
from pathlib import Path
from typing import Dict

from rdflib import Graph
from pyshacl import validate

from app.models.rdf_schema import (
    INSTANCES_DIR,
    SHAPES_DIR,
    VALIDATION_REPORT_PATH,
    LOG_FILE_PATH,
    LOG_FORMAT,
    LOG_DATE_FORMAT,
    SHACL_CONFIG,
)

# Logging Configuration
logging.basicConfig(
    filename=LOG_FILE_PATH,
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT,
)
logger = logging.getLogger(__name__)

class RDFValidator:
    """
    Loads RDF files, validates syntax, runs SHACL validation,
    and produces a JSON report.
    """

    def __init__(self, instances_dir: Path = INSTANCES_DIR, shapes_dir: Path = SHAPES_DIR):
        self.instances_dir = instances_dir
        self.shapes_dir = shapes_dir
        self.graphs: Dict[str, Graph] = {}

    def load_ttl_files(self) -> None:
        """
        Load all TTL files from the instances directory into rdflib.Graph objects.

        Raises:
            FileNotFoundError: if no TTL files found
        """
        ttl_files = list(self.instances_dir.glob("*.ttl"))
        if not ttl_files:
            logger.warning(f"No TTL files found in {self.instances_dir}")
            raise FileNotFoundError(f"No TTL files found in {self.instances_dir}")

        for ttl_file in ttl_files:
            g = Graph()
            try:
                g.parse(ttl_file, format="turtle")
                self.graphs[ttl_file.name] = g
                logger.info(f"Loaded RDF file: {ttl_file.name} ({len(g)} triples)")
            except Exception as e:
                logger.error(f"Failed to parse {ttl_file.name}: {e}")

    def run_shacl_validation(self) -> Dict[str, Dict]:
        """
        Runs SHACL validation on all loaded graphs against corresponding shapes.

        Returns:
            Dict[str, Dict]: {filename: {conforms: bool, report_text: str, report_graph: rdflib.Graph}}
        """
        results = {}

        for filename, graph in self.graphs.items():
            shape_file = self._infer_shape_file(filename)
            shape_path = self.shapes_dir / shape_file

            if not shape_path.exists():
                logger.warning(f"Shape file not found for {filename}: {shape_path}")
                continue

            try:
                # Load both common and specific shape files
                common_shapes = self.shapes_dir / "common_shapes.ttl"
                shacl_graph = Graph()
                shacl_graph.parse(common_shapes, format="turtle")
                shacl_graph.parse(shape_path, format="turtle")


                conforms, report_graph, report_text = validate(
                    data_graph=graph,
                    shacl_graph=str(shape_path),
                    **SHACL_CONFIG,
                )
                results[filename] = {
                    "conforms": conforms,
                    "report_text": report_text.decode() if isinstance(report_text, bytes) else report_text,
                    "report_graph": report_graph,
                    "triple_count": len(graph),
                }
                logger.info(f"SHACL validation completed for {filename} | conforms={conforms}")
            except Exception as e:
                logger.error(f"SHACL validation failed for {filename}: {e}")

        return results

    def generate_report(self, validation_results: Dict[str, Dict], report_path: Path = VALIDATION_REPORT_PATH) -> None:
        """
        Save validation results to a JSON file.

        Args:
            validation_results: dict from run_shacl_validation()
            report_path: path to save the JSON report
        """
        report_data = {}
        for fname, result in validation_results.items():
            report_data[fname] = {
                "conforms": result["conforms"],
                "triple_count": result["triple_count"],
                "report_text": result["report_text"],
            }

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=4)
        logger.info(f"Validation report saved: {report_path}")

    @staticmethod
    def _infer_shape_file(filename: str) -> str:
        """
        Infer SHACL shape file name based on RDF instance file name.

        Args:
            filename: e.g., audio_metadata.ttl, text_metadata.ttl, video_metadata.ttl

        Returns:
            corresponding shape file name
        """
        if "audio" in filename.lower():
            return "audio_shapes.ttl"
        elif "text" in filename.lower():
            return "text_shapes.ttl"
        elif "video" in filename.lower():
            return "video_shapes.ttl"
        else:
            return "common_shapes.ttl"

# CLI Usage
if __name__ == "__main__":
    validator = RDFValidator()
    validator.load_ttl_files()
    results = validator.run_shacl_validation()
    validator.generate_report(results)
    logger.info("RDF validation pipeline completed successfully.")
