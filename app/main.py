"""
FastAPI application entrypoint for the Multimodal Ingestion System.

This app allows:
- Uploading of video/audio/text files
- Running ingestion pipelines for transcription and metadata enrichment
- Grouping of metadata into a single multimodal collection
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import aud_vid_ingestion_routes, graph_merger_routes, upload_routes, group_data
from app.routes.embedding_routes import router as embedding_router
from app.routes.description_routes import router as description_router
from app.routes import rdf_validator_route
from app.routes import rdf_generator_routes
from app.services.logging_service import get_logger


logger = get_logger(__name__)

app = FastAPI(
    title="Semantic RDF Pipeline",
    description="Upload, transcribe, group, and manage multimedia data using FFmpeg + Whisper",
    version="1.0.0",
)

# Allow cross-origin requests (useful for web clients)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(upload_routes.router)
app.include_router(aud_vid_ingestion_routes.router)
app.include_router(embedding_router)
app.include_router(description_router)
app.include_router(group_data.router)

# Register RDF routes
app.include_router(rdf_generator_routes.router)
app.include_router(rdf_validator_route.router)
app.include_router(graph_merger_routes.router)

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Welcome to the Semantic Pipeline for RDF-Based Knowledge Discovery!"}

@app.on_event("startup")
async def startup_event():
    logger.info("Multimodal Ingestion API started successfully.")
