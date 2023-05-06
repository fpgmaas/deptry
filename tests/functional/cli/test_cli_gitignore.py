from __future__ import annotations

import shlex
from typing import TYPE_CHECKING

from click.testing import CliRunner

from deptry.cli import deptry
from tests.utils import get_issues_report, run_within_dir

if TYPE_CHECKING:
    from tests.functional.types import ToolSpecificProjectBuilder


def test_cli_gitignore_is_used(pip_project_builder: ToolSpecificProjectBuilder) -> None:
    with run_within_dir(pip_project_builder("project_with_gitignore")):
        result = CliRunner().invoke(deptry, shlex.split(". -o report.json"))

        assert result.exit_code == 1
        assert get_issues_report() == {
            "misplaced_dev": [],
            "missing": [],
            "obsolete": ["requests", "mypy", "pytest"],
            "transitive": [],
        }


def test_cli_gitignore_is_not_used(pip_project_builder: ToolSpecificProjectBuilder) -> None:
    with run_within_dir(pip_project_builder("project_with_gitignore")):
        result = CliRunner().invoke(deptry, ". --exclude build/|src/bar.py -o report.json")

        assert result.exit_code == 1
        assert get_issues_report() == {
            "misplaced_dev": [],
            "missing": [],
            "obsolete": ["isort", "requests", "pytest"],
            "transitive": [],
        }
