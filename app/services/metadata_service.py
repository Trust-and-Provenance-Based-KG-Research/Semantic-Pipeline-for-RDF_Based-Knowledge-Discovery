"""
Provides a MetadataService class that encapsulates safe JSON read/write/update
operations used by the multimodal ingestion pipeline.
"""

from pathlib import Path
import json
from typing import Optional, Dict, Any
from datetime import datetime
import tempfile


class MetadataService:
    """Provides methods to manage metadata JSON files safely and atomically."""

    def __init__(self):
        pass

    def _safe_json_load(self, path: Path) -> Optional[Dict[str, Any]]:
        try:
            with open(path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            return None

    def _safe_json_dump(self, data: Dict[str, Any], path: Path) -> bool:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                "w", delete=False, dir=str(path.parent), encoding="utf-8"
            ) as tmp:
                json.dump(data, tmp, indent=4, ensure_ascii=False)
                tmp.flush()
                tmp_name = Path(tmp.name)
            tmp_name.replace(path)
            return True
        except Exception:
            return False

    def find_metadata_for_file(self, original_file_name: str, meta_dir: Path) -> Optional[Path]:
        """Find metadata JSON for the given filename."""
        if not meta_dir.exists():
            return None

        for meta_file in meta_dir.glob("*.json"):
            data = self._safe_json_load(meta_file)
            if not data:
                continue
            if data.get("file_name") == original_file_name:
                return meta_file
        return None

    def load_metadata(self, meta_path: Path) -> Optional[Dict[str, Any]]:
        """Load and return metadata dict."""
        return self._safe_json_load(meta_path)

    def write_metadata(self, meta_path: Path, metadata: Dict[str, Any]) -> bool:
        """Atomically write metadata."""
        return self._safe_json_dump(metadata, meta_path)

    def update_metadata_field(self, meta_path: Path, field: str, value: Any) -> bool:
        """Update a single field in the metadata JSON file."""
        data = self.load_metadata(meta_path)
        if data is None:
            data = {"file_name": meta_path.stem}

        data[field] = value
        data["updated_at"] = datetime.utcnow().isoformat() + "Z"
        return self.write_metadata(meta_path, data)

    def save_metadata(self, metadata: Dict[str, Any], meta_dir: Path) -> bool:
        """Save metadata to the appropriate folder (default naming)."""
        file_name = metadata.get("file_name") or "unknown_file"
        meta_path = meta_dir / f"{file_name}.json"
        return self._safe_json_dump(metadata, meta_path)

    def get_namespace(self, meta_path: Path) -> Optional[str]:
        """Extract and return the namespace from a metadata JSON file."""
        data = self.load_metadata(meta_path)
        if not data:
            return None
        return data.get("namespace")
