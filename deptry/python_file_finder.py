from __future__ import annotations

import logging
import os
import re
from pathlib import Path


class PythonFileFinder:
    """
    Get a list of all .py and .ipynb files recursively within a directory.
    Args:
        exclude: A list of regex patterns of paths to ignore. Matching is done by re.match(), so it checks for a match at the beginning
            of the string.
        ignore_notebooks: If ignore_notebooks is set to True, .ipynb files are ignored and only .py files are returned.
    """

    def __init__(self, exclude: tuple[str, ...], ignore_notebooks: bool = False) -> None:
        self.exclude = exclude
        self.ignore_notebooks = ignore_notebooks

    def get_all_python_files_in(self, directory: Path) -> list[Path]:
        logging.debug("Collecting Python files to scan...")

        source_files = []

        ignore_regex = re.compile("|".join(self.exclude))
        file_lookup_suffixes = {".py"} if self.ignore_notebooks else {".py", ".ipynb"}

        for root_str, dirs, files in os.walk(directory, topdown=True):
            root = Path(root_str)

            if self.exclude and ignore_regex.match(str(root)):
                dirs[:] = []
                continue

            for file_str in files:
                file = root / file_str
                if file.suffix in file_lookup_suffixes and (not self.exclude or not ignore_regex.match(str(file))):
                    source_files.append(file)

        logging.debug("Python files to scan for imports:\n%s\n", "\n".join([str(file) for file in source_files]))

        return source_files
