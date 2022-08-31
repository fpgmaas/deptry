from pathlib import Path
from typing import List
import numpy.random as rd


class PythonFileFinder:
    """
    Get a list of all .py and .ipynb files recursively within a directory.

    TODO: This can be probably sped up easily by not listing all files within the
    ignored directories and them dropping them from the list, but only listing files
    in non-ignored directories.
    """

    def __init__(self, paths_to_ignore: List[str] = [".venv"], include_ipynb: bool = False) -> None:
        self.paths_to_ignore = paths_to_ignore
        self.include_ipynb = include_ipynb

    def get_list_of_python_files(self):
        all_py_files = self._get_all_python_files()
        if self.include_ipynb:
            all_py_files = self._add_ipynb_files(all_py_files)
        all_py_files = self._remove_paths_to_ignore(all_py_files)
        return all_py_files

    def _get_all_python_files(self) -> List[Path]:
        return [path for path in Path(".").rglob("*.py")]

    def _add_ipynb_files(self, all_py_files: List[Path]) -> List[Path]:
        return all_py_files + [path for path in Path(".").rglob("*.ipynb")]

    def _remove_paths_to_ignore(self, all_py_files: List[Path]) -> List[Path]:
        return [
            path
            for path in all_py_files
            if not any([str(path).startswith(pattern) for pattern in self.paths_to_ignore])
        ]
