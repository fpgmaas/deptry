from __future__ import annotations

import shlex
import subprocess
import sys
from pathlib import Path

import pytest

from tests.functional.utils import DEPTRY_WHEEL_DIRECTORY
from tests.utils import PDMVenvFactory, PipVenvFactory, PoetryVenvFactory


def pytest_sessionstart() -> None:
    deptry_wheel_path = Path(DEPTRY_WHEEL_DIRECTORY)

    print(f"Building `deptry` wheel in {deptry_wheel_path} to use it on functional tests...")  # noqa: T201

    subprocess.run(
        shlex.split(f"pdm build --no-sdist --dest {deptry_wheel_path}", posix=sys.platform != "win32"),
        capture_output=True,
        text=True,
        check=True,
    )


@pytest.fixture(scope="session")
def pdm_venv_factory(tmp_path_factory: pytest.TempPathFactory) -> PDMVenvFactory:
    return PDMVenvFactory(tmp_path_factory.getbasetemp() / "venvs")


@pytest.fixture(scope="session")
def poetry_venv_factory(tmp_path_factory: pytest.TempPathFactory) -> PoetryVenvFactory:
    return PoetryVenvFactory(tmp_path_factory.getbasetemp() / "venvs")


@pytest.fixture(scope="session")
def pip_venv_factory(tmp_path_factory: pytest.TempPathFactory) -> PipVenvFactory:
    return PipVenvFactory(tmp_path_factory.getbasetemp() / "venvs")
