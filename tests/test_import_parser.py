import logging
from pathlib import Path
from unittest.mock import Mock

from deptry.import_parser import ImportParser
from deptry.utils import run_within_dir


def test_import_parser_py():
    imported_modules = ImportParser().get_imported_modules_from_file(Path("tests/data/some_imports.py"))
    assert set(imported_modules) == {
        "barfoo",
        "baz",
        "click",
        "foobar",
        "httpx",
        "module_in_class",
        "module_in_func",
        "not_click",
        "numpy",
        "os",
        "pandas",
        "pathlib",
        "randomizer",
        "typing",
    }


def test_import_parser_ipynb():
    imported_modules = ImportParser().get_imported_modules_from_file(
        Path("tests/data/example_project/src/notebook.ipynb")
    )
    assert set(imported_modules) == {"click", "urllib3", "toml"}


def test_import_parser_ignores_setuptools(tmp_path):
    with run_within_dir(tmp_path):
        with open("file.py", "w") as f:
            f.write("import setuptools\nimport foo")
        imported_modules = ImportParser().get_imported_modules_for_list_of_files([Path("file.py")])
        assert set(imported_modules) == {"foo"}


def test_import_parser_file_encodings(tmp_path):
    with run_within_dir(tmp_path):
        with open("file1.py", "w", encoding="utf-8") as f:
            f.write(
                """#!/usr/bin/python
# -*- encoding: utf-8 -*-
import foo
print('嘉大')
"""
            )
        with open("file2.py", "w", encoding="iso-8859-15") as f:
            f.write(
                """
#!/usr/bin/python
# -*- encoding: iso-8859-15 -*-
import foo
print('Æ	Ç')
"""
            )
        with open("file3.py", "w", encoding="utf-16") as f:
            f.write(
                """#!/usr/bin/python
# -*- encoding: utf-16 -*-
import foo
print('嘉大')
"""
            )
        with open("file4.py", "w") as f:
            f.write("""my_string = '🐺'\nimport foo""")

        imported_modules = ImportParser().get_imported_modules_from_file(Path("file1.py"))
        assert set(imported_modules) == {"foo"}

        imported_modules = ImportParser().get_imported_modules_from_file(Path("file2.py"))
        assert set(imported_modules) == {"foo"}

        imported_modules = ImportParser().get_imported_modules_from_file(Path("file3.py"))
        assert set(imported_modules) == {"foo"}

        imported_modules = ImportParser().get_imported_modules_from_file(Path("file4.py"))
        assert set(imported_modules) == {"foo"}


def test_import_parser_file_encodings_warning(tmp_path, caplog):
    with run_within_dir(tmp_path):
        with open("file1.py", "w", encoding="utf-8") as f:
            f.write("print('this is a mock unparseable file')")

        mockObject = ImportParser
        mockObject._get_import_modules_from = Mock(
            side_effect=UnicodeDecodeError("fakecodec", b"\x00\x00", 1, 2, "Fake reason!")
        )
        with caplog.at_level(logging.WARNING):
            imported_modules = mockObject().get_imported_modules_from_file(Path("file1.py"))
            assert set(imported_modules) == set()
        assert "Warning: File file1.py could not be decoded. Skipping..." in caplog.text
