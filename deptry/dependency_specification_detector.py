from __future__ import annotations

import logging
from enum import Enum
from pathlib import Path

from deptry.exceptions import DependencySpecificationNotFoundError
from deptry.utils import load_pyproject_toml


class DependencyManagementFormat(Enum):
    PDM = "pdm"
    PEP_621 = "pep_621"
    POETRY = "poetry"
    REQUIREMENTS_TXT = "requirements_txt"


class DependencySpecificationDetector:
    """
    Class to detect how dependencies are specified:
    - Either find a pyproject.toml with a [poetry.tool.dependencies] section
    - Otherwise, find a pyproject.toml with a [tool.pdm] section
    - Otherwise, find a pyproject.toml with a [project] section
    - Otherwise, find a requirements.txt.

    """

    def __init__(self, config: Path, requirements_txt: tuple[str, ...] = ("requirements.txt",)) -> None:
        self.config = config
        self.requirements_txt = requirements_txt

    def detect(self) -> DependencyManagementFormat:
        pyproject_toml_found = self._project_contains_pyproject_toml()
        if pyproject_toml_found and self._project_uses_poetry():
            return DependencyManagementFormat.POETRY
        if pyproject_toml_found and self._project_uses_pdm():
            return DependencyManagementFormat.PDM
        if pyproject_toml_found and self._project_uses_pep_621():
            return DependencyManagementFormat.PEP_621
        if self._project_uses_requirements_txt():
            return DependencyManagementFormat.REQUIREMENTS_TXT

        raise DependencySpecificationNotFoundError(self.requirements_txt)

    def _project_contains_pyproject_toml(self) -> bool:
        if self.config.exists():
            logging.debug("pyproject.toml found!")
            return True
        else:
            logging.debug("No pyproject.toml found.")
            return False

    def _project_uses_poetry(self) -> bool:
        pyproject_toml = load_pyproject_toml(self.config)
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

    def _project_uses_pdm(self) -> bool:
        pyproject_toml = load_pyproject_toml(self.config)
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

    def _project_uses_pep_621(self) -> bool:
        pyproject_toml = load_pyproject_toml(self.config)
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

    def _project_uses_requirements_txt(self) -> bool:
        check = any(Path(requirements_txt).is_file() for requirements_txt in self.requirements_txt)
        if check:
            logging.debug(
                "Dependency specification found in '%s'. Will use this to determine the project's dependencies.\n",
                ", ".join(self.requirements_txt),
            )
        return check
