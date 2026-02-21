from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from inline_snapshot import snapshot

from tests.functional.utils import Project

if TYPE_CHECKING:
    from tests.utils import PipVenvFactory


@pytest.mark.xdist_group(name=Project.REQUIREMENTS_TXT)
def test_cli_single_requirements_files(pip_venv_factory: PipVenvFactory) -> None:
    with pip_venv_factory(
        Project.REQUIREMENTS_TXT,
        install_command=(
            "pip install -r requirements.txt -r requirements-dev.txt -r requirements-2.txt -r requirements-typing.txt"
        ),
    ) as virtual_env:
        result = virtual_env.run_deptry(
            ". --requirements-files requirements.txt --requirements-files-dev requirements-dev.txt"
        )

        assert result.returncode == 1
        assert result.stderr == snapshot("""\
Scanning 2 files...

requirements.txt: DEP002 'isort' defined as a dependency but not used in the codebase
requirements.txt: DEP002 'requests' defined as a dependency but not used in the codebase
src/main.py:4:8: DEP004 'black' imported but declared as a dev dependency
src/main.py:6:8: DEP001 'white' imported but missing from the dependency definitions
src/main.py:7:1: DEP003 'urllib3' imported but it is a transitive dependency
src/notebook.ipynb:2:1: DEP003 'urllib3' imported but it is a transitive dependency
Found 6 dependency issues.

For more information, see the documentation: https://deptry.com/
""")


@pytest.mark.xdist_group(name=Project.REQUIREMENTS_TXT)
def test_cli_multiple_requirements_files(pip_venv_factory: PipVenvFactory) -> None:
    with pip_venv_factory(
        Project.REQUIREMENTS_TXT,
        install_command=(
            "pip install -r requirements.txt -r requirements-dev.txt -r requirements-2.txt -r requirements-typing.txt"
        ),
    ) as virtual_env:
        result = virtual_env.run_deptry(
            ". --requirements-files requirements.txt,requirements-2.txt --requirements-files-dev requirements-dev.txt"
        )

        assert result.returncode == 1
        assert result.stderr == snapshot("""\
Scanning 2 files...

requirements.txt: DEP002 'isort' defined as a dependency but not used in the codebase
requirements.txt: DEP002 'requests' defined as a dependency but not used in the codebase
src/main.py:4:8: DEP004 'black' imported but declared as a dev dependency
src/main.py:6:8: DEP001 'white' imported but missing from the dependency definitions
Found 4 dependency issues.

For more information, see the documentation: https://deptry.com/
""")
