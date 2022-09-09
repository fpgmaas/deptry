import logging
from typing import List

from deptry.dependency import Dependency
from deptry.module import Module


class TransitiveDependenciesFinder:
    """
    Given a list of imported modules and a list of project dependencies, determine which ones are transitive.
    This is done by elimination; if a module uses an installed package but the package is;
    - not a local directory
    - not in standard library
    - not a dependency
    - not a dev dependency

    Then it must be a transitive dependency.
    """

    def __init__(
        self, imported_modules: List[Module], dependencies: List[Dependency], ignore_transitive: List[str] = []
    ) -> None:
        self.imported_modules = imported_modules
        self.dependencies = dependencies
        self.ignore_transitive = ignore_transitive

    def find(self) -> List[str]:
        logging.debug("\nScanning for transitive dependencies...")
        transitive_dependencies = []
        for module in self.imported_modules:
            logging.debug(f"Scanning module {module.name}...")
            if self._is_transitive(module):
                transitive_dependencies.append(module.package)
        return transitive_dependencies

    def _is_transitive(self, module: Module) -> bool:
        if (
            module.package is not None
            and not module.is_dependency
            and not module.is_dev_dependency
            and not module.local_module
        ):
            if module.name in self.ignore_transitive:
                logging.debug(f"Dependency '{module.package}' found to be a transitive dependency, but ignoring.")
            else:
                logging.debug(f"Dependency '{module.package}' marked as a transitive dependency.")
                return True
        return False
