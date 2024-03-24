use crate::file_utils;
use crate::location;

use file_utils::read_file;
use location::Location;
use pyo3::exceptions::PySyntaxError;
use pyo3::prelude::*;
use pyo3::types::PyString;
use rayon::prelude::*;
use std::collections::HashMap;

use super::shared;

/// Processes multiple Python files in parallel to extract import statements and their locations.
/// Accepts a list of file paths and returns a dictionary mapping module names to their import locations.
#[pyfunction]
pub fn get_imports_from_ipynb_files(py: Python, file_paths: Vec<&PyString>) -> PyResult<PyObject> {
    let rust_file_paths: Vec<String> = file_paths
        .iter()
        .map(|py_str| py_str.to_str().unwrap().to_owned())
        .collect();

    let results: Vec<_> = rust_file_paths
        .par_iter()
        .map(|path_str| {
            let result = _get_imports_from_ipynb_file(path_str);
            shared::ThreadResult {
                file: path_str.to_string(),
                result,
            }
        })
        .collect();

    let (all_imports, errors) = shared::merge_results_from_threads(results);
    shared::log_python_errors_as_warnings(&errors);

    shared::convert_to_python_dict(py, all_imports)
}

/// Core helper function that extracts import statements and their locations from a single .ipynb file.
/// Ensures robust error handling and provides clearer, more detailed comments.
fn _get_imports_from_ipynb_file(path_str: &str) -> PyResult<HashMap<String, Vec<Location>>> {
    let file_content = read_file(path_str)?;
    let notebook: serde_json::Value =
        serde_json::from_str(&file_content).map_err(|e| PySyntaxError::new_err(e.to_string()))?;
    let cells = notebook["cells"]
        .as_array()
        .ok_or_else(|| PySyntaxError::new_err("Expected 'cells' to be an array"))?;
    let python_code = _extract_code_from_notebook_cells(cells);

    let ast = shared::get_ast_from_file_content(&python_code)?;
    let imported_modules = shared::extract_imports_from_ast(ast);

    Ok(shared::convert_imports_with_textranges_to_location_objects(
        imported_modules,
        path_str,
        &python_code,
    ))
}

/// Extracts and concatenates code from notebook code cells.
fn _extract_code_from_notebook_cells(cells: &[serde_json::Value]) -> String {
    let code_lines: Vec<String> = cells
        .iter()
        .filter(|cell| cell["cell_type"] == "code")
        .filter_map(|cell| cell["source"].as_array())
        .flatten()
        .filter_map(|line| line.as_str())
        .map(str::to_owned)
        .collect();

    code_lines.join("\n")
}
