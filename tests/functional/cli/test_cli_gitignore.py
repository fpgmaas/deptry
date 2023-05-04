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
def dir_with_gitignore(tmp_path_factory: TempPathFactory) -> Path:
    tmp_path_proj = tmp_path_factory.getbasetemp() / "project_with_gitignore"
    shutil.copytree("tests/data/project_with_gitignore", str(tmp_path_proj))
    with run_within_dir(tmp_path_proj):
        assert subprocess.check_call(shlex.split("pip install .")) == 0
    return tmp_path_proj


def test_cli_gitignore_is_used(dir_with_gitignore: Path) -> None:
    with run_within_dir(dir_with_gitignore):
        result = CliRunner().invoke(deptry, shlex.split(". -o report.json"))

        assert result.exit_code == 1
        assert get_issues_report() == {
            "misplaced_dev": [],
            "missing": [],
            "obsolete": ["requests", "mypy", "pytest"],
            "transitive": [],
        }


def test_cli_gitignore_is_not_used(dir_with_gitignore: Path) -> None:
    with run_within_dir(dir_with_gitignore):
        result = CliRunner().invoke(deptry, ". --exclude build/|src/bar.py -o report.json")

        assert result.exit_code == 1
        assert get_issues_report() == {
            "misplaced_dev": [],
            "missing": [],
            "obsolete": ["isort", "requests", "pytest"],
            "transitive": [],
        }
