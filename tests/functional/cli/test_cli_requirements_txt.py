from __future__ import annotations

import uuid
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tests.functional.utils import Project
from tests.utils import get_issues_report

if TYPE_CHECKING:
    from tests.utils import PipVenvFactory


@pytest.mark.xdist_group(name=Project.REQUIREMENTS_TXT)
def test_cli_single_requirements_files(pip_venv_factory: PipVenvFactory) -> None:
    with pip_venv_factory(
        Project.REQUIREMENTS_TXT,
        install_command=(
            "pip install -r requirements.txt -r requirements-dev.txt -r requirements-2.txt -r requirements-typing.txt"
        ),
    ) as virtual_env:
        issue_report = f"{uuid.uuid4()}.json"
        result = virtual_env.run(
            "deptry . --requirements-files requirements.txt --requirements-files-dev requirements-dev.txt -o"
            f" {issue_report}"
        )

        assert result.returncode == 1
        assert get_issues_report(Path(issue_report)) == [
            {
                "error": {
                    "code": "DEP002",
                    "message": "'isort' defined as a dependency but not used in the codebase",
                },
                "module": "isort",
                "location": {
                    "file": str(Path("requirements.txt")),
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
                    "file": str(Path("requirements.txt")),
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
                    "column": 8,
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
                    "column": 8,
                },
            },
            {
                "error": {
                    "code": "DEP003",
                    "message": "'urllib3' imported but it is a transitive dependency",
                },
                "module": "urllib3",
                "location": {
                    "file": str(Path("src/main.py")),
                    "line": 7,
                    "column": 1,
                },
            },
            {
                "error": {
                    "code": "DEP003",
                    "message": "'urllib3' imported but it is a transitive dependency",
                },
                "module": "urllib3",
                "location": {
                    "file": str(Path("src/notebook.ipynb")),
                    "line": 2,
                    "column": 1,
                },
            },
        ]


@pytest.mark.xdist_group(name=Project.REQUIREMENTS_TXT)
def test_cli_multiple_requirements_files(pip_venv_factory: PipVenvFactory) -> None:
    with pip_venv_factory(
        Project.REQUIREMENTS_TXT,
        install_command=(
            "pip install -r requirements.txt -r requirements-dev.txt -r requirements-2.txt -r requirements-typing.txt"
        ),
    ) as virtual_env:
        issue_report = f"{uuid.uuid4()}.json"
        result = virtual_env.run(
            "deptry . --requirements-files requirements.txt,requirements-2.txt --requirements-files-dev"
            f" requirements-dev.txt -o {issue_report}"
        )

        assert result.returncode == 1
        assert get_issues_report(Path(issue_report)) == [
            {
                "error": {
                    "code": "DEP002",
                    "message": "'isort' defined as a dependency but not used in the codebase",
                },
                "module": "isort",
                "location": {
                    "file": str(Path("requirements.txt")),
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
                    "file": str(Path("requirements.txt")),
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
                    "column": 8,
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
                    "column": 8,
                },
            },
        ]
