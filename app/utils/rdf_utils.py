"""
Utilities for building RDF resources and serializing graphs.
Functions:
 - create_uri(resource_type: str, identifier: str) -> URIRef
 - register_namespaces(graph) -> None
 - create_resource_triple_set(graph, resource_uri, resource_type_uri, props: dict) -> None
 - serialize_graph_to_ttl(graph, path) -> None
 - new_graph_with_bindings() -> Graph
"""

from rdflib import Graph, URIRef, Literal, XSD
from rdflib.namespace import RDF
from typing import Dict, Any
import re
import os
import yaml
from pathlib import Path

from app.models.rdf_schema import NAMESPACES, FLOW, AUDIO_CLASS, VIDEO_CLASS, TEXT_CLASS

# A safe slug generator for identifiers to produce URL-safe fragment or paths
def _safe_slug(value: str) -> str:
    # Lowercase, replace spaces and illegal chars with underscore
    s = re.sub(r"\s+", "_", value.strip())
    s = re.sub(r"[^a-zA-Z0-9_\-\.]", "", s)
    return s

def load_rdf_config(config_path: str = "app/config/graphdb_config.yaml") -> dict:
    """
    Load RDF/GraphDB configuration from YAML file.
    Returns a dictionary containing:
      - graphdb: connection settings
      - namespaces: prefix to URI mappings
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(path, "r") as f:
        config = yaml.safe_load(f)
    return config


def create_uri(resource_type: str, identifier: str, base_ns: str = "flow") -> URIRef:
    """
    Create a stable URIRef for a resource.
    Args:
        resource_type: e.g., "audio", "video", "text" or a custom label
        identifier: unique id (preferably the namespace field from metadata)
        base_ns: which prefix from rdf_schema.NAMESPACES to use for base (default "flow")

    Returns:
        rdflib.URIRef
    """
    ns = NAMESPACES.get(base_ns)
    if ns is None:
        # fallback to example namespace
        ns = NAMESPACES["ex"]

    slug = _safe_slug(identifier)
    # Use resource_type as an intermediate path segment for readability
    uri = ns[f"{resource_type}/{slug}"]
    return URIRef(uri)

def register_namespaces(g: Graph, config_path: str = "app/config/graphdb_config.yaml") -> None:
    """
    Register namespaces defined in the config file (and rdf_schema fallback).
    """
    try:
        config = load_rdf_config(config_path)
        namespaces = config.get("namespaces", {})
        for prefix, uri in namespaces.items():
            if uri:
                g.bind(prefix, uri)
    except Exception:
        # fallback to rdf_schema static bindings
        from app.models.rdf_schema import NAMESPACES
        for prefix, ns in NAMESPACES.items():
            g.bind(prefix, ns)


def new_graph_with_bindings() -> Graph:
    """
    Create a fresh rdflib Graph with registered namespace bindings.
    """
    g = Graph()
    register_namespaces(g)
    return g

def create_resource_triple_set(g: Graph, resource_uri: URIRef, resource_type_uri: URIRef, props: Dict[str, Any]) -> None:
    """
    Add triples for a resource to the provided graph.

    Args:
        g: rdflib.Graph
        resource_uri: URIRef for the resource
        resource_type_uri: class URIRef (AudioFile, VideoFile, TextFile)
        props: mapping from property URI (or string key recognized below) to value

    Supported short keys (when a string key is used instead of full URI):
      - title, description, upload_timestamp, namespace, file_format, file_size_mb, chunk_count,
        embedding_status, embedding_model, transcript

    Values:
      - if the value looks like a datetime (ISO), it will be typed as xsd:dateTime
      - numeric values become xsd:decimal (rdflib Literal auto-detection suffices in many cases)
    """
    # type triple
    g.add((resource_uri, RDF.type, resource_type_uri))

    # map short keys to property URIs if user passed short names
    from app.models.rdf_schema import (
        TITLE,
        DESCRIPTION,
        UPLOAD_TIMESTAMP,
        NAMESPACE_PROP,
        FILE_FORMAT,
        FILE_SIZE_MB,
        CHUNK_COUNT,
        EMBEDDING_STATUS,
        EMBEDDING_MODEL,
        TRANSCRIPT,
    )

    key_map = {
        "title": TITLE,
        "description": DESCRIPTION,
        "upload_timestamp": UPLOAD_TIMESTAMP,
        "namespace": NAMESPACE_PROP,
        "file_format": FILE_FORMAT,
        "file_size_mb": FILE_SIZE_MB,
        "chunk_count": CHUNK_COUNT,
        "embedding_status": EMBEDDING_STATUS,
        "embedding_model": EMBEDDING_MODEL,
        "transcript": TRANSCRIPT,
    }

    for k, v in props.items():
        prop = key_map.get(k, None)
        # if user supplied a full URIRef-like string, try to use it
        if prop is None:
            # If k looks like a namespaced prefixed name (e.g., dcterms:title) try to resolve
            if isinstance(k, str) and ":" in k:
                prefix, local = k.split(":", 1)
                ns = NAMESPACES.get(prefix)
                if ns:
                    prop = ns[local]
        if prop is None:
            # Skip unknown property
            continue

        # Create typed literal where appropriate
        if isinstance(v, str) and _is_iso_datetime(v):
            lit = Literal(v, datatype=XSD.dateTime)
        else:
            lit = Literal(v)
        g.add((resource_uri, prop, lit))

def _is_iso_datetime(value: str) -> bool:
    """
    Simple heuristic to determine if a string looks like an ISO datetime (YYYY-MM-DD...).
    Keeps this lightweight; for strict validation use dateutil or datetime parsing.
    """
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", value))

def serialize_graph_to_ttl(g: Graph, path: str, overwrite: bool = True) -> None:
    """
    Serialize a graph to Turtle (ttl) file.
    Creates parent directories if necessary.

    Args:
        g: rdflib.Graph
        path: filesystem path to write (e.g., knowledge_graph/instances/audio_data.ttl)
        overwrite: if False and file exists, will raise FileExistsError
    """
    parent = os.path.dirname(path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)

    if not overwrite and os.path.exists(path):
        raise FileExistsError(f"{path} already exists and overwrite=False")

    g.serialize(destination=path, format="turtle")

# Small example helper to choose class URI from a resource_type string
def class_for_resource_type(resource_type: str):
    rt = resource_type.lower()
    if rt in ("audio", "audiofile"):
        return AUDIO_CLASS
    if rt in ("video", "videofile"):
        return VIDEO_CLASS
    if rt in ("text", "textfile", "document"):
        return TEXT_CLASS
    # fallback to generic resource class
    from app.models.rdf_schema import RESOURCE_CLASS
    return RESOURCE_CLASS


