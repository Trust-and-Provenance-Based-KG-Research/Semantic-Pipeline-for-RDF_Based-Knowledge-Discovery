# Semantic Pipeline for RDF-Based Knowledge Discovery

From Multimodal Data to Knowledge Graphs

This project implements a full semantic processing pipeline that converts multimodal raw data (text, audio, and video) into structured RDF knowledge graphs. The system extracts metadata, generates linked semantic triples, validates them against SHACL shapes, and merges instances into a unified RDF repository for querying and reasoning.

---

## Key Features

* Processes multimodal data (PDFs, transcripts, audio, video)
* Generates standardized RDF triples using an extensible ontology
* Produces `.ttl` instance graphs for each modality
* Validates RDF output using SHACL constraints
* Merges graphs into a unified global knowledge graph
* Exposes pipelines and RDF operations through REST API endpoints
* Supports GraphDB ingestion and SPARQL querying

---

## Architecture Overview

```
Raw Data (PDF/Text/Audio/Video)
        ↓
Metadata Extraction (pipelines)
        ↓
RDF Triple Generation (transform_to_ttl)
        ↓
Validation (SHACL shapes)
        ↓
Knowledge Graph Output (.ttl/.trig)
        ↓
GraphDB Storage + SPARQL Querying
```

Core modules:

| Component                                 | Responsibility                                       |
| ----------------------------------------- | ---------------------------------------------------- |
| utils/rdf_utils.py                        | URI creation, graph serialization, namespace binding |
| models/rdf_schema.py                      | Ontology classes, predicates, node definitions       |
| services/transform_to_ttl.py              | JSON metadata → RDF triple generation                |
| pipelines/rdf_generator_model_pipeline.py | End-to-end RDF processing pipeline                   |
| knowledge_graph/shapes/*.ttl              | SHACL validation rules for output triples            |
| validator/rdf_validator.py                | Schema conformance and SHACL inference               |
| routes/rdf_generator_routes.py            | API endpoints for generating and exporting RDF       |
| knowledge_graph/instances/                | Generated semantic data per processing run           |


## Running the Pipeline

```bash
uvicorn app.main:app
```

## API Endpoints

All functionality is exposed through FastAPI and accessible via Swagger UI at:

```
http://127.0.0.1:8000/docs
```

Below is the detailed breakdown of core operational endpoints.

---

### Upload

```
POST /upload/
```

Uploads a single file (video, audio, or text), extracts metadata, and stores the file in the appropriate directory.
This step initializes the resource lifecycle and ensures the system can ingest it into downstream pipelines.

---

### Ingestion Pipelines

```
POST /ingest/all
```

Runs the complete ingestion pipeline for audio, video, and text resources in one execution.

```
POST /ingest/audio
```

Processes only audio files. Extracts transcripts (if available), generates metadata, and prepares for embedding and RDF conversion.

```
POST /ingest/video
```

Processes only video files with transcript extraction and metadata generation.

---

### Embedding

```
POST /resource_embedding/
```

Generates embeddings for a resource’s metadata namespace. This applies to text, audio transcript, and video transcript content.
Embeddings support semantic search, description generation, and knowledge linking.

---

### Description Generation

```
POST /description_retrieval/
```

Generates a 150–200 word descriptive summary for a resource.
This step enriches metadata and ensures better contextual RDF representation.

Pipeline execution sequence:

1. Retrieve the resource namespace from metadata
2. Retrieve top 5 most relevant text chunks from ChromaDB
3. Generate a concise 150–200 word description using Groq LLaMA
4. Update the metadata JSON with the generated description

Arguments:
`metadata_path (str)` - Path to the metadata JSON file
`resource_path (str, optional)` - Resource file path, preserved for compatibility

Returns: `dict` containing success status and generation summary.

---

### Grouping Multimodal Data

```
POST /group_data/
```

Aggregates metadata from all modalities (Text/Audio/Video) into a unified `Grouped_multi_modal_data` directory.
Generated JSON files contain flat arrays of objects (no wrapper key).

---

### RDF Generation

```
POST /rdf/generate
```

Generates RDF models for available multimodal resources (audio, video, text) using the defined schema.
Returns a JSON summary mapping modality → generated TTL file paths.

---

### RDF Validation

```
POST /validator/validate
```

Validates all RDF instance graphs located in the `knowledge_graph/instances` directory.
Useful for quality checks before merge and GraphDB ingestion.

No parameters required.

---

### Graph Merging

```
POST /merger/named_graph
```

Performs merge into a named graph representation.

```
POST /merger/normal_graph
```

Performs merge into a single consolidated graph structure.



#### **Generate RDF triples manually from json metadata:**

```bash
python -m app.services.transform_to_ttl
```

## **Upload merged graph to GraphDB:**

```bash
curl -X POST \
  -H "Content-Type: application/x-trig" \
  --data-binary @knowledge_graph/merge_report/merged_graph.trig \
  "http://localhost:7200/repositories/flow_kg/statements"
```

---

## Use Cases

* Semantic indexing of heterogeneous documents
* Foundation for agents, KG-QA systems, or semantic search engines
* Research knowledge exploration and graph reasoning
* AI-assisted retrieval, summarization, and linking
* Automated ontology-based knowledge base construction
