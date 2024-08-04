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
        result = virtual_env.run(f"deptry . -o {issue_report}")

        assert result.returncode == 1
        assert get_issues_report(Path(issue_report)) == [
            {
                "error": {"code": "DEP004", "message": "'black' imported but declared as a dev dependency"},
                "module": "black",
                "location": {"file": str(Path("foo/database/bar.py")), "line": 4, "column": 8},
            },
            {
                "error": {"code": "DEP001", "message": "'white' imported but missing from the dependency definitions"},
                "module": "white",
                "location": {"file": str(Path("foo/database/bar.py")), "line": 5, "column": 8},
            },
            {
                "error": {"code": "DEP002", "message": "'toml' defined as a dependency but not used in the codebase"},
                "module": "toml",
                "location": {"file": str(Path("pyproject.toml")), "line": None, "column": None},
            },
        ]
