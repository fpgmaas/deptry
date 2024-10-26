from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import sys
import venv
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from deptry.reporters.text import COLORS
from tests.functional.utils import DEPTRY_WHEEL_DIRECTORY

if TYPE_CHECKING:
    from collections.abc import Generator


@dataclass
class _BaseVenvFactory:
    venvs_directory: Path

    @contextmanager
    def venv(self, project: str, setup_commands: list[str]) -> Generator[VirtualEnvironment, None, None]:
        venv_path = self.venvs_directory / project

        old_cwd = Path.cwd()

        virtual_env = VirtualEnvironment(venv_path, project)
        virtual_env.setup(setup_commands, old_cwd)

        os.chdir(venv_path / "project")

        try:
            yield virtual_env
        finally:
            os.chdir(old_cwd)


class PDMVenvFactory(_BaseVenvFactory):
    @contextmanager
    def __call__(self, project: str) -> Generator[VirtualEnvironment, None, None]:
        with self.venv(project, ["pip install pdm", "pdm install --no-self"]) as virtual_env:
            yield virtual_env


class UvVenvFactory(_BaseVenvFactory):
    @contextmanager
    def __call__(self, project: str) -> Generator[VirtualEnvironment, None, None]:
        with self.venv(project, ["pip install uv", "uv sync"]) as virtual_env:
            yield virtual_env


@dataclass
class PoetryVenvFactory(_BaseVenvFactory):
    @contextmanager
    def __call__(self, project: str) -> Generator[VirtualEnvironment, None, None]:
        with self.venv(project, ["pip install poetry", "poetry install --no-root"]) as virtual_env:
            yield virtual_env


class PipVenvFactory(_BaseVenvFactory):
    @contextmanager
    def __call__(
        self, project: str, install_command: str = "pip install ."
    ) -> Generator[VirtualEnvironment, None, None]:
        with self.venv(project, [install_command]) as virtual_env:
            yield virtual_env


@dataclass
class VirtualEnvironment:
    project_path: Path
    project: str
    python_executable: Path | None = None

    def __post_init__(self) -> None:
        self.python_executable = self.project_path / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")

    def setup(self, setup_commands: list[str], deptry_directory: Path) -> None:
        if self.project_path.exists():
            return

        virtual_env = venv.EnvBuilder(with_pip=True)
        virtual_env.create(self.project_path)

        shutil.copytree(deptry_directory / "tests/fixtures" / self.project, self.project_path / "project")

        path_to_wheel_file = self._get_path_to_wheel_file(deptry_directory / DEPTRY_WHEEL_DIRECTORY)

        for setup_command in [
            f"pip install --no-cache-dir {path_to_wheel_file}",
            *setup_commands,
        ]:
            self.run(setup_command, check=True, cwd=self.project_path / "project")

    def run(self, command: str, check: bool = False, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            shlex.split(f"{self.python_executable} -m {command}", posix=sys.platform != "win32"),
            env={**os.environ, "VIRTUAL_ENV": str(self.project_path)},
            capture_output=True,
            text=True,
            check=check,
            cwd=cwd,
        )

    @staticmethod
    def _get_path_to_wheel_file(directory: Path) -> Path:
        """
        Get the path to a single wheel file in the specified directory. If there is not exactly one wheel file, raise an error.
        """
        wheel_files = list(directory.glob("*.whl"))
        if len(wheel_files) != 1:
            raise ValueError(f"Expected exactly one wheel file in {directory}, but found {len(wheel_files)}.")  # noqa: TRY003
        return wheel_files[0]


@contextmanager
def run_within_dir(path: Path) -> Generator[None, None, None]:
    """
    Utility function to run some code within a directory, and change back to the current directory afterwards.

    Example usage:

    ```
    with run_within_dir(directory):
        some_code()
    ```

    """
    oldpwd = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldpwd)


def get_issues_report(path: Path) -> list[dict[str, Any]]:
    with path.open() as file:
        report: list[dict[str, Any]] = json.load(file)

    return report


def create_files(paths: list[Path]) -> None:
    """
    Takes as input an argument paths, which is a list of dicts. Each dict should have two keys;
    'dir' to denote a directory and 'file' to denote the file name. This function creates all files
    within their corresponding directories.
    """
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()


def stylize(text: str, **kwargs: Any) -> str:
    return text.format(**kwargs, **COLORS)
