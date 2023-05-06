from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from click.testing import CliRunner

from deptry.cli import deptry
from tests.utils import get_issues_report, run_within_dir

if TYPE_CHECKING:
    from tests.functional.types import ToolSpecificProjectBuilder


def test_cli_single_requirements_txt(requirements_txt_project_builder: ToolSpecificProjectBuilder) -> None:
    with run_within_dir(requirements_txt_project_builder("project_with_requirements_txt")):
        result = CliRunner().invoke(
            deptry,
            ". --requirements-txt requirements.txt --requirements-txt-dev requirements-dev.txt -o report.json",
        )

        assert result.exit_code == 1
        assert get_issues_report() == [
            {
                "error": {
                    "code": "DEP002",
                    "message": "isort defined as a dependency but not used in the codebase",
                },
                "module": "isort",
                "location": {
                    "file": str(Path("requirements.txt")),
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
                    "file": str(Path("requirements.txt")),
                    "line": None,
                    "column": None,
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
            {
                "error": {
                    "code": "DEP003",
                    "message": "urllib3 imported but it is a transitive dependency",
                },
                "module": "urllib3",
                "location": {
                    "file": str(Path("src/notebook.ipynb")),
                    "line": 3,
                    "column": 0,
                },
            },
            {
                "error": {
                    "code": "DEP003",
                    "message": "urllib3 imported but it is a transitive dependency",
                },
                "module": "urllib3",
                "location": {
                    "file": str(Path("src/main.py")),
                    "line": 7,
                    "column": 0,
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


def test_cli_multiple_requirements_txt(requirements_txt_project_builder: ToolSpecificProjectBuilder) -> None:
    with run_within_dir(requirements_txt_project_builder("project_with_requirements_txt")):
        result = CliRunner().invoke(
            deptry,
            (
                ". --requirements-txt requirements.txt,requirements-2.txt --requirements-txt-dev requirements-dev.txt"
                " -o report.json"
            ),
        )

        assert result.exit_code == 1
        assert get_issues_report() == [
            {
                "error": {
                    "code": "DEP002",
                    "message": "isort defined as a dependency but not used in the codebase",
                },
                "module": "isort",
                "location": {
                    "file": str(Path("requirements.txt")),
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
                    "file": str(Path("requirements.txt")),
                    "line": None,
                    "column": None,
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
