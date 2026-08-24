from mcp_server.schemas import (
    DocumentResponse,
    SearchResponse,
    SearchResult,
    SourceInfo,
    SourcesResponse,
)
from app.services.search_service import SearchService


class MCPTools:
    """
    MCP tool layer. Connects MCP tools to the application's single
    SearchService implementation (app/services/search_service.py),
    which itself calls the Qdrant-backed ingestion/processor module.

    No duplicate Qdrant logic lives here.
    """

    def __init__(self, search_service: SearchService):
        self.search_service = search_service

    def search_notes(
        self,
        user_id: str,
        query: str,
        top_k: int = 5,
    ) -> SearchResponse:

        query = query.strip()

        if not query:
            return SearchResponse(
                query=query,
                results=[],
                message="Please provide a search query.",
            )

        if top_k < 1:
            top_k = 1
        if top_k > 20:
            top_k = 20

        raw_results = self.search_service.search_notes(
            user_id=user_id,
            query=query,
            top_k=top_k,
        )

        results = [
            SearchResult(
                document_id=item["document_id"],
                filename=item["filename"],
                page=item.get("page"),
                chunk_text=item["chunk_text"],
                score=float(item["score"]),
            )
            for item in raw_results
        ]

        if not results:
            return SearchResponse(
                query=query,
                results=[],
                message="No confident match found.",
            )

        return SearchResponse(
            query=query,
            results=results,
        )

    def get_document(
        self,
        user_id: str,
        doc_id: str,
    ) -> DocumentResponse:

        document = self.search_service.get_document(
            user_id=user_id,
            doc_id=doc_id,
        )

        return DocumentResponse(
            document_id=document["document_id"],
            filename=document["filename"],
            content=document["content"],
        )

    def list_sources(
        self,
        user_id: str,
    ) -> SourcesResponse:

        sources = self.search_service.list_sources(
            user_id=user_id,
        )

        result = [
            SourceInfo(
                document_id=item["document_id"],
                filename=item["filename"],
            )
            for item in sources
        ]

        return SourcesResponse(sources=result)
