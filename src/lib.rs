// lib.rs

use pyo3::prelude::*;

mod file_utils;
mod imports;
mod location;
mod visitor;

use location::Location;

#[pymodule]
fn rust(_py: Python, m: &PyModule) -> PyResult<()> {
    pyo3_log::init(); // Initialize logging to forward to Python's logger

    m.add_function(wrap_pyfunction!(imports::get_imports_from_py_files, m)?)?;
    m.add_function(wrap_pyfunction!(imports::get_imports_from_py_file, m)?)?;
    m.add_class::<Location>()?;
    Ok(())
}
