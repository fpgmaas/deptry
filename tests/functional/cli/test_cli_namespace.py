from __future__ import annotations

import uuid
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tests.functional.utils import Project
from tests.utils import get_issues_report

if TYPE_CHECKING:
    from tests.utils import PipVenvFactory


@pytest.mark.xdist_group(name=Project.NAMESPACE)
def test_cli_with_namespace(pip_venv_factory: PipVenvFactory) -> None:
    with pip_venv_factory(Project.NAMESPACE) as virtual_env:
        issue_report = f"{uuid.uuid4()}.json"
        result = virtual_env.run(f"deptry . --experimental-namespace-package -o {issue_report}")

        assert result.returncode == 1
        assert get_issues_report(Path(issue_report)) == [
            {
                "error": {"code": "DEP004", "message": "'flake8' imported but declared as a dev dependency"},
                "module": "flake8",
                "location": {"file": str(Path("foo/database/bar.py")), "line": 4, "column": 8},
            },
            {
                "error": {"code": "DEP001", "message": "'white' imported but missing from the dependency definitions"},
                "module": "white",
                "location": {"file": str(Path("foo/database/bar.py")), "line": 5, "column": 8},
            },
            {
                "error": {"code": "DEP002", "message": "'arrow' defined as a dependency but not used in the codebase"},
                "module": "arrow",
                "location": {"file": str(Path("pyproject.toml")), "line": None, "column": None},
            },
        ]


@pytest.mark.xdist_group(name=Project.NAMESPACE)
def test_cli_with_namespace_without_experimental_flag(pip_venv_factory: PipVenvFactory) -> None:
    with pip_venv_factory(Project.NAMESPACE) as virtual_env:
        issue_report = f"{uuid.uuid4()}.json"
        result = virtual_env.run(f"deptry . -o {issue_report}")

        assert result.returncode == 1
        assert get_issues_report(Path(issue_report)) == [
            {
                "error": {"code": "DEP004", "message": "'flake8' imported but declared as a dev dependency"},
                "module": "flake8",
                "location": {"file": str(Path("foo/database/bar.py")), "line": 4, "column": 8},
            },
            {
                "error": {"code": "DEP001", "message": "'white' imported but missing from the dependency definitions"},
                "module": "white",
                "location": {"file": str(Path("foo/database/bar.py")), "line": 5, "column": 8},
            },
            {
                "error": {"code": "DEP003", "message": "'foo' imported but it is a transitive dependency"},
                "module": "foo",
                "location": {"file": str(Path("foo/database/bar.py")), "line": 7, "column": 1},
            },
            {
                "error": {"code": "DEP002", "message": "'arrow' defined as a dependency but not used in the codebase"},
                "module": "arrow",
                "location": {"file": str(Path("pyproject.toml")), "line": None, "column": None},
            },
        ]
