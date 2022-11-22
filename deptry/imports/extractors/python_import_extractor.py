from __future__ import annotations

import ast
import logging
from dataclasses import dataclass

from deptry.imports.extractors.base import ImportExtractor


@dataclass
class PythonImportExtractor(ImportExtractor):
    """Extract import statements from a Python module."""

    def extract_imports(self) -> set[str]:
        try:
            with open(self.file) as python_file:
                tree = ast.parse(python_file.read(), str(self.file))
        except UnicodeDecodeError:
            try:
                with open(self.file, encoding=self._get_file_encoding(self.file)) as python_file:
                    tree = ast.parse(python_file.read(), str(self.file))
            except UnicodeDecodeError:
                logging.warning(f"Warning: File {self.file} could not be decoded. Skipping...")
                return set()

        return self._extract_imports_from_ast(tree)
