from datetime import datetime
from pydantic import BaseModel, UUID4


class DocumentMetadata(BaseModel):
    name: str
    number: str | None = None
    readers: list[str]
    created_at: datetime
    datasource: list[str]
    attachment_name: str | None = None


class Document(BaseModel):
    page_content: str
    metadata: DocumentMetadata


class Session(BaseModel):
    id: UUID4
    documents: list[Document]
