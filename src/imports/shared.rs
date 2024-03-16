use crate::location;
use crate::visitor;

use location::Location;
use pyo3::exceptions::PySyntaxError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use rustpython_ast::Mod;
use rustpython_ast::Visitor;
use rustpython_parser::source_code::LineIndex;
use rustpython_parser::text_size::TextRange;
use rustpython_parser::{parse, Mode};
use std::collections::HashMap;
use visitor::ImportVisitor;

/// Parses the content of a Python file into an abstract syntax tree (AST).
pub fn get_ast_from_file_content(file_content: &str, file_path: &str) -> PyResult<Mod> {
    parse(file_content, Mode::Module, file_path)
        .map_err(|e| PySyntaxError::new_err(format!("Error parsing file {}: {}", file_path, e)))
}

/// Iterates through an AST to identify and collect import statements, and returns them together with their
/// respective TextRange for each occurrence.
pub fn extract_imports_from_ast(ast: Mod) -> HashMap<String, Vec<TextRange>> {
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
pub fn convert_imports_with_textranges_to_location_objects(
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
pub fn convert_to_python_dict(
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
