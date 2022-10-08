import shlex
import shutil
import subprocess

import pytest

from deptry.utils import run_within_dir


@pytest.fixture(scope="session")
def requirements_txt_dir_with_venv_installed(tmp_path_factory):
    tmp_path_proj = tmp_path_factory.getbasetemp() / "project_with_requirements_txt"
    shutil.copytree("tests/data/project_with_requirements_txt", str(tmp_path_proj))
    with run_within_dir(tmp_path_proj):
        assert (
            subprocess.check_call(
                shlex.split(
                    "pip install -r requirements.txt -r requirements-dev.txt -r requirements-2.txt -r"
                    " requirements-typing.txt"
                )
            )
            == 0
        )
    return tmp_path_proj


def test_cli_single_requirements_txt(requirements_txt_dir_with_venv_installed):
    with run_within_dir(requirements_txt_dir_with_venv_installed):
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
    with run_within_dir(requirements_txt_dir_with_venv_installed):
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
