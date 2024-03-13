from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from deptry.violations.base import Violation

if TYPE_CHECKING:
    from deptry.dependency import Dependency


@dataclass
class DEP002UnusedDependencyViolation(Violation):
    error_code: ClassVar[str] = "DEP002"
    error_template: ClassVar[str] = "'{name}' defined as a dependency but not used in the codebase"
    issue: Dependency

    def get_error_message(self) -> str:
        return self.error_template.format(name=self.issue.name)
