#![forbid(unsafe_code)]
//! VE profiles over the kernel: evaluation, routes, countermodel search and order.
mod eval;
mod order;
mod route;
mod search;

#[cfg(feature = "bench-internals")]
#[doc(hidden)]
pub use eval::EvaluationKernel;
#[cfg(feature = "bench-internals")]
#[doc(hidden)]
pub use order::order_candidates;
pub use eval::{Evaluation, TracedEvaluation, evaluate, evaluate_formula, evaluate_traced};
pub use order::order_case;
pub use route::{check_label, check_reading_binding, label_is_canonical};
pub use search::{
    CandidateIterator, CountermodelCheck, CountermodelProblem, SearchBounds, SearchResult, find_countermodel,
    find_countermodel_min, find_countermodel_with_nonvacuity, find_distinguishing_model,
    find_distinguishing_model_with_nonvacuity,
};
