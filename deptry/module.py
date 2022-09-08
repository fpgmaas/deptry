import logging
import os
import sys
from pathlib import Path
from typing import List, Set

from isort.stdlibs.py37 import stdlib as stdlib37
from isort.stdlibs.py38 import stdlib as stdlib38
from isort.stdlibs.py39 import stdlib as stdlib39
from isort.stdlibs.py310 import stdlib as stdlib310

from deptry.dependency import Dependency
from deptry.utils import import_importlib_metadata

metadata, PackageNotFoundError = import_importlib_metadata()


class Module:
    def __init__(
        self,
        name: str,
        standard_library: bool = False,
        local_module: bool = False,
        package: str = None,
        top_levels: List[str] = None,
        dev_top_levels: List[str] = None,
        dependency: bool = None,
        dev_dependency: bool = None,
    ):
        self.name = name
        self.standard_library = standard_library
        self.local_module = local_module
        self.package = package
        self.top_levels = top_levels
        self.dev_top_levels = dev_top_levels
        self.dependency = dependency
        self.dev_dependency = dev_dependency
        self._log()

    def _log(self):
        logging.debug("--- MODULE ---")
        logging.debug(self.__str__())
        logging.debug("")

    def __repr__(self) -> str:
        return f"Module '{self.name}'"

    def __str__(self) -> str:
        return "\n".join("%s: %s" % item for item in vars(self).items())


class ModuleBuilder:
    def __init__(self, name: str, dependencies: List[Dependency] = [], dev_dependencies: List[Dependency] = []) -> None:
        """
        A Module object that represents an imported module. If the metadata field 'Name' is found for a module, it's added as the associated package name.
        Otherwise, check if it is part of the standard library.

        If the metadata is not found and it's not part of the standard library, check if the module is equal to any of the top-level module names
        of any of the installed dependencies. If so, it's not added as the Module's package name (since it's ambiguous, e.g. 'google' is the top-level
        name for both 'google-cloud-bigquery' and 'google-cloud-auth', so which one is the associated package for the module 'google'?) However,
        we do know that this information can be used in detecting obsolete dependencies, so there is no need to raise a warning.

        If nothing is found, a warning is logged to inform the user that there is no information available about this package.
        TODO: Move name arg to build func
        """
        self.name = name
        self.dependencies = dependencies
        self.dev_dependencies = dev_dependencies

    def build(self) -> Module:

        standard_library = self._in_standard_library()
        if standard_library:
            return Module(self.name, standard_library=True)
        else:
            local_module = self._is_local_directory()
            if local_module:
                return Module(self.name, local_module=True)
            else:
                package = self._get_package_name()
                top_levels = self._get_corresponding_top_levels(self.dependencies)
                dev_top_levels = self._get_corresponding_top_levels(self.dev_dependencies)
                dependency = self._has_matching_dependency(package, top_levels)
                dev_dependency = self._has_matching_dev_dependency(package, dev_top_levels)
                return Module(
                    self.name,
                    package=package,
                    top_levels=top_levels,
                    dev_top_levels=dev_top_levels,
                    dependency=dependency,
                    dev_dependency=dev_dependency,
                )

    def _get_package_name(self) -> str:
        try:
            return self._extract_package_name_from_metadata()
        except PackageNotFoundError:
            pass

    def _get_corresponding_top_levels(self, dependencies: List[Dependency]) -> bool:
        return [
            dependency.name
            for dependency in dependencies
            if dependency.top_levels and self.name in dependency.top_levels
        ]

    def _extract_package_name_from_metadata(self) -> str:
        package = metadata.metadata(self.name)["Name"]
        return package

    def _in_standard_library(self):
        if self.name in self._get_stdlib_packages():
            return True

    def _get_stdlib_packages(self) -> Set[str]:
        incorrect_version_error = ValueError(
            f"Incorrect Python version {'.'.join([str(x) for x in sys.version_info[0:3]])}. Only 3.7, 3.8, 3.9 and 3.10 are currently supported."
        )
        if sys.version_info[0] == 3:
            if sys.version_info[1] == 7:
                stdlib = stdlib37
            elif sys.version_info[1] == 8:
                stdlib = stdlib38
            elif sys.version_info[1] == 9:
                stdlib = stdlib39
            elif sys.version_info[1] == 10:
                stdlib = stdlib310
            else:
                raise incorrect_version_error
            stdlib.add("__future__")
            return stdlib
        else:
            raise incorrect_version_error

    def _is_local_directory(self):
        directories = [f for f in os.listdir() if Path(f).is_dir()]
        local_modules = [subdir for subdir in directories if "__init__.py" in os.listdir(subdir)]
        return self.name in local_modules

    def _has_matching_dependency(self, package, top_levels):
        return (package in [dep.name for dep in self.dependencies]) or len(top_levels) > 0

    def _has_matching_dev_dependency(self, package, dev_top_levels):
        return (package in [dep.name for dep in self.dev_dependencies]) or len(dev_top_levels) > 0
