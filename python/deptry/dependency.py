from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from deptry.distribution import get_packages_from_distribution

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path


class Dependency:
    """
    A project's dependency with its associated top-level module names. There are stored in the metadata's top_level.txt.
    An example of this is 'matplotlib' with top-levels: ['matplotlib', 'mpl_toolkits', 'pylab'].

    Attributes:
        name (str): The name of the dependency.
        definition_file (Path): The path to the file defining the dependency, e.g. 'pyproject.toml'.
          and that can be used to create a variant of the package with a set of extra functionalities.
        top_levels (set[str]): The top-level module names associated with the dependency.
    """

    def __init__(
        self,
        name: str,
        definition_file: Path,
        module_names: Sequence[str] | None = None,
    ) -> None:
        self.name = name
        self.definition_file = definition_file
        self.top_levels = self._get_top_levels(name, module_names)

    def _get_top_levels(self, name: str, module_names: Sequence[str] | None) -> set[str]:
        """
        Get the top-level module names for a dependency. They are searched for in the following order:
                1. If `module_names` is defined, simply use those as the top-level modules.
                2. Otherwise, try to extract the top-level module names from the metadata.
                3. If metadata extraction fails, fall back to the dependency's name, where `-` is replaced with `_`.

        Args:
            name: The name of the dependency.
            module_names: If this is given, use these as the top-level modules instead of
                searching for them in the metadata.
        """
        if module_names is not None:
            return set(module_names)

        if distributions := get_packages_from_distribution(self.name):
            return distributions

        # No metadata or other configuration has been found. As a fallback we'll guess the name.
        module_name = name.replace("-", "_").lower()
        logging.warning(
            "Assuming the corresponding module name of package %r is %r. Install the package or configure a"
            " package_module_name_map entry to override this behaviour.",
            self.name,
            module_name,
        )
        return {module_name}

    def __repr__(self) -> str:
        return f"Dependency '{self.name}'"

    def __str__(self) -> str:
        return f"Dependency '{self.name}' with top-levels: {self.top_levels}."
