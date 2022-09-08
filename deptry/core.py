import logging
from pathlib import Path
from typing import Dict, List

from deptry.dependency_getter import DependencyGetter
from deptry.import_parser import ImportParser
from deptry.issue_finders.dev import DevDependenciesFinder
from deptry.issue_finders.missing import MissingDependenciesFinder
from deptry.issue_finders.obsolete import ObsoleteDependenciesFinder
from deptry.issue_finders.transitive import TransitiveDependenciesFinder
from deptry.module import ModuleBuilder
from deptry.python_file_finder import PythonFileFinder


class Core:
    def __init__(
        self,
        ignore_obsolete: List[str],
        ignore_missing: List[str],
        ignore_transitive: List[str],
        ignore_develop: List[str],
        skip_obsolete: bool,
        skip_missing: bool,
        skip_transitive: bool,
        skip_develop: bool,
        exclude: List[str],
        ignore_notebooks: bool,
    ) -> None:
        self.ignore_obsolete = ignore_obsolete
        self.ignore_missing = ignore_missing
        self.ignore_transitive = ignore_transitive
        self.ignore_develop = ignore_develop
        self.exclude = exclude
        self.ignore_notebooks = ignore_notebooks
        self.skip_obsolete = skip_obsolete
        self.skip_missing = skip_missing
        self.skip_transitive = skip_transitive
        self.skip_develop = skip_develop
        logging.debug("Running with the following configuration:")
        logging.debug(f"ignore_obsolete: {ignore_obsolete}")
        logging.debug(f"ignore_missing: {ignore_missing}")
        logging.debug(f"ignore_transitive: {ignore_transitive}")
        logging.debug(f"ignore_develop: {ignore_develop}")
        logging.debug(f"skip_obsolete: {skip_obsolete}")
        logging.debug(f"skip_missing: {skip_missing}")
        logging.debug(f"skip_transitive: {skip_transitive}")
        logging.debug(f"skip_develop {skip_develop}")
        logging.debug(f"exclude: {exclude}")
        logging.debug(f"ignore_notebooks: {ignore_notebooks}\n")

    def run(self) -> Dict:

        dependencies = DependencyGetter().get()
        dev_dependencies = DependencyGetter(dev=True).get()

        all_python_files = PythonFileFinder(
            exclude=self.exclude, ignore_notebooks=self.ignore_notebooks
        ).get_all_python_files_in(Path("."))

        imported_modules = ImportParser().get_imported_modules_for_list_of_files(all_python_files)
        imported_modules = [ModuleBuilder(mod, dependencies, dev_dependencies).build() for mod in imported_modules]
        imported_modules = [mod for mod in imported_modules if not mod.standard_library]

        result = {}
        if not self.skip_obsolete:
            result["obsolete"] = ObsoleteDependenciesFinder(
                imported_modules=imported_modules, dependencies=dependencies, ignore_obsolete=self.ignore_obsolete
            ).find()
        if not self.skip_missing:
            result["missing"] = MissingDependenciesFinder(
                imported_modules=imported_modules, dependencies=dependencies, ignore_missing=self.ignore_missing
            ).find()
        if not self.skip_transitive:
            result["transitive"] = TransitiveDependenciesFinder(
                imported_modules=imported_modules, dependencies=dependencies, ignore_transitive=self.ignore_transitive
            ).find()
        if not self.skip_develop:
            result["develop"] = DevDependenciesFinder(
                imported_modules=imported_modules, dependencies=dependencies, ignore_develop=self.ignore_develop
            ).find()

        return result
