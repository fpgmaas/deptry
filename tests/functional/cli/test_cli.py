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
        assert get_issues_report() == [
            {
                "error": {
                    "code": "DEP002",
                    "message": "isort defined as a dependency but not used in the codebase",
                },
                "module": "isort",
                "location": {
                    "file": str(Path("pyproject.toml")),
                    "line": None,
                    "column": None,
                },
            },
            {
                "error": {
                    "code": "DEP002",
                    "message": "requests defined as a dependency but not used in the codebase",
                },
                "module": "requests",
                "location": {
                    "file": str(Path("pyproject.toml")),
                    "line": None,
                    "column": None,
                },
            },
            {
                "error": {
                    "code": "DEP004",
                    "message": "black imported but declared as a dev dependency",
                },
                "module": "black",
                "location": {
                    "file": str(Path("src/main.py")),
                    "line": 4,
                    "column": 0,
                },
            },
            {
                "error": {
                    "code": "DEP001",
                    "message": "white imported but missing from the dependency definitions",
                },
                "module": "white",
                "location": {
                    "file": str(Path("src/main.py")),
                    "line": 6,
                    "column": 0,
                },
            },
        ]


def test_cli_ignore_notebooks(project_builder: ToolSpecificProjectBuilder) -> None:
    with run_within_dir(project_builder("example_project", "poetry install --no-interaction --no-root")):
        result = CliRunner().invoke(deptry, ". --ignore-notebooks -o report.json")

        assert result.exit_code == 1
        assert get_issues_report() == [
            {
                "error": {
                    "code": "DEP002",
                    "message": "toml defined as a dependency but not used in the codebase",
                },
                "module": "toml",
                "location": {
                    "file": str(Path("pyproject.toml")),
                    "line": None,
                    "column": None,
                },
            },
            {
                "error": {
                    "code": "DEP002",
                    "message": "isort defined as a dependency but not used in the codebase",
                },
                "module": "isort",
                "location": {
                    "file": str(Path("pyproject.toml")),
                    "line": None,
                    "column": None,
                },
            },
            {
                "error": {
                    "code": "DEP002",
                    "message": "requests defined as a dependency but not used in the codebase",
                },
                "module": "requests",
                "location": {
                    "file": str(Path("pyproject.toml")),
                    "line": None,
                    "column": None,
                },
            },
            {
                "error": {
                    "code": "DEP004",
                    "message": "black imported but declared as a dev dependency",
                },
                "module": "black",
                "location": {
                    "file": str(Path("src/main.py")),
                    "line": 4,
                    "column": 0,
                },
            },
            {
                "error": {
                    "code": "DEP001",
                    "message": "white imported but missing from the dependency definitions",
                },
                "module": "white",
                "location": {
                    "file": str(Path("src/main.py")),
                    "line": 6,
                    "column": 0,
                },
            },
        ]


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
        assert get_issues_report() == [
            {
                "error": {
                    "code": "DEP002",
                    "message": "toml defined as a dependency but not used in the codebase",
                },
                "module": "toml",
                "location": {
                    "file": str(Path("pyproject.toml")),
                    "line": None,
                    "column": None,
                },
            },
            {
                "error": {
                    "code": "DEP002",
                    "message": "isort defined as a dependency but not used in the codebase",
                },
                "module": "isort",
                "location": {
                    "file": str(Path("pyproject.toml")),
                    "line": None,
                    "column": None,
                },
            },
            {
                "error": {
                    "code": "DEP002",
                    "message": "requests defined as a dependency but not used in the codebase",
                },
                "module": "requests",
                "location": {
                    "file": str(Path("pyproject.toml")),
                    "line": None,
                    "column": None,
                },
            },
            {
                "error": {
                    "code": "DEP004",
                    "message": "black imported but declared as a dev dependency",
                },
                "module": "black",
                "location": {
                    "file": str(Path("src/main.py")),
                    "line": 4,
                    "column": 0,
                },
            },
            {
                "error": {
                    "code": "DEP001",
                    "message": "white imported but missing from the dependency definitions",
                },
                "module": "white",
                "location": {
                    "file": str(Path("src/main.py")),
                    "line": 6,
                    "column": 0,
                },
            },
        ]


