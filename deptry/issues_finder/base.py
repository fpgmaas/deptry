from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from deptry.dependency import Dependency
from deptry.module import Module


@dataclass
class IssuesFinder(ABC):
    """Base class for all issues finders."""

    imported_modules: list[Module]
    dependencies: list[Dependency]
    ignored_modules: tuple[str, ...] = ()

    @abstractmethod
    def find(self) -> list[str]:
        """Find issues about dependencies."""
        raise NotImplementedError()
