import shlex
import shutil
import subprocess

import pytest

from deptry.utils import run_within_dir


@pytest.fixture(scope="session")
def pdm_dir_with_venv_installed(tmp_path_factory):
    tmp_path_proj = tmp_path_factory.getbasetemp() / "project_with_pdm"
    shutil.copytree("tests/data/project_with_pdm", str(tmp_path_proj))
    with run_within_dir(tmp_path_proj):
        assert (
            subprocess.check_call(
                shlex.split("pip install pdm; pdm install")
            )
            == 0
        )
    return tmp_path_proj


def test_cli_with_pdm(pdm_dir_with_venv_installed):
    with run_within_dir(pdm_dir_with_venv_installed):
        result = subprocess.run(shlex.split("deptry ."), capture_output=True, text=True)
        assert result.returncode == 1
        print(result.stderr)
        assert "The project contains obsolete dependencies:\n\n\tisort\n\trequests\n\n" in result.stderr
        assert "There are dependencies missing from the project's list of dependencies:\n\n\twhite\n\n" in result.stderr
        assert "There are imported modules from development dependencies detected:\n\n\tblack\n\n" in result.stderr