def test_cli_extend_exclude(project_builder: ToolSpecificProjectBuilder) -> None:
    with run_within_dir(project_builder("example_project", "poetry install --no-interaction --no-root")):
        result = CliRunner().invoke(deptry, ". -ee src/notebook.ipynb -o report.json")

        assert result.exit_code == 1
        assert get_issues_report() == [
            {
                "error": {
                    "code": "DEP002",
                    "message": "toml defined as a dependency but not used in the codebase",
                },
                "module": "toml",
                "location": {
                    "file": str(Path("pyproject.toml")),
                    "line": None,
                    "column": None,
                },
            },
            {
                "error": {
                    "code": "DEP002",
                    "message": "isort defined as a dependency but not used in the codebase",
                },
                "module": "isort",
                "location": {
                    "file": str(Path("pyproject.toml")),
                    "line": None,
                    "column": None,
                },
            },
            {
                "error": {
                    "code": "DEP002",
                    "message": "requests defined as a dependency but not used in the codebase",
                },
                "module": "requests",
                "location": {
                    "file": str(Path("pyproject.toml")),
                    "line": None,
                    "column": None,
                },
            },
            {
                "error": {
                    "code": "DEP004",
                    "message": "black imported but declared as a dev dependency",
                },
                "module": "black",
                "location": {
                    "file": str(Path("src/main.py")),
                    "line": 4,
                    "column": 0,
                },
            },
            {
                "error": {
                    "code": "DEP001",
                    "message": "white imported but missing from the dependency definitions",
                },
                "module": "white",
                "location": {
                    "file": str(Path("src/main.py")),
                    "line": 6,
                    "column": 0,
                },
            },
        ]


def test_cli_known_first_party(project_builder: ToolSpecificProjectBuilder) -> None:
    with run_within_dir(project_builder("example_project", "poetry install --no-interaction --no-root")):
        result = CliRunner().invoke(deptry, ". --known-first-party white -o report.json")

        assert result.exit_code == 1
        assert get_issues_report() == [
            {
                "error": {
                    "code": "DEP002",
                    "message": "isort defined as a dependency but not used in the codebase",
                },
                "module": "isort",
                "location": {
                    "file": str(Path("pyproject.toml")),
                    "line": None,
                    "column": None,
                },
            },
            {
                "error": {
                    "code": "DEP002",
                    "message": "requests defined as a dependency but not used in the codebase",
                },
                "module": "requests",
                "location": {
                    "file": str(Path("pyproject.toml")),
                    "line": None,
                    "column": None,
                },
            },
            {
                "error": {
                    "code": "DEP004",
                    "message": "black imported but declared as a dev dependency",
                },
                "module": "black",
                "location": {
                    "file": str(Path("src/main.py")),
                    "line": 4,
                    "column": 0,
                },
            },
        ]


def test_cli_not_verbose(project_builder: ToolSpecificProjectBuilder) -> None:
    with run_within_dir(project_builder("example_project", "poetry install --no-interaction --no-root")):
        result = subprocess.run(shlex.split("poetry run deptry . -o report.json"), capture_output=True, text=True)

        assert result.returncode == 1
        assert "The project contains the following dependencies:" not in result.stderr
        assert get_issues_report() == [
            {
                "error": {
                    "code": "DEP002",
                    "message": "isort defined as a dependency but not used in the codebase",
                },
                "module": "isort",
                "location": {
                    "file": str(Path("pyproject.toml")),
                    "line": None,
                    "column": None,
                },
            },
            {
                "error": {
                    "code": "DEP002",
                    "message": "requests defined as a dependency but not used in the codebase",
                },
                "module": "requests",
                "location": {
                    "file": str(Path("pyproject.toml")),
                    "line": None,
                    "column": None,
                },
            },
            {
                "error": {
                    "code": "DEP004",
                    "message": "black imported but declared as a dev dependency",
                },
                "module": "black",
                "location": {
                    "file": str(Path("src/main.py")),
                    "line": 4,
                    "column": 0,
                },
            },
            {
                "error": {
                    "code": "DEP001",
                    "message": "white imported but missing from the dependency definitions",
                },
                "module": "white",
                "location": {
                    "file": str(Path("src/main.py")),
                    "line": 6,
                    "column": 0,
                },
            },
        ]


