from pathlib import Path

import pytest

from databao_cli.features.init.service import init_impl
from databao_cli.shared.project.layout import ProjectLayout


@pytest.fixture
def project_layout(tmp_path: Path) -> ProjectLayout:
    return init_impl(tmp_path)
