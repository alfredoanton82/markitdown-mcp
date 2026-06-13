from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict, Any


class DocumentSchema(BaseModel):
    file_id: str
    filename: str
    status: str
    processed_at: Optional[datetime] = None
    markdown_size: Optional[int] = None


class ProcessDocumentRequest(BaseModel):
    file_path: str
    store_in_db: bool = True


class ProcessDocumentResponse(BaseModel):
    file_id: str
    filename: str
    status: str
    markdown: str
    markdown_size_bytes: int
    processed_at: Optional[str] = None
    processing_time_seconds: float
    cached: bool = False


class GetMarkdownResponse(BaseModel):
    file_id: str
    filename: str
    markdown: str
    markdown_size_bytes: int


class ListDocumentsResponse(BaseModel):
    documents: List[DocumentSchema]
    total: int
    limit: int
    offset: int


class SearchSummariesResponse(BaseModel):
    results: List[Dict[str, Any]]
    total_results: int


class GetSummaryResponse(BaseModel):
    file_id: str
    filename: str
    status: str
    file_type: Optional[str] = None
    markdown_size: Optional[int] = None
    processed_at: Optional[str] = None


class ErrorResponse(BaseModel):
    error_type: str
    error_message: str
    file_id: Optional[str] = None
