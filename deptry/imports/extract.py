from __future__ import annotations

import logging
from collections import defaultdict
from typing import TYPE_CHECKING

from deptryrs import get_imports_from_file

from deptry.imports.extractors import NotebookImportExtractor

if TYPE_CHECKING:
    from pathlib import Path

    from deptryrs import Location


def get_imported_modules_for_list_of_files(list_of_files: list[Path]) -> dict[str, list[Location]]:
    logging.info("Scanning %d %s...", len(list_of_files), "files" if len(list_of_files) > 1 else "file")

    modules: dict[str, list[Location]] = defaultdict(list)

    for file in list_of_files:
        for module, locations in get_imported_modules_from_file(file).items():
            for location in locations:
                modules[module].append(location)

    logging.debug("All imported modules: %s\n", modules)

    return modules


def get_imported_modules_from_file(path_to_file: Path) -> dict[str, list[Location]]:
    logging.debug("Scanning %s...", path_to_file)

    if path_to_file.suffix == ".ipynb":
        modules = NotebookImportExtractor(path_to_file).extract_imports()
    elif path_to_file.suffix == ".py":
        modules = get_imports_from_file(str(path_to_file))

    logging.debug("Found the following imports in %s: %s", path_to_file, modules)

    return modules
