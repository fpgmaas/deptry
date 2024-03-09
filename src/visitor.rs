use rustpython_ast::{self, Mod, Stmt, StmtImport, StmtImportFrom, Visitor};
use rustpython_parser::text_size::TextRange;
use std::collections::HashMap;

#[derive(Debug, Clone)]

pub struct ImportVisitor {
    imports: HashMap<String, Vec<TextRange>>,
}

/// Used to walk through an AST and extract all imported modules
/// It will return a HashMap, where each key is a module and the value is a vector of TextRanges.
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
            self.imports
                .entry(alias.name.to_string())
                .or_default()
                .push(alias.range);
        }
    }

    fn visit_stmt_import_from(&mut self, node: StmtImportFrom) {
        if let Some(module) = &node.module {
            let module_name = module.to_string();
            let module_range = node.range;
            self.imports
                .entry(module_name)
                .or_default()
                .push(module_range);
        }
    }
}
