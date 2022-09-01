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

    tmp_path_proj = tmp_path / "project_with_missing_imports"
    shutil.copytree("tests/projects/project_with_missing_imports", tmp_path_proj)

    with run_within_dir(str(tmp_path_proj)):
        subprocess.check_call(shlex.split("poetry install --no-interaction --no-root")) == 0
        result = subprocess.run(shlex.split("poetry run deptry check"), capture_output=True, text=True)
        assert result.returncode == 1
        assert (
            result.stderr
            == "pyproject.toml contains obsolete dependencies: ['click', 'cookiecutter-poetry', 'isort']\n"
        )


def test_cli_returns_no_error(tmp_path):

    tmp_path_proj = tmp_path / "project_without_missing_imports"
    shutil.copytree("tests/projects/project_without_missing_imports", tmp_path_proj)

    with run_within_dir(str(tmp_path_proj)):
        subprocess.check_call(shlex.split("poetry install --no-interaction --no-root")) == 0
        result = subprocess.run(shlex.split("poetry run deptry check"), capture_output=True, text=True)
        assert result.returncode == 0


def test_cli_help():
    subprocess.check_call(shlex.split("deptry --help")) == 0
