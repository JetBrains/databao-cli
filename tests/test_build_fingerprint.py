"""Tests for build fingerprint detection and new-build notification logic."""

import os
from pathlib import Path

import pytest

from databao_cli.project.layout import BUILD_SENTINEL, ProjectLayout
from databao_cli.ui.project_utils import get_build_fingerprint


@pytest.fixture
def project_with_sentinel(tmp_path: Path) -> ProjectLayout:
    """Create a minimal project layout with a build sentinel file."""
    domain_dir = tmp_path / "databao" / "domains" / "root"
    domain_dir.mkdir(parents=True)
    (domain_dir / BUILD_SENTINEL).write_text("")
    return ProjectLayout(tmp_path)


def test_fingerprint_returns_zero_without_sentinel(tmp_path: Path) -> None:
    """Fingerprint is 0.0 when the sentinel file does not exist."""
    domain_dir = tmp_path / "databao" / "domains" / "root"
    domain_dir.mkdir(parents=True)
    project = ProjectLayout(tmp_path)
    assert get_build_fingerprint(project) == 0.0


def test_fingerprint_returns_zero_for_missing_domain(tmp_path: Path) -> None:
    """Fingerprint is 0.0 when the domain directory does not exist."""
    project = ProjectLayout(tmp_path)
    assert get_build_fingerprint(project) == 0.0


def test_fingerprint_returns_nonzero_with_sentinel(
    project_with_sentinel: ProjectLayout,
) -> None:
    """Fingerprint is positive when sentinel file exists."""
    fp = get_build_fingerprint(project_with_sentinel)
    assert fp > 0.0


def test_fingerprint_changes_after_new_build(
    project_with_sentinel: ProjectLayout,
) -> None:
    """Fingerprint changes when sentinel is rewritten (simulating a new build)."""
    fp_before = get_build_fingerprint(project_with_sentinel)

    sentinel = project_with_sentinel.root_domain_dir / BUILD_SENTINEL
    os.utime(sentinel, (fp_before + 10, fp_before + 10))

    fp_after = get_build_fingerprint(project_with_sentinel)
    assert fp_after > fp_before


def test_fingerprint_stable_without_changes(
    project_with_sentinel: ProjectLayout,
) -> None:
    """Fingerprint is stable when sentinel is not rewritten."""
    fp1 = get_build_fingerprint(project_with_sentinel)
    fp2 = get_build_fingerprint(project_with_sentinel)
    assert fp1 == fp2
