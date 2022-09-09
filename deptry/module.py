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
        is_dependency: bool = None,
        is_dev_dependency: bool = None,
    ):
        self.name = name
        self.standard_library = standard_library
        self.local_module = local_module
        self.package = package
        self.top_levels = top_levels
        self.dev_top_levels = dev_top_levels
        self.is_dependency = is_dependency
        self.is_dev_dependency = is_dev_dependency
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
        Create a Module object that represents an imported module.

        Args:
            name: The name of the imported module
            dependencies: A list of the project's dependencies
            dependencies: A list of the project's development dependencies
        """
        self.name = name
        self.dependencies = dependencies
        self.dev_dependencies = dev_dependencies

    def build(self) -> Module:
        """
        Build the Module object. First check if the module is in the standard library or if it's a local module,
        in that case many checks can be omitted.
        """

        standard_library = self._in_standard_library()
        if standard_library:
            return Module(self.name, standard_library=True)

        local_module = self._is_local_directory()
        if local_module:
            return Module(self.name, local_module=True)

        package = self._get_package_name_from_metadata()
        top_levels = self._get_corresponding_top_levels_from(self.dependencies)
        dev_top_levels = self._get_corresponding_top_levels_from(self.dev_dependencies)

        is_dependency = self._has_matching_dependency(package, top_levels)
        is_dev_dependency = self._has_matching_dev_dependency(package, dev_top_levels)
        return Module(
            self.name,
            package=package,
            top_levels=top_levels,
            dev_top_levels=dev_top_levels,
            is_dependency=is_dependency,
            is_dev_dependency=is_dev_dependency,
        )

    def _get_package_name_from_metadata(self) -> str:
        """
        Most packages simply have a field called "Name" in their metadata. This method extracts that field.
        """
        try:
            return metadata.metadata(self.name)["Name"]
        except PackageNotFoundError:
            pass

    def _get_corresponding_top_levels_from(self, dependencies: List[Dependency]) -> bool:
        """
        Not all modules have associated metadata. e.g. `mpl_toolkits` from `matplotlib` has no metadata. However, it is in the
        top-level module names of package matplotlib. This function extracts all dependencies which have this module in their top-level module names.
        This can be multiple. e.g. `google-cloud-api` and `google-cloud-bigquery` both have `google` in their top-level module names.
        """
        return [
            dependency.name
            for dependency in dependencies
            if dependency.top_levels and self.name in dependency.top_levels
        ]

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
            stdlib.add("__future__")  # Not sure why this is omitted explicitly in isort's source code.
            return stdlib
        else:
            raise incorrect_version_error

    def _is_local_directory(self):
        """
        Check if the module is a local directory with an __init__.py file.
        """
        directories = [f for f in os.listdir() if Path(f).is_dir()]
        local_modules = [subdir for subdir in directories if "__init__.py" in os.listdir(subdir)]
        return self.name in local_modules

    def _has_matching_dependency(self, package, top_levels):
        """
        Check if this module is provided by a listed dependency. This is the case if either the package name that was found in the metadata is
        listed as a dependency, or if the we found a top-level module name match earlier.
        """
        return (package in [dep.name for dep in self.dependencies]) or len(top_levels) > 0

    def _has_matching_dev_dependency(self, package, dev_top_levels):
        """
        Same as _has_matching_dependency, but for development dependencies.
        """
        return (package in [dep.name for dep in self.dev_dependencies]) or len(dev_top_levels) > 0
