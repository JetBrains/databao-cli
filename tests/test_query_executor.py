"""Tests for query executor interruption logic."""

import threading
import time
from unittest.mock import MagicMock, patch

import pytest

from databao_cli.ui.models.chat_session import ChatSession
from databao_cli.ui.services.query_executor import (
    QueryResult,
    QueryThread,
    _raise_in_thread,
    _reap_thread,
    check_query_completion,
    get_query_phase,
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


@pytest.fixture
def mock_thread() -> MagicMock:
    """Create a mock databao Thread."""
    thread = MagicMock()
    thread._auto_output_modality = True
    thread._data_result = MagicMock()
    thread._data_result.text = "result text"
    thread._data_result.meta = None
    thread._visualization_result = None
    return thread


class TestQueryResult:
    """Tests for QueryResult dataclass."""

    def test_query_result_defaults(self) -> None:
        result = QueryResult(
            text="test",
            thinking="thinking",
            result=None,
            has_visualization=False,
        )
        assert result.visualization_data is None
        assert result.error is None
        assert result.viz_pending is False

    def test_query_result_with_error(self) -> None:
        result = QueryResult(
            text="",
            thinking="",
            result=None,
            has_visualization=False,
            error="test error",
        )
        assert result.error == "test error"


class TestIsQueryRunning:
    """Tests for is_query_running function."""

    def test_idle_status(self, chat_session: ChatSession) -> None:
        chat_session.query_status = "idle"
        assert is_query_running(chat_session) is False

    def test_running_status(self, chat_session: ChatSession) -> None:
        chat_session.query_status = "running"
        assert is_query_running(chat_session) is True

    def test_visualizing_status(self, chat_session: ChatSession) -> None:
        chat_session.query_status = "visualizing"
        assert is_query_running(chat_session) is True

    def test_completed_status(self, chat_session: ChatSession) -> None:
        chat_session.query_status = "completed"
        assert is_query_running(chat_session) is False

    def test_error_status(self, chat_session: ChatSession) -> None:
        chat_session.query_status = "error"
        assert is_query_running(chat_session) is False


class TestGetQueryPhase:
    """Tests for get_query_phase function."""

    def test_no_query_thread(self, chat_session: ChatSession) -> None:
        chat_session.query_thread = None
        assert get_query_phase(chat_session) is None

    def test_with_query_thread(self, chat_session: ChatSession, mock_thread: MagicMock) -> None:
        query_thread = QueryThread(mock_thread, "test query", None)
        chat_session.query_thread = query_thread
        assert get_query_phase(chat_session) == "asking"


class TestStartQueryExecution:
    """Tests for start_query_execution function."""

    def test_already_running(self, chat_session: ChatSession, mock_thread: MagicMock) -> None:
        chat_session.query_status = "running"
        result = start_query_execution(chat_session, mock_thread, "test")
        assert result is False

    @patch("databao_cli.ui.services.query_executor.get_script_run_ctx")
    def test_starts_execution(
        self,
        mock_ctx: MagicMock,
        chat_session: ChatSession,
        mock_thread: MagicMock,
        mock_writer: MagicMock,
    ) -> None:
        mock_ctx.return_value = None
        chat_session.writer = mock_writer

        result = start_query_execution(chat_session, mock_thread, "test query")

        assert result is True
        assert chat_session.query_status == "running"
        assert chat_session.query_thread is not None
        mock_writer.clear.assert_called_once()

        # Cleanup
        if chat_session.query_thread and chat_session.query_thread.is_alive():
            chat_session.query_thread.join(timeout=1.0)


class TestCheckQueryCompletion:
    """Tests for check_query_completion function."""

    def test_idle_status_returns_none(self, chat_session: ChatSession) -> None:
        chat_session.query_status = "idle"
        assert check_query_completion(chat_session) is None

    def test_no_query_thread_resets_status(self, chat_session: ChatSession) -> None:
        chat_session.query_status = "running"
        chat_session.query_thread = None
        result = check_query_completion(chat_session)
        assert result is None
        assert chat_session.query_status == "idle"

    def test_thread_finished_returns_result(self, chat_session: ChatSession) -> None:
        # Use a MagicMock to simulate a finished thread
        mock_query_thread = MagicMock(spec=QueryThread)
        mock_query_thread.is_alive.return_value = False
        mock_query_thread.result = QueryResult(
            text="test",
            thinking="",
            result=None,
            has_visualization=False,
        )

        chat_session.query_status = "running"
        chat_session.query_thread = mock_query_thread

        result = check_query_completion(chat_session)

        assert result is not None
        assert result.text == "test"
        assert chat_session.query_status == "completed"
        assert chat_session.query_thread is None

    def test_thread_finished_no_result_creates_error(self, chat_session: ChatSession) -> None:
        mock_query_thread = MagicMock(spec=QueryThread)
        mock_query_thread.is_alive.return_value = False
        mock_query_thread.result = None

        chat_session.query_status = "running"
        chat_session.query_thread = mock_query_thread

        result = check_query_completion(chat_session)

        assert result is not None
        assert result.error == "Thread finished without result"
        assert chat_session.query_status == "error"

    def test_partial_result_transitions_to_visualizing(self, chat_session: ChatSession) -> None:
        """Test that partial_result triggers transition to visualizing status."""
        mock_query_thread = MagicMock(spec=QueryThread)
        mock_query_thread.is_alive.return_value = True
        mock_query_thread.partial_result = QueryResult(
            text="partial",
            thinking="thinking",
            result=None,
            has_visualization=False,
            viz_pending=True,
        )

        chat_session.query_status = "running"
        chat_session.query_thread = mock_query_thread

        result = check_query_completion(chat_session)

        assert result is not None
        assert result.viz_pending is True
        assert chat_session.query_status == "visualizing"
        assert mock_query_thread.partial_result is None  # consumed


class TestStopQuery:
    """Tests for stop_query function."""

    def test_not_running_returns_none(self, chat_session: ChatSession) -> None:
        chat_session.query_status = "idle"
        result = stop_query(chat_session)
        assert result is None

    def test_stop_captures_thinking_text(self, chat_session: ChatSession, mock_writer: MagicMock) -> None:
        chat_session.query_status = "running"
        chat_session.writer = mock_writer
        chat_session.query_thread = None
        chat_session.thread = MagicMock()

        result = stop_query(chat_session)

        assert result == "thinking text"
        assert chat_session.query_status == "idle"
        assert chat_session.thread is None
        assert chat_session.writer is None

    def test_stop_disconnects_writer(self, chat_session: ChatSession, mock_writer: MagicMock) -> None:
        chat_session.query_status = "running"
        chat_session.writer = mock_writer
        chat_session.query_thread = None

        stop_query(chat_session)

        assert mock_writer._on_write is None

    def test_stop_running_thread_raises_interrupt(self, chat_session: ChatSession, mock_writer: MagicMock) -> None:
        """Test that stopping a running thread raises KeyboardInterrupt in it."""
        interrupt_received = threading.Event()

        def blocking_work() -> None:
            try:
                while True:
                    time.sleep(0.01)
            except KeyboardInterrupt:
                interrupt_received.set()

        worker = threading.Thread(target=blocking_work, daemon=True)
        worker.start()

        chat_session.query_status = "running"
        chat_session.writer = mock_writer
        chat_session.query_thread = worker

        stop_query(chat_session)

        # Give time for interrupt to be delivered
        interrupt_received.wait(timeout=2.0)
        assert interrupt_received.is_set()

    def test_stop_resets_chat_state(self, chat_session: ChatSession, mock_writer: MagicMock) -> None:
        chat_session.query_status = "visualizing"
        chat_session.writer = mock_writer
        chat_session.query_thread = None
        chat_session.thread = MagicMock()

        stop_query(chat_session)

        assert chat_session.query_status == "idle"
        assert chat_session.query_thread is None
        assert chat_session.thread is None
        assert chat_session.writer is None


class TestRaiseInThread:
    """Tests for _raise_in_thread function."""

    def test_dead_thread_returns_false(self) -> None:
        thread = threading.Thread(target=lambda: None)
        thread.start()
        thread.join()

        result = _raise_in_thread(thread, KeyboardInterrupt)
        assert result is False

    def test_raises_exception_in_thread(self) -> None:
        exception_caught = threading.Event()

        def wait_for_interrupt() -> None:
            try:
                while True:
                    time.sleep(0.01)
            except KeyboardInterrupt:
                exception_caught.set()

        thread = threading.Thread(target=wait_for_interrupt, daemon=True)
        thread.start()

        time.sleep(0.05)  # Let thread start

        result = _raise_in_thread(thread, KeyboardInterrupt)
        assert result is True

        exception_caught.wait(timeout=2.0)
        assert exception_caught.is_set()


class TestReapThread:
    """Tests for _reap_thread function."""

    def test_thread_stops_gracefully(self) -> None:
        stop_flag = threading.Event()

        def stoppable_work() -> None:
            while not stop_flag.is_set():
                time.sleep(0.01)

        thread = threading.Thread(target=stoppable_work, daemon=True)
        thread.start()

        stop_flag.set()
        _reap_thread(thread, timeout=1.0)

        assert not thread.is_alive()

    def test_thread_force_killed_after_timeout(self) -> None:
        """Test that stubborn threads get SystemExit after timeout."""
        system_exit_received = threading.Event()

        def stubborn_work() -> None:
            try:
                while True:
                    time.sleep(0.01)
            except SystemExit:
                system_exit_received.set()

        thread = threading.Thread(target=stubborn_work, daemon=True)
        thread.start()

        # Use very short timeout to trigger force kill
        _reap_thread(thread, timeout=0.05)

        system_exit_received.wait(timeout=2.0)
        assert system_exit_received.is_set()


class TestQueryThread:
    """Tests for QueryThread class."""

    def test_initial_phase_is_asking(self, mock_thread: MagicMock) -> None:
        query_thread = QueryThread(mock_thread, "test query", None)
        assert query_thread.phase == "asking"

    def test_stores_query(self, mock_thread: MagicMock) -> None:
        query_thread = QueryThread(mock_thread, "my question", None)
        assert query_thread.query == "my question"

    def test_result_initially_none(self, mock_thread: MagicMock) -> None:
        query_thread = QueryThread(mock_thread, "test", None)
        assert query_thread.result is None
        assert query_thread.partial_result is None

    def test_handles_keyboard_interrupt(self, mock_thread: MagicMock) -> None:
        mock_thread.ask.side_effect = KeyboardInterrupt()

        query_thread = QueryThread(mock_thread, "test", None)
        query_thread.run()

        # Should not raise, result stays None
        assert query_thread.result is None

    def test_handles_system_exit(self, mock_thread: MagicMock) -> None:
        mock_thread.ask.side_effect = SystemExit()

        query_thread = QueryThread(mock_thread, "test", None)
        query_thread.run()

        assert query_thread.result is None

    def test_handles_exception(self, mock_thread: MagicMock, mock_writer: MagicMock) -> None:
        mock_thread.ask.side_effect = RuntimeError("test error")

        query_thread = QueryThread(mock_thread, "test", mock_writer)
        query_thread.run()

        assert query_thread.result is not None
        assert query_thread.result.error == "test error"
