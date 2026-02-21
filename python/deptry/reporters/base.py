from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from deptry.violations import Violation


@dataclass
class Reporter(ABC):
    """Base class for all violation reporters."""

    violations: list[Violation]
    output_posix_paths: bool

    @abstractmethod
    def report(self) -> None:
        raise NotImplementedError()

    def _format_path(self, path: Path) -> str:
        if self.output_posix_paths:
            return str(path.as_posix())
        return str(path)
