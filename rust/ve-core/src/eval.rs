use crate::{Document, Error, FiniteModel, Formula, MAX_EVALUATIONS, Result, Term, error};
use serde::Serialize;

#[derive(Clone, Debug, Serialize)]
pub struct Evaluation {
    pub status: &'static str,
    pub value: Option<bool>,
    pub evaluations: u64,
}

pub(crate) struct Evaluator<'a> {
    pub model: &'a FiniteModel,
    pub maximum: u64,
    pub work: u64,
}
impl Evaluator<'_> {
    fn term(&self, t: &Term, bindings: &[usize]) -> usize {
        match t {
            Term::Var(i) => bindings[bindings.len() - 1 - *i as usize],
            Term::Const(n) => self.model.constants[n],
        }
    }
    pub fn formula(&mut self, f: &Formula, bindings: &mut Vec<usize>) -> Result<bool> {
        if self.work >= self.maximum {
            return error("ResourceLimit", "formula-node evaluation budget exhausted");
        }
        self.work += 1;
        Ok(match f {
            Formula::Top => true,
            Formula::Bottom => false,
            Formula::Unary(p, t) => {
                self.model.relations[p].contains([self.term(t, bindings)].as_slice())
            }
            Formula::Binary(p, t, u) => self.model.relations[p]
                .contains([self.term(t, bindings), self.term(u, bindings)].as_slice()),
            Formula::Eq(t, u) => self.term(t, bindings) == self.term(u, bindings),
            Formula::Not(a) => !self.formula(a, bindings)?,
            Formula::And(a, b) => self.formula(a, bindings)? && self.formula(b, bindings)?,
            Formula::Or(a, b) => self.formula(a, bindings)? || self.formula(b, bindings)?,
            Formula::Implies(a, b) => !self.formula(a, bindings)? || self.formula(b, bindings)?,
            Formula::Forall(s, a) | Formula::Exists(s, a) => {
                let universal = matches!(f, Formula::Forall(..));
                for i in 0..self.model.domains[s].len() {
                    bindings.push(i);
                    let result = self.formula(a, bindings);
                    bindings.pop();
                    if result? != universal {
                        return Ok(!universal);
                    }
                }
                universal
            }
        })
    }
}
pub(crate) fn compatible(doc: &Document, model: &FiniteModel, maximum: u64) -> Result<()> {
    if doc.environment_id() != model.environment_id() {
        return error("InvalidModel", "model and document environments differ");
    }
    if maximum > MAX_EVALUATIONS {
        return error("ResourceLimit", "budget exceeds 1,000,000 evaluations");
    }
    Ok(())
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
    let mut ev = Evaluator {
        model,
        maximum,
        work: 0,
    };
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
        evaluations: ev.work,
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
