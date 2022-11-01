import itertools
import re
from dataclasses import dataclass
from typing import Dict, List, Optional

from deptry.dependency import Dependency
from deptry.dependency_getter.base import DependenciesExtract, DependencyGetter
from deptry.utils import load_pyproject_toml


@dataclass
class PEP621DependencyGetter(DependencyGetter):
    def get(self) -> DependenciesExtract:
        dependencies = [*self._get_dependencies(), *itertools.chain(*self._get_optional_dependencies().values())]
        self._log_dependencies(dependencies)

        return DependenciesExtract(dependencies, [])

    @classmethod
    def _get_dependencies(cls) -> List[Dependency]:
        pyproject_data = load_pyproject_toml()
        dependency_strings: List[str] = pyproject_data["project"]["dependencies"]
        return cls._extract_pep_508_dependencies(dependency_strings)

    @classmethod
    def _get_optional_dependencies(cls) -> Dict[str, List[Dependency]]:
        pyproject_data = load_pyproject_toml()

        return {
            group: cls._extract_pep_508_dependencies(dependencies)
            for group, dependencies in pyproject_data["project"].get("optional-dependencies", {}).items()
        }

    @classmethod
    def _extract_pep_508_dependencies(cls, dependencies: List[str]) -> List[Dependency]:
        extracted_dependencies = []

        for spec in dependencies:
            # An example of a spec is `"tomli>=1.1.0; python_version < \"3.11\""`
            name = cls._find_dependency_name_in(spec)
            if name:
                extracted_dependencies.append(
                    Dependency(name, conditional=cls._is_conditional(spec), optional=cls._is_optional(spec))
                )

        return extracted_dependencies

    @staticmethod
    def _is_optional(dependency_specification: str) -> bool:
        return bool(re.findall(r"\[([a-zA-Z0-9-]+?)\]", dependency_specification))

    @staticmethod
    def _is_conditional(dependency_specification: str) -> bool:
        return ";" in dependency_specification

    @staticmethod
    def _find_dependency_name_in(spec: str) -> Optional[str]:
        match = re.search("[a-zA-Z0-9-_]+", spec)
        if match:
            return match.group(0)
        return None
