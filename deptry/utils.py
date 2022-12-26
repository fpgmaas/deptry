from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

PYPROJECT_TOML_PATH = "./pyproject.toml"


def load_pyproject_toml(pyproject_toml_path: str = PYPROJECT_TOML_PATH) -> dict[str, Any]:
    try:
        with Path(pyproject_toml_path).open("rb") as pyproject_file:
            return tomllib.load(pyproject_file)
    except FileNotFoundError:
        raise FileNotFoundError(f"No file `pyproject.toml` found in directory {os.getcwd()}") from None
