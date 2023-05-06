from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True)
class Location:
    file: Path
    line: int | None = None
    column: int | None = None

    def format_for_terminal(self) -> str:
        if self.line is not None and self.column is not None:
            return f"{self.file}:{self.line}:{self.column}"
        return str(self.file)
