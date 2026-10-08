#![forbid(unsafe_code)]
//! Experimental VE v0 and closure@0 core. Checked values have private fields; raw indexed
//! syntax becomes a claim only through `Document::check` or the wire decoders.
//!
//! A facade over the kernel and profile crates: it re-exports their public API and none of
//! `ve_kernel::internal`. Rust reads no VE source text: Python parses and prints, and Lean
//! checks (docs/LEAN-FIRST-PLAN.md, batch 15b).
pub use ve_kernel::{
    Document, Edge, Environment, Error, FiniteModel, Formula, MAX_DEPTH, MAX_EVALUATIONS,
    MAX_INDEX, MAX_NODES, MAX_PACKAGE_BYTES, MAX_SOURCE_BYTES, ReachKind, Result, Span, Term,
    canonical_json, dependency_order, digest, loads_json,
};
#[cfg(feature = "bench-internals")]
#[doc(hidden)]
pub use ve_profile::{EvaluationKernel, order_candidates};
pub use ve_profile::{
    CandidateIterator, CountermodelCheck, CountermodelProblem, Evaluation, SearchBounds, SearchResult,
    TracedEvaluation, evaluate, evaluate_formula, evaluate_traced, find_countermodel,
    find_countermodel_min, find_countermodel_with_nonvacuity, find_distinguishing_model,
    find_distinguishing_model_with_nonvacuity, order_case,
};
