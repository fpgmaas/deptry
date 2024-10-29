from __future__ import annotations

import uuid
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from click.testing import CliRunner

from deptry.cli import cli
from tests.functional.utils import Project
from tests.utils import get_issues_report, stylize

if TYPE_CHECKING:
    from tests.utils import PoetryVenvFactory


@pytest.mark.xdist_group(name=Project.EXAMPLE)
def test_cli_returns_error(poetry_venv_factory: PoetryVenvFactory) -> None:
    with poetry_venv_factory(Project.EXAMPLE) as virtual_env:
        issue_report = f"{uuid.uuid4()}.json"
        result = virtual_env.run(f"deptry . -o {issue_report}")

        assert result.returncode == 1
        assert get_issues_report(Path(issue_report)) == [
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
                    "column": 8,
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
                    "column": 8,
                },
            },
        ]


@pytest.mark.xdist_group(name=Project.EXAMPLE)
def test_cli_ignore_notebooks(poetry_venv_factory: PoetryVenvFactory) -> None:
    with poetry_venv_factory(Project.EXAMPLE) as virtual_env:
        issue_report = f"{uuid.uuid4()}.json"
        result = virtual_env.run(f"deptry . --ignore-notebooks -o {issue_report}")

        assert result.returncode == 1
        assert get_issues_report(Path(issue_report)) == [
            {
                "error": {
                    "code": "DEP002",
                    "message": "'arrow' defined as a dependency but not used in the codebase",
                },
                "module": "arrow",
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
                    "column": 8,
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
                    "column": 8,
                },
            },
        ]


@pytest.mark.xdist_group(name=Project.EXAMPLE)
def test_cli_ignore_flags(poetry_venv_factory: PoetryVenvFactory) -> None:
    with poetry_venv_factory(Project.EXAMPLE) as virtual_env:
        result = virtual_env.run("deptry . --per-rule-ignores DEP001=white,DEP002=isort|pkginfo|requests,DEP004=black")

        assert result.returncode == 0


@pytest.mark.xdist_group(name=Project.EXAMPLE)
def test_cli_ignore_flag(poetry_venv_factory: PoetryVenvFactory) -> None:
    with poetry_venv_factory(Project.EXAMPLE) as virtual_env:
        result = virtual_env.run("deptry . --ignore DEP001,DEP002,DEP003,DEP004")

        assert result.returncode == 0


@pytest.mark.xdist_group(name=Project.EXAMPLE)
def test_cli_exclude(poetry_venv_factory: PoetryVenvFactory) -> None:
    with poetry_venv_factory(Project.EXAMPLE) as virtual_env:
        issue_report = f"{uuid.uuid4()}.json"
        result = virtual_env.run(f"deptry . --exclude src/notebook.ipynb -o {issue_report}")

        assert result.returncode == 1
        assert get_issues_report(Path(issue_report)) == [
            {
                "error": {
                    "code": "DEP002",
                    "message": "'arrow' defined as a dependency but not used in the codebase",
                },
                "module": "arrow",
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
                    "column": 8,
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
                    "column": 8,
                },
            },
        ]


@pytest.mark.xdist_group(name=Project.EXAMPLE)
def test_cli_extend_exclude(poetry_venv_factory: PoetryVenvFactory) -> None:
    with poetry_venv_factory(Project.EXAMPLE) as virtual_env:
        issue_report = f"{uuid.uuid4()}.json"
        result = virtual_env.run(f"deptry . -ee src/notebook.ipynb -o {issue_report}")

        assert result.returncode == 1
        assert get_issues_report(Path(issue_report)) == [
            {
                "error": {
                    "code": "DEP002",
                    "message": "'arrow' defined as a dependency but not used in the codebase",
                },
                "module": "arrow",
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
                    "column": 8,
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
                    "column": 8,
                },
            },
        ]


@pytest.mark.xdist_group(name=Project.EXAMPLE)
def test_cli_known_first_party(poetry_venv_factory: PoetryVenvFactory) -> None:
    with poetry_venv_factory(Project.EXAMPLE) as virtual_env:
        issue_report = f"{uuid.uuid4()}.json"
        result = virtual_env.run(f"deptry . --known-first-party white -o {issue_report}")

        assert result.returncode == 1
        assert get_issues_report(Path(issue_report)) == [
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
                    "column": 8,
                },
            },
        ]


@pytest.mark.xdist_group(name=Project.EXAMPLE)
def test_cli_not_verbose(poetry_venv_factory: PoetryVenvFactory) -> None:
    with poetry_venv_factory(Project.EXAMPLE) as virtual_env:
        issue_report = f"{uuid.uuid4()}.json"
        result = virtual_env.run(f"deptry . -o {issue_report}")

        assert result.returncode == 1
        assert "The project contains the following dependencies:" not in result.stderr
        assert get_issues_report(Path(issue_report)) == [
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
                    "column": 8,
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
                    "column": 8,
                },
            },
        ]


@pytest.mark.xdist_group(name=Project.EXAMPLE)
def test_cli_verbose(poetry_venv_factory: PoetryVenvFactory) -> None:
    with poetry_venv_factory(Project.EXAMPLE) as virtual_env:
        issue_report = f"{uuid.uuid4()}.json"
        result = virtual_env.run(f"deptry . --verbose -o {issue_report}")

        assert result.returncode == 1
        assert "The project contains the following dependencies:" in result.stderr
        assert "The project contains the following dev dependencies:" in result.stderr
        assert get_issues_report(Path(issue_report)) == [
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
                    "column": 8,
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
                    "column": 8,
                },
            },
        ]


