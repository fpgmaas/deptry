import logging
from typing import List

from deptry.dependency import Dependency
from deptry.module import Module


class ObsoleteDependenciesFinder:
    """
    Given a list of imported modules and a list of project dependencies, determine which ones are obsolete.

    This is done by checking for each dependency if there is any module of which the metadata field 'Name' is equal to the dependency.
    If that is found, the dependency is not obsolete.
    Otherwise, we look at the top-level module names of the dependency, and check if any of those is imported. An example of this is
    'matplotlib' with top-levels: ['matplotlib', 'mpl_toolkits', 'pylab']. `mpl_toolkits` does not have any associated metadata,
    but if this is imported, the associated dependency `matplotlib` is not obsolete, even if `matplotlib` itself is not imported anywhere.
    """

    def __init__(
        self, imported_modules: List[Module], dependencies: List[Dependency], ignore_obsolete: List[str] = []
    ) -> None:
        self.imported_modules = imported_modules
        self.dependencies = dependencies
        self.ignore_obsolete = ignore_obsolete

    def find(self) -> List[str]:
        logging.debug("\nScanning for obsolete dependencies...")
        obsolete_dependencies = []
        for dependency in self.dependencies:

            logging.debug(f"Scanning module {dependency.name}...")

            if self._is_obsolete(dependency):
                obsolete_dependencies.append(dependency.name)

        return obsolete_dependencies

    def _is_obsolete(self, dependency: Dependency) -> bool:

        if not self._dependency_found_in_imported_modules(dependency) and not self._any_of_the_top_levels_imported(
            dependency
        ):
            if dependency.name in self.ignore_obsolete:
                logging.debug(f"Dependency '{dependency.name}' found to be obsolete, but ignoring.")
            else:
                logging.debug(f"Dependency '{dependency.name}' does not seem to be used.")
                return True
        return False

    def _dependency_found_in_imported_modules(self, dependency: Dependency) -> bool:
        for module in self.imported_modules:
            if module.package == dependency.name:
                return True
        else:
            return False

    def _any_of_the_top_levels_imported(self, dependency: Dependency) -> bool:
        if not dependency.top_levels:
            return False
        else:
            for top_level in dependency.top_levels:
                if any(module.name == top_level for module in self.imported_modules):
                    return True
        return False
