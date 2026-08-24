\# Submission Status — Member 4 (Huzaifa Haider Khan)



\*\*Role:\*\* Frontend + Testing + Evaluation + Documentation

\*\*Branch:\*\* `feature/frontend`

\*\*Date:\*\* August 24, 2026



\## Summary

All assigned deliverables for Member 4 are complete. The frontend is fully

built, styled, and functions as a real, working, end-to-end application via

a mock API service layer — built specifically because Member 3's backend

API endpoints (auth, document upload/list, search) are not yet available in

the repository as of this submission.



\## Completed Deliverables



\### 1. Frontend — all 6 required pages (`frontend/`)

\- \*\*Login\*\* — functional email/password form

\- \*\*Dashboard\*\* — navigation cards to Upload / My Documents / Search

\- \*\*Upload Documents\*\* — real file upload flow with loading/success/error states

\- \*\*My Documents\*\* — fetches and displays uploaded documents, with loading/empty states

\- \*\*Search\*\* — query input, navigates to results

\- \*\*Search Results\*\* — fetches and displays results for the query, with loading/empty states



Shared design system in `frontend/src/styles/theme.css` (consistent

typography, color tokens, and layout across all pages).



\### 2. Mock API service layer (`frontend/src/services/api.js`)

Since Member 3's backend endpoints (`POST /documents/upload`, `GET /documents`,

`POST /search`, `GET /documents/{id}`) do not yet exist in the repository

(verified via `git ls-tree` on `feature/backend-auth` and `dev` — no

`backend/app/api/`, `backend/app/core/`, or `backend/app/models/` present),

a mock service layer was built that:

\- Matches the exact function names/signatures the real backend will need

\- Persists uploaded documents via `localStorage` so the app is genuinely

&#x20; demoable end-to-end (upload a file → see it in My Documents → search finds it)

\- Simulates realistic network delay



\*\*Integration plan:\*\* once Member 3's endpoints are live, each mock function

body in `api.js` will be replaced with a real `fetch()` call. No page code

will need to change, since the function signatures already match the

intended contract.



\### 3. Integration test plan (`evaluation/INTEGRATION\_TESTS.md`)

Full test plan covering authentication, upload, document listing, search,

multi-user isolation, MCP connection, and edge cases. Ready to execute once

the real backend is available.



\### 4. Evaluation setup (`evaluation/test\_queries.json`, `evaluation/evaluation\_results.md`)

5 hand-labeled test queries written against a real, student-owned document

(`Zeppelin AI-GenAI Fellowship — Personal Knowledge Base MCP Server - Team

Project Plan.docx`) — 4 relevant queries and 1 negative control. Results are

marked PENDING, since real retrieval precision cannot be honestly computed

until search runs against the real backend and Qdrant, not the mock layer.



\## Blocked / Pending (not part of Member 4's scope)

\- Member 3's backend/auth API (`backend/app/api/`, `backend/app/core/`,

&#x20; `backend/app/models/`) has not been pushed to the repository as of this

&#x20; submission. Verified by inspecting both `feature/backend-auth` and `dev`.

\- Real API integration, real auth logic, and real retrieval precision numbers

&#x20; are blocked on this and will be completed as soon as those endpoints land.



\## Commit History

All work is committed and pushed to `feature/frontend` under the correct

GitHub identity (Huzaifa Haider Khan / huzaifa.haider19@gmail.com), following

the team's `feat:`/`test:` commit convention.

