from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from uuid import uuid4

Base = declarative_base()


class Document(Base):
    """Document model for storing file information and processing status."""
    __tablename__ = "documents"

    id: str = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    filename: str = Column(String(255), nullable=False)
    original_path: str = Column(String(500), nullable=True)
    file_type: str = Column(String(20), nullable=True)
    file_hash: str = Column(String(32), nullable=True)
    uploaded_at: datetime = Column(DateTime, default=datetime.utcnow)
    processed_at: datetime = Column(DateTime, nullable=True)
    status: str = Column(String(20), default="pending")
    markdown_size: int = Column(Integer, nullable=True)
    summary_size: int = Column(Integer, nullable=True)
    error_message: str = Column(Text, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<Document(id={self.id}, filename={self.filename}, "
            f"status={self.status}, file_type={self.file_type})>"
        )


class ProcessingResult(Base):
    """Processing result model for storing converted markdown content."""
    __tablename__ = "processing_results"

    id: str = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    document_id: str = Column(String(36), ForeignKey("documents.id"), nullable=False)
    markdown: str = Column(Text, nullable=True)
    processing_time_seconds: float = Column(Float, nullable=True)
    error_message: str = Column(Text, nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<ProcessingResult(id={self.id}, document_id={self.document_id})>"
