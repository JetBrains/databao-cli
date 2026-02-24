import shutil
import tempfile
from pathlib import Path

import pytest

from utils.path_utils import ARTIFACT_DIR


@pytest.fixture(scope="session", autouse=True)
def prepare_artifacts_dir():
    shutil.rmtree(ARTIFACT_DIR, ignore_errors=True)
    ARTIFACT_DIR.mkdir(exist_ok=True)


@pytest.fixture(autouse=True)
def project_folder(tmp_path: Path) -> Path:
    tmp = Path(tempfile.mkdtemp(dir=ARTIFACT_DIR))
    return tmp
