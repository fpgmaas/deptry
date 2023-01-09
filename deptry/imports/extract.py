from __future__ import annotations

import itertools
import logging
from pathlib import Path

from deptry.imports.extractors import NotebookImportExtractor, PythonImportExtractor
from deptry.imports.extractors.base import ImportExtractor


def get_imported_modules_for_list_of_files(list_of_files: list[Path]) -> list[str]:
    logging.info(f"Scanning {len(list_of_files)} files...")

    modules = sorted(set(itertools.chain.from_iterable(get_imported_modules_from_file(file) for file in list_of_files)))

    logging.debug(f"All imported modules: {modules}\n")

    return modules


def get_imported_modules_from_file(path_to_file: Path) -> set[str]:
    logging.debug(f"Scanning {path_to_file}...")

    modules = _get_extractor_class(path_to_file)(path_to_file).extract_imports()

    logging.debug(f"Found the following imports in {str(path_to_file)}: {modules}")

    return modules


def _get_extractor_class(path_to_file: Path) -> type[ImportExtractor]:
    if path_to_file.suffix == ".ipynb":
        return NotebookImportExtractor
    return PythonImportExtractor
