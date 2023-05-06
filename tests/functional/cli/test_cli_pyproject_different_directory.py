from __future__ import annotations

from typing import TYPE_CHECKING

from click.testing import CliRunner

from deptry.cli import deptry
from tests.utils import get_issues_report, run_within_dir

if TYPE_CHECKING:
    from tests.functional.types import ToolSpecificProjectBuilder


def test_cli_with_pyproject_different_directory(pip_project_builder: ToolSpecificProjectBuilder) -> None:
    with run_within_dir(pip_project_builder("project_with_pyproject_different_directory", cwd="a_sub_directory")):
        result = CliRunner().invoke(deptry, "src --config a_sub_directory/pyproject.toml -o report.json")

        assert result.exit_code == 1
        assert get_issues_report() == {
            "misplaced_dev": [],
            "missing": ["white"],
            "obsolete": ["isort", "requests", "mypy", "pytest"],
            "transitive": [],
        }
