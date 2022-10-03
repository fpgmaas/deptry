from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple

from deptry.dependency import Dependency
from deptry.module import Module


@dataclass
class IssuesFinder(ABC):
    """Base class for all issues finders."""

    imported_modules: List[Module]
    dependencies: List[Dependency]
    ignored_modules: Tuple[str, ...] = ()

    @abstractmethod
    def find(self) -> List[str]:
        """Find issues about dependencies."""
        raise NotImplementedError()
