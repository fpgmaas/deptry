from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from importlib import metadata
from typing import TYPE_CHECKING

from deptry.dependency import Dependency

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from pathlib import Path


@dataclass
class DependenciesExtract:
    dependencies: list[Dependency]
    dev_dependencies: list[Dependency]
    transitive_dependencies: list[Dependency]


@dataclass
class DependencyGetter(ABC):
    """Base class for all classes that extract a list of project's dependencies from a file.

    Args:
        config: The path to a configuration file that contains the project's dependencies.
        package_module_name_map: A mapping of package names to their corresponding module names that may not be found
        otherwise from the package's metadata. The keys in the mapping should be package names, and the values should
        be sequences of module names associated with the package.
    """

    config: Path
    package_module_name_map: Mapping[str, Sequence[str]] = field(default_factory=dict)

    def get(self) -> DependenciesExtract:
        dependencies, dev_dependencies = self._get_direct_dependencies()

        return DependenciesExtract(
            dependencies, dev_dependencies, self._get_transitive_dependencies(dependencies, dev_dependencies)
        )

    @abstractmethod
    def _get_direct_dependencies(self) -> tuple[list[Dependency], list[Dependency]]:
        raise NotImplementedError

    def _get_transitive_dependencies(
        self, dependencies: list[Dependency], dev_dependencies: list[Dependency]
    ) -> list[Dependency]:
        return [
            Dependency(dependency, module_names=self.package_module_name_map.get(dependency))
            for dependency in set(self._get_installed_dependencies()).difference(
                {d.name for d in dependencies},
                {d.name for d in dev_dependencies},
            )
        ]

    @staticmethod
    def _get_installed_dependencies() -> list[str]:
        return [distribution.name for distribution in metadata.distributions()]
