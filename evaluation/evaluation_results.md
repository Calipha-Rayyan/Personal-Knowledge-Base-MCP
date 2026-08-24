# Retrieval Evaluation Results — Personal Knowledge Base MCP Server

Owner: Huzaifa Haider Khan (Member 4)
Status: Test queries defined against a real document; awaiting Member 3's
real /search endpoint to compute actual precision.

## Methodology
1. Upload a real, student-owned document corpus (own notes/assignments/papers).
2. Hand-label a set of test queries in `test_queries.json`, each mapped to the
   document(s) it should retrieve.
3. Run each query against the real `/search` endpoint.
4. Record whether the top-ranked result(s) match the expected document.
5. Compute retrieval precision: (relevant results retrieved) / (total results retrieved).

## Document Corpus Used
- `Zeppelin AI-GenAI Fellowship — Personal Knowledge Base MCP Server - Team Project Plan.docx`
  (real, student-owned project document; uploaded and verified working via the
  mock service layer in `frontend/src/services/api.js`)

## Test Queries
See `test_queries.json` for the 5 hand-labeled queries (4 relevant, 1 negative
control), each based on real content from the document above.

## Results

| Query ID | Query | Expected Document | Retrieved? | Correct? |
|----------|-------|--------------------|------------|----------|
| q1       | What are the three MCP tools our server exposes? | Team Project Plan.docx | PENDING — mock search only | PENDING |
| q2       | Is this project a chatbot or an autonomous AI agent? | Team Project Plan.docx | PENDING — mock search only | PENDING |
| q3       | What vector database does the project use for storage? | Team Project Plan.docx | PENDING — mock search only | PENDING |
| q4       | How does the system know what a search question means, not just keywords? | Team Project Plan.docx | PENDING — mock search only | PENDING |
| q5       | What is the weather forecast for tomorrow? (negative control) | None expected | PENDING — mock search only | PENDING |

## Precision Summary
- Total queries tested: 5 (defined, not yet run against real search)
- Correct retrievals: N/A — blocked on Member 3's real /search endpoint
- Precision: N/A

## Observations
Search is currently served by a mock service layer (`frontend/src/services/api.js`)
that returns a generic snippet for every uploaded document regardless of query,
so it cannot yet be meaningfully scored for precision. This file and
`test_queries.json` are ready to go the moment the real `/search` endpoint
(semantic search over Qdrant) is available — this table will be filled in with
actual retrieved results and a real precision score at that point.