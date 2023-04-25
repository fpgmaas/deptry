from __future__ import annotations

import json
import os
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Generator

if TYPE_CHECKING:
    from pathlib import Path


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


def get_issues_report(path: str = "report.json") -> dict[str, Any]:
    with open(path) as file:
        report: dict[str, Any] = json.load(file)

    return report


def create_files(paths: list[Path]) -> None:
    """
    Takes as input an argument paths, which is a list of dicts. Each dict should have two keys;
    'dir' to denote a directory and 'file' to denote the file name. This function creates all files
    within their corresponding directories.
    """
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w"):
            pass
