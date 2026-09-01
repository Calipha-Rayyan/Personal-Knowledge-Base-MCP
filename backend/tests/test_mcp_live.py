"""
Live MCP tool check — calls search_notes, get_document, and list_sources
directly (not through the MCP transport) using your REAL uploaded data
and REAL Qdrant server, so you can see actual output before wiring up
a real MCP client.

IMPORTANT: run this from the backend/ folder (same folder you run
uvicorn from), NOT from the project root. The database path in
config.py is relative ("./knowledge_base.db"), so running from the
wrong folder silently creates a new empty database instead of using
your real one.

Run from backend/:
    cd D:\\Personal-Knowledge-Base-MCP\\Personal-Knowledge-Base-MCP\\backend
    .venv\\Scripts\\activate
    python tests\\test_mcp_live.py <user_id>

To find your user_id: log into the app, open http://localhost:8000/docs,
authorize with your token (from DevTools > Application > Local Storage >
pkb_access_token), then call GET /auth/me — the response has "id".
"""
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import all models before querying the database, so SQLAlchemy can
# resolve the "User" string reference inside Document's relationship().
from app.models import user, document, knowledge  # noqa: F401

from app.services.search_service import get_search_service
from mcp_server.tools import MCPTools


def main():
    if len(sys.argv) < 2:
        print("Usage: python tests/test_mcp_live.py <user_id>")
        print("(Find your user_id via GET /auth/me while logged in)")
        return

    user_id = sys.argv[1]
    tools = MCPTools(get_search_service())

    print("=" * 60)
    print("1. list_sources()")
    print("=" * 60)
    sources = tools.list_sources(user_id=user_id)
    if not sources.sources:
        print("No documents found for this user_id. Upload a document first,")
        print("and make sure you passed the correct user_id.")
        return
    for s in sources.sources:
        print(f"  - {s.filename}  (document_id={s.document_id})")

    first_doc_id = sources.sources[0].document_id

    print("\n" + "=" * 60)
    print("2. search_notes(query='semantic search', top_k=3)")
    print("=" * 60)
    result = tools.search_notes(user_id=user_id, query="semantic search", top_k=3)
    if result.message:
        print(f"  Message: {result.message}")
    for r in result.results:
        print(f"  - [{r.score:.2f}] {r.filename}: {r.chunk_text[:80]}...")

    print("\n" + "=" * 60)
    print(f"3. get_document(doc_id='{first_doc_id}')")
    print("=" * 60)
    doc = tools.get_document(user_id=user_id, doc_id=first_doc_id)
    print(f"  Filename: {doc.filename}")
    print(f"  Content length: {len(doc.content)} chars")
    print(f"  Preview: {doc.content[:150]}...")

    print("\n" + "=" * 60)
    print("ALL 3 MCP TOOLS EXECUTED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    main()