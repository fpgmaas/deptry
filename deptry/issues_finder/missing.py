from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from deptry.issues_finder.base import IssuesFinder
from deptry.violations import MissingDependencyViolation

if TYPE_CHECKING:
    from deptry.module import Module
    from deptry.violations import Violation


@dataclass
class MissingDependenciesFinder(IssuesFinder):
    """
    Given a list of imported modules and a list of project dependencies, determine which ones are missing.
    """

    def find(self) -> list[Violation]:
        logging.debug("\nScanning for missing dependencies...")
        missing_dependencies: list[Violation] = []

        for module_with_locations in self.imported_modules_with_locations:
            module = module_with_locations.module

            logging.debug(f"Scanning module {module.name}...")

            if self._is_missing(module):
                for location in module_with_locations.locations:
                    missing_dependencies.append(MissingDependencyViolation(module, location))

        return missing_dependencies

    def _is_missing(self, module: Module) -> bool:
        if any([module.package is not None, module.is_dependency, module.is_dev_dependency, module.local_module]):
            return False

        if module.name in self.ignored_modules:
            logging.debug(f"Identified module '{module.name}' as a missing dependency, but ignoring.")
            return False

        logging.debug(f"No package found to import module '{module.name}' from. Marked as a missing dependency.")
        return True
