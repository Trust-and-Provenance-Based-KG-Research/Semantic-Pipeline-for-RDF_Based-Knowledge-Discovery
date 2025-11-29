"""
FastAPI routes to expose Graph Merge engine.

Endpoints:
 - POST /merger/named : Merge RDF graphs into a unified named graph (TriG)
 - POST /merger/normal : Merge RDF graphs into a normal merged graph (TTL)
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path

from knowledge_graph.validator.rdf_validator import RDFValidator
from knowledge_graph.validator.graph_merger import GraphMerger
from app.models.rdf_schema import MERGE_REPORT_PATH, MERGED_GRAPH_PATH

router = APIRouter(
    prefix="/merger",
    tags=["Graph Merger"]
)

# Base directory for TTL files
INSTANCE_DIR = Path(__file__).resolve().parents[2] / "knowledge_graph" / "instances"


def _validate_and_load_graphs() -> RDFValidator:
    """Helper function to validate and load RDF TTL files."""
    ttl_files = list(INSTANCE_DIR.glob("*.ttl"))
    if not ttl_files:
        raise HTTPException(status_code=404, detail=f"No TTL files found in {INSTANCE_DIR}")

    validator = RDFValidator()
    validator.load_ttl_files()
    validator.run_shacl_validation()
    return validator


@router.post("/named_graph")
async def merge_named_graphs():
    """
    Merge RDF graphs into a unified named graph (TriG format).

    Returns:
        JSON merge report
    """
    try:
        validator = _validate_and_load_graphs()
        merger = GraphMerger(validator)

        # Perform named graph merge
        merge_report = merger.named_graph_merger()

        # Save report and merged TriG
        merger.save_merge_report(merge_report, path=MERGE_REPORT_PATH.with_name("named_merge_report.json"))
        merger.save_merged_graph(graph_type="named")

        return JSONResponse(content=merge_report)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/normal_graph")
async def merge_normal_graphs():
    """
    Merge RDF graphs into a normal merged graph (TTL format, no named graphs).

    Returns:
        JSON merge report
    """
    try:
        validator = _validate_and_load_graphs()
        merger = GraphMerger(validator)

        # Perform normal graph merge
        merge_report = merger.normal_graph_merger()

        # Save report and merged TTL
        merger.save_merge_report(merge_report, path=MERGE_REPORT_PATH.with_name("normal_merge_report.json"))
        merger.save_merged_graph(graph_type="normal")

        return JSONResponse(content=merge_report)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
