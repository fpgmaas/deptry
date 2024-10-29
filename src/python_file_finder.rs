use ignore::types::{Types, TypesBuilder};
use ignore::{DirEntry, Walk, WalkBuilder};
use path_slash::PathExt;
use pyo3::types::PyList;
use pyo3::{pyfunction, PyObject, PyResult, Python};
use regex::Regex;
use std::path::PathBuf;

#[pyfunction]
#[pyo3(signature = (directories, exclude, extend_exclude, using_default_exclude, ignore_notebooks=false))]
pub fn find_python_files(
    py: Python,
    directories: Vec<PathBuf>,
    exclude: Vec<String>,
    extend_exclude: Vec<String>,
    using_default_exclude: bool,
    ignore_notebooks: bool,
) -> PyResult<PyObject> {
    let mut unique_directories = directories;
    unique_directories.dedup();

    let python_files: Vec<_> = build_walker(
        unique_directories,
        [exclude, extend_exclude].concat(),
        using_default_exclude,
        ignore_notebooks,
    )
    .flatten()
    .filter(|entry| entry.path().is_file())
    .map(|entry| {
        entry
            .path()
            .to_string_lossy()
            .strip_prefix("./")
            .unwrap_or(&entry.path().to_string_lossy())
            .to_owned()
    })
    .collect();

    Ok(PyList::new_bound(py, &python_files).into())
}

fn build_walker(
    directories: Vec<PathBuf>,
    excluded_patterns: Vec<String>,
    use_git_ignore: bool,
    ignore_notebooks: bool,
) -> Walk {
    let (first_directory, additional_directories) = directories.split_first().unwrap();

    let mut walk_builder = WalkBuilder::new(first_directory);
    for path in additional_directories {
        walk_builder.add(path);
    }

    let re: Option<Regex> = if excluded_patterns.is_empty() {
        None
    } else {
        Some(Regex::new(format!(r"^({})", excluded_patterns.join("|")).as_str()).unwrap())
    };

    walk_builder
        .types(build_types(ignore_notebooks).unwrap())
        .standard_filters(use_git_ignore)
        .hidden(false)
        .filter_entry(move |entry| entry_satisfies_predicate(entry, re.as_ref()))
        .build()
}

fn build_types(ignore_notebooks: bool) -> Result<Types, ignore::Error> {
    let mut types_builder = TypesBuilder::new();
    types_builder.add("python", "*.py").unwrap();
    types_builder.select("python");

    if !ignore_notebooks {
        types_builder.add("jupyter", "*.ipynb").unwrap();
        types_builder.select("jupyter");
    }

    types_builder.build()
}

fn entry_satisfies_predicate(entry: &DirEntry, regex: Option<&Regex>) -> bool {
    if regex.is_none() {
        return true;
    }

    let path_str = entry.path().to_slash_lossy();
    !regex
        .unwrap()
        .is_match(path_str.strip_prefix("./").unwrap_or(&path_str).as_ref())
}
