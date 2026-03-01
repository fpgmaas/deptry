use pyo3::prelude::*;

#[pyclass(skip_from_py_object)]
#[derive(Clone, Debug)]
pub struct Location {
    #[pyo3(get, set)]
    pub file: String,
    #[pyo3(get, set)]
    pub line: Option<usize>,
    #[pyo3(get, set)]
    pub column: Option<usize>,
    #[pyo3(get, set)]
    pub ignored_rule_codes: Vec<String>,
}

#[pymethods]
impl Location {
    #[new]
    #[pyo3(signature = (file, line=None, column=None, ignored_rule_codes=vec![]))]
    fn new(
        file: String,
        line: Option<usize>,
        column: Option<usize>,
        ignored_rule_codes: Vec<String>,
    ) -> Self {
        Self {
            file,
            line,
            column,
            ignored_rule_codes,
        }
    }

    fn __repr__(&self) -> String {
        format!(
            "Location(file='{}', line={:?}, column={:?}, ignored_rule_codes={:?})",
            self.file, self.line, self.column, self.ignored_rule_codes
        )
    }
}
