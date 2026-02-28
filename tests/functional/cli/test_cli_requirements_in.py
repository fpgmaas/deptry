from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import pytest
from inline_snapshot import snapshot

from tests.functional.utils import Project

if TYPE_CHECKING:
    from tests.utils import PipVenvFactory


@pytest.mark.xdist_group(name=Project.REQUIREMENTS_IN)
def test_cli_single_requirements_files(pip_venv_factory: PipVenvFactory) -> None:
    """
    in this case, deptry should recognize that there is a `requirements.in` in the project, and
    use that as the source of the dependencies.
    """
    with pip_venv_factory(
        Project.REQUIREMENTS_IN,
        install_command=("pip install -r requirements.txt -r requirements-dev.txt"),
    ) as virtual_env:
        result = virtual_env.run_deptry(".")

        assert result.returncode == 1
        assert result.stderr == snapshot("""\
Detected a 'requirements.in' file in the project and no 'requirements-files' were explicitly specified. Automatically using 'requirements.in' as the source for the project's dependencies. To specify a different source for the project's dependencies, use the '--requirements-files' option.
Scanning 2 files...

requirements.in: DEP002 'isort' defined as a dependency but not used in the codebase
requirements.in: DEP002 'uvicorn' defined as a dependency but not used in the codebase
src/main.py:4:8: DEP004 'black' imported but declared as a dev dependency
src/main.py:6:8: DEP003 'h11' imported but it is a transitive dependency
src/main.py:7:8: DEP001 'white' imported but missing from the dependency definitions
src/main.py:9:8: DEP003 'bs4' imported but it is a transitive dependency
src/notebook.ipynb:3:8: DEP001 'arrow' imported but missing from the dependency definitions
Found 7 dependency issues.

For more information, see the documentation: https://deptry.com/
""")


@pytest.mark.xdist_group(name=Project.REQUIREMENTS_IN)
def test_cli_multiple_requirements_files(pip_venv_factory: PipVenvFactory) -> None:
    """
    in this case, deptry recognizes that there is a `requirements.in` in the project, but the user
    can overwrite that with '--requirements-files requirements.txt', so it still takes requirements.txt as the source
    for the project's dependencies.
    """
    with pip_venv_factory(
        Project.REQUIREMENTS_IN,
        install_command=("pip install -r requirements.txt -r requirements-dev.txt"),
    ) as virtual_env:
        issue_report = f"{uuid.uuid4()}.json"
        result = virtual_env.run_deptry(f". --requirements-files requirements.txt -o {issue_report}")

        assert result.returncode == 1
        assert result.stderr == snapshot("""\
Scanning 2 files...

requirements.txt: DEP002 'args' defined as a dependency but not used in the codebase
requirements.txt: DEP002 'certifi' defined as a dependency but not used in the codebase
requirements.txt: DEP002 'charset-normalizer' defined as a dependency but not used in the codebase
requirements.txt: DEP002 'clint' defined as a dependency but not used in the codebase
requirements.txt: DEP002 'idna' defined as a dependency but not used in the codebase
requirements.txt: DEP002 'isort' defined as a dependency but not used in the codebase
requirements.txt: DEP002 'requests' defined as a dependency but not used in the codebase
requirements.txt: DEP002 'soupsieve' defined as a dependency but not used in the codebase
requirements.txt: DEP002 'uvicorn' defined as a dependency but not used in the codebase
src/main.py:4:8: DEP004 'black' imported but declared as a dev dependency
src/main.py:7:8: DEP001 'white' imported but missing from the dependency definitions
src/notebook.ipynb:3:8: DEP001 'arrow' imported but missing from the dependency definitions
Found 12 dependency issues.

For more information, see the documentation: https://deptry.com/
""")
