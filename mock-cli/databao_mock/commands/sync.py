from __future__ import annotations

import time
from pathlib import Path

import click
import yaml
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn


def _load_yaml(path: Path) -> dict:
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def sync_impl(project_dir: Path) -> None:
    databao_yml = project_dir / ".databao" / "databao.yml"
    if not databao_yml.exists():
        click.echo(click.style("Error: ", fg="red") + "No Databao project found. Run `databao init` first.")
        raise SystemExit(1)

    config = _load_yaml(databao_yml)
    dbt_path = Path(config.get("dbt", {}).get("path", project_dir))
    project_name = config.get("dbt", {}).get("project", "databao")
    conn_type = config.get("connection", {}).get("type", "database")

    sources_yml = dbt_path / "models" / "staging" / "_sources.yml"
    if not sources_yml.exists():
        click.echo(click.style("Error: ", fg="red") + f"No _sources.yml found at {sources_yml}")
        raise SystemExit(1)

    sources_data = _load_yaml(sources_yml)
    tables: list[str] = []
    for source in sources_data.get("sources", []):
        for table in source.get("tables", []):
            name = table.get("name") if isinstance(table, dict) else table
            if name:
                tables.append(name)

    click.echo(f"\n  Connecting to {conn_type}...", nl=False)
    time.sleep(0.5)
    click.echo(click.style(" connected", fg="green"))
    click.echo(f"  Syncing {len(tables)} tables from '{project_name}'...\n")

    updated_cols = 0
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[cyan]{task.completed}/{task.total}"),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task("  Syncing", total=len(tables))
        for table in tables:
            progress.update(task, description=f"  {table:<35}")
            time.sleep(0.12)
            # Mock: pretend each table has ~6 columns updated
            updated_cols += 6
            progress.advance(task)

    click.echo()

    # Mock: detect 2 new tables not yet in sources
    new_tables = ["abandoned_checkout_line_items", "shop_policies"]
    click.echo(click.style("  ✓ ", fg="green") + f"{len(tables)} tables synced")
    click.echo(click.style("  ✓ ", fg="green") + f"{updated_cols} columns updated")
    if new_tables:
        click.echo(click.style("  ! ", fg="yellow") + f"{len(new_tables)} new tables detected: {', '.join(new_tables)}")
        click.echo(f"    Run `databao init` or add them manually to {sources_yml}")
    click.echo()
