#![forbid(unsafe_code)]
//! VE kernel: syntax, environments, finite models, the wire format, the evaluator core and the
//! dependency order. Checked values have private fields; raw indexed syntax becomes a claim only
//! through `Document::check` (or the surface crate's `parse`). `internal` serves the profile and
//! surface crates only; the `ve-core` facade does not re-export it.
mod ast;
mod environment;
mod graph;
#[doc(hidden)]
pub mod internal;
mod model;
mod semantics;
mod wire;

pub use ast::{Document, Edge, Formula, ReachKind, Term};
pub use environment::Environment;
pub use graph::dependency_order;
pub use model::FiniteModel;
pub use semantics::{Explanation, TraceBinding};
use serde::Serialize;
pub use wire::{canonical_json, digest, loads_json};

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
        Self {
            code: code.into(),
            message: message.into(),
            span: None,
        }
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
