#![forbid(unsafe_code)]
//! VE strict surface notation over the kernel: the parser and the canonical printer.
mod surface;

pub use surface::{ParseResult, SourceNode, parse, parse_with_metadata, print_document};
