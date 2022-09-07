import logging
from pathlib import Path
from typing import List, Dict,

from deptry.dependency_getter import DependencyGetter
from deptry.import_parser import ImportParser
from deptry.missing_dependencies_finder import MissingDependenciesFinder
from deptry.obsolete_dependencies_finder import ObsoleteDependenciesFinder
from deptry.python_file_finder import PythonFileFinder


class Core:
    def __init__(self, 
        ignore_obsolete: List[str],
        ignore_missing: List[str],
        ignore_transitive: List[str],
        skip_obsolete: bool,
        skip_missing: bool,
        skip_transitive: bool,
        ignore_directories: List[str],
        ignore_notebooks: bool
        ) -> None:
        self.ignore_obsolete = ignore_obsolete
        self.ignore_missing = ignore_missing
        self.ignore_transitive = ignore_transitive
        self.ignore_directories = ignore_directories
        self.ignore_notebooks = ignore_notebooks
        self.skip_obsolete = skip_obsolete
        self.skip_missing = skip_missing
        self.skip_transitive = skip_transitive
        logging.debug("Running with the following configuration:")
        logging.debug(f"ignore_obsolete: {ignore_obsolete}")
        logging.debug(f"ignore_missing: {ignore_missing}")
        logging.debug(f"ignore_transitive: {ignore_transitive}")
        logging.debug(f"skip_obsolete: {skip_obsolete}")
        logging.debug(f"skip_missing: {skip_missing}")
        logging.debug(f"skip_transitive: {skip_transitive}")
        logging.debug(f"ignore_directories: {ignore_directories}")
        logging.debug(f"ignore_notebooks: {ignore_notebooks}\n")

    def run(self) -> Dict:

        dependencies = DependencyGetter().get()
        all_python_files = PythonFileFinder(
            ignore_directories=self.ignore_directories, ignore_notebooks=self.ignore_notebooks
        ).get_all_python_files_in(Path("."))
        imported_modules = ImportParser().get_imported_modules_for_list_of_files(all_python_files)

        obsolete_dependencies = ObsoleteDependenciesFinder(
            imported_modules=imported_modules, dependencies=dependencies
        ).find()
        missing_dependencies = MissingDependenciesFinder(
            imported_modules=imported_modules, dependencies=dependencies
        ).find()

        return {
            'obsolete': obsolete_dependencies, 
            'missing' : missing_dependencies['missing'], 
            'transitive' : missing_dependencies['transitive']
            }
