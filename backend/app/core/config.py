from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Personal Knowledge Base API"
    app_version: str = "1.0.0"

    database_url: str = "sqlite:///./knowledge_base.db"

    secret_key: str = "change-this-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Qdrant / vector search
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "document_chunks"
    qdrant_in_memory: bool = False  # set False once a real Qdrant server is running

    # Embeddings
    embedding_model: str = "all-MiniLM-L6-v2"

    # Search
    search_score_threshold: float = 0.3
    search_top_k_default: int = 5
    search_top_k_max: int = 20

    # Uploads
    upload_dir: str = "./uploads"
    allowed_extensions: tuple = (".pdf", ".txt", ".md", ".docx", ".ppt", ".pptx")
    max_upload_size_mb: int = 25

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
