import contextlib
import logging
from typing import Any, Dict, List, Union, Optional

import re

from deptry.dependency import Dependency
from deptry.utils import load_pyproject_toml


class PdmDependencyGetter:
    """
    Class to get dependencies from a project's pyproject.toml that are specified according to PEP621 and that is managed with PDM.

    Args:
        dev (bool): Read either the regular, or the dev dependencies, based on this argument.
    """

    def __init__(self, dev: bool = False) -> None:
        self.dev = dev

    def get(self) -> List[Dependency]:
        if self.dev:
            pdm_dependencies = self._get_dev_dependencies()
        else:
            pdm_dependencies = self._get_dependencies()

        dependencies = []
        for spec in pdm_dependencies:
            # An example of a spec is `"tomli>=1.1.0; python_version < \"3.11\""`
            name = self._find_dependency_name_in(spec)
            if name:
                optional = self._is_optional(spec)
                conditional = self._is_conditional(spec)
                dependencies.append(Dependency(name, conditional=conditional, optional=optional))

        self._log_dependencies(dependencies)
        return dependencies

    @staticmethod
    def _get_dependencies() -> List[str]:
        pyproject_data = load_pyproject_toml()
        dependencies: List[str] = pyproject_data["project"]["dependencies"]
        return dependencies

    @staticmethod
    def _get_dev_dependencies() -> List[str]:
        """
        Try to get development dependencies from pyproject.toml, which with PDM are specified as:

        [tool.pdm.dev-dependencies]
        test = [
            "pytest",
            "pytest-cov",
        ]
        tox = [
            "tox",
            "tox-pdm>=0.5",
        ]
        """
        dev_dependencies: List[str] = []
        pyproject_data = load_pyproject_toml()

        with contextlib.suppress(KeyError):
            dev_dependencies_dict: Dict[str, str] = pyproject_data["tool"]["pdm"]["dev-dependencies"]
            for deps in dev_dependencies_dict.values():
                dev_dependencies += deps

        return dev_dependencies

    def _log_dependencies(self, dependencies: List[Dependency]) -> None:
        logging.debug(f"The project contains the following {'dev-' if self.dev else ''}dependencies:")
        for dependency in dependencies:
            logging.debug(str(dependency))
        logging.debug("")

    @staticmethod
    def _is_optional(dependency_specification: str) -> bool:
        return bool(re.findall(r"\[([a-zA-Z0-9-]+?)\]", dependency_specification))

    @staticmethod
    def _is_conditional(dependency_specification: str) -> bool:
        return ";" in dependency_specification

    @staticmethod
    def _find_dependency_name_in(spec: str) -> Optional[str]:
        match = re.search("[a-zA-Z0-9-_]+", spec)
        if match:
            return match.group(0)
        return None