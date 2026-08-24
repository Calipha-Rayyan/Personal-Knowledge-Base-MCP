from fastmcp import FastMCP

from mcp_server.tools import MCPTools
from mcp_server.schemas import (
    SearchResponse,
    DocumentResponse,
    SourcesResponse,
)
from app.services.search_service import get_search_service


mcp = FastMCP("Personal Knowledge Base MCP")

# Real, Qdrant-backed search service (the same one used by the FastAPI
# /search route) — replaces the old TemporarySearchService stub that
# always returned empty results.
tools = MCPTools(get_search_service())


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
