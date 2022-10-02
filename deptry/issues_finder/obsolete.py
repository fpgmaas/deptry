import logging
from dataclasses import dataclass
from typing import List

from deptry.dependency import Dependency
from deptry.issues_finder.base import IssuesFinder


@dataclass
class ObsoleteDependenciesFinder(IssuesFinder):
    """
    Given a list of imported modules and a list of project dependencies, determine which ones are obsolete.

    This is done by checking for each dependency if there is any module of which the metadata field 'Name' is equal to the dependency.
    If that is found, the dependency is not obsolete.
    Otherwise, we look at the top-level module names of the dependency, and check if any of those is imported. An example of this is
    'matplotlib' with top-levels: ['matplotlib', 'mpl_toolkits', 'pylab']. `mpl_toolkits` does not have any associated metadata,
    but if this is imported, the associated dependency `matplotlib` is not obsolete, even if `matplotlib` itself is not imported anywhere.
    """

    def find(self) -> List[str]:
        logging.debug("\nScanning for obsolete dependencies...")
        obsolete_dependencies = []
        for dependency in self.dependencies:
            logging.debug(f"Scanning module {dependency.name}...")

            if self._is_obsolete(dependency):
                obsolete_dependencies.append(dependency.name)

        return obsolete_dependencies

    def _is_obsolete(self, dependency: Dependency) -> bool:
        if self._dependency_found_in_imported_modules(dependency) or self._any_of_the_top_levels_imported(dependency):
            return False

        if dependency.name in self.ignored_modules:
            logging.debug(f"Dependency '{dependency.name}' found to be obsolete, but ignoring.")
            return False

        logging.debug(f"Dependency '{dependency.name}' does not seem to be used.")
        return True

    def _dependency_found_in_imported_modules(self, dependency: Dependency) -> bool:
        return any(module.package == dependency.name for module in self.imported_modules)

    def _any_of_the_top_levels_imported(self, dependency: Dependency) -> bool:
        if not dependency.top_levels:
            return False

        return any(
            any(module.name == top_level for module in self.imported_modules) for top_level in dependency.top_levels
        )
