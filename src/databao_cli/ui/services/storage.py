"""Storage service for determining and managing storage paths."""

import logging
import re
from pathlib import Path

import streamlit as st

logger = logging.getLogger(__name__)

_UI_SUBDIR = "ui"

_CHATS_SUBDIR = "chats"
_CACHE_SUBDIR = "cache"
_SETTINGS_FILE = "settings.yaml"

_UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE)

_DIR_MODE = 0o700


def is_valid_chat_id(chat_id: str) -> bool:
    """Check whether *chat_id* looks like a valid UUID (hex + dashes)."""
    return bool(_UUID_RE.match(chat_id))


def _mkdir_secure(path: Path) -> None:
    """Create a directory (and parents) with owner-only permissions."""
    path.mkdir(parents=True, exist_ok=True)
    path.chmod(_DIR_MODE)


def get_storage_base_path() -> Path:
    """Get the storage path for UI settings and chats.

    Returns:
        Path to <databao_project_path>/ui/
    """
    databao_project = st.session_state.databao_project
    if databao_project is None:
        raise RuntimeError("Databao project path not set")
    return databao_project.databao_dir / _UI_SUBDIR


def get_settings_path() -> Path:
    """Get the path to settings.yaml file.

    Returns:
        Path to settings.yaml
    """
    base = get_storage_base_path()
    return base / _SETTINGS_FILE


def get_chats_dir() -> Path:
    """Get the chats directory path.

    Returns:
        Path to chats directory
    """
    base = get_storage_base_path()
    chats_dir = base / _CHATS_SUBDIR
    _mkdir_secure(chats_dir)
    return chats_dir


def get_cache_dir() -> Path:
    """Get the cache directory path for DiskCache.

    Returns:
        Path to cache directory
    """
    base = get_storage_base_path()
    cache_dir = base / _CACHE_SUBDIR
    _mkdir_secure(cache_dir)
    return cache_dir


def get_chat_dir(chat_id: str) -> Path:
    """Get the directory for a specific chat.

    Args:
        chat_id: The chat's unique ID

    Returns:
        Path to the chat's directory

    Raises:
        ValueError: If chat_id is not a valid UUID.
    """
    if not is_valid_chat_id(chat_id):
        raise ValueError(f"Invalid chat_id: {chat_id!r}")
    chats = get_chats_dir()
    chat_dir = chats / chat_id
    _mkdir_secure(chat_dir)
    return chat_dir
