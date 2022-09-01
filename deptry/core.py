from typing import List

from deptry.import_parser import ImportParser
from deptry.imports_to_package_names import ImportsToPackageNames
from deptry.obsolete_dependencies_finder import ObsoleteDependenciesFinder
from deptry.python_file_finder import PythonFileFinder


class Core:
    def __init__(self, ignore_dependencies: List[str] = None, ignore_directories: List[str] = None):
        self.ignore_dependencies = ignore_dependencies
        self.ignore_directories = ignore_directories

    def run(self):
        all_py_files = PythonFileFinder(ignore_directories=self.ignore_directories).get_list_of_python_files()
        imported_modules = ImportParser().get_imported_modules_for_list_of_files(all_py_files)
        imported_packages = ImportsToPackageNames().convert(imported_modules)
        obsolete_dependencies = ObsoleteDependenciesFinder(
            imported_packages=imported_packages, ignore_dependencies=self.ignore_dependencies
        ).find()
        return obsolete_dependencies
