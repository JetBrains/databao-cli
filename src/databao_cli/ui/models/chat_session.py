"""Chat session model for managing multiple chat conversations."""

import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

from databao.agent import ExecutionResult

if TYPE_CHECKING:
    from databao.agent.core.thread import Thread

    from databao_cli.ui.streaming import StreamingWriter

__all__ = ["ChatMessage", "ChatSession"]


@dataclass
class ChatMessage:
    """Represents a chat message."""

    role: str
    content: str
    thinking: str | None = None
    result: ExecutionResult | None = None
    has_visualization: bool = False
    visualization_data: dict[str, Any] | None = None
    viz_pending: bool = False
    """Transient flag: visualization is being generated (not persisted to disk)."""
    message_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


def _serialize_visualization_data(data: dict[str, Any] | None) -> dict[str, Any] | None:
    """Serialize visualization_data for JSON, excluding non-serializable fields like spec_df."""
    if data is None:
        return None
    serializable = {k: v for k, v in data.items() if k != "spec_df"}
    if "spec_df" in data and data["spec_df"] is not None:
        serializable["_has_spec_df"] = True
    return serializable


@dataclass
class ChatSession:
    """A chat session containing conversation history and metadata."""

    id: str  # UUID6 string
    created_at: datetime = field(default_factory=datetime.now)
    title: str | None = None
    title_status: str = "pending"
    messages: list[ChatMessage] = field(default_factory=list)
    thread: "Thread | None" = None
    cache_scope: str | None = None

    query_thread: threading.Thread | None = None
    query_status: str = "idle"

    writer: "StreamingWriter | None" = None

    @property
    def display_title(self) -> str:
        """Get display title for navigation menu."""
        if self.title:
            return self.title
        return f"Chat {self.created_at.strftime('%b %d, %H:%M')}"

    @property
    def first_user_message(self) -> str | None:
        """Get the first user message for title generation."""
        for msg in self.messages:
            if msg.role == "user":
                return msg.content
        return None

    @property
    def has_first_response(self) -> bool:
        """Check if the chat has received its first assistant response."""
        user_found = False
        for msg in self.messages:
            if msg.role == "user":
                user_found = True
            elif msg.role == "assistant" and user_found:
                return True
        return False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization.

        Note: thread is not serialized (rebuilt on load), results are handled separately.
        """
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "title": self.title,
            "title_status": self.title_status,
            "cache_scope": self.cache_scope,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "thinking": msg.thinking,
                    "has_visualization": msg.has_visualization,
                    "visualization_data": _serialize_visualization_data(msg.visualization_data),
                    "message_id": msg.message_id,
                    "metadata": msg.metadata,
                    "timestamp": msg.timestamp.isoformat(),
                }
                for msg in self.messages
            ],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any], results: list[Any] | None = None) -> "ChatSession":
        """Create ChatSession from dictionary.

        Args:
            data: Dictionary from to_dict()
            results: Optional list of ExecutionResult objects to attach to messages
        """
        messages = []
        for i, msg_data in enumerate(data.get("messages", [])):
            result = results[i] if results and i < len(results) else None

            messages.append(
                ChatMessage(
                    role=msg_data["role"],
                    content=msg_data["content"],
                    thinking=msg_data.get("thinking"),
                    result=result,
                    has_visualization=msg_data.get("has_visualization", False),
                    visualization_data=msg_data.get("visualization_data"),
                    message_id=msg_data.get("message_id", ""),
                    metadata=msg_data.get("metadata", {}),
                    timestamp=datetime.fromisoformat(msg_data["timestamp"]) if "timestamp" in msg_data else datetime.now(),
                )
            )

        return cls(
            id=data["id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            title=data.get("title"),
            title_status=data.get("title_status", "pending"),
            messages=messages,
            thread=None,
            cache_scope=data.get("cache_scope"),
        )
