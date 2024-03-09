use pyo3::exceptions::{PyFileNotFoundError, PyIOError, PySyntaxError};
use pyo3::prelude::*;
use rustpython_ast::{Mod, Stmt};
use rustpython_parser::{parse, Mode};
use std::collections::HashMap;
use std::fs;

use std::io::ErrorKind;

mod visitor;
use visitor::ImportVisitor;
mod location;
use location::Location;
use rustpython_ast::Visitor;
use rustpython_parser::text_size::TextRange;

#[pyfunction]
fn get_imports_from_file(file_path: String) -> PyResult<String> {
    let ast: Mod = get_ast_from_file(&file_path)?;
    let imported_modules = extract_imports_from_ast(ast, &file_path);

    // Convert the HashMap debug representation to a String
    let imports_str = format!("{:#?}", imported_modules);
    // Return the string representation of imported modules
    Ok(imports_str)
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
fn get_ast_from_file(file_path: &str) -> PyResult<Mod> {
    let file_content: String = read_file(file_path)?;
    parse(&file_content, Mode::Module, file_path)
        .map_err(|e| PySyntaxError::new_err(format!("Error parsing file {}: {}", file_path, e)))
}

fn extract_imports_from_ast(ast: Mod, file_path: &str) -> HashMap<String, Vec<TextRange>> {
    let mut visitor = ImportVisitor::new(file_path.to_string());

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

/// A Python module implemented in Rust.
#[pymodule]
fn deptryrs(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(get_imports_from_file, m)?)?;
    Ok(())
}
