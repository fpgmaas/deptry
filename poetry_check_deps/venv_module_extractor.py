import glob
import re
from pathlib import Path

class VenvModuleExtractor:
    """
    Extract the installed modules and their corresponding package name. Here, module refers to the name
    used for importing (e.g. python_dateutil) and package refers to the name used to install it (e.g. python-dateutil)

    Finding these modules and their package names is done by searching for the .dist-info files within the .venv directory
    and opening the METADATA files within them.
    """

    def __init__(self):
        pass

    def extract_modules(self):
        modules_and_packages = []
        for module_path in glob.glob('.venv/**/site-packages/*.dist-info', recursive=True):
            module_name = self._get_module_name_from(module_path)
            package_name = self._get_package_name_from(module_path)
            modules_and_packages.append({'module_name' : module_name, 'package_name' : package_name})
        return modules_and_packages

    @staticmethod
    def _get_module_name_from(module_path: str) -> str:
       return re.search(r'(.*?)-[0-9]', module_path.split('/')[-1], re.IGNORECASE).group(1)

    @staticmethod
    def _get_package_name_from(module_path: str) -> str:
        with open(Path(module_path) / 'METADATA', 'r') as file:
            metadata = file.readlines()
        return re.search( r'Name: (.+?)$', [line for line in metadata if line.startswith('Name:')][0]).group(1)