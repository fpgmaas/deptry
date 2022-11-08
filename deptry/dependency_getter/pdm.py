import logging
from dataclasses import dataclass
from typing import Dict, List

from deptry.dependency import Dependency
from deptry.dependency_getter.base import DependenciesExtract
from deptry.dependency_getter.pep_621 import PEP621DependencyGetter
from deptry.utils import load_pyproject_toml


@dataclass
class PDMDependencyGetter(PEP621DependencyGetter):
    """
    Class to get dependencies that are specified according to PEP 621 from a `pyproject.toml` file for a project that uses PDM for its dependency management.
    """

    def get(self) -> DependenciesExtract:
        pep_621_dependencies_extract = super().get()

        dev_dependencies = self._get_pdm_dev_dependencies()
        self._log_dependencies(dev_dependencies, is_dev=True)

        return DependenciesExtract(pep_621_dependencies_extract.dependencies, dev_dependencies)

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

        return cls._extract_pep_508_dependencies(dev_dependency_strings)
