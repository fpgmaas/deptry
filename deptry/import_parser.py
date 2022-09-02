import ast
import logging
from pathlib import Path
from typing import List

from deptry.notebook_converter import NotebookConverter

import logging
logger = logging.getLogger(__name__)

class ImportParser:
    """
    Get a list of imported modules from a python file.
    """

    def __init__(self, temp_directory: str = ".deptry") -> None:
        self.temp_directory = temp_directory

    def get_imported_modules_for_list_of_files(self, list_of_files: List[Path]) -> List[str]:
        modules_per_file = [self.get_imported_modules_for_file(file) for file in list_of_files]
        all_modules = self._flatten_list(modules_per_file)
        unique_modules = sorted(list(set(all_modules)))
        logger.debug(f"All imported modules: {unique_modules}\n")
        return unique_modules

    def get_imported_modules_for_file(self, path_to_file: Path) -> List[str]:
        if str(path_to_file).endswith(".ipynb"):
            path_to_py_file = self._convert_ipynb_to_py(path_to_file)
        else:
            path_to_py_file = path_to_file

        try:
            modules = self._get_imported_modules_for_py_file(path_to_py_file)
            logger.debug(f"Found the following imports in {str(path_to_file)}: {modules}")
            return modules
        except Exception as e:
            logger.warning(f"Warning: Parsing imports for file {str(path_to_file)} failed.")
            raise (e)

    def _get_imported_modules_for_py_file(self, path_to_py_file: Path):
        modules = []
        with open(path_to_py_file) as f:
            root = ast.parse(f.read(), path_to_py_file)
        for node in ast.iter_child_nodes(root):
            if isinstance(node, ast.Import):
                modules += [x.name.split(".")[0] for x in node.names]
            elif isinstance(node, ast.ImportFrom):
                modules.append(node.module.split(".")[0])
        return modules

    def _convert_ipynb_to_py(self, path_to_ipynb_file: Path):
        return NotebookConverter(self.temp_directory).convert(path_to_ipynb_file, "tmp")

    @staticmethod
    def _flatten_list(modules_per_file):
        all_modules = []
        for modules in modules_per_file:
            if modules:
                all_modules += modules
        return all_modules
