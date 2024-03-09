# ruff: noqa

from __future__ import annotations

from deptryrs import get_imports_from_file

try:
    ast = get_imports_from_file("deptry/utils.py")
    print(ast)
except Exception as e:  # It will catch the PyIOError thrown by Rust
    print(type(e))
    print(e)
