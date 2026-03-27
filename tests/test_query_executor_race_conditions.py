"""Race condition and edge case tests for query executor interruption logic.

These tests focus on UX guarantees:
- App stability under concurrent/rapid operations
- User can stop queries and start new ones immediately
- Data is preserved when stopping during visualization
- Thinking text is captured for display to user
"""

import contextlib
import threading
import time
from unittest.mock import MagicMock, patch

import pytest

from databao_cli.features.ui.models.chat_session import ChatMessage, ChatSession
from databao_cli.features.ui.services.query_executor import (
    QueryResult,
    QueryThread,
    check_query_completion,
    is_query_running,
    start_query_execution,
    stop_query,
)


@pytest.fixture
def chat_session() -> ChatSession:
    """Create a minimal chat session for testing."""
    return ChatSession(id="test-chat-id")


@pytest.fixture
def mock_writer() -> MagicMock:
    """Create a mock StreamingWriter."""
    writer = MagicMock()
    writer.getvalue.return_value = "thinking text"
    writer.clear = MagicMock()
    writer._on_write = MagicMock()
    return writer


class TestConcurrentStopCalls:
    """Tests for race conditions when stop_query is called concurrently."""

    def test_concurrent_stop_calls_are_safe(self, chat_session: ChatSession, mock_writer: MagicMock) -> None:
        """Two threads calling stop_query simultaneously should not crash."""
        # Setup a long-running query thread
        query_running = threading.Event()

        def slow_work() -> None:
            query_running.set()
            try:
                while True:
                    time.sleep(0.01)
            except (KeyboardInterrupt, SystemExit):
                pass

        worker = threading.Thread(target=slow_work, daemon=True)
        worker.start()
        query_running.wait(timeout=1.0)

        chat_session.query_status = "running"
        chat_session.writer = mock_writer
        chat_session.query_thread = worker
        chat_session.thread = MagicMock()

        # Synchronize two threads to call stop_query simultaneously
        barrier = threading.Barrier(2)
        results: list[str | None] = [None, None]
        exceptions: list[Exception | None] = [None, None]

        def stop_caller(index: int) -> None:
            try:
                barrier.wait(timeout=1.0)
                results[index] = stop_query(chat_session)
            except Exception as e:
                exceptions[index] = e

        t1 = threading.Thread(target=stop_caller, args=(0,))
        t2 = threading.Thread(target=stop_caller, args=(1,))

        t1.start()
        t2.start()
        t1.join(timeout=2.0)
        t2.join(timeout=2.0)

        # Neither should raise an exception
        assert exceptions[0] is None, f"Thread 1 raised: {exceptions[0]}"
        assert exceptions[1] is None, f"Thread 2 raised: {exceptions[1]}"

        # Final state should be idle
        assert chat_session.query_status == "idle"

    def test_multiple_stops_idempotent(self, chat_session: ChatSession, mock_writer: MagicMock) -> None:
        """Calling stop_query multiple times should be safe and idempotent."""
        chat_session.query_status = "running"
        chat_session.writer = mock_writer
        chat_session.query_thread = None
        chat_session.thread = MagicMock()

        # First stop
        result1 = stop_query(chat_session)
        assert result1 == "thinking text"
        assert chat_session.query_status == "idle"

        # Second stop (already idle)
        result2 = stop_query(chat_session)
        assert result2 is None  # Returns None when not running

        # Third stop
        result3 = stop_query(chat_session)
        assert result3 is None


