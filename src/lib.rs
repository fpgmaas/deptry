use pyo3::prelude::*;
use pyo3::exceptions::{PyFileNotFoundError, PyIOError, PySyntaxError};
use rustpython_parser::{ast, parse, Mode, text_size};
use std::collections::HashMap;
use std::fs;


use std::io::ErrorKind;

#[pyfunction]
fn get_imports_from_file(file_path: String) -> PyResult<String> {
    let ast: ast::Mod = get_ast_from_file(file_path.clone())?;
    let imported_modules = extract_imports_from_ast(ast, &file_path);

    // Print the imported modules in a readable multi-line format
    println!("{:#?}", imported_modules);
    // Convert the HashMap debug representation to a String
    let imports_str = format!("{:#?}", imported_modules);
    // Return the string representation of imported modules
    Ok(imports_str)
}

/// Read a file and return its contents as a String.
fn read_file(file_path: String) -> PyResult<String> {
    let file_content: PyResult<String> = fs::read_to_string(&file_path)
    .map_err(|e| {
        if e.kind() == ErrorKind::NotFound {
            PyFileNotFoundError::new_err(format!("File not found: '{}'", file_path))
        } else {
            PyIOError::new_err(format!("An error occured: '{}'", e))
        }
    });
    return file_content
}

/// Read a Python file, and return it as an AST,
fn get_ast_from_file(file_path: String) -> PyResult<ast::Mod> {
    let file_content: String = read_file(file_path.clone())?;
    let file_content_slice: &str = &file_content;

    let ast: ast::Mod = parse(&file_content_slice, Mode::Module, "<embedded>")
        .map_err(|e| PySyntaxError::new_err(format!("Error parsing file {}: {}", file_path, e)))?;
    return Ok(ast);
}

#[derive(Debug, Clone)]
struct Location {
    file: String,
    lineno: usize,
    col_offset: usize,
}

struct ImportVisitor<R = crate::text_size::TextRange> {
    imports: HashMap<String, Vec<Location>>,
    file_path: String,
    phantom: std::marker::PhantomData<R>,
}

impl<R> ImportVisitor<R> {
    fn new(file_path: String) -> Self {
        ImportVisitor {
            imports: HashMap::new(),
            file_path,
            phantom: std::marker::PhantomData,
        }
    }
}

impl<R: text_size::TextRange> ast::<R> for ImportVisitor<R> {
    fn visit_stmt_import(&mut self, node: ast::StmtImport<R>) {
        for alias in &node.names {
            let name = alias.name.split('.').next().unwrap_or_default().to_string();
            self.imports.entry(name).or_default().push(Location {
                file: self.file_path.clone(),
                lineno: alias.location.row(),
                col_offset: alias.location.column(),
            });
        }
    }

    fn visit_stmt_import_from(&mut self, node: StmtImportFrom<R>) {
        let module_name = node.module.as_ref().map_or("", String::as_str).split('.').next().unwrap_or_default().to_string();
        for alias in &node.names {
            let name = if module_name.is_empty() {
                alias.name.clone()
            } else {
                format!("{}.{}", module_name, alias.name)
            };
            self.imports.entry(name).or_default().push(Location {
                file: self.file_path.clone(),
                lineno: alias.location.row(),
                col_offset: alias.location.column(),
            });
        }
    }
}



/// A Python module implemented in Rust.
#[pymodule]
fn deptryrs(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(get_imports_from_file, m)?)?;
    Ok(())
}
