\# Integration Test Plan — Personal Knowledge Base MCP Server



Owner: Huzaifa Haider Khan (Member 4)

Status: Draft — pending backend endpoints from Member 3



\## Purpose

Verify that frontend, backend API, Qdrant storage, and the MCP server work

correctly together as a full system, not just in isolation.



\## Test Environment

\- Frontend: React dev server (localhost:5173)

\- Backend: FastAPI dev server (URL TBD — pending Member 3)

\- Vector DB: Qdrant (managed by Member 2)

\- MCP Server: FastMCP (managed by Rayyan)



\## Test Cases



\### 1. Authentication

\- \[ ] User can register a new account

\- \[ ] User can log in with correct credentials

\- \[ ] Login fails gracefully with wrong credentials (clear error shown)

\- \[ ] Session/token persists across page reloads

\- \[ ] Logged-out user cannot access Dashboard/Upload/Documents/Search directly (redirect to Login)



\### 2. Document Upload

\- \[ ] Upload a valid PDF — succeeds, appears in My Documents

\- \[ ] Upload a valid TXT/MD/DOCX/PPT/PPTX — succeeds

\- \[ ] Upload an unsupported file type — rejected with clear error

\- \[ ] Upload with no file selected — blocked client-side (already verified in UI)

\- \[ ] Large file upload — check timeout/error handling



\### 3. My Documents

\- \[ ] Document list loads and matches what was actually uploaded

\- \[ ] Empty state displays correctly for a new user with no uploads

\- \[ ] Document list only shows the logged-in user's own documents (user isolation)



\### 4. Search

\- \[ ] Search with a query matching uploaded content returns relevant results

\- \[ ] Search with a query that matches nothing returns a graceful "no results" state

\- \[ ] Empty search query is blocked client-side (already verified in UI)

\- \[ ] Search results only pull from the logged-in user's own documents (user isolation)



\### 5. User Isolation (multi-user)

\- \[ ] User A cannot see User B's documents in My Documents

\- \[ ] User A's search never returns User B's document content

\- \[ ] Uploading as User A does not affect User B's document list



\### 6. MCP Connection

\- \[ ] MCP server successfully connects to an MCP-compatible client (e.g. Claude)

\- \[ ] search\_notes tool returns expected results via MCP

\- \[ ] get\_document tool retrieves correct document via MCP

\- \[ ] list\_sources tool lists the correct user's documents via MCP



\### 7. Edge Cases

\- \[ ] Wrong query language/format handled without crashing

\- \[ ] Special characters in search query handled correctly

\- \[ ] Duplicate file upload (same file twice) handled sensibly

\- \[ ] Network/API failure shows a user-friendly error, not a blank page



\## Notes

This plan will be executed once Member 3's API endpoints

(POST /documents/upload, GET /documents, POST /search, GET /documents/{id})

and Member 1's MCP tools are confirmed ready for integration.

