#![forbid(unsafe_code)]
//! Experimental VE v0 and closure@0 core. Checked values have private fields; raw indexed
//! syntax becomes a claim only through `Document::check` or `parse`.
//!
//! A facade over the kernel, profile and surface crates: it re-exports exactly the public API
//! the single `ve-core` crate had, and none of `ve_kernel::internal`.
pub use ve_kernel::{
    Document, Edge, Environment, Error, FiniteModel, Formula, MAX_DEPTH, MAX_EVALUATIONS,
    MAX_INDEX, MAX_NODES, MAX_PACKAGE_BYTES, MAX_SOURCE_BYTES, ReachKind, Result, Span, Term,
    canonical_json, dependency_order, digest, loads_json,
};
#[cfg(feature = "bench-internals")]
#[doc(hidden)]
pub use ve_profile::EvaluationKernel;
pub use ve_profile::{
    CountermodelCheck, CountermodelProblem, ELABORATED_DOCUMENT, Evaluation, RiskRange,
    SearchBounds, SearchResult, TracedEvaluation, check_label, check_reading_binding,
    elaborated_document_case, evaluate, evaluate_formula, evaluate_risk_condition,
    evaluate_traced, find_countermodel, find_countermodel_min, find_countermodel_with_nonvacuity,
    find_distinguishing_model, find_distinguishing_model_with_nonvacuity, label_is_canonical,
    order_case, quantity_case, readings_evaluate_case, regenerate_risk_cells,
};
pub use ve_surface::{ParseResult, SourceNode, parse, parse_with_metadata, print_document};
