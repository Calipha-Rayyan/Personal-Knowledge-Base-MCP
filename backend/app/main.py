from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.documents import router as documents_router
from app.api.search import router as search_router
from app.core.database import Base, engine

# Import models so SQLAlchemy metadata knows about them before create_all.
from app.models import user, knowledge, document  # noqa: F401


app = FastAPI(
    title="Personal Knowledge Base API",
    version="1.0.0",
    description="Backend API for Personal Knowledge Base MCP",
)

# NOTE: with the Vite dev proxy in place (see frontend/vite.config.js),
# the browser talks only to localhost:5173 and this CORS config is not
# actually exercised for local dev. It's kept as a safety net for anyone
# who calls the API directly (e.g. curl, Postman, or a future deployment
# where frontend and backend are on different origins).
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(search_router)


@app.get("/")
def root():
    return {
        "message": "Personal Knowledge Base API is running"
    }