from deptry.notebook_import_extractor import NotebookImportExtractor


def test_convert_notebook():
    imports = NotebookImportExtractor().extract("tests/data/example_project/src/notebook.ipynb")
    assert "import click" in imports[0]
    assert "from urllib3 import contrib" in imports[1]
    assert len(imports) == 3
