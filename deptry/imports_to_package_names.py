import logging
import sys
from importlib.metadata import metadata
from typing import List, Set

from isort.stdlibs.py37 import stdlib as stdlib37
from isort.stdlibs.py38 import stdlib as stdlib38
from isort.stdlibs.py39 import stdlib as stdlib39
from isort.stdlibs.py310 import stdlib as stdlib310

COMMON_PACKAGES_WITHOUT_METADATA = {"bs4": "beautifulsoup4", "dotenv": "python-dotenv"}


class ImportsToPackageNames:
    """
    For a list of imported modules, find for each module (e.g. python_dateutil) the corresponding package
    name used to install it (e.g. python-dateutil) and return those names as a list.

    There are three reasons that can cause the corresponding package name not to be found:
    - The package is in the Python standard library. In this case, nothing is added to the output list.
    - The package lacks metadata. In this case, a warning is raised.
    - The package is not installed.
    """

    def __init__(self) -> None:
        pass

    def convert(self, imported_modules: List[str]) -> List[str]:
        packages = []
        for module in imported_modules:
            try:
                packages.append(metadata(module)["Name"])
                logging.debug(
                    f"Corresponding package name for imported module `{module}` is `{metadata(module)['Name']}`."
                )
            except:  # noqa
                if module in self._get_stdlib_packages():
                    logging.debug(f"module `{module}` is in the Python standard library.")
                elif module in COMMON_PACKAGES_WITHOUT_METADATA.keys():
                    packages.append(COMMON_PACKAGES_WITHOUT_METADATA[module])
                else:
                    logging.warning(
                        f"Warning: Failed to find corresponding package name for import `{module}` in current environment."
                    )

        if len(packages) == 0:
            logging.warning(
                "Warning: No metadata was found for any of the imported modules. This can simply be because the package only uses the Python standard library,"
            )
            logging.warning(
                "but this can also be caused by the environment not being installed, found, or activated. Run `deptry` with the `-v` flag for more details."
            )
        logging.debug("\n")

        return packages

    def _get_stdlib_packages(self) -> Set[str]:
        incorrect_version_error = ValueError(
            f"Incorrect Python version {'.'.join([str(x) for x in sys.version_info[0:3]])}. Only 3.7, 3.8, 3.9 and 3.10 are currently supported."
        )
        if sys.version_info[0] == 3:
            if sys.version_info[1] == 7:
                return stdlib37
            elif sys.version_info[1] == 8:
                return stdlib38
            elif sys.version_info[1] == 9:
                return stdlib39
            elif sys.version_info[1] == 10:
                return stdlib310
            else:
                raise incorrect_version_error
        else:
            raise incorrect_version_error
