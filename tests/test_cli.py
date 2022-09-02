import os
import shlex
import shutil
import subprocess
from contextlib import contextmanager

import pytest


@contextmanager
def run_within_dir(path: str):
    oldpwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldpwd)


def test_cli_returns_error(tmp_path):
    """
    data/projects/project_with_obsolete has obsolete dependencies.
    Verify that `deptry check` returns status code 1
    and verify that it finds the right obsolete dependencies.
    """

    tmp_path_proj = tmp_path / "project_with_obsolete"
    shutil.copytree("tests/data/projects/project_with_obsolete", tmp_path_proj)

    with run_within_dir(str(tmp_path_proj)):
        subprocess.check_call(shlex.split("poetry install --no-interaction --no-root")) == 0
        result = subprocess.run(shlex.split("poetry run deptry check"), capture_output=True, text=True)
        assert result.returncode == 1
        assert result.stderr == "pyproject.toml contains obsolete dependencies: ['isort']\n"

        result = subprocess.run(shlex.split("poetry run deptry check --ignore-notebooks"), capture_output=True, text=True)
        assert result.returncode == 1
        assert result.stderr == "pyproject.toml contains obsolete dependencies: ['cookiecutter-poetry', 'isort']\n"


def test_cli_returns_no_error(tmp_path):
    """
    data/projects/project_without_obsolete has no obsolete dependencies.
    Verify that `deptry check` completes with status code 0.
    """

    tmp_path_proj = tmp_path / "project_without_obsolete"
    shutil.copytree("tests/data/projects/project_without_obsolete", tmp_path_proj)

    with run_within_dir(str(tmp_path_proj)):
        subprocess.check_call(shlex.split("poetry install --no-interaction --no-root")) == 0
        result = subprocess.run(shlex.split("poetry run deptry check"), capture_output=True, text=True)
        assert result.returncode == 0


def test_cli_argument_overwrites_pyproject_toml_argument(tmp_path):
    """
    The cli argument should overwrite the pyproject.toml argument. In project_with_obsolete, pyproject.toml specifies
    to ignore 'toml' and the obsolete dependencies are ['click', 'cookiecutter-poetry', 'isort'].
    Verify that this is changed to ['cookiecutter-poetry', 'isort', 'toml'] if we run the command with `-i click`
    """

    tmp_path_proj = tmp_path / "project_with_obsolete"
    shutil.copytree("tests/data/projects/project_with_obsolete", tmp_path_proj)

    with run_within_dir(str(tmp_path_proj)):
        subprocess.check_call(shlex.split("poetry install --no-interaction --no-root")) == 0
        result = subprocess.run(shlex.split("poetry run deptry check -i click"), capture_output=True, text=True)
        assert result.returncode == 1
        assert (
            result.stderr == "pyproject.toml contains obsolete dependencies: ['cookiecutter-poetry', 'isort', 'toml']\n"
        )


def test_cli_help():
    subprocess.check_call(shlex.split("deptry --help")) == 0
