import os
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

PYPROJECT_TOML_PATH = "./pyproject.toml"


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
    oldpwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldpwd)


def load_pyproject_toml(pyproject_toml_path: str = PYPROJECT_TOML_PATH) -> Dict[str, Any]:
    try:
        with Path(pyproject_toml_path).open("rb") as pyproject_file:
            return tomllib.load(pyproject_file)
    except FileNotFoundError:
        raise FileNotFoundError(f"No file `pyproject.toml` found in directory {os.getcwd()}")
