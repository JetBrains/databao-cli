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