class TestThreadStateTransitionRaces:
    """Tests for races during thread state transitions."""

    def test_thread_dies_between_alive_check_and_result_read(self, chat_session: ChatSession) -> None:
        """Thread finishes exactly between is_alive() check and reading result."""
        check_started = threading.Event()

        def quick_work() -> None:
            check_started.wait(timeout=1.0)
            # Finish immediately after check_query_completion starts
            time.sleep(0.01)

        worker = threading.Thread(target=quick_work, daemon=True)
        worker.start()

        # Create a QueryThread-like mock that simulates the race
        mock_query_thread = MagicMock(spec=QueryThread)
        call_count = [0]

        def is_alive_side_effect() -> bool:
            call_count[0] += 1
            if call_count[0] == 1:
                check_started.set()
                time.sleep(0.02)  # Let thread finish
                return True  # First call returns True
            return False  # Subsequent calls return False

        mock_query_thread.is_alive.side_effect = is_alive_side_effect
        mock_query_thread.result = QueryResult(
            text="result",
            thinking="",
            result=None,
            has_visualization=False,
        )
        mock_query_thread.partial_result = None

        chat_session.query_status = "running"
        chat_session.query_thread = mock_query_thread

        # This should handle the race gracefully - key is it doesn't crash
        check_query_completion(chat_session)

        worker.join(timeout=1.0)

    def test_partial_result_consumed_by_single_caller(self, chat_session: ChatSession) -> None:
        """Only one caller should consume partial_result."""
        mock_query_thread = MagicMock(spec=QueryThread)
        mock_query_thread.is_alive.return_value = True

        partial = QueryResult(
            text="partial",
            thinking="thinking",
            result=None,
            has_visualization=False,
            viz_pending=True,
        )
        mock_query_thread.partial_result = partial

        chat_session.query_status = "running"
        chat_session.query_thread = mock_query_thread

        # First call consumes the partial result
        result1 = check_query_completion(chat_session)
        assert result1 is not None
        assert result1.viz_pending is True
        assert mock_query_thread.partial_result is None

        # Reset status for second check
        chat_session.query_status = "visualizing"

        # Second call gets None (partial already consumed)
        result2 = check_query_completion(chat_session)
        assert result2 is None

    def test_phase_transition_during_stop(self, chat_session: ChatSession, mock_writer: MagicMock) -> None:
        """Phase changes from 'asking' to 'visualizing' during stop should be handled."""
        phase_changed = threading.Event()
        stop_called = threading.Event()

        def work_with_phase_change() -> None:
            try:
                stop_called.wait(timeout=1.0)
                # Simulate phase change during stop
                time.sleep(0.01)
                phase_changed.set()
                while True:
                    time.sleep(0.01)
            except (KeyboardInterrupt, SystemExit):
                pass  # Expected - test is verifying stop works

        worker = threading.Thread(target=work_with_phase_change, daemon=True)
        worker.start()

        chat_session.query_status = "running"
        chat_session.writer = mock_writer
        chat_session.query_thread = worker
        chat_session.thread = MagicMock()

        # Signal that stop is about to be called
        stop_called.set()

        # Stop should work regardless of phase changes
        result = stop_query(chat_session)

        assert result is not None
        assert chat_session.query_status == "idle"


class TestRapidSequentialOperations:
    """Tests for rapid sequential operations."""

    @patch("databao_cli.features.ui.services.query_executor.get_script_run_ctx")
    def test_rapid_stop_start_stop(self, mock_ctx: MagicMock, chat_session: ChatSession, mock_writer: MagicMock) -> None:
        """Quick stop→start→stop sequence should work correctly."""
        mock_ctx.return_value = None

        # Setup initial running query
        def slow_work() -> None:
            try:
                while True:
                    time.sleep(0.01)
            except (KeyboardInterrupt, SystemExit):
                pass

        worker = threading.Thread(target=slow_work, daemon=True)
        worker.start()

        chat_session.query_status = "running"
        chat_session.writer = mock_writer
        chat_session.query_thread = worker
        chat_session.thread = MagicMock()

        # Stop
        stop_query(chat_session)
        assert chat_session.query_status == "idle"

        # Immediately start new query
        mock_thread = MagicMock()
        mock_thread._data_result = MagicMock(text="result", meta=None)
        mock_thread._visualization_result = None

        new_writer = MagicMock()
        new_writer.getvalue.return_value = ""
        new_writer.clear = MagicMock()
        chat_session.writer = new_writer

        started = start_query_execution(chat_session, mock_thread, "new query")
        assert started is True
        assert chat_session.query_status == "running"

        # Immediately stop again
        stop_query(chat_session)
        assert chat_session.query_status == "idle"

    @patch("databao_cli.features.ui.services.query_executor.get_script_run_ctx")
    def test_start_immediately_after_stop(
        self, mock_ctx: MagicMock, chat_session: ChatSession, mock_writer: MagicMock
    ) -> None:
        """Start new query before reaper finishes previous one."""
        mock_ctx.return_value = None

        # Create a stubborn thread that ignores KeyboardInterrupt
        stubborn_running = threading.Event()

        def stubborn_work() -> None:
            stubborn_running.set()
            try:
                while True:
                    with contextlib.suppress(KeyboardInterrupt):
                        time.sleep(0.1)
            except SystemExit:
                pass

        worker = threading.Thread(target=stubborn_work, daemon=True)
        worker.start()
        stubborn_running.wait(timeout=1.0)

        chat_session.query_status = "running"
        chat_session.writer = mock_writer
        chat_session.query_thread = worker
        chat_session.thread = MagicMock()

        # Stop (spawns reaper)
        stop_query(chat_session)
        assert chat_session.query_status == "idle"

        # Original worker might still be alive (reaper hasn't killed it yet)
        # But we should be able to start a new query
        mock_thread = MagicMock()
        mock_thread._data_result = MagicMock(text="result", meta=None)
        mock_thread._visualization_result = None

        new_writer = MagicMock()
        new_writer.getvalue.return_value = ""
        new_writer.clear = MagicMock()
        chat_session.writer = new_writer

        started = start_query_execution(chat_session, mock_thread, "new query")
        assert started is True


