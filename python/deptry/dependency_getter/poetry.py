from __future__ import annotations

import contextlib
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from deptry.dependency import Dependency
from deptry.dependency_getter.base import DependenciesExtract, DependencyGetter
from deptry.utils import load_pyproject_toml

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence


@dataclass
class PoetryDependencyGetter(DependencyGetter):
    """Extract Poetry dependencies from pyproject.toml."""

    def get(self) -> DependenciesExtract:
        return DependenciesExtract(self._get_poetry_dependencies(), self._get_poetry_dev_dependencies())

    def _get_poetry_dependencies(self) -> list[Dependency]:
        pyproject_data = load_pyproject_toml(self.config)
        dependencies: dict[str, Any] = pyproject_data["tool"]["poetry"].get("dependencies", {})
        return self._get_dependencies(dependencies, self.package_module_name_map)

    def _get_poetry_dev_dependencies(self) -> list[Dependency]:
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

        return self._get_dependencies(dependencies, self.package_module_name_map)

    def _get_dependencies(
        self, poetry_dependencies: dict[str, Any], package_module_name_map: Mapping[str, Sequence[str]]
    ) -> list[Dependency]:
        return [
            Dependency(dep, self.config, module_names=package_module_name_map.get(dep))
            for dep in poetry_dependencies
            if dep != "python"
        ]
