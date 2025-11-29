"""
Pydantic models for metadata validation and RDF pipeline responses.
Used across the RDF knowledge discovery API.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


# File & Metadata Models

class FileMetadata(BaseModel):
    """Metadata about an uploaded or generated RDF-related file."""
    file_name: str = Field(..., description="The name of the file.")
    file_format: str = Field(..., description="File format, e.g., 'ttl', 'trig'.")
    file_size_MB: float = Field(..., description="File size in megabytes.")
    upload_timestamp: str = Field(..., description="ISO 8601 timestamp when file was uploaded.")
    namespace: str = Field(..., description="Base namespace or ontology URI associated with the file.")
    file_description: Optional[str] = Field(None, description="Optional description or notes about the file.")


# RDF Generation & Upload Responses

class GenerateRDFResponse(BaseModel):
    """Response returned after generating RDF files from metadata."""
    status: str = Field(..., description="Overall status of the RDF generation (e.g., 'success' or 'failed').")
    generated_files: Dict[str, str] = Field(
        ..., description="Mapping of file type to file path or URI (e.g., {'ttl': 'path/to/file.ttl'})."
    )


class UploadAllResponse(BaseModel):
    """Response after batch uploading multiple RDF files."""
    status: str = Field(..., description="Overall status of the upload process.")
    results: Dict[str, str] = Field(
        ..., description="Mapping of each file name to its upload status or repository URI."
    )