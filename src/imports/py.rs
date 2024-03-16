use crate::file_utils;
use crate::location;

use file_utils::read_file;
use location::Location;
use pyo3::exceptions::PySyntaxError;
use pyo3::prelude::*;
use pyo3::types::PyString;
use rayon::prelude::*;
use std::collections::HashMap;

use super::shared::{
    convert_imports_with_textranges_to_location_objects, convert_to_python_dict,
    extract_imports_from_ast, get_ast_from_file_content,
};

/// Processes multiple Python files in parallel to extract import statements and their locations.
/// Accepts a list of file paths and returns a dictionary mapping module names to their import locations.
#[pyfunction]
pub fn get_imports_from_py_files(py: Python, file_paths: Vec<&PyString>) -> PyResult<PyObject> {
    let rust_file_paths: Vec<String> = file_paths
        .iter()
        .map(|py_str| py_str.to_str().unwrap().to_owned())
        .collect();

    // Process each file in parallel and collect results
    let results: PyResult<Vec<_>> = rust_file_paths
        .par_iter()
        .map(|path_str| _get_imports_from_py_file(path_str))
        .collect();

    let results = results?;

    // Merge results from each thread
    let mut all_imports = HashMap::new();
    for file_result in results {
        for (module, locations) in file_result {
            all_imports
                .entry(module)
                .or_insert_with(Vec::new)
                .extend(locations);
        }
    }

    convert_to_python_dict(py, all_imports)
}

/// Processes a single Python file to extract import statements and their locations.
/// Accepts a single file path and returns a dictionary mapping module names to their import locations.
#[pyfunction]
pub fn get_imports_from_py_file(py: Python, file_path: &PyString) -> PyResult<PyObject> {
    let path_str = file_path.to_str()?;
    let result = _get_imports_from_py_file(path_str)?;

    convert_to_python_dict(py, result)
}

/// Core helper function that extracts import statements and their locations from the content of a single Python file.
/// Used internally by both parallel and single file processing functions.
fn _get_imports_from_py_file(path_str: &str) -> PyResult<HashMap<String, Vec<Location>>> {
    let file_content = match read_file(path_str) {
        Ok(content) => content,
        Err(_) => {
            log::warn!("Warning: File {} could not be read. Skipping...", path_str);
            return Ok(HashMap::new());
        }
    };

    let ast = get_ast_from_file_content(&file_content, path_str)
        .map_err(|e| PySyntaxError::new_err(format!("Error parsing file {}: {}", path_str, e)))?;

    let imported_modules = extract_imports_from_ast(ast);

    Ok(convert_imports_with_textranges_to_location_objects(
        imported_modules,
        path_str,
        &file_content,
    ))
}
