import pytest

from deptry.virtualenv_finder import (
    ExecutionContext,
    find_site_packages_in,
    guess_virtualenv_site_packages,
)


def test_find_site_packages_in(tmp_path):
    d = tmp_path / "lib" / "python3.8" / "site-packages"
    d.mkdir(parents=True)
    assert find_site_packages_in(tmp_path) == d


def test_find_site_packages_in_windows(tmp_path):
    d = tmp_path / "Lib" / "site-packages"
    d.mkdir(parents=True)
    assert find_site_packages_in(tmp_path) == d


def test_find_site_packages_in_missing(tmp_path):
    assert find_site_packages_in(tmp_path) is None


@pytest.mark.parametrize(
    "params, expected",
    [
        # Global installation
        (("theproject", "/usr", "/usr", None), False),
        # Direct invocation with project interpreter
        (("theproject", "/usr", "/home/user/.virtualenvs/theproject", None), True),
        # Pipx global install. Project virtualenv active
        (("theproject", "/usr", "/home/user/.local/pipx/venvs/deptry", "/home/user/theproject/.venv"), False),
        # Project virtualenv active and running
        (("theproject", "/usr", "/home/user/theproject/.venv", "/home/user/theproject/.venv"), True),
    ],
)
def test_running_in_project_virtualenv(params, expected):
    arg_names = ("project_name", "base_prefix", "prefix", "active_virtual_env")
    kwargs = dict(zip(arg_names, params))
    ctx = ExecutionContext(**kwargs)
    assert ctx.running_in_project_virtualenv() == expected


def test_guess_site_packages(tmp_path):
    d = tmp_path / ".venv" / "lib" / "python3.10" / "site-packages"
    d.mkdir(parents=True)
    assert guess_virtualenv_site_packages(tmp_path) == d


def test_guess_site_packages_active_venv(tmp_path):
    project_root = tmp_path / "project"
    project_root.mkdir()

    active_virtual_env = tmp_path / "virtualenv"
    d = active_virtual_env / "lib" / "python3.10" / "site-packages"
    d.mkdir(parents=True)

    assert guess_virtualenv_site_packages(project_root, active_virtual_env) == d
