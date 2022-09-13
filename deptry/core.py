import logging
from pathlib import Path
from typing import Dict, List

from deptry.dependency import Dependency
from deptry.dependency_getter.pyproject_toml import PyprojectTomlDependencyGetter
from deptry.dependency_getter.requirements_txt import RequirementsTxtDependencyGetter
from deptry.dependency_specification_detector import DependencySpecificationDetector
from deptry.import_parser import ImportParser
from deptry.issue_finders.misplaced_dev import MisplacedDevDependenciesFinder
from deptry.issue_finders.missing import MissingDependenciesFinder
from deptry.issue_finders.obsolete import ObsoleteDependenciesFinder
from deptry.issue_finders.transitive import TransitiveDependenciesFinder
from deptry.module import Module, ModuleBuilder
from deptry.python_file_finder import PythonFileFinder
from deptry.result_logger import ResultLogger


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
        requirements_txt: str,
        requirements_txt_dev: List[str],
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
        self.requirements_txt = requirements_txt
        self.requirements_txt_dev = requirements_txt_dev

    def run(self) -> Dict:

        self._log_config()

        dependency_management_format = DependencySpecificationDetector(requirements_txt=self.requirements_txt).detect()
        dependencies, dev_dependencies = self._get_dependencies(dependency_management_format)

        all_python_files = PythonFileFinder(
            exclude=self.exclude + self.extend_exclude, ignore_notebooks=self.ignore_notebooks
        ).get_all_python_files_in(Path("."))

        imported_modules = ImportParser().get_imported_modules_for_list_of_files(all_python_files)
        imported_modules = [ModuleBuilder(mod, dependencies, dev_dependencies).build() for mod in imported_modules]
        imported_modules = [mod for mod in imported_modules if not mod.standard_library]

        issues = self._find_issues(imported_modules, dependencies, dev_dependencies)
        ResultLogger(issues=issues).log_and_exit()

    def _find_issues(
        self, imported_modules: List[Module], dependencies: List[Dependency], dev_dependencies: List[Dependency]
    ):
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
                dev_dependencies=dev_dependencies,
                ignore_misplaced_dev=self.ignore_misplaced_dev,
            ).find()
        return result

    def _get_dependencies(self, dependency_management_format: str):
        if dependency_management_format == "pyproject_toml":
            dependencies = PyprojectTomlDependencyGetter().get()
            dev_dependencies = PyprojectTomlDependencyGetter(dev=True).get()
        elif dependency_management_format == "requirements_txt":
            dependencies = RequirementsTxtDependencyGetter(requirements_txt=self.requirements_txt).get()
            dev_dependencies = RequirementsTxtDependencyGetter(
                dev=True, requirements_txt_dev=self.requirements_txt_dev
            ).get()
        else:
            raise ValueError(
                "Incorrect dependency manage format. Only pyproject.toml and requirements.txt are supported."
            )
        return dependencies, dev_dependencies

    def _log_config(self):
        logging.debug("Running with the following configuration:")
        for key, value in vars(self).items():
            logging.debug(f"{key}: {value}")
        logging.debug("")
