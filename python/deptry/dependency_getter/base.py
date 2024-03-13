from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from pathlib import Path

    from deptry.dependency import Dependency


@dataclass
class DependenciesExtract:
    dependencies: list[Dependency]
    dev_dependencies: list[Dependency]


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

    @abstractmethod
    def get(self) -> DependenciesExtract:
        """Get extracted dependencies and dev dependencies."""
        raise NotImplementedError()

    @staticmethod
    def _log_dependencies(dependencies: list[Dependency], is_dev: bool = False) -> None:
        logging.debug("The project contains the following %s:", "dev dependencies" if is_dev else "dependencies")

        for dependency in dependencies:
            logging.debug(dependency)

        logging.debug("")
