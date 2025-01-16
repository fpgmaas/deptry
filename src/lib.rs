use pyo3::prelude::*;

mod file_utils;
mod imports;
mod location;
mod python_file_finder;
mod visitor;

use location::Location;

#[pymodule]
fn rust(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    pyo3_log::init(); // Initialize logging to forward to Python's logger

    m.add_function(wrap_pyfunction!(imports::py::get_imports_from_py_files, m)?)?;
    m.add_function(wrap_pyfunction!(
        imports::ipynb::get_imports_from_ipynb_files,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(python_file_finder::find_python_files, m)?)?;
    m.add_class::<Location>()?;
    Ok(())
}
