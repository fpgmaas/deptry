from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from deptry.violations import Violation

if TYPE_CHECKING:
    from deptry.dependency import Dependency


@dataclass
class ObsoleteDependencyViolation(Violation):
    issue: Dependency
