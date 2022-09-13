import logging
from typing import List

from deptry.dependency import Dependency
from deptry.module import Module


class MisplacedDevDependenciesFinder:
    """
    Given a list of imported modules and a list of project dependencies, determine which development dependencies
    should actually be regular dependencies.

    This is the case for any development dependency encountered, since files solely used for development purposes should be excluded from scanning.
    """

    def __init__(
        self,
        imported_modules: List[Module],
        dependencies: List[Dependency],
        dev_dependencies: List[Dependency],
        ignore_misplaced_dev: List[str] = [],
    ) -> None:
        self.imported_modules = imported_modules
        self.dependencies = dependencies
        self.dev_dependencies = dev_dependencies
        self.ignore_misplaced_dev = ignore_misplaced_dev

    def find(self) -> List[str]:
        """
        In this function, we use 'corresponding_package_name' instead of module.package, since it can happen that a
        development dependency is not installed, but it's still found to be used in the codebase, due to simple name matching.
        In that case, it's added under module.dev_top_levels. _get_package_name is added for these edge-cases.
        """
        logging.debug("\nScanning for incorrect development dependencies...")
        misplaced_dev_dependencies = []
        for module in self.imported_modules:
            logging.debug(f"Scanning module {module.name}...")
            corresponding_package_name = self._get_package_name(module)
            if corresponding_package_name:
                if self._is_development_dependency(module, corresponding_package_name):
                    misplaced_dev_dependencies.append(corresponding_package_name)
        return misplaced_dev_dependencies

    def _is_development_dependency(self, module: Module, corresponding_package_name: str) -> bool:
        if module.is_dev_dependency:
            if module.name in self.ignore_misplaced_dev:
                logging.debug(
                    f"Module '{corresponding_package_name}' found to be a misplaced development dependency, but ignoring."
                )
            else:
                logging.debug(
                    f"Dependency '{corresponding_package_name}' marked as a misplaced development dependency."
                )
                return True
        return False

    def _get_package_name(self, module: Module):
        if module.package:
            return module.package
        if module.dev_top_levels:
            if len(module.dev_top_levels) > 1:
                logging.debug(
                    f"Module {module.name} is found in the top-level module names of multiple development dependencies. Skipping."
                )
            elif len(module.dev_top_levels) == 0:
                logging.debug(
                    f"Module {module.name} has no metadata and it is not found in any top-level module names. Skipping."
                )
            else:
                return module.dev_top_levels[0]
        return None
