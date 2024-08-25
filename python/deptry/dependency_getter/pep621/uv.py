from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from deptry.dependency_getter.pep621.base import PEP621DependencyGetter
from deptry.utils import load_pyproject_toml

if TYPE_CHECKING:
    from deptry.dependency import Dependency


@dataclass
class UvDependencyGetter(PEP621DependencyGetter):
    """
    Class to get dependencies that are specified according to PEP 621 from a `pyproject.toml` file for a project that
    uses uv for its dependency management.
    """

    def _get_dev_dependencies(self, dev_dependencies_from_optional: list[Dependency]) -> list[Dependency]:
        """
        Retrieve dev dependencies from pyproject.toml, which in uv are specified as:

        [tool.uv]
        dev-dependencies = [
            "pytest==8.3.2",
            "pytest-cov==5.0.0",
            "tox",
        ]

        Dev dependencies marked as such from optional dependencies are also added to the list of dev dependencies found.
        """
        dev_dependencies = super()._get_dev_dependencies(dev_dependencies_from_optional)

        pyproject_data = load_pyproject_toml(self.config)

        dev_dependency_strings: list[str] = []
        try:
            dev_dependency_strings = pyproject_data["tool"]["uv"]["dev-dependencies"]
        except KeyError:
            logging.debug("No section [tool.uv.dev-dependencies] found in pyproject.toml")

        return [*dev_dependencies, *self._extract_pep_508_dependencies(dev_dependency_strings)]
