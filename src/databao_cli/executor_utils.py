"""Shared executor type definitions."""

EXECUTOR_TYPES = {
    "lighthouse": "LighthouseExecutor (recommended)",
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
        "o3-mini",
    ],
    "anthropic": [
        "claude-sonnet-4-6-20250217",
        "claude-opus-4-6-20250205",
        "claude-sonnet-4-20250514",
        "claude-haiku-4-20250414",
    ],
    "ollama": [
        "qwen3-coder:30b",
        "devstral:24b",
        "qwen3.5:8b",
        "qwen3.5:32b",
        "qwen3:8b",
        "qwen3:14b",
        "deepseek-r1:8b",
    ],
    "openai_compat": [],
}
