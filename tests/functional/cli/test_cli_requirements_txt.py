from __future__ import annotations

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
        assert get_issues_report() == {
            "misplaced_dev": ["black"],
            "missing": ["white"],
            "obsolete": ["isort", "requests"],
            "transitive": ["urllib3"],
        }


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
        assert get_issues_report() == {
            "misplaced_dev": ["black"],
            "missing": ["white"],
            "obsolete": ["isort", "requests"],
            "transitive": [],
        }
