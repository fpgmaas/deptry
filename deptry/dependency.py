import sys
from pathlib import Path
from typing import List

import toml

from deptry.utils import import_importlib_metadata

metadata = import_importlib_metadata()


class Dependency:
    def __init__(self, name: str):
        self.name = name
        self.top_levels = self._get_top_levels(name)

    @staticmethod
    def _get_top_levels(name: str):
        top_levels = metadata.distribution(name).read_text("top_level.txt")
        if top_levels:
            return [x for x in top_levels.split("\n") if len(x) > 0]

    def __repr__(self):
        return f"Dependency '{self.name}'"

    def __str__(self):
        return f"Dependency '{self.name}' with top-levels: {self.top_levels}"
