import logging
from typing import List

from deptry.dependency import Dependency
from deptry.module import Module


class TransitiveDependenciesFinder:
    """
    Given a list of imported modules and a list of project dependencies, determine which ones are transitive.
    """

    def __init__(
        self, imported_modules: List[Module], dependencies: List[Dependency], ignore_transitive: List[str] = []
    ) -> None:
        self.imported_modules = imported_modules
        self.imported_modules = self._filter_out_standard_library_from(self.imported_modules)
        self.dependencies = dependencies
        self.ignore_transitive = ignore_transitive

    def find(self) -> List[str]:
        logging.debug("\nScanning for transitive dependencies...")
        transitive_dependencies = self._get_transitive_dependencies()
        return transitive_dependencies

    def _get_transitive_dependencies(self):
        transitive_dependencies = []
        for module in self.imported_modules:
            if (
                module.package is not None
                and not self._module_in_any_top_level(module)
                and not self._module_in_dependencies(module)
                and not module.local_module
            ):
                if module.name in self.ignore_transitive:
                    logging.debug(f"Module '{module.package}' found to be a transitive dependency, but ignoring.")
                else:
                    transitive_dependencies.append(module.package)
                    logging.debug(f"Dependency '{module.package}' marked as a transitive dependency.")

        return transitive_dependencies

    def _module_in_any_top_level(self, module: Module) -> bool:
        for dependency in self.dependencies:
            if dependency.top_levels and module.name in dependency.top_levels:
                return True
        return False

    def _module_in_dependencies(self, module: Module) -> bool:
        for dependency in self.dependencies:
            if module.package == dependency.name:
                return True
        return False

    def _filter_out_standard_library_from(self, imported_modules: List[Module]):
        return [module for module in imported_modules if not module.standard_library]
