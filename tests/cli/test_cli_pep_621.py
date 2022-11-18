import shlex
import shutil
import subprocess
from pathlib import Path

import pytest
from _pytest.tmpdir import TempPathFactory

from deptry.utils import run_within_dir


@pytest.fixture(scope="session")
def pep_621_dir_with_venv_installed(tmp_path_factory: TempPathFactory) -> Path:
    tmp_path_proj = tmp_path_factory.getbasetemp() / "pep_621_project"
    shutil.copytree("tests/data/pep_621_project", str(tmp_path_proj))
    with run_within_dir(tmp_path_proj):
        assert subprocess.check_call(shlex.split("pip install .")) == 0
    return tmp_path_proj


def test_cli_with_pep_621(pep_621_dir_with_venv_installed: Path) -> None:
    with run_within_dir(pep_621_dir_with_venv_installed):
        result = subprocess.run(shlex.split("deptry ."), capture_output=True, text=True)
        assert result.returncode == 1
        print(result.stderr)
        assert (
            "The project contains obsolete dependencies:\n\n\tisort\n\tmypy\n\tpytest\n\trequests\n\n" in result.stderr
        )
        assert "There are dependencies missing from the project's list of dependencies:\n\n\twhite\n\n" in result.stderr
