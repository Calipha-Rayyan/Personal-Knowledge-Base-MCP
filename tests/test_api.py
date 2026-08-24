"""
Automated API tests. Uses an isolated in-memory SQLite DB and in-memory
Qdrant so tests don't touch real dev data.

Run from backend/:
    pytest tests/test_api.py -v
"""
import io
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["QDRANT_IN_MEMORY"] = "true"
os.environ["QDRANT_COLLECTION"] = "test_chunks"
os.environ["SEARCH_SCORE_THRESHOLD"] = "0.0"  # deterministic for tests

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db

# Shared in-memory SQLite engine (StaticPool keeps it alive across connections)
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


def register_and_login(username="alice", email="alice@example.com", password="pw123456"):
    client.post(
        "/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    resp = client.post("/auth/login", json={"email": email, "password": password})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ---------- Authentication ----------

def test_register_and_login():
    resp = client.post(
        "/auth/register",
        json={"username": "bob", "email": "bob@example.com", "password": "secret123"},
    )
    assert resp.status_code == 200
    resp = client.post(
        "/auth/login", json={"email": "bob@example.com", "password": "secret123"}
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_invalid_credentials():
    resp = client.post(
        "/auth/login", json={"email": "nobody@example.com", "password": "wrong"}
    )
    assert resp.status_code == 401


# ---------- Documents ----------

def test_upload_unsupported_file_type():
    headers = register_and_login("carol", "carol@example.com")
    resp = client.post(
        "/documents/upload",
        headers=headers,
        files={"file": ("malware.exe", io.BytesIO(b"data"), "application/octet-stream")},
    )
    assert resp.status_code == 400


def test_upload_list_get_delete_document():
    headers = register_and_login("dave", "dave@example.com")

    content = b"The sky is blue.\n\nMango is the best fruit in the world."
    resp = client.post(
        "/documents/upload",
        headers=headers,
        files={"file": ("notes.txt", io.BytesIO(content), "text/plain")},
    )
    assert resp.status_code == 201
    doc_id = resp.json()["document_id"]

    resp = client.get("/documents", headers=headers)
    assert resp.status_code == 200
    assert any(d["document_id"] == doc_id for d in resp.json())

    resp = client.get(f"/documents/{doc_id}", headers=headers)
    assert resp.status_code == 200
    assert "mango" in resp.json()["content"].lower()

    resp = client.delete(f"/documents/{doc_id}", headers=headers)
    assert resp.status_code == 200

    resp = client.get(f"/documents/{doc_id}", headers=headers)
    assert resp.status_code == 404


# ---------- Search ----------

def test_search_empty_query_rejected():
    headers = register_and_login("erin", "erin@example.com")
    resp = client.post("/search", headers=headers, json={"query": "   "})
    assert resp.status_code == 400


def test_search_returns_relevant_result():
    headers = register_and_login("frank", "frank@example.com")
    content = b"Random Forest is an ensemble learning algorithm used in machine learning."
    client.post(
        "/documents/upload",
        headers=headers,
        files={"file": ("ml_notes.txt", io.BytesIO(content), "text/plain")},
    )
    resp = client.post("/search", headers=headers, json={"query": "Random Forest", "top_k": 3})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["results"]) > 0
    assert "forest" in body["results"][0]["chunk_text"].lower()


def test_search_no_match_returns_graceful_message():
    headers = register_and_login("gina", "gina@example.com")
    resp = client.post(
        "/search", headers=headers, json={"query": "xyzzy nonexistent topic 12345"}
    )
    assert resp.status_code == 200
    # With no documents uploaded for this user, there should be no results.
    assert resp.json()["results"] == []


# ---------- Multi-user isolation ----------

def test_user_isolation_documents_and_search():
    headers_a = register_and_login("userA", "usera@example.com")
    headers_b = register_and_login("userB", "userb@example.com")

    content = b"UserA secret project notes about quantum computing."
    resp = client.post(
        "/documents/upload",
        headers=headers_a,
        files={"file": ("secret.txt", io.BytesIO(content), "text/plain")},
    )
    doc_id = resp.json()["document_id"]

    # User B must not see User A's document in their list.
    resp = client.get("/documents", headers=headers_b)
    assert all(d["document_id"] != doc_id for d in resp.json())

    # User B must not be able to fetch User A's document directly.
    resp = client.get(f"/documents/{doc_id}", headers=headers_b)
    assert resp.status_code == 404

    # User B's search must never surface User A's content.
    resp = client.post(
        "/search", headers=headers_b, json={"query": "quantum computing", "top_k": 5}
    )
    assert resp.status_code == 200
    assert all(r["document_id"] != doc_id for r in resp.json()["results"])
