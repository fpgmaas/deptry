from __future__ import annotations

import logging
import re
from contextlib import suppress
from importlib import metadata
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence
    from importlib.metadata import Distribution


class Dependency:
    """
    A project's dependency with its associated top-level module names. There are stored in the metadata's top_level.txt.
    An example of this is 'matplotlib' with top-levels: ['matplotlib', 'mpl_toolkits', 'pylab'].

    By default, we also add the dependency's name with '-' replaced by '_' to the top-level modules.
    """

    def __init__(
        self, name: str, conditional: bool = False, optional: bool = False, module_names: Sequence[str] | None = None
    ) -> None:
        """
        Args:
            name: Name of the dependency, as shown in pyproject.toml
            conditional: boolean to indicate if the dependency is conditional, e.g. 'importlib-metadata': {'version': '*', 'python': '<=3.7'}
        """
        distribution = self.find_distribution(name)

        self.name = name
        self.is_conditional = conditional
        self.is_optional = optional
        self.found = distribution is not None
        self.top_levels = self._get_top_levels(name, distribution, module_names)

    def _get_top_levels(
        self, name: str, distribution: Distribution | None, module_names: Sequence[str] | None
    ) -> set[str]:
        if module_names is not None:
            return set(module_names)

        if distribution is not None:
            with suppress(FileNotFoundError):
                return self._get_top_level_module_names_from_top_level_txt(distribution)

            with suppress(FileNotFoundError):
                return self._get_top_level_module_names_from_record_file(distribution)

        # No metadata or other configuration has been found. As a fallback
        # we'll guess the name.
        module_name = name.replace("-", "_").lower()
        logging.warning(
            f"Assuming the corresponding module name of package {self.name!r} is {module_name!r}. Install the package"
            " or configure a package_module_name_map entry to override this behaviour."
        )
        return {module_name}

    def __repr__(self) -> str:
        return f"Dependency '{self.name}'"

    def __str__(self) -> str:
        return f"Dependency '{self.name}'{self._string_for_printing()}with top-levels: {self.top_levels}."

    @staticmethod
    def find_distribution(name: str) -> Distribution | None:
        try:
            return metadata.distribution(name)
        except metadata.PackageNotFoundError:
            return None

    def _string_for_printing(self) -> str:
        """
        Return 'Conditional', 'Optional' or 'Conditional and optional'
        """
        output_list = []
        if self.is_optional:
            output_list.append("optional")
        if self.is_conditional:
            output_list.append("conditional")

        if len(output_list) > 0:
            return f" ({', '.join(output_list)}) "
        else:
            return " "

    @staticmethod
    def _get_top_level_module_names_from_top_level_txt(distribution: Distribution) -> set[str]:
        """
        top-level.txt is a metadata file added by setuptools that looks as follows:

        610faff656c4cfcbb4a3__mypyc
        _black_version
        black
        blackd
        blib2to3

        This function extracts these names, if a top-level.txt file exists.
        """
        metadata_top_levels = distribution.read_text("top_level.txt")
        if metadata_top_levels is None:
            raise FileNotFoundError("top_level.txt")

        return {x for x in metadata_top_levels.splitlines() if x}

    @staticmethod
    def _get_top_level_module_names_from_record_file(distribution: Distribution) -> set[str]:
        """
        Get the top-level module names from the RECORD file, whose contents usually look as follows:

            ...
            ../../../bin/black,sha256=<HASH>,247
            __pycache__/_black_version.cpython-311.pyc,,
            _black_version.py,sha256=<HASH>,19
            black/trans.cpython-39-darwin.so,sha256=<HASH>
            black/trans.py,sha256=<HASH>
            blackd/__init__.py,sha256=<HASH>
            blackd/__main__.py,sha256=<HASH>
            ...

        So if no file top-level.txt is provided, we can try and extract top-levels from this file, in
        this case _black_version, black, and blackd.
        """
        metadata_records = distribution.read_text("RECORD")

        if metadata_records is None:
            raise FileNotFoundError("RECORD")

        matches = re.finditer(r"^(?!__)([a-zA-Z0-9-_]+)(?:/|\.py,)", metadata_records, re.MULTILINE)

        return {x.group(1) for x in matches}
