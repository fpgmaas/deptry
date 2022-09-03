import ast
import logging
from pathlib import Path
from typing import List

from deptry.notebook_import_extractor import NotebookImportExtractor


class ImportParser:
    """
    Scan a Python file for import statements and return a list of imported modules.
    """

    def __init__(self) -> None:
        pass

    def get_imported_modules_for_list_of_files(self, list_of_files: List[Path]) -> List[str]:
        modules_per_file = [self._get_imported_modules_from_file(file) for file in list_of_files]
        all_modules = self._flatten_list(modules_per_file)
        unique_modules = sorted(list(set(all_modules)))
        logging.debug(f"All imported modules: {unique_modules}\n")
        return unique_modules

    def _get_imported_modules_from_file(self, path_to_file: Path) -> List[str]:
        try:
            if str(path_to_file).endswith(".ipynb"):
                modules = self._get_imported_modules_from_ipynb(path_to_file)
            else:
                modules = self._get_imported_modules_from_py(path_to_file)
            logging.debug(f"Found the following imports in {str(path_to_file)}: {modules}")
        except Exception as e:
            logging.warning(f"Warning: Parsing imports for file {str(path_to_file)} failed.")
            raise (e)
        return modules

    def _get_imported_modules_from_py(self, path_to_py_file: Path):
        with open(path_to_py_file) as f:
            root = ast.parse(f.read(), path_to_py_file)
        return self._get_modules_from_ast_root(root)

    def _get_imported_modules_from_ipynb(self, path_to_ipynb_file: Path):
        imports = NotebookImportExtractor().extract(path_to_ipynb_file)
        root = ast.parse("\n".join(imports))
        return self._get_modules_from_ast_root(root)

    @staticmethod
    def _get_modules_from_ast_root(root):
        modules = []
        for node in ast.iter_child_nodes(root):
            if isinstance(node, ast.Import):
                modules += [x.name.split(".")[0] for x in node.names]
            elif isinstance(node, ast.ImportFrom):
                modules.append(node.module.split(".")[0])
        return modules

    @staticmethod
    def _flatten_list(modules_per_file):
        all_modules = []
        for modules in modules_per_file:
            if modules:
                all_modules += modules
        return all_modules
