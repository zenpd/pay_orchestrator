"""Central configuration — reads from .env via pydantic-settings.

Secrets that live in Azure Key Vault are declared as *_kv_uri fields.
The _resolve_kv_secrets validator fetches the real values at startup.
"""
from __future__ import annotations

from functools import lru_cache
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # ── App ──────────────────────────────────────────────────────────────────
    app_env: str = "development"
    app_secret_key: str = "change-me"
    log_level: str = "INFO"
    cors_allowed_origins: str = ""

    # ── Database / Cache ─────────────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/payment_orchestrator"
    redis_url: str = "redis://localhost:6379/0"

    # ── Azure OpenAI ─────────────────────────────────────────────────────────
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment: str = "gpt-4.1-mini"
    azure_openai_embedding_deployment: str = "text-embedding-3-small"
    azure_openai_api_version: str = "2025-01-01-preview"

    # ── Azure Key Vault ───────────────────────────────────────────────────────
    azure_keyvault_url: str = "https://zaf-kv-01.vault.azure.net/"
    azure_openai_endpoint_kv_uri: str = ""
    azure_openai_api_key_kv_uri: str = ""
    azure_openai_deployment_kv_uri: str = ""
    database_url_kv_uri: str = ""
    redis_url_kv_uri: str = ""

    # ── Azure / EntraID ───────────────────────────────────────────────────────
    azure_tenant_id: str = ""
    azure_client_id: str = ""
    azure_client_secret: str = ""
    entra_authority: str = "https://login.microsoftonline.com/"
    entra_audience: str = ""

    # ── Temporal Workflow Engine ──────────────────────────────────────────────
    # Whether to enable Temporal workflows for payment orchestration
    temporal_enabled: bool = False
    temporal_host: str = "localhost"
    temporal_port: int = 7233
    temporal_namespace: str = "payment-orchestrator"
    temporal_task_queue: str = "payment.processing"

    # ── Arize Phoenix Observability ───────────────────────────────────────────
    phoenix_admin_email: str = "admin@localhost"
    phoenix_admin_password: str = ""
    arize_phoenix_api_key: str = ""
    phoenix_admin_secret: str = ""
    phoenix_db_connection_string: str = ""
    phoenix_postgres_host: str = ""
    phoenix_postgres_user: str = ""
    phoenix_postgres_password: str = ""
    phoenix_host: str = "localhost"
    phoenix_port: int = 6006
    phoenix_collector_endpoint: str = ""
    phoenix_project_name: str = "payment-orchestration"

    # KV URIs for Phoenix / Arize
    arize_phoenix_api_key_kv_uri: str = ""
    arize_phoenix_password_kv_uri: str = ""
    phoenix_admin_secret_kv_uri: str = ""
    phoenix_db_connection_string_kv_uri: str = ""
    phoenix_postgres_host_kv_uri: str = ""
    phoenix_postgres_user_kv_uri: str = ""
    phoenix_postgres_password_kv_uri: str = ""

    # ── Vector DBs ────────────────────────────────────────────────────────────
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""

    # ── Payment Processing ────────────────────────────────────────────────────
    # External payment rail service credentials (if not using mock)
    payment_rails_api_key: str = ""
    payment_rails_api_url: str = "http://localhost:8080"
    payment_rails_timeout_seconds: int = 30

    @model_validator(mode="after")
    def _resolve_kv_secrets(self) -> Settings:
        """Placeholder for Key Vault secret resolution.
        
        In production, this would fetch secrets from Azure Key Vault
        using the *_kv_uri fields and populate the corresponding plain fields.
        """
        # TODO: Implement Azure Key Vault integration if needed
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
