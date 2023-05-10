from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from click.testing import CliRunner

from deptry.cli import deptry
from tests.utils import get_issues_report, run_within_dir

if TYPE_CHECKING:
    from tests.functional.types import ToolSpecificProjectBuilder


def test_cli_with_pdm(pdm_project_builder: ToolSpecificProjectBuilder) -> None:
    with run_within_dir(pdm_project_builder("project_with_pdm")):
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
                    "code": "DEP004",
                    "message": "'mypy' imported but declared as a dev dependency",
                },
                "module": "mypy",
                "location": {
                    "file": str(Path("src/main.py")),
                    "line": 6,
                    "column": 0,
                },
            },
            {
                "error": {
                    "code": "DEP004",
                    "message": "'pytest' imported but declared as a dev dependency",
                },
                "module": "pytest",
                "location": {
                    "file": str(Path("src/main.py")),
                    "line": 7,
                    "column": 0,
                },
            },
            {
                "error": {
                    "code": "DEP004",
                    "message": "'pytest_cov' imported but declared as a dev dependency",
                },
                "module": "pytest_cov",
                "location": {
                    "file": str(Path("src/main.py")),
                    "line": 8,
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
                    "line": 9,
                    "column": 0,
                },
            },
        ]
