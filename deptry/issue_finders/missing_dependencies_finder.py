import logging
from typing import List

from deptry.dependency import Dependency
from deptry.issue_finders.issue_finder import IssueFinder
from deptry.module import Module


class MissingDependenciesFinder(IssueFinder):
    """
    Given a list of imported modules and a list of project dependencies, determine which ones are missing.
    TODO make one class dependencyfinder that the other three inherit from
    """

    def __init__(
        self, imported_modules: List[Module], dependencies: List[Dependency], list_to_ignore: List[str] = []
    ) -> None:
        super().__init__(imported_modules, dependencies, list_to_ignore)

    def find(self) -> List[str]:
        logging.debug("\nScanning for missing dependencies...")
        missing_dependencies = self._get_missing_dependencies()
        return missing_dependencies

    def _get_missing_dependencies(self):
        missing_dependencies = []
        for module in self.imported_modules:
            logging.info(f"Scanning module {module.name}...")
            if module.package is None and not self._module_in_any_top_level(module) and not module.is_local_module():
                if module.name in self.list_to_ignore:
                    logging.debug(f"Identified module '{module.name}' as a missing dependency, but ignoring.")
                else:
                    missing_dependencies.append(module.name)
                    logging.debug(
                        f"No package found to import module '{module.name}' from. Marked as a missing dependency."
                    )
        return missing_dependencies
