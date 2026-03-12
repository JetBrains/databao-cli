from __future__ import annotations

import shutil
from pathlib import Path

import click
import yaml

VERSION = "0.1.0"

# Each entry is (text, color | None, bold)
BAO_ART: list[list[tuple[str, str | None, bool]]] = [
    [("     ╭─────────╮  ", "magenta", False)],
    [("    ╭╯  ", "magenta", False), ("◕   ◕", "white", False), ("  ╰╮ ", "magenta", False)],
    [("    │    ", "magenta", False), ("╰ω╯", "white", True), ("    │ ", "magenta", False)],
    [("    │  ", "magenta", False), ("databao", "green", True), ("  │ ", "magenta", False)],
    [("    ╰╮         ╭╯ ", "magenta", False)],
    [("     ╰─────────╯  ", "magenta", False)],
    [("      ░░░░░░░░░   ", "magenta", False)],
]


def _load_yaml(path: Path) -> dict:
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def _project_subtitle(project_dir: Path) -> str:
    databao_yml = project_dir / "databao.yml"
    if not databao_yml.exists():
        return str(project_dir)
    config = _load_yaml(databao_yml)
    dbt_name = config.get("dbt", {}).get("project")
    conn_type = config.get("connection", {}).get("type")
    parts = [f"~/{project_dir.name}"]
    if dbt_name:
        parts.append(f"dbt:{dbt_name}")
    if conn_type:
        parts.append(conn_type)
    return "  ·  ".join(parts)


def _render_art_line(segments: list[tuple[str, str | None, bool]]) -> str:
    return "".join(click.style(text, fg=color, bold=bold) for text, color, bold in segments)


def _plain_len(segments: list[tuple[str, str | None, bool]]) -> int:
    return sum(len(text) for text, _, _ in segments)


def print_header(project_dir: Path) -> None:
    term_width = shutil.get_terminal_size((80, 20)).columns
    box_width = min(term_width - 2, 56)
    inner = box_width - 2

    subtitle = _project_subtitle(project_dir)
    title = f" Databao v{VERSION} "

    def border_row(content_plain: str) -> str:
        padded = content_plain.center(inner)
        return click.style("│", fg="bright_black") + padded + click.style("│", fg="bright_black")

    def colored_border_row(segments: list[tuple[str, str | None, bool]]) -> str:
        plain_len = _plain_len(segments)
        pad_total = inner - plain_len
        left = pad_total // 2
        right = pad_total - left
        return (
            click.style("│", fg="bright_black")
            + " " * left
            + _render_art_line(segments)
            + " " * right
            + click.style("│", fg="bright_black")
        )

    left_dashes = 3
    right_dashes = box_width - left_dashes - len(title) - 2
    top = (
        click.style("╭" + "─" * left_dashes, fg="bright_black")
        + click.style(title, fg="magenta", bold=True)
        + click.style("─" * right_dashes + "╮", fg="bright_black")
    )
    bottom = click.style("╰" + "─" * (box_width - 2) + "╯", fg="bright_black")

    print(top)
    print(border_row(""))
    for segments in BAO_ART:
        print(colored_border_row(segments))
    print(border_row(""))
    print(colored_border_row([(subtitle, "cyan", False)]))
    print(border_row(""))
    print(bottom)
    print()
