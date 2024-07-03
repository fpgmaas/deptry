use pyo3::prelude::*;

#[pyclass]
#[derive(Clone, Debug)]
pub struct Location {
    #[pyo3(get, set)]
    pub file: String,
    #[pyo3(get, set)]
    pub line: Option<usize>,
    #[pyo3(get, set)]
    pub column: Option<usize>,
}

#[pymethods]
impl Location {
    #[new]
    #[pyo3(signature = (file, line=None, column=None))]
    fn new(file: String, line: Option<usize>, column: Option<usize>) -> Self {
        Self { file, line, column }
    }

    fn __repr__(&self) -> String {
        format!(
            "Location(file='{}', line={:?}, column={:?})",
            self.file, self.line, self.column
        )
    }
}
