from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from deptry.dependency_getter.pep621.base import PEP621DependencyGetter
from deptry.utils import load_pyproject_toml

if TYPE_CHECKING:
    from deptry.dependency import Dependency


@dataclass
class PDMDependencyGetter(PEP621DependencyGetter):
    """
    Class to get dependencies that are specified according to PEP 621 from a `pyproject.toml` file for a project that
    uses PDM for its dependency management.
    """

    def _get_dev_dependencies(self, dev_dependencies_from_optional: list[Dependency]) -> list[Dependency]:
        """
        Retrieve dev dependencies from pyproject.toml, which in PDM are specified as:

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
        dev_dependencies = super()._get_dev_dependencies(dev_dependencies_from_optional)

        pyproject_data = load_pyproject_toml(self.config)

        dev_dependency_strings: list[str] = []
        try:
            dev_dependencies_dict: dict[str, str] = pyproject_data["tool"]["pdm"]["dev-dependencies"]
            for deps in dev_dependencies_dict.values():
                dev_dependency_strings += deps
        except KeyError:
            logging.debug("No section [tool.pdm.dev-dependencies] found in pyproject.toml")

        return [*dev_dependencies, *self._extract_pep_508_dependencies(dev_dependency_strings)]
