from __future__ import annotations

import shlex
import shutil
import subprocess
from pathlib import Path

import pytest
from _pytest.tmpdir import TempPathFactory

from tests.utils import get_issues_report, run_within_dir


@pytest.fixture(scope="session")
def requirements_txt_dir_with_venv_installed(tmp_path_factory: TempPathFactory) -> Path:
    tmp_path_proj = tmp_path_factory.getbasetemp() / "project_with_requirements_txt"
    shutil.copytree("tests/data/project_with_requirements_txt", str(tmp_path_proj))
    with run_within_dir(tmp_path_proj):
        assert (
            subprocess.check_call(
                shlex.split(
                    "pip install -r requirements.txt -r requirements-dev.txt -r requirements-2.txt -r"
                    " requirements-typing.txt"
                )
            )
            == 0
        )
    return tmp_path_proj


def test_cli_single_requirements_txt(requirements_txt_dir_with_venv_installed: Path) -> None:
    with run_within_dir(requirements_txt_dir_with_venv_installed):
        result = subprocess.run(
            shlex.split(
                "deptry . --requirements-txt requirements.txt --requirements-txt-dev requirements-dev.txt -o"
                " report.json"
            ),
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert get_issues_report() == {
            "misplaced_dev": ["black"],
            "missing": ["white"],
            "obsolete": ["isort", "requests"],
            "transitive": ["urllib3"],
        }


def test_cli_multiple_requirements_txt(requirements_txt_dir_with_venv_installed: Path) -> None:
    with run_within_dir(requirements_txt_dir_with_venv_installed):
        result = subprocess.run(
            shlex.split(
                "deptry . --requirements-txt requirements.txt,requirements-2.txt --requirements-txt-dev"
                " requirements-dev.txt,requirements-typing.txt -o report.json"
            ),
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert get_issues_report() == {
            "misplaced_dev": ["black"],
            "missing": ["white"],
            "obsolete": ["isort", "requests"],
            "transitive": [],
        }
