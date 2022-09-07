import logging
from typing import List

from deptry.dependency import Dependency
from deptry.module import Module

class MissingDependenciesFinder:
    """
    Given a list of imported modules and a list of project dependencies, determine which ones are missing.
    """

    def __init__(self, imported_modules: List[str], dependencies: List[Dependency]) -> None:
        self.imported_modules = [Module(mod, dependencies) for mod in imported_modules]
        logging.debug("")
        self.imported_modules = self._filter_out_standard_library_from(self.imported_modules)
        self.dependencies = dependencies

    def find(self) -> List[str]:
        logging.debug("Scanning for missing dependencies...")
        transitive_dependencies = self._get_transitive_dependencies()
        missing_dependencies = self._get_missing_dependencies()
        return {
            'transitive' : transitive_dependencies, 
        'missing' : missing_dependencies
        }


    def _get_transitive_dependencies(self):
        transitive_dependencies = []
        for module in self.imported_modules:
            if module.package is not None and not self._module_in_any_top_level(module) and not self._module_in_dependencies(module) and not module.local_module:
                transitive_dependencies.append(module.name)
        return transitive_dependencies

    def _get_missing_dependencies(self):
        missing_dependencies = []
        for module in self.imported_modules:
            if module.package is None and not self._module_in_any_top_level(module) and not module.local_module:
                missing_dependencies.append(module.name)
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