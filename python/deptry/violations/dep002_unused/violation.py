from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from deptry.violations.base import Violation


@dataclass
class DEP002UnusedDependencyViolation(Violation):
    error_code: ClassVar[str] = "DEP002"
    error_template: ClassVar[str] = "'{name}' defined as a dependency but not used in the codebase"

    def get_error_message(self) -> str:
        return self.error_template.format(name=self.issue.name)
