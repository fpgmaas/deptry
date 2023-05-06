from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Reporter(ABC):
    """Base class for all violation reporters."""

    issues: dict[str, list[str]]

    @abstractmethod
    def report(self) -> None:
        raise NotImplementedError()
