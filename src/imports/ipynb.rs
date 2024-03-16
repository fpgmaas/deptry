use crate::file_utils;
use crate::location;

use file_utils::read_file;
use location::Location;
use pyo3::exceptions::PySyntaxError;
use pyo3::prelude::*;
use pyo3::types::PyString;
use rayon::prelude::*;
use regex::Regex;
use std::collections::HashMap;

use super::shared::{
    convert_imports_with_textranges_to_location_objects, convert_to_python_dict,
    extract_imports_from_ast, get_ast_from_file_content,
};

/// Processes multiple .ipynb files in parallel to extract import statements and their locations.
/// Accepts a list of file paths and returns a dictionary mapping module names to their import locations.
#[pyfunction]
pub fn get_imports_from_ipynb_files(py: Python, file_paths: Vec<&PyString>) -> PyResult<PyObject> {
    let rust_file_paths: Vec<String> = file_paths
        .iter()
        .map(|py_str| py_str.to_str().unwrap().to_owned())
        .collect();

    // Process each file in parallel and collect results
    let results: PyResult<Vec<_>> = rust_file_paths
        .par_iter()
        .map(|path_str| _get_imports_from_ipynb_file(path_str))
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

/// Processes a single .ipynb file to extract import statements and their locations.
/// Accepts a single file path and returns a dictionary mapping module names to their import locations.
#[pyfunction]
pub fn get_imports_from_ipynb_file(py: Python, file_path: &PyString) -> PyResult<PyObject> {
    let path_str = file_path.to_str()?;
    let result = _get_imports_from_ipynb_file(path_str)?;

    convert_to_python_dict(py, result)
}

fn _extract_import_statements_from_notebook_cells(cells: &[serde_json::Value]) -> String {
    let import_regex =
        Regex::new(r"^(?:from\s+(\w+)(?:\.\w+)?\s+)?import\s+([^\s,.]+)(?:\.\w+)?").unwrap();

    let import_statements: Vec<String> = cells
        .iter()
        .filter(|cell| cell["cell_type"] == "code")
        .flat_map(|cell| cell["source"].as_array())
        .flatten()
        .filter_map(|line| line.as_str())
        .filter(|line| import_regex.is_match(line))
        .map(|line| line.to_string())
        .collect();

    import_statements.join("\n")
}

/// Core helper function that extracts import statements and their locations from the content of a single .ipynb file.
fn _get_imports_from_ipynb_file(path_str: &str) -> PyResult<HashMap<String, Vec<Location>>> {
    let file_content = match read_file(path_str) {
        Ok(content) => content,
        Err(_) => {
            log::warn!("Warning: File {} could not be read. Skipping...", path_str);
            return Ok(HashMap::new());
        }
    };

    let notebook: serde_json::Value = match serde_json::from_str(&file_content) {
        Ok(content) => content,
        Err(_) => {
            log::warn!("Warning: File {} is not valid JSON. Skipping...", path_str);
            return Ok(HashMap::new());
        }
    };

    let cells = match notebook["cells"].as_array() {
        Some(cells) => cells,
        None => {
            log::warn!(
                "Warning: File {} is not a valid notebook: 'cells' is not an array. Skipping...",
                path_str
            );
            return Ok(HashMap::new());
        }
    };

    let imports_script = _extract_import_statements_from_notebook_cells(cells);

    let ast = get_ast_from_file_content(&imports_script, path_str)
        .map_err(|e| PySyntaxError::new_err(format!("Error parsing file {}: {}", path_str, e)))?;

    let imported_modules = extract_imports_from_ast(ast);

    Ok(convert_imports_with_textranges_to_location_objects(
        imported_modules,
        path_str,
        &file_content,
    ))
}
