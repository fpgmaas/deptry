import json
import re
from pathlib import Path


class NotebookImportExtractor:
    """
    Class to extract import statements from a Jupyter notebook and return as a list of strings.
    """

    def __init__(self):
        pass

    def extract(self, path_to_ipynb: Path):
        """
        Extract import statements from a Jupyter notebook and return as a list of strings.

        Args:
            path_to_ipynb: Path to the .ipynb file to extract inputs from
        """
        notebook = self._read_ipynb_file(path_to_ipynb)
        cells = self._keep_code_cells(notebook)
        import_statements = [self._extract_import_statements_from_cell(cell) for cell in cells]
        return self._flatten(import_statements)

    @staticmethod
    def _read_ipynb_file(path_to_ipynb):
        with open(path_to_ipynb, "r") as f:
            notebook = json.load(f)
        return notebook

    @staticmethod
    def _keep_code_cells(notebook):
        return [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]

    @staticmethod
    def _contains_import_statements(line):
        return re.search(r"^(?:from\s+(\w+)(?:\.\w+)?\s+)?import\s+([^\s,.]+)(?:\.\w+)?", line) is not None

    def _extract_import_statements_from_cell(self, cell):
        return [line for line in cell["source"] if self._contains_import_statements(line)]

    @staticmethod
    def _flatten(list_of_lists):
        return [item for sublist in list_of_lists for item in sublist]
