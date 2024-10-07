from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from deptry.distribution import get_distributions_from_package

if TYPE_CHECKING:
    from deptry.dependency import Dependency
    from deptry.imports.location import Location


@dataclass
class Module:
    """
    Represents an imported module and its properties.

    Attributes:
        name: The name of the imported module.
        standard_library: Whether the module is part of the Python standard library.
        local_module: Whether the module is a local module.
        packages: The names of the packages that contain the module.
        top_levels: A list of dependencies that contain this module in their top-level module
            names. This can be multiple, e.g. `google-cloud-api` and `google-cloud-bigquery` both have
            `google` in their top-level module names.
        dev_top_levels: A list of development dependencies that contain this module in their
            top-level module names. Can be multiple, similar to the attribute `top_levels`.
        is_provided_by_dependency: Whether the module is provided by a listed dependency.
        is_provided_by_dev_dependency: Whether the module is provided by a listed development dependency.
    """

    name: str
    standard_library: bool = False
    local_module: bool = False
    packages: list[str] | None = None
    top_levels: list[str] | None = None
    dev_top_levels: list[str] | None = None
    is_provided_by_dependency: bool | None = None
    is_provided_by_dev_dependency: bool | None = None

    def __post_init__(self) -> None:
        self._log()

    def _log(self) -> None:
        logging.debug("--- MODULE ---")
        logging.debug(self.__str__())
        logging.debug("")

    def __repr__(self) -> str:
        return f"Module '{self.name}'"

    def __str__(self) -> str:
        return "\n".join("{}: {}".format(*item) for item in vars(self).items())


@dataclass
class ModuleLocations:
    module: Module
    locations: list[Location] = field(default_factory=list)


class ModuleBuilder:
    def __init__(
        self,
        name: str,
        local_modules: set[str],
        standard_library_modules: frozenset[str],
        dependencies: list[Dependency] | None = None,
        dev_dependencies: list[Dependency] | None = None,
    ) -> None:
        """
        Create a Module object that represents an imported module.

        Args:
            name: The name of the imported module
            local_modules: The list of local modules
            standard_library_modules: The list of Python stdlib modules
            dependencies: A list of the project's dependencies
            dev_dependencies: A list of the project's development dependencies
        """
        self.name = name
        self.local_modules = local_modules
        self.standard_library_modules = standard_library_modules
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

        packages = self._get_package_names_from_metadata()
        top_levels = self._get_corresponding_top_levels_from(self.dependencies)
        dev_top_levels = self._get_corresponding_top_levels_from(self.dev_dependencies)

        is_provided_by_dependency = self._has_matching_dependency(packages, top_levels)
        is_provided_by_dev_dependency = self._has_matching_dev_dependency(packages, dev_top_levels)

        return Module(
            self.name,
            packages=packages,
            top_levels=top_levels,
            dev_top_levels=dev_top_levels,
            is_provided_by_dependency=is_provided_by_dependency,
            is_provided_by_dev_dependency=is_provided_by_dev_dependency,
        )

    def _get_package_names_from_metadata(self) -> list[str] | None:
        if distributions := get_distributions_from_package(self.name):
            return list(distributions)
        return None

    def _get_corresponding_top_levels_from(self, dependencies: list[Dependency]) -> list[str]:
        """
        Not all modules have associated metadata. e.g. `mpl_toolkits` from `matplotlib` has no metadata. However, it is
        in the top-level module names of package matplotlib. This function extracts all dependencies which have this
        module in their top-level module names.
        This can be multiple, e.g. `google-cloud-api` and `google-cloud-bigquery` both have `google` in their top-level
        module names.
        """
        return [
            dependency.name
            for dependency in dependencies
            if dependency.top_levels and self.name in dependency.top_levels
        ]

    def _in_standard_library(self) -> bool:
        return self.name in self.standard_library_modules

    def _is_local_module(self) -> bool:
        """
        Check if the module is a local directory with an __init__.py file.
        """
        return self.name in self.local_modules

    def _has_matching_dependency(self, packages: list[str] | None, top_levels: list[str]) -> bool:
        """
        Check if this module is provided by a listed dependency. This is the case if either the package name that was
        found in the metadata is listed as a dependency, or if we found a top-level module name match earlier.
        """
        if len(top_levels) > 0:
            return True

        if packages:
            for dep in self.dependencies:
                for package in packages:
                    if dep.name == package:
                        return True

        return False

    def _has_matching_dev_dependency(self, packages: list[str] | None, dev_top_levels: list[str]) -> bool:
        """
        Same as _has_matching_dependency, but for development dependencies.
        """
        if len(dev_top_levels) > 0:
            return True

        if packages:
            for dep in self.dev_dependencies:
                for package in packages:
                    if dep.name == package:
                        return True

        return False
