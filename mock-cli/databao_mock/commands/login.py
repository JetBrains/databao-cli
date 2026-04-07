from __future__ import annotations

import time
from pathlib import Path

import click
import yaml

_MOCK_TOKEN = "mock_oauth_token_a1b2c3d4"
_MOCK_EMAIL = "artem@databao.app"


def _load_yaml(path: Path) -> dict:
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def _save_yaml(path: Path, data: dict) -> None:
    with open(path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def is_logged_in(project_dir: Path) -> bool:
    databao_yml = project_dir / "databao.yml"
    if not databao_yml.exists():
        return False
    config = _load_yaml(databao_yml)
    return bool(config.get("user", {}).get("token"))


def login_impl(project_dir: Path) -> None:
    databao_yml = project_dir / "databao.yml"

    click.echo("  Opening browser for authentication...")
    click.echo(click.style("  > https://app.databao.app/auth/login", fg="bright_black"))
    click.echo()
    click.echo("  Waiting for authentication...", nl=False)
    time.sleep(2.0)
    click.echo(click.style(" done", fg="green"))
    click.echo()
    click.echo(click.style("  ✓ ", fg="green") + f"Logged in as {click.style(_MOCK_EMAIL, bold=True)}")
    click.echo()

    config = _load_yaml(databao_yml) if databao_yml.exists() else {}
    config["user"] = {"email": _MOCK_EMAIL, "token": _MOCK_TOKEN}
    _save_yaml(databao_yml, config)
