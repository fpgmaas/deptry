import logging
from typing import Any, Dict, List, Union

from deptry.dependency import Dependency
from deptry.utils import load_pyproject_toml


class PyprojectTomlDependencyGetter:
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
            # dep is the dependency name, spec is the version specification, e.g. "^0.2.2" or {"*", optional = true}
            if not dep == "python":
                optional = self._is_optional(dep, spec)
                conditional = self._is_conditional(dep, spec)
                dependencies.append(Dependency(dep, conditional=conditional, optional=optional))

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

    @staticmethod
    def _is_optional(dep: str, spec: Union[str, dict]):
        # if of the shape `isodate = {version = "*", optional = true}` mark as optional`
        if isinstance(spec, dict) and "optional" in spec.keys() and spec["optional"]:
            return True
        return False

    @staticmethod
    def _is_conditional(dep: str, spec: Union[str, dict]):
        # if of the shape `tomli = { version = "^2.0.1", python = "<3.11" }`, mark as conditional.
        if isinstance(spec, dict) and "python" in spec.keys() and "version" in spec.keys():
            return True
        return False
