from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from inline_snapshot import snapshot

from tests.functional.utils import Project

if TYPE_CHECKING:
    from tests.utils import PipVenvFactory


@pytest.mark.xdist_group(name=Project.NAMESPACE)
def test_cli_with_namespace(pip_venv_factory: PipVenvFactory) -> None:
    with pip_venv_factory(Project.NAMESPACE) as virtual_env:
        result = virtual_env.run_deptry(". --experimental-namespace-package")

        assert result.returncode == 1
        assert result.stderr == snapshot("""\
Assuming the corresponding module name of package 'flake8' is 'flake8'. Install the package or configure a package_module_name_map entry to override this behaviour.
Scanning 2 files...

foo/database/bar.py:4:8: DEP004 'flake8' imported but declared as a dev dependency
foo/database/bar.py:5:8: DEP001 'white' imported but missing from the dependency definitions
pyproject.toml: DEP002 'arrow' defined as a dependency but not used in the codebase
Found 3 dependency issues.

For more information, see the documentation: https://deptry.com/
""")


@pytest.mark.xdist_group(name=Project.NAMESPACE)
def test_cli_with_namespace_without_experimental_flag(pip_venv_factory: PipVenvFactory) -> None:
    with pip_venv_factory(Project.NAMESPACE) as virtual_env:
        result = virtual_env.run_deptry(".")

        assert result.returncode == 1
        assert result.stderr == snapshot("""\
Assuming the corresponding module name of package 'flake8' is 'flake8'. Install the package or configure a package_module_name_map entry to override this behaviour.
Scanning 2 files...

foo/database/bar.py:4:8: DEP004 'flake8' imported but declared as a dev dependency
foo/database/bar.py:5:8: DEP001 'white' imported but missing from the dependency definitions
foo/database/bar.py:7:1: DEP003 'foo' imported but it is a transitive dependency
pyproject.toml: DEP002 'arrow' defined as a dependency but not used in the codebase
Found 4 dependency issues.

For more information, see the documentation: https://deptry.com/
""")
