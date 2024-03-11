// lib.rs

use pyo3::exceptions::PySyntaxError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyString};
use rustpython_ast::Mod;
use rustpython_parser::source_code::LineIndex;
use rustpython_parser::text_size::TextRange;
use rustpython_parser::{parse, Mode};
use std::collections::HashMap;

mod file_utils;
mod location;
mod visitor;

use file_utils::read_file;
use location::Location;
use rayon::prelude::*;
use rustpython_ast::Visitor;
use visitor::ImportVisitor;

#[pymodule]
fn deptry(py: Python, m: &PyModule) -> PyResult<()> {
    pyo3_log::init(); // Initialize logging to forward to Python's logger

    m.add_function(wrap_pyfunction!(get_imports_from_py_files, m)?)?;
    m.add_function(wrap_pyfunction!(get_imports_from_py_file, m)?)?;
    m.add_class::<Location>()?;
    Ok(())
}

#[pyfunction]
fn get_imports_from_py_files(py: Python, file_paths: Vec<&PyString>) -> PyResult<PyObject> {
    let rust_file_paths: Vec<String> = file_paths
        .iter()
        .map(|py_str| py_str.to_str().unwrap().to_owned())
        .collect();

    // This will hold the merged results from all files
    let mut all_imports = HashMap::new();

    // Iterate over file paths, process each, and merge the results
    for path_str in rust_file_paths.iter() {
        let file_result = _get_imports_from_py_file(path_str)?;
        for (module, locations) in file_result {
            all_imports.entry(module).or_insert_with(Vec::new).extend(locations);
        }
    }

    // Now convert the merged results to a Python dictionary
    convert_to_python_dict(py, all_imports)
}


#[pyfunction]
fn get_imports_from_py_file(py: Python, file_path: &PyString) -> PyResult<PyObject> {
    let path_str = file_path.to_str()?;
    let result = _get_imports_from_py_file(path_str)?;

    convert_to_python_dict(py, result)
}

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

// Parses the content of a Python file into an abstract syntax tree (AST).
pub fn get_ast_from_file_content(file_content: &str, file_path: &str) -> PyResult<Mod> {
    parse(&file_content, Mode::Module, file_path)
        .map_err(|e| PySyntaxError::new_err(format!("Error parsing file {}: {}", file_path, e)))
}

// Iterates through an AST to extract import statements and collects them along with their locations.
fn extract_imports_from_ast(ast: Mod) -> HashMap<String, Vec<TextRange>> {
    let mut visitor = ImportVisitor::new();

    match ast {
        Mod::Module(module) => {
            for stmt in module.body {
                visitor.visit_stmt(stmt);
            }
        }
        _ => {}
    }
    visitor.get_imports()
}

/// Imports now have associated TextRanges, which is the amount of bytes since the start of the file.
/// This function takes that as input, and converts it to imports with associated Location objects,
/// That carry information such as the file name, the line number, and the column offset.
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

// Converts the structured location data into a Python-compatible dictionary format.
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
