from __future__ import annotations

import logging
from collections import defaultdict
from typing import TYPE_CHECKING

from deptry import get_imports_from_py_files
from deptry.imports.extractors import NotebookImportExtractor

if TYPE_CHECKING:
    from pathlib import Path

    from deptry import Location as RustLocation

from deptry.imports.location import Location


def get_imported_modules_from_list_of_files(list_of_files: list[Path]) -> dict[str, list[Location]]:
    logging.info("Scanning %d %s...", len(list_of_files), "files" if len(list_of_files) > 1 else "file")

    py_files = [str(file) for file in list_of_files if file.suffix == ".py"]
    ipynb_files = [file for file in list_of_files if file.suffix == ".ipynb"]

    modules: dict[str, list[Location]] = defaultdict(list)

    # Process all .py files in parallel using Rust
    if py_files:
        rust_result = get_imports_from_py_files(py_files)
        for module, locations in convert_rust_locations_to_python_locations(rust_result).items():
            modules[module].extend(locations)

    # Process each .ipynb file individually
    for file in ipynb_files:
        for module, locations in get_imported_modules_from_ipynb_file(file).items():
            modules[module].extend(locations)

    logging.debug("All imported modules: %s\n", modules)

    return modules


def get_imported_modules_from_ipynb_file(path_to_file: Path) -> dict[str, list[Location]]:
    logging.debug("Scanning %s...", path_to_file)

    modules = NotebookImportExtractor(path_to_file).extract_imports()

    modules = convert_rust_locations_to_python_locations(modules)
    logging.debug("Found the following imports in %s: %s", path_to_file, modules)
    return modules


def convert_rust_locations_to_python_locations(
    imported_modules: dict[str, list[RustLocation]],
) -> dict[str, list[Location]]:
    for module, locations in imported_modules.items():
        imported_modules[module] = [Location.from_rust_location_object(loc) for loc in locations]
    return imported_modules
