from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from deptry.violations.base import Violation


@dataclass
class DEP005StandardLibraryDependencyViolation(Violation):
    error_code: ClassVar[str] = "DEP005"
    error_template: ClassVar[str] = (
        "'{name}' is defined as a dependency but it is included in the Python standard library."
    )

    def get_error_message(self) -> str:
        return self.error_template.format(name=self.issue.name)
