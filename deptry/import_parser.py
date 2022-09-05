import ast
import logging
from pathlib import Path
from typing import List, Union

from deptry.notebook_import_extractor import NotebookImportExtractor


class ImportParser:
    """
    Class to scan Python files or Python code for import statements. Scanning is done by creating the abstract syntax tree
    and extracting all nodes that contain import statements.
    """

    def __init__(self) -> None:
        pass

    def get_imported_modules_for_list_of_files(self, list_of_files: List[Path]) -> List[str]:
        modules_per_file = [self.get_imported_modules_from_file(file) for file in list_of_files]
        all_modules = self._flatten_list(modules_per_file)
        unique_modules = sorted(list(set(all_modules)))
        logging.debug(f"All imported modules: {unique_modules}\n")
        return unique_modules

    def get_imported_modules_from_file(self, path_to_file: Path) -> List[str]:
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

    def get_imported_modules_from_str(self, file_str: str) -> List[str]:
        root = ast.parse(file_str)
        import_nodes = self._get_import_nodes_from(root)
        return self._get_import_modules_from(import_nodes)

    def _get_imported_modules_from_py(self, path_to_py_file: Path) -> List[str]:
        with open(path_to_py_file) as f:
            root = ast.parse(f.read(), path_to_py_file)  # type: ignore
        import_nodes = self._get_import_nodes_from(root)
        return self._get_import_modules_from(import_nodes)

    def _get_imported_modules_from_ipynb(self, path_to_ipynb_file: Path) -> List[str]:
        imports = NotebookImportExtractor().extract(path_to_ipynb_file)
        root = ast.parse("\n".join(imports))
        import_nodes = self._get_import_nodes_from(root)
        return self._get_import_modules_from(import_nodes)

    def _get_import_nodes_from(self, root: Union[ast.Module, ast.If]):
        """
        Recursively collect import nodes from a Python module. This is needed to find imports that
        are defined within if/else statements. In that case, the ast.Import or ast.ImportFrom node
        is a child of an ast.If node.
        """
        imports = []
        for node in ast.iter_child_nodes(root):
            if isinstance(node, ast.If) or isinstance(node, ast.Try) or isinstance(node, ast.ExceptHandler):
                imports += self._get_import_nodes_from(node)
            elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                imports += [node]
        return imports

    @staticmethod
    def _get_import_modules_from(nodes: List[Union[ast.Import, ast.ImportFrom]]) -> List[str]:
        modules = []
        for node in nodes:
            if isinstance(node, ast.Import):
                modules += [x.name.split(".")[0] for x in node.names]
            elif isinstance(node, ast.ImportFrom):
                modules.append(node.module.split(".")[0])  # type: ignore
        return modules

    @staticmethod
    def _flatten_list(modules_per_file: List[List]) -> List:
        all_modules = []
        for modules in modules_per_file:
            if modules:
                all_modules += modules
        return all_modules
