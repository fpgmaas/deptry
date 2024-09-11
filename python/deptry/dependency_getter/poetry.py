from __future__ import annotations

import contextlib
from dataclasses import dataclass
from typing import Any

from deptry.dependency_getter.base import DependenciesExtract, DependencyExtract, DependencyGetter
from deptry.utils import load_pyproject_toml


@dataclass
class PoetryDependencyGetter(DependencyGetter):
    """Extract Poetry dependencies from pyproject.toml."""

    def get(self) -> DependenciesExtract:
        return DependenciesExtract(self._get_poetry_dependencies(), self._get_poetry_dev_dependencies())

    def _get_poetry_dependencies(self) -> list[DependencyExtract]:
        pyproject_data = load_pyproject_toml(self.config)
        dependencies: dict[str, Any] = pyproject_data["tool"]["poetry"].get("dependencies", {})
        return self._get_dependencies(dependencies)

    def _get_poetry_dev_dependencies(self) -> list[DependencyExtract]:
        """
        Poetry's development dependencies can be specified under either of the following:

        [tool.poetry.dev-dependencies]
        [tool.poetry.group.dev.dependencies]

        or both.
        """
        dependencies: dict[str, str] = {}
        pyproject_data = load_pyproject_toml(self.config)

        with contextlib.suppress(KeyError):
            dependencies = {**dependencies, **pyproject_data["tool"]["poetry"]["dev-dependencies"]}

        try:
            dependency_groups = pyproject_data["tool"]["poetry"]["group"]
        except KeyError:
            dependency_groups = {}

        for group_values in dependency_groups.values():
            with contextlib.suppress(KeyError):
                dependencies = {**dependencies, **group_values["dependencies"]}

        return self._get_dependencies(dependencies)

    def _get_dependencies(self, poetry_dependencies: dict[str, Any]) -> list[DependencyExtract]:
        return [DependencyExtract(dep, self.config) for dep in poetry_dependencies if dep != "python"]
