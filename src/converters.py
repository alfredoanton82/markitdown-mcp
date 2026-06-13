import logging
import hashlib
from pathlib import Path
from typing import Optional, Tuple
from markitdown import MarkItDown

logger = logging.getLogger(__name__)

SUPPORTED_TYPES = {".pdf", ".docx", ".xlsx", ".html", ".txt", ".md"}
MAX_FILE_SIZE_MB = 500


def get_file_hash(file_path: str) -> str:
    """Calculate MD5 hash of file for caching."""
    try:
        md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5.update(chunk)
        return md5.hexdigest()
    except Exception as e:
        logger.error(f"Failed to calculate hash for {file_path}: {e}")
        raise


def validate_file(file_path: str) -> Tuple[bool, Optional[str]]:
    """Validate file exists, type, and size."""
    path = Path(file_path)

    if not path.exists():
        return False, f"File not found: {file_path}"

    if path.suffix.lower() not in SUPPORTED_TYPES:
        return False, f"Unsupported file type: {path.suffix}"

    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        return False, f"File too large: {size_mb:.1f} MB (max {MAX_FILE_SIZE_MB} MB)"

    return True, None


def convert_to_markdown(file_path: str) -> Tuple[str, Optional[str]]:
    """Convert document to markdown using markitdown."""
    try:
        is_valid, error_msg = validate_file(file_path)
        if not is_valid:
            return "", error_msg

        path = Path(file_path)
        logger.debug(f"Converting {path.name} to markdown...")

        if path.suffix.lower() in {".txt", ".md"}:
            with open(file_path, "r", encoding="utf-8") as f:
                markdown_content = f.read()
            logger.debug(f"Read text file: {len(markdown_content)} chars")
            return markdown_content, None

        md = MarkItDown()
        result = md.convert(file_path)
        markdown_content = result.text_content

        if not markdown_content or len(markdown_content.strip()) == 0:
            return "", "Conversion resulted in empty markdown"

        logger.debug(f"Converted {path.name}: {len(markdown_content)} chars")
        return markdown_content, None

    except Exception as e:
        error_msg = f"Conversion error: {str(e)}"
        logger.error(f"Failed to convert {file_path}: {e}")
        return "", error_msg


def get_file_type(file_path: str) -> str:
    """Get file type from extension."""
    return Path(file_path).suffix.lower().lstrip(".")
