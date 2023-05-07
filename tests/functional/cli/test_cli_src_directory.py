from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from click.testing import CliRunner

from deptry.cli import deptry
from tests.utils import get_issues_report, run_within_dir

if TYPE_CHECKING:
    from tests.functional.types import ToolSpecificProjectBuilder


def test_cli_with_src_directory(pip_project_builder: ToolSpecificProjectBuilder) -> None:
    with run_within_dir(pip_project_builder("project_with_src_directory")):
        result = CliRunner().invoke(deptry, "src -o report.json")

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
                    "code": "DEP002",
                    "message": "'mypy' defined as a dependency but not used in the codebase",
                },
                "module": "mypy",
                "location": {
                    "file": str(Path("pyproject.toml")),
                    "line": None,
                    "column": None,
                },
            },
            {
                "error": {
                    "code": "DEP002",
                    "message": "'pytest' defined as a dependency but not used in the codebase",
                },
                "module": "pytest",
                "location": {
                    "file": str(Path("pyproject.toml")),
                    "line": None,
                    "column": None,
                },
            },
            {
                "error": {
                    "code": "DEP001",
                    "message": "'httpx' imported but missing from the dependency definitions",
                },
                "module": "httpx",
                "location": {
                    "file": str(Path("src/foobar.py")),
                    "line": 1,
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
                    "file": str(Path("src/project_with_src_directory/foo.py")),
                    "line": 6,
                    "column": 0,
                },
            },
        ]
