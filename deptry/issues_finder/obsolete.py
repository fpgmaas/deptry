from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from deptry.imports.location import Location
from deptry.issues_finder.base import IssuesFinder
from deptry.violations import ObsoleteDependencyViolation

if TYPE_CHECKING:
    from deptry.dependency import Dependency
    from deptry.violations import Violation


@dataclass
class ObsoleteDependenciesFinder(IssuesFinder):
    """
    Finds obsolete dependencies by comparing a list of imported modules to a list of project dependencies.

    A dependency is considered obsolete if none of the following conditions hold:
    - A module with the exact name of the dependency is imported.
    - Any of the top-level modules of the dependency are imported.

    For example, 'matplotlib' has top-levels ['matplotlib', 'mpl_toolkits', 'pylab']. `mpl_toolkits` does not have
    any associated metadata, but if this is imported the associated dependency `matplotlib` is not obsolete,
    even if `matplotlib` itself is not imported anywhere.
    """

    def find(self) -> list[Violation]:
        logging.debug("\nScanning for obsolete dependencies...")
        obsolete_dependencies: list[Violation] = []

        for dependency in self.dependencies:
            logging.debug(f"Scanning module {dependency.name}...")

            if self._is_obsolete(dependency):
                obsolete_dependencies.append(
                    ObsoleteDependencyViolation(dependency, Location(dependency.definition_file))
                )

        return obsolete_dependencies

    def _is_obsolete(self, dependency: Dependency) -> bool:
        if self._dependency_found_in_imported_modules(dependency) or self._any_of_the_top_levels_imported(dependency):
            return False

        if dependency.name in self.ignored_modules:
            logging.debug(f"Dependency '{dependency.name}' found to be obsolete, but ignoring.")
            return False

        logging.debug(f"Dependency '{dependency.name}' does not seem to be used.")
        return True

    def _dependency_found_in_imported_modules(self, dependency: Dependency) -> bool:
        return any(
            module_with_locations.module.package == dependency.name
            for module_with_locations in self.imported_modules_with_locations
        )

    def _any_of_the_top_levels_imported(self, dependency: Dependency) -> bool:
        if not dependency.top_levels:
            return False

        return any(
            any(
                module_with_locations.module.name == top_level
                for module_with_locations in self.imported_modules_with_locations
            )
            for top_level in dependency.top_levels
        )
