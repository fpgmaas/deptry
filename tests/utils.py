from __future__ import annotations

import json
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator


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


def create_files_from_list_of_dicts(paths: list[dict[str, str]]) -> None:
    """
    Takes as input an argument paths, which is a list of dicts. Each dict should have two keys;
    'dir' to denote a directory and 'file' to denote the file name. This function creates all files
    within their corresponding directories.
    """
    for path in paths:
        Path(path["dir"]).mkdir(parents=True, exist_ok=True)
        with open(Path(path["dir"]) / Path(path["file"]), "w"):
            pass
