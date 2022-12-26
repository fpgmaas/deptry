import json
import shlex
import shutil
import subprocess
from pathlib import Path

import pytest
from _pytest.tmpdir import TempPathFactory

from tests.utils import run_within_dir


@pytest.fixture(scope="session")
def dir_with_venv_installed(tmp_path_factory: TempPathFactory) -> Path:
    tmp_path_proj = tmp_path_factory.getbasetemp() / "example_project"
    shutil.copytree("tests/data/example_project", tmp_path_proj)
    with run_within_dir(tmp_path_proj):
        assert subprocess.check_call(shlex.split("poetry install --no-interaction --no-root")) == 0
    return tmp_path_proj


def test_cli_returns_error(dir_with_venv_installed: Path) -> None:
    with run_within_dir(dir_with_venv_installed):
        result = subprocess.run(shlex.split("poetry run deptry ."), capture_output=True, text=True)
        assert result.returncode == 1
        print(result.stderr)
        assert "The project contains obsolete dependencies:\n\n\tisort\n\trequests\n\n" in result.stderr
        assert "There are dependencies missing from the project's list of dependencies:\n\n\twhite\n\n" in result.stderr
        assert "There are imported modules from development dependencies detected:\n\n\tblack\n\n" in result.stderr


def test_cli_ignore_notebooks(dir_with_venv_installed: Path) -> None:
    with run_within_dir(dir_with_venv_installed):
        result = subprocess.run(shlex.split("poetry run deptry . --ignore-notebooks"), capture_output=True, text=True)
        assert result.returncode == 1
        assert "The project contains obsolete dependencies:\n\n\tisort\n\trequests\n\ttoml\n\n" in result.stderr


def test_cli_ignore_flags(dir_with_venv_installed: Path) -> None:
    with run_within_dir(dir_with_venv_installed):
        result = subprocess.run(
            shlex.split("poetry run deptry . --ignore-obsolete isort,pkginfo,requests -im white -id black"),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0


def test_cli_skip_flags(dir_with_venv_installed: Path) -> None:
    with run_within_dir(dir_with_venv_installed):
        result = subprocess.run(
            shlex.split("poetry run deptry . --skip-obsolete --skip-missing --skip-misplaced-dev --skip-transitive"),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0


def test_cli_exclude(dir_with_venv_installed: Path) -> None:
    with run_within_dir(dir_with_venv_installed):
        result = subprocess.run(
            shlex.split("poetry run deptry . --exclude src/notebook.ipynb "), capture_output=True, text=True
        )
        assert result.returncode == 1
        assert "The project contains obsolete dependencies:\n\n\tisort\n\trequests\n\ttoml\n\n" in result.stderr


def test_cli_extend_exclude(dir_with_venv_installed: Path) -> None:
    with run_within_dir(dir_with_venv_installed):
        result = subprocess.run(
            shlex.split("poetry run deptry . -ee src/notebook.ipynb "), capture_output=True, text=True
        )
        assert result.returncode == 1
        assert "The project contains obsolete dependencies:\n\n\tisort\n\trequests\n\ttoml\n\n" in result.stderr


def test_cli_verbose(dir_with_venv_installed: Path) -> None:
    with run_within_dir(dir_with_venv_installed):
        result = subprocess.run(shlex.split("poetry run deptry . "), capture_output=True, text=True)
        assert result.returncode == 1
        assert "The project contains the following dependencies:" not in result.stderr

    with run_within_dir(dir_with_venv_installed):
        result = subprocess.run(shlex.split("poetry run deptry . -v "), capture_output=True, text=True)
        assert result.returncode == 1
        assert "The project contains the following dependencies:" in result.stderr


def test_cli_with_json_output(dir_with_venv_installed: Path) -> None:
    with run_within_dir(dir_with_venv_installed):
        # assert that there is no json output
        subprocess.run(shlex.split("poetry run deptry ."), capture_output=True, text=True)
        assert len(list(Path(".").glob("*.json"))) == 0

        # assert that there is json output
        subprocess.run(shlex.split("poetry run deptry . -o deptry.json"), capture_output=True, text=True)
        with open("deptry.json") as f:
            data = json.load(f)
        assert set(data["obsolete"]) == {"isort", "requests"}
        assert set(data["missing"]) == {"white"}
        assert set(data["misplaced_dev"]) == {"black"}
        assert set(data["transitive"]) == set()


def test_cli_help() -> None:
    assert subprocess.check_call(shlex.split("deptry --help")) == 0
