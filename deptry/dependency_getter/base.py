from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from deptry.dependency import Dependency


@dataclass
class DependenciesExtract:
    dependencies: list[Dependency]
    dev_dependencies: list[Dependency]


@dataclass
class DependencyGetter(ABC):
    """Base class for all dependency getter."""

    config: Path

    @abstractmethod
    def get(self) -> DependenciesExtract:
        """Get extracted dependencies and dev dependencies."""
        raise NotImplementedError()

    @staticmethod
    def _log_dependencies(dependencies: list[Dependency], is_dev: bool = False) -> None:
        logging.debug(f"The project contains the following {'dev ' if is_dev else ''}dependencies:")
        for dependency in dependencies:
            logging.debug(str(dependency))
        logging.debug("")
