import logging
from typing import List

from deptry.dependency import Dependency
from deptry.module import Module


class MissingDependenciesFinder:
    """
    Given a list of imported modules and a list of project dependencies, determine which ones are missing.
    """

    def __init__(
        self, imported_modules: List[Module], dependencies: List[Dependency], ignore_missing: List[str] = []
    ) -> None:
        self.imported_modules = imported_modules
        self.dependencies = dependencies
        self.ignore_missing = ignore_missing

    def find(self) -> List[str]:
        logging.debug("\nScanning for missing dependencies...")
        missing_dependencies = []
        for module in self.imported_modules:
            logging.debug(f"Scanning module {module.name}...")
            if self._is_missing(module):
                missing_dependencies.append(module.name)
        return missing_dependencies

    def _is_missing(self, module: Module) -> bool:

        if (
            module.package is None
            and not module.is_dependency
            and not module.is_dev_dependency
            and not module.local_module
        ):
            if module.name in self.ignore_missing:
                logging.debug(f"Identified module '{module.name}' as a missing dependency, but ignoring.")
            else:
                logging.debug(
                    f"No package found to import module '{module.name}' from. Marked as a missing dependency."
                )
                return True
        return False