def test_cli_verbose(project_builder: ToolSpecificProjectBuilder) -> None:
    with run_within_dir(project_builder("example_project", "poetry install --no-interaction --no-root")):
        result = subprocess.run(
            shlex.split("poetry run deptry . --verbose -o report.json"), capture_output=True, text=True
        )

        assert result.returncode == 1
        assert "The project contains the following dependencies:" in result.stderr
        assert get_issues_report() == [
            {
                "error": {
                    "code": "DEP002",
                    "message": "isort defined as a dependency but not used in the codebase",
                },
                "module": "isort",
                "location": {
                    "file": str(Path("pyproject.toml")),
                    "line": None,
                    "column": None,
                },
            },
            {
                "error": {
                    "code": "DEP002",
                    "message": "requests defined as a dependency but not used in the codebase",
                },
                "module": "requests",
                "location": {
                    "file": str(Path("pyproject.toml")),
                    "line": None,
                    "column": None,
                },
            },
            {
                "error": {
                    "code": "DEP004",
                    "message": "black imported but declared as a dev dependency",
                },
                "module": "black",
                "location": {
                    "file": str(Path("src/main.py")),
                    "line": 4,
                    "column": 0,
                },
            },
            {
                "error": {
                    "code": "DEP001",
                    "message": "white imported but missing from the dependency definitions",
                },
                "module": "white",
                "location": {
                    "file": str(Path("src/main.py")),
                    "line": 6,
                    "column": 0,
                },
            },
        ]


def test_cli_with_not_json_output(project_builder: ToolSpecificProjectBuilder) -> None:
    with run_within_dir(project_builder("example_project", "poetry install --no-interaction --no-root")):
        # Remove previously generated `report.json`.
        os.remove("report.json")

        result = subprocess.run(shlex.split("poetry run deptry ."), capture_output=True, text=True)

        assert result.returncode == 1
        assert len(list(Path(".").glob("*.json"))) == 0
        assert (
            result.stderr
            == f"Scanning 2 files...\n\n{str(Path('pyproject.toml'))}: DEP002 isort defined as a dependency but not"
            f" used in the codebase\n{str(Path('pyproject.toml'))}: DEP002 requests defined as a dependency but not"
            f" used in the codebase\n{str(Path('src/main.py'))}:4:0: DEP004 black imported but declared as a dev"
            f" dependency\n{str(Path('src/main.py'))}:6:0: DEP001 white imported but missing from the dependency"
            " definitions\nFound 4 dependency issues.\n\nFor more information, see the documentation:"
            " https://fpgmaas.github.io/deptry/\n"
        )


def test_cli_with_json_output(project_builder: ToolSpecificProjectBuilder) -> None:
    with run_within_dir(project_builder("example_project", "poetry install --no-interaction --no-root")):
        result = subprocess.run(shlex.split("poetry run deptry . -o deptry.json"), capture_output=True, text=True)

        # Assert that we still write to console when generating a JSON report.
        assert (
            result.stderr
            == f"Scanning 2 files...\n\n{str(Path('pyproject.toml'))}: DEP002 isort defined as a dependency but not"
            f" used in the codebase\n{str(Path('pyproject.toml'))}: DEP002 requests defined as a dependency but not"
            f" used in the codebase\n{str(Path('src/main.py'))}:4:0: DEP004 black imported but declared as a dev"
            f" dependency\n{str(Path('src/main.py'))}:6:0: DEP001 white imported but missing from the dependency"
            " definitions\nFound 4 dependency issues.\n\nFor more information, see the documentation:"
            " https://fpgmaas.github.io/deptry/\n"
        )
        assert get_issues_report("deptry.json") == [
            {
                "error": {
                    "code": "DEP002",
                    "message": "isort defined as a dependency but not used in the codebase",
                },
                "module": "isort",
                "location": {
                    "file": str(Path("pyproject.toml")),
                    "line": None,
                    "column": None,
                },
            },
            {
                "error": {
                    "code": "DEP002",
                    "message": "requests defined as a dependency but not used in the codebase",
                },
                "module": "requests",
                "location": {
                    "file": str(Path("pyproject.toml")),
                    "line": None,
                    "column": None,
                },
            },
            {
                "error": {
                    "code": "DEP004",
                    "message": "black imported but declared as a dev dependency",
                },
                "module": "black",
                "location": {
                    "file": str(Path("src/main.py")),
                    "line": 4,
                    "column": 0,
                },
            },
            {
                "error": {
                    "code": "DEP001",
                    "message": "white imported but missing from the dependency definitions",
                },
                "module": "white",
                "location": {
                    "file": str(Path("src/main.py")),
                    "line": 6,
                    "column": 0,
                },
            },
        ]


def test_cli_help() -> None:
    result = CliRunner().invoke(deptry, "--help")

    assert result.exit_code == 0
