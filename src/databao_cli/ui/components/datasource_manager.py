"""Reusable datasource management UI component.

Used by both the Welcome Page (setup wizard) and the Context Settings page.
Reads datasource configs from disk on every render -- no in-memory caching.
"""

import logging
from pathlib import Path
from typing import Any, cast

import streamlit as st
from databao_context_engine import ConfiguredDatasource, DatasourceConnectionStatus

from databao_cli.ui.app import invalidate_agent
from databao_cli.ui.components.datasource_form import render_datasource_config_form
from databao_cli.ui.services.dce_operations import (
    add_datasource,
    get_available_datasource_types,
    get_datasource_config_fields,
    list_datasources,
    remove_datasource,
    save_datasource,
    verify_datasource,
    verify_datasource_config,
)

logger = logging.getLogger(__name__)


def render_datasource_manager(project_dir: Path, *, read_only: bool = False) -> None:
    """Render the full datasource management UI.

    Shows:
    - "Add data source" section at top (hidden in read-only mode)
    - List of existing data sources below, each with Save/Verify/Remove buttons
      (buttons hidden in read-only mode, fields disabled)

    Args:
        project_dir: Path to the DCE project directory (e.g. root_domain_dir).
        read_only: If True, show existing datasources as non-editable and hide
            the add section and action buttons.
    """
    if not read_only:
        _render_add_datasource_section(project_dir)
        st.markdown("---")

    configured = list_datasources(project_dir)

    if not configured:
        st.caption("No datasources configured yet.")
        return

    st.subheader("Your data sources")

    for idx, ds in enumerate(configured):
        _render_existing_datasource(project_dir, ds, idx, read_only=read_only)


def _get_form_version() -> int:
    """Get the current form version counter used to reset widget keys."""
    if "_new_ds_form_version" not in st.session_state:
        st.session_state._new_ds_form_version = 0
    return cast(int, st.session_state._new_ds_form_version)


def _render_add_datasource_section(project_dir: Path) -> None:
    """Render the 'Add data source' section."""
    st.subheader("Add data source")

    available_types = get_available_datasource_types()

    if not available_types:
        st.warning("No datasource plugins available.")
        return

    v = _get_form_version()

    selected_type = st.selectbox(
        "Datasource type",
        options=available_types,
        key=f"new_ds_type_v{v}",
        help="Select the type of datasource to add",
    )

    ds_name = st.text_input(
        "Datasource name",
        key=f"new_ds_name_v{v}",
        help="A unique name for this datasource",
    )

    config_values: dict[str, Any] = {}
    if selected_type:
        try:
            config_fields = get_datasource_config_fields(selected_type)
            if config_fields:
                config_values = render_datasource_config_form(
                    config_fields=config_fields,
                    key_prefix=f"new_ds_config_v{v}_",
                )
        except Exception as e:
            st.error(f"Failed to load config fields: {e}")
            logger.exception("Failed to load datasource config fields")

    col_add, col_verify_new = st.columns(2)

    with col_add:
        if st.button("Add datasource", key="add_ds_btn", type="primary", use_container_width=True):
            if not ds_name or not ds_name.strip():
                st.error("Please provide a datasource name.")
            elif not selected_type:
                st.error("Please select a datasource type.")
            else:
                try:
                    add_datasource(project_dir, selected_type, ds_name.strip(), config_values)
                    _clear_new_datasource_form()
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to add datasource: {e}")
                    logger.exception("Failed to add datasource")

    with col_verify_new:
        if st.button("Verify connection", key="verify_new_ds_btn", use_container_width=True):
            if not ds_name or not ds_name.strip() or not selected_type:
                st.error("Please provide a datasource name and type first.")
            else:
                try:
                    result = verify_datasource_config(selected_type, ds_name.strip(), config_values)
                    if result.connection_status == DatasourceConnectionStatus.VALID:
                        st.success("Connection valid.")
                    elif result.connection_status == DatasourceConnectionStatus.UNKNOWN:
                        st.warning(f"Unknown: {result.summary or 'Plugin does not support verification.'}")
                    else:
                        st.error(f"Invalid: {result.summary or 'Connection failed.'}")
                        if result.full_message:
                            with st.expander("Details"):
                                st.code(result.full_message)
                except Exception as e:
                    st.error(f"Verification failed: {e}")
                    logger.exception("Failed to verify new datasource")


def _render_existing_datasource(project_dir: Path, ds: ConfiguredDatasource, idx: int, *, read_only: bool = False) -> None:
    """Render a single existing datasource with its config fields and action buttons."""
    ds_id = ds.datasource.id
    ds_type = ds.datasource.type.full_type
    ds_config = ds.config or {}
    ds_name = ds_config.get("name", ds_id.datasource_path.split("/")[-1])

    with st.container():
        st.markdown(f"**{ds_name}** &nbsp; `{ds_type}`")

        try:
            config_fields = get_datasource_config_fields(ds_type)
        except Exception:
            config_fields = []
            st.caption("Could not load config field definitions for this datasource type.")

        edited_values: dict[str, Any] = {}
        if config_fields:
            edited_values = render_datasource_config_form(
                config_fields=config_fields,
                existing_values=ds_config,
                key_prefix=f"ds_{idx}_",
                disabled=read_only,
            )

        if not read_only:
            _original_config = {k: v for k, v in ds_config.items() if k not in ("type", "name")}
            has_changes = edited_values != _original_config

            col_save, col_verify, col_remove = st.columns(3)

            with col_save:
                if st.button(
                    "Save",
                    key=f"save_ds_{idx}",
                    disabled=not has_changes,
                    use_container_width=True,
                ):
                    try:
                        save_datasource(project_dir, ds_type, ds_name, edited_values)
                        st.success("Saved.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Save failed: {e}")

            with col_verify:
                if st.button("Verify", key=f"verify_ds_{idx}", use_container_width=True):
                    try:
                        result = verify_datasource(project_dir, ds_id)
                        if result.connection_status == DatasourceConnectionStatus.VALID:
                            st.success("Connection valid.")
                        elif result.connection_status == DatasourceConnectionStatus.UNKNOWN:
                            st.warning(f"Unknown: {result.summary or 'Plugin does not support verification.'}")
                        else:
                            st.error(f"Invalid: {result.summary or 'Connection failed.'}")
                            if result.full_message:
                                with st.expander("Details"):
                                    st.code(result.full_message)
                    except Exception as e:
                        st.error(f"Verification failed: {e}")

            with col_remove:
                if st.button(
                    "Remove",
                    key=f"remove_ds_{idx}",
                    type="primary",
                    use_container_width=True,
                ):
                    st.session_state[f"_confirm_remove_{idx}"] = True

            if st.session_state.get(f"_confirm_remove_{idx}"):
                st.warning(f"Are you sure you want to remove **{ds_name}**?")
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("Yes, remove", key=f"confirm_remove_{idx}", type="primary", use_container_width=True):
                        try:
                            remove_datasource(project_dir, ds_id)
                            st.session_state.pop(f"_confirm_remove_{idx}", None)
                            invalidate_agent("Datasource removed, reinitializing agent...")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Remove failed: {e}")
                with col_no:
                    if st.button("Cancel", key=f"cancel_remove_{idx}", use_container_width=True):
                        st.session_state.pop(f"_confirm_remove_{idx}", None)
                        st.rerun()

        st.markdown("---")


def _clear_new_datasource_form() -> None:
    """Reset the 'Add data source' form by incrementing the version counter.

    This causes all form widgets to get fresh keys on the next rerun,
    so they render with their default (empty) values.
    """
    st.session_state._new_ds_form_version = _get_form_version() + 1
