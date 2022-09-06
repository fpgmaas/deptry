from importlib.metadata import PackageNotFoundError
from typing import List, Set

from pathlib import Path
import sys

from isort.stdlibs.py37 import stdlib as stdlib37
from isort.stdlibs.py38 import stdlib as stdlib38
from isort.stdlibs.py39 import stdlib as stdlib39
from isort.stdlibs.py310 import stdlib as stdlib310

from deptry.utils import import_importlib_metadata
from deptry.dependency import Dependency
import logging

metadata = import_importlib_metadata()

class Module:
    
    def __init__(self, module: str, dependencies = List[Dependency]):
        self.module = module
        self.package = self._get_package_name()
    
    def _get_package_name(self, dependencies):
        try:
            self.package = self._extract_package_name_from_metadata()
        except PackageNotFoundError:
            if self._module_in_standard_library():
                pass
            elif self._module_found_in_top_levels:
                logging.info(
                        f"Failed to find metadata for import `{self.module}` in current environment, but it was encountered in a dependency's top-levels."
                    )
            else:
                logging.warning(
                        f"Warning: Failed to find corresponding package name for import `{self.module}` in current environment."
                    )

    def _module_found_in_top_levels(self):
        any([self.module in dependency.top_levels for dependency in self.dependencies])

    def _extract_package_name_from_metadata(self):
        package = metadata.metadata(self.module)["Name"]
        logging.debug(
            f"Corresponding package name for imported module `{self.module}` is `{package}`."
            )
        return package
    
    def _module_in_standard_library(self):
        if self.module in self._get_stdlib_packages():
            logging.debug(f"module `{self.module}` is in the Python standard library.")
            return True
    
    def __repr__(self):
        return f"Module '{self.module}'"
    
    def __str__(self):
        return f"Module '{self.module}' from package {self.package}"

    def _get_stdlib_packages(self) -> Set[str]:
        incorrect_version_error = ValueError(
            f"Incorrect Python version {'.'.join([str(x) for x in sys.version_info[0:3]])}. Only 3.7, 3.8, 3.9 and 3.10 are currently supported."
        )
        if sys.version_info[0] == 3:
            if sys.version_info[1] == 7:
                return stdlib37
            elif sys.version_info[1] == 8:
                return stdlib38
            elif sys.version_info[1] == 9:
                return stdlib39
            elif sys.version_info[1] == 10:
                return stdlib310
            else:
                raise incorrect_version_error
        else:
            raise incorrect_version_error