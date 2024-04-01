from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Mapping

from deptry.dependency_getter.pdm import PDMDependencyGetter
from deptry.dependency_getter.pep_621 import PEP621DependencyGetter
from deptry.dependency_getter.poetry import PoetryDependencyGetter
from deptry.dependency_getter.requirements_files import RequirementsTxtDependencyGetter
from deptry.exceptions import DependencySpecificationNotFoundError
from deptry.utils import load_pyproject_toml

if TYPE_CHECKING:
    from typing import Any

    from deptry.dependency_getter.base import DependencyGetter


@dataclass
class DependencyGetterBuilder:
    """
    Class to detect how dependencies are specified:
    - Either find a pyproject.toml with a [poetry.tool.dependencies] section
    - Otherwise, find a pyproject.toml with a [tool.pdm] section
    - Otherwise, find a pyproject.toml with a [project] section
    - Otherwise, find a requirements.txt.
    """

    config: Path
    package_module_name_map: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    pep621_dev_dependency_groups: tuple[str, ...] = ()
    requirements_files: tuple[str, ...] = ()
    requirements_files_dev: tuple[str, ...] = ()

    def build(self) -> DependencyGetter:
        pyproject_toml_found = self._project_contains_pyproject_toml()

        if pyproject_toml_found:
            pyproject_toml = load_pyproject_toml(self.config)

            if self._project_uses_poetry(pyproject_toml):
                return PoetryDependencyGetter(self.config, self.package_module_name_map)

            if self._project_uses_pdm(pyproject_toml):
                return PDMDependencyGetter(self.config, self.package_module_name_map, self.pep621_dev_dependency_groups)

            if self._project_uses_pep_621(pyproject_toml):
                return PEP621DependencyGetter(
                    self.config, self.package_module_name_map, self.pep621_dev_dependency_groups
                )

        if self._project_uses_requirements_files():
            return RequirementsTxtDependencyGetter(
                self.config, self.package_module_name_map, self.requirements_files, self.requirements_files_dev
            )

        raise DependencySpecificationNotFoundError(self.requirements_files)

    def _project_contains_pyproject_toml(self) -> bool:
        if self.config.exists():
            logging.debug("pyproject.toml found!")
            return True
        else:
            logging.debug("No pyproject.toml found.")
            return False

    @staticmethod
    def _project_uses_poetry(pyproject_toml: dict[str, Any]) -> bool:
        try:
            pyproject_toml["tool"]["poetry"]["dependencies"]
            logging.debug(
                "pyproject.toml contains a [tool.poetry.dependencies] section, so Poetry is used to specify the"
                " project's dependencies."
            )
        except KeyError:
            logging.debug(
                "pyproject.toml does not contain a [tool.poetry.dependencies] section, so Poetry is not used to specify"
                " the project's dependencies."
            )
            return False
        else:
            return True

    @staticmethod
    def _project_uses_pdm(pyproject_toml: dict[str, Any]) -> bool:
        try:
            pyproject_toml["tool"]["pdm"]["dev-dependencies"]
            logging.debug(
                "pyproject.toml contains a [tool.pdm.dev-dependencies] section, so PDM is used to specify the project's"
                " dependencies."
            )
        except KeyError:
            logging.debug(
                "pyproject.toml does not contain a [tool.pdm.dev-dependencies] section, so PDM is not used to specify"
                " the project's dependencies."
            )
            return False
        else:
            return True

    @staticmethod
    def _project_uses_pep_621(pyproject_toml: dict[str, Any]) -> bool:
        try:
            pyproject_toml["project"]
            logging.debug(
                "pyproject.toml contains a [project] section, so PEP 621 is used to specify the project's dependencies."
            )
        except KeyError:
            logging.debug(
                "pyproject.toml does not contain a [project] section, so PEP 621 is not used to specify the project's"
                " dependencies."
            )
            return False
        else:
            return True

    def _project_uses_requirements_files(self) -> bool:
        check = any(Path(requirements_files).is_file() for requirements_files in self.requirements_files)
        if check:
            logging.debug(
                "Dependency specification found in '%s'. Will use this to determine the project's dependencies.\n",
                ", ".join(self.requirements_files),
            )
        return check
