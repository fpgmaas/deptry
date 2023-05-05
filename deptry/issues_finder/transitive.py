from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from deptry.issues_finder.base import IssuesFinder
from deptry.violation import Violation

if TYPE_CHECKING:
    from deptry.module import Module


@dataclass
class TransitiveDependenciesFinder(IssuesFinder):
    """
    Given a list of imported modules and a list of project dependencies, determine which ones are transitive.
    This is done by elimination; if a module uses an installed package but the package is;
    - not a local directory
    - not in standard library
    - not a dependency
    - not a dev dependency

    Then it must be a transitive dependency.
    """

    def find(self) -> list[Violation]:
        logging.debug("\nScanning for transitive dependencies...")
        transitive_dependencies = []

        for module in self.imported_modules:
            logging.debug(f"Scanning module {module.name}...")

            if self._is_transitive(module):
                # `self._is_transitive` only returns `True` if the package is not None.
                transitive_dependencies.append(Violation(self.__class__, module))

        return transitive_dependencies

    def _is_transitive(self, module: Module) -> bool:
        if any([module.package is None, module.is_dependency, module.is_dev_dependency, module.local_module]):
            return False

        if module.name in self.ignored_modules:
            logging.debug(f"Dependency '{module.package}' found to be a transitive dependency, but ignoring.")
            return False

        logging.debug(f"Dependency '{module.package}' marked as a transitive dependency.")
        return True
