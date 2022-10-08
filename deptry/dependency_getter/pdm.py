import logging
import re
from typing import Dict, List, Optional

from deptry.dependency import Dependency
from deptry.dependency_getter.base import DependenciesExtract, DependencyGetter
from deptry.utils import load_pyproject_toml


class PDMDependencyGetter(DependencyGetter):
    """
    Class to get dependencies that are specified according to PEP 621 from a `pyproject.toml` file for a project that uses PDM for its dependency management.
    """

    def get(self) -> DependenciesExtract:
        dependencies = self._get_pdm_dependencies()
        self._log_dependencies(dependencies)

        dev_dependencies = self._get_pdm_dev_dependencies()
        self._log_dependencies(dev_dependencies, is_dev=True)

        return DependenciesExtract(dependencies, dev_dependencies)

    @classmethod
    def _get_pdm_dependencies(cls) -> List[Dependency]:
        pyproject_data = load_pyproject_toml()
        dependency_strings: List[str] = pyproject_data["project"]["dependencies"]
        return cls._extract_dependency_objects_from(dependency_strings)

    @classmethod
    def _get_pdm_dev_dependencies(cls) -> List[Dependency]:
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
        pyproject_data = load_pyproject_toml()

        dev_dependency_strings: List[str] = []
        try:
            dev_dependencies_dict: Dict[str, str] = pyproject_data["tool"]["pdm"]["dev-dependencies"]
            for deps in dev_dependencies_dict.values():
                dev_dependency_strings += deps
        except KeyError:
            logging.debug("No section [tool.pdm.dev-dependencies] found in pyproject.toml")

        return cls._extract_dependency_objects_from(dev_dependency_strings)

    @classmethod
    def _extract_dependency_objects_from(cls, pdm_dependencies: List[str]) -> List[Dependency]:
        dependencies = []
        for spec in pdm_dependencies:
            # An example of a spec is `"tomli>=1.1.0; python_version < \"3.11\""`
            name = cls._find_dependency_name_in(spec)
            if name:
                optional = cls._is_optional(spec)
                conditional = cls._is_conditional(spec)
                dependencies.append(Dependency(name, conditional=conditional, optional=optional))
        return dependencies

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
