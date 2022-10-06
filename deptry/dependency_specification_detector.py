import logging
import os
from enum import Enum
from typing import Tuple

from deptry.utils import load_pyproject_toml


class DependencyManagementFormat(Enum):
    POETRY = "poetry"
    PDM = "pdm"
    REQUIREMENTS_TXT = "requirements_txt"


class DependencySpecificationDetector:
    """
    Class to detect how dependencies are specified:
    - Either find a pyproject.toml with a [poetry.tool.dependencies] section
    - Otherwise, find a pyproject.toml with a [tool.pdm] section
    - Otherwise, find a requirements.txt.

    """

    def __init__(self, requirements_txt: Tuple[str, ...] = ("requirements.txt",)) -> None:
        self.requirements_txt = requirements_txt

    def detect(self) -> DependencyManagementFormat:
        pyproject_toml_found = self._project_contains_pyproject_toml()
        if pyproject_toml_found and self._project_uses_poetry():
            return DependencyManagementFormat.POETRY
        if pyproject_toml_found and self._project_uses_pdm():
            return DependencyManagementFormat.PDM
        if self._project_uses_requirements_txt():
            return DependencyManagementFormat.REQUIREMENTS_TXT
        raise FileNotFoundError(
            "No file called 'pyproject.toml' with a [tool.poetry.dependencies] or [tool.pdm] section or file(s)"
            f" called '{', '.join(self.requirements_txt)}' found. Exiting."
        )

    @staticmethod
    def _project_contains_pyproject_toml() -> bool:
        if "pyproject.toml" in os.listdir():
            logging.debug("pyproject.toml found!")
            return True
        else:
            logging.debug("No pyproject.toml found.")
            return False

    @staticmethod
    def _project_uses_poetry() -> bool:
        pyproject_toml = load_pyproject_toml()
        try:
            pyproject_toml["tool"]["poetry"]["dependencies"]
            logging.debug(
                "pyproject.toml contains a [tool.poetry.dependencies] section, so Poetry is used to specify the"
                " project's dependencies."
            )
            return True
        except KeyError:
            logging.debug(
                "pyproject.toml does not contain a [tool.poetry.dependencies] section, so PDM is not used to specify"
                " the project's dependencies."
            )
            pass
        return False

    @staticmethod
    def _project_uses_pdm() -> bool:
        pyproject_toml = load_pyproject_toml()
        try:
            pyproject_toml["tool"]["pdm"]
            logging.debug(
                "pyproject.toml contains a [tool.pdm] section, so PDM is used to specify the project's dependencies."
            )
            return True
        except KeyError:
            logging.debug(
                "pyproject.toml does not contain a [tool.pdm] section, so PDM is not used to specify"
                " the project's dependencies."
            )
            pass
        return False

    def _project_uses_requirements_txt(self) -> bool:
        check = any(os.path.isfile(requirements_txt) for requirements_txt in self.requirements_txt)
        if check:
            logging.debug(
                f"Dependency specification found in '{', '.join(self.requirements_txt)}'. Will use this to determine"
                " the project's dependencies.\n"
            )
        return check
