use ruff_python_ast::visitor::{walk_stmt, Visitor};
use ruff_python_ast::{self, Expr, ExprAttribute, ExprName, Stmt, StmtIf, StmtImportFrom};
use ruff_text_size::TextRange;
use std::collections::HashMap;

#[derive(Debug, Clone)]
pub struct ImportVisitor {
    imports: HashMap<String, Vec<TextRange>>,
    has_future_annotations: bool,
}

impl ImportVisitor {
    pub fn new() -> Self {
        Self {
            imports: HashMap::new(),
            has_future_annotations: false,
        }
    }

    pub fn get_imports(self) -> HashMap<String, Vec<TextRange>> {
        self.imports
    }
}

impl<'a> Visitor<'a> for ImportVisitor {
    fn visit_stmt(&mut self, stmt: &'a Stmt) {
        match stmt {
            Stmt::Import(import_stmt) => {
                for alias in &import_stmt.names {
                    let top_level_module = get_top_level_module_name(&alias.name);
                    self.imports
                        .entry(top_level_module)
                        .or_default()
                        .push(alias.range);
                }
            }
            Stmt::ImportFrom(import_from_stmt) => {
                if let Some(module) = &import_from_stmt.module {
                    if import_from_stmt.level == Some(0) {
                        if is_future_annotations_import(module.as_str(), import_from_stmt) {
                            self.has_future_annotations = true;
                        }

                        self.imports
                            .entry(get_top_level_module_name(module.as_str()))
                            .or_default()
                            .push(import_from_stmt.range);
                    }
                }
            }
            Stmt::If(if_stmt) if is_typing_only_block(self.has_future_annotations, if_stmt) => {
                // Avoid parsing imports that are only evaluated by type checkers.
            }
            _ => walk_stmt(self, stmt), // Delegate other statements to walk_stmt
        }
    }
}

/// Extracts the top-level module name from a potentially nested module path.
/// e.g. when a `module_name` is `foo.bar`, this returns `foo`.
fn get_top_level_module_name(module_name: &str) -> String {
    module_name
        .split('.')
        .next()
        .unwrap_or(module_name)
        .to_owned()
}

/// Checks if the import is a `from __future__ import annotations` one.
fn is_future_annotations_import(module: &str, import_from_stmt: &StmtImportFrom) -> bool {
    return module == "__future__"
        && import_from_stmt
            .names
            .iter()
            .any(|alias| alias.name.as_str() == "annotations");
}

/// Checks if we are in a block that will only be evaluated by type checkers, in accordance with
/// <https://peps.python.org/pep-0563/>. If no `__future__.annotations` import is made, a block using `TYPE_CHECKING`
/// will be evaluated at runtime, so we should not consider that this is a typing only block in that case.
fn is_typing_only_block(has_future_annotations: bool, if_stmt: &StmtIf) -> bool {
    if has_future_annotations {
        match &if_stmt.test.as_ref() {
            Expr::Attribute(ExprAttribute { value, attr, .. }) => {
                if let Expr::Name(ExprName { id, .. }) = value.as_ref() {
                    if id.as_str() == "typing" && attr.as_str() == "TYPE_CHECKING" {
                        return true;
                    }
                }
            }
            Expr::Name(ExprName { id, .. }) => {
                if id == "TYPE_CHECKING" {
                    return true;
                }
            }
            _ => (),
        }
    }

    false
}
