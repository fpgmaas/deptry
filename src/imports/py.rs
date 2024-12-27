use crate::file_utils;
use crate::location;

use super::shared;
use file_utils::read_file;
use location::Location;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use rayon::prelude::*;
use std::collections::HashMap;

/// Processes multiple Python files in parallel to extract import statements and their locations.
/// Accepts a list of file paths and returns a dictionary mapping module names to their import locations.
#[pyfunction]
pub fn get_imports_from_py_files(py: Python, file_paths: Vec<String>) -> Bound<'_, PyDict> {
    let results: Vec<_> = file_paths
        .par_iter()
        .map(|path_str| {
            let result = get_imports_from_py_file(path_str);
            shared::ThreadResult {
                file: path_str.to_string(),
                result,
            }
        })
        .collect();

    let (all_imports, errors) = shared::merge_results_from_threads(results);
    shared::log_python_errors_as_warnings(&errors);

    all_imports.into_pyobject(py).unwrap()
}

/// Core helper function that extracts import statements and their locations from the content of a single Python file.
/// Used internally by both parallel and single file processing functions.
fn get_imports_from_py_file(path_str: &str) -> PyResult<HashMap<String, Vec<Location>>> {
    let file_content = read_file(path_str)?;
    let ast = shared::parse_file_content(&file_content)?;
    let imported_modules = shared::extract_imports_from_parsed_file_content(ast);
    Ok(shared::convert_imports_with_textranges_to_location_objects(
        imported_modules,
        path_str,
        &file_content,
    ))
}
