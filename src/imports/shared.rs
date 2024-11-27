use crate::location;
use crate::visitor;

use location::Location;
use pyo3::exceptions::PySyntaxError;
use pyo3::prelude::*;
use ruff_python_ast::visitor::Visitor;
use ruff_python_ast::{Mod, ModModule};
use ruff_python_parser::{parse, Mode, Parsed};
use ruff_source_file::LineIndex;
use ruff_text_size::TextRange;
use std::collections::HashMap;
use visitor::ImportVisitor;

pub type FileToImportsMap = HashMap<String, Vec<Location>>;
pub type ErrorList = Vec<(String, PyErr)>;

pub struct ThreadResult {
    pub file: String,
    pub result: PyResult<FileToImportsMap>,
}

/// Parses the content of a Python file into a parsed source code.
pub fn parse_file_content(file_content: &str) -> PyResult<Parsed<Mod>> {
    let parsed =
        parse(file_content, Mode::Module).map_err(|e| PySyntaxError::new_err(e.to_string()))?;
    Ok(parsed)
}

/// Iterates through a parsed source code to identify and collect import statements, and returns them
/// together with their respective `TextRange` for each occurrence.
pub fn extract_imports_from_parsed_file_content(
    parsed: Parsed<Mod>,
) -> HashMap<String, Vec<TextRange>> {
    let mut visitor = ImportVisitor::new();

    if let Mod::Module(ModModule { body, .. }) = parsed.into_syntax() {
        for stmt in body {
            visitor.visit_stmt(&stmt);
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
) -> FileToImportsMap {
    let line_index = LineIndex::from_source_text(source_code);
    let mut imports_with_locations = HashMap::<String, Vec<Location>>::new();

    for (module, ranges) in imports {
        let locations: Vec<Location> = ranges
            .iter()
            .map(|range| {
                let start_line = line_index.line_index(range.start()).get();
                let start_col = line_index
                    .source_location(range.start(), source_code)
                    .column
                    .get();
                Location {
                    file: file_path.to_owned(),
                    line: Some(start_line),
                    column: Some(start_col),
                }
            })
            .collect();
        imports_with_locations.insert(module, locations);
    }
    imports_with_locations
}

// Shared logic for merging results from different threads.
pub fn merge_results_from_threads(results: Vec<ThreadResult>) -> (FileToImportsMap, ErrorList) {
    let mut all_imports = HashMap::new();
    let mut errors = Vec::new();

    for thread_result in results {
        match thread_result.result {
            Ok(file_result) => {
                for (module, locations) in file_result {
                    all_imports
                        .entry(module)
                        .or_insert_with(Vec::new)
                        .extend(locations);
                }
            }
            Err(e) => errors.push((thread_result.file, e)),
        }
    }

    (all_imports, errors)
}

// Shared logic for logging errors.
pub fn log_python_errors_as_warnings(errors: &[(String, PyErr)]) {
    for (path, error) in errors {
        log::warn!(
            "Warning: Skipping processing of {} because of the following error: \"{}\".",
            path,
            error
        );
    }
}
