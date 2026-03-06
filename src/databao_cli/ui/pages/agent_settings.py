"""Agent Settings page - Executor and LLM configuration."""

from __future__ import annotations

import streamlit as st

from databao_cli.executor_utils import EXECUTOR_TYPES, LLM_PROVIDERS
from databao_cli.ui.app import _clear_all_chat_threads
from databao_cli.ui.components.status import AppStatus, set_status
from databao_cli.ui.models.settings import LLMProviderConfig, LLMSettings


def render_agent_settings_page() -> None:
    """Render the Agent Settings page."""
    st.title("Agent Settings")
    st.markdown("Configure the AI agent behavior and execution engine.")

    st.markdown("---")

    st.subheader("⚙️ Execution Engine")

    st.markdown(
        """
        The executor determines how queries are processed and executed against your data sources.
        """
    )

    current = st.session_state.get("executor_type", "lighthouse")

    selected = st.selectbox(
        "Executor type",
        options=list(EXECUTOR_TYPES.keys()),
        index=list(EXECUTOR_TYPES.keys()).index(current),
        format_func=lambda x: EXECUTOR_TYPES[x],
        help="Choose the execution engine for queries",
    )

    if selected == "lighthouse":
        st.info(
            """
            **LighthouseExecutor** is the default and recommended executor.
            It uses a sophisticated graph-based approach with planning and validation steps.
            Best for complex queries requiring multiple steps.
            """,
            icon="💡",
        )
    elif selected == "react_duckdb":
        st.warning(
            """
            **ReactDuckDBExecutor** is experimental.
            It uses a ReAct-style loop optimized for DuckDB queries.
            May be faster for simple queries but less reliable for complex ones.
            """,
            icon="⚠️",
        )
    elif selected == "dbt":
        st.warning(
            """
            **DbtProjectExecutor** is experimental.
            It relies on initialized dbt project and a connected warehouse.
            Should be used in case you need to automate dbt project changes.
            """,
            icon="⚠️",
        )

    if selected != current and st.button("✓ Apply Changes", type="primary", key="apply_executor"):
        st.session_state.executor_type = selected
        st.session_state.agent = None
        _clear_all_chat_threads()
        set_status(AppStatus.INITIALIZING, "Applying executor change...")
        st.success(f"Executor changed to {EXECUTOR_TYPES[selected]}")
        st.rerun()

    st.markdown("---")

    st.subheader("🤖 Language Model")

    st.markdown("Choose the LLM provider and configure its credentials.")

    llm: LLMSettings = st.session_state.get("llm_settings", LLMSettings())

    provider_keys = list(LLM_PROVIDERS.keys())
    current_provider = llm.active_provider if llm.active_provider in provider_keys else "openai"

    chosen_provider = st.selectbox(
        "Provider",
        options=provider_keys,
        index=provider_keys.index(current_provider),
        format_func=lambda x: LLM_PROVIDERS[x],
        help="The LLM provider the agent will use",
    )

    existing = llm.providers.get(chosen_provider, LLMProviderConfig())

    api_key = ""
    if chosen_provider not in ("ollama",):
        api_key = st.text_input(
            "API key",
            value=existing.api_key,
            type="password",
            help="Stored locally, sent only to the provider",
        )

    base_url = ""
    if chosen_provider == "openai_compat":
        base_url = st.text_input(
            "Base URL",
            value=existing.base_url,
            placeholder="http://localhost:8000/v1",
            help="The base URL of your OpenAI-compatible API server",
        )
    elif chosen_provider == "ollama":
        base_url = st.text_input(
            "Ollama host",
            value=existing.base_url or "http://localhost:11434",
            help="Ollama server URL (leave default for local)",
        )

    model = st.text_input(
        "Model",
        value=existing.model,
        placeholder=_model_placeholder(chosen_provider),
        help="The specific model identifier",
    )

    new_cfg = LLMProviderConfig(api_key=api_key, model=model, base_url=base_url)
    new_providers = dict(llm.providers)
    new_providers[chosen_provider] = new_cfg
    new_llm = LLMSettings(active_provider=chosen_provider, providers=new_providers)

    changed = (new_llm.active_provider != llm.active_provider) or (new_cfg != existing)

    if changed and st.button("✓ Apply Changes", type="primary", key="apply_llm"):
        errors = _validate_provider(chosen_provider, new_cfg)
        if errors:
            for err in errors:
                st.error(err)
        else:
            st.session_state.llm_settings = new_llm
            st.session_state.agent = None
            _clear_all_chat_threads()
            set_status(AppStatus.INITIALIZING, "Applying LLM change...")
            st.success(f"LLM provider changed to {LLM_PROVIDERS[chosen_provider]}")
            st.rerun()


def _validate_provider(provider_type: str, cfg: LLMProviderConfig) -> list[str]:
    """Return a list of validation error messages (empty if valid)."""
    errors: list[str] = []

    if not cfg.model:
        errors.append("**Model** is required.")

    if provider_type in ("openai", "anthropic", "openai_compat") and not cfg.api_key:
        errors.append("**API key** is required for this provider.")

    if provider_type == "openai_compat" and not cfg.base_url:
        errors.append("**Base URL** is required for an OpenAI-compatible provider.")

    return errors


def _model_placeholder(provider_type: str) -> str:
    """Return a helpful placeholder for the model input based on provider type."""
    placeholders: dict[str, str] = {
        "openai": "gpt-5-mini",
        "anthropic": "claude-sonnet-4-20250514",
        "ollama": "qwen3:8b",
        "openai_compat": "model-name-on-server",
    }
    return placeholders.get(provider_type, "model-name")
