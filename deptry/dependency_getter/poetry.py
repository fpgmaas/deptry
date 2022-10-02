import contextlib
import logging
from typing import Any, Dict, List, Union

from deptry.dependency import Dependency
from deptry.utils import load_pyproject_toml


class PoetryDependencyGetter:
    """
    Class to get Poetry dependencies from a project's pyproject.toml.

    Args:
        dev (bool): Read either the regular, or the dev dependencies, based on this argument.
    """

    def __init__(self, dev: bool = False) -> None:
        self.dev = dev

    def get(self) -> List[Dependency]:
        if self.dev:
            poetry_dependencies = self._get_dev_dependencies()
        else:
            poetry_dependencies = self._get_dependencies()

        dependencies = []
        for dep, spec in poetry_dependencies.items():
            # dep is the dependency name, spec is the version specification, e.g. "^0.2.2" or {"*", optional = true}
            if dep != "python":
                optional = self._is_optional(spec)
                conditional = self._is_conditional(spec)
                dependencies.append(Dependency(dep, conditional=conditional, optional=optional))

        self._log_dependencies(dependencies)
        return dependencies

    @staticmethod
    def _get_dependencies() -> Dict[str, Any]:
        pyproject_data = load_pyproject_toml()
        dependencies: Dict[str, Any] = pyproject_data["tool"]["poetry"]["dependencies"]
        return dependencies

    @staticmethod
    def _get_dev_dependencies() -> Dict[str, Any]:
        """
        These can be either under;

        [tool.poetry.dev-dependencies]
        [tool.poetry.group.dev.dependencies]

        or both.
        """
        dev_dependencies: Dict[str, str] = {}
        pyproject_data = load_pyproject_toml()

        with contextlib.suppress(KeyError):
            dev_dependencies = {**pyproject_data["tool"]["poetry"]["dev-dependencies"], **dev_dependencies}

        with contextlib.suppress(KeyError):
            dev_dependencies = {**pyproject_data["tool"]["poetry"]["group"]["dev"]["dependencies"], **dev_dependencies}

        return dev_dependencies

    def _log_dependencies(self, dependencies: List[Dependency]) -> None:
        logging.debug(f"The project contains the following {'dev-' if self.dev else ''}dependencies:")
        for dependency in dependencies:
            logging.debug(str(dependency))
        logging.debug("")

    @staticmethod
    def _is_optional(spec: Union[str, Dict[str, Any]]) -> bool:
        # if of the shape `isodate = {version = "*", optional = true}` mark as optional`
        return bool(isinstance(spec, dict) and spec.get("optional"))

    @staticmethod
    def _is_conditional(spec: Union[str, Dict[str, Any]]) -> bool:
        # if of the shape `tomli = { version = "^2.0.1", python = "<3.11" }`, mark as conditional.
        return isinstance(spec, dict) and "python" in spec and "version" in spec
