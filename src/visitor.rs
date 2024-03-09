use rustpython_ast::{self, Mod, Stmt, StmtImport, StmtImportFrom, Visitor};
use rustpython_parser::text_size::TextRange;
use std::collections::HashMap;

#[derive(Debug, Clone)]

pub struct ImportVisitor {
    imports: HashMap<String, Vec<TextRange>>,
    file_path: String,
}

impl ImportVisitor {
    pub fn new(file_path: String) -> Self {
        ImportVisitor {
            imports: HashMap::new(),
            file_path,
        }
    }
    pub fn get_imports(self) -> HashMap<String, Vec<TextRange>> {
        self.imports
    }
}

impl Visitor for ImportVisitor {
    // Override this method to handle 'import' statements.
    fn visit_stmt_import(&mut self, node: StmtImport) {
        // println!("{:#?}", node);
        for alias in &node.names {
            self.imports
                .entry(alias.name.to_string())
                .or_default()
                .push(alias.range);
        }
    }

    // Override this method to handle 'import from' statements.
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
