from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import click
import yaml

SKILL_CONTENT = """\
---
name: databao
description: >
  Ask questions about your data in plain English. Databao will query your
  dbt project, write and run SQL, and return results with explanations.
  Use when the user wants to explore data, build reports, or understand metrics.
argument-hint: "[your question about the data]"
allowed-tools: Bash, Read
---

You have access to a Databao project connected to a dbt warehouse.

When the user asks a data question:
1. Run `databao ask --one-shot "$ARGUMENTS"` to query the data
2. Present the results clearly — use tables or bullet points
3. Explain what the numbers mean in plain language
4. If relevant, mention which dbt models were used

To start an interactive data session run `databao ask` without arguments.
"""


def claude_impl(project_dir: Path) -> None:
    # 1. Read databao.yml to confirm project is initialized
    databao_yml = project_dir / "databao.yml"
    if not databao_yml.exists():
        click.echo(click.style("Error: ", fg="red") + "No Databao project found. Run `databao init` first.")
        raise SystemExit(1)

    config = _load_yaml(databao_yml)
    dbt_project = config.get("dbt", {}).get("project", "databao")

    # 2. Write skill file
    skill_dir = project_dir / ".claude" / "skills" / "databao"
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(SKILL_CONTENT)

    click.echo(click.style("  ✓ ", fg="green") + f"Databao skill written to {skill_file}")
    click.echo(f"\nOpening Claude Code with Databao skill for '{dbt_project}'...\n")

    # 3. Launch claude
    result = subprocess.run(["claude"], cwd=project_dir)
    if result.returncode != 0:
        click.echo(click.style("Error: ", fg="red") + "`claude` exited with an error.", err=True)
        sys.exit(result.returncode)


def _load_yaml(path: Path) -> dict:
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}
