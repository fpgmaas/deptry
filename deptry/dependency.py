import logging
from typing import List

from deptry.utils import import_importlib_metadata

metadata, PackageNotFoundError = import_importlib_metadata()


class Dependency:
    """
    A project's dependency with it's associated top-level module names. There are stored in the metadata's top_level.txt.
    An example of this is 'matplotlib' with top-levels: ['matplotlib', 'mpl_toolkits', 'pylab'].
    """

    def __init__(self, name: str) -> None:
        self.name = name
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
        return f"Dependency '{self.name}' with top-levels: {self.top_levels}"
