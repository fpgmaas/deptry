from __future__ import annotations

import logging
import sys
from dataclasses import dataclass

from deptry.compat import PackageNotFoundError, metadata
from deptry.dependency import Dependency


@dataclass
class Module:
    name: str
    standard_library: bool = False
    local_module: bool = False
    package: str | None = None
    top_levels: list[str] | None = None
    dev_top_levels: list[str] | None = None
    is_dependency: bool | None = None
    is_dev_dependency: bool | None = None

    def __post_init__(self) -> None:
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
        local_modules: set[str],
        dependencies: list[Dependency] | None = None,
        dev_dependencies: list[Dependency] | None = None,
    ) -> None:
        """
        Create a Module object that represents an imported module.

        Args:
            name: The name of the imported module
            dependencies: A list of the project's dependencies
            dev-dependencies: A list of the project's development dependencies
        """
        self.name = name
        self.local_modules = local_modules
        self.dependencies = dependencies or []
        self.dev_dependencies = dev_dependencies or []

    def build(self) -> Module:
        """
        Build the Module object. First check if the module is in the standard library or if it's a local module,
        in that case many checks can be omitted.
        """

        if self._in_standard_library():
            return Module(self.name, standard_library=True)

        if self._is_local_module():
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

    def _get_package_name_from_metadata(self) -> str | None:
        """
        Most packages simply have a field called "Name" in their metadata. This method extracts that field.
        """
        try:
            name: str = metadata.metadata(self.name)["Name"]  # type: ignore[no-untyped-call]
            return name
        except PackageNotFoundError:
            return None

    def _get_corresponding_top_levels_from(self, dependencies: list[Dependency]) -> list[str]:
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
    def _get_stdlib_packages() -> set[str]:
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

    def _is_local_module(self) -> bool:
        """
        Check if the module is a local directory with an __init__.py file.
        """
        return self.name in self.local_modules

    def _has_matching_dependency(self, package: str | None, top_levels: list[str]) -> bool:
        """
        Check if this module is provided by a listed dependency. This is the case if either the package name that was found in the metadata is
        listed as a dependency, or if the we found a top-level module name match earlier.
        """
        return package and (package in [dep.name for dep in self.dependencies]) or len(top_levels) > 0

    def _has_matching_dev_dependency(self, package: str | None, dev_top_levels: list[str]) -> bool:
        """
        Same as _has_matching_dependency, but for development dependencies.
        """
        return package and (package in [dep.name for dep in self.dev_dependencies]) or len(dev_top_levels) > 0
