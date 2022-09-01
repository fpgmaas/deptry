import ast
from pathlib import Path
from typing import List


class ImportParser:
    """
    Get a list of imported modules from a python file.

    TODO get this to work with ipynb files. Maybe need to convert to py files first?
    """

    def __init__(self) -> None:
        pass

    def get_imported_modules_for_file(self, path_to_py_file: Path) -> List[str]:
        modules = []
        with open(path_to_py_file) as f:
            root = ast.parse(f.read(), path_to_py_file)

        for node in ast.iter_child_nodes(root):
            if isinstance(node, ast.Import):
                modules += [x.name.split(".")[0] for x in node.names]
            elif isinstance(node, ast.ImportFrom):
                modules.append(node.module.split(".")[0])
        return modules

    def get_imported_modules_for_list_of_files(self, list_of_paths: List[Path]) -> List[str]:
        modules_per_file = [
            {"path": str(path), "modules": self.get_imported_modules_for_file(path)} for path in list_of_paths
        ]
        # TODO logging statement for debugging
        modules = []
        for file in modules_per_file:
            modules += file["modules"]
        return sorted(list(set(modules)))
