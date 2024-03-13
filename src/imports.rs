use crate::file_utils;
use crate::location;
use crate::visitor;

use file_utils::read_file;
use location::Location;
use pyo3::exceptions::PySyntaxError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyString};
use rayon::prelude::*;
use rustpython_ast::Mod;
use rustpython_ast::Visitor;
use rustpython_parser::source_code::LineIndex;
use rustpython_parser::text_size::TextRange;
use rustpython_parser::{parse, Mode};
use std::collections::HashMap;
use visitor::ImportVisitor;

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

/// Parses the content of a Python file into an abstract syntax tree (AST).
pub fn get_ast_from_file_content(file_content: &str, file_path: &str) -> PyResult<Mod> {
    parse(file_content, Mode::Module, file_path)
        .map_err(|e| PySyntaxError::new_err(format!("Error parsing file {}: {}", file_path, e)))
}

/// Iterates through an AST to identify and collect import statements, and returns them together with their
/// respective TextRange for each occurrence.
fn extract_imports_from_ast(ast: Mod) -> HashMap<String, Vec<TextRange>> {
    let mut visitor = ImportVisitor::new();

    if let Mod::Module(module) = ast {
        for stmt in module.body {
            visitor.visit_stmt(stmt);
        }
    }

    visitor.get_imports()
}

/// Converts textual ranges of import statements into structured location objects.
/// Facilitates the mapping of imports to detailed, file-specific location data (file, line, column).
fn convert_imports_with_textranges_to_location_objects(
    imports: HashMap<String, Vec<TextRange>>,
    file_path: &str,
    source_code: &str,
) -> HashMap<String, Vec<Location>> {
    let line_index = LineIndex::from_source_text(source_code);
    let mut imports_with_locations = HashMap::<String, Vec<Location>>::new();

    for (module, ranges) in imports {
        let locations: Vec<Location> = ranges
            .iter()
            .map(|range| {
                let start_line = line_index.line_index(range.start()).get() as usize;
                let start_col = line_index
                    .source_location(range.start(), source_code)
                    .column
                    .get() as usize;
                Location {
                    file: file_path.to_string(),
                    line: Some(start_line),
                    column: Some(start_col),
                }
            })
            .collect();
        imports_with_locations.insert(module, locations);
    }
    imports_with_locations
}

/// Transforms a Rust HashMap containing import data into a Python dictionary suitable for Python-side consumption.
fn convert_to_python_dict(
    py: Python<'_>,
    imports_with_locations: HashMap<String, Vec<Location>>,
) -> PyResult<PyObject> {
    let imports_dict = PyDict::new(py);

    for (module, locations) in imports_with_locations {
        let py_locations: Vec<PyObject> = locations
            .into_iter()
            .map(|location| location.into_py(py))
            .collect();
        let locations_list = PyList::new(py, &py_locations);
        imports_dict.set_item(module, locations_list)?;
    }

    Ok(imports_dict.into())
}
