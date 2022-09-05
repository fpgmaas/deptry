import logging
from pathlib import Path
from typing import List

from deptry.import_parser import ImportParser
from deptry.imports_to_package_names import ImportsToPackageNames
from deptry.obsolete_dependencies_finder import ObsoleteDependenciesFinder
from deptry.python_file_finder import PythonFileFinder


class Core:
    def __init__(self, ignore_dependencies: List[str], ignore_directories: List[str], ignore_notebooks: bool) -> None:
        self.ignore_dependencies = ignore_dependencies
        self.ignore_directories = ignore_directories
        self.ignore_notebooks = ignore_notebooks
        logging.debug("Running with the following configuration:")
        logging.debug(f"ignore_dependencies: {ignore_dependencies}")
        logging.debug(f"ignore_directories: {ignore_directories}")
        logging.debug(f"ignore_notebooks: {ignore_notebooks}")

    def run(self) -> List[str]:
        all_python_files = PythonFileFinder(
            ignore_directories=self.ignore_directories, ignore_notebooks=self.ignore_notebooks
        ).get_all_python_files_in(Path("."))
        imported_modules = ImportParser().get_imported_modules_for_list_of_files(all_python_files)
        imported_packages = ImportsToPackageNames().convert(imported_modules)
        obsolete_dependencies = ObsoleteDependenciesFinder(
            imported_packages=imported_packages, ignore_dependencies=self.ignore_dependencies
        ).find()
        return obsolete_dependencies
