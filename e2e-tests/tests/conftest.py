import shutil
import tempfile
from pathlib import Path

import pytest
from utils.path_utils import ARTIFACT_DIR


@pytest.fixture(scope="session", autouse=True)
def prepare_artifacts_dir():
    shutil.rmtree(ARTIFACT_DIR, ignore_errors=True)
    ARTIFACT_DIR.mkdir(exist_ok=True)
    ARTIFACT_DIR.is_dir()


@pytest.fixture(autouse=True)
def project_folder(request, tmp_path: Path) -> Path:
    tmp = Path(tempfile.mkdtemp(suffix=request.node.name, dir=ARTIFACT_DIR))
    return tmp
