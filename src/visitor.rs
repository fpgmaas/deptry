use rustpython_ast::{self, Int, StmtImport, StmtImportFrom, Visitor};
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
            let top_level_module = get_top_level_module_name(&alias.name);
            self.imports
                .entry(top_level_module)
                .or_default()
                .push(alias.range);
        }
    }

    fn visit_stmt_import_from(&mut self, node: StmtImportFrom) {
        let Some(module) = &node.module else { return };
        if node.level != Some(Int::new(0)) {
            return;
        }

        self.imports
            .entry(get_top_level_module_name(module.as_str()))
            .or_default()
            .push(node.range);
    }
}

/// Extracts the top-level module name from a potentially nested module path.
/// e.g. when a module_name is `foo.bar`, this returns `foo`.
fn get_top_level_module_name(module_name: &str) -> String {
    module_name
        .split('.')
        .next()
        .unwrap_or(module_name)
        .to_string()
}