class TestThinkingTextCapture:
    """Tests that thinking text is captured for display to user when stopping."""

    def test_stop_returns_thinking_text_for_user_display(self, chat_session: ChatSession) -> None:
        """User should see the thinking text that was captured before stop."""
        mock_writer = MagicMock()
        mock_writer.getvalue.return_value = "Analyzing your question about sales data..."
        mock_writer._on_write = MagicMock()

        chat_session.query_status = "running"
        chat_session.writer = mock_writer
        chat_session.query_thread = None
        chat_session.thread = MagicMock()

        thinking_text = stop_query(chat_session)

        # User should see this text in the stopped message
        assert thinking_text == "Analyzing your question about sales data..."

    def test_stop_returns_empty_when_no_thinking_yet(self, chat_session: ChatSession) -> None:
        """If stopped before any thinking, user sees empty (not an error)."""
        chat_session.query_status = "running"
        chat_session.writer = None
        chat_session.query_thread = None
        chat_session.thread = MagicMock()

        thinking_text = stop_query(chat_session)

        # Empty string is valid - user just sees "Query was stopped"
        assert thinking_text == ""
        # User can start new query
        assert chat_session.query_status == "idle"


class TestUserCanStartNewQueryAfterStop:
    """Tests that user can always start a new query after stopping."""

    def test_stop_allows_immediate_new_query(self, chat_session: ChatSession, mock_writer: MagicMock) -> None:
        """After stopping, user should be able to start a new query immediately."""
        mock_query_thread = MagicMock()
        mock_query_thread.is_alive.return_value = True

        chat_session.query_status = "running"
        chat_session.writer = mock_writer
        chat_session.query_thread = mock_query_thread
        chat_session.thread = MagicMock()

        stop_query(chat_session)

        # Key UX assertion: user can start new query
        assert chat_session.query_status == "idle"
        assert not is_query_running(chat_session)

    def test_inconsistent_state_does_not_crash(self, chat_session: ChatSession) -> None:
        """App should not crash even with inconsistent internal state."""
        # Simulate edge case: status idle but thread ref exists
        mock_query_thread = MagicMock(spec=QueryThread)
        mock_query_thread.is_alive.return_value = False
        mock_query_thread.result = QueryResult(
            text="stale",
            thinking="",
            result=None,
            has_visualization=False,
        )

        chat_session.query_status = "idle"
        chat_session.query_thread = mock_query_thread

        # Should not crash - this is the key UX guarantee
        check_query_completion(chat_session)


class TestDataAppearsOnceToUser:
    """Tests that query results appear exactly once to the user."""

    def test_complete_result_shown_to_user(self) -> None:
        """User sees complete result with text and thinking."""
        mock_databao_thread = MagicMock()
        mock_databao_thread._auto_output_modality = True
        mock_databao_thread._data_result = MagicMock()
        mock_databao_thread._data_result.text = "Here are your top 10 customers..."
        mock_databao_thread._data_result.meta = None
        mock_databao_thread._visualization_result = None

        mock_writer = MagicMock()
        mock_writer.getvalue.return_value = "Looking up customer data..."

        query_thread = QueryThread(mock_databao_thread, "test", mock_writer)
        query_thread.run()

        # User sees both the answer and the thinking process
        assert query_thread.result is not None
        assert query_thread.result.text == "Here are your top 10 customers..."
        assert query_thread.result.thinking == "Looking up customer data..."
        assert query_thread.result.error is None

    def test_data_available_before_visualization_starts(self) -> None:
        """User can see data results while visualization is generating."""
        mock_databao_thread = MagicMock()
        mock_databao_thread._auto_output_modality = True

        mock_result = MagicMock()
        mock_result.text = "Sales data for Q1"
        mock_result.meta = {"output_modality_hints": MagicMock(should_visualize=True, visualization_prompt="plot it")}
        mock_databao_thread._data_result = mock_result
        mock_databao_thread._visualization_result = MagicMock()

        mock_writer = MagicMock()
        mock_writer.getvalue.return_value = "Querying database..."

        query_thread = QueryThread(mock_databao_thread, "test", mock_writer)

        # Track when data becomes visible
        data_visible_before_plot = [False]

        def check_on_plot(*args, **kwargs) -> None:  # type: ignore
            # When plot starts, partial_result should be set (data visible to user)
            if query_thread.partial_result is not None:
                data_visible_before_plot[0] = True

        mock_databao_thread.plot.side_effect = check_on_plot

        query_thread.run()

        # UX: User can see data while waiting for chart
        assert data_visible_before_plot[0], "Data should be visible before viz starts"


