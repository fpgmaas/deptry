from __future__ import annotations

import logging
import operator
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

from deptry.dependency_getter.pdm import PDMDependencyGetter
from deptry.dependency_getter.pep_621 import PEP621DependencyGetter
from deptry.dependency_getter.poetry import PoetryDependencyGetter
from deptry.dependency_getter.requirements_txt import RequirementsTxtDependencyGetter
from deptry.dependency_specification_detector import DependencyManagementFormat, DependencySpecificationDetector
from deptry.exceptions import IncorrectDependencyFormatError, UnsupportedPythonVersionError
from deptry.imports.extract import get_imported_modules_for_list_of_files
from deptry.module import ModuleBuilder, ModuleLocations
from deptry.python_file_finder import PythonFileFinder
from deptry.reporters import JSONReporter, TextReporter
from deptry.stdlibs import STDLIBS_PYTHON
from deptry.violations import (
    DEP001MissingDependenciesFinder,
    DEP001MissingDependencyViolation,
    DEP002UnusedDependenciesFinder,
    DEP002UnusedDependencyViolation,
    DEP003TransitiveDependenciesFinder,
    DEP003TransitiveDependencyViolation,
    DEP004MisplacedDevDependenciesFinder,
    DEP004MisplacedDevDependencyViolation,
)

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

    from deptry.dependency import Dependency
    from deptry.dependency_getter.base import DependenciesExtract
    from deptry.violations import Violation


@dataclass
class Core:
    root: tuple[Path, ...]
    config: Path
    no_ansi: bool
    per_rule_ignores: Mapping[str, tuple[str, ...]]
    ignore: tuple[str, ...]
    exclude: tuple[str, ...]
    extend_exclude: tuple[str, ...]
    using_default_exclude: bool
    ignore_notebooks: bool
    requirements_txt: tuple[str, ...]
    requirements_txt_dev: tuple[str, ...]
    known_first_party: tuple[str, ...]
    json_output: str
    package_module_name_map: Mapping[str, tuple[str, ...]]

    def run(self) -> None:
        self._log_config()

        dependency_management_format = DependencySpecificationDetector(
            self.config, requirements_txt=self.requirements_txt
        ).detect()
        dependencies_extract = self._get_dependencies(dependency_management_format)

        all_python_files = PythonFileFinder(
            self.exclude, self.extend_exclude, self.using_default_exclude, self.ignore_notebooks
        ).get_all_python_files_in(self.root)

        local_modules = self._get_local_modules()
        stdlib_modules = self._get_stdlib_modules()

        imported_modules_with_locations = [
            ModuleLocations(
                ModuleBuilder(
                    module,
                    local_modules,
                    stdlib_modules,
                    dependencies_extract.dependencies,
                    dependencies_extract.dev_dependencies,
                ).build(),
                locations,
            )
            for module, locations in get_imported_modules_for_list_of_files(all_python_files).items()
        ]
        imported_modules_with_locations = [
            module_with_locations
            for module_with_locations in imported_modules_with_locations
            if not module_with_locations.module.standard_library
        ]

        violations = self._find_violations(imported_modules_with_locations, dependencies_extract.dependencies)
        TextReporter(violations, use_ansi=not self.no_ansi).report()

        if self.json_output:
            JSONReporter(violations, self.json_output).report()

        self._exit(violations)

    def _find_violations(
        self, imported_modules_with_locations: list[ModuleLocations], dependencies: list[Dependency]
    ) -> list[Violation]:
        violations = []

        if DEP001MissingDependencyViolation.error_code not in self.ignore:
            violations.extend(
                DEP001MissingDependenciesFinder(
                    imported_modules_with_locations, dependencies, self.per_rule_ignores.get("DEP001", ())
                ).find()
            )

        if DEP002UnusedDependencyViolation.error_code not in self.ignore:
            violations.extend(
                DEP002UnusedDependenciesFinder(
                    imported_modules_with_locations, dependencies, self.per_rule_ignores.get("DEP002", ())
                ).find()
            )

        if DEP003TransitiveDependencyViolation.error_code not in self.ignore:
            violations.extend(
                DEP003TransitiveDependenciesFinder(
                    imported_modules_with_locations, dependencies, self.per_rule_ignores.get("DEP003", ())
                ).find()
            )

        if DEP004MisplacedDevDependencyViolation.error_code not in self.ignore:
            violations.extend(
                DEP004MisplacedDevDependenciesFinder(
                    imported_modules_with_locations, dependencies, self.per_rule_ignores.get("DEP004", ())
                ).find()
            )

        return self._get_sorted_violations(violations)

    @staticmethod
    def _get_sorted_violations(violations: list[Violation]) -> list[Violation]:
        return sorted(
            violations, key=operator.attrgetter("location.file", "location.line", "location.column", "error_code")
        )

    def _get_dependencies(self, dependency_management_format: DependencyManagementFormat) -> DependenciesExtract:
        if dependency_management_format is DependencyManagementFormat.POETRY:
            return PoetryDependencyGetter(self.config, self.package_module_name_map).get()
        if dependency_management_format is DependencyManagementFormat.PDM:
            return PDMDependencyGetter(self.config, self.package_module_name_map).get()
        if dependency_management_format is DependencyManagementFormat.PEP_621:
            return PEP621DependencyGetter(self.config, self.package_module_name_map).get()
        if dependency_management_format is DependencyManagementFormat.REQUIREMENTS_TXT:
            return RequirementsTxtDependencyGetter(
                self.config, self.package_module_name_map, self.requirements_txt, self.requirements_txt_dev
            ).get()
        raise IncorrectDependencyFormatError

    def _get_local_modules(self) -> set[str]:
        """
        Get all local Python modules from the source directories and `known_first_party` list.
        A module is considered a local Python module if it matches at least one of those conditions:
        - it is a directory that contains at least one Python file
        - it is a Python file that is not named `__init__.py` (since it is a special case)
        - it is set in the `known_first_party` list
        """
        guessed_local_modules = {
            path.stem for source in self.root for path in source.iterdir() if self._is_local_module(path)
        }

        return guessed_local_modules | set(self.known_first_party)

    @staticmethod
    def _is_local_module(path: Path) -> bool:
        """Guess if a module is a local Python module."""
        return bool(
            (path.is_file() and path.name != "__init__.py" and path.suffix == ".py")
            or (path.is_dir() and list(path.glob("*.py")))
        )

    @staticmethod
    def _get_stdlib_modules() -> frozenset[str]:
        if sys.version_info[:2] >= (3, 10):
            return sys.stdlib_module_names

        try:  # type: ignore[unreachable, unused-ignore]
            return STDLIBS_PYTHON[f"{sys.version_info[0]}{sys.version_info[1]}"]
        except KeyError as e:
            raise UnsupportedPythonVersionError((sys.version_info[0], sys.version_info[1])) from e

    def _log_config(self) -> None:
        logging.debug("Running with the following configuration:")
        for key, value in vars(self).items():
            logging.debug("%s: %s", key, value)
        logging.debug("")

    @staticmethod
    def _exit(violations: list[Violation]) -> None:
        sys.exit(bool(violations))
