from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from deptry.violations import Violation

if TYPE_CHECKING:
    from deptry.module import Module


@dataclass
class TransitiveDependencyViolation(Violation):
    issue: Module
