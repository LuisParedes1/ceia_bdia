"""Explicit local-development settings for the trusted backend boundary."""

# pyright: reportMissingImports=false

from urllib.parse import urlparse

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


_LOCAL_HOSTS = {"localhost", "127.0.0.1", "db", "minio", "mailpit", "embeddings-api"}


class Settings(BaseSettings):
    """Allow-list target configuration; excluded product settings fail fast."""

    model_config = SettingsConfigDict(env_file=".env", extra="forbid")

    project_name: str = "Generic Student Project API"
    app_env: str = "development"
    api_public_url: str = "http://localhost:8000"
    web_public_url: str = "http://localhost:5173"
    landing_public_url: str = "http://localhost:4321"
    backend_cors_origins: list[str] = ["http://localhost:5173", "http://localhost:4321"]
    backend_trusted_hosts: list[str] = ["localhost", "127.0.0.1", "api"]

    runtime_database_url: str
    migrator_database_url: str
    assistant_database_url: str

    minio_endpoint: str = "minio:9000"
    minio_access_key: str
    minio_secret_key: str
    minio_bucket: str = "student-assets"
    smtp_host: str = "mailpit"
    smtp_port: int = 1025
    smtp_from: str

    session_secret: str
    session_ttl_minutes: int = Field(default=480, ge=1, le=10_080)
    recovery_token_secret: str
    recovery_token_ttl_minutes: int = Field(default=30, ge=1, le=120)
    recovery_requests_per_hour: int = Field(default=5, ge=1, le=100)
    max_upload_bytes: int = Field(default=25 * 1024 * 1024, ge=1, le=25 * 1024 * 1024)
    embedding_dimension: int = Field(default=384, ge=384, le=384)
    modelo_embedding: str = "intfloat/multilingual-e5-small"
    embeddings_api_url: str = "http://embeddings-api:8000"
    sql_statement_timeout_ms: int = Field(default=2_000, ge=100, le=30_000)
    sql_max_rows: int = Field(default=200, ge=1, le=200)
    sql_max_result_bytes: int = Field(default=256 * 1024, ge=1, le=256 * 1024)

    openrouter_api_key: str | None = None
    openrouter_model: str = "openai/gpt-4o-mini"

    @field_validator("api_public_url", "web_public_url", "landing_public_url", "embeddings_api_url")
    @classmethod
    def public_urls_are_local(cls, value: str) -> str:
        if urlparse(value).hostname not in _LOCAL_HOSTS:
            raise ValueError("public URLs must use a local development host")
        return value.rstrip("/")

    @field_validator("backend_cors_origins")
    @classmethod
    def cors_origins_are_local(cls, values: list[str]) -> list[str]:
        for value in values:
            if urlparse(value).hostname not in _LOCAL_HOSTS:
                raise ValueError("CORS origins must use a local development host")
        return [value.rstrip("/") for value in values]


settings = Settings()  # pyright: ignore[reportCallIssue] -- values are loaded from the environment
