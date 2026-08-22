from fastapi import FastAPI

from app.api.auth import router as auth_router


app = FastAPI(
    title="Personal Knowledge Base API",
    version="1.0.0",
    description="Backend API for Personal Knowledge Base MCP",
)


app.include_router(auth_router)


@app.get("/")
def root():
    return {
        "message": "Personal Knowledge Base API is running"
    }