import logging
from typing import List

from deptry.utils import import_importlib_metadata

metadata, PackageNotFoundError = import_importlib_metadata()


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

    def _get_top_levels(self, name: str) -> List[str]:
        top_levels = []

        if self.found:
            top_levels += self._get_top_level_module_names_from_metadata()

        top_levels.append(name.replace("-", "_").lower())
        return set(top_levels)

    def __repr__(self) -> str:
        return f"Dependency '{self.name}'"

    def __str__(self) -> str:
        return f"Dependency '{self.name}'{self._string_for_printing()}with top-levels: {self.top_levels}."

    def find_metadata(self, name):
        try:
            metadata.distribution(name)
            return True
        except PackageNotFoundError:
            logging.warning(
                f"Warning: Package '{name}'{self._string_for_printing()}not found in current environment. Assuming its corresponding module name is '{name.replace('-','_').lower()}'."
            )
            return False

    def _string_for_printing(self):
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

    def _get_top_level_module_names_from_metadata(self):
        metadata_top_levels = metadata.distribution(self.name).read_text("top_level.txt")
        if metadata_top_levels:
            return [x for x in metadata_top_levels.split("\n") if len(x) > 0]
        else:
            return []
