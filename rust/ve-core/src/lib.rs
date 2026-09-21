#![forbid(unsafe_code)]
//! Experimental VE v0 core. Checked values have private fields; raw indexed
//! syntax becomes a claim only through `Document::check` or `parse`.
mod ast;
mod environment;
mod eval;
mod model;
mod surface;
mod wire;

pub use ast::{Document, Formula, Term};
pub use environment::Environment;
pub use eval::{Evaluation, evaluate, evaluate_formula};
pub use model::FiniteModel;
pub use surface::{ParseResult, SourceNode, parse, parse_with_metadata, print_document};
pub use wire::{canonical_json, digest, loads_json};
use serde::Serialize;

pub const MAX_PACKAGE_BYTES: usize = 16 * 1024 * 1024;
pub const MAX_SOURCE_BYTES: usize = 64 * 1024;
pub const MAX_NODES: usize = 10_000;
pub const MAX_DEPTH: usize = 64;
pub const MAX_EVALUATIONS: u64 = 1_000_000;
pub const MAX_INDEX: u64 = (1 << 53) - 1;

#[derive(Clone, Debug, PartialEq, Eq, Serialize)]
pub struct Span {
    pub start: usize,
    pub end: usize,
    pub line: usize,
    pub column: usize,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize)]
pub struct Error {
    pub code: String,
    pub message: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub span: Option<Span>,
}
impl Error {
    pub fn new(code: &str, message: impl Into<String>) -> Self {
        Self { code: code.into(), message: message.into(), span: None }
    }
}
impl std::fmt::Display for Error {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}: {}", self.code, self.message)
    }
}
impl std::error::Error for Error {}
pub type Result<T> = std::result::Result<T, Error>;
pub(crate) fn error<T>(code: &str, message: impl Into<String>) -> Result<T> {
    Err(Error::new(code, message))
}
