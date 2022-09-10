import logging
from pathlib import Path
from typing import Dict, List

from deptry.dependency_getter import DependencyGetter
from deptry.import_parser import ImportParser
from deptry.issue_finders.misplaced_dev import MisplacedDevDependenciesFinder
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
        ignore_misplaced_dev: List[str],
        skip_obsolete: bool,
        skip_missing: bool,
        skip_transitive: bool,
        skip_misplaced_dev: bool,
        exclude: List[str],
        extend_exclude: List[str],
        ignore_notebooks: bool,
    ) -> None:
        self.ignore_obsolete = ignore_obsolete
        self.ignore_missing = ignore_missing
        self.ignore_transitive = ignore_transitive
        self.ignore_misplaced_dev = ignore_misplaced_dev
        self.exclude = exclude
        self.extend_exclude = extend_exclude
        self.ignore_notebooks = ignore_notebooks
        self.skip_obsolete = skip_obsolete
        self.skip_missing = skip_missing
        self.skip_transitive = skip_transitive
        self.skip_misplaced_dev = skip_misplaced_dev

    def run(self) -> Dict:

        self._log_config()

        dependencies = DependencyGetter().get()
        dev_dependencies = DependencyGetter(dev=True).get()

        all_python_files = PythonFileFinder(
            exclude=self.exclude + self.extend_exclude, ignore_notebooks=self.ignore_notebooks
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
        if not self.skip_misplaced_dev:
            result["misplaced_dev"] = MisplacedDevDependenciesFinder(
                imported_modules=imported_modules,
                dependencies=dependencies,
                ignore_misplaced_dev=self.ignore_misplaced_dev,
            ).find()

        return result

    def _log_config(self):
        logging.debug("Running with the following configuration:")
        for key, value in vars(self).items():
            logging.debug(f"{key}: {value}")
        logging.debug("\n")
