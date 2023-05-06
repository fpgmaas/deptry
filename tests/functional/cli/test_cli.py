from __future__ import annotations

import os
import shlex
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

from click.testing import CliRunner

from deptry.cli import deptry
from tests.utils import get_issues_report, run_within_dir

if TYPE_CHECKING:
    from tests.functional.types import ToolSpecificProjectBuilder


def test_cli_returns_error(poetry_project_builder: ToolSpecificProjectBuilder) -> None:
    with run_within_dir(poetry_project_builder("example_project")):
        result = CliRunner().invoke(deptry, ". -o report.json")

        assert result.exit_code == 1
        assert get_issues_report() == {
            "misplaced_dev": ["black"],
            "missing": ["white"],
            "obsolete": ["isort", "requests"],
            "transitive": [],
        }


def test_cli_ignore_notebooks(project_builder: ToolSpecificProjectBuilder) -> None:
    with run_within_dir(project_builder("example_project", "poetry install --no-interaction --no-root")):
        result = CliRunner().invoke(deptry, ". --ignore-notebooks -o report.json")

        assert result.exit_code == 1
        assert get_issues_report() == {
            "misplaced_dev": ["black"],
            "missing": ["white"],
            "obsolete": ["toml", "isort", "requests"],
            "transitive": [],
        }


def test_cli_ignore_flags(project_builder: ToolSpecificProjectBuilder) -> None:
    with run_within_dir(project_builder("example_project", "poetry install --no-interaction --no-root")):
        result = CliRunner().invoke(deptry, ". --ignore-obsolete isort,pkginfo,requests -im white -id black")

        assert result.exit_code == 0


def test_cli_skip_flags(project_builder: ToolSpecificProjectBuilder) -> None:
    with run_within_dir(project_builder("example_project", "poetry install --no-interaction --no-root")):
        result = CliRunner().invoke(deptry, ". --skip-obsolete --skip-missing --skip-misplaced-dev --skip-transitive")

        assert result.exit_code == 0


def test_cli_exclude(project_builder: ToolSpecificProjectBuilder) -> None:
    with run_within_dir(project_builder("example_project", "poetry install --no-interaction --no-root")):
        result = CliRunner().invoke(deptry, ". --exclude src/notebook.ipynb -o report.json")

        assert result.exit_code == 1
        assert get_issues_report() == {
            "misplaced_dev": ["black"],
            "missing": ["white"],
            "obsolete": ["toml", "isort", "requests"],
            "transitive": [],
        }


def test_cli_extend_exclude(project_builder: ToolSpecificProjectBuilder) -> None:
    with run_within_dir(project_builder("example_project", "poetry install --no-interaction --no-root")):
        result = CliRunner().invoke(deptry, ". -ee src/notebook.ipynb -o report.json")

        assert result.exit_code == 1
        assert get_issues_report() == {
            "misplaced_dev": ["black"],
            "missing": ["white"],
            "obsolete": ["toml", "isort", "requests"],
            "transitive": [],
        }


def test_cli_known_first_party(project_builder: ToolSpecificProjectBuilder) -> None:
    with run_within_dir(project_builder("example_project", "poetry install --no-interaction --no-root")):
        result = CliRunner().invoke(deptry, ". --known-first-party white -o report.json")

        assert result.exit_code == 1
        assert get_issues_report() == {
            "misplaced_dev": ["black"],
            "missing": [],
            "obsolete": ["isort", "requests"],
            "transitive": [],
        }


def test_cli_not_verbose(project_builder: ToolSpecificProjectBuilder) -> None:
    with run_within_dir(project_builder("example_project", "poetry install --no-interaction --no-root")):
        result = subprocess.run(shlex.split("poetry run deptry . -o report.json"), capture_output=True, text=True)

        assert result.returncode == 1
        assert "The project contains the following dependencies:" not in result.stderr
        assert get_issues_report() == {
            "misplaced_dev": ["black"],
            "missing": ["white"],
            "obsolete": ["isort", "requests"],
            "transitive": [],
        }


def test_cli_verbose(project_builder: ToolSpecificProjectBuilder) -> None:
    with run_within_dir(project_builder("example_project", "poetry install --no-interaction --no-root")):
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


def test_cli_with_not_json_output(project_builder: ToolSpecificProjectBuilder) -> None:
    with run_within_dir(project_builder("example_project", "poetry install --no-interaction --no-root")):
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


def test_cli_with_json_output(project_builder: ToolSpecificProjectBuilder) -> None:
    with run_within_dir(project_builder("example_project", "poetry install --no-interaction --no-root")):
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