class TestStopPreservesUserData:
    """Tests that stopping preserves data the user should see."""

    def test_stop_early_no_data_lost(self) -> None:
        """Stopping before data phase completes - no data to lose, app doesn't crash."""
        mock_databao_thread = MagicMock()

        def interrupted_ask(*args, **kwargs) -> None:  # type: ignore
            raise KeyboardInterrupt()

        mock_databao_thread.ask.side_effect = interrupted_ask

        query_thread = QueryThread(mock_databao_thread, "test", None)
        query_thread.run()

        # No crash, no data to show user (expected)
        assert query_thread.result is None

    def test_stop_during_visualization_preserves_data_for_user(self) -> None:
        """User sees data result even if stopped during chart generation."""
        mock_databao_thread = MagicMock()
        mock_databao_thread._auto_output_modality = True

        mock_result = MagicMock()
        mock_result.text = "Revenue increased 15% in Q2"
        mock_result.meta = {"output_modality_hints": MagicMock(should_visualize=True, visualization_prompt="plot")}
        mock_databao_thread._data_result = mock_result

        def interrupted_plot(*args, **kwargs) -> None:  # type: ignore
            raise KeyboardInterrupt()

        mock_databao_thread.plot.side_effect = interrupted_plot

        mock_writer = MagicMock()
        mock_writer.getvalue.return_value = "Calculating quarterly revenue..."

        query_thread = QueryThread(mock_databao_thread, "test", mock_writer)
        query_thread.run()

        # Key UX: User still sees the data even though viz was cancelled
        assert query_thread.partial_result is not None
        assert query_thread.partial_result.text == "Revenue increased 15% in Q2"

    def test_viz_error_shows_data_with_error_message(self) -> None:
        """If visualization fails, user sees data + error message (not lost data)."""
        mock_databao_thread = MagicMock()
        mock_databao_thread._auto_output_modality = True

        mock_result = MagicMock()
        mock_result.text = "Top 5 products by sales"
        mock_result.meta = {"output_modality_hints": MagicMock(should_visualize=True, visualization_prompt="plot")}
        mock_databao_thread._data_result = mock_result

        mock_databao_thread.plot.side_effect = RuntimeError("Chart rendering failed")

        mock_writer = MagicMock()
        mock_writer.getvalue.return_value = "Generating chart..."

        query_thread = QueryThread(mock_databao_thread, "test", mock_writer)
        query_thread.run()

        # UX: User sees data AND knows viz failed (not silent failure)
        assert query_thread.result is not None
        assert query_thread.result.text == "Top 5 products by sales"
        assert query_thread.result.error is not None
        assert "Chart rendering failed" in query_thread.result.error


class TestOverwriteDialogBehavior:
    """Tests for the overwrite dialog UX after stopping a query."""

    def test_stopped_message_marked_for_overwrite_dialog(self) -> None:
        """A stopped message without result triggers overwrite dialog on new query."""
        # This represents the message that would be created by _handle_stop_click
        stopped_message = ChatMessage(
            role="assistant",
            content="",
            thinking="Partial thinking...",
            result=None,  # No result = stopped early
            metadata={"stopped": True},
        )

        # UX: This message should trigger overwrite confirmation
        assert stopped_message.metadata.get("stopped") is True
        assert stopped_message.result is None

    def test_stopped_during_viz_has_result_no_overwrite_needed(self) -> None:
        """Stopped during viz has result, so no overwrite dialog needed."""
        # Simulates stopping during visualization phase
        stopped_message = ChatMessage(
            role="assistant",
            content="Here is your data",
            thinking="Processing...",
            result=MagicMock(),  # Has result = stopped during viz
            metadata={"stopped": True},
        )

        # UX: This has data, conversation can continue normally
        assert stopped_message.metadata.get("stopped") is True
        assert stopped_message.result is not None  # Has data, no overwrite needed
