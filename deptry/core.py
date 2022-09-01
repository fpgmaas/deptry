import os
from typing import List

from deptry.dependencies_getter import DependenciesGetter
from deptry.import_parser import ImportParser
from deptry.imports_to_package_names import ImportsToPackageNames
from deptry.python_file_finder import PythonFileFinder


class Core:
    def __init__(self, ignore_packages: List[str]):
        self.ignore_packages = ignore_packages

    def run(self):
        all_py_files = PythonFileFinder(include_ipynb=True).get_list_of_python_files()
        imported_modules = ImportParser().get_imported_modules_for_list_of_files(all_py_files)
        imported_packages = ImportsToPackageNames().convert(imported_modules)
        dependencies = DependenciesGetter().get()
        return sorted(list(set(dependencies) - set(self.ignore_packages) - set(imported_packages) - set(["python"])))
