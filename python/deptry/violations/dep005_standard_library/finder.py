from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from deptry.imports.location import Location
from deptry.violations.base import ViolationsFinder
from deptry.violations.dep005_standard_library.violation import DEP005StandardLibraryDependencyViolation

if TYPE_CHECKING:
    from deptry.dependency import Dependency
    from deptry.module import ModuleLocations
    from deptry.violations import Violation


class DEP005StandardLibraryDependencyFinder(ViolationsFinder):
    """
    Finds dependencies that are part of the standard library but are defined as dependencies.
    """

    violation = DEP005StandardLibraryDependencyViolation

    def __init__(
        self,
        imported_modules_with_locations: list[ModuleLocations],
        dependencies: list[Dependency],
        stdlib_modules: set[str],
        ignored_modules: tuple[str, ...] = (),
    ):
        super().__init__(imported_modules_with_locations, dependencies, ignored_modules)
        self.stdlib_modules = stdlib_modules

    def find(self) -> list[Violation]:
        logging.debug("\nScanning for dependencies that are part of the standard library...")
        stdlib_violations: list[Violation] = []

        for dependency in self.dependencies:
            logging.debug("Scanning module %s...", dependency.name)

            if dependency.name in self.stdlib_modules:
                if dependency.name in self.ignored_modules:
                    logging.debug(
                        "Dependency '%s' found to be a dependency that is part of the standard library, but ignoring.",
                        dependency.name,
                    )
                    continue

                logging.debug(
                    "Dependency '%s' marked as a dependency that is part of the standard library.", dependency.name
                )
                stdlib_violations.append(self.violation(dependency, Location(dependency.definition_file)))

        return stdlib_violations
