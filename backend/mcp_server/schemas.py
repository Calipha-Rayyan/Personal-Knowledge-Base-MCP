from pydantic import BaseModel


class SearchResult(BaseModel):
    document_id: str
    filename: str
    page: int | None = None
    chunk_text: str
    score: float


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
    message: str | None = None


class DocumentResponse(BaseModel):
    document_id: str
    filename: str
    content: str


class SourceInfo(BaseModel):
    document_id: str
    filename: str


class SourcesResponse(BaseModel):
    sources: list[SourceInfo]
