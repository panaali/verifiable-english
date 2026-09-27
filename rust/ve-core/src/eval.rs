use crate::{
    Document, Edge, Error, FiniteModel, Formula, MAX_EVALUATIONS, ReachKind, Result, Term, error,
};
use serde::Serialize;
use std::collections::{BTreeSet, HashMap};

type ClosureCache<'a> = HashMap<(&'a Edge, Vec<usize>), BTreeSet<(usize, usize)>>;

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
    // Structural edge identity plus the entire captured context. Never shared
    // between models; plus/star reuse the same positive closure, without seeding
    // diagonal edges. Borrowing avoids cloning nested edge ASTs into the cache.
    closures: ClosureCache<'a>,
}
impl<'a> Evaluator<'a> {
    pub fn new(model: &'a FiniteModel, maximum: u64) -> Self {
        Self {
            model,
            maximum,
            work: 0,
            closures: HashMap::new(),
        }
    }
    pub fn clear_closures(&mut self) {
        self.closures.clear();
    }
    fn tick(&mut self) -> Result<()> {
        if self.work >= self.maximum {
            return error("ResourceLimit", "evaluation budget exhausted");
        }
        self.work += 1;
        Ok(())
    }
    fn term(&self, t: &Term, bindings: &[usize]) -> usize {
        match t {
            Term::Var(i) => bindings[bindings.len() - 1 - *i as usize],
            Term::Const(n) => self.model.constants[n],
        }
    }
    pub fn formula(&mut self, f: &'a Formula, bindings: &mut Vec<usize>) -> Result<bool> {
        self.tick()?;
        Ok(match f {
            Formula::Top => true,
            Formula::Bottom => false,
            Formula::Unary(p, t) => {
                self.model.relations[p].contains([self.term(t, bindings)].as_slice())
            }
            Formula::Binary(p, t, u) => self.model.relations[p]
                .contains([self.term(t, bindings), self.term(u, bindings)].as_slice()),
            Formula::Atom(p, ts) => self.model.relations[p].contains(
                &ts.iter().map(|t| self.term(t, bindings)).collect::<Vec<_>>()),
            Formula::Reach(kind, edge, t, u) => {
                let key = (edge, bindings.clone());
                if !self.closures.contains_key(&key) {
                    let mut edges = BTreeSet::new();
                    let domain: Vec<usize> = match edge {
                        Edge::Named(p) => {
                            let mut active = BTreeSet::new();
                            for row in &self.model.relations[p] {
                                self.tick()?;
                                edges.insert((row[0], row[1]));
                                active.extend([row[0], row[1]]);
                            }
                            active.into_iter().collect()
                        }
                        Edge::Body(s, body) => {
                            let domain: Vec<_> = (0..self.model.domains[s].len()).collect();
                            for &source in &domain {
                                for &destination in &domain {
                                    let outer_len = bindings.len();
                                    bindings.extend([source, destination]);
                                    let value = self.formula(body, bindings);
                                    bindings.truncate(outer_len);
                                    if value? {
                                        edges.insert((source, destination));
                                    }
                                }
                            }
                            domain
                        }
                    };
                    // Materialize each pivot's incoming/outgoing sets before
                    // adding paths. Charge edge visits and Warshall work, as in
                    // Python, so dense/nested closures respect the work limit.
                    for &pivot in &domain {
                        let mut incoming = Vec::new();
                        let mut outgoing = Vec::new();
                        for &x in &domain {
                            self.tick()?;
                            if edges.contains(&(x, pivot)) {
                                incoming.push(x);
                            }
                            if edges.contains(&(pivot, x)) {
                                outgoing.push(x);
                            }
                        }
                        for &x in &incoming {
                            for &y in &outgoing {
                                self.tick()?;
                                edges.insert((x, y));
                            }
                        }
                    }
                    self.closures.insert(key.clone(), edges);
                }
                let left = self.term(t, bindings);
                let right = self.term(u, bindings);
                (matches!(kind, ReachKind::Star) && left == right)
                    || self.closures[&key].contains(&(left, right))
            }
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
