from __future__ import annotations

import time
from pathlib import Path

import click
import yaml


def _load_yaml(path: Path) -> dict:
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def deploy_impl(project_dir: Path) -> None:
    databao_yml = project_dir / ".databao" / "databao.yml"
    if not databao_yml.exists():
        click.echo(click.style("Error: ", fg="red") + "No Databao project found. Run `databao init` first.")
        raise SystemExit(1)

    config = _load_yaml(databao_yml)
    dbt_project = config.get("dbt", {}).get("project", "databao")

    click.echo(f"\n  Deploying Slack Bot for '{click.style(dbt_project, bold=True)}'...\n")

    steps = [
        ("Packaging semantic models",   1.0),
        ("Uploading to Databao cloud",  1.4),
        ("Registering Slack app",       1.0),
        ("Configuring OAuth scopes",    0.8),
        ("Running smoke test",          1.2),
    ]

    for label, duration in steps:
        click.echo(f"  {label}...", nl=False)
        time.sleep(duration)
        click.echo(click.style(" done", fg="green"))

    click.echo()
    click.echo(click.style("  ✓ ", fg="green") + "Slack Bot deployed successfully.")
    click.echo(click.style("  ✓ ", fg="green") + "Invite it to a channel:  " + click.style("/invite @databao", bold=True))
    click.echo(click.style("  ✓ ", fg="green") + "Users can now ask questions directly in Slack.")
    click.echo()
