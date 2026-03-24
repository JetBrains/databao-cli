"""Tests for build fingerprint and sentinel (DBA-136)."""

import os
import time
from pathlib import Path

import pytest

from databao_cli.ui.project_utils import BUILD_SENTINEL, get_build_fingerprint, write_build_sentinel


@pytest.fixture
def domain_dir(tmp_path: Path) -> Path:
    """Create a minimal domain directory structure."""
    domain = tmp_path / "domain"
    domain.mkdir()
    return domain


# -- get_build_fingerprint --


def test_no_output_dir(domain_dir: Path) -> None:
    """Returns 0.0 when the output directory does not exist."""
    assert get_build_fingerprint(domain_dir) == 0.0


def test_output_dir_without_sentinel(domain_dir: Path) -> None:
    """Returns 0.0 when output dir exists but sentinel is missing."""
    (domain_dir / "output").mkdir()
    (domain_dir / "output" / "ds.yaml").write_text("tables: []")
    assert get_build_fingerprint(domain_dir) == 0.0


def test_fingerprint_from_sentinel(domain_dir: Path) -> None:
    """Returns the mtime of the sentinel file."""
    output = domain_dir / "output"
    output.mkdir()
    sentinel = output / BUILD_SENTINEL
    sentinel.touch()
    expected = sentinel.stat().st_mtime
    assert get_build_fingerprint(domain_dir) == expected


def test_fingerprint_changes_after_rebuild(domain_dir: Path) -> None:
    """Fingerprint changes when sentinel is re-touched (simulating rebuild)."""
    output = domain_dir / "output"
    output.mkdir()
    sentinel = output / BUILD_SENTINEL
    sentinel.touch()

    fp1 = get_build_fingerprint(domain_dir)

    # Explicitly set a future mtime to avoid filesystem granularity issues.
    future = fp1 + 10
    os.utime(sentinel, (future, future))

    fp2 = get_build_fingerprint(domain_dir)
    assert fp2 > fp1


# -- write_build_sentinel --


def test_write_sentinel_creates_file(domain_dir: Path) -> None:
    """write_build_sentinel creates the sentinel (and output dir if needed)."""
    write_build_sentinel(domain_dir)
    sentinel = domain_dir / "output" / BUILD_SENTINEL
    assert sentinel.is_file()


def test_write_sentinel_updates_mtime(domain_dir: Path) -> None:
    """Calling write_build_sentinel again updates the sentinel mtime."""
    write_build_sentinel(domain_dir)
    sentinel = domain_dir / "output" / BUILD_SENTINEL
    fp1 = sentinel.stat().st_mtime

    # Set an old mtime, then re-touch via write_build_sentinel.
    past = fp1 - 100
    os.utime(sentinel, (past, past))
    assert sentinel.stat().st_mtime < fp1

    write_build_sentinel(domain_dir)
    fp2 = sentinel.stat().st_mtime
    assert fp2 >= fp1


def test_fingerprint_round_trip(domain_dir: Path) -> None:
    """get_build_fingerprint returns 0 before write, non-zero after."""
    assert get_build_fingerprint(domain_dir) == 0.0
    write_build_sentinel(domain_dir)
    assert get_build_fingerprint(domain_dir) > 0.0
