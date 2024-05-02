from __future__ import annotations

import itertools
import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from deptry.dependency import Dependency
from deptry.dependency_getter.base import DependenciesExtract, DependencyGetter


@dataclass
class RequirementsTxtDependencyGetter(DependencyGetter):
    """Extract dependencies from requirements.txt files."""

    requirements_files: tuple[str, ...] = ("requirements.txt",)
    requirements_files_dev: tuple[str, ...] = ("dev-requirements.txt", "requirements-dev.txt")

    def get(self) -> DependenciesExtract:
        dependencies = list(
            itertools.chain(
                *(self._get_dependencies_from_requirements_files(file_name) for file_name in self.requirements_files)
            )
        )

        dev_dependencies = list(
            itertools.chain(
                *(
                    self._get_dependencies_from_requirements_files(file_name)
                    for file_name in self._scan_for_dev_requirements_files()
                )
            )
        )

        return DependenciesExtract(dependencies, dev_dependencies)

    def _scan_for_dev_requirements_files(self) -> list[str]:
        """
        Check if any of the files passed as requirements_files_dev exist, and if so; return them.
        """
        dev_requirements_files = [file_name for file_name in self.requirements_files_dev if file_name in os.listdir()]
        if dev_requirements_files:
            logging.debug("Found files with development requirements! %s", dev_requirements_files)
        return dev_requirements_files

    def _get_dependencies_from_requirements_files(self, file_name: str, is_dev: bool = False) -> list[Dependency]:
        logging.debug("Scanning %s for %s", file_name, "dev dependencies" if is_dev else "dependencies")
        dependencies = []

        file_path = Path(file_name)

        with file_path.open() as f:
            data = f.readlines()

        for line in data:
            dependency = self._extract_dependency_from_line(line, file_path)
            if dependency:
                dependencies.append(dependency)

        return dependencies

    def _extract_dependency_from_line(self, line: str, file_path: Path) -> Dependency | None:
        """
        Extract a dependency from a single line of a requirements.txt file.
        """
        line = self._remove_comments_from(line)
        line = self._remove_newlines_from(line)
        name = self._find_dependency_name_in(line)
        if name:
            return Dependency(
                name=name,
                definition_file=file_path,
                module_names=self.package_module_name_map.get(name),
            )
        else:
            return None

    def _find_dependency_name_in(self, line: str) -> str | None:
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
    def _remove_comments_from(line: str) -> str:
        """
        Removes comments from a line. A comment is defined as any text
        following a '#' that is either at the start of the line or preceded by a space.
        This ensures that fragments like '#egg=' in URLs are not mistakenly removed.
        """
        return re.sub(r"(?<!\S)#.*", "", line).strip()

    @staticmethod
    def _remove_newlines_from(line: str) -> str:
        return line.replace("\n", "")

    @staticmethod
    def _line_is_url(line: str) -> bool:
        return urlparse(line).scheme != ""

    @staticmethod
    def _extract_name_from_url(line: str) -> str | None:
        # Try to find egg, for url like git+https://github.com/xxxxx/package@xxxxx#egg=package
        match = re.search("egg=([a-zA-Z0-9-_]*)", line)
        if match:
            return match.group(1)

        # for url like git+https://github.com/name/python-module.git@0d6dc38d58
        match = re.search(r"\/((?:(?!\/).)*?)\.git", line)
        if match:
            return match.group(1)

        # for url like https://github.com/urllib3/urllib3/archive/refs/tags/1.26.8.zip
        match = re.search(r"\/((?:(?!\/).)*?)\/archive\/", line)
        if match:
            return match.group(1)

        logging.warning("Could not parse dependency name from url %s", line)
        return None
