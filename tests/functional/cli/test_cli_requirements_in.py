from __future__ import annotations

import uuid
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tests.functional.utils import Project
from tests.utils import get_issues_report

if TYPE_CHECKING:
    from tests.utils import PipVenvFactory


@pytest.mark.xdist_group(name=Project.REQUIREMENTS_IN)
def test_cli_single_requirements_files(pip_venv_factory: PipVenvFactory) -> None:
    """
    in this case, deptry should recognize that there is a `requirements.in` in the project, and
    use that as the source of the dependencies.
    """
    with pip_venv_factory(
        Project.REQUIREMENTS_IN,
        install_command=("pip install -r requirements.txt -r requirements-dev.txt"),
    ) as virtual_env:
        issue_report = f"{uuid.uuid4()}.json"
        result = virtual_env.run(f"deptry . -o {issue_report}")

        assert result.returncode == 1
        assert get_issues_report(Path(issue_report)) == [
            {
                "error": {"code": "DEP002", "message": "'isort' defined as a dependency but not used in the codebase"},
                "module": "isort",
                "location": {"file": str(Path("requirements.in")), "line": None, "column": None},
            },
            {
                "error": {
                    "code": "DEP002",
                    "message": "'uvicorn' defined as a dependency but not used in the codebase",
                },
                "module": "uvicorn",
                "location": {"file": str(Path("requirements.in")), "line": None, "column": None},
            },
            {
                "error": {"code": "DEP004", "message": "'black' imported but declared as a dev dependency"},
                "module": "black",
                "location": {"file": str(Path("src/main.py")), "line": 4, "column": 8},
            },
            {
                "error": {"code": "DEP003", "message": "'h11' imported but it is a transitive dependency"},
                "module": "h11",
                "location": {"file": str(Path("src/main.py")), "line": 6, "column": 8},
            },
            {
                "error": {"code": "DEP001", "message": "'white' imported but missing from the dependency definitions"},
                "module": "white",
                "location": {"file": str(Path("src/main.py")), "line": 7, "column": 8},
            },
            {
                "error": {"code": "DEP001", "message": "'arrow' imported but missing from the dependency definitions"},
                "module": "arrow",
                "location": {"file": str(Path("src/notebook.ipynb")), "line": 3, "column": 8},
            },
        ]


@pytest.mark.xdist_group(name=Project.REQUIREMENTS_IN)
def test_cli_multiple_requirements_files(pip_venv_factory: PipVenvFactory) -> None:
    """
    in this case, deptry recognizes that there is a `requirements.in` in the project, but the user
    can overwrite that with '--requirements-files requirements.txt', so it still takes requirements.txt as the source
    for the project's dependencies.
    """
    with pip_venv_factory(
        Project.REQUIREMENTS_IN,
        install_command=("pip install -r requirements.txt -r requirements-dev.txt"),
    ) as virtual_env:
        issue_report = f"{uuid.uuid4()}.json"
        result = virtual_env.run(f"deptry . --requirements-files requirements.txt -o {issue_report}")

        assert result.returncode == 1
        assert get_issues_report(Path(issue_report)) == [
            {
                "error": {"code": "DEP002", "message": "'isort' defined as a dependency but not used in the codebase"},
                "module": "isort",
                "location": {"file": str(Path("requirements.txt")), "line": None, "column": None},
            },
            {
                "error": {
                    "code": "DEP002",
                    "message": "'uvicorn' defined as a dependency but not used in the codebase",
                },
                "module": "uvicorn",
                "location": {"file": str(Path("requirements.txt")), "line": None, "column": None},
            },
            {
                "error": {"code": "DEP004", "message": "'black' imported but declared as a dev dependency"},
                "module": "black",
                "location": {"file": str(Path("src/main.py")), "line": 4, "column": 8},
            },
            {
                "error": {"code": "DEP001", "message": "'white' imported but missing from the dependency definitions"},
                "module": "white",
                "location": {"file": str(Path("src/main.py")), "line": 7, "column": 8},
            },
            {
                "error": {"code": "DEP001", "message": "'arrow' imported but missing from the dependency definitions"},
                "module": "arrow",
                "location": {"file": str(Path("src/notebook.ipynb")), "line": 3, "column": 8},
            },
        ]
