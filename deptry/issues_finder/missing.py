import logging
from dataclasses import dataclass
from typing import List

from deptry.issues_finder.base import IssuesFinder
from deptry.module import Module


@dataclass
class MissingDependenciesFinder(IssuesFinder):
    """
    Given a list of imported modules and a list of project dependencies, determine which ones are missing.
    """

    def find(self) -> List[str]:
        logging.debug("\nScanning for missing dependencies...")
        missing_dependencies = []

        for module in self.imported_modules:
            logging.debug(f"Scanning module {module.name}...")

            if self._is_missing(module):
                missing_dependencies.append(module.name)

        return missing_dependencies

    def _is_missing(self, module: Module) -> bool:
        if any([module.package is not None, module.is_dependency, module.is_dev_dependency, module.local_module]):
            return False

        if module.name in self.ignored_modules:
            logging.debug(f"Identified module '{module.name}' as a missing dependency, but ignoring.")
            return False

        logging.debug(f"No package found to import module '{module.name}' from. Marked as a missing dependency.")
        return True