@pytest.mark.xdist_group(name=Project.EXAMPLE)
def test_cli_with_no_ansi(poetry_venv_factory: PoetryVenvFactory) -> None:
    with poetry_venv_factory(Project.EXAMPLE) as virtual_env:
        result = virtual_env.run("deptry . --no-ansi")

        expected_output = [
            "Scanning 2 files...",
            "",
            f"{Path('pyproject.toml')}: DEP002 'isort' defined as a dependency but not used in the codebase",
            f"{Path('pyproject.toml')}: DEP002 'requests' defined as a dependency but not used in the codebase",
            f"{Path('src/main.py')}:4:8: DEP004 'black' imported but declared as a dev dependency",
            f"{Path('src/main.py')}:6:8: DEP001 'white' imported but missing from the dependency definitions",
            "Found 4 dependency issues.",
            "",
            "For more information, see the documentation: https://deptry.com/",
            "",
        ]

        assert result.returncode == 1
        assert result.stderr == "\n".join(expected_output)


@pytest.mark.xdist_group(name=Project.EXAMPLE)
def test_cli_with_not_json_output(poetry_venv_factory: PoetryVenvFactory) -> None:
    with poetry_venv_factory(Project.EXAMPLE) as virtual_env:
        json_files_count = len(list(Path().glob("*.json")))

        result = virtual_env.run("deptry .")

        expected_output = [
            "Scanning 2 files...",
            "",
            stylize(
                "{BOLD}{file}{RESET}{CYAN}:{RESET} {BOLD}{RED}DEP002{RESET} 'isort' defined as a dependency but not"
                " used in the codebase",
                file=Path("pyproject.toml"),
            ),
            stylize(
                "{BOLD}{file}{RESET}{CYAN}:{RESET} {BOLD}{RED}DEP002{RESET} 'requests' defined as a dependency but"
                " not used in the codebase",
                file=Path("pyproject.toml"),
            ),
            stylize(
                "{BOLD}{file}{RESET}{CYAN}:{RESET}4{CYAN}:{RESET}8{CYAN}:{RESET} {BOLD}{RED}DEP004{RESET} 'black'"
                " imported but declared as a dev dependency",
                file=Path("src/main.py"),
            ),
            stylize(
                "{BOLD}{file}{RESET}{CYAN}:{RESET}6{CYAN}:{RESET}8{CYAN}:{RESET} {BOLD}{RED}DEP001{RESET} 'white'"
                " imported but missing from the dependency definitions",
                file=Path("src/main.py"),
            ),
            stylize("{BOLD}{RED}Found 4 dependency issues.{RESET}"),
            "",
            "For more information, see the documentation: https://deptry.com/",
            "",
        ]

        assert result.returncode == 1
        # Assert that we have the same number of JSON files as before running the command.
        assert len(list(Path().glob("*.json"))) == json_files_count
        assert result.stderr == "\n".join(expected_output)


@pytest.mark.xdist_group(name=Project.EXAMPLE)
def test_cli_with_json_output(poetry_venv_factory: PoetryVenvFactory) -> None:
    with poetry_venv_factory(Project.EXAMPLE) as virtual_env:
        issue_report = f"{uuid.uuid4()}.json"
        result = virtual_env.run(f"deptry . -o {issue_report}")

        expected_output = [
            "Scanning 2 files...",
            "",
            stylize(
                "{BOLD}{file}{RESET}{CYAN}:{RESET} {BOLD}{RED}DEP002{RESET} 'isort' defined as a dependency but not"
                " used in the codebase",
                file=Path("pyproject.toml"),
            ),
            stylize(
                "{BOLD}{file}{RESET}{CYAN}:{RESET} {BOLD}{RED}DEP002{RESET} 'requests' defined as a dependency but"
                " not used in the codebase",
                file=Path("pyproject.toml"),
            ),
            stylize(
                "{BOLD}{file}{RESET}{CYAN}:{RESET}4{CYAN}:{RESET}8{CYAN}:{RESET} {BOLD}{RED}DEP004{RESET} 'black'"
                " imported but declared as a dev dependency",
                file=Path("src/main.py"),
            ),
            stylize(
                "{BOLD}{file}{RESET}{CYAN}:{RESET}6{CYAN}:{RESET}8{CYAN}:{RESET} {BOLD}{RED}DEP001{RESET} 'white'"
                " imported but missing from the dependency definitions",
                file=Path("src/main.py"),
            ),
            stylize("{BOLD}{RED}Found 4 dependency issues.{RESET}"),
            "",
            "For more information, see the documentation: https://deptry.com/",
            "",
        ]

        # Assert that we still write to console when generating a JSON report.
        assert result.stderr == "\n".join(expected_output)
        assert get_issues_report(Path(issue_report)) == [
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
                    "column": 8,
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
                    "column": 8,
                },
            },
        ]


def test_cli_help() -> None:
    result = CliRunner().invoke(cli, "--help")

    assert result.exit_code == 0
