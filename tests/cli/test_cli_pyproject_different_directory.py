import shlex
import shutil
import subprocess
from pathlib import Path

import pytest
from _pytest.tmpdir import TempPathFactory

from tests.utils import get_issues_report, run_within_dir


@pytest.fixture(scope="session")
def pep_621_dir_with_pyproject_different_directory(tmp_path_factory: TempPathFactory) -> Path:
    tmp_path_proj = tmp_path_factory.getbasetemp() / "project_with_pyproject_different_directory"
    shutil.copytree("tests/data/project_with_pyproject_different_directory", str(tmp_path_proj))
    with run_within_dir(tmp_path_proj):
        assert subprocess.check_call(shlex.split("pip install ."), cwd="a_sub_directory") == 0
    return tmp_path_proj


def test_cli_with_pyproject_different_directory(pep_621_dir_with_pyproject_different_directory: Path) -> None:
    with run_within_dir(pep_621_dir_with_pyproject_different_directory):
        result = subprocess.run(
            shlex.split("deptry --config a_sub_directory/pyproject.toml src -o report.json"),
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert get_issues_report() == {
            "misplaced_dev": [],
            "missing": ["white"],
            "obsolete": ["isort", "requests", "mypy", "pytest"],
            "transitive": [],
        }
