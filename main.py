# ruff: noqa

from __future__ import annotations

from deptryrs import get_imports_from_file

try:
    imports_with_locations = get_imports_from_file("deptry/utils.py")
    for k, v in imports_with_locations.items():
        print(k)
        print(v)
        print(v[0].line + 1)
except Exception as e:  # It will catch the PyIOError thrown by Rust
    print(type(e))
    print(e)
