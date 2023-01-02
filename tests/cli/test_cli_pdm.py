import shlex
import shutil
import subprocess
from pathlib import Path

import pytest
from _pytest.tmpdir import TempPathFactory

from tests.utils import get_issues_report, run_within_dir


@pytest.fixture(scope="session")
def pdm_dir_with_venv_installed(tmp_path_factory: TempPathFactory) -> Path:
    tmp_path_proj = tmp_path_factory.getbasetemp() / "project_with_pdm"
    shutil.copytree("tests/data/project_with_pdm", str(tmp_path_proj))
    with run_within_dir(tmp_path_proj):
        assert subprocess.check_call(shlex.split("pip install pdm; pdm install")) == 0
    return tmp_path_proj


def test_cli_with_pdm(pdm_dir_with_venv_installed: Path) -> None:
    with run_within_dir(pdm_dir_with_venv_installed):
        result = subprocess.run(shlex.split("deptry . -o report.json"), capture_output=True, text=True)

        assert result.returncode == 1
        assert get_issues_report() == {
            "misplaced_dev": ["black"],
            "missing": ["white"],
            "obsolete": ["isort", "requests"],
            "transitive": [],
        }
