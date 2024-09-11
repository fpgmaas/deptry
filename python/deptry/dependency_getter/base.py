from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


@dataclass
class DependencyExtract:
    name: str
    definition_file: Path


@dataclass
class DependenciesExtract:
    dependencies: list[DependencyExtract]
    dev_dependencies: list[DependencyExtract]


@dataclass
class DependencyGetter(ABC):
    """Base class for all classes that extract a list of project's dependencies from a file.

    Args:
        config: The path to a configuration file that contains the project's dependencies.
    """

    config: Path

    @abstractmethod
    def get(self) -> DependenciesExtract:
        """Get extracted dependencies and dev dependencies."""
        raise NotImplementedError()
