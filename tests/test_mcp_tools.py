"""
Tests for the MCP tool layer (mcp_server/tools.py) against the real
SearchService, independent of the FastMCP transport.

Run from backend/:
    pytest tests/test_mcp_tools.py -v
"""
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

os.environ["QDRANT_IN_MEMORY"] = "true"
os.environ["QDRANT_COLLECTION"] = "test_mcp_chunks"
os.environ["SEARCH_SCORE_THRESHOLD"] = "0.0"

from app.ingestion.processor import process_document
from app.services.search_service import get_search_service
from mcp_server.tools import MCPTools


def _make_tools():
    return MCPTools(get_search_service())


def test_search_notes_no_query():
    tools = _make_tools()
    result = tools.search_notes(user_id="u1", query="   ", top_k=5)
    assert result.results == []
    assert result.message == "Please provide a search query."


def test_search_notes_finds_uploaded_content(tmp_path):
    tools = _make_tools()

    f = tmp_path / "doc.txt"
    f.write_text("The mitochondria is the powerhouse of the cell.")
    process_document(str(f), user_id="u2", document_id="d1", filename="doc.txt")

    result = tools.search_notes(user_id="u2", query="mitochondria", top_k=3)
    assert len(result.results) > 0
    assert result.results[0].document_id == "d1"


def test_list_sources_and_get_document(tmp_path):
    tools = _make_tools()

    f = tmp_path / "bio.txt"
    f.write_text("Photosynthesis converts light energy into chemical energy.")
    process_document(str(f), user_id="u3", document_id="d2", filename="bio.txt")

    # Note: list_sources / get_document read from the app DB (Document table)
    # in the full app; this test exercises the search-layer retrieval that
    # get_document relies on for chunk content via get_document_chunks.
    from app.ingestion.processor import get_document_chunks
    chunks = get_document_chunks(user_id="u3", document_id="d2")
    assert len(chunks) > 0
    assert "photosynthesis" in chunks[0]["chunk_text"].lower()
