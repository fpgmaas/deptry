import logging
from pathlib import Path
from typing import List


class PythonFileFinder:
    """
    Get a list of all .py and .ipynb files recursively within a directory.
    If ignore_notebooks is set to True, .ipynb files are ignored and only .py files are returned.
    """

    def __init__(self, exclude: List[str] = [".venv"], ignore_notebooks: bool = False) -> None:
        self.exclude = exclude
        self.ignore_notebooks = ignore_notebooks

    def get_all_python_files_in(self, directory: Path) -> List[Path]:
        logging.debug("Collecting Python files to scan...")
        all_python_files = self._get_all_py_files_in(directory)
        if not self.ignore_notebooks:
            all_python_files += self._get_all_ipynb_files_in(directory)
        all_python_files = self._remove_directories_to_ignore(all_python_files)
        nl = "\n"
        logging.debug(f"Python files to scan for imports:\n{nl.join([str(x) for x in all_python_files])}\n")
        return all_python_files

    def _get_all_py_files_in(self, directory: Path) -> List[Path]:
        return [path for path in directory.rglob("*.py")]

    def _get_all_ipynb_files_in(self, directory: Path) -> List[Path]:
        return [path for path in directory.rglob("*.ipynb")]

    def _remove_directories_to_ignore(self, all_py_files: List[Path]) -> List[Path]:
        """
        Simply use startswith() to determine which directories and files to exclude. This should definitely be improved in the future.
        """
        return [path for path in all_py_files if not any([str(path).startswith(pattern) for pattern in self.exclude])]
