from datetime import datetime
from pydantic import BaseModel, UUID4


class DocumentMetadata(BaseModel):
    created_at: datetime
    name: str
    readers: list[str]
    data_source: list[str]
    number: str | None = None
    attachment_name: str | None = None


class Document(BaseModel):
    page_content: str
    metadata: DocumentMetadata


class Session(BaseModel):
    id: UUID4
    documents: list[Document]
