import logging
from typing import List

from deptry.dependency import Dependency
from deptry.issue_finders.issue_finder import IssueFinder
from deptry.module import Module


class ObsoleteDependenciesFinder(IssueFinder):
    """
    Given a list of imported modules and a list of project dependencies, determine which ones are obsolete.

    This is done by checking for each dependency if there is any module of which the metadata field 'Name' is equal to the dependency.
    If that is found, the dependency is not obsolete.
    Otherwise, we look at the top-level module names of the dependency, and check if any of those is imported. An example of this is
    'matplotlib' with top-levels: ['matplotlib', 'mpl_toolkits', 'pylab']. `mpl_toolkits` does not have any associated metadata,
    but if this is imported, the associated dependency `matplotlib` is not obsolete, even if `matplotlib` itself is not imported anywhere.
    """

    def __init__(
        self, imported_modules: List[Module], dependencies: List[Dependency], list_to_ignore: List[str] = []
    ) -> None:
        super().__init__(imported_modules, dependencies, list_to_ignore)

    def find(self) -> List[str]:
        logging.debug("\nScanning for obsolete dependencies...")
        obsolete_dependencies = []

        for dependency in self.dependencies:
            if not self._dependency_found_in_imported_modules(dependency) and not self._any_of_the_top_levels_imported(
                dependency
            ):
                if dependency.name in self.list_to_ignore:
                    logging.debug(f"Dependency '{dependency.name}' found to be obsolete, but ignoring.")
                else:
                    obsolete_dependencies.append(dependency)
                    logging.debug(f"Dependency '{dependency.name}' does not seem to be used.")

        return [dependency.name for dependency in obsolete_dependencies]
