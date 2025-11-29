"""
Centralized logging configuration for the multimodal ingestion project.
Provides a `get_logger` helper that returns a configured logger with both
console and rotating-file handlers. Intended to be imported and used across
services and pipelines to ensure consistent log formatting and retention.
"""

from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler


LOG_DIR = Path(__file__).resolve().parents[2] / "app" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "app.log"


def get_logger(name: str = "multimodal_ingest", level: int = logging.INFO, max_bytes: int = 10 * 1024 * 1024, backup_count: int = 5):
    """
    Create and return a logger configured with a stream handler and a
    rotating file handler.

    Args:
        name: logger name
        level: logging level (e.g., logging.INFO)
        max_bytes: maximum bytes per log file before rotation
        backup_count: number of rotated log files to keep

    Returns:
        logging.Logger: configured logger instance
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        # Avoid adding handlers multiple times if logger already configured
        return logger

    logger.setLevel(level)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    ch.setFormatter(ch_formatter)
    logger.addHandler(ch)

    # Rotating file handler
    fh = RotatingFileHandler(str(LOG_FILE), maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
    fh.setLevel(level)
    fh_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    fh.setFormatter(fh_formatter)
    logger.addHandler(fh)

    # Avoid propagating to root logger
    logger.propagate = False

    return logger

