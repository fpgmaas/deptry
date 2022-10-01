import json
import pathlib
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


@pytest.fixture(scope="session")
def requirements_txt_dir_with_venv_installed(tmp_path_factory):
    tmp_path_proj = tmp_path_factory.getbasetemp() / "project_with_requirements_txt"
    shutil.copytree("tests/data/project_with_requirements_txt", str(tmp_path_proj))
    with run_within_dir(str(tmp_path_proj)):
        subprocess.check_call(
            shlex.split(
                "pip install -r requirements.txt -r requirements-dev.txt -r requirements-2.txt -r"
                " requirements-typing.txt"
            )
        ) == 0
    return tmp_path_proj


def test_cli_returns_error(dir_with_venv_installed):
    with run_within_dir(str(dir_with_venv_installed)):
        result = subprocess.run(shlex.split("poetry run deptry ."), capture_output=True, text=True)
        assert result.returncode == 1
        print(result.stderr)
        assert "The project contains obsolete dependencies:\n\n\tisort\n\trequests\n\n" in result.stderr
        assert "There are dependencies missing from the project's list of dependencies:\n\n\twhite\n\n" in result.stderr
        assert "There are imported modules from development dependencies detected:\n\n\tblack\n\n" in result.stderr


def test_cli_ignore_notebooks(dir_with_venv_installed):
    with run_within_dir(str(dir_with_venv_installed)):
        result = subprocess.run(shlex.split("poetry run deptry . --ignore-notebooks"), capture_output=True, text=True)
        assert result.returncode == 1
        assert "The project contains obsolete dependencies:\n\n\tisort\n\trequests\n\ttoml\n\n" in result.stderr


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
        assert "The project contains obsolete dependencies:\n\n\tisort\n\trequests\n\ttoml\n\n" in result.stderr


def test_cli_extend_exclude(dir_with_venv_installed):
    with run_within_dir(str(dir_with_venv_installed)):
        result = subprocess.run(
            shlex.split("poetry run deptry . -ee src/notebook.ipynb "), capture_output=True, text=True
        )
        assert result.returncode == 1
        assert "The project contains obsolete dependencies:\n\n\tisort\n\trequests\n\ttoml\n\n" in result.stderr


def test_cli_single_requirements_txt(requirements_txt_dir_with_venv_installed):
    with run_within_dir(str(requirements_txt_dir_with_venv_installed)):
        result = subprocess.run(
            shlex.split("deptry . --requirements-txt requirements.txt --requirements-txt-dev requirements-dev.txt"),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert (
            "The project contains obsolete dependencies:\n\n\tisort\n\trequests\n\nConsider removing them from your"
            " project's dependencies. If a package is used for development purposes, you should add it to your"
            " development dependencies instead.\n\n-----------------------------------------------------\n\nThere are"
            " dependencies missing from the project's list of dependencies:\n\n\twhite\n\nConsider adding them to your"
            " project's dependencies. \n\n-----------------------------------------------------\n\nThere are transitive"
            " dependencies that should be explicitly defined as dependencies:\n\n\turllib3\n\nThey are currently"
            " imported but not specified directly as your project's"
            " dependencies.\n\n-----------------------------------------------------\n\nThere are imported modules from"
            " development dependencies detected:\n\n\tblack\n\n"
            in result.stderr
        )


def test_cli_multiple_requirements_txt(requirements_txt_dir_with_venv_installed):
    with run_within_dir(str(requirements_txt_dir_with_venv_installed)):
        result = subprocess.run(
            shlex.split(
                "deptry . --requirements-txt requirements.txt,requirements-2.txt --requirements-txt-dev"
                " requirements-dev.txt,requirements-typing.txt"
            ),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert (
            "The project contains obsolete dependencies:\n\n\tisort\n\trequests\n\nConsider removing them from your"
            " project's dependencies. If a package is used for development purposes, you should add it to your"
            " development dependencies instead.\n\n-----------------------------------------------------\n\nThere are"
            " dependencies missing from the project's list of dependencies:\n\n\twhite\n\nConsider adding them to your"
            " project's dependencies. \n\n-----------------------------------------------------\n\nThere are imported"
            " modules from development dependencies detected:\n\n\tblack\n\n"
            in result.stderr
        )


def test_cli_verbose(dir_with_venv_installed):
    with run_within_dir(str(dir_with_venv_installed)):
        result = subprocess.run(shlex.split("poetry run deptry . "), capture_output=True, text=True)
        assert result.returncode == 1
        assert not "The project contains the following dependencies:" in result.stderr

    with run_within_dir(str(dir_with_venv_installed)):
        result = subprocess.run(shlex.split("poetry run deptry . -v "), capture_output=True, text=True)
        assert result.returncode == 1
        assert "The project contains the following dependencies:" in result.stderr


def test_cli_with_json_output(dir_with_venv_installed):
    with run_within_dir(str(dir_with_venv_installed)):
        # assert that there is no json output
        subprocess.run(shlex.split("poetry run deptry ."), capture_output=True, text=True)
        assert len(list(pathlib.Path(".").glob("*.json"))) == 0

        # assert that there is json output
        subprocess.run(shlex.split("poetry run deptry . -o deptry.json"), capture_output=True, text=True)
        with open("deptry.json", "r") as f:
            data = json.load(f)
        assert set(data["obsolete"]) == set(["isort", "requests"])
        assert set(data["missing"]) == set(["white"])
        assert set(data["misplaced_dev"]) == set(["black"])
        assert set(data["transitive"]) == set([])


def test_cli_help():
    subprocess.check_call(shlex.split("deptry --help")) == 0
