//! The evaluator core (kernel, like Lean `VE.Semantics`; Python's is `ve.evaluate._Evaluator`):
//! `FiniteModel` decoding evaluates defined relations with it; profile `eval` and `search` drive it.
use crate::{
    Document, Edge, FiniteModel, Formula, MAX_EVALUATIONS, ReachKind, Result, Term, error,
};
use serde::Serialize;
use std::collections::{BTreeSet, HashMap};

type ClosureCache<'a> = HashMap<(&'a Edge, Vec<usize>), BTreeSet<(usize, usize)>>;

#[derive(Clone, Debug, Serialize, PartialEq, Eq)]
pub struct TraceBinding {
    pub debruijn_index: usize,
    pub sort: String,
    pub local_id: String,
}

#[derive(Clone, Debug, Serialize, PartialEq, Eq)]
pub struct Explanation {
    pub kind: &'static str,
    pub value: Option<bool>,
    pub bindings: Vec<TraceBinding>,
    pub detail: String,
    pub children: Vec<Explanation>,
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
    pub(crate) fn tick(&mut self) -> Result<()> {
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

    fn trace_node(&self, kind: &'static str, value: bool, context: &[(String, usize)],
                  detail: String, children: Vec<Explanation>) -> Explanation {
        Explanation {
            kind, value: Some(value),
            bindings: context.iter().rev().enumerate().map(|(index, (sort, id))| TraceBinding {
                debruijn_index: index, sort: sort.clone(), local_id: self.model.domains[sort][*id].clone(),
            }).collect(),
            detail, children,
        }
    }

    pub(crate) fn traced_formula(&mut self, f: &'a Formula, bindings: &mut Vec<usize>,
                      context: &mut Vec<(String, usize)>) -> Result<(bool, Explanation)> {
        // The atomic and Reach paths use the ordinary evaluator. This retains
        // exactly its ticks, closure cache, and short circuit behavior.
        let (kind, value, detail, children) = match f {
            Formula::Top => ("top", self.formula(f, bindings)?, String::new(), vec![]),
            Formula::Bottom => ("bottom", self.formula(f, bindings)?, String::new(), vec![]),
            Formula::Unary(p, t) => {
                let row = self.model.domains[&self.model_sort(p, 0)][self.term(t, bindings)].clone();
                ("unary", self.formula(f, bindings)?, format!("{p}('{}',)", row), vec![])
            }
            Formula::Binary(p, t, u) => {
                let left = self.model.domains[&self.model_sort(p, 0)][self.term(t, bindings)].clone();
                let right = self.model.domains[&self.model_sort(p, 1)][self.term(u, bindings)].clone();
                ("binary", self.formula(f, bindings)?, format!("{p}('{}', '{}')", left, right), vec![])
            }
            Formula::Atom(p, ts) => {
                let row = ts.iter().enumerate().map(|(i, t)| {
                    let sort = self.model_sort(p, i);
                    format!("'{}'", self.model.domains[&sort][self.term(t, bindings)])
                }).collect::<Vec<_>>();
                let tuple = if row.len() == 1 { format!("({},)", row[0]) }
                            else { format!("({})", row.join(", ")) };
                ("atom", self.formula(f, bindings)?, format!("{p}{tuple}"), vec![])
            }
            Formula::Reach(kind, _, t, u) => {
                let left = self.term(t, bindings);
                let right = self.term(u, bindings);
                let sort = self.model_sort_for_reach(f);
                let name = if matches!(kind, ReachKind::Star) { "star" } else { "plus" };
                let detail = format!("{name}: {} to {}; finite directed paths",
                    self.model.domains[&sort][left], self.model.domains[&sort][right]);
                ("reach", self.formula(f, bindings)?, detail, vec![])
            }
            Formula::Eq(t, u) => {
                let sort = self.model_sort_for_term(t, context);
                let left = &self.model.domains[&sort][self.term(t, bindings)];
                let right = &self.model.domains[&sort][self.term(u, bindings)];
                ("equality", self.formula(f, bindings)?, format!("{left} equals {right}"), vec![])
            }
            Formula::Not(body) => {
                self.tick()?;
                let (child_value, child) = self.traced_formula(body, bindings, context)?;
                ("not", !child_value, String::new(), vec![child])
            }
            Formula::And(left, right) | Formula::Or(left, right) | Formula::Implies(left, right) => {
                self.tick()?;
                let (lv, first) = self.traced_formula(left, bindings, context)?;
                let kind = match f { Formula::And(..) => "and", Formula::Or(..) => "or", _ => "implies" };
                if kind == "and" && !lv {
                    (kind, false, "right branch not needed".into(), vec![first])
                } else if kind == "or" && lv {
                    (kind, true, "right branch not needed".into(), vec![first])
                } else if kind == "implies" && !lv {
                    (kind, true, "vacuously true: antecedent is false".into(), vec![first])
                } else {
                    let (rv, second) = self.traced_formula(right, bindings, context)?;
                    (kind, if kind == "and" { lv && rv } else { rv }, String::new(), vec![first, second])
                }
            }
            Formula::Forall(sort, body) | Formula::Exists(sort, body) => {
                self.tick()?;
                let universal = matches!(f, Formula::Forall(..));
                let kind = if universal { "forall" } else { "exists" };
                let domain = &self.model.domains[sort];
                if domain.is_empty() {
                    let detail = if universal { "vacuously true: domain is empty" }
                                 else { "false: domain is empty" };
                    (kind, universal, detail.into(), vec![])
                } else {
                    let mut children = Vec::new();
                    let mut decisive = None;
                    for i in 0..domain.len() {
                        bindings.push(i);
                        context.push((sort.clone(), i));
                        let child = self.traced_formula(body, bindings, context);
                        context.pop(); bindings.pop();
                        let (value, trace) = child?;
                        children.push(trace);
                        if value != universal { decisive = Some(i); break; }
                    }
                    let value = if decisive.is_some() { !universal } else { universal };
                    let detail = match decisive {
                        Some(i) if universal => format!("counterexample {}", domain[i]),
                        Some(i) => format!("witness {}", domain[i]),
                        None if universal => "all entities checked".into(),
                        None => "no witness".into(),
                    };
                    (kind, value, detail, children)
                }
            }
        };
        Ok((value, self.trace_node(kind, value, context, detail, children)))
    }

    fn model_sort(&self, predicate: &str, position: usize) -> String {
        // The checked model retains the defining environment's signature.
        self.model.predicate_sort(predicate, position).to_owned()
    }

    fn model_sort_for_reach(&self, f: &Formula) -> String {
        match f {
            Formula::Reach(_, Edge::Body(sort, _), _, _) => sort.clone(),
            Formula::Reach(_, Edge::Named(name), _, _) => self.model_sort(name, 0),
            _ => unreachable!(),
        }
    }

    fn model_sort_for_term(&self, term: &Term, context: &[(String, usize)]) -> String {
        match term {
            Term::Var(i) => context[context.len() - 1 - *i as usize].0.clone(),
            Term::Const(name) => self.model.constant_sort(name).to_owned(),
        }
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
