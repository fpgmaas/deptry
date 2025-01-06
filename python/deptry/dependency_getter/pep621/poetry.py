from __future__ import annotations

import contextlib
from dataclasses import dataclass
from typing import Any

from deptry.dependency import Dependency
from deptry.dependency_getter.pep621.base import PEP621DependencyGetter
from deptry.utils import load_pyproject_toml


@dataclass
class PoetryDependencyGetter(PEP621DependencyGetter):
    """
    Class that retrieves dependencies from a project that uses Poetry, either through PEP 621 syntax, Poetry specific
    syntax, or a mix of both.
    """

    def _get_dependencies(self) -> list[Dependency]:
        """
        Retrieve dependencies from either:
        - `[project.dependencies]` defined by PEP 621
        - `[tool.poetry.dependencies]` which is specific to Poetry

        If dependencies are set in `[project.dependencies]`, then assume that the project uses PEP 621 format to define
        dependencies. Even if `[tool.poetry.dependencies]` is populated, having entries in `[project.dependencies]`
        means that `[tool.poetry.dependencies]` is only used to enrich existing dependencies, and cannot be used to
        define additional ones.

        If no dependencies are found in `[project.dependencies]`, then extract dependencies present in
        `[tool.poetry.dependencies]`.
        """
        if dependencies := super()._get_dependencies():
            return dependencies

        pyproject_data = load_pyproject_toml(self.config)
        return self._extract_poetry_dependencies(pyproject_data["tool"]["poetry"].get("dependencies", {}))

    def _get_dev_dependencies(
        self,
        dependency_groups_dependencies: dict[str, list[Dependency]],
        dev_dependencies_from_optional: list[Dependency],
    ) -> list[Dependency]:
        """
        Poetry's development dependencies can be specified under either, or both:
        - [tool.poetry.dev-dependencies]
        - [tool.poetry.group.<group>.dependencies]
        """
        dev_dependencies = super()._get_dev_dependencies(dependency_groups_dependencies, dev_dependencies_from_optional)

        pyproject_data = load_pyproject_toml(self.config)
        poetry_dev_dependencies: dict[str, str] = {}

        with contextlib.suppress(KeyError):
            poetry_dev_dependencies = {
                **poetry_dev_dependencies,
                **pyproject_data["tool"]["poetry"]["dev-dependencies"],
            }

        try:
            dependency_groups = pyproject_data["tool"]["poetry"]["group"]
        except KeyError:
            dependency_groups = {}

        for group_values in dependency_groups.values():
            with contextlib.suppress(KeyError):
                poetry_dev_dependencies = {**poetry_dev_dependencies, **group_values["dependencies"]}

        return [*dev_dependencies, *self._extract_poetry_dependencies(poetry_dev_dependencies)]

    def _extract_poetry_dependencies(self, poetry_dependencies: dict[str, Any]) -> list[Dependency]:
        return [
            Dependency(dep, self.config, module_names=self.package_module_name_map.get(dep))
            for dep in poetry_dependencies
            if dep != "python"
        ]
