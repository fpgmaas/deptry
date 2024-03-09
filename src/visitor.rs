use rustpython_ast::{self, StmtImport, StmtImportFrom, Visitor};
use rustpython_parser::text_size::TextRange;
use std::collections::HashMap;

#[derive(Debug, Clone)]
pub struct ImportVisitor {
    imports: HashMap<String, Vec<TextRange>>,
}

impl ImportVisitor {
    pub fn new() -> Self {
        ImportVisitor {
            imports: HashMap::new(),
        }
    }

    pub fn get_imports(self) -> HashMap<String, Vec<TextRange>> {
        self.imports
    }
}

impl Visitor for ImportVisitor {
    fn visit_stmt_import(&mut self, node: StmtImport) {
        for alias in &node.names {
            let top_level_module = get_top_level_module_name(&alias.name.to_string());
            self.imports
                .entry(top_level_module)
                .or_default()
                .push(alias.range);
        }
    }

    fn visit_stmt_import_from(&mut self, node: StmtImportFrom) {
        if let Some(module) = &node.module {
            let module_name = module.to_string();
            let top_level_module = get_top_level_module_name(&module_name);
            let module_range = node.range;
            self.imports
                .entry(top_level_module)
                .or_default()
                .push(module_range);
        }
    }
}

/// Extracts the top-level module name from a potentially nested module path.
/// e.g. when a module_name is `foo.bar`, this returns `foo`.
///
/// # Arguments
///
/// * `module_name` - The potentially nested module name.
///
/// # Returns
///
/// The top-level module name.
fn get_top_level_module_name(module_name: &str) -> String {
    module_name
        .split('.')
        .next()
        .unwrap_or(module_name)
        .to_string()
}
