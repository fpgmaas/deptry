use rustpython_ast::{
    self, Visitor, StmtImport, StmtImportFrom, Stmt, Mod,
};
use std::collections::HashMap;
use crate::location::Location;

#[derive(Debug, Clone)]


pub struct ImportVisitor {
    imports: HashMap<String, Vec<Location>>,
    file_path: String,
}

impl ImportVisitor {
    pub fn new(file_path: String) -> Self {
        ImportVisitor {
            imports: HashMap::new(),
            file_path,
        }
    }
}

impl Visitor for ImportVisitor {
    // Override this method to handle 'import' statements.
    fn visit_stmt_import(&mut self, node: StmtImport) {
        println!("{:#?}", node);
        // for alias in &node.names {
        //     let location = Location {
        //         file: self.file_path.clone(),
        //         lineno: node.location.row(),
        //         col_offset: node.location.column(),
        //     };
        //     self.imports.entry(alias.symbol.clone()).or_default().push(location);
        // }
    }

    // Override this method to handle 'import from' statements.
    fn visit_stmt_import_from(&mut self, node: StmtImportFrom) {
        println!("{:#?}", node);
        // if let Some(module) = &node.module {
        //     for alias in &node.names {
        //         let full_name = format!("{}.{}", module.join("."), alias.symbol);
        //         let location = Location {
        //             file: self.file_path.clone(),
        //             lineno: node.location.row(),
        //             col_offset: node.location.column(),
        //         };
        //         self.imports.entry(full_name).or_default().push(location);
        //     }
        // }
    }
}
