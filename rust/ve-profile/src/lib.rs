#![forbid(unsafe_code)]
//! VE profiles over the kernel: evaluation, routes, countermodel search, order, units, risk,
//! readings and discourse.
mod discourse;
mod eval;
mod order;
mod readings;
mod risk;
mod route;
mod search;
mod units;

pub use discourse::{ELABORATED_DOCUMENT, elaborated_document_case};
#[cfg(feature = "bench-internals")]
#[doc(hidden)]
pub use eval::EvaluationKernel;
pub use eval::{Evaluation, TracedEvaluation, evaluate, evaluate_formula, evaluate_traced};
pub use order::order_case;
pub use readings::readings_evaluate_case;
pub use risk::{Range as RiskRange, evaluate_risk_condition, regenerate_risk_cells};
pub use route::{check_label, check_reading_binding, label_is_canonical};
pub use search::{
    CountermodelCheck, CountermodelProblem, SearchBounds, SearchResult, find_countermodel,
    find_countermodel_min, find_countermodel_with_nonvacuity, find_distinguishing_model,
    find_distinguishing_model_with_nonvacuity,
};
pub use units::quantity_case;
