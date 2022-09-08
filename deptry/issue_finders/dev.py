import logging
from typing import List

from deptry.dependency import Dependency
from deptry.module import Module


class DevDependenciesFinder:
    """
    Given a list of imported modules and a list of project dependencies, determine which ones are transitive.
    """

    def __init__(
        self, imported_modules: List[Module], dependencies: List[Dependency], ignore_develop: List[str] = []
    ) -> None:
        self.imported_modules = imported_modules
        self.dependencies = dependencies
        self.ignore_develop = ignore_develop

    def find(self) -> List[str]:
        logging.debug("\nScanning for incorrect development dependencies...")
        dev_dependencies = []
        for module in self.imported_modules:
            logging.debug(f"Scanning module {module.name}...")
            if self._is_development_dependency(module):
                dev_dependencies.append(module.package)
        return dev_dependencies

    def _is_development_dependency(self, module: Module) -> bool:
        if module.dev_dependency:
            if module.name in self.ignore_develop:
                logging.debug(f"Module '{module.package}' found to be a development dependency, but ignoring.")
            else:
                logging.debug(f"Dependency '{module.package}' marked as a transitive dependency.")
                return True
        return False
