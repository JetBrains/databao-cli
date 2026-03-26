"""Fetch available models from LLM providers."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def fetch_models(provider_type: str, api_key: str, base_url: str = "") -> list[str] | None:
    """Fetch available model IDs from a provider.

    Returns a sorted list of model names, or None if the provider
    doesn't support listing models (e.g. Anthropic).

    Raises on connection / auth errors so the caller can display them.
    """
    if provider_type == "openai":
        return _fetch_openai_models(api_key)
    if provider_type == "openai_compat":
        return _fetch_openai_models(api_key, base_url=base_url)
    if provider_type == "ollama":
        return _fetch_ollama_models(base_url)
    if provider_type == "anthropic":
        return _fetch_anthropic_models(api_key)
    return None


def _fetch_openai_models(api_key: str, base_url: str = "") -> list[str]:
    """List models via the OpenAI-compatible /v1/models endpoint."""
    import openai

    client = openai.OpenAI(api_key=api_key or None, base_url=base_url or None)
    response = client.models.list()

    chat_prefixes = ("gpt-", "o1", "o3", "o4", "chatgpt-")
    all_ids = sorted(m.id for m in response.data)

    if base_url:
        return all_ids

    filtered = [m for m in all_ids if any(m.startswith(p) for p in chat_prefixes)]
    return filtered or all_ids


def _fetch_ollama_models(base_url: str) -> list[str]:
    """List locally available models via Ollama's /api/tags endpoint."""
    import requests

    host = base_url or "http://localhost:11434"
    resp = requests.get(f"{host.rstrip('/')}/api/tags", timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return sorted(m["name"] for m in data.get("models", []))


def _fetch_anthropic_models(api_key: str) -> list[str]:
    """List available models via the Anthropic /v1/models endpoint."""
    import anthropic

    client = anthropic.Anthropic(api_key=api_key or None)
    response = client.models.list(limit=100)

    chat_prefixes = ("claude-",)
    all_ids = sorted(m.id for m in response.data)

    filtered = [m for m in all_ids if any(m.startswith(p) for p in chat_prefixes)]
    return filtered or all_ids


def pick_default_model(models: list[str], provider_type: str) -> str:
    """Pick the best default from a fetched model list."""
    from databao_cli.shared.executor_utils import LLM_PROVIDER_MODELS

    preferred = LLM_PROVIDER_MODELS.get(provider_type, [])

    for pref in preferred:
        if pref in models:
            return pref

    for pref in preferred:
        family = pref.split("-")[0]  # e.g. "gpt" from "gpt-5-mini"
        for m in models:
            if m.startswith(family):
                return m

    return models[0] if models else ""
