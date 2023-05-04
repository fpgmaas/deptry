from __future__ import annotations

import os
import shlex
import shutil
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from click.testing import CliRunner

from deptry.cli import deptry
from tests.utils import get_issues_report, run_within_dir

if TYPE_CHECKING:
    from _pytest.tmpdir import TempPathFactory


@pytest.fixture(scope="session")
def dir_with_venv_installed(tmp_path_factory: TempPathFactory) -> Path:
    tmp_path_proj = tmp_path_factory.getbasetemp() / "example_project"
    shutil.copytree("tests/data/example_project", tmp_path_proj)
    with run_within_dir(tmp_path_proj):
        assert subprocess.check_call(shlex.split("poetry install --no-interaction --no-root")) == 0
    return tmp_path_proj


def test_cli_returns_error(dir_with_venv_installed: Path) -> None:
    with run_within_dir(dir_with_venv_installed):
        result = CliRunner().invoke(deptry, ". -o report.json")

        assert result.exit_code == 1
        assert get_issues_report() == {
            "misplaced_dev": ["black"],
            "missing": ["white"],
            "obsolete": ["isort", "requests"],
            "transitive": [],
        }


def test_cli_ignore_notebooks(dir_with_venv_installed: Path) -> None:
    with run_within_dir(dir_with_venv_installed):
        result = CliRunner().invoke(deptry, ". --ignore-notebooks -o report.json")

        assert result.exit_code == 1
        assert get_issues_report() == {
            "misplaced_dev": ["black"],
            "missing": ["white"],
            "obsolete": ["toml", "isort", "requests"],
            "transitive": [],
        }


def test_cli_ignore_flags(dir_with_venv_installed: Path) -> None:
    with run_within_dir(dir_with_venv_installed):
        result = CliRunner().invoke(deptry, ". --ignore-obsolete isort,pkginfo,requests -im white -id black")

        assert result.exit_code == 0


def test_cli_skip_flags(dir_with_venv_installed: Path) -> None:
    with run_within_dir(dir_with_venv_installed):
        result = CliRunner().invoke(deptry, ". --skip-obsolete --skip-missing --skip-misplaced-dev --skip-transitive")

        assert result.exit_code == 0


def test_cli_exclude(dir_with_venv_installed: Path) -> None:
    with run_within_dir(dir_with_venv_installed):
        result = CliRunner().invoke(deptry, ". --exclude src/notebook.ipynb -o report.json")

        assert result.exit_code == 1
        assert get_issues_report() == {
            "misplaced_dev": ["black"],
            "missing": ["white"],
            "obsolete": ["toml", "isort", "requests"],
            "transitive": [],
        }


def test_cli_extend_exclude(dir_with_venv_installed: Path) -> None:
    with run_within_dir(dir_with_venv_installed):
        result = CliRunner().invoke(deptry, ". -ee src/notebook.ipynb -o report.json")

        assert result.exit_code == 1
        assert get_issues_report() == {
            "misplaced_dev": ["black"],
            "missing": ["white"],
            "obsolete": ["toml", "isort", "requests"],
            "transitive": [],
        }


def test_cli_known_first_party(dir_with_venv_installed: Path) -> None:
    with run_within_dir(dir_with_venv_installed):
        result = CliRunner().invoke(deptry, ". --known-first-party white -o report.json")

        assert result.exit_code == 1
        assert get_issues_report() == {
            "misplaced_dev": ["black"],
            "missing": [],
            "obsolete": ["isort", "requests"],
            "transitive": [],
        }


def test_cli_not_verbose(dir_with_venv_installed: Path) -> None:
    with run_within_dir(dir_with_venv_installed):
        result = subprocess.run(shlex.split("poetry run deptry . -o report.json"), capture_output=True, text=True)

        assert result.returncode == 1
        assert "The project contains the following dependencies:" not in result.stderr
        assert get_issues_report() == {
            "misplaced_dev": ["black"],
            "missing": ["white"],
            "obsolete": ["isort", "requests"],
            "transitive": [],
        }


def test_cli_verbose(dir_with_venv_installed: Path) -> None:
    with run_within_dir(dir_with_venv_installed):
        result = subprocess.run(
            shlex.split("poetry run deptry . --verbose -o report.json"), capture_output=True, text=True
        )

        assert result.returncode == 1
        assert "The project contains the following dependencies:" in result.stderr
        assert get_issues_report() == {
            "misplaced_dev": ["black"],
            "missing": ["white"],
            "obsolete": ["isort", "requests"],
            "transitive": [],
        }


def test_cli_with_not_json_output(dir_with_venv_installed: Path) -> None:
    with run_within_dir(dir_with_venv_installed):
        # Remove previously generated `report.json`.
        os.remove("report.json")

        result = subprocess.run(shlex.split("poetry run deptry ."), capture_output=True, text=True)

        assert result.returncode == 1
        assert len(list(Path(".").glob("*.json"))) == 0
        assert (
            "The project contains obsolete dependencies:\n\n\tisort\n\trequests\n\nConsider removing them from your"
            " project's dependencies. If a package is used for development purposes, you should add it to your"
            " development dependencies instead.\n\n-----------------------------------------------------\n\nThere are"
            " dependencies missing from the project's list of dependencies:\n\n\twhite\n\nConsider adding them to your"
            " project's dependencies. \n\n-----------------------------------------------------\n\nThere are imported"
            " modules from development dependencies detected:\n\n\tblack\n\n"
            in result.stderr
        )


def test_cli_with_json_output(dir_with_venv_installed: Path) -> None:
    with run_within_dir(dir_with_venv_installed):
        result = subprocess.run(shlex.split("poetry run deptry . -o deptry.json"), capture_output=True, text=True)

        # Assert that we still write to console when generating a JSON report.
        assert (
            "The project contains obsolete dependencies:\n\n\tisort\n\trequests\n\nConsider removing them from your"
            " project's dependencies. If a package is used for development purposes, you should add it to your"
            " development dependencies instead.\n\n-----------------------------------------------------\n\nThere are"
            " dependencies missing from the project's list of dependencies:\n\n\twhite\n\nConsider adding them to your"
            " project's dependencies. \n\n-----------------------------------------------------\n\nThere are imported"
            " modules from development dependencies detected:\n\n\tblack\n\n"
            in result.stderr
        )
        assert get_issues_report("deptry.json") == {
            "misplaced_dev": ["black"],
            "missing": ["white"],
            "obsolete": ["isort", "requests"],
            "transitive": [],
        }


def test_cli_help() -> None:
    result = CliRunner().invoke(deptry, "--help")

    assert result.exit_code == 0
