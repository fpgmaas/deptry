from .rust import Location as RustLocation

def get_imports_from_py_files(file_paths: list[str]) -> dict[str, list[RustLocation]]: ...
def get_imports_from_ipynb_files(file_paths: list[str]) -> dict[str, list[RustLocation]]: ...

class Location:
    file: str
    line: int
    column: int
    def __init__(self, file: str, line: int, column: int) -> None: ...
