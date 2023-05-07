from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from deptry.dependency import Dependency
    from deptry.module import ModuleLocations
    from deptry.violations import Violation


@dataclass
class IssuesFinder(ABC):
    """Base class for all issues finders."""

    imported_modules_with_locations: list[ModuleLocations]
    dependencies: list[Dependency]
    ignored_modules: tuple[str, ...] = ()

    @abstractmethod
    def find(self) -> list[Violation]:
        """Find issues about dependencies."""
        raise NotImplementedError()
