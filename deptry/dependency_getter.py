from typing import List
from pathlib import Path
from deptry.dependency import Dependency
import toml

class DependencyGetter:
    
    def __init__(self) -> None:
        pass
    
    def get(self):
        pyproject_toml_dependencies = self._get_pyproject_toml_dependencies()
        dependencies = []
        for dep in pyproject_toml_dependencies:
            if not dep == 'python':
                dependencies.append(Dependency(dep))
        return dependencies

    def _get_pyproject_toml_dependencies(self) -> List[str]:
        pyproject_text = Path("./pyproject.toml").read_text()
        pyproject_data = toml.loads(pyproject_text)
        dependencies = list(pyproject_data["tool"]["poetry"]["dependencies"].keys())
        return sorted(dependencies)