from __future__ import annotations
from langchain_openai import AzureChatOpenAI
from shared.config import get_settings


def get_llm(max_tokens: int = 512) -> AzureChatOpenAI:
    """Return a configured AzureChatOpenAI instance."""
    settings = get_settings()
    endpoint = settings.azure_openai_endpoint.removesuffix("/openai")
    return AzureChatOpenAI(
        azure_endpoint=endpoint,
        api_key=settings.azure_openai_api_key,
        azure_deployment=settings.azure_openai_deployment,
        api_version=settings.azure_openai_api_version,
        max_tokens=max_tokens,
        temperature=0,
    )
