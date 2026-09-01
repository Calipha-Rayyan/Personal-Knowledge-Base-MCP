"""
Tests for Phase 4/5 document features: background processing status
transitions, pagination, and file-type filtering.

Run from backend/:
    pytest tests/test_documents_v2.py -v
"""
import io
import os
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["QDRANT_IN_MEMORY"] = "true"
os.environ["QDRANT_COLLECTION"] = "test_documents_v2_chunks"
os.environ["SEARCH_SCORE_THRESHOLD"] = "0.0"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def register_and_login(username, email, password="pw123456"):
    client.post("/auth/register", json={"username": username, "email": email, "password": password})
    resp = client.post("/auth/login", json={"email": email, "password": password})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def _wait_for_status(headers, document_id, target_statuses, timeout=15):
    deadline = time.time() + timeout
    while time.time() < deadline:
        resp = client.get("/documents", headers=headers, params={"limit": 100})
        doc = next((d for d in resp.json()["documents"] if d["document_id"] == document_id), None)
        if doc and doc["status"] in target_statuses:
            return doc
        time.sleep(0.2)
    raise AssertionError(f"Document did not reach status {target_statuses} within {timeout}s")


def test_upload_returns_immediately_in_uploading_status():
    headers = register_and_login("ivy", "ivy_v2@example.com")
    content = b"Some test content for background processing."
    resp = client.post(
        "/documents/upload",
        headers=headers,
        files={"file": ("notes.txt", io.BytesIO(content), "text/plain")},
    )
    assert resp.status_code == 201
    assert resp.json()["status"] == "uploading"


def test_document_eventually_reaches_indexed_status():
    headers = register_and_login("jack", "jack_v2@example.com")
    content = b"Background processing test document about machine learning."
    resp = client.post(
        "/documents/upload",
        headers=headers,
        files={"file": ("ml.txt", io.BytesIO(content), "text/plain")},
    )
    document_id = resp.json()["document_id"]

    doc = _wait_for_status(headers, document_id, ["indexed", "failed"])
    assert doc["status"] == "indexed"
    assert doc["chunk_count"] > 0


def test_pagination_response_shape():
    headers = register_and_login("kate", "kate_v2@example.com")
    resp = client.get("/documents", headers=headers, params={"limit": 5, "offset": 0})
    assert resp.status_code == 200
    body = resp.json()
    assert "total" in body
    assert "documents" in body
    assert body["limit"] == 5
    assert body["offset"] == 0


def test_file_type_filter():
    headers = register_and_login("liam", "liam_v2@example.com")

    resp1 = client.post(
        "/documents/upload",
        headers=headers,
        files={"file": ("a.txt", io.BytesIO(b"txt content about cooking"), "text/plain")},
    )
    doc_txt = resp1.json()["document_id"]
    _wait_for_status(headers, doc_txt, ["indexed", "failed"])

    resp = client.get("/documents", headers=headers, params={"file_type": "txt"})
    assert resp.status_code == 200
    body = resp.json()
    assert all(d["file_type"] == "txt" for d in body["documents"])
    assert any(d["document_id"] == doc_txt for d in body["documents"])