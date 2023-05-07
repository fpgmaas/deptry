from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from deptry.dependency import Dependency
    from deptry.imports.location import Location
    from deptry.module import Module


@dataclass
class Violation(ABC):
    error_code: ClassVar[str] = ""
    error_template: ClassVar[str] = ""
    issue: Dependency | Module
    location: Location

    @abstractmethod
    def get_error_message(self) -> str:
        raise NotImplementedError()
