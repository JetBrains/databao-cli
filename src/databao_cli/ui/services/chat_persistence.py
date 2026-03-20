"""Chat persistence service for saving and loading chat sessions."""

from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pandas as pd
from databao.agent import ExecutionResult

from databao_cli.ui.services.storage import get_cache_dir, get_chat_dir, get_chats_dir, is_valid_chat_id

if TYPE_CHECKING:
    from databao_cli.ui.models.chat_session import ChatSession

logger = logging.getLogger(__name__)


def save_current_chat() -> None:
    """Save the current chat from session state to disk.

    This is a convenience function that gets the current chat from
    st.session_state and saves it using save_chat().
    """
    import streamlit as st

    current_chat_id = st.session_state.get("current_chat_id")
    chats = st.session_state.get("chats", {})
    if current_chat_id and current_chat_id in chats:
        save_chat(chats[current_chat_id])


_SESSION_FILE = "session.json"
_RESULTS_DIR = "results"
_VISUALIZATIONS_DIR = "visualizations"


def _write_file_secure(path: Path, data: bytes | str, *, binary: bool = False) -> None:
    """Write data to a file and set owner-only permissions (0o600)."""
    mode = "wb" if binary else "w"
    with open(path, mode) as f:
        f.write(data)
    path.chmod(0o600)


def save_chat(chat: ChatSession) -> None:
    """Save a chat session to disk.

    Saves:
    - session.json: Chat metadata and messages (without results)
    - results/{idx}.json: JSON with text/code from ExecutionResult
    - results/{idx}.parquet: DataFrame from ExecutionResult (when present)
    - visualizations/{idx}_spec_df.parquet: Visualization spec DataFrame

    Args:
        chat: The ChatSession to save
    """
    chat_dir = get_chat_dir(chat.id)

    session_data = chat.to_dict()
    session_path = chat_dir / _SESSION_FILE
    _write_file_secure(session_path, json.dumps(session_data, indent=2))

    results_dir = chat_dir / _RESULTS_DIR
    results_dir.mkdir(parents=True, exist_ok=True)

    for i, msg in enumerate(chat.messages):
        json_path = results_dir / f"{i}.json"
        parquet_path = results_dir / f"{i}.parquet"
        if msg.result is not None:
            try:
                result_json = {"text": msg.result.text, "code": msg.result.code}
                _write_file_secure(json_path, json.dumps(result_json))
                if msg.result.df is not None:
                    msg.result.df.to_parquet(parquet_path)
                    parquet_path.chmod(0o600)
                elif parquet_path.exists():
                    parquet_path.unlink()
            except Exception as e:
                logger.warning(f"Failed to save result for message {i}: {e}")
                for p in (json_path, parquet_path):
                    if p.exists():
                        p.unlink()
        else:
            for p in (json_path, parquet_path):
                if p.exists():
                    p.unlink()

    visualizations_dir = chat_dir / _VISUALIZATIONS_DIR
    visualizations_dir.mkdir(parents=True, exist_ok=True)

    for i, msg in enumerate(chat.messages):
        vis_df_path = visualizations_dir / f"{i}_spec_df.parquet"
        vis_data = msg.visualization_data
        if vis_data is not None and vis_data.get("spec_df") is not None:
            try:
                vis_data["spec_df"].to_parquet(vis_df_path)
                vis_df_path.chmod(0o600)
            except Exception as e:
                logger.warning(f"Failed to save visualization spec_df for message {i}: {e}")
                if vis_df_path.exists():
                    vis_df_path.unlink()
        elif vis_df_path.exists():
            vis_df_path.unlink()

    logger.debug(f"Chat saved: {chat.id}")


