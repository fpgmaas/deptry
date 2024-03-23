from __future__ import annotations

import itertools
import logging
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from deptry.dependency import Dependency
from deptry.dependency_getter.base import DependenciesExtract, DependencyGetter
from deptry.utils import load_pyproject_toml

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence


@dataclass
class PEP621DependencyGetter(DependencyGetter):
    pep621_dev_dependency_groups: tuple[str, ...] = ()
    """
    Class to extract dependencies from a pyproject.toml file in which dependencies are specified according to PEP 621. For example:

        [project]
        ...
        dependencies = [
            "httpx",
            "gidgethub[httpx]>4.0.0",
            "django>2.1; os_name != 'nt'",
            "django>2.0; os_name == 'nt'"
        ]

        [project.optional-dependencies]
        test = [
            "pytest < 5.0.0",
            "pytest-cov[all]"
        ]

    Note that by default both dependencies and optional-dependencies are extracted as regular dependencies, since PEP-621 does not specify
    a recommended way to extract development dependencies. However, if a value is passed for the `pep621_dev_dependency_groups`
    argument, all dependencies from groups in that argument are considered to be development dependencies. e.g. in the example above, when
    `pep621_dev_dependency_groups=(test,)`, both `pytest` and `pytest-cov` are returned as development dependencies.
    """

    def get(self) -> DependenciesExtract:
        dependencies = self._get_dependencies()
        optional_dependencies = self._get_optional_dependencies()

        if self.pep621_dev_dependency_groups:
            self._check_for_invalid_group_names(optional_dependencies)
            dev_dependencies, leftover_optional_dependencies = (
                self._split_development_dependencies_from_optional_dependencies(optional_dependencies)
            )
            dependencies = [*dependencies, *leftover_optional_dependencies]
            return DependenciesExtract(dependencies, dev_dependencies)

        dependencies = [*dependencies, *itertools.chain(*optional_dependencies.values())]
        return DependenciesExtract(dependencies, [])

    def _get_dependencies(self) -> list[Dependency]:
        pyproject_data = load_pyproject_toml(self.config)
        dependency_strings: list[str] = pyproject_data["project"]["dependencies"]
        return self._extract_pep_508_dependencies(dependency_strings, self.package_module_name_map)

    def _get_optional_dependencies(self) -> dict[str, list[Dependency]]:
        pyproject_data = load_pyproject_toml(self.config)

        return {
            group: self._extract_pep_508_dependencies(dependencies, self.package_module_name_map)
            for group, dependencies in pyproject_data["project"].get("optional-dependencies", {}).items()
        }

    def _check_for_invalid_group_names(self, optional_dependencies: dict[str, list[Dependency]]) -> None:
        missing_groups = set(self.pep621_dev_dependency_groups) - set(optional_dependencies.keys())
        if missing_groups:
            logging.warning(
                "Warning: Trying to extract the dependencies from the optional dependency groups %s as development dependencies, "
                "but the following groups were not found: %s",
                list(self.pep621_dev_dependency_groups),
                list(missing_groups),
            )

    def _split_development_dependencies_from_optional_dependencies(
        self, optional_dependencies: dict[str, list[Dependency]]
    ) -> tuple[list[Dependency], list[Dependency]]:
        """
        Split the optional dependencies into optional dependencies and development dependencies based on the `pep621_dev_dependency_groups`
        parameter. Return a tuple with two values: a list of the development dependencies and a list of the remaining 'true' optional dependencies.
        """
        dev_dependencies = list(
            itertools.chain.from_iterable(
                deps for group, deps in optional_dependencies.items() if group in self.pep621_dev_dependency_groups
            )
        )
        regular_dependencies = list(
            itertools.chain.from_iterable(
                deps for group, deps in optional_dependencies.items() if group not in self.pep621_dev_dependency_groups
            )
        )
        return dev_dependencies, regular_dependencies

    def _extract_pep_508_dependencies(
        self, dependencies: list[str], package_module_name_map: Mapping[str, Sequence[str]]
    ) -> list[Dependency]:
        """
        Given a list of dependency specifications (e.g. "django>2.1; os_name != 'nt'"), convert them to Dependency objects.
        """
        extracted_dependencies = []

        for spec in dependencies:
            # An example of a spec is `"tomli>=1.1.0; python_version < \"3.11\""`
            name = self._find_dependency_name_in(spec)
            if name:
                extracted_dependencies.append(
                    Dependency(
                        name,
                        self.config,
                        conditional=self._is_conditional(spec),
                        optional=self._is_optional(spec),
                        module_names=package_module_name_map.get(name),
                    )
                )

        return extracted_dependencies

    @staticmethod
    def _is_optional(dependency_specification: str) -> bool:
        return bool(re.findall(r"\[([a-zA-Z0-9-]+?)\]", dependency_specification))

    @staticmethod
    def _is_conditional(dependency_specification: str) -> bool:
        return ";" in dependency_specification

    @staticmethod
    def _find_dependency_name_in(spec: str) -> str | None:
        match = re.search("[a-zA-Z0-9-_]+", spec)
        if match:
            return match.group(0)
        return None
