import logging
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Generator, Optional

from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session, sessionmaker

from .models import Base, Document

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and operations."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize database manager with SQLite database."""
        if db_path is None:
            db_path = str(Path.home() / ".claude/skills/markitdown-mcp/data/documents.db")

        self.db_path = db_path
        self.db_dir = Path(db_path).parent
        self.db_dir.mkdir(parents=True, exist_ok=True)

        self.engine = create_engine(f"sqlite:///{db_path}")
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def init_db(self) -> None:
        """Create database and tables if they don't exist."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.debug(f"Database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Context manager for database sessions."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    def get_document(self, file_id: str) -> Optional[Document]:
        """Retrieve a document by its ID."""
        try:
            with self.get_session() as session:
                doc = session.query(Document).filter(Document.id == file_id).first()
                logger.debug(f"Retrieved document: {file_id}")
                return doc
        except Exception as e:
            logger.error(f"Failed to retrieve document {file_id}: {e}")
            raise

    def save_document(self, doc: Document) -> Document:
        """Save a document to the database."""
        try:
            with self.get_session() as session:
                session.add(doc)
                session.flush()
                logger.debug(f"Saved document: {doc.id}")
                return doc
        except Exception as e:
            logger.error(f"Failed to save document: {e}")
            raise

    def delete_old_cache(self, days: int = 30) -> int:
        """Delete documents older than specified days."""
        try:
            with self.get_session() as session:
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                stmt = delete(Document).where(Document.uploaded_at < cutoff_date)
                result = session.execute(stmt)
                deleted_count = result.rowcount
                logger.debug(f"Deleted {deleted_count} documents older than {days} days")
                return deleted_count
        except Exception as e:
            logger.error(f"Failed to delete old cache: {e}")
            raise


_db_manager: Optional[DatabaseManager] = None


def init_db(db_path: Optional[str] = None) -> DatabaseManager:
    """Initialize database manager."""
    global _db_manager
    _db_manager = DatabaseManager(db_path)
    _db_manager.init_db()
    return _db_manager


def get_session() -> Generator[Session, None, None]:
    """Get database session."""
    if _db_manager is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _db_manager.get_session()


def get_database_manager() -> DatabaseManager:
    """Get the database manager instance."""
    if _db_manager is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _db_manager
