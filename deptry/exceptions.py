from __future__ import annotations


class DependencySpecificationNotFoundError(FileNotFoundError):
    def __init__(self, requirements_txt: tuple[str, ...]) -> None:
        super().__init__(
            "No file called 'pyproject.toml' with a [tool.poetry.dependencies], [tool.pdm] or [project] section or"
            f" file(s) called '{', '.join(requirements_txt)}' found. Exiting."
        )


class IncorrectDependencyFormatError(ValueError):
    def __init__(self) -> None:
        super().__init__("Incorrect dependency manage format. Only poetry, pdm and requirements.txt are supported.")


class PyprojectFileNotFoundError(FileNotFoundError):
    def __init__(self, directory: str) -> None:
        super().__init__(f"No file `pyproject.toml` found in directory {directory}")


class UnsupportedPythonVersionError(ValueError):
    def __init__(self, version: tuple[int, int]) -> None:
        super().__init__(
            f"Python version {version[0]}.{version[1]} is not supported. Only versions >= 3.8 are supported."
        )
