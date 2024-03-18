from __future__ import annotations

import logging
from collections import defaultdict
from typing import TYPE_CHECKING

from deptry.rust import get_imports_from_ipynb_files, get_imports_from_py_files

if TYPE_CHECKING:
    from pathlib import Path

    from deptry.rust import Location as RustLocation

from deptry.imports.location import Location


def get_imported_modules_from_list_of_files(list_of_files: list[Path]) -> dict[str, list[Location]]:
    logging.info("Scanning %d %s...", len(list_of_files), "files" if len(list_of_files) > 1 else "file")

    py_files = [str(file) for file in list_of_files if file.suffix == ".py"]
    ipynb_files = [str(file) for file in list_of_files if file.suffix == ".ipynb"]

    modules: dict[str, list[Location]] = defaultdict(list)

    # Process all .py files in parallel using Rust
    if py_files:
        rust_result = get_imports_from_py_files(py_files)
        for module, locations in convert_rust_locations_to_python_locations(rust_result).items():
            modules[module].extend(locations)

    # Process all .ipynb files in parallel using Rust
    if ipynb_files:
        rust_result = get_imports_from_ipynb_files(ipynb_files)
        for module, locations in convert_rust_locations_to_python_locations(rust_result).items():
            modules[module].extend(locations)

    logging.debug("All imported modules: %s\n", modules)

    return modules


def convert_rust_locations_to_python_locations(
    imported_modules: dict[str, list[RustLocation]],
) -> dict[str, list[Location]]:
    converted_modules: dict[str, list[Location]] = {}
    for module, locations in imported_modules.items():
        converted_modules[module] = [Location.from_rust_location_object(loc) for loc in locations]
    return converted_modules
