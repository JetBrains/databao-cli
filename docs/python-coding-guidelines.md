# Python Coding Guidelines

Rules for writing Python in `databao-cli`. Covers patterns the linter can't
enforce. For style/formatting, run `uv run ruff check --fix && uv run ruff format` and move on.

## Tooling

- Python target: see `requires-python` in `pyproject.toml`.
- Deps managed by `uv` + `pyproject.toml`. No stray `requirements.txt`.
- All commands run via `uv run`. Dev setup: `make setup`.

## CLI Layer (Click)

Commands live in `src/databao_cli/commands/`. Thin handlers delegate to `*_impl()`.

```python
# __main__.py — wiring only
@cli.command()
@click.argument("question", required=False)
@click.option("--one-shot", is_flag=True)
@click.pass_context
def ask(ctx: click.Context, question: str | None, one_shot: bool) -> None:
    """Chat with the Databao agent."""
    from databao_cli.commands.ask import ask_impl
    ask_impl(ctx, question, one_shot)
```

- Keep `__main__.py` scannable — no logic, just registrations.
- Shared state travels in `ctx.obj` (dict), set on the root group.
- Use Click's type system (`click.Path`, `click.Choice`) over manual parsing.
- User-facing output: `click.echo` / `click.secho`, not `print`.
- For user-facing errors (bad input or broken state), emit a clear
  `click.echo(..., err=True)` message and then `sys.exit(1)`.

## Error Handling

Don't blanket `try/except`. When you do catch, catch narrow.

```python
# bad — swallows everything, hides bugs
try:
    result = build_context(project)
except Exception:
    logger.error("build failed")

# good — catch what you expect, let the rest crash
try:
    result = build_context(project)
except ContextBuildError as e:
    click.echo(f"Build failed: {e}", err=True)
    sys.exit(1)
```

Define domain exceptions when the caller needs to distinguish failure modes:

```python
class InitDatabaoProjectError(ValueError):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

class DatabaoProjectDirAlreadyExistsError(InitDatabaoProjectError): ...
```

Rules:
- Validate early, before expensive work.
- Exception messages must be actionable — include the path, value, or state
  that caused the problem.
- Never `except Exception: pass`. If you're tempted, you're missing a design
  decision.
- `RuntimeError` for "should never happen" states. `ValueError` for bad input.
  `FileNotFoundError` for missing paths.

## Data Modelling

Dataclasses for internal data. Pydantic for validation boundaries (API input,
MCP tool params).

```python
# internal state — plain dataclass
@dataclass
class ChatMessage:
    role: str
    content: str
    thinking: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)

# immutable layout — frozen dataclass
@dataclass(frozen=True)
class ProjectLayout:
    project_dir: Path

    @property
    def databao_dir(self) -> Path:
        return get_databao_project_dir(self.project_dir)

# MCP tool params — Pydantic for schema generation
class Message(BaseModel):
    role: str = Field(description="Message role: 'user' or 'assistant'")
    content: str = Field(description="Message text content")
```

- Use `field(default_factory=...)` for mutable defaults. Always.
- Prefer `@property` for derived values on dataclasses.
- Serialization helpers (`to_dict` / `from_dict`) live on the class, not in
  utility modules.

## Type Hints

Strict mypy is on. No shortcuts.

- `X | None`, not `Optional[X]`.
- All public functions get full signatures. Internal helpers get at least
  return types.
- Use `TYPE_CHECKING` to break circular imports:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from databao.agent.core.thread import Thread
```

- Forward refs (`"Settings"`) for self-referencing classmethods.

## Imports

- No import-time side effects. Heavy imports go inside functions:

```python
def ask_impl(...):
    from databao_cli.executor_utils import build_llm_config  # lazy
    llm_config = build_llm_config(model)
```

- This keeps `__main__.py` fast and avoids pulling Streamlit / heavy deps
  into CLI-only paths.

## Enums for Finite States

```python
class DatabaoProjectStatus(Enum):
    VALID = "valid"
    NO_DATASOURCES = "no_datasources"
    NOT_INITIALIZED = "not_initialized"
```

Don't use string literals for states that have a fixed set of values.
Enums give you typo protection and exhaustiveness hints.

## Concurrency

This project uses threading, not asyncio. Streamlit doesn't play well with
event loops.

- `ThreadPoolExecutor` for background tasks (builds).
- Custom `Thread` subclasses for query execution with result storage.
- Thread-safe IO: `threading.Lock` around shared buffers.
- Streamlit polling: `@st.fragment(run_every=...)`, not busy loops.

## MCP Tools

Tools live in `src/databao_cli/mcp/tools/`. Each tool module exports a
`register(mcp, context)` function.

```python
def register(mcp: "FastMCP", context: "McpContext") -> None:
    @mcp.tool()
    def databao_ask(
        messages: Annotated[list[Message], Field(description="...")],
    ) -> str:
        request_id = str(uuid6())
        try:
            ...
            return json.dumps(result, default=str)
        # Broad catch is acceptable here at the MCP tool boundary so we can
        # always return a structured error JSON instead of crashing the server.
        # Inside the codebase, avoid blanket `except Exception` without re-raise.
        except Exception as e:
            logger.exception("[%s] Query failed", request_id)
            return _error(f"Query failed: {e}", request_id=request_id)
```

- Tools return JSON strings. Errors are JSON too (`{"error": "...", "request_id": "..."}`).
- Tag logs with `request_id` for traceability.
- Validate project state before doing work (not initialized? no datasources?
  no build output?).

## Logging

```python
logger = logging.getLogger(__name__)
```

- `logging` for runtime diagnostics. `click.echo` for user output. Don't mix.
- Log at `DEBUG` for internal flow, `INFO` for operations, `WARNING` for
  recoverable issues, `ERROR`/`EXCEPTION` for failures.
- LLM provider errors go through `log/llm_errors.py` formatter chain.
- Never log secrets, API keys, or full response bodies at INFO+.

## Project-Aware Code

Almost every command starts by locating and validating the project:

```python
project = ProjectLayout(project_path)
status = databao_project_status(project)
if status == DatabaoProjectStatus.NOT_INITIALIZED:
    click.echo("No project found. Run 'databao init'.", err=True)
    sys.exit(1)
```

This is the pattern. Don't skip validation. Don't invent a new way to find
the project directory.

## Things to Avoid

- `except Exception` / `except BaseException` without re-raise.
- Mutable default arguments (use `field(default_factory=...)`).
- `os.path` when `pathlib.Path` works (it always does).
- Raw `dict` for structured data that gets passed around — make a dataclass.
- `asyncio.run()` in Streamlit code paths — use threads.
- Putting logic in `__main__.py` — it's a wiring file.
- `requirements.txt`, `setup.py`, or any non-`pyproject.toml` dep files.
