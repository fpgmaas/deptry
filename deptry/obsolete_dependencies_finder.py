import logging
from pathlib import Path
from typing import List

import toml


class ObsoleteDependenciesFinder:
    """
    Given a list of imported packages in a project, fetch the project dependencies from pyproject.toml and
    determine which dependencies are not used in the project. Optionally, ignore_dependencies can be used
    to not mark packages as obsolete, even if they are not imported in the project.
    """

    def __init__(self, imported_packages: List[str], ignore_dependencies: List[str]):
        self.imported_packages = imported_packages
        self.ignore_dependencies = ignore_dependencies

    def find(self):
        dependencies = self._get_project_dependencies()
        logging.debug(f"The project's dependencies are: {dependencies}")
        logging.debug(f"The imported packages are: {self.imported_packages}")
        logging.debug(f"The dependencies to ignore are: {self.ignore_dependencies}")
        obsolete_dependencies = set(dependencies) - set(self.imported_packages) - set(["python"])
        if self.ignore_dependencies:
            obsolete_dependencies = obsolete_dependencies - set(self.ignore_dependencies)
        obsolete_dependencies = sorted(list(obsolete_dependencies))
        logging.debug(f"The obsolete dependencies are: {obsolete_dependencies}\n")
        return obsolete_dependencies

    def _get_project_dependencies(self):
        pyproject_text = Path("./pyproject.toml").read_text()
        pyproject_data = toml.loads(pyproject_text)
        dependencies = list(pyproject_data["tool"]["poetry"]["dependencies"].keys())
        return sorted(dependencies)
