from __future__ import annotations

import ast
import itertools
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from deptry.imports.extractors.base import ImportExtractor


@dataclass
class NotebookImportExtractor(ImportExtractor):
    """Extract import statements from a Jupyter notebook."""

    def extract_imports(self) -> set[str]:
        notebook = self._read_ipynb_file(self.file)
        cells = self._keep_code_cells(notebook)
        import_statements = [self._extract_import_statements_from_cell(cell) for cell in cells]

        tree = ast.parse("\n".join(itertools.chain.from_iterable(import_statements)), str(self.file))

        return self._extract_imports_from_ast(tree)

    @staticmethod
    def _read_ipynb_file(path_to_ipynb: Path) -> dict[str, Any]:
        with open(path_to_ipynb) as f:
            notebook: dict[str, Any] = json.load(f)
        return notebook

    @staticmethod
    def _keep_code_cells(notebook: dict[str, Any]) -> list[dict[str, Any]]:
        return [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]

    @staticmethod
    def _contains_import_statements(line: str) -> bool:
        return re.search(r"^(?:from\s+(\w+)(?:\.\w+)?\s+)?import\s+([^\s,.]+)(?:\.\w+)?", line) is not None

    @classmethod
    def _extract_import_statements_from_cell(cls, cell: dict[str, Any]) -> list[str]:
        return [line for line in cell["source"] if cls._contains_import_statements(line)]

    @staticmethod
    def _flatten(list_of_lists: list[list[str]]) -> set[str]:
        return {item for sublist in list_of_lists for item in sublist}
