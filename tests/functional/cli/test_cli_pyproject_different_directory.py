from __future__ import annotations

import shlex
import shutil
import subprocess
from typing import TYPE_CHECKING

import pytest
from click.testing import CliRunner

from deptry.cli import deptry
from tests.utils import get_issues_report, run_within_dir

if TYPE_CHECKING:
    from pathlib import Path

    from _pytest.tmpdir import TempPathFactory


@pytest.fixture(scope="session")
def pep_621_dir_with_pyproject_different_directory(tmp_path_factory: TempPathFactory) -> Path:
    tmp_path_proj = tmp_path_factory.getbasetemp() / "project_with_pyproject_different_directory"
    shutil.copytree("tests/data/project_with_pyproject_different_directory", str(tmp_path_proj))
    with run_within_dir(tmp_path_proj):
        assert subprocess.check_call(shlex.split("pip install ."), cwd="a_sub_directory") == 0
    return tmp_path_proj


def test_cli_with_pyproject_different_directory(pep_621_dir_with_pyproject_different_directory: Path) -> None:
    with run_within_dir(pep_621_dir_with_pyproject_different_directory):
        result = CliRunner().invoke(deptry, "src --config a_sub_directory/pyproject.toml -o report.json")

        assert result.exit_code == 1
        assert get_issues_report() == {
            "misplaced_dev": [],
            "missing": ["white"],
            "obsolete": ["isort", "requests", "mypy", "pytest"],
            "transitive": [],
        }
