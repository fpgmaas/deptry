from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Pattern

from pathspec import PathSpec


@dataclass
class PythonFileFinder:
    """
    Get a list of all .py and .ipynb files recursively within a directory.
    Args:
        exclude: A list of regex patterns of paths to ignore.
        extend_exclude: An additional list of regex patterns of paths to ignore.
        using_default_exclude: Whether the exclude list was explicitly set, or the default was used.
        ignore_notebooks: If ignore_notebooks is set to True, .ipynb files are ignored and only .py files are returned.
    """

    exclude: tuple[str, ...]
    extend_exclude: tuple[str, ...]
    using_default_exclude: bool
    ignore_notebooks: bool = False

    def get_all_python_files_in(self, directories: tuple[Path, ...]) -> list[Path]:
        logging.debug("Collecting Python files to scan...")

        source_files = set()

        ignore_regex = re.compile("|".join(self.exclude + self.extend_exclude))
        file_lookup_suffixes = {".py"} if self.ignore_notebooks else {".py", ".ipynb"}

        gitignore_spec = self._generate_gitignore_pathspec(Path())

        for directory in directories:
            for root_str, dirs, files in os.walk(directory, topdown=True):
                root = Path(root_str)

                if self._is_directory_ignored(root, ignore_regex):
                    dirs[:] = []
                    continue

                for file_str in files:
                    file = root / file_str
                    if not self._is_file_ignored(file, file_lookup_suffixes, ignore_regex, gitignore_spec):
                        source_files.add(file)

        source_files_list = list(source_files)

        logging.debug("Python files to scan for imports:\n%s\n", "\n".join([str(file) for file in source_files_list]))

        return source_files_list

    def _is_directory_ignored(self, directory: Path, ignore_regex: Pattern[str]) -> bool:
        return bool((self.exclude + self.extend_exclude) and ignore_regex.match(str(directory)))

    def _is_file_ignored(
        self, file: Path, file_lookup_suffixes: set[str], ignore_regex: Pattern[str], gitignore_spec: PathSpec | None
    ) -> bool:
        return bool(
            file.suffix not in file_lookup_suffixes
            or ((self.exclude + self.extend_exclude) and ignore_regex.match(file.as_posix()))
            or (gitignore_spec and gitignore_spec.match_file(file))
        )

    def _generate_gitignore_pathspec(self, directory: Path) -> PathSpec | None:
        # If `exclude` is explicitly set, `.gitignore` is not taken into account.
        if not self.using_default_exclude:
            return None

        try:
            with (directory / ".gitignore").open() as gitignore:
                return PathSpec.from_lines("gitwildmatch", gitignore)
        except FileNotFoundError:
            return None
