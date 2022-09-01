import logging
from importlib.metadata import metadata
from typing import List

from isort.stdlibs.py39 import stdlib


class ImportsToPackageNames:
    """
    For a list of imported modules, convert for each module (e.g. python_dateutil) the corresponding package
    name used to install it (e.g. python-dateutil)

    TODO: Add stdlib for 3.7, 3.8 and 3.10. 3.10 has a built-in method for this.
    """

    def __init__(self):
        pass

    def convert(self, imported_modules: List[str]):
        packages = []
        for module in imported_modules:
            try:
                packages.append(metadata(module)["Name"])
                logging.debug(f"imported module {module}'s corresponding package name is {metadata(module)['Name']}.")
            except:
                if module in stdlib:
                    pass
                    logging.debug(f"module {module} is in the Python standard library.")
                else:
                    logging.warn(f"Warning: Failed to find corresponding package name for import {module}")

        if len(packages) == 0:
            logging.warn(
                f"No metadata was found for any of the imported modules. Did you install your virtual environment?"
            )
        logging.debug("\n")

        return packages
