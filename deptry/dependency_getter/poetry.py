import contextlib
from dataclasses import dataclass
from typing import Any, Dict, List, Union

from deptry.dependency import Dependency
from deptry.dependency_getter.base import DependenciesExtract, DependencyGetter
from deptry.utils import load_pyproject_toml


@dataclass
class PoetryDependencyGetter(DependencyGetter):
    """Extract Poetry dependencies from pyproject.toml."""

    def get(self) -> DependenciesExtract:
        dependencies = self._get_poetry_dependencies()
        self._log_dependencies(dependencies)

        dev_dependencies = self._get_poetry_dev_dependencies()
        self._log_dependencies(dev_dependencies, is_dev=True)

        return DependenciesExtract(dependencies, dev_dependencies)

    @classmethod
    def _get_poetry_dependencies(cls) -> List[Dependency]:
        pyproject_data = load_pyproject_toml()
        dependencies: Dict[str, Any] = pyproject_data["tool"]["poetry"]["dependencies"]
        return cls._get_dependencies(dependencies)

    @classmethod
    def _get_poetry_dev_dependencies(cls) -> List[Dependency]:
        """
        These can be either under;

        [tool.poetry.dev-dependencies]
        [tool.poetry.group.dev.dependencies]

        or both.
        """
        dependencies: Dict[str, str] = {}
        pyproject_data = load_pyproject_toml()

        with contextlib.suppress(KeyError):
            dependencies = {**pyproject_data["tool"]["poetry"]["dev-dependencies"], **dependencies}

        with contextlib.suppress(KeyError):
            dependencies = {**pyproject_data["tool"]["poetry"]["group"]["dev"]["dependencies"], **dependencies}

        return cls._get_dependencies(dependencies)

    @classmethod
    def _get_dependencies(cls, poetry_dependencies: Dict[str, Any]) -> List[Dependency]:
        dependencies = []
        for dep, spec in poetry_dependencies.items():
            # dep is the dependency name, spec is the version specification, e.g. "^0.2.2" or {"*", optional = true}
            if dep != "python":
                optional = cls._is_optional(spec)
                conditional = cls._is_conditional(spec)
                dependencies.append(Dependency(dep, conditional=conditional, optional=optional))

        return dependencies

    @staticmethod
    def _is_optional(spec: Union[str, Dict[str, Any]]) -> bool:
        # if of the shape `isodate = {version = "*", optional = true}` mark as optional`
        return bool(isinstance(spec, dict) and spec.get("optional"))

    @staticmethod
    def _is_conditional(spec: Union[str, Dict[str, Any]]) -> bool:
        # if of the shape `tomli = { version = "^2.0.1", python = "<3.11" }`, mark as conditional.
        return isinstance(spec, dict) and "python" in spec and "version" in spec
