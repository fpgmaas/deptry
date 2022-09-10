import shlex
import shutil
import subprocess

import pytest

from deptry.utils import run_within_dir


@pytest.fixture(scope="session")
def dir_with_venv_installed(tmp_path_factory):
    tmp_path_proj = tmp_path_factory.getbasetemp() / "example_project"
    shutil.copytree("tests/data/example_project", str(tmp_path_proj))
    with run_within_dir(str(tmp_path_proj)):
        subprocess.check_call(shlex.split("poetry install --no-interaction --no-root")) == 0
    return tmp_path_proj


def test_cli_returns_error(dir_with_venv_installed):
    with run_within_dir(str(dir_with_venv_installed)):
        result = subprocess.run(shlex.split("poetry run deptry ."), capture_output=True, text=True)
        assert result.returncode == 1
        assert "pyproject.toml contains obsolete dependencies:\n\n\tisort\n\trequests\n\n" in result.stderr
        assert "There are dependencies missing from pyproject.toml:\n\n\twhite\n\n" in result.stderr
        assert "There are imported modules from development dependencies detected:\n\n\tblack\n\n" in result.stderr


def test_cli_ignore_notebooks(dir_with_venv_installed):
    with run_within_dir(str(dir_with_venv_installed)):
        result = subprocess.run(shlex.split("poetry run deptry . --ignore-notebooks"), capture_output=True, text=True)
        assert result.returncode == 1
        assert "pyproject.toml contains obsolete dependencies:\n\n\tisort\n\trequests\n\ttoml\n\n" in result.stderr


def test_cli_ignore_flags(dir_with_venv_installed):
    with run_within_dir(str(dir_with_venv_installed)):
        result = subprocess.run(
            shlex.split("poetry run deptry . --ignore-obsolete isort,pkginfo,requests -im white -id black"),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0


def test_cli_skip_flags(dir_with_venv_installed):
    with run_within_dir(str(dir_with_venv_installed)):
        result = subprocess.run(
            shlex.split("poetry run deptry . --skip-obsolete --skip-missing --skip-misplaced-dev --skip-transitive"),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0


def test_cli_exclude(dir_with_venv_installed):
    with run_within_dir(str(dir_with_venv_installed)):
        result = subprocess.run(
            shlex.split("poetry run deptry . --exclude src/notebook.ipynb "), capture_output=True, text=True
        )
        assert result.returncode == 1
        assert "pyproject.toml contains obsolete dependencies:\n\n\tisort\n\trequests\n\ttoml\n\n" in result.stderr


def test_cli_extend_exclude(dir_with_venv_installed):
    with run_within_dir(str(dir_with_venv_installed)):
        result = subprocess.run(
            shlex.split("poetry run deptry . -ee src/notebook.ipynb "), capture_output=True, text=True
        )
        assert result.returncode == 1
        assert "pyproject.toml contains obsolete dependencies:\n\n\tisort\n\trequests\n\ttoml\n\n" in result.stderr


def test_cli_help():
    subprocess.check_call(shlex.split("deptry --help")) == 0
