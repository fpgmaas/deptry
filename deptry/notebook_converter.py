import logging
from pathlib import Path

import nbformat
from nbconvert import PythonExporter
from nbconvert.writers import FilesWriter


class NotebookConverter:
    """
    Class to convert Jupyter notebooks into .py files.

    Args:
        build_directory: The directory in which to place the converted .py files.
    """

    def __init__(self, build_directory: str):

        self.build_directory = build_directory

    def convert(self, path_to_ipynb: Path, output_file_name: str):
        """
        Convert a Jupyter notebook into a .py file.

        Args:
            path_to_ipynb: Path to the .ipynb file to be converted.
            output_file_name: Name of the .py file to be created. NOTE: Name should be supplied Without the .py extension.
        """

        # We need to disable logging because nbconvert logs to the root logger.
        logging.disable(logging.CRITICAL)
        notebook = nbformat.read(path_to_ipynb, as_version=4)

        exporter = PythonExporter()
        (body, resources) = exporter.from_notebook_node(notebook)
        path_to_output = FilesWriter(build_directory=self.build_directory).write(
            output=body, resources=resources, notebook_name=output_file_name
        )
        logging.disable(logging.NOTSET)
        return path_to_output
