import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

from deptry.dependency import Dependency


@dataclass
class DependenciesExtract:
    dependencies: List[Dependency]
    dev_dependencies: List[Dependency]


@dataclass
class DependencyGetter(ABC):
    """Base class for all dependency getter."""

    @abstractmethod
    def get(self) -> DependenciesExtract:
        """Get extracted dependencies and dev dependencies."""
        raise NotImplementedError()

    @staticmethod
    def _log_dependencies(dependencies: List[Dependency], is_dev: bool = False) -> None:
        logging.debug(f"The project contains the following {'dev ' if is_dev else ''}dependencies:")
        for dependency in dependencies:
            logging.debug(str(dependency))
        logging.debug("")
