from __future__ import annotations
from functools import lru_cache
from typing import Any
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # ── App ──────────────────────────────────────────────────────────────────
    app_env: str = "development"
    app_secret_key: str = "change-me"
    cors_allowed_origins: str = ""
    log_level: str = "INFO"

    # ── Database / Cache ──────────────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/pay_orchestrator"
    redis_url: str = "redis://localhost:6379"

    # ── Azure OpenAI ──────────────────────────────────────────────────────────
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment: str = "gpt-4.1-mini"
    azure_openai_embedding_deployment: str = "text-embedding-3-small"
    azure_openai_api_version: str = "2025-01-01-preview"

    # ── Azure Key Vault ───────────────────────────────────────────────────────
    azure_keyvault_url: str = ""
    azure_openai_api_key_kv_uri: str = ""

    # ── EntraID ───────────────────────────────────────────────────────────────
    azure_tenant_id: str = ""
    azure_client_id: str = ""
    entra_authority: str = "https://login.microsoftonline.com/"
    entra_audience: str = ""

    # ── Temporal ─────────────────────────────────────────────────────────────
    temporal_host: str = "localhost:7233"
    temporal_namespace: str = "pay_orchestrator"
    temporal_task_queue_payments: str = "payment-processing"

    # ── Compliance / Screening ────────────────────────────────────────────────
    aml_provider_url: str = ""
    aml_api_key: str = ""
    sanctions_provider_url: str = ""

    # ── FX / Data ─────────────────────────────────────────────────────────────
    fx_provider_url: str = ""
    fx_api_key: str = ""

    # ── Payment thresholds ────────────────────────────────────────────────────
    global_max_amount: float = 500_000.0
    high_corridor_max_amount: float = 250_000.0
    high_value_threshold: float = 100_000.0

    @field_validator("app_secret_key")
    @classmethod
    def _enforce_secret_key(cls, v: str, info: Any) -> str:
        if v == "change-me" and info.data.get("app_env") == "production":
            raise ValueError("APP_SECRET_KEY must be set in production.")
        return v

    @model_validator(mode="after")
    def _resolve_kv_secrets(self) -> "Settings":
        """Resolve Azure Key Vault URIs when running outside development."""
        if self.app_env == "development":
            return self
        if self.azure_openai_api_key_kv_uri and not self.azure_openai_api_key:
            try:
                from azure.keyvault.secrets import SecretClient
                from azure.identity import DefaultAzureCredential
                client = SecretClient(
                    vault_url=self.azure_keyvault_url,
                    credential=DefaultAzureCredential(),
                )
                uri = self.azure_openai_api_key_kv_uri
                secret_name = uri.split("/secrets/")[-1].split("/")[0]
                self.azure_openai_api_key = client.get_secret(secret_name).value or ""
            except Exception:
                pass
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
