from __future__ import annotations

import ast
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING

import chardet

from deptry.imports.location import Location

if TYPE_CHECKING:
    from pathlib import Path


@dataclass
class ImportExtractor(ABC):
    """
    Base class for other classes that can be used to extract the imported modules from a file.
    """

    file: Path

    @abstractmethod
    def extract_imports(self) -> dict[str, list[Location]]:
        raise NotImplementedError()

    def _extract_imports_from_ast(self, tree: ast.AST) -> dict[str, list[Location]]:
        """
        Given an Abstract Syntax Tree, find the imported top-level modules.
        For example, given the source tree of a file with contents:

            from pandas.tools import scatter_matrix

        Will return the set {"pandas"}.
        """

        imported_modules: dict[str, list[Location]] = defaultdict(list)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for module in node.names:
                    imported_modules[module.name.split(".")[0]].append(
                        Location(self.file, node.lineno, node.col_offset)
                    )
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                imported_modules[node.module.split(".")[0]].append(Location(self.file, node.lineno, node.col_offset))

        return imported_modules

    @staticmethod
    def _get_file_encoding(file: Path) -> str:
        with file.open("rb") as f:
            return chardet.detect(f.read())["encoding"]
