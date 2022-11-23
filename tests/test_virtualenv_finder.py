from pathlib import Path

import pytest

from deptry.metadata_finder import ExecutionContext


@pytest.mark.parametrize(
    "params, expected",
    [
        # Global installation
        ((Path("theproject"), "/usr", "/usr", None), False),
        # Direct invocation with project interpreter
        ((Path("theproject"), "/usr", "/home/user/.virtualenvs/theproject", None), True),
        # Pipx global install. Project virtualenv active
        ((Path("theproject"), "/usr", "/home/user/.local/pipx/venvs/deptry", "/home/user/theproject/.venv"), False),
        # Project virtualenv active and running
        ((Path("theproject"), "/usr", "/home/user/theproject/.venv", "/home/user/theproject/.venv"), True),
    ],
)
def test_running_in_project_virtualenv(params, expected):
    arg_names = ("project_root", "base_prefix", "prefix", "active_virtual_env")
    kwargs = dict(zip(arg_names, params))
    ctx = ExecutionContext(**kwargs)
    assert ctx.running_in_project_virtualenv() == expected
