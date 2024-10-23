from __future__ import annotations

import uuid
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tests.functional.utils import Project
from tests.utils import get_issues_report

if TYPE_CHECKING:
    from tests.utils import PipVenvFactory


@pytest.mark.xdist_group(name=Project.GITIGNORE)
def test_cli_gitignore_used(pip_venv_factory: PipVenvFactory) -> None:
    with pip_venv_factory(Project.GITIGNORE) as virtual_env:
        issue_report = f"{uuid.uuid4()}.json"

        # Simulate the fact that the project is a git repository.
        Path(".git").mkdir(exist_ok=True)

        result = virtual_env.run(f"deptry . -o {issue_report}")

        assert result.returncode == 1
        assert get_issues_report(Path(issue_report)) == [
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
        ]


@pytest.mark.xdist_group(name=Project.GITIGNORE)
def test_cli_gitignore_used_for_non_root_directory(pip_venv_factory: PipVenvFactory) -> None:
    with pip_venv_factory(Project.GITIGNORE) as virtual_env:
        issue_report = f"{uuid.uuid4()}.json"

        # Simulate the fact that the project is a git repository.
        Path(".git").mkdir(exist_ok=True)

        result = virtual_env.run(f"deptry src -o {issue_report}")

        assert result.returncode == 1
        assert get_issues_report(Path(issue_report)) == [
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
        ]


@pytest.mark.xdist_group(name=Project.GITIGNORE)
def test_cli_gitignore_not_used_when_using_exclude(pip_venv_factory: PipVenvFactory) -> None:
    with pip_venv_factory(Project.GITIGNORE) as virtual_env:
        issue_report = f"{uuid.uuid4()}.json"

        # Simulate the fact that the project is a git repository.
        Path(".git").mkdir(exist_ok=True)

        result = virtual_env.run(f"deptry . --exclude build/|src/bar.py -o {issue_report}")

        assert result.returncode == 1
        assert get_issues_report(Path(issue_report)) == [
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
                    "message": "'hello' imported but missing from the dependency definitions",
                },
                "module": "hello",
                "location": {
                    "file": str(Path("src/barfoo.py")),
                    "line": 1,
                    "column": 8,
                },
            },
            {
                "error": {
                    "code": "DEP001",
                    "message": "'hej' imported but missing from the dependency definitions",
                },
                "module": "hej",
                "location": {
                    "file": str(Path("src/baz.py")),
                    "line": 1,
                    "column": 8,
                },
            },
        ]
