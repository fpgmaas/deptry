import logging
import os

from deptry.utils import load_pyproject_toml


class DependencyManagementDetector:
    """
    Class to detect how dependencies are specified:
    - Either find a pyproject.toml with a [poetry.tool.dependencies] section
    - Or find a requirements.txt.

    If both are found, pyproject.toml is preferred.

    """

    def __init__(self) -> None:
        pass

    def detect(self):
        uses_pyproject_toml = self._check_if_project_uses_pyproject_toml_for_dependencies()
        uses_requirements_txt = self._check_if_project_uses_requirements_txt_for_dependencies()
        if uses_pyproject_toml and uses_requirements_txt:
            logging.debug(
                "Dependency specification found in both 'pyproject.toml' and 'requirements.txt'. Defaulting to 'pyproject.toml'."
            )
            return "pyproject_toml"
        elif uses_pyproject_toml:
            logging.debug("Dependency specification found in 'pyproject.toml'.")
            return "pyproject_toml"
        elif uses_requirements_txt:
            logging.debug("Dependency specification found in 'requirements.txt'")
            return "requirements_txt"
        else:
            raise FileNotFoundError(
                "No file called 'pyproject.toml' with a [tool.poetry.dependencies] section or a file called 'requirements.txt' found. Exiting."
            )

    @staticmethod
    def _check_if_project_uses_pyproject_toml_for_dependencies():
        if "pyproject.toml" in os.listdir():
            logging.debug("pyproject.toml found!")
            pyproject_toml = load_pyproject_toml()
            try:
                pyproject_toml["tool"]["poetry"]["dependencies"]
                return True
            except KeyError:
                logging.debug("Pyproject.toml found, but it is not used to specify the project's dependencies.")
                return False

    @staticmethod
    def _check_if_project_uses_requirements_txt_for_dependencies():
        if "requirements.txt" in os.listdir():
            return True
        return False
