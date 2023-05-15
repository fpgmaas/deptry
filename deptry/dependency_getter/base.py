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
class InstallationOption:
    """
    Represents an installation option for a project.

    An installation option is a configuration that defines additional dependencies for a project.
    For example, given a project 'foo', a valid installation option would be
    `InstallationOption(name='plot', dependencies=['matplotlib'])`, which indicates that the 'plot'
    installation option requires the 'matplotlib' package. This installation option can be installed
    from PyPI as 'foo[plot]'. Setuptools refers to these as optional dependencies, while Poetry
    refers to them as extras.

    Attributes:
        name: The name of the installation option.
        dependencies: A list of additional dependencies required by the installation option.
    """

    name: str
    dependencies: list[str]

    def __repr__(self) -> str:
        return f"Installation option '{self.name}'"

    def __str__(self) -> str:
        return f"Installation option '{self.name}' with dependencies: {self.dependencies}."


@dataclass
class DependenciesExtract:
    dependencies: list[Dependency]
    dev_dependencies: list[Dependency]
    installation_options: list[InstallationOption] | None = None


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

    @staticmethod
    def _log_installation_options(installation_options: list[InstallationOption]) -> None:
        logging.debug("The project contains the following installation options:")

        for option in installation_options:
            logging.debug(option)

        logging.debug("")
