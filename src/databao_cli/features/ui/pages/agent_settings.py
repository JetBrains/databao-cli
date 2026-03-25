"""Agent settings page - Executor and LLM configuration."""

from __future__ import annotations

import os

import streamlit as st

from databao_cli.features.ui.app import _clear_all_chat_threads
from databao_cli.features.ui.components.status import AppStatus, set_status
from databao_cli.features.ui.models.settings import _ENV_VAR_MAP, LLMProviderConfig, LLMSettings
from databao_cli.shared.executor_utils import EXECUTOR_TYPES, LLM_PROVIDER_MODELS, LLM_PROVIDERS


def render_agent_settings_page(*, auto_apply: bool = False) -> None:
    """Render the Agent settings page."""
    if not auto_apply:
        st.title("Agent settings")
        st.markdown("Configure the AI agent behavior and execution engine.")
        st.markdown("---")

    st.subheader("⚙️ Execution engine")

    st.markdown(
        """
        The executor determines how queries are processed and executed against your data sources.
        """
    )

    current = st.session_state.get("executor_type", "claude_code")

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
            **LighthouseExecutor** uses a sophisticated graph-based approach with planning and validation steps.
            Best for complex queries requiring multiple steps.
            """,
            icon="ℹ️",
        )
    elif selected == "react_duckdb":
        st.info(
            """
            **ReactDuckDBExecutor** is experimental.
            It uses a ReAct-style loop optimized for DuckDB queries.
            May be faster for simple queries but less reliable for complex ones.
            """,
            icon="ℹ️",
        )
    elif selected == "dbt":
        st.info(
            """
            **DbtProjectExecutor** is experimental.
            It relies on initialized dbt project and a connected warehouse.
            Should be used in case you need to automate dbt project changes.
            """,
            icon="ℹ️",
        )
    elif selected == "claude_code":
        st.info(
            """
            **ClaudeCodeExecutor** is the default and recommended executor.
            It uses Claude Code as the execution backend for queries.
            Requires a valid Anthropic API key configured in the LLM settings.
            """,
            icon="💡",
        )

    if selected != current:
        if auto_apply:
            # Always sync — even if user kept the default executor.
            st.session_state.executor_type = selected
        elif selected != current and st.button("✓ Apply Changes", type="primary", key="apply_executor"):
            st.session_state.executor_type = selected
            st.session_state.agent = None
            _clear_all_chat_threads()
            set_status(AppStatus.INITIALIZING, "Applying executor change...")
            st.success(f"Executor changed to {EXECUTOR_TYPES[selected]}")
            st.rerun()

    st.markdown("---")

    st.subheader("🤖 Language model")

    st.markdown("Choose an LLM provider and configure its credentials.")

    llm: LLMSettings = st.session_state.get("llm_settings", LLMSettings())

    provider_keys = list(LLM_PROVIDERS.keys())
    current_provider = llm.active_provider if llm.active_provider in provider_keys else "openai"

    is_claude_code = st.session_state.get("executor_type", "claude_code") == "claude_code"

    if is_claude_code:
        chosen_provider = "anthropic"
        st.selectbox(
            "Provider",
            options=["anthropic"],
            index=0,
            format_func=lambda x: LLM_PROVIDERS[x],
            help="ClaudeCodeExecutor requires the Anthropic provider",
            disabled=True,
        )
        st.caption("🔒 Provider is locked to **Anthropic** when using the ClaudeCodeExecutor.")
    else:
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
        env_var = _ENV_VAR_MAP.get(chosen_provider, "")
        env_key_value = os.environ.get(env_var, "")
        has_env_key = bool(env_key_value)
        if has_env_key:
            label = f"API key (using `{env_var}` from environment)"
            st.text_input(
                label,
                value="",
                type="password",
                disabled=True,
                placeholder="Provided by environment variable",
                help=f"The API key is loaded from the `{env_var}` environment variable.",
            )
            api_key = ""
        else:
            default_value = existing.api_key
            api_key = st.text_input(
                "API key",
                value=default_value,
                type="password",
                help="Stored locally, sent only to the provider.",
            )

    base_url = ""
    if chosen_provider == "openai_compat":
        base_url = st.text_input(
            "Base URL",
            value=existing.base_url or "http://localhost:8000/v1",
            help="The base URL of your OpenAI-compatible API server",
        )
    elif chosen_provider == "ollama":
        base_url = st.text_input(
            "Ollama host",
            value=existing.base_url or "http://localhost:11434",
            help="Ollama server URL (leave default for local)",
        )

    _render_test_connection(chosen_provider, api_key, base_url)

    model = _render_model_picker(chosen_provider, existing.model)

    new_cfg = LLMProviderConfig(api_key=api_key, model=model, base_url=base_url)
    new_providers = dict(llm.providers)
    new_providers[chosen_provider] = new_cfg
    new_llm = LLMSettings(
        active_provider=chosen_provider,
        providers=new_providers,
        cached_models=llm.cached_models,
    )

    if auto_apply:
        # Always sync form state → session state so that
        # mark_welcome_completed() persists the correct values,
        # even if the user never touched the defaults.
        st.session_state.llm_settings = new_llm
        st.session_state.executor_type = selected
    else:
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


def _persist_current_settings() -> None:
    """Persist the current executor + LLM settings to disk.

    Called by auto_apply mode so that settings survive the transition
    from setup wizard to normal app mode (where _load_persisted_state
    reads from disk).
    """
    from databao_cli.features.ui.services.settings_persistence import get_or_create_settings, save_settings

    settings = get_or_create_settings()
    settings.agent.executor_type = st.session_state.get("executor_type", "claude_code")
    llm: LLMSettings = st.session_state.get("llm_settings", LLMSettings())
    settings.agent.llm = llm
    save_settings(settings)


def _render_test_connection(provider_type: str, api_key: str, base_url: str) -> None:
    """Render a 'Test connection' link that fetches models and caches the result."""
    cache_key = f"_llm_test_{provider_type}"

    if st.button("🔗 Test connection", type="tertiary", key=f"test_conn_{provider_type}"):
        from databao_cli.features.ui.services.llm_models import fetch_models

        try:
            models = fetch_models(provider_type, api_key, base_url)
            if models is not None:
                st.session_state[cache_key] = {"status": "ok", "models": models}
                llm: LLMSettings = st.session_state.get("llm_settings", LLMSettings())
                llm.cached_models[provider_type] = models
                st.session_state.llm_settings = llm
                st.success(f"Connected! Found {len(models)} model(s).")
            else:
                st.session_state[cache_key] = {"status": "no_list"}
                st.info("Provider doesn't support listing models — enter the model name manually.")
        except Exception as e:
            st.session_state[cache_key] = {"status": "error", "error": str(e)}
            st.error(f"Connection failed: {e}")
        st.rerun()

    # Show persisted status from session
    cached = st.session_state.get(cache_key)
    if cached:
        if cached["status"] == "ok":
            st.caption(f"✅ Connected — {len(cached['models'])} model(s) available")
        elif cached["status"] == "error":
            st.caption(f"❌ {cached['error']}")


def _render_model_picker(provider_type: str, current_model: str) -> str:
    """Render either a dropdown (if models were fetched) or a text input."""
    cache_key = f"_llm_test_{provider_type}"
    session_cached = st.session_state.get(cache_key)
    if session_cached and session_cached.get("status") == "ok" and session_cached.get("models"):
        return _model_selectbox(provider_type, session_cached["models"], current_model)

    llm: LLMSettings = st.session_state.get("llm_settings", LLMSettings())
    persisted = llm.cached_models.get(provider_type)
    if persisted:
        return _model_selectbox(provider_type, persisted, current_model)

    curated = LLM_PROVIDER_MODELS.get(provider_type, [])
    if curated:
        return _model_selectbox(provider_type, curated, current_model)

    return st.text_input(
        "Model",
        value=current_model,
        placeholder=_model_placeholder(provider_type),
        help="The specific model identifier",
    )


def _model_selectbox(provider_type: str, models: list[str], current_model: str) -> str:
    """Render a selectbox with a list of models + 'Other (custom)' option."""
    other_label = "Other (custom)"
    options = [*models, other_label]

    if current_model in models:
        default_index = models.index(current_model)
    elif current_model:
        default_index = _find_closest_model_index(models, current_model, provider_type)
    else:
        from databao_cli.features.ui.services.llm_models import pick_default_model

        best = pick_default_model(models, provider_type)
        default_index = models.index(best) if best in models else 0

    choice = st.selectbox(
        "Model",
        options=options,
        index=default_index,
        key=f"llm_{provider_type}_model_select",
        help="Choose a model or select 'Other' to enter a custom one",
    )

    if choice == other_label:
        return st.text_input(
            "Custom model name",
            value=current_model if current_model not in models else "",
            placeholder=_model_placeholder(provider_type),
            key=f"llm_{provider_type}_model_custom",
        )

    return choice


def _find_closest_model_index(models: list[str], target: str, provider_type: str) -> int:
    """Find the index of the model closest to target by family prefix."""
    family = target.split("-")[0].split(":")[0]
    for i, m in enumerate(models):
        if m.startswith(family):
            return i
    return 0


def _validate_provider(provider_type: str, cfg: LLMProviderConfig) -> list[str]:
    """Return a list of validation error messages (empty if valid)."""
    errors: list[str] = []

    if not cfg.model:
        errors.append("**Model** is required.")

    if provider_type in ("openai", "anthropic"):
        env_var = _ENV_VAR_MAP.get(provider_type, "")
        if not cfg.api_key and not os.environ.get(env_var):
            errors.append(f"**API key** is required (or set `{env_var}` in your environment).")

    if provider_type == "openai_compat" and not cfg.base_url:
        errors.append("**Base URL** is required for an OpenAI-compatible provider.")

    return errors


def _model_placeholder(provider_type: str) -> str:
    """Return a helpful placeholder for the model input based on provider type."""
    placeholders: dict[str, str] = {
        "openai": "gpt-5-mini",
        "anthropic": "claude-sonnet-4-6",
        "ollama": "qwen3:8b",
        "openai_compat": "model-name-on-server",
    }
    return placeholders.get(provider_type, "model-name")
