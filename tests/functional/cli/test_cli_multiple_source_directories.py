from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from inline_snapshot import snapshot

from tests.functional.utils import Project

if TYPE_CHECKING:
    from tests.utils import PipVenvFactory


@pytest.mark.xdist_group(name=Project.MULTIPLE_SOURCE_DIRECTORIES)
def test_cli_with_multiple_source_directories(pip_venv_factory: PipVenvFactory) -> None:
    with pip_venv_factory(Project.MULTIPLE_SOURCE_DIRECTORIES) as virtual_env:
        result = virtual_env.run_deptry("src worker")

        assert result.returncode == 1
        assert result.stderr == snapshot("""\
Scanning 6 files...

pyproject.toml: DEP002 'arrow' defined as a dependency but not used in the codebase
src/foo.py:1:8: DEP001 'httpx' imported but missing from the dependency definitions
worker/foo.py:1:8: DEP001 'celery' imported but missing from the dependency definitions
Found 3 dependency issues.

For more information, see the documentation: https://deptry.com/
""")
