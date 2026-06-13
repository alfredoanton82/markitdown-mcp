import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from .converters import convert_to_markdown, get_file_hash, get_file_type, validate_file
from .database import get_database_manager
from .models import Document, ProcessingResult

logger = logging.getLogger(__name__)

CACHE_DIR = Path.home() / ".claude/skills/markitdown-mcp/data/cache"


def _ensure_cache_dir() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _save_markdown_cache(file_id: str, markdown: str) -> None:
    _ensure_cache_dir()
    cache_file = CACHE_DIR / f"{file_id}.md"
    cache_file.write_text(markdown, encoding="utf-8")


def _load_markdown_cache(file_id: str) -> str | None:
    cache_file = CACHE_DIR / f"{file_id}.md"
    if cache_file.exists():
        return cache_file.read_text(encoding="utf-8")
    return None


def process_document(
    file_path: str,
    convert_to_md: bool = True,
    store_in_db: bool = True,
) -> dict[str, Any]:
    """Convert a document to markdown and store in local DB."""
    start_time = time.time()
    db = get_database_manager()

    is_valid, error = validate_file(file_path)
    if not is_valid:
        return {"status": "error", "error_type": "validation_error", "error_message": error}

    file_hash = get_file_hash(file_path)
    filename = Path(file_path).name

    # Return cached result if same file was processed before
    with db.get_session() as session:
        existing = session.query(Document).filter_by(file_hash=file_hash, status="completed").first()
        if existing:
            result = session.query(ProcessingResult).filter_by(document_id=existing.id).first()
            markdown = _load_markdown_cache(existing.id) or (result.markdown if result else "")
            logger.debug(f"Cache hit for {filename}: {existing.id}")
            return {
                "file_id": existing.id,
                "filename": existing.filename,
                "status": "completed",
                "markdown": markdown,
                "markdown_size_bytes": len(markdown.encode()),
                "processed_at": existing.processed_at.isoformat() if existing.processed_at else None,
                "processing_time_seconds": 0.0,
                "cached": True,
            }

    file_id = str(uuid4())
    doc = Document(
        id=file_id,
        filename=filename,
        original_path=file_path,
        file_type=get_file_type(file_path),
        file_hash=file_hash,
        status="processing",
    )

    if store_in_db:
        db.save_document(doc)

    markdown, error = convert_to_markdown(file_path)
    if error:
        doc.status = "error"
        doc.error_message = error
        if store_in_db:
            db.save_document(doc)
        return {"status": "error", "error_type": "conversion_error", "error_message": error, "file_id": file_id}

    processing_time = time.time() - start_time
    doc.status = "completed"
    doc.processed_at = datetime.utcnow()
    doc.markdown_size = len(markdown.encode())

    _save_markdown_cache(file_id, markdown)

    if store_in_db:
        with db.get_session() as session:
            session.merge(doc)
            result = ProcessingResult(
                id=str(uuid4()),
                document_id=file_id,
                markdown=markdown,
                processing_time_seconds=processing_time,
            )
            session.add(result)

    logger.info(f"Processed {filename} in {processing_time:.2f}s")
    return {
        "file_id": file_id,
        "filename": filename,
        "status": "completed",
        "markdown": markdown,
        "markdown_size_bytes": len(markdown.encode()),
        "processed_at": doc.processed_at.isoformat(),
        "processing_time_seconds": round(processing_time, 2),
        "cached": False,
    }


def get_markdown(file_id: str) -> dict[str, Any]:
    """Retrieve stored markdown for a document."""
    db = get_database_manager()
    doc = db.get_document(file_id)

    if not doc:
        return {"status": "error", "error_type": "not_found", "error_message": f"Document {file_id} not found"}

    markdown = _load_markdown_cache(file_id)
    if not markdown:
        with db.get_session() as session:
            result = session.query(ProcessingResult).filter_by(document_id=file_id).first()
            markdown = result.markdown if result else ""

    return {
        "file_id": file_id,
        "filename": doc.filename,
        "markdown": markdown or "",
        "markdown_size_bytes": len((markdown or "").encode()),
    }


def list_documents(limit: int = 10, offset: int = 0) -> dict[str, Any]:
    """List processed documents."""
    db = get_database_manager()
    with db.get_session() as session:
        total = session.query(Document).count()
        docs = (
            session.query(Document)
            .order_by(Document.uploaded_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return {
            "documents": [
                {
                    "file_id": d.id,
                    "filename": d.filename,
                    "status": d.status,
                    "file_type": d.file_type,
                    "markdown_size": d.markdown_size,
                    "processed_at": d.processed_at.isoformat() if d.processed_at else None,
                }
                for d in docs
            ],
            "total": total,
            "limit": limit,
            "offset": offset,
        }


def search_summaries(query: str, limit: int = 5) -> dict[str, Any]:
    """Search across stored markdown content."""
    db = get_database_manager()
    query_lower = query.lower()
    results = []

    with db.get_session() as session:
        docs = session.query(Document).filter_by(status="completed").all()
        for doc in docs:
            markdown = _load_markdown_cache(doc.id) or ""
            if query_lower in markdown.lower() or query_lower in doc.filename.lower():
                idx = markdown.lower().find(query_lower)
                excerpt = markdown[max(0, idx - 100): idx + 200].strip() if idx >= 0 else markdown[:300]
                results.append({
                    "file_id": doc.id,
                    "filename": doc.filename,
                    "summary_excerpt": excerpt,
                    "relevance_score": 1.0 if query_lower in doc.filename.lower() else 0.8,
                })

    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    return {"results": results[:limit], "total_results": len(results)}


def get_summary(file_id: str) -> dict[str, Any]:
    """Get document metadata (summary is handled by NotebookLM MCP)."""
    db = get_database_manager()
    doc = db.get_document(file_id)

    if not doc:
        return {"status": "error", "error_type": "not_found", "error_message": f"Document {file_id} not found"}

    return {
        "file_id": doc.id,
        "filename": doc.filename,
        "status": doc.status,
        "file_type": doc.file_type,
        "markdown_size": doc.markdown_size,
        "processed_at": doc.processed_at.isoformat() if doc.processed_at else None,
    }
