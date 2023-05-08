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
    """Base class for all issues finders.

    This abstract class provides a common interface for classes that find issues related to project dependencies.
    Subclasses must implement the 'find' method, which returns a list of Violation objects representing the issues found.

    Attributes:
        imported_modules_with_locations: A list of ModuleLocations objects representing the
            modules imported by the project and their locations.
        dependencies: A list of Dependency objects representing the project's dependencies.
        ignored_modules: A tuple of module names to ignore when scanning for issues. Defaults to an
            empty tuple.

    """

    imported_modules_with_locations: list[ModuleLocations]
    dependencies: list[Dependency]
    ignored_modules: tuple[str, ...] = ()

    @abstractmethod
    def find(self) -> list[Violation]:
        """Find issues about dependencies."""
        raise NotImplementedError()
