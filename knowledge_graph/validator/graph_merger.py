"""
Responsibilities:
 - Load validated RDF graphs (from rdf_validator)
 - Merge graphs into either:
     - a unified RDF dataset using named graphs (TriG)
     - a normal merged RDF dataset (TTL)
 - Generate merge report (JSON)
 - Export merged datasets to disk
"""

import json
import logging
from pathlib import Path
from typing import Dict

from rdflib import ConjunctiveGraph, Graph, URIRef

from .rdf_validator import RDFValidator
from app.models.rdf_schema import (
    MERGE_REPORT_PATH,
    MERGED_GRAPH_PATH,
    LOG_FILE_PATH,
    LOG_FORMAT,
    LOG_DATE_FORMAT,
    NAMESPACES,
)

# Logging Configuration
logging.basicConfig(
    filename=LOG_FILE_PATH,
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT,
)
logger = logging.getLogger(__name__)


class GraphMerger:
    """
    Merge validated RDF graphs into either:
      - a single unified RDF dataset using named graphs (TriG)
      - a normal merged RDF dataset (TTL)
    """

    def __init__(self, validator: RDFValidator):
        self.validator = validator
        self.conj_graph = ConjunctiveGraph()  # For named graph merging
        self.normal_graph = Graph()            # For normal graph merging

        # Bind namespaces
        for prefix, ns in NAMESPACES.items():
            self.conj_graph.bind(prefix, ns)
            self.normal_graph.bind(prefix, ns)

    def named_graph_merger(self) -> Dict[str, Dict]:
        """
        Merge validated graphs into named graphs within a ConjunctiveGraph.

        Returns:
            Dict[str, Dict]: merge report with graph name, triple count, status
        """
        merge_report = {}

        for filename, graph in self.validator.graphs.items():
            base_uri = "http://flow_ai.org/graph"
            category = (
                "audio" if "audio" in filename
                else "video" if "video" in filename
                else "text"
            )
            graph_name = URIRef(f"{base_uri}/{category}/{Path(filename).stem}")

            try:
                # Add triples to the ConjunctiveGraph with named graph context
                self.conj_graph.addN((s, p, o, graph_name) for s, p, o in graph)
                merge_report[filename] = {
                    "graph_uri": str(graph_name),
                    "triples_added": len(graph),
                    "status": "merged",
                }
                logger.info(f"Merged graph: {filename} into named graph {graph_name}")
            except Exception as e:
                merge_report[filename] = {
                    "graph_uri": str(graph_name),
                    "triples_added": 0,
                    "status": f"failed: {e}",
                }
                logger.error(f"Failed to merge {filename}: {e}")

        logger.info(f"Total triples in named graph merged dataset: {len(self.conj_graph)}")
        logger.info(f"Total named graphs merged: {len(merge_report)}")

        return merge_report

    def normal_graph_merger(self) -> Dict[str, Dict]:
        """
        Merge validated graphs into a normal RDF graph (no named graphs).

        Returns:
            Dict[str, Dict]: merge report with filename, triple count, status
        """
        merge_report = {}

        for filename, graph in self.validator.graphs.items():
            try:
                # Add triples to the normal graph
                for triple in graph:
                    self.normal_graph.add(triple)
                merge_report[filename] = {
                    "triples_added": len(graph),
                    "status": "merged",
                }
                logger.info(f"Merged graph: {filename} into normal RDF graph")
            except Exception as e:
                merge_report[filename] = {
                    "triples_added": 0,
                    "status": f"failed: {e}",
                }
                logger.error(f"Failed to merge {filename}: {e}")

        logger.info(f"Total triples in normal merged dataset: {len(self.normal_graph)}")
        return merge_report

    def save_merged_graph(
        self,
        graph_type: str = "named",
        path: Path = MERGED_GRAPH_PATH
    ) -> None:
        """
        Serialize the merged graph to disk.

        Args:
            graph_type: 'named' for TriG, 'normal' for TTL
            path: Path to save the merged dataset
        """
        try:
            if graph_type == "named":
                trig_path = path.with_suffix(".trig")
                self.conj_graph.serialize(destination=str(trig_path), format="trig")
                logger.info(f"Merged named graph dataset saved to {trig_path}")
            elif graph_type == "normal":
                ttl_path = path.with_suffix(".ttl")
                self.normal_graph.serialize(destination=str(ttl_path), format="turtle")
                logger.info(f"Merged normal RDF dataset saved to {ttl_path}")
            else:
                raise ValueError("graph_type must be 'named' or 'normal'")
        except Exception as e:
            logger.error(f"Failed to save merged dataset: {e}")

    def save_merge_report(
        self,
        report: Dict[str, Dict],
        path: Path = MERGE_REPORT_PATH
    ) -> None:
        """
        Save merge report as a JSON file.

        Args:
            report: merge report dictionary
            path: path to save JSON report
        """
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=4)
            logger.info(f"Merge report saved: {path}")
        except Exception as e:
            logger.error(f"Failed to save merge report: {e}")


if __name__ == "__main__":
    validator = RDFValidator()
    validator.load_ttl_files()
    validator.run_shacl_validation()

    merger = GraphMerger(validator)

    # Example: Named Graph Merge (TriG)
    named_report = merger.named_graph_merger()
    merger.save_merge_report(named_report)
    merger.save_merged_graph(graph_type="named")

    # Example: Normal Graph Merge (TTL)
    normal_report = merger.normal_graph_merger()
    merger.save_merge_report(normal_report, path=MERGE_REPORT_PATH.with_name("normal_merge_report.json"))
    merger.save_merged_graph(graph_type="normal")
    logger.info("Graph merge pipeline completed successfully.")
