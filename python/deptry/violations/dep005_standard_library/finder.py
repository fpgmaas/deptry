from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from deptry.imports.location import Location
from deptry.violations.base import ViolationsFinder
from deptry.violations.dep005_standard_library.violation import DEP005StandardLibraryDependencyViolation

if TYPE_CHECKING:
    from deptry.violations import Violation


@dataclass
class DEP005StandardLibraryDependenciesFinder(ViolationsFinder):
    """
    Finds dependencies that are part of the standard library but are defined as dependencies.
    """

    violation = DEP005StandardLibraryDependencyViolation

    def find(self) -> list[Violation]:
        logging.debug("\nScanning for dependencies that are part of the standard library...")
        stdlib_violations: list[Violation] = []

        for dependency in self.dependencies:
            logging.debug("Scanning module %s...", dependency.name)

            if dependency.name in self.standard_library_modules:
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
