import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

from deptry.dependency import Dependency
from deptry.dependency_getter.base import DependenciesExtract
from deptry.dependency_getter.pdm import PDMDependencyGetter
from deptry.dependency_getter.poetry import PoetryDependencyGetter
from deptry.dependency_getter.requirements_txt import RequirementsTxtDependencyGetter
from deptry.dependency_specification_detector import (
    DependencyManagementFormat,
    DependencySpecificationDetector,
)
from deptry.import_parser import ImportParser
from deptry.issues_finder.misplaced_dev import MisplacedDevDependenciesFinder
from deptry.issues_finder.missing import MissingDependenciesFinder
from deptry.issues_finder.obsolete import ObsoleteDependenciesFinder
from deptry.issues_finder.transitive import TransitiveDependenciesFinder
from deptry.json_writer import JsonWriter
from deptry.module import Module, ModuleBuilder
from deptry.python_file_finder import PythonFileFinder
from deptry.result_logger import ResultLogger


@dataclass
class Core:
    ignore_obsolete: Tuple[str, ...]
    ignore_missing: Tuple[str, ...]
    ignore_transitive: Tuple[str, ...]
    ignore_misplaced_dev: Tuple[str, ...]
    skip_obsolete: bool
    skip_missing: bool
    skip_transitive: bool
    skip_misplaced_dev: bool
    exclude: Tuple[str, ...]
    extend_exclude: Tuple[str, ...]
    ignore_notebooks: bool
    requirements_txt: Tuple[str, ...]
    requirements_txt_dev: Tuple[str, ...]
    json_output: str

    def run(self) -> None:
        self._log_config()

        dependency_management_format = DependencySpecificationDetector(requirements_txt=self.requirements_txt).detect()
        dependencies_extract = self._get_dependencies(dependency_management_format)

        all_python_files = PythonFileFinder(
            exclude=self.exclude + self.extend_exclude, ignore_notebooks=self.ignore_notebooks
        ).get_all_python_files_in(Path("."))

        imported_modules = [
            ModuleBuilder(mod, dependencies_extract.dependencies, dependencies_extract.dev_dependencies).build()
            for mod in ImportParser().get_imported_modules_for_list_of_files(all_python_files)
        ]
        imported_modules = [mod for mod in imported_modules if not mod.standard_library]

        issues = self._find_issues(imported_modules, dependencies_extract.dependencies)
        ResultLogger(issues=issues).log_and_exit()

        if self.json_output:
            JsonWriter(self.json_output).write(issues=issues)

        self._exit(issues)

    def _find_issues(self, imported_modules: List[Module], dependencies: List[Dependency]) -> Dict[str, List[str]]:
        result = {}
        if not self.skip_obsolete:
            result["obsolete"] = ObsoleteDependenciesFinder(imported_modules, dependencies, self.ignore_obsolete).find()
        if not self.skip_missing:
            result["missing"] = MissingDependenciesFinder(imported_modules, dependencies, self.ignore_missing).find()
        if not self.skip_transitive:
            result["transitive"] = TransitiveDependenciesFinder(
                imported_modules, dependencies, self.ignore_transitive
            ).find()
        if not self.skip_misplaced_dev:
            result["misplaced_dev"] = MisplacedDevDependenciesFinder(
                imported_modules, dependencies, self.ignore_misplaced_dev
            ).find()
        return result

    def _get_dependencies(self, dependency_management_format: DependencyManagementFormat) -> DependenciesExtract:
        if dependency_management_format is DependencyManagementFormat.POETRY:
            return PoetryDependencyGetter().get()
        if dependency_management_format is DependencyManagementFormat.PDM:
            return PDMDependencyGetter().get()
        if dependency_management_format is DependencyManagementFormat.REQUIREMENTS_TXT:
            return RequirementsTxtDependencyGetter(self.requirements_txt, self.requirements_txt_dev).get()
        raise ValueError("Incorrect dependency manage format. Only poetry, pdm and requirements.txt are supported.")

    def _log_config(self) -> None:
        logging.debug("Running with the following configuration:")
        for key, value in vars(self).items():
            logging.debug(f"{key}: {value}")
        logging.debug("")

    @staticmethod
    def _exit(issues: Dict[str, List[str]]) -> None:
        sys.exit(int(any(issues.values())))
