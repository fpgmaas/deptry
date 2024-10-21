from __future__ import annotations

import uuid
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tests.functional.utils import Project
from tests.utils import get_issues_report

if TYPE_CHECKING:
    from tests.utils import PipVenvFactory


@pytest.mark.xdist_group(name=Project.SETUPTOOLS_DYNAMIC_DEPENDENCIES)
def test_cli_setuptools_dynamic_dependencies(pip_venv_factory: PipVenvFactory) -> None:
    with pip_venv_factory(
        Project.SETUPTOOLS_DYNAMIC_DEPENDENCIES,
        install_command="pip install -r requirements.txt -r requirements-2.txt -r cli-requirements.txt -r dev-requirements.txt",
    ) as virtual_env:
        issue_report = f"{uuid.uuid4()}.json"
        result = virtual_env.run(f"deptry . -o {issue_report}")

        assert result.returncode == 1
        assert get_issues_report(Path(issue_report)) == [
            {
                "error": {
                    "code": "DEP002",
                    "message": "'packaging' defined as a dependency but not used in the codebase",
                },
                "module": "packaging",
                "location": {
                    "file": "requirements-2.txt",
                    "line": None,
                    "column": None,
                },
            },
            {
                "error": {
                    "code": "DEP002",
                    "message": "'pkginfo' defined as a dependency but not used in the codebase",
                },
                "module": "pkginfo",
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
                    "message": "'isort' imported but declared as a dev dependency",
                },
                "module": "isort",
                "location": {
                    "file": str(Path("src/main.py")),
                    "line": 5,
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
