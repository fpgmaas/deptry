from __future__ import annotations

import uuid
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tests.functional.utils import Project
from tests.utils import get_issues_report

if TYPE_CHECKING:
    from tests.utils import PipVenvFactory


@pytest.mark.xdist_group(name=Project.PYPROJECT_DIFFERENT_DIRECTORY)
def test_cli_with_pyproject_different_directory(pip_venv_factory: PipVenvFactory) -> None:
    with pip_venv_factory(
        Project.PYPROJECT_DIFFERENT_DIRECTORY, install_command="pip install ./a_sub_directory"
    ) as virtual_env:
        issue_report = f"{uuid.uuid4()}.json"
        result = virtual_env.run(f"deptry src --config a_sub_directory/pyproject.toml -o {issue_report}")

        assert result.returncode == 1
        assert get_issues_report(Path(issue_report)) == [
            {
                "error": {
                    "code": "DEP002",
                    "message": "'isort' defined as a dependency but not used in the codebase",
                },
                "module": "isort",
                "location": {
                    "file": str(Path("a_sub_directory/pyproject.toml")),
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
                    "file": str(Path("a_sub_directory/pyproject.toml")),
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
                    "file": str(Path("a_sub_directory/pyproject.toml")),
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
                    "file": str(Path("a_sub_directory/pyproject.toml")),
                    "line": None,
                    "column": None,
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
                    "column": 8,
                },
            },
        ]
