import logging
from typing import Any, Dict, List

from deptry.dependency import Dependency
from deptry.utils import load_pyproject_toml


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
        for dep, spec in pyproject_toml_dependencies.items():
            if not dep == "python":
                # if of the shape `tomli = { version = "^2.0.1", python = "<3.11" }`, mark as conditional.
                if isinstance(spec, dict) and "python" in spec.keys() and "version" in spec.keys():
                    dependencies.append(Dependency(dep, conditional=True))
                else:
                    dependencies.append(Dependency(dep))
        dependencies.sort(key=lambda x: x.name)
        self._log_dependencies(dependencies)
        return dependencies

    def _get_pyproject_toml_dependencies(self) -> Dict[str, Any]:
        pyproject_data = load_pyproject_toml()
        dependencies = pyproject_data["tool"]["poetry"]["dependencies"]
        return dependencies

    def _get_pyproject_toml_dev_dependencies(self) -> Dict[str, Any]:
        """
        These can be either under;

        [tool.poetry.dev-dependencies]
        [tool.poetry.group.dev.dependencies]

        or both.
        """
        dev_dependencies = {}
        pyproject_data = load_pyproject_toml()
        try:
            dev_dependencies = {**pyproject_data["tool"]["poetry"]["dev-dependencies"], **dev_dependencies}
        except KeyError:
            pass
        try:
            dev_dependencies = {**pyproject_data["tool"]["poetry"]["group"]["dev"]["dependencies"], **dev_dependencies}
        except KeyError:
            pass
        return dev_dependencies

    def _log_dependencies(self, dependencies: List[Dependency]) -> None:
        logging.debug(f"The project contains the following {'dev-' if self.dev else ''}dependencies:")
        for dependency in dependencies:
            logging.debug(str(dependency))
        logging.debug("")
