import logging
from typing import List

from deptry.dependency import Dependency
from deptry.module import Module


class MissingDependenciesFinder:
    """
    Given a list of imported modules and a list of project dependencies, determine which ones are missing.
    TODO make one class dependencyfinder that the other three inherit from
    """

    def __init__(
        self, imported_modules: List[Module], dependencies: List[Dependency], ignore_missing: List[str] = []
    ) -> None:
        self.imported_modules = imported_modules
        self.imported_modules = self._filter_out_standard_library_from(self.imported_modules)
        self.dependencies = dependencies
        self.ignore_missing = ignore_missing

    def find(self) -> List[str]:
        logging.debug("\nScanning for missing dependencies...")
        missing_dependencies = self._get_missing_dependencies()
        return missing_dependencies

    def _get_missing_dependencies(self):
        missing_dependencies = []
        for module in self.imported_modules:
            if module.package is None and not self._module_in_any_top_level(module) and not module.local_module:
                if module.name in self.ignore_missing:
                    logging.debug(f"Identified module '{module.name}' as a missing dependency, but ignoring.")
                else:
                    missing_dependencies.append(module.name)
                    logging.debug(
                        f"No package found to import module '{module.name}' from. Marked as a missing dependency."
                    )
        return missing_dependencies

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
