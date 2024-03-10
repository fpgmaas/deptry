# ruff: noqa

from __future__ import annotations

from deptry import get_imports_from_py_file

try:
    imports_with_locations = get_imports_from_py_file("tests/data/some_imports.py")
    for k, v in imports_with_locations.items():
        print(k)
        print(v)
except Exception as e:  # It will catch the PyIOError thrown by Rust
    print(type(e))
    print(e)
