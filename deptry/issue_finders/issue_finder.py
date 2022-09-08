import logging
from typing import List

from deptry.dependency import Dependency
from deptry.module import Module


class IssueFinder:
    """
    Helper class to find issues within a project's dependencies
    """

    def __init__(
        self, imported_modules: List[Module], dependencies: List[Dependency], list_to_ignore: List[str] = []
    ) -> None:
        self.imported_modules = imported_modules
        self.dependencies = dependencies
        self.list_to_ignore = list_to_ignore

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

    def _dependency_found_in_imported_modules(self, dependency: Dependency) -> bool:
        for module in self.imported_modules:
            if module.package == dependency.name:
                logging.debug(f"Dependency '{dependency.name}' is used as module '{module.name}'.")
                return True
        else:
            return False

    def _any_of_the_top_levels_imported(self, dependency: Dependency) -> bool:
        if not dependency.top_levels:
            return False
        else:
            for top_level in dependency.top_levels:
                if any(module.name == top_level for module in self.imported_modules):
                    logging.debug(
                        f"Dependency '{dependency.name}' is not obsolete, since imported module '{top_level}' is in its top-level module names"
                    )
                    return True
        return False
