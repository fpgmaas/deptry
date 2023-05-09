from __future__ import annotations

import shlex
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

from click.testing import CliRunner

from deptry.cli import deptry
from tests.utils import get_issues_report, run_within_dir, stylize

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
                    "message": "'isort' defined as a dependency but not used in the codebase",
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
                    "message": "'requests' defined as a dependency but not used in the codebase",
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
                    "message": "'black' imported but declared as a dev dependency",
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
                    "message": "'white' imported but missing from the dependency definitions",
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
                    "message": "'toml' defined as a dependency but not used in the codebase",
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
                    "message": "'isort' defined as a dependency but not used in the codebase",
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
                    "message": "'requests' defined as a dependency but not used in the codebase",
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
                    "message": "'black' imported but declared as a dev dependency",
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
                    "message": "'white' imported but missing from the dependency definitions",
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
        result = CliRunner().invoke(deptry, ". --ignore-unused isort,pkginfo,requests -im white -id black")

        assert result.exit_code == 0


def test_cli_skip_flags(project_builder: ToolSpecificProjectBuilder) -> None:
    with run_within_dir(project_builder("example_project", "poetry install --no-interaction --no-root")):
        result = CliRunner().invoke(deptry, ". --skip-unused --skip-missing --skip-misplaced-dev --skip-transitive")

        assert result.exit_code == 0


def test_cli_exclude(project_builder: ToolSpecificProjectBuilder) -> None:
    with run_within_dir(project_builder("example_project", "poetry install --no-interaction --no-root")):
        result = CliRunner().invoke(deptry, ". --exclude src/notebook.ipynb -o report.json")

        assert result.exit_code == 1
        assert get_issues_report() == [
            {
                "error": {
                    "code": "DEP002",
                    "message": "'toml' defined as a dependency but not used in the codebase",
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
                    "message": "'isort' defined as a dependency but not used in the codebase",
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
                    "message": "'requests' defined as a dependency but not used in the codebase",
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
                    "message": "'black' imported but declared as a dev dependency",
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
                    "message": "'white' imported but missing from the dependency definitions",
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
                    "message": "'toml' defined as a dependency but not used in the codebase",
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
                    "message": "'isort' defined as a dependency but not used in the codebase",
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
                    "message": "'requests' defined as a dependency but not used in the codebase",
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
                    "message": "'black' imported but declared as a dev dependency",
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
                    "message": "'white' imported but missing from the dependency definitions",
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
                    "message": "'isort' defined as a dependency but not used in the codebase",
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
                    "message": "'requests' defined as a dependency but not used in the codebase",
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
                    "message": "'black' imported but declared as a dev dependency",
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
                    "message": "'isort' defined as a dependency but not used in the codebase",
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
                    "message": "'requests' defined as a dependency but not used in the codebase",
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
                    "message": "'black' imported but declared as a dev dependency",
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
                    "message": "'white' imported but missing from the dependency definitions",
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
                    "message": "'isort' defined as a dependency but not used in the codebase",
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
                    "message": "'requests' defined as a dependency but not used in the codebase",
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
                    "message": "'black' imported but declared as a dev dependency",
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
                    "message": "'white' imported but missing from the dependency definitions",
                },
                "module": "white",
                "location": {
                    "file": str(Path("src/main.py")),
                    "line": 6,
                    "column": 0,
                },
            },
        ]


def test_cli_with_no_ansi(project_builder: ToolSpecificProjectBuilder) -> None:
    with run_within_dir(project_builder("example_project", "poetry install --no-interaction --no-root")):
        result = subprocess.run(shlex.split("poetry run deptry . --no-ansi"), capture_output=True, text=True)

        expected_output = [
            "Scanning 2 files...",
            "",
            f"{Path('pyproject.toml')}: DEP002 'isort' defined as a dependency but not used in the codebase",
            f"{Path('pyproject.toml')}: DEP002 'requests' defined as a dependency but not used in the codebase",
            f"{Path('src/main.py')}:4:0: DEP004 'black' imported but declared as a dev dependency",
            f"{Path('src/main.py')}:6:0: DEP001 'white' imported but missing from the dependency definitions",
            "Found 4 dependency issues.",
            "",
            "For more information, see the documentation: https://fpgmaas.github.io/deptry/",
            "",
        ]

        assert result.returncode == 1
        assert result.stderr == "\n".join(expected_output)


