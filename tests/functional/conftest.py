from __future__ import annotations

import shlex
import shutil
import subprocess
import venv
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tests.utils import PDMVenvFactory, PipVenvFactory, PoetryVenvFactory, run_within_dir

if TYPE_CHECKING:
    from tests.functional.types import ProjectBuilder, ToolSpecificProjectBuilder


@pytest.fixture(scope="session")
def pdm_venv_factory(tmp_path_factory: pytest.TempPathFactory) -> PDMVenvFactory:
    return PDMVenvFactory(tmp_path_factory.getbasetemp() / "venvs")


@pytest.fixture(scope="session")
def poetry_venv_factory(tmp_path_factory: pytest.TempPathFactory) -> PoetryVenvFactory:
    return PoetryVenvFactory(tmp_path_factory.getbasetemp() / "venvs")


@pytest.fixture(scope="session")
def pip_venv_factory(tmp_path_factory: pytest.TempPathFactory) -> PipVenvFactory:
    return PipVenvFactory(tmp_path_factory.getbasetemp() / "venvs")


def _build_project(root_directory: Path, project: str, setup_commands: list[str], cwd: str | None = None) -> Path:
    project_path = root_directory / project

    # If the fixture was already called with the same parameters, the project is already bootstrapped.
    if project_path.exists():
        return project_path / "project"

    shutil.copytree(Path("tests/data") / project, project_path / "project")

    env = venv.EnvBuilder(with_pip=True)
    env.create(project_path)

    deptry_directory = Path.cwd()

    with run_within_dir(project_path / "project"):
        for setup_command in [*setup_commands, f"pip install {deptry_directory}"]:
            subprocess.check_call(
                shlex.split(setup_command),
                cwd=cwd,
                env={"PATH": str(project_path / "bin"), "VIRTUAL_ENV": str(project_path)},
            )

    return project_path / "project"


@pytest.fixture(scope="session")
def project_builder() -> ProjectBuilder:
    def _project_builder(root_directory: Path, project: str, setup_commands: list[str], cwd: str | None = None) -> Path:
        return _build_project(root_directory, project, setup_commands, cwd)

    return _project_builder


@pytest.fixture(scope="session")
def poetry_project_builder() -> ToolSpecificProjectBuilder:
    def _project_builder(root_directory: Path, project: str, cwd: str | None = None) -> Path:
        return _build_project(
            root_directory, project, ["pip install poetry", "poetry install --no-interaction --no-root"], cwd
        )

    return _project_builder


@pytest.fixture(scope="session")
def pip_project_builder() -> ToolSpecificProjectBuilder:
    def _project_builder(root_directory: Path, project: str, cwd: str | None = None) -> Path:
        return _build_project(root_directory, project, ["pip install ."], cwd)

    return _project_builder


@pytest.fixture(scope="session")
def pdm_project_builder() -> ToolSpecificProjectBuilder:
    def _project_builder(root_directory: Path, project: str, cwd: str | None = None) -> Path:
        return _build_project(root_directory, project, ["pip install pdm", "pdm install --no-self"], cwd)

    return _project_builder


@pytest.fixture(scope="session")
def requirements_txt_project_builder() -> ToolSpecificProjectBuilder:
    def _project_builder(root_directory: Path, project: str, cwd: str | None = None) -> Path:
        return _build_project(
            root_directory,
            project,
            [
                "python -m pip install -r requirements.txt -r requirements-dev.txt -r requirements-2.txt -r"
                " requirements-typing.txt"
            ],
            cwd,
        )

    return _project_builder
