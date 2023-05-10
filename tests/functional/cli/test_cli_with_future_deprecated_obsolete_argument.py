from __future__ import annotations

import shlex
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

from deptry.deprecate_obsolete import (
    IGNORE_OBSOLETE_AND_IGNORE_UNUSED_ERROR_MESSAGE,
    IGNORE_OBSOLETE_WARNING,
    SKIP_OBSOLETE_AND_SKIP_UNUSED_ERROR_MESSAGE,
    SKIP_OBSOLETE_WARNING,
)
from tests.utils import get_issues_report, run_within_dir

if TYPE_CHECKING:
    from tests.functional.types import ToolSpecificProjectBuilder


def test_cli_uses_both_obsolete_and_unused_flag_from_pyproject_toml(
    project_builder: ToolSpecificProjectBuilder,
) -> None:
    with run_within_dir(
        project_builder("project_with_future_deprecated_obsolete_argument", "poetry install --no-interaction --no-root")
    ):
        result = subprocess.run(shlex.split("poetry run deptry . -o report.json"), capture_output=True, text=True)

        assert IGNORE_OBSOLETE_WARNING in result.stderr
        assert result.returncode == 1
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
                    "code": "DEP001",
                    "message": "'white' imported but missing from the dependency definitions",
                },
                "module": "white",
                "location": {
                    "file": str(Path("src/main.py")),
                    "line": 6,
                    "column": 0,
                },
            },
        ]


def test_cli_skip_obsolete_argument_still_works(project_builder: ToolSpecificProjectBuilder) -> None:
    with run_within_dir(
        project_builder("project_with_future_deprecated_obsolete_argument", "poetry install --no-interaction --no-root")
    ):
        result = subprocess.run(
            shlex.split("poetry run deptry . --skip-obsolete -o report.json"), capture_output=True, text=True
        )

        assert SKIP_OBSOLETE_WARNING in result.stderr
        assert IGNORE_OBSOLETE_WARNING in result.stderr
        assert result.returncode == 1
        assert get_issues_report() == [
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
                    "code": "DEP001",
                    "message": "'white' imported but missing from the dependency definitions",
                },
                "module": "white",
                "location": {
                    "file": str(Path("src/main.py")),
                    "line": 6,
                    "column": 0,
                },
            },
        ]


def test_cli_raise_error_if_both_skip_options_used(project_builder: ToolSpecificProjectBuilder) -> None:
    with run_within_dir(
        project_builder("project_with_future_deprecated_obsolete_argument", "poetry install --no-interaction --no-root")
    ):
        result = subprocess.run(
            shlex.split("poetry run deptry . --skip-obsolete --skip-unused"), capture_output=True, text=True
        )
        assert SKIP_OBSOLETE_AND_SKIP_UNUSED_ERROR_MESSAGE in result.stderr


def test_cli_raise_error_if_both_ignore_options_used(project_builder: ToolSpecificProjectBuilder) -> None:
    with run_within_dir(
        project_builder("project_with_future_deprecated_obsolete_argument", "poetry install --no-interaction --no-root")
    ):
        result = subprocess.run(
            shlex.split("poetry run deptry . --ignore-unused 'a,b'"), capture_output=True, text=True
        )
        assert IGNORE_OBSOLETE_AND_IGNORE_UNUSED_ERROR_MESSAGE in result.stderr
