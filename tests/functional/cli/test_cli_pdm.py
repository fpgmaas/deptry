from __future__ import annotations

import uuid
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tests.functional.utils import Project
from tests.utils import get_issues_report

if TYPE_CHECKING:
    from tests.utils import PDMVenvFactory


@pytest.mark.xdist_group(name=Project.PDM)
def test_cli_with_pdm(pdm_venv_factory: PDMVenvFactory) -> None:
    with pdm_venv_factory(Project.PDM) as virtual_env:
        issue_report = f"{uuid.uuid4()}.json"
        result = virtual_env.run(f"deptry . -o {issue_report}")

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
                    "code": "DEP004",
                    "message": "'certifi' imported but declared as a dev dependency",
                },
                "module": "certifi",
                "location": {
                    "file": str(Path("src/main.py")),
                    "line": 5,
                    "column": 8,
                },
            },
            {
                "error": {
                    "code": "DEP004",
                    "message": "'idna' imported but declared as a dev dependency",
                },
                "module": "idna",
                "location": {
                    "file": str(Path("src/main.py")),
                    "line": 7,
                    "column": 8,
                },
            },
            {
                "error": {
                    "code": "DEP004",
                    "message": "'mypy' imported but declared as a dev dependency",
                },
                "module": "mypy",
                "location": {
                    "file": str(Path("src/main.py")),
                    "line": 8,
                    "column": 8,
                },
            },
            {
                "error": {
                    "code": "DEP004",
                    "message": "'packaging' imported but declared as a dev dependency",
                },
                "module": "packaging",
                "location": {
                    "file": str(Path("src/main.py")),
                    "line": 9,
                    "column": 8,
                },
            },
            {
                "error": {
                    "code": "DEP004",
                    "message": "'pytest' imported but declared as a dev dependency",
                },
                "module": "pytest",
                "location": {
                    "file": str(Path("src/main.py")),
                    "line": 10,
                    "column": 8,
                },
            },
            {
                "error": {
                    "code": "DEP004",
                    "message": "'pytest_cov' imported but declared as a dev dependency",
                },
                "module": "pytest_cov",
                "location": {
                    "file": str(Path("src/main.py")),
                    "line": 11,
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
                    "line": 12,
                    "column": 8,
                },
            },
        ]
