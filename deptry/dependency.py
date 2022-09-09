import logging
from typing import List

from deptry.utils import import_importlib_metadata

metadata, PackageNotFoundError = import_importlib_metadata()


class Dependency:
    """
    A project's dependency with its associated top-level module names. There are stored in the metadata's top_level.txt.
    An example of this is 'matplotlib' with top-levels: ['matplotlib', 'mpl_toolkits', 'pylab'].
    """

    def __init__(self, name: str, conditional: bool = False) -> None:
        """
        Args:
            name: Name of the dependency, as shown in pyproject.toml
            conditional: boolean to indicate if the dependency is conditional, e.g. 'importlib-metadata': {'version': '*', 'python': '<=3.7'}
        """
        self.name = name
        self.conditional = conditional
        self.top_levels = self._get_top_levels(name)

    @staticmethod
    def _get_top_levels(name: str) -> List[str]:
        try:
            top_levels = metadata.distribution(name).read_text("top_level.txt")
            if top_levels:
                return [x for x in top_levels.split("\n") if len(x) > 0]
        except PackageNotFoundError:
            logging.warning(f"Warning: Package '{name}' not found in current environment.")
            return None

    def __repr__(self) -> str:
        return f"Dependency '{self.name}'"

    def __str__(self) -> str:
        return (
            f"{'Conditional d' if self.conditional else 'D'}ependency '{self.name}' with top-levels: {self.top_levels}."
        )
