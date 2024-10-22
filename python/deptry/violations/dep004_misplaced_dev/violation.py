from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from deptry.violations.base import Violation


@dataclass
class DEP004MisplacedDevDependencyViolation(Violation):
    error_code: ClassVar[str] = "DEP004"
    error_template: ClassVar[str] = "'{name}' imported but declared as a dev dependency"

    def get_error_message(self) -> str:
        return self.error_template.format(name=self.issue.name)
