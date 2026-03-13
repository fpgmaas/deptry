from __future__ import annotations

import uuid
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tests.functional.utils import Project
from tests.utils import get_issues_report

if TYPE_CHECKING:
    from tests.utils import PipVenvFactory


@pytest.mark.xdist_group(name=Project.INLINE_IGNORES)
def test_cli_inline_ignore_combined_with_pyproject_toml_config(pip_venv_factory: PipVenvFactory) -> None:
    """Verify that inline ignore comments and pyproject.toml `per_rule_ignores` work together.

    The fixture's pyproject.toml has `per_rule_ignores = {DEP002 = ["requests"]}`, and the source
    file has `import white  # deptry: ignore[DEP001]`.  Together they suppress both the DEP001
    for 'white' and the DEP002 for 'requests'.  The inline `# deptry: ignore[DEP003]` on 'gray'
    does NOT suppress the DEP001 violation because the rule code does not match.

    Additionally, 'white' and 'orange' verify that the deptry ignore comment is correctly parsed
    when a `# noqa: ...` comment appears on the same line (both before and after the deptry comment)."""
    with pip_venv_factory(Project.INLINE_IGNORES) as virtual_env:
        issue_report = f"{uuid.uuid4()}.json"
        result = virtual_env.run(f"deptry src -o {issue_report}")

        assert result.returncode == 1
        assert get_issues_report(Path(issue_report)) == [
            {
                "error": {
                    "code": "DEP004",
                    "message": "'black' imported but declared as a dev dependency",
                },
                "module": "black",
                "location": {"file": str(Path("src/main.py")), "line": 3, "column": 8},
            },
            {
                "error": {
                    "code": "DEP001",
                    "message": "'gray' imported but missing from the dependency definitions",
                },
                "module": "gray",
                "location": {"file": str(Path("src/main.py")), "line": 6, "column": 8},
            },
        ]


@pytest.mark.xdist_group(name=Project.INLINE_IGNORES)
def test_cli_inline_ignore_combined_with_per_rule_ignores_flag(pip_venv_factory: PipVenvFactory) -> None:
    """Verify that inline ignore comments and the --per-rule-ignores CLI flag work together.

    The inline comment suppresses DEP001 for 'white', and the CLI flag suppresses DEP004 for
    'black', DEP001 for 'gray', and DEP002 for 'requests' (note: the CLI flag overrides
    the pyproject.toml per_rule_ignores, so DEP002=requests must be repeated here).
    With all mechanisms active, no violations should remain."""
    with pip_venv_factory(Project.INLINE_IGNORES) as virtual_env:
        result = virtual_env.run("deptry src --per-rule-ignores DEP002=requests,DEP004=black,DEP001=gray")

        assert result.returncode == 0


@pytest.mark.xdist_group(name=Project.INLINE_IGNORES)
def test_cli_inline_ignore_combined_with_ignore_flag(pip_venv_factory: PipVenvFactory) -> None:
    """Verify that inline ignore comments and the --ignore CLI flag work together.

    The --ignore flag disables DEP004 entirely, the inline comment suppresses DEP001 for 'white',
    and the pyproject.toml suppresses DEP002 for 'requests'.  Only the DEP001 for 'gray' (whose
    inline ignore targets the wrong rule code) should remain."""
    with pip_venv_factory(Project.INLINE_IGNORES) as virtual_env:
        issue_report = f"{uuid.uuid4()}.json"
        result = virtual_env.run(f"deptry src --ignore DEP004 -o {issue_report}")

        assert result.returncode == 1
        assert get_issues_report(Path(issue_report)) == [
            {
                "error": {
                    "code": "DEP001",
                    "message": "'gray' imported but missing from the dependency definitions",
                },
                "module": "gray",
                "location": {"file": str(Path("src/main.py")), "line": 6, "column": 8},
            },
        ]
