from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from deptry.violation import Violation


@dataclass
class Reporter(ABC):
    """Base class for all violation reporters."""

    issues: dict[str, list[Violation]]

    @abstractmethod
    def report(self) -> None:
        raise NotImplementedError()
