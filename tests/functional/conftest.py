from __future__ import annotations

import pytest

from tests.utils import PDMVenvFactory, PipVenvFactory, PoetryVenvFactory


@pytest.fixture(scope="session")
def pdm_venv_factory(tmp_path_factory: pytest.TempPathFactory) -> PDMVenvFactory:
    return PDMVenvFactory(tmp_path_factory.getbasetemp() / "venvs")


@pytest.fixture(scope="session")
def poetry_venv_factory(tmp_path_factory: pytest.TempPathFactory) -> PoetryVenvFactory:
    return PoetryVenvFactory(tmp_path_factory.getbasetemp() / "venvs")


@pytest.fixture(scope="session")
def pip_venv_factory(tmp_path_factory: pytest.TempPathFactory) -> PipVenvFactory:
    return PipVenvFactory(tmp_path_factory.getbasetemp() / "venvs")