def load_chat(chat_id: str) -> ChatSession | None:
    """Load a chat session from disk.

    Args:
        chat_id: The chat's unique ID

    Returns:
        ChatSession if found, None otherwise
    """
    if not is_valid_chat_id(chat_id):
        logger.warning(f"Refusing to load chat with invalid id: {chat_id!r}")
        return None

    from databao_cli.ui.models.chat_session import ChatSession

    chats_dir = get_chats_dir()
    chat_dir = chats_dir / chat_id

    if not chat_dir.exists():
        return None

    session_path = chat_dir / _SESSION_FILE
    if not session_path.exists():
        return None

    try:
        with open(session_path) as f:
            session_data = json.load(f)

        results_dir = chat_dir / _RESULTS_DIR
        results: list[Any] = []

        num_messages = len(session_data.get("messages", []))
        for i in range(num_messages):
            json_path = results_dir / f"{i}.json"
            if json_path.exists():
                try:
                    with open(json_path) as f:
                        result_data = json.load(f)
                    parquet_path = results_dir / f"{i}.parquet"
                    df = pd.read_parquet(parquet_path) if parquet_path.exists() else None
                    results.append(
                        ExecutionResult(
                            text=result_data["text"],
                            code=result_data.get("code"),
                            df=df,
                            meta={},
                        )
                    )
                except Exception as e:
                    logger.warning(f"Failed to load result {i} for chat {chat_id}: {e}")
                    results.append(None)
            else:
                results.append(None)

        visualizations_dir = chat_dir / _VISUALIZATIONS_DIR
        for i, msg_data in enumerate(session_data.get("messages", [])):
            vis_data = msg_data.get("visualization_data")
            if vis_data is not None:
                vis_df_path = visualizations_dir / f"{i}_spec_df.parquet"
                expects_spec_df = bool(vis_data.get("_has_spec_df"))
                has_spec_df_parquet = vis_df_path.exists()
                if expects_spec_df or has_spec_df_parquet:
                    if has_spec_df_parquet:
                        try:
                            vis_data["spec_df"] = pd.read_parquet(vis_df_path)
                        except Exception as e:
                            logger.warning(f"Failed to load visualization spec_df {i} for chat {chat_id}: {e}")
                            vis_data["spec_df"] = None
                    elif expects_spec_df:
                        logger.warning(f"Missing visualization spec_df parquet for message {i} in chat {chat_id}")
                        vis_data["spec_df"] = None
                vis_data.pop("_has_spec_df", None)

        chat = ChatSession.from_dict(session_data, results)
        logger.debug(f"Chat loaded: {chat_id}")
        return chat

    except Exception as e:
        logger.error(f"Failed to load chat {chat_id}: {e}")
        return None


def load_all_chats() -> dict[str, ChatSession]:
    """Load all chat sessions from disk.

    Returns:
        Dictionary mapping chat ID to ChatSession
    """
    chats_dir = get_chats_dir()
    chats: dict[str, ChatSession] = {}

    if not chats_dir.exists():
        return chats

    for chat_dir in chats_dir.iterdir():
        if not chat_dir.is_dir():
            continue

        chat_id = chat_dir.name
        if not is_valid_chat_id(chat_id):
            continue
        chat = load_chat(chat_id)
        if chat is not None:
            chats[chat_id] = chat

    logger.info(f"Loaded {len(chats)} chats from disk")
    return chats


def delete_chat(chat_id: str) -> bool:
    """Delete a chat session and its cache data.

    Args:
        chat_id: The chat's unique ID

    Returns:
        True if deleted successfully, False otherwise
    """
    if not is_valid_chat_id(chat_id):
        logger.warning(f"Refusing to delete chat with invalid id: {chat_id!r}")
        return False

    chat = load_chat(chat_id)
    cache_scope = chat.cache_scope if chat else None

    chats_dir = get_chats_dir()
    chat_dir = chats_dir / chat_id

    try:
        if chat_dir.exists():
            shutil.rmtree(chat_dir)
            logger.info(f"Deleted chat directory: {chat_dir}")
    except Exception as e:
        logger.error(f"Failed to delete chat directory {chat_dir}: {e}")
        return False

    if cache_scope:
        try:
            _delete_cache_scope(cache_scope)
        except Exception as e:
            logger.warning(f"Failed to delete cache scope {cache_scope}: {e}")

    return True


def _delete_cache_scope(cache_scope: str) -> None:
    """Delete cache data for a specific scope.

    Args:
        cache_scope: The cache scope identifier (e.g., "agent_name/uuid")
    """
    from databao.agent.caches.disk_cache import DiskCache, DiskCacheConfig

    cache_dir = get_cache_dir()
    config = DiskCacheConfig(db_dir=cache_dir / "diskcache")
    cache = DiskCache(config=config)

    try:
        cache.invalidate_tag(cache_scope)
        logger.debug(f"Invalidated cache tag: {cache_scope}")
    finally:
        cache.close()


def delete_all_chats() -> int:
    """Delete all chat sessions.

    Returns:
        Number of chats deleted
    """
    chats_dir = get_chats_dir()
    deleted = 0

    if not chats_dir.exists():
        return 0

    for chat_dir in list(chats_dir.iterdir()):
        if not chat_dir.is_dir():
            continue

        chat_id = chat_dir.name
        if delete_chat(chat_id):
            deleted += 1

    cache_dir = get_cache_dir()
    diskcache_dir = cache_dir / "diskcache"
    if diskcache_dir.exists():
        try:
            shutil.rmtree(diskcache_dir)
            logger.info(f"Cleared cache directory: {diskcache_dir}")
        except Exception as e:
            logger.warning(f"Failed to clear cache directory: {e}")

    logger.info(f"Deleted {deleted} chats")
    return deleted
