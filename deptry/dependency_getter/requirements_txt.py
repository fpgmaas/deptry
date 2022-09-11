import logging
import os
import re
from typing import List

from deptry.dependency import Dependency


class RequirementsTxtDependencyGetter:
    """
    Extract dependencies from a requirements.txt file.

    By default, dependencies are extracted from requirements.txt if dev = False, and from ["dev-requirements.txt", "requirements-dev.txt"]
    if dev = True, if any of these files exists. These defaults are overriden with the arguments requirements_txt and requirements_txt_dev.
    """

    def __init__(
        self,
        requirements_txt: str = "requirements.txt",
        requirements_txt_dev: List[str] = ["dev-requirements.txt", "requirements-dev.txt"],
        dev: bool = False,
    ) -> None:
        self.dev = dev
        self.requirements_txt = requirements_txt
        self.requirements_txt_dev = requirements_txt_dev

    def get(self):
        if not self.dev:
            dependencies = self._get_dependencies_from_requirements_txt(self.requirements_txt)
        else:
            dev_requirements_files = self._scan_for_dev_requirements_files()
            if dev_requirements_files:
                dependencies = []
                for file_name in dev_requirements_files:
                    dependencies += self._get_dependencies_from_requirements_txt(file_name)
            else:
                return []

        self._log_dependencies(dependencies=dependencies)
        return dependencies

    def _scan_for_dev_requirements_files(self):
        dev_requirements_files = [file_name for file_name in self.requirements_txt_dev if file_name in os.listdir()]
        if dev_requirements_files:
            logging.debug(f"Found files with development requirements! {dev_requirements_files}")
        return dev_requirements_files

    def _get_dependencies_from_requirements_txt(self, file_name: str):
        logging.debug(f"Scanning {file_name} for {'dev-' if self.dev else ''}dependencies")
        dependencies = []

        with open(file_name) as f:
            data = f.readlines()

        for line in data:
            dependency = self._extract_dependency_from_line(line)
            if dependency:
                dependencies.append(dependency)

        return dependencies

    def _extract_dependency_from_line(self, line: str) -> Dependency:
        line = self._remove_comments_from(line)
        line = self._remove_newlines_from(line)
        name = self._find_dependency_name_in(line)
        if name:
            line = line.replace(name, "")
            optional = self._check_if_dependency_is_optional(line)
            conditional = self._check_if_dependency_is_conditional(line)
            return Dependency(name=name, optional=optional, conditional=conditional)
        else:
            return None

    @staticmethod
    def _find_dependency_name_in(line):
        match = re.search("^[a-zA-Z0-9-_]+", line)
        if match and not match.group(0)[0] == "-":
            name = match.group(0)
            return name
        else:
            return None

    @staticmethod
    def _remove_comments_from(line):
        return re.sub(r"#.*", "", line).strip()

    @staticmethod
    def _remove_newlines_from(line):
        return line.replace("\n", "")

    @staticmethod
    def _check_if_dependency_is_optional(line):
        return True if re.findall(r"\[([a-zA-Z0-9-]+?)\]", line) else False

    @staticmethod
    def _check_if_dependency_is_conditional(line):
        return True if ";" in line else False

    def _log_dependencies(self, dependencies: List[Dependency]) -> None:
        logging.debug(f"The project contains the following {'dev-' if self.dev else ''}dependencies:")
        for dependency in dependencies:
            logging.debug(str(dependency))
        logging.debug("")
