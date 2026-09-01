"""
Tests for Phase 2b/2c/3 auth features: refresh tokens, logout,
forgot/reset/change password, rate limiting, and specific login
error messages.

Run from backend/:
    pytest tests/test_auth_v2.py -v
"""
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["QDRANT_IN_MEMORY"] = "true"
os.environ["QDRANT_COLLECTION"] = "test_auth_v2_chunks"

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
    return resp.json()


# ---------- Refresh tokens ----------

def test_login_returns_both_tokens():
    data = register_and_login("alice", "alice_v2@example.com")
    assert "access_token" in data
    assert "refresh_token" in data


def test_refresh_issues_new_tokens_and_revokes_old():
    data = register_and_login("bob", "bob_v2@example.com")
    old_refresh = data["refresh_token"]

    resp = client.post("/auth/refresh", json={"refresh_token": old_refresh})
    assert resp.status_code == 200
    new_data = resp.json()
    assert new_data["refresh_token"] != old_refresh

    # Old refresh token should now be revoked (rotation).
    resp2 = client.post("/auth/refresh", json={"refresh_token": old_refresh})
    assert resp2.status_code == 401


def test_invalid_refresh_token_rejected():
    resp = client.post("/auth/refresh", json={"refresh_token": "not-a-real-token"})
    assert resp.status_code == 401


def test_logout_revokes_refresh_token():
    data = register_and_login("carol", "carol_v2@example.com")
    refresh_token = data["refresh_token"]

    resp = client.post("/auth/logout", json={"refresh_token": refresh_token})
    assert resp.status_code == 200

    resp2 = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert resp2.status_code == 401


# ---------- Login error messages (specific, not generic) ----------

def test_login_unknown_email_returns_specific_message():
    resp = client.post(
        "/auth/login", json={"email": "totally_unknown_v2@example.com", "password": "whatever123"}
    )
    assert resp.status_code == 401
    assert "No account found" in resp.json()["detail"]


def test_login_wrong_password_returns_specific_message():
    register_and_login("mia", "mia_v2@example.com")
    resp = client.post("/auth/login", json={"email": "mia_v2@example.com", "password": "wrongpassword"})
    assert resp.status_code == 401
    assert "Incorrect password" in resp.json()["detail"]


# ---------- Forgot / reset password ----------

def test_forgot_password_unknown_email_returns_404():
    resp = client.post("/auth/forgot-password", json={"email": "nobody_v2@example.com"})
    assert resp.status_code == 404
    assert "No account found" in resp.json()["detail"]


def test_forgot_password_known_email_returns_link():
    register_and_login("dave", "dave_v2@example.com")
    resp = client.post("/auth/forgot-password", json={"email": "dave_v2@example.com"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["reset_link"] is not None
    assert "token=" in body["reset_link"]


def test_reset_password_with_valid_token_changes_password():
    register_and_login("erin", "erin_v2@example.com")
    resp = client.post("/auth/forgot-password", json={"email": "erin_v2@example.com"})
    reset_link = resp.json()["reset_link"]
    token = reset_link.split("token=")[1]

    resp2 = client.post("/auth/reset-password", json={"token": token, "new_password": "newpass123"})
    assert resp2.status_code == 200

    # Old password should no longer work.
    resp3 = client.post("/auth/login", json={"email": "erin_v2@example.com", "password": "pw123456"})
    assert resp3.status_code == 401
    assert "Incorrect password" in resp3.json()["detail"]

    # New password should work.
    resp4 = client.post("/auth/login", json={"email": "erin_v2@example.com", "password": "newpass123"})
    assert resp4.status_code == 200


def test_reset_password_token_is_single_use():
    register_and_login("frank", "frank_v2@example.com")
    resp = client.post("/auth/forgot-password", json={"email": "frank_v2@example.com"})
    token = resp.json()["reset_link"].split("token=")[1]

    resp1 = client.post("/auth/reset-password", json={"token": token, "new_password": "firstnew123"})
    assert resp1.status_code == 200

    resp2 = client.post("/auth/reset-password", json={"token": token, "new_password": "secondnew123"})
    assert resp2.status_code == 400


def test_reset_password_invalid_token_rejected():
    resp = client.post("/auth/reset-password", json={"token": "bogus", "new_password": "whatever123"})
    assert resp.status_code == 400


# ---------- Change password ----------

def test_change_password_wrong_current_password_rejected():
    data = register_and_login("gina", "gina_v2@example.com")
    headers = {"Authorization": f"Bearer {data['access_token']}"}

    resp = client.post(
        "/auth/change-password",
        headers=headers,
        json={"current_password": "wrongpass", "new_password": "newpass123"},
    )
    assert resp.status_code == 400


def test_change_password_success_and_revokes_sessions():
    data = register_and_login("henry", "henry_v2@example.com")
    headers = {"Authorization": f"Bearer {data['access_token']}"}
    refresh_token = data["refresh_token"]

    resp = client.post(
        "/auth/change-password",
        headers=headers,
        json={"current_password": "pw123456", "new_password": "brandnew123"},
    )
    assert resp.status_code == 200

    # Refresh token from before the change should now be revoked.
    resp2 = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert resp2.status_code == 401

    # New password logs in fine.
    resp3 = client.post("/auth/login", json={"email": "henry_v2@example.com", "password": "brandnew123"})
    assert resp3.status_code == 200


# ---------- Register error messages ----------

def test_register_duplicate_username_specific_message():
    client.post("/auth/register", json={"username": "dupuser", "email": "dup1_v2@example.com", "password": "pw123456"})
    resp = client.post("/auth/register", json={"username": "dupuser", "email": "dup2_v2@example.com", "password": "pw123456"})
    assert resp.status_code == 400
    assert "username" in resp.json()["detail"].lower()


def test_register_duplicate_email_specific_message():
    client.post("/auth/register", json={"username": "user1_v2", "email": "dupemail_v2@example.com", "password": "pw123456"})
    resp = client.post("/auth/register", json={"username": "user2_v2", "email": "dupemail_v2@example.com", "password": "pw123456"})
    assert resp.status_code == 400
    assert "email" in resp.json()["detail"].lower()