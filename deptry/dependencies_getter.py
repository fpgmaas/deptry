from pathlib import Path

import toml


class DependenciesGetter:
    def __init__(self):
        pass

    def get(self):
        pyproject_text = Path("./pyproject.toml").read_text()
        pyproject_data = toml.loads(pyproject_text)
        dependencies = list(pyproject_data["tool"]["poetry"]["dependencies"].keys())
        return dependencies
