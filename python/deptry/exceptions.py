from __future__ import annotations

from typing import TYPE_CHECKING

from click import UsageError

if TYPE_CHECKING:
    from pathlib import Path


class DependencySpecificationNotFoundError(FileNotFoundError):
    def __init__(self, requirements_files: tuple[str, ...]) -> None:
        super().__init__(
            "No file called 'pyproject.toml' with a [tool.poetry.dependencies], [tool.pdm] or [project] section or"
            f" file(s) called '{', '.join(requirements_files)}' found. Exiting."
        )


class PyprojectFileNotFoundError(FileNotFoundError):
    def __init__(self, directory: Path) -> None:
        super().__init__(f"No file `pyproject.toml` found in directory {directory}")


class UnsupportedPythonVersionError(ValueError):
    def __init__(self, version: tuple[int, int]) -> None:
        super().__init__(
            f"Python version {version[0]}.{version[1]} is not supported. Only versions >= 3.9 are supported."
        )


class InvalidPyprojectTOMLOptionsError(UsageError):
    def __init__(self, invalid_options: list[str]) -> None:
        super().__init__(
            f"'[tool.deptry]' section in 'pyproject.toml' contains invalid configuration options: {invalid_options}."
        )
