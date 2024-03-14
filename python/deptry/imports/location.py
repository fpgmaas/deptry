from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from deptry.rust import Location as RustLocation


@dataclass(frozen=True)
class Location:
    file: Path
    line: int | None = None
    column: int | None = None

    @classmethod
    def from_rust_location_object(cls, location: RustLocation) -> Location:
        return cls(file=Path(location.file), line=location.line, column=location.column)
