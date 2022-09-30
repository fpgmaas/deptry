import logging
import os
from typing import Tuple

from deptry.utils import load_pyproject_toml


class DependencySpecificationDetector:
    """
    Class to detect how dependencies are specified:
    - Either find a pyproject.toml with a [poetry.tool.dependencies] section
    - Or find a requirements.txt.

    If both are found, pyproject.toml is preferred.

    """

    def __init__(self, requirements_txt: Tuple[str, ...] = ("requirements.txt",)) -> None:
        self.requirements_txt = requirements_txt

    def detect(self) -> str:
        uses_pyproject_toml = self._check_if_project_uses_pyproject_toml_for_dependencies()
        uses_requirements_txt = self._check_if_project_uses_requirements_txt_for_dependencies()
        if uses_pyproject_toml and uses_requirements_txt:
            logging.info(
                "Found both 'pyproject.toml' with a [tool.poetry.dependencies] section and"
                f" '{', '.join(self.requirements_txt)}' requirements file(s). Defaulting to 'pyproject.toml'.\n"
            )
            return "pyproject_toml"
        elif uses_pyproject_toml:
            logging.debug(
                "Dependency specification found in 'pyproject.toml'. Will use this to determine the project's"
                " dependencies.\n"
            )
            return "pyproject_toml"
        elif uses_requirements_txt:
            logging.debug(
                f"Dependency specification found in '{', '.join(self.requirements_txt)}'. Will use this to determine"
                " the project's dependencies.\n"
            )
            return "requirements_txt"
        else:
            raise FileNotFoundError(
                "No file called 'pyproject.toml' with a [tool.poetry.dependencies] section or called"
                f" '{', '.join(self.requirements_txt)}' found. Exiting."
            )

    @staticmethod
    def _check_if_project_uses_pyproject_toml_for_dependencies() -> bool:
        if "pyproject.toml" in os.listdir():
            logging.debug("pyproject.toml found!")
            pyproject_toml = load_pyproject_toml()
            try:
                pyproject_toml["tool"]["poetry"]["dependencies"]
                logging.debug(
                    "pyproject.toml contains a [tool.poetry.dependencies] section, so it is used to specify the"
                    " project's dependencies."
                )
                return True
            except KeyError:
                logging.debug(
                    "pyproject.toml does not contain a [tool.poetry.dependencies] section, so it is not used to specify"
                    " the project's dependencies."
                )
                pass

        return False

    def _check_if_project_uses_requirements_txt_for_dependencies(self) -> bool:
        return any(os.path.isfile(requirements_txt) for requirements_txt in self.requirements_txt)
