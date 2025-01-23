from __future__ import annotations

import uuid
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tests.functional.utils import Project
from tests.utils import get_issues_report

if TYPE_CHECKING:
    from tests.utils import PipVenvFactory


@pytest.mark.xdist_group(name=Project.REQUIREMENTS_TXT_AND_POETRY)
def test_cli_requirements_files_overrides_pyproject_toml_when_passed_explicitly(
    pip_venv_factory: PipVenvFactory,
) -> None:
    with pip_venv_factory(
        Project.REQUIREMENTS_TXT_AND_POETRY,
        install_command=("pip install -r requirements.txt"),
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
                    "code": "DEP004",
                    "message": "'black' imported but declared as a dev dependency",
                },
                "location": {
                    "column": 8,
                    "file": str(Path("src/main.py")),
                    "line": 1,
                },
                "module": "black",
            },
            {
                "error": {
                    "code": "DEP001",
                    "message": "'arrow' imported but missing from the dependency definitions",
                },
                "module": "arrow",
                "location": {"file": str(Path("src/notebook.ipynb")), "line": 2, "column": 8},
            },
        ]
