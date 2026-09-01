from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from app.api.auth import router as auth_router
from app.api.documents import router as documents_router
from app.api.search import router as search_router
from app.api.health import router as health_router
from app.core.rate_limit import limiter

from app.models import user, document, knowledge, refresh_token, password_reset_token  # noqa: F401


app = FastAPI(
    title="Personal Knowledge Base API",
    version="1.0.0",
    description="Backend API for Personal Knowledge Base MCP",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(search_router)


@app.get("/")
def root():
    return {"message": "Personal Knowledge Base API is running"}