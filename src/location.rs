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
    pub fn new(file: String, line: Option<usize>, column: Option<usize>) -> Self {
        Location { file, line, column }
    }

    fn __repr__(&self) -> PyResult<String> {
        Ok(format!(
            "Location(file='{}', line={:?}, column={:?})",
            self.file, self.line, self.column
        ))
    }
}
