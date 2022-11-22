from __future__ import annotations

import ast
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

import chardet


@dataclass
class ImportExtractor(ABC):
    file: Path

    @abstractmethod
    def extract_imports(self) -> set[str]:
        raise NotImplementedError()

    @staticmethod
    def _extract_imports_from_ast(tree: ast.AST) -> set[str]:
        imported_modules: set[str] = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules |= {module.name.split(".")[0] for module in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                imported_modules.add(node.module.split(".")[0])

        return imported_modules

    @staticmethod
    def _get_file_encoding(file: Path) -> str:
        with open(file, "rb") as f:
            return chardet.detect(f.read())["encoding"]
