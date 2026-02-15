from __future__ import annotations

import uuid
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from inline_snapshot import snapshot

from tests.functional.utils import Project
from tests.utils import get_issues_report

if TYPE_CHECKING:
    from tests.utils import PipVenvFactory


@pytest.mark.xdist_group(name=Project.MULTIPLE_SOURCE_DIRECTORIES)
def test_cli_with_multiple_source_directories(pip_venv_factory: PipVenvFactory) -> None:
    with pip_venv_factory(Project.MULTIPLE_SOURCE_DIRECTORIES) as virtual_env:
        issue_report = f"{uuid.uuid4()}.json"
        result = virtual_env.run(f"deptry src worker -o {issue_report}")

        assert result.returncode == 1
        assert get_issues_report(Path(issue_report)) == snapshot([
            {
                "error": {"code": "DEP002", "message": "'arrow' defined as a dependency but not used in the codebase"},
                "module": "arrow",
                "location": {"file": "pyproject.toml", "line": None, "column": None},
            },
            {
                "error": {"code": "DEP001", "message": "'httpx' imported but missing from the dependency definitions"},
                "module": "httpx",
                "location": {"file": "src/foo.py", "line": 1, "column": 8},
            },
            {
                "error": {"code": "DEP001", "message": "'celery' imported but missing from the dependency definitions"},
                "module": "celery",
                "location": {"file": "worker/foo.py", "line": 1, "column": 8},
            },
        ])
