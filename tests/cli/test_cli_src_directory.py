import shlex
import shutil
import subprocess
from pathlib import Path

import pytest
from _pytest.tmpdir import TempPathFactory

from tests.utils import run_within_dir


@pytest.fixture(scope="session")
def pep_621_dir_with_src_directory(tmp_path_factory: TempPathFactory) -> Path:
    tmp_path_proj = tmp_path_factory.getbasetemp() / "project_with_src_directory"
    shutil.copytree("tests/data/project_with_src_directory", str(tmp_path_proj))
    with run_within_dir(tmp_path_proj):
        assert subprocess.check_call(shlex.split("pip install .")) == 0
    return tmp_path_proj


def test_cli_with_src_directory(pep_621_dir_with_src_directory: Path) -> None:
    with run_within_dir(pep_621_dir_with_src_directory):
        result = subprocess.run(shlex.split("deptry src"), capture_output=True, text=True)
        assert result.returncode == 1
        assert (
            "The project contains obsolete dependencies:\n\n\tisort\n\tmypy\n\tpytest\n\trequests\n\n" in result.stderr
        )
        assert "There are dependencies missing from the project's list of dependencies:\n\n\twhite\n\n" in result.stderr
