import logging
import re
from typing import List, Set

from deptry.compat import PackageNotFoundError, metadata


class Dependency:
    """
    A project's dependency with its associated top-level module names. There are stored in the metadata's top_level.txt.
    An example of this is 'matplotlib' with top-levels: ['matplotlib', 'mpl_toolkits', 'pylab'].

    By default, we also add the dependency's name with '-' replaced by '_' to the top-level modules.
    """

    def __init__(self, name: str, conditional: bool = False, optional: bool = False) -> None:
        """
        Args:
            name: Name of the dependency, as shown in pyproject.toml
            conditional: boolean to indicate if the dependency is conditional, e.g. 'importlib-metadata': {'version': '*', 'python': '<=3.7'}
        """
        self.name = name
        self.is_conditional = conditional
        self.is_optional = optional
        self.found = self.find_metadata(name)
        self.top_levels = self._get_top_levels(name)

    def _get_top_levels(self, name: str) -> Set[str]:
        top_levels = []

        if self.found:
            top_levels += self._get_top_level_module_names_from_top_level_txt()
            if not top_levels:
                top_levels += self._get_top_level_module_names_from_record_file()

        top_levels.append(name.replace("-", "_").lower())
        return set(top_levels)

    def __repr__(self) -> str:
        return f"Dependency '{self.name}'"

    def __str__(self) -> str:
        return f"Dependency '{self.name}'{self._string_for_printing()}with top-levels: {self.top_levels}."

    def find_metadata(self, name: str) -> bool:
        try:
            metadata.distribution(name)  # type: ignore[no-untyped-call]
            return True
        except PackageNotFoundError:
            logging.warning(
                f"Warning: Package '{name}'{self._string_for_printing()}not found in current environment. Assuming its"
                f" corresponding module name is '{name.replace('-','_').lower()}'."
            )
            return False

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

    def _get_top_level_module_names_from_top_level_txt(self) -> List[str]:
        """
        top-level.txt is a metadata file added by setuptools that looks as follows:

        610faff656c4cfcbb4a3__mypyc
        _black_version
        black
        blackd
        blib2to3

        This function extracts these names, if a top-level.txt file exists.
        """
        metadata_top_levels = metadata.distribution(self.name).read_text("top_level.txt")  # type: ignore[no-untyped-call]
        if metadata_top_levels:
            return [x for x in metadata_top_levels.split("\n") if len(x) > 0]
        else:
            return []

    def _get_top_level_module_names_from_record_file(self) -> List[str]:
        """
        Get the top-level module names from the RECORD file, whose contents usually look as follows:

            ...
            black/trans.cpython-39-darwin.so,sha256=<HASH>
            black/trans.py,sha256=<HASH>
            blackd/__init__.py,sha256=<HASH>
            blackd/__main__.py,sha256=<HASH>
            ...

        So if no file top-level.txt is provided, we can try and extract top-levels from this file, in this case black and blackd.
        """
        top_levels = []
        try:
            metadata_records = metadata.distribution(self.name).read_text("RECORD")  # type: ignore[no-untyped-call]

            if not metadata_records:
                return []
        except Exception:
            return []

        for line in metadata_records.split("\n"):
            match = re.match("([a-zA-Z0-9-_]+)/", line)
            if match:
                top_levels.append(match.group(1))

        return list(set(top_levels))
