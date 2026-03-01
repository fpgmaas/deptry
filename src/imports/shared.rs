use crate::location;
use crate::visitor;

use location::Location;
use pyo3::exceptions::PySyntaxError;
use pyo3::prelude::*;
use regex::Regex;
use ruff_python_ast::visitor::Visitor;
use ruff_python_ast::{Mod, ModModule};
use ruff_python_parser::{Mode, ParseOptions, Parsed, parse};
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
    let parsed = parse(file_content, ParseOptions::from(Mode::Module))
        .map_err(|e| PySyntaxError::new_err(e.to_string()))?;
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

/// Extracts ignored rule codes from an inline `# deptry: ignore` comment on a source line.
///
/// Supports:
/// - `# deptry: ignore` — returns `["ALL"]` to indicate all rules are ignored.
/// - `# deptry: ignore[DEP001]` — returns `["DEP001"]`.
/// - `# deptry: ignore[DEP001,DEP003]` — returns `["DEP001", "DEP003"]`.
///
/// Returns an empty `Vec` if no ignore comment is found.
pub fn extract_ignored_rule_codes(line: &str) -> Vec<String> {
    let re = Regex::new(r"#\s*deptry:\s*ignore(?:\[([A-Z0-9,\s]+)\])?").unwrap();

    if let Some(caps) = re.captures(line) {
        match caps.get(1) {
            Some(codes) => codes
                .as_str()
                .split(',')
                .map(|s| s.trim().to_owned())
                .filter(|s| !s.is_empty())
                .collect(),
            None => vec!["ALL".to_owned()],
        }
    } else {
        vec![]
    }
}

/// Converts textual ranges of import statements into structured location objects.
/// Facilitates the mapping of imports to detailed, file-specific location data (file, line, column).
pub fn convert_imports_with_textranges_to_location_objects(
    imports: HashMap<String, Vec<TextRange>>,
    file_path: &str,
    source_code: &str,
) -> FileToImportsMap {
    let line_index = LineIndex::from_source_text(source_code);
    let source_lines: Vec<&str> = source_code.lines().collect();
    let mut imports_with_locations = HashMap::<String, Vec<Location>>::new();

    for (module, ranges) in imports {
        let locations: Vec<Location> = ranges
            .iter()
            .map(|range| {
                let line_column = line_index.line_column(range.start(), source_code);
                let line_number = line_column.line.get();
                let ignored_rule_codes = source_lines
                    .get(line_number - 1)
                    .map(|line| extract_ignored_rule_codes(line))
                    .unwrap_or_default();
                Location {
                    file: file_path.to_owned(),
                    line: Some(line_number),
                    column: Some(line_column.column.get()),
                    ignored_rule_codes,
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
            "Warning: Skipping processing of {path} because of the following error: \"{error}\"."
        );
    }
}
