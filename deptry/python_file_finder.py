import logging
import os
import re
from pathlib import Path
from typing import List, Tuple


class PythonFileFinder:
    """
    Get a list of all .py and .ipynb files recursively within a directory.
    Args:
        exclude: A list of regex patterns of paths to ignore. Matching is done by re.match(), so it checks for a match at the beginning
            of the string.
        ignore_notebooks: If ignore_notebooks is set to True, .ipynb files are ignored and only .py files are returned.
    """

    def __init__(self, exclude: Tuple[str, ...], ignore_notebooks: bool = False) -> None:
        self.exclude = exclude
        self.ignore_notebooks = ignore_notebooks

    def get_all_python_files_in(self, directory: Path) -> List[Path]:
        logging.debug("Collecting Python files to scan...")

        all_py_files = []

        ignore_regex = re.compile("|".join(self.exclude))
        py_regex = re.compile(r".*\.py$") if self.ignore_notebooks else re.compile(r".*\.py$|.*\.ipynb$")

        for root, dirs, files in os.walk(directory, topdown=True):
            root_without_trailing_dotslash = re.sub("^\./", "", root)
            if self.exclude and ignore_regex.match(root_without_trailing_dotslash):
                dirs[:] = []
                continue
            files_with_path = [Path(root) / Path(file) for file in files]

            files_to_keep = [file for file in files_with_path if py_regex.match(str(file))]
            if self.exclude:
                files_to_keep = [file for file in files_to_keep if not ignore_regex.match(str(file))]

            all_py_files += files_to_keep

        nl = "\n"
        logging.debug(f"Python files to scan for imports:\n{nl.join([str(x) for x in all_py_files])}\n")
        return all_py_files
