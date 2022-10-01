import ast
import logging
from pathlib import Path
from typing import List, Union

import chardet

from deptry.notebook_import_extractor import NotebookImportExtractor

RECURSION_TYPES = [ast.If, ast.Try, ast.ExceptHandler, ast.FunctionDef, ast.ClassDef]


class ImportParser:
    """
    Class to scan Python files or Python code for import statements. Scanning is done by creating the abstract syntax tree
    and extracting all nodes that contain import statements.
    """

    def __init__(self) -> None:
        pass

    def get_imported_modules_for_list_of_files(self, list_of_files: List[Path]) -> List[str]:
        logging.info(f"Scanning {len(list_of_files)} files...")
        modules_per_file = [self.get_imported_modules_from_file(file) for file in list_of_files]
        all_modules = self._flatten_list(modules_per_file)
        unique_modules = sorted(set(all_modules))
        unique_modules = self._filter_exceptions(unique_modules)
        logging.debug(f"All imported modules: {unique_modules}\n")
        return unique_modules

    def get_imported_modules_from_file(self, path_to_file: Path) -> List[str]:
        try:
            if str(path_to_file).endswith(".ipynb"):
                modules = self._get_imported_modules_from_ipynb(path_to_file)
            else:
                modules = self._get_imported_modules_from_py(path_to_file)
            modules = sorted(set(modules))
            logging.debug(f"Found the following imports in {str(path_to_file)}: {modules}")
        except AttributeError as e:
            logging.warning(f"Warning: Parsing imports for file {str(path_to_file)} failed.")
            raise (e)
        return modules

    def get_imported_modules_from_str(self, file_str: str) -> List[str]:
        root = ast.parse(file_str)
        import_nodes = self._get_import_nodes_from(root)
        return self._get_import_modules_from(import_nodes)

    def _get_imported_modules_from_py(self, path_to_py_file: Path) -> List[str]:
        try:
            with open(path_to_py_file) as f:
                root = ast.parse(f.read(), path_to_py_file)  # type: ignore[call-overload]
            import_nodes = self._get_import_nodes_from(root)
            return self._get_import_modules_from(import_nodes)
        except UnicodeDecodeError:
            return self._get_imported_modules_from_py_and_guess_encoding(path_to_py_file)

    def _get_imported_modules_from_py_and_guess_encoding(self, path_to_py_file: Path) -> List[str]:
        try:
            with open(path_to_py_file, encoding=self._get_file_encoding(path_to_py_file)) as f:
                root = ast.parse(f.read(), path_to_py_file)  # type: ignore[call-overload]
            import_nodes = self._get_import_nodes_from(root)
            return self._get_import_modules_from(import_nodes)
        except UnicodeDecodeError:
            logging.warning(f"Warning: File {path_to_py_file} could not be decoded. Skipping...")
            return []

    def _get_imported_modules_from_ipynb(self, path_to_ipynb_file: Path) -> List[str]:
        imports = NotebookImportExtractor().extract(path_to_ipynb_file)
        root = ast.parse("\n".join(imports))
        import_nodes = self._get_import_nodes_from(root)
        return self._get_import_modules_from(import_nodes)

    def _get_import_nodes_from(
        self, root: Union[ast.AST, ast.If, ast.Try, ast.ExceptHandler, ast.FunctionDef, ast.ClassDef]
    ) -> List[Union[ast.Import, ast.ImportFrom]]:
        """
        Recursively collect import nodes from a Python module. This is needed to find imports that
        are defined within if/else or try/except statements. In that case, the ast.Import or ast.ImportFrom node
        is a child of an ast.If/Try/ExceptHandler node.
        """

        imports = []
        for node in ast.iter_child_nodes(root):
            if any([isinstance(node, recursion_type) for recursion_type in RECURSION_TYPES]):
                imports += self._get_import_nodes_from(node)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                imports += [node]
        return imports

    @staticmethod
    def _get_import_modules_from(nodes: List[Union[ast.Import, ast.ImportFrom]]) -> List[str]:
        modules = []
        for node in nodes:
            if isinstance(node, ast.Import):
                modules += [x.name.split(".")[0] for x in node.names]
            # nodes for imports like `from . import foo` do not have a module attribute.
            elif node.module and node.level == 0:
                modules.append(node.module.split(".")[0])
        return modules

    @staticmethod
    def _flatten_list(modules_per_file: List[List[str]]) -> List[str]:
        all_modules = []
        for modules in modules_per_file:
            if modules:
                all_modules += modules
        return all_modules

    @staticmethod
    def _filter_exceptions(modules: List[str]) -> List[str]:
        exceptions = [
            "setuptools"
        ]  # setuptools is usually available by default, so often not specified in dependencies.
        for exception in exceptions:
            if exception in modules:
                logging.debug(f"Found module {exception} to be imported, omitting from the list of modules.")
                modules = [module for module in modules if module != exception]
        return modules

    @staticmethod
    def _get_file_encoding(file_name: Union[str, Path]) -> str:
        with open(file_name, "rb") as f:
            return chardet.detect(f.read())["encoding"]
