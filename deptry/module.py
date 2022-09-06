import logging
import sys
from typing import List, Set

from isort.stdlibs.py37 import stdlib as stdlib37
from isort.stdlibs.py38 import stdlib as stdlib38
from isort.stdlibs.py39 import stdlib as stdlib39
from isort.stdlibs.py310 import stdlib as stdlib310

from deptry.dependency import Dependency
from deptry.utils import import_importlib_metadata

metadata, PackageNotFoundError = import_importlib_metadata()


class Module:
    def __init__(self, name: str, dependencies: List[Dependency] = None) -> None:
        """
        A Module object that represents an imported module. If the metadata field 'Name' is found for a module, it's added as the associated package name.
        Otherwise, check if it is part of the standard library.

        If the metadata is not found and it's not part of the standard library, check if the module is equal to any of the top-level module names
        of any of the installed dependencies. If so, it's not added as the Module's package name (since it's ambiguous, e.g. 'google' is the top-level
        name for both 'google-cloud-bigquery' and 'google-cloud-auth', so which one is the associated package for the module 'google'?) However,
        we do know that this information can be used in detecting obsolete dependencies, so there is no need to raise a warning.

        If nothing is found, a warning is logged to inform the user that there is no information available about this package.
        """
        self.name = name
        self.standard_library = False
        self.package = self._get_package_name(dependencies)

    def _get_package_name(self, dependencies: List[Dependency]) -> str:
        try:
            return self._extract_package_name_from_metadata()
        except PackageNotFoundError:
            if self._module_in_standard_library():
                self.standard_library = True
            elif dependencies and self._module_found_in_top_levels(dependencies):
                logging.debug(
                    f"Failed to find metadata for import `{self.name}` in current environment, but it was encountered in a dependency's top-level module names."
                )
            else:
                logging.warning(
                    f"Warning: Failed to find corresponding package name for import `{self.name}` in current environment."
                )

    def _module_found_in_top_levels(self, dependencies: List[Dependency]) -> bool:
        return any([self.name in dependency.top_levels for dependency in dependencies if dependency.top_levels])

    def _extract_package_name_from_metadata(self) -> str:
        package = metadata.metadata(self.name)["Name"]
        logging.debug(f"Corresponding package name for imported module `{self.name}` is `{package}`.")
        return package

    def _module_in_standard_library(self):
        if self.name in self._get_stdlib_packages():
            logging.debug(f"module `{self.name}` is in the Python standard library.")
            return True

    def __repr__(self) -> str:
        return f"Module '{self.name}'"

    def __str__(self) -> str:
        if self.standard_library:
            return f"Module '{self.name}' from standard library"
        else:
            if self.package:
                return f"Module '{self.name}' from package '{self.package}'"
            else:
                return f"Module '{self.name}' from unknown source"

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
