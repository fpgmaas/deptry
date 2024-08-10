from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from deptry.dependency import Dependency
from deptry.dependency_getter.base import DependenciesExtract, DependencyGetter
from deptry.utils import load_pyproject_toml


@dataclass
class PEP621DependencyGetter(DependencyGetter):
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

    pep621_dev_dependency_groups: tuple[str, ...] = ()

    def get(self) -> DependenciesExtract:
        dependencies = self._get_dependencies()
        optional_dependencies = self._get_optional_dependencies()

        dev_dependencies_from_optional, remaining_optional_dependencies = (
            self._split_development_dependencies_from_optional_dependencies(optional_dependencies)
        )
        return DependenciesExtract(
            [*dependencies, *remaining_optional_dependencies],
            self._get_dev_dependencies(dev_dependencies_from_optional),
        )

    def _get_dependencies(self) -> list[Dependency]:
        pyproject_data = load_pyproject_toml(self.config)
        dependency_strings: list[str] = pyproject_data["project"].get("dependencies", [])
        return self._extract_pep_508_dependencies(dependency_strings)

    def _get_optional_dependencies(self) -> dict[str, list[Dependency]]:
        pyproject_data = load_pyproject_toml(self.config)

        return {
            group: self._extract_pep_508_dependencies(dependencies)
            for group, dependencies in pyproject_data["project"].get("optional-dependencies", {}).items()
        }

    def _get_dev_dependencies(self, dev_dependencies_from_optional: list[Dependency]) -> list[Dependency]:
        return dev_dependencies_from_optional

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
        dev_dependencies: list[Dependency] = []
        regular_dependencies: list[Dependency] = []

        if self.pep621_dev_dependency_groups:
            self._check_for_invalid_group_names(optional_dependencies)

        for group, dependencies in optional_dependencies.items():
            if group in self.pep621_dev_dependency_groups:
                dev_dependencies.extend(dependencies)
            else:
                regular_dependencies.extend(dependencies)

        return dev_dependencies, regular_dependencies

    def _extract_pep_508_dependencies(self, dependencies: list[str]) -> list[Dependency]:
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
                        module_names=self.package_module_name_map.get(name),
                    )
                )

        return extracted_dependencies

    @staticmethod
    def _find_dependency_name_in(spec: str) -> str | None:
        match = re.search("[a-zA-Z0-9-_]+", spec)
        if match:
            return match.group(0)
        return None
