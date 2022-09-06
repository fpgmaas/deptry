import logging
from pathlib import Path
from typing import List

import toml
from deptry.dependency import Dependency
from deptry.module import Module


class ObsoleteDependenciesFinder:
    """
    Given a list of imported packages in a project, fetch the project dependencies from pyproject.toml and
    determine which dependencies are not used in the project. Optionally, ignore_dependencies can be used
    to not mark packages as obsolete, even if they are not imported in the project.
    """

    def __init__(self, imported_modules: List[str], dependencies: List[Dependency]) -> None:
        self.imported_modules = [Module(mod, dependencies) for mod in imported_modules]
        logging.debug('')
        self.dependencies = dependencies

    def find(self) -> List[str]:
        logging.debug('Scanning for obsolete dependencies...')
        obsolete_dependencies = []

        for dependency in self.dependencies:
            if not self._dependency_found_in_imported_modules(dependency):
                if not self._any_of_the_top_levels_imported(dependency):
                    obsolete_dependencies.append(dependency)
                    logging.debug(f"Dependency '{dependency.name}' does not seem to be used.")
        
        logging.debug('')
        return [dependency.name for dependency in obsolete_dependencies]

    def _dependency_found_in_imported_modules(self, dependency: Dependency):
        for module in self.imported_modules:
            if module.package == dependency.name:
                logging.debug(f"Dependency '{dependency.name}' is used as module {module.package}.")
                return True
        else:
            return False


    def _any_of_the_top_levels_imported(self, dependency: Dependency):
        if not dependency.top_levels:
            return False
        else:
            for top_level in dependency.top_levels:
                if any(module.name == top_level for module in self.imported_modules):
                    logging.debug(f"Dependency '{dependency.name}' is not obsolete, since imported module '{top_level}' is in its top-level module names")
                    return True
        return False