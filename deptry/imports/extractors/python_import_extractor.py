from __future__ import annotations

import ast
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from deptry.imports.extractors.base import ImportExtractor

if TYPE_CHECKING:
    from deptry.imports.location import Location


@dataclass
class PythonImportExtractor(ImportExtractor):
    """Extract import statements from a Python module."""

    def extract_imports(self) -> dict[str, list[Location]]:
        """Extract all imported top-level modules from the Python file."""
        try:
            with self.file.open() as python_file:
                tree = ast.parse(python_file.read(), str(self.file))
        except (SyntaxError, ValueError):
            try:
                with self.file.open(encoding=self._get_file_encoding(self.file)) as python_file:
                    tree = ast.parse(python_file.read(), str(self.file))
            except UnicodeDecodeError:
                logging.warning("Warning: File %s could not be decoded. Skipping...", self.file)
                return {}

        return self._extract_imports_from_ast(tree)
