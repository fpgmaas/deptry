from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from deptry.imports.location import Location
from deptry.module import ModuleBuilder, ModuleLocations
from deptry.violations import DEP003TransitiveDependenciesFinder
from deptry.violations.dep003_transitive.violation import DEP003TransitiveDependencyViolation


def test_simple() -> None:
    module = ModuleBuilder("foo", set(), frozenset()).build()

    with patch.object(module, "package", return_value="foo"):
        issues = DEP003TransitiveDependenciesFinder(
            [ModuleLocations(module, [Location(Path("foo.py"), 1, 2)])],
            [],
            frozenset(),
        ).find()

    assert issues == [
        DEP003TransitiveDependencyViolation(
            issue=module,
            location=Location(
                file=Path("foo.py"),
                line=1,
                column=2,
            ),
        ),
    ]


def test_simple_with_ignore() -> None:
    module = ModuleBuilder("foo", set(), frozenset()).build()

    with patch.object(module, "package", return_value="foo"):
        issues = DEP003TransitiveDependenciesFinder(
            [ModuleLocations(module, [Location(Path("foo.py"), 1, 2)])],
            [],
            frozenset(),
            ignored_modules=("foo",),
        ).find()

    assert issues == []


def test_simple_with_standard_library() -> None:
    module = ModuleBuilder("foo", set(), standard_library_modules=frozenset(["foo"])).build()

    with patch.object(module, "package", return_value="foo"):
        issues = DEP003TransitiveDependenciesFinder(
            [ModuleLocations(module, [Location(Path("foo.py"), 1, 2)])], [], frozenset()
        ).find()

    assert issues == []
