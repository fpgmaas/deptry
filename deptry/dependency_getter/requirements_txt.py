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
            dependencies = self._get_dependencies_from_requirements_file(self.requirements_txt)
        else:
            dev_requirements_files = self._scan_for_dev_requirements_files()
            if dev_requirements_files:
                dependencies = []
                for file_name in dev_requirements_files:
                    dependencies += self._get_dependencies_from_requirements_file(file_name)
            else:
                return []

        self._log_dependencies(dependencies=dependencies)
        return dependencies

    def _scan_for_dev_requirements_files(self):
        """
        Check if any of the files passed as requirements_txt_dev exist, and if so; return them.
        """
        dev_requirements_files = [file_name for file_name in self.requirements_txt_dev if file_name in os.listdir()]
        if dev_requirements_files:
            logging.debug(f"Found files with development requirements! {dev_requirements_files}")
        return dev_requirements_files

    def _get_dependencies_from_requirements_file(self, file_name: str):
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
        """
        Extract a dependency from a single line of a requirements.txt file.
        """
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

    def _find_dependency_name_in(self, line):
        """
        Find the dependency name of a dependency specified according to the pip-standards for requirement.txt
        """
        if self._line_is_url(line):
            return self._extract_name_from_url(line)
        else:
            match = re.search("^[^-][a-zA-Z0-9-_]+", line)
            if match:
                return match.group(0)
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

    @staticmethod
    def _line_is_url(line):
        return re.search("^(http|https|git\+https)", line)

    @staticmethod
    def _extract_name_from_url(line):

        # for url like git+https://github.com/name/python-module.git@0d6dc38d58
        match = re.search("\/((?:(?!\/).)*?)\.git", line)
        if match:
            return match.group(1)

        # for url like https://github.com/urllib3/urllib3/archive/refs/tags/1.26.8.zip
        match = re.search("\/((?:(?!\/).)*?)\/archive\/", line)
        if match:
            return match.group(1)

        logging.warning(f"Could not parse dependency name from url {line}")
        return None
