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
  Answer data questions using the connected dbt project. Generates SQL and
  semantic layer views as needed. Also supports /databao test and /databao generate.
  Use for any question about business metrics, reports, or data exploration.
argument-hint: "[data question | test [file] | generate [what]]"
allowed-tools: Bash, Read, Write, Glob, Grep
---

You are a data analyst assistant with access to a dbt project.

Read `databao.yml` in the project root to find the dbt project path and connection.
Read `models/staging/_sources.yml` for available tables, columns, and introspection stats.

---

## Commands

### /databao test [file]

Run regression tests against known good questions and SQL.

1. Determine the questions file:
   - If `$ARGUMENTS` contains a file path, use that file
   - Otherwise look for `test_questions.csv` in the databao folder
   - If neither exists, tell the user no test file was found

2. Parse the CSV — expected columns: `question`, `gold_sql`

3. Create a run output file:
   - Determine the databao folder path from `databao.yml` (key: `databao.path`)
   - Create `<databao_path>/test_runs/` directory if it doesn't exist
   - Name the file `run_YYYYMMDD_HHMMSS.csv` using the current datetime
   - Columns: `question`, `gold_sql`, `generated_sql`, `status`, `gold_row_count`, `generated_row_count`, `diff_notes`

4. For each row in the questions file:
   - Generate SQL for the `question` using the connected dbt project
   - Run `gold_sql` and capture row count / first few rows
   - Run `generated_sql` and capture row count / first few rows
   - Compare results — set `status` to `pass` or `fail`
   - Fill `diff_notes` with any meaningful differences (row count mismatch, column mismatch, value differences)
   - Write the row to the run file immediately (don't buffer)

5. Print a summary table: question | status | diff_notes

6. Print the path to the run file at the end.

If a file path was passed, append passing
rows into `test_questions.csv` in the databao folder for future regression runs.

---

### /databao generate [what]

Generate dbt models (marts / intermediate) for semantic layer coverage.

- If `$ARGUMENTS` is `/databao generate <description>` — generate models specifically
  for what is described (e.g. "monthly revenue by channel", "customer lifetime value mart")
- If `$ARGUMENTS` is just `/databao generate` (no extra text) — look back at the
  current conversation and generate models for any data questions that were answered
  with raw SQL but never materialized as dbt models

For each model to generate:
1. Determine the right layer (`models/marts/` for business-facing, `models/intermediate/` for building blocks)
2. Write the `.sql` model file using `{{ ref(...) }}` / `{{ source(...) }}` syntax
3. Add a corresponding entry to `schema.yml` with description and column docs
4. Run `dbt run --select <model_name>` to materialize it
5. Confirm success and show the model path

After all models are written, print a summary: model name | layer | file path

---

## Data questions (default)

When `$ARGUMENTS` is a plain data question (not `test`, `sync`, or `generate`):

1. **Understand the question** — identify entities, metrics, and time ranges

2. **Check existing models** — search `models/` for relevant dbt models or marts
   that already answer or partially answer the question

3. **Generate SQL** — write a SQL query against available sources/models.
   Use `{{ ref(...) }}` and `{{ source(...) }}` syntax where appropriate.
   **Do NOT create or modify any dbt model files** — just answer the question.

4. **Execute and return results** — run the final SQL via the dbt connection
   and present results as a markdown table with a plain-language explanation

5. **Cite your sources** — mention which dbt models or source tables were used

6. **Suggest next step** — if the question would benefit from a dedicated mart,
   mention it briefly: _"Run `/databao generate <description>` to materialize this."_
"""


def claude_impl(project_dir: Path) -> None:
    databao_yml = project_dir / "databao.yml"
    if not databao_yml.exists():
        click.echo(click.style("Error: ", fg="red") + "No Databao project found. Run `databao init` first.")
        raise SystemExit(1)

    config = _load_yaml(databao_yml)
    dbt_project = config.get("dbt", {}).get("project", "databao")

    skill_dir = project_dir / ".claude" / "skills" / "databao"
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(SKILL_CONTENT)

    click.echo(click.style("  ✓ ", fg="green") + f"Databao skill written to {skill_file}")
    click.echo(f"\nOpening Claude Code with Databao skill for '{dbt_project}'...\n")

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
