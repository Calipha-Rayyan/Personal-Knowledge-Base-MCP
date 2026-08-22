from fastmcp import FastMCP

from .tools import MCPTools
from .schemas import (
    SearchResponse,
    DocumentResponse,
    SourcesResponse,
)


mcp = FastMCP(
    "Personal Knowledge Base MCP"
)


# Temporary development search service.
#
# Member 2 will later provide the real implementation.
class TemporarySearchService:
    def search_notes(
        self,
        user_id: str,
        query: str,
        top_k: int = 5,
    ):
        return []

    def get_document(
        self,
        user_id: str,
        doc_id: str,
    ):
        return {
            "document_id": doc_id,
            "filename": "Not available",
            "content": "",
        }

    def list_sources(self, user_id: str):
        return []


search_service = TemporarySearchService()
tools = MCPTools(search_service)


@mcp.tool
def search_notes(
    user_id: str,
    query: str,
    top_k: int = 5,
) -> SearchResponse:
    """
    Search the user's personal knowledge base using semantic search.

    Returns ranked document chunks with source information.
    """

    return tools.search_notes(
        user_id=user_id,
        query=query,
        top_k=top_k,
    )


@mcp.tool
def get_document(
    user_id: str,
    doc_id: str,
) -> DocumentResponse:
    """
    Retrieve the full content of a document belonging to the user.
    """

    return tools.get_document(
        user_id=user_id,
        doc_id=doc_id,
    )


@mcp.tool
def list_sources(
    user_id: str,
) -> SourcesResponse:
    """
    List documents available in the user's personal knowledge base.
    """

    return tools.list_sources(
        user_id=user_id,
    )


if __name__ == "__main__":
    mcp.run()