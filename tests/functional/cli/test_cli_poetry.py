from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from inline_snapshot import snapshot

from tests.functional.utils import Project

if TYPE_CHECKING:
    from tests.utils import PoetryVenvFactory


@pytest.mark.xdist_group(name=Project.POETRY)
def test_cli_with_poetry(poetry_venv_factory: PoetryVenvFactory) -> None:
    with poetry_venv_factory(Project.POETRY) as virtual_env:
        result = virtual_env.run_deptry(".")

        assert result.returncode == 1
        assert result.stderr == snapshot("""\
Assuming the corresponding module name of package 'isort' is 'isort'. Install the package or configure a package_module_name_map entry to override this behaviour.
Assuming the corresponding module name of package 'requests' is 'requests'. Install the package or configure a package_module_name_map entry to override this behaviour.
Scanning 2 files...

pyproject.toml: DEP002 'isort' defined as a dependency but not used in the codebase
pyproject.toml: DEP002 'requests' defined as a dependency but not used in the codebase
src/main.py:4:8: DEP004 'black' imported but declared as a dev dependency
src/main.py:6:8: DEP004 'mypy' imported but declared as a dev dependency
src/main.py:7:8: DEP004 'pytest' imported but declared as a dev dependency
src/main.py:8:8: DEP004 'pytest_cov' imported but declared as a dev dependency
src/main.py:9:8: DEP001 'white' imported but missing from the dependency definitions
Found 7 dependency issues.

For more information, see the documentation: https://deptry.com/
""")
