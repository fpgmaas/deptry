import pytest

from deptry.utils import (
    find_site_packages_below,
    guess_virtualenv_site_packages,
    in_project_virtualenv,
    load_pyproject_toml,
)


def test_load_pyproject_toml() -> None:
    assert load_pyproject_toml("tests/data/example_project/pyproject.toml") == {
        "tool": {
            "deptry": {"ignore_obsolete": ["pkginfo"]},
            "poetry": {
                "authors": ["test <test@test.com>"],
                "dependencies": {
                    "click": "^8.1.3",
                    "isort": "^5.10.1",
                    "pkginfo": "^1.8.3",
                    "python": ">=3.7,<4.0",
                    "requests": "^2.28.1",
                    "toml": "^0.10.2",
                    "urllib3": "^1.26.12",
                },
                "description": "A test project",
                "dev-dependencies": {"black": "^22.6.0"},
                "name": "test",
                "version": "0.0.1",
            },
        }
    }


def test_find_site_packages_below(tmp_path):
    d = tmp_path / "lib" / "python3.8" / "site-packages"
    d.mkdir(parents=True)
    assert find_site_packages_below(tmp_path, "Linux") == d


def test_find_site_packages_below_windows(tmp_path):
    d = tmp_path / "Lib" / "site-packages"
    d.mkdir(parents=True)
    assert find_site_packages_below(tmp_path, "Windows") == d


def test_find_site_packages_below_missing(tmp_path):
    assert find_site_packages_below(tmp_path, "Linux") is None


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
def test_in_project_virtualenv(params, expected):
    arg_names = ("project_name", "base_prefix", "prefix", "active_virtual_env")
    kwargs = dict(zip(arg_names, params))
    assert in_project_virtualenv(**kwargs) == expected


def test_guess_site_packages(tmp_path):
    d = tmp_path / ".venv" / "lib" / "python3.10" / "site-packages"
    d.mkdir(parents=True)
    assert guess_virtualenv_site_packages(tmp_path, "Linux") == d


def test_guess_site_packages_active_venv(tmp_path):
    project_root = tmp_path / "project"
    project_root.mkdir()

    active_virtual_env = tmp_path / "virtualenv"
    d = active_virtual_env / "lib" / "python3.10" / "site-packages"
    d.mkdir(parents=True)

    assert guess_virtualenv_site_packages(project_root, "Linux", active_virtual_env) == d
