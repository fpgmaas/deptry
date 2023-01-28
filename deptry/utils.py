from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any


from deptry.exceptions import PyprojectFileNotFoundError

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def load_pyproject_toml(config: Path) -> dict[str, Any]:
    try:
        with config.open("rb") as pyproject_file:
            return tomllib.load(pyproject_file)
    except FileNotFoundError:
        raise PyprojectFileNotFoundError(os.getcwd()) from None
