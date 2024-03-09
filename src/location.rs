
#[derive(Debug)]
#[derive(Clone)]
pub struct Location {
    file: String,
    range: usize,
    col_offset: usize,
}
