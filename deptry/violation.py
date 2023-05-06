from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from deptry.dependency import Dependency
    from deptry.issues_finder.base import IssuesFinder
    from deptry.module import Module


@dataclass
class Violation:
    issue_type: type[IssuesFinder]
    issue: Dependency | Module
