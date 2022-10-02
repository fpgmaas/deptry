import logging
import os
import sys
from pathlib import Path
from typing import List, Optional, Set

from deptry.compat import PackageNotFoundError, metadata
from deptry.dependency import Dependency


class Module:
    def __init__(
        self,
        name: str,
        standard_library: bool = False,
        local_module: bool = False,
        package: Optional[str] = None,
        top_levels: Optional[List[str]] = None,
        dev_top_levels: Optional[List[str]] = None,
        is_dependency: Optional[bool] = None,
        is_dev_dependency: Optional[bool] = None,
    ) -> None:
        self.name = name
        self.standard_library = standard_library
        self.local_module = local_module
        self.package = package
        self.top_levels = top_levels
        self.dev_top_levels = dev_top_levels
        self.is_dependency = is_dependency
        self.is_dev_dependency = is_dev_dependency
        self._log()

    def _log(self) -> None:
        logging.debug("--- MODULE ---")
        logging.debug(self.__str__())
        logging.debug("")

    def __repr__(self) -> str:
        return f"Module '{self.name}'"

    def __str__(self) -> str:
        return "\n".join("%s: %s" % item for item in vars(self).items())


class ModuleBuilder:
    def __init__(
        self,
        name: str,
        dependencies: Optional[List[Dependency]] = None,
        dev_dependencies: Optional[List[Dependency]] = None,
    ) -> None:
        """
        Create a Module object that represents an imported module.

        Args:
            name: The name of the imported module
            dependencies: A list of the project's dependencies
            dev-dependencies: A list of the project's development dependencies
        """
        self.name = name
        self.dependencies = dependencies or []
        self.dev_dependencies = dev_dependencies or []

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

    def _get_package_name_from_metadata(self) -> Optional[str]:
        """
        Most packages simply have a field called "Name" in their metadata. This method extracts that field.
        """
        try:
            name: str = metadata.metadata(self.name)["Name"]  # type: ignore[no-untyped-call]
            return name
        except PackageNotFoundError:
            return None

    def _get_corresponding_top_levels_from(self, dependencies: List[Dependency]) -> List[str]:
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

    def _in_standard_library(self) -> bool:
        return self.name in self._get_stdlib_packages()

    @staticmethod
    def _get_stdlib_packages() -> Set[str]:
        if sys.version_info[:2] == (3, 7):
            from deptry.stdlibs.py37 import stdlib
        elif sys.version_info[:2] == (3, 8):
            from deptry.stdlibs.py38 import stdlib
        elif sys.version_info[:2] == (3, 9):
            from deptry.stdlibs.py39 import stdlib
        elif sys.version_info[:2] == (3, 10):
            from deptry.stdlibs.py310 import stdlib
        elif sys.version_info[:2] == (3, 11):
            from deptry.stdlibs.py311 import stdlib
        else:
            raise ValueError(
                f"Python version {'.'.join([str(x) for x in sys.version_info[0:3]])} is not supported. Only 3.7, 3.8,"
                " 3.9, 3.10 and 3.11 are currently supported."
            )

        return stdlib

    def _is_local_directory(self) -> bool:
        """
        Check if the module is a local directory with an __init__.py file.
        """
        directories = [f for f in os.listdir() if Path(f).is_dir()]
        local_modules = [subdir for subdir in directories if "__init__.py" in os.listdir(subdir)]
        return self.name in local_modules

    def _has_matching_dependency(self, package: Optional[str], top_levels: List[str]) -> bool:
        """
        Check if this module is provided by a listed dependency. This is the case if either the package name that was found in the metadata is
        listed as a dependency, or if the we found a top-level module name match earlier.
        """
        return package and (package in [dep.name for dep in self.dependencies]) or len(top_levels) > 0

    def _has_matching_dev_dependency(self, package: Optional[str], dev_top_levels: List[str]) -> bool:
        """
        Same as _has_matching_dependency, but for development dependencies.
        """
        return package and (package in [dep.name for dep in self.dev_dependencies]) or len(dev_top_levels) > 0
