"""
Defines the domain ontology and project-wide RDF configuration
for the multimodal knowledge graph using rdflib.

Exported elements:
 - NAMESPACES: mapping of prefix -> rdflib.Namespace
 - AUDIO_CLASS, VIDEO_CLASS, TEXT_CLASS: URIs for core classes
 - Core properties: title, description, uploadTimestamp, namespace, etc.
 - build_ontology_graph(): helper to create a graph containing ontology declarations
 - BASE_DIR, INSTANCES_DIR, SHAPES_DIR, REPORTS_DIR, LOGS_DIR: file paths
 - SHACL_CONFIG: settings for SHACL validation
 - REPORT paths: validation, merge, merged graph
 - LOG configuration
"""

from rdflib import Namespace, URIRef, Graph, RDF, RDFS, Literal
from pathlib import Path
from typing import Dict

# RDF Namespaces
NAMESPACES: Dict[str, Namespace] = {
    "ex": Namespace("http://example.org/flow/"),
    "flow": Namespace("http://flow_ai.org/ontology#"),
    "schema": Namespace("http://schema.org/"),
    "dcterms": Namespace("http://purl.org/dc/terms/"),
    "rdf": Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
    "rdfs": Namespace("http://www.w3.org/2000/01/rdf-schema#"),
    "owl": Namespace("http://www.w3.org/2002/07/owl#"),
    "xsd": Namespace("http://www.w3.org/2001/XMLSchema#"),
}

# Shortcuts
EX = NAMESPACES["ex"]
FLOW = NAMESPACES["flow"]
SCHEMA = NAMESPACES["schema"]
DCTERMS = NAMESPACES["dcterms"]
XSD = NAMESPACES["xsd"]

# Core Classes
AUDIO_CLASS: URIRef = FLOW.AudioFile
VIDEO_CLASS: URIRef = FLOW.VideoFile
TEXT_CLASS: URIRef = FLOW.TextFile
RESOURCE_CLASS: URIRef = FLOW.Resource

# Core Properties
TITLE = DCTERMS.title
DESCRIPTION = DCTERMS.description
UPLOAD_TIMESTAMP = FLOW.uploadTimestamp
NAMESPACE_PROP = FLOW.namespace
FILE_FORMAT = FLOW.fileFormat
FILE_SIZE_MB = FLOW.fileSizeMB
CHUNK_COUNT = FLOW.chunkCount
EMBEDDING_STATUS = FLOW.embeddingStatus
EMBEDDING_MODEL = FLOW.embeddingModel
TRANSCRIPT = FLOW.transcript

# File System Paths
BASE_DIR = Path(__file__).resolve().parents[2] / "knowledge_graph"
INSTANCES_DIR = BASE_DIR / "instances"
MERGE_DIR = BASE_DIR / "merge_report"
SHAPES_DIR = BASE_DIR / "shapes"
REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = REPORTS_DIR / "logs"


# Ensure directories exist
for _dir in (REPORTS_DIR, MERGE_DIR, LOGS_DIR):
    _dir.mkdir(parents=True, exist_ok=True)

# SHACL Validation Settings
SHACL_CONFIG = {
    "inference": "rdfs",
    "abort_on_first": False,
    "meta_shacl": True,
    "advanced": True,
    "debug": False,
}

# Report Paths
VALIDATION_REPORT_PATH = REPORTS_DIR / "validation_report.json"
MERGE_REPORT_PATH = REPORTS_DIR / "merge_report.json"

# Merge graph report
MERGED_GRAPH_PATH = MERGE_DIR / "merged_graph.ttl"

# Logging
LOG_FILE_PATH = LOGS_DIR / "rdf_validation.log"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Ontology Graph
def build_ontology_graph() -> Graph:
    """
    Create an rdflib Graph containing basic ontology declarations:
      - Classes and rdfs:labels
      - Properties and rdfs:labels / domain / range

    Returns:
        rdflib.Graph with ontology triples.
    """
    g = Graph()

    # Bind prefixes
    for prefix, ns in NAMESPACES.items():
        g.bind(prefix, ns)

    # Declare classes
    g.add((RESOURCE_CLASS, RDF.type, RDFS.Class))
    g.add((RESOURCE_CLASS, RDFS.label, Literal("Resource")))

    for cls, label in [(AUDIO_CLASS, "AudioFile"), (VIDEO_CLASS, "VideoFile"), (TEXT_CLASS, "TextFile")]:
        g.add((cls, RDF.type, RDFS.Class))
        g.add((cls, RDFS.subClassOf, RESOURCE_CLASS))
        g.add((cls, RDFS.label, Literal(label)))

    # Declare properties
    props = [
        (TITLE, "title", None, None),
        (DESCRIPTION, "description", None, None),
        (UPLOAD_TIMESTAMP, "uploadTimestamp", None, XSD.dateTime),
        (NAMESPACE_PROP, "namespace", None, None),
        (FILE_FORMAT, "fileFormat", None, None),
        (FILE_SIZE_MB, "fileSizeMB", None, None),
        (CHUNK_COUNT, "chunkCount", None, None),
        (EMBEDDING_STATUS, "embeddingStatus", None, None),
        (EMBEDDING_MODEL, "embeddingModel", None, None),
        (TRANSCRIPT, "transcript", None, None),
    ]

    for prop_uri, label, _, datatype in props:
        g.add((prop_uri, RDF.type, RDF.Property))
        g.add((prop_uri, RDFS.label, Literal(label)))
        if datatype:
            g.add((prop_uri, RDFS.range, datatype))
        g.add((prop_uri, RDFS.domain, RESOURCE_CLASS))

    return g
