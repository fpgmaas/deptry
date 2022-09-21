import os
import sys
import types
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Tuple

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

PYPROJECT_TOML_PATH = "./pyproject.toml"


@contextmanager
def run_within_dir(path: Path) -> None:
    """
    Utility function to run some code within a directory, and change back to the current directory afterwards.

    Example usage:

    ```
    with run_within_dir(directory):
        some_code()
    ```

    """
    oldpwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldpwd)


def import_importlib_metadata() -> Tuple[types.ModuleType, Exception]:
    """
    importlib.metadata is in the standard library since Python version 3.8
    """
    if sys.version_info[1] == 7:
        import importlib_metadata as metadata
        from importlib_metadata import PackageNotFoundError

        return metadata, PackageNotFoundError
    else:
        import importlib.metadata as metadata
        from importlib.metadata import PackageNotFoundError

        return metadata, PackageNotFoundError


def load_pyproject_toml(pyproject_toml_path: str = PYPROJECT_TOML_PATH) -> Dict:
    try:
        with Path(pyproject_toml_path).open("rb") as pyproject_file:
            return tomllib.load(pyproject_file)
    except FileNotFoundError:
        raise FileNotFoundError(f"No file `pyproject.toml` found in directory {os.getcwd()}")
