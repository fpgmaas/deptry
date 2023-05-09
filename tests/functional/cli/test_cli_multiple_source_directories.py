from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from click.testing import CliRunner

from deptry.cli import deptry
from tests.utils import get_issues_report, run_within_dir

if TYPE_CHECKING:
    from tests.functional.types import ToolSpecificProjectBuilder


def test_cli_with_multiple_source_directories(pip_project_builder: ToolSpecificProjectBuilder) -> None:
    with run_within_dir(pip_project_builder("project_with_multiple_source_directories")):
        result = CliRunner().invoke(deptry, "src worker -o report.json")

        assert result.exit_code == 1
        assert get_issues_report() == [
            {
                "error": {"code": "DEP002", "message": "'toml' defined as a dependency but not used in the codebase"},
                "module": "toml",
                "location": {"file": str(Path("pyproject.toml")), "line": None, "column": None},
            },
            {
                "error": {"code": "DEP001", "message": "'httpx' imported but missing from the dependency definitions"},
                "module": "httpx",
                "location": {"file": str(Path("src/foo.py")), "line": 1, "column": 0},
            },
            {
                "error": {"code": "DEP001", "message": "'celery' imported but missing from the dependency definitions"},
                "module": "celery",
                "location": {"file": str(Path("worker/foo.py")), "line": 1, "column": 0},
            },
        ]
