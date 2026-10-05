use ve_kernel::{
    Document, Error, Explanation, FiniteModel, Formula, Result,
    internal::{Evaluator, compatible},
};
use serde::Serialize;

#[derive(Clone, Debug, Serialize)]
pub struct Evaluation {
    pub status: &'static str,
    pub value: Option<bool>,
    pub evaluations: u64,
}

#[derive(Clone, Debug, Serialize)]
pub struct TracedEvaluation {
    pub status: &'static str,
    pub value: Option<bool>,
    pub evaluations: u64,
    pub explanation: Explanation,
}

fn run(
    doc: &Document,
    model: &FiniteModel,
    formulas: &[Formula],
    maximum: u64,
) -> Result<Evaluation> {
    compatible(doc, model, maximum)?;
    Ok(run_formulas(model, formulas, maximum))
}
fn run_formulas(model: &FiniteModel, formulas: &[Formula], maximum: u64) -> Evaluation {
    let mut ev = Evaluator::new(model, maximum);
    let mut result = Some(true);
    for formula in formulas {
        match ev.formula(formula, &mut Vec::new()) {
            Ok(true) => {}
            Ok(false) => {
                result = Some(false);
                break;
            }
            Err(_) => {
                result = None;
                break;
            }
        }
    }
    Evaluation {
        status: match result {
            Some(true) => "Satisfied",
            Some(false) => "Violated",
            None => "ResourceLimit",
        },
        value: result,
        evaluations: ev.work(),
    }
}

/// Benchmark-only prepared call: compatibility and selection occur outside
/// the timed kernel. Private fields still prevent unchecked evaluator inputs.
#[cfg(feature = "bench-internals")]
pub struct EvaluationKernel<'a> {
    model: &'a FiniteModel,
    formula: &'a Formula,
    maximum: u64,
}
#[cfg(feature = "bench-internals")]
impl<'a> EvaluationKernel<'a> {
    pub fn new(
        doc: &'a Document,
        index: usize,
        model: &'a FiniteModel,
        maximum: u64,
    ) -> Result<Self> {
        compatible(doc, model, maximum)?;
        let formula = doc
            .formulas()
            .get(index)
            .ok_or_else(|| Error::new("InvalidInput", "formula index out of range"))?;
        Ok(Self {
            model,
            formula,
            maximum,
        })
    }
    pub fn evaluate(&self) -> Evaluation {
        run_formulas(self.model, std::slice::from_ref(self.formula), self.maximum)
    }
}
pub fn evaluate(doc: &Document, model: &FiniteModel, maximum: u64) -> Result<Evaluation> {
    run(doc, model, doc.formulas(), maximum)
}

pub fn evaluate_traced(doc: &Document, model: &FiniteModel, maximum: u64,
                       max_trace_nodes: u64) -> Result<TracedEvaluation> {
    compatible(doc, model, maximum)?;
    let budget = maximum.min(max_trace_nodes);
    let mut ev = Evaluator::new(model, budget);
    let mut children = Vec::new();
    let mut status = "Satisfied";
    let mut value = Some(true);
    let mut detail = "all statements satisfied".to_owned();
    for (index, formula) in doc.formulas().iter().enumerate() {
        match ev.traced_formula(formula, &mut Vec::new(), &mut Vec::new()) {
            Ok((true, child)) => children.push(child),
            Ok((false, child)) => {
                children.push(child);
                status = "Violated";
                value = Some(false);
                detail = format!("statement {} violated", index + 1);
                break;
            }
            Err(_) => {
                status = "ResourceLimit";
                value = None;
                detail = if max_trace_nodes < maximum {
                    "trace-node budget exhausted".to_owned()
                } else {
                    "formula-node evaluation budget exhausted".to_owned()
                };
                break;
            }
        }
    }
    let explanation = Explanation {
        kind: if value.is_some() { "document" } else { "resource_limit" },
        value, bindings: vec![], detail, children,
    };
    Ok(TracedEvaluation { status, value, evaluations: ev.work(), explanation })
}
pub fn evaluate_formula(
    doc: &Document,
    index: usize,
    model: &FiniteModel,
    maximum: u64,
) -> Result<Evaluation> {
    let f = doc
        .formulas()
        .get(index)
        .ok_or_else(|| Error::new("InvalidInput", "formula index out of range"))?;
    run(doc, model, std::slice::from_ref(f), maximum)
}
