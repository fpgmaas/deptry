from typing import List
import toml 
from pathlib import Path
import sys

from deptry.utils import import_importlib_metadata

metadata = import_importlib_metadata()

class Dependency:
    
    def __init__(self, dependency: str):
        self.dependency = dependency
        self.top_levels = self._get_top_levels(dependency)
    
    @staticmethod
    def _get_top_levels(dependency: str):
        top_levels = metadata.distribution(dependency).read_text('top_level.txt')
        if top_levels:
            return [x for x in top_levels.split('\n') if len(x)>0]
    
    def __repr__(self):
        return f"Dependency '{self.dependency}'"
    
    def __str__(self):
        return f"Dependency '{self.dependency}' with top-levels: {self.top_levels}"