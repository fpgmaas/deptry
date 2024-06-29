from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from deptry.violations.dep004_misplaced_dev.violation import DEP

if TYPE_CHECKING:
    from deptry.module import Module
    from deptry.violations import Violation

    violation: ClassVar[type[Violation]]
    imported_modules_with_locations: list[ModuleLocations]
    dependencies: list[Dependency]
    modules_to_ignore: tuple[str, ...] = ()
    used_ignores: list[str] = []

    @abstractmethod
    def find(self) -> list[Violation]:
        """Find issues about dependencies."""
        raise NotImplementedError()


@dataclass
class DEP100UnusedIgnoresFinder:
    """
    TODO
    """