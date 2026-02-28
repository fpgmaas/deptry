from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from inline_snapshot import snapshot

from tests.functional.utils import Project

if TYPE_CHECKING:
    from tests.utils import PipVenvFactory


@pytest.mark.xdist_group(name=Project.SETUPTOOLS_DYNAMIC_DEPENDENCIES)
def test_cli_setuptools_dynamic_dependencies(pip_venv_factory: PipVenvFactory) -> None:
    with pip_venv_factory(
        Project.SETUPTOOLS_DYNAMIC_DEPENDENCIES,
        install_command="pip install -r requirements.txt -r requirements-2.txt -r cli-requirements.txt -r dev-requirements.txt",
    ) as virtual_env:
        result = virtual_env.run_deptry(".")

        assert result.returncode == 1
        assert result.stderr == snapshot("""\
Scanning 2 files...

requirements-2.txt: DEP002 'packaging' defined as a dependency but not used in the codebase
requirements.txt: DEP002 'pkginfo' defined as a dependency but not used in the codebase
requirements.txt: DEP002 'requests' defined as a dependency but not used in the codebase
src/main.py:5:8: DEP004 'isort' imported but declared as a dev dependency
src/main.py:6:8: DEP001 'white' imported but missing from the dependency definitions
src/main.py:7:1: DEP003 'urllib3' imported but it is a transitive dependency
src/notebook.ipynb:2:1: DEP003 'urllib3' imported but it is a transitive dependency
Found 7 dependency issues.

For more information, see the documentation: https://deptry.com/
""")
