from __future__ import annotations

import shlex
import shutil
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tests.utils import run_within_dir

if TYPE_CHECKING:
    from _pytest.tmpdir import TempPathFactory

    from tests.functional.types import ProjectBuilder, ToolSpecificProjectBuilder


def _build_project(root_directory: Path, project: str, setup_command: str, cwd: str | None = None) -> Path:
    project_path = root_directory / project

    # If the fixture was already called with the same parameters, the project is already bootstrapped.
    if project_path.exists():
        return project_path

    shutil.copytree(Path("tests/data") / project, project_path)

    with run_within_dir(project_path):
        assert subprocess.check_call(shlex.split(setup_command), cwd=cwd) == 0

    return project_path


@pytest.fixture(scope="session")
def project_builder(tmp_path_factory: TempPathFactory) -> ProjectBuilder:
    def _project_builder(project: str, setup_command: str, cwd: str | None = None) -> Path:
        return _build_project(tmp_path_factory.getbasetemp(), project, setup_command, cwd)

    return _project_builder


@pytest.fixture(scope="session")
def poetry_project_builder(tmp_path_factory: TempPathFactory) -> ToolSpecificProjectBuilder:
    def _project_builder(project: str, cwd: str | None = None) -> Path:
        return _build_project(tmp_path_factory.getbasetemp(), project, "poetry install --no-interaction --no-root", cwd)

    return _project_builder


@pytest.fixture(scope="session")
def pip_project_builder(tmp_path_factory: TempPathFactory) -> ToolSpecificProjectBuilder:
    def _project_builder(project: str, cwd: str | None = None) -> Path:
        return _build_project(tmp_path_factory.getbasetemp(), project, "pip install .", cwd)

    return _project_builder


@pytest.fixture(scope="session")
def pdm_project_builder(tmp_path_factory: TempPathFactory) -> ToolSpecificProjectBuilder:
    def _project_builder(project: str, cwd: str | None = None) -> Path:
        return _build_project(tmp_path_factory.getbasetemp(), project, "pip install pdm; pdm install", cwd)

    return _project_builder


@pytest.fixture(scope="session")
def requirements_txt_project_builder(tmp_path_factory: TempPathFactory) -> ToolSpecificProjectBuilder:
    def _project_builder(project: str, cwd: str | None = None) -> Path:
        return _build_project(
            tmp_path_factory.getbasetemp(),
            project,
            (
                "python -m pip install -r requirements.txt -r requirements-dev.txt -r requirements-2.txt -r"
                " requirements-typing.txt"
            ),
            cwd,
        )

    return _project_builder
