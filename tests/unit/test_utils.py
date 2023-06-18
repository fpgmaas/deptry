from __future__ import annotations

from pathlib import Path

from deptry.utils import load_pyproject_toml


def test_load_pyproject_toml() -> None:
    assert load_pyproject_toml(Path("tests/data/example_project/pyproject.toml")) == {
        "tool": {
            "deptry": {"per_rule_ignores": {"DEP002": ["pkginfo"]}},
            "poetry": {
                "authors": ["test <test@test.com>"],
                "dependencies": {
                    "click": "^8.1.3",
                    "isort": "^5.10.1",
                    "pkginfo": "^1.8.3",
                    "python": ">=3.7,<4.0",
                    "requests": "^2.28.1",
                    "toml": "^0.10.2",
                    "urllib3": "^1.26.12",
                },
                "description": "A test project",
                "dev-dependencies": {"black": "^22.6.0"},
                "name": "test",
                "version": "0.0.1",
            },
        }
    }
