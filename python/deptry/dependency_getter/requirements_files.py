from __future__ import annotations

import itertools
import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from deptry.dependency import parse_pep_508_dependency
from deptry.dependency_getter.base import DependenciesExtract, DependencyGetter

if TYPE_CHECKING:
    from deptry.dependency import Dependency


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
        # Note that `packaging` does not strip comments on purpose (https://github.com/pypa/packaging/issues/807), so we
        # need to remove the comments ourselves.
        return parse_pep_508_dependency(self._remove_comments_from(line), file_path, self.package_module_name_map)

    @staticmethod
    def _remove_comments_from(line: str) -> str:
        """
        Removes comments from a line. A comment is defined as any text following a '#' that is either at the start of
        the line or preceded by a space.
        This ensures that fragments like '#egg=' in URLs are not mistakenly removed.
        """
        return re.sub(r"(?<!\S)#.*", "", line).strip()
