import logging
from pathlib import Path
from typing import Dict, List

import toml

from deptry.dependency import Dependency


class DependencyGetter:
    """
    Class to get a project's list of dependencies from pyproject.toml.

    Args:
        dev (bool): Read either the regular, or the dev dependencies, based on this argument.
    """

    def __init__(self, dev: bool = False) -> None:
        self.dev = dev

    def get(self):
        if self.dev:
            pyproject_toml_dependencies = self._get_pyproject_toml_dev_dependencies()
        else:
            pyproject_toml_dependencies = self._get_pyproject_toml_dependencies()

        dependencies = []
        for dep in pyproject_toml_dependencies:
            if not dep == "python":
                dependencies.append(Dependency(dep))
        self._log_dependencies(dependencies)
        return dependencies

    def _load_pyproject_toml(self) -> Dict:
        pyproject_text = Path("./pyproject.toml").read_text()
        return toml.loads(pyproject_text)

    def _get_pyproject_toml_dependencies(self) -> List[str]:
        pyproject_data = self._load_pyproject_toml()
        dependencies = list(pyproject_data["tool"]["poetry"]["dependencies"].keys())
        return sorted(dependencies)

    def _get_pyproject_toml_dev_dependencies(self) -> List[str]:
        dev_dependencies = {}
        pyproject_data = self._load_pyproject_toml()
        try:
            dev_dependencies = {**pyproject_data["tool"]["poetry"]["dev-dependencies"], **dev_dependencies}
        except KeyError:
            pass
        try:
            dev_dependencies = {**pyproject_data["tool"]["poetry"]["group"]["dev"]["dependencies"], **dev_dependencies}
        except KeyError:
            pass
        return sorted(dev_dependencies)

    def _log_dependencies(self, dependencies: List[Dependency]) -> None:
        logging.debug(f"The project contains the following {'dev-' if self.dev else ''}dependencies:")
        for dependency in dependencies:
            logging.debug(str(dependency))
        logging.debug("")