def test_cli_with_not_json_output(project_builder: ToolSpecificProjectBuilder) -> None:
    with run_within_dir(project_builder("example_project", "poetry install --no-interaction --no-root")):
        # Remove previously generated `report.json`.
        Path("report.json").unlink()

        result = subprocess.run(shlex.split("poetry run deptry ."), capture_output=True, text=True)

        expected_output = [
            "Scanning 2 files...",
            "",
            stylize(
                (
                    "{BOLD}{file}{RESET}{CYAN}:{RESET} {BOLD}{RED}DEP002{RESET} 'isort' defined as a dependency but not"
                    " used in the codebase"
                ),
                file=Path("pyproject.toml"),
            ),
            stylize(
                (
                    "{BOLD}{file}{RESET}{CYAN}:{RESET} {BOLD}{RED}DEP002{RESET} 'requests' defined as a dependency but"
                    " not used in the codebase"
                ),
                file=Path("pyproject.toml"),
            ),
            stylize(
                (
                    "{BOLD}{file}{RESET}{CYAN}:{RESET}4{CYAN}:{RESET}0{CYAN}:{RESET} {BOLD}{RED}DEP004{RESET} 'black'"
                    " imported but declared as a dev dependency"
                ),
                file=Path("src/main.py"),
            ),
            stylize(
                (
                    "{BOLD}{file}{RESET}{CYAN}:{RESET}6{CYAN}:{RESET}0{CYAN}:{RESET} {BOLD}{RED}DEP001{RESET} 'white'"
                    " imported but missing from the dependency definitions"
                ),
                file=Path("src/main.py"),
            ),
            stylize("{BOLD}{RED}Found 4 dependency issues.{RESET}"),
            "",
            "For more information, see the documentation: https://fpgmaas.github.io/deptry/",
            "",
        ]

        assert result.returncode == 1
        assert len(list(Path(".").glob("*.json"))) == 0
        assert result.stderr == "\n".join(expected_output)


def test_cli_with_json_output(project_builder: ToolSpecificProjectBuilder) -> None:
    with run_within_dir(project_builder("example_project", "poetry install --no-interaction --no-root")):
        result = subprocess.run(shlex.split("poetry run deptry . -o deptry.json"), capture_output=True, text=True)

        expected_output = [
            "Scanning 2 files...",
            "",
            stylize(
                (
                    "{BOLD}{file}{RESET}{CYAN}:{RESET} {BOLD}{RED}DEP002{RESET} 'isort' defined as a dependency but not"
                    " used in the codebase"
                ),
                file=Path("pyproject.toml"),
            ),
            stylize(
                (
                    "{BOLD}{file}{RESET}{CYAN}:{RESET} {BOLD}{RED}DEP002{RESET} 'requests' defined as a dependency but"
                    " not used in the codebase"
                ),
                file=Path("pyproject.toml"),
            ),
            stylize(
                (
                    "{BOLD}{file}{RESET}{CYAN}:{RESET}4{CYAN}:{RESET}0{CYAN}:{RESET} {BOLD}{RED}DEP004{RESET} 'black'"
                    " imported but declared as a dev dependency"
                ),
                file=Path("src/main.py"),
            ),
            stylize(
                (
                    "{BOLD}{file}{RESET}{CYAN}:{RESET}6{CYAN}:{RESET}0{CYAN}:{RESET} {BOLD}{RED}DEP001{RESET} 'white'"
                    " imported but missing from the dependency definitions"
                ),
                file=Path("src/main.py"),
            ),
            stylize("{BOLD}{RED}Found 4 dependency issues.{RESET}"),
            "",
            "For more information, see the documentation: https://fpgmaas.github.io/deptry/",
            "",
        ]

        # Assert that we still write to console when generating a JSON report.
        assert result.stderr == "\n".join(expected_output)
        assert get_issues_report("deptry.json") == [
            {
                "error": {
                    "code": "DEP002",
                    "message": "'isort' defined as a dependency but not used in the codebase",
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
                    "message": "'requests' defined as a dependency but not used in the codebase",
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
                    "message": "'black' imported but declared as a dev dependency",
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
                    "message": "'white' imported but missing from the dependency definitions",
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
