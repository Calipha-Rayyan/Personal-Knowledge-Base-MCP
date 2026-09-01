from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Personal Knowledge Base API"
    app_version: str = "1.0.0"

    database_url: str = "sqlite:///./knowledge_base.db"

    secret_key: str = "change-this-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    reset_token_expire_minutes: int = 30

    frontend_url: str = "http://localhost:5173"

    # Qdrant / vector search
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "document_chunks"
    qdrant_in_memory: bool = False
    # Qdrant Cloud (and any auth-protected Qdrant instance) requires an
    # API key and HTTPS. Left blank for local Docker Qdrant, which has
    # no auth by default.
    qdrant_api_key: str | None = None
    qdrant_use_https: bool = False

    embedding_model: str = "multi-qa-MiniLM-L6-cos-v1"

    search_score_threshold: float = 0.3
    search_top_k_default: int = 5
    search_top_k_max: int = 20

    upload_dir: str = "./uploads"
    allowed_extensions: tuple = (".pdf", ".txt", ".md", ".docx", ".ppt", ".pptx")
    max_upload_size_mb: int = 25

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()