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
        dependencies = self._get_poetry_dependencies()
        self._log_dependencies(dependencies)

        dev_dependencies = self._get_poetry_dev_dependencies()
        self._log_dependencies(dev_dependencies, is_dev=True)

        return DependenciesExtract(dependencies, dev_dependencies)

    def _get_poetry_dependencies(self) -> list[Dependency]:
        pyproject_data = load_pyproject_toml(self.config)
        dependencies: dict[str, Any] = pyproject_data["tool"]["poetry"]["dependencies"]
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
        dependencies = []
        for dep, spec in poetry_dependencies.items():
            # dep is the dependency name, spec is the version specification, e.g. "^0.2.2" or {"*", optional = true}
            if dep != "python":
                optional = self._is_optional(spec)
                conditional = self._is_conditional(spec)
                dependencies.append(
                    Dependency(
                        dep,
                        self.config,
                        conditional=conditional,
                        optional=optional,
                        module_names=package_module_name_map.get(dep),
                    )
                )

        return dependencies

    @staticmethod
    def _is_optional(spec: str | dict[str, Any]) -> bool:
        """
        If a dependency specification is of the shape `isodate = {version = "*", optional = true}`, mark it as optional.
        """
        return bool(isinstance(spec, dict) and spec.get("optional"))

    @staticmethod
    def _is_conditional(spec: str | dict[str, Any]) -> bool:
        """
        If a dependency specification is of the shape `tomli = { version = "^2.0.1", python = "<3.11" }`, mark it as conditional.
        """
        return isinstance(spec, dict) and "python" in spec and "version" in spec
