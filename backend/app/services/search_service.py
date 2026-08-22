from typing import Any


class SearchService:
    """
    Interface between the MCP layer and the knowledge-base search system.

    The actual Qdrant implementation will be provided by the
    document/vector-search module.
    """

    def search_notes(
        self,
        user_id: str,
        query: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        raise NotImplementedError(
            "SearchService.search_notes() is not implemented yet."
        )

    def get_document(
        self,
        user_id: str,
        doc_id: str,
    ) -> dict[str, Any]:
        raise NotImplementedError(
            "SearchService.get_document() is not implemented yet."
        )

    def list_sources(
        self,
        user_id: str,
    ) -> list[dict[str, Any]]:
        raise NotImplementedError(
            "SearchService.list_sources() is not implemented yet."
        )