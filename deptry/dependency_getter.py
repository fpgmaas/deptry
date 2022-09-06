import logging
from pathlib import Path
from typing import List

import toml

from deptry.dependency import Dependency


class DependencyGetter:
    """
    Class to get a project's list of dependencies from pyproject.toml.

    Args:
        ignore_dependencies: A list of dependencies which should be omitted from the resulting list.
    """

    def __init__(self, ignore_dependencies: List[str] = []) -> None:
        self.ignore_dependencies = ignore_dependencies if ignore_dependencies else []

    def get(self):
        pyproject_toml_dependencies = self._get_pyproject_toml_dependencies()
        dependencies = []
        for dep in pyproject_toml_dependencies:
            if not dep == "python" and dep not in self.ignore_dependencies:
                dependencies.append(Dependency(dep))
        self._log_dependencies(dependencies)
        return dependencies

    def _get_pyproject_toml_dependencies(self) -> List[str]:
        pyproject_text = Path("./pyproject.toml").read_text()
        pyproject_data = toml.loads(pyproject_text)
        dependencies = list(pyproject_data["tool"]["poetry"]["dependencies"].keys())
        return sorted(dependencies)

    def _log_dependencies(self, dependencies: List[Dependency]) -> None:
        logging.debug("The project contains the following dependencies:")
        for dependency in dependencies:
            logging.debug(str(dependency))
        logging.debug("")
