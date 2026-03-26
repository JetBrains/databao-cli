"""Shared executor type definitions."""

from databao.agent.configs.llm import LLMConfig

EXECUTOR_TYPES = {
    "claude_code": "ClaudeCodeExecutor (recommended)",
    "lighthouse": "LighthouseExecutor",
    "react_duckdb": "ReactDuckDBExecutor (experimental)",
    "dbt": "DbtProjectExecutor (experimental)",
}

LLM_PROVIDERS: dict[str, str] = {
    "openai": "OpenAI",
    "anthropic": "Anthropic",
    "ollama": "Ollama (local)",
    "openai_compat": "OpenAI-compatible API (vLLM, LM Studio, etc.)",
}

LLM_PROVIDER_MODELS: dict[str, list[str]] = {
    "openai": [
        "gpt-5.4",
        "gpt-5.3-codex",
        "gpt-5.2",
        "gpt-5.2-codex",
        "gpt-5-mini",
    ],
    "anthropic": [
        "claude-sonnet-4-6",
        "claude-opus-4-6",
        "claude-haiku-4-6",
    ],
    "ollama": [
        "qwen3.5:8b",
        "qwen3:8b",
    ],
    "openai_compat": [],
}


def build_llm_config(
    model: str,
    *,
    provider: str = "",
    temperature: float = 0.0,
    base_url: str = "",
) -> LLMConfig:
    """Build an LLMConfig with correct provider prefix and provider-specific options.

    Handles:
    - Prefixing Ollama model names with ``ollama:`` so LangChain routes correctly.
    - Setting ``api_base_url`` for OpenAI-compatible endpoints.
    - Disabling ``ollama_pull_model`` (the UI already verifies model availability).
    """

    name = model
    kwargs: dict[str, object] = {}

    if provider == "ollama":
        if not name.startswith("ollama:"):
            name = f"ollama:{name}"
        kwargs["ollama_pull_model"] = False

    if provider == "openai_compat" and base_url:
        kwargs["api_base_url"] = base_url

    return LLMConfig(name=name, temperature=temperature, **kwargs)
