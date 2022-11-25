from __future__ import annotations

import itertools
import logging
from pathlib import Path

from deptry.imports.extractors import NotebookImportExtractor, PythonImportExtractor

# setuptools is usually available by default, so often not specified in dependencies.
_FILTERED_OUT_MODULES = {"setuptools"}


def get_imported_modules_for_list_of_files(list_of_files: list[Path]) -> list[str]:
    logging.info(f"Scanning {len(list_of_files)} files...")

    unique_modules = set(itertools.chain.from_iterable(get_imported_modules_from_file(file) for file in list_of_files))
    filtered_modules = sorted(_filter_out_modules(unique_modules))

    logging.debug(f"All imported modules: {filtered_modules}\n")

    return filtered_modules


def get_imported_modules_from_file(path_to_file: Path) -> set[str]:
    logging.debug(f"Scanning {path_to_file}...")

    if path_to_file.suffix == ".ipynb":
        modules = NotebookImportExtractor(path_to_file).extract_imports()
    else:
        modules = PythonImportExtractor(path_to_file).extract_imports()

    logging.debug(f"Found the following imports in {str(path_to_file)}: {modules}")

    return modules


def _filter_out_modules(modules: set[str]) -> set[str]:
    for filtered_out_module in _FILTERED_OUT_MODULES:
        if filtered_out_module in modules:
            logging.debug(f"Found module {filtered_out_module} to be imported, omitting from the list of modules.")

    return modules - _FILTERED_OUT_MODULES
