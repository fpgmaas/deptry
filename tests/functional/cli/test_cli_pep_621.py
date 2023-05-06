from __future__ import annotations

from typing import TYPE_CHECKING

from click.testing import CliRunner

from deptry.cli import deptry
from tests.utils import get_issues_report, run_within_dir

if TYPE_CHECKING:
    from tests.functional.types import ToolSpecificProjectBuilder


def test_cli_with_pep_621(pip_project_builder: ToolSpecificProjectBuilder) -> None:
    with run_within_dir(pip_project_builder("pep_621_project")):
        result = CliRunner().invoke(deptry, ". -o report.json")

        assert result.exit_code == 1
        assert get_issues_report() == {
            "misplaced_dev": [],
            "missing": ["white"],
            "obsolete": ["isort", "requests", "mypy", "pytest"],
            "transitive": [],
        }
