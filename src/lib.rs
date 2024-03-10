use pyo3::exceptions::{PyFileNotFoundError, PyIOError, PySyntaxError};
use pyo3::prelude::*;
use rustpython_ast::{Mod, Stmt};
use rustpython_parser::{parse, Mode};
use std::collections::HashMap;
use std::fs;

use std::io::ErrorKind;
use std::path::PathBuf;

mod visitor;
use visitor::ImportVisitor;
mod location;
use location::Location;
use pyo3::types::{PyDict, PyList, PyString};
use pyo3::{PyObject, PyResult};
use rustpython_ast::Visitor;
use rustpython_parser::source_code::LineIndex;
use rustpython_parser::text_size::TextRange;

#[pymodule]
fn deptryrs(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(get_imports_from_file, m)?)?;
    m.add_class::<Location>()?;
    Ok(())
}

#[pyfunction]
fn get_imports_from_file(py: Python<'_>, file_path: &PyString) -> PyResult<PyObject> {
    let path_str = file_path.to_str()?;
    let file_content = read_file(&path_str)?;
    let ast = get_ast_from_file_content(&file_content, &path_str)?;
    let imported_modules = extract_imports_from_ast(ast);
    let imports_with_locations = convert_imports_with_textranges_to_location_objects(
        imported_modules,
        &path_str,
        &file_content,
    );
    let imports_dict = convert_to_python_dict(py, imports_with_locations);
    Ok(imports_dict)
}

/// Read a file and return its contents as a String.
fn read_file(file_path: &str) -> PyResult<String> {
    fs::read_to_string(file_path).map_err(|e| {
        if e.kind() == ErrorKind::NotFound {
            PyFileNotFoundError::new_err(format!("File not found: '{}'", file_path))
        } else {
            PyIOError::new_err(format!("An error occured: '{}'", e))
        }
    })
}

/// Read a Python file, and return it as an AST,
fn get_ast_from_file_content(file_content: &str, file_path: &str) -> PyResult<Mod> {
    parse(&file_content, Mode::Module, file_path)
        .map_err(|e| PySyntaxError::new_err(format!("Error parsing file {}: {}", file_path, e)))
}

/// Extract all imports from an AST
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
/// This function takes thata s input, and converts it to imports with associated Location objects,
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

fn convert_to_python_dict(
    py: Python<'_>,
    imports_with_locations: HashMap<String, Vec<Location>>,
) -> PyObject {
    let imports_dict = PyDict::new(py);

    for (module, locations) in imports_with_locations {
        let py_locations: Vec<PyObject> = locations
            .into_iter()
            .map(|location| location.into_py(py))
            .collect();
        let locations_list = PyList::new(py, &py_locations);
        imports_dict.set_item(module, locations_list).unwrap();
    }

    imports_dict.into()
}
