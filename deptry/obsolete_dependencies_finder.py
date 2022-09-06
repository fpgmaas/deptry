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

    def __init__(self, imported_modules: List[str], dependencies: List[Dependency]) -> None:
        self.imported_modules = [Module(mod, dependencies) for mod in imported_modules]
        logging.debug("")
        self.dependencies = dependencies

    def find(self) -> List[str]:
        logging.debug("Scanning for obsolete dependencies...")
        obsolete_dependencies = []

        for dependency in self.dependencies:
            if not self._dependency_found_in_imported_modules(dependency):
                if not self._any_of_the_top_levels_imported(dependency):
                    obsolete_dependencies.append(dependency)
                    logging.debug(f"Dependency '{dependency.name}' does not seem to be used.")

        logging.debug("")
        return [dependency.name for dependency in obsolete_dependencies]

    def _dependency_found_in_imported_modules(self, dependency: Dependency) -> bool:
        for module in self.imported_modules:
            if module.package == dependency.name:
                logging.debug(f"Dependency '{dependency.name}' is used as module {module.package}.")
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
