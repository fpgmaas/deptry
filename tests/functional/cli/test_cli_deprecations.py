from __future__ import annotations

import uuid
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tests.functional.utils import Project
from tests.utils import get_issues_report

if TYPE_CHECKING:
    from tests.utils import UvVenvFactory


@pytest.mark.xdist_group(name=Project.DEPRECATED_ARGUMENTS)
def test_cli_deprecated_argument(uv_venv_factory: UvVenvFactory) -> None:
    with uv_venv_factory(Project.DEPRECATED_ARGUMENTS) as virtual_env:
        issue_report = f"{uuid.uuid4()}.json"
        result = virtual_env.run(f"deptry . --pep621-dev-dependency-groups dev -o {issue_report}")

        assert result.returncode == 1
        assert get_issues_report(Path(issue_report)) == [
            {
                "error": {
                    "code": "DEP004",
                    "message": "'black' imported but declared as a dev dependency",
                },
                "module": "black",
                "location": {
                    "file": str(Path("src/main.py")),
                    "line": 1,
                    "column": 8,
                },
            },
        ]


@pytest.mark.xdist_group(name=Project.DEPRECATED_OPTIONS)
def test_cli_deprecated_config(uv_venv_factory: UvVenvFactory) -> None:
    with uv_venv_factory(Project.DEPRECATED_OPTIONS) as virtual_env:
        issue_report = f"{uuid.uuid4()}.json"
        result = virtual_env.run(f"deptry . -o {issue_report}")

        assert result.returncode == 1
        assert get_issues_report(Path(issue_report)) == [
            {
                "error": {
                    "code": "DEP004",
                    "message": "'black' imported but declared as a dev dependency",
                },
                "module": "black",
                "location": {
                    "file": str(Path("src/main.py")),
                    "line": 1,
                    "column": 8,
                },
            },
        ]


@pytest.mark.xdist_group(name=Project.DEPRECATED_ARGUMENTS)
def test_cli_deprecated_conflict(uv_venv_factory: UvVenvFactory) -> None:
    with uv_venv_factory(Project.DEPRECATED_ARGUMENTS) as virtual_env:
        result = virtual_env.run("deptry . --pep621-dev-dependency-groups dev --optional-dependencies-dev-groups dev")

        assert result.returncode == 2
        assert (
            result.stderr
            == "Error: Cannot use both `--pep621-dev-dependency-groups` and `--optional-dependencies-dev-groups`. Only use the latter, as the former is deprecated.\n"
        )
