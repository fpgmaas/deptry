from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from deptry.violations.base import Violation


@dataclass
class DEP003TransitiveDependencyViolation(Violation):
    error_code: ClassVar[str] = "DEP003"
    error_template: ClassVar[str] = "'{name}' imported but it is a transitive dependency"

    def get_error_message(self) -> str:
        return self.error_template.format(name=self.issue.name)
