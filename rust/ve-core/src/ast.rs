use crate::{
    Environment, Error, MAX_DEPTH, MAX_INDEX, MAX_NODES, Result, digest, error, loads_json,
};
use serde_json::{Value, json};

#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub enum Term {
    Var(u64),
    Const(String),
}
/// A directed edge: Body binds source then destination (nearest-first 1, 0).
#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub enum Edge {
    Named(String),
    Body(String, Box<Formula>),
}
#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub enum ReachKind {
    Plus,
    Star,
    /// Raw wire value retained until the complete AST has been decoded.
    Invalid(String),
}
impl ReachKind {
    fn as_str(&self) -> &str {
        match self {
            Self::Plus => "plus",
            Self::Star => "star",
            Self::Invalid(s) => s,
        }
    }
}
#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub enum Formula {
    Top,
    Bottom,
    Unary(String, Term),
    Binary(String, Term, Term),
    Reach(ReachKind, Edge, Term, Term),
    Eq(Term, Term),
    Not(Box<Formula>),
    And(Box<Formula>, Box<Formula>),
    Or(Box<Formula>, Box<Formula>),
    Implies(Box<Formula>, Box<Formula>),
    Forall(String, Box<Formula>),
    Exists(String, Box<Formula>),
}
impl Term {
    pub fn to_value(&self) -> Value {
        match self {
            Self::Var(i) => json!(["var", i]),
            Self::Const(n) => json!(["const", n]),
        }
    }
}
impl Formula {
    pub fn to_value(&self) -> Value {
        match self {
            Self::Top => json!(["top"]),
            Self::Bottom => json!(["bottom"]),
            Self::Unary(p, t) => json!(["unary", p, t.to_value()]),
            Self::Binary(p, t, u) => json!(["binary", p, t.to_value(), u.to_value()]),
            Self::Reach(k, e, t, u) => {
                let edge = match e {
                    Edge::Named(p) => json!(["named", p]),
                    Edge::Body(s, f) => json!(["body", s, f.to_value()]),
                };
                json!(["reach", k.as_str(), edge, t.to_value(), u.to_value()])
            }
            Self::Eq(t, u) => json!(["eq", t.to_value(), u.to_value()]),
            Self::Not(f) => json!(["not", f.to_value()]),
            Self::And(a, b) | Self::Or(a, b) | Self::Implies(a, b) => json!([
                match self {
                    Self::And(..) => "and",
                    Self::Or(..) => "or",
                    _ => "implies",
                },
                a.to_value(),
                b.to_value()
            ]),
            Self::Forall(s, f) | Self::Exists(s, f) => json!([
                if matches!(self, Self::Forall(..)) {
                    "forall"
                } else {
                    "exists"
                },
                s,
                f.to_value()
            ]),
        }
    }
    pub(crate) fn predicates(&self, result: &mut std::collections::BTreeSet<String>) {
        match self {
            Self::Unary(p, _) | Self::Binary(p, _, _) => {
                result.insert(p.clone());
            }
            Self::Reach(_, Edge::Named(p), _, _) => {
                result.insert(p.clone());
            }
            Self::Reach(_, Edge::Body(_, f), _, _) => f.predicates(result),
            Self::Not(a) | Self::Forall(_, a) | Self::Exists(_, a) => a.predicates(result),
            Self::And(a, b) | Self::Or(a, b) | Self::Implies(a, b) => {
                a.predicates(result);
                b.predicates(result);
            }
            _ => {}
        }
    }
}
/// Extrinsically typed, nonempty, closed indexed AST bound to a full environment.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Document {
    formulas: Vec<Formula>,
    environment_id: String,
    identity_version: String,
}
impl Document {
    pub fn check(env: &Environment, formulas: Vec<Formula>) -> Result<Self> {
        if env.order() {
            return error("UnsupportedProfile", "use the order AST route for order@0");
        }
        if formulas.is_empty() {
            return error("SyntaxError", "document must be nonempty");
        }
        let mut checker = Checker { env, nodes: 0 };
        for f in &formulas {
            checker.formula(f, &mut Vec::new(), 1)?;
        }
        Ok(Self {
            formulas,
            environment_id: env.environment_id().into(),
            identity_version: env.identity_version(),
        })
    }
    pub fn from_json(env: &Environment, bytes: &[u8]) -> Result<Self> {
        Self::from_value(env, &loads_json(bytes)?)
    }
    pub fn from_value(env: &Environment, data: &Value) -> Result<Self> {
        let a = data
            .as_array()
            .ok_or_else(|| Error::new("SyntaxError", "document must be an array"))?;
        let mut decoder = AstDecoder { nodes: 0 };
        let formulas = a
            .iter()
            .map(|v| decoder.formula(v, 1))
            .collect::<Result<_>>()?;
        Self::check(env, formulas)
    }
    pub fn formulas(&self) -> &[Formula] {
        &self.formulas
    }
    pub fn environment_id(&self) -> &str {
        &self.environment_id
    }
    pub fn to_value(&self) -> Value {
        Value::Array(self.formulas.iter().map(Formula::to_value).collect())
    }
    pub fn meaning_id(&self) -> Result<String> {
        digest(
            &format!("ve-meaning-{}\n", self.identity_version),
            &json!({"environment_id":self.environment_id,"ast":self.to_value()}),
        )
    }
    pub fn formula_meaning_id(&self, index: usize) -> Result<String> {
        let f = self
            .formulas
            .get(index)
            .ok_or_else(|| Error::new("InvalidInput", "formula index out of range"))?;
        digest(
            &format!("ve-meaning-{}\n", self.identity_version),
            &json!({"environment_id":self.environment_id,"ast":f.to_value()}),
        )
    }
    pub(crate) fn belongs_to(&self, env: &Environment) -> Result<()> {
        if self.environment_id != env.environment_id() {
            return error(
                "TypeMismatch",
                "document belongs to a different environment",
            );
        }
        Ok(())
    }
}
struct Checker<'a> {
    env: &'a Environment,
    nodes: usize,
}
impl Checker<'_> {
    fn tick(&mut self) -> Result<()> {
        self.nodes += 1;
        if self.nodes > MAX_NODES {
            error("ResourceLimit", "AST exceeds 10,000 nodes")
        } else {
            Ok(())
        }
    }
    fn term(&mut self, t: &Term, context: &[String]) -> Result<String> {
        self.tick()?;
        match t {
            Term::Var(i) => {
                if *i > MAX_INDEX || *i >= context.len() as u64 {
                    return error("UnboundVariable", "variable index outside scope");
                }
                Ok(context[context.len() - 1 - *i as usize].clone())
            }
            Term::Const(c) => self
                .env
                .constants
                .get(c)
                .cloned()
                .ok_or_else(|| Error::new("UnknownSymbol", format!("unknown constant {c:?}"))),
        }
    }
    fn formula(&mut self, f: &Formula, context: &mut Vec<String>, depth: usize) -> Result<()> {
        self.tick()?;
        if depth > MAX_DEPTH {
            return error("ResourceLimit", "formula exceeds 64 nesting levels");
        }
        match f {
            Formula::Top | Formula::Bottom => {}
            Formula::Unary(p, t) | Formula::Binary(p, t, _) => {
                let signature = self
                    .env
                    .predicates
                    .get(p)
                    .ok_or_else(|| Error::new("UnknownSymbol", format!("unknown predicate {p:?}")))?
                    .clone();
                let terms = match f {
                    Formula::Binary(_, _, u) => vec![t, u],
                    _ => vec![t],
                };
                if signature.len() != terms.len() {
                    return error("TypeMismatch", "predicate arity mismatch");
                }
                let actual: Vec<_> = terms
                    .iter()
                    .map(|t| self.term(t, context))
                    .collect::<Result<_>>()?;
                if actual != signature {
                    return error("TypeMismatch", "predicate argument sort mismatch");
                }
            }
            Formula::Eq(a, b) => {
                if self.term(a, context)? != self.term(b, context)? {
                    return error("TypeMismatch", "equality requires one sort");
                }
            }
            Formula::Reach(kind, edge, left, right) => {
                if !self.env.closure() {
                    return error("UnsupportedProfile", "Reach requires closure@0");
                }
                if matches!(kind, ReachKind::Invalid(_)) {
                    return error("TypeMismatch", "Reach kind must be plus or star");
                }
                let sort = match edge {
                    Edge::Named(p) => {
                        let args = self.env.predicates.get(p).ok_or_else(|| {
                            Error::new("UnknownSymbol", "unknown closure relation")
                        })?;
                        if args.len() != 2 || args[0] != args[1] {
                            return error(
                                "TypeMismatch",
                                "closure requires a homogeneous binary relation",
                            );
                        }
                        args[0].clone()
                    }
                    Edge::Body(s, f) => {
                        if !self.env.sorts.contains(s) {
                            return error("UnknownSymbol", "unknown closure sort");
                        }
                        context.extend([s.clone(), s.clone()]);
                        self.formula(f, context, depth + 1)?;
                        context.truncate(context.len() - 2);
                        s.clone()
                    }
                };
                if self.term(left, context)? != sort || self.term(right, context)? != sort {
                    return error(
                        "TypeMismatch",
                        "closure endpoints require the edge sort in the outer context",
                    );
                }
            }
            Formula::Not(a) => self.formula(a, context, depth + 1)?,
            Formula::And(a, b) | Formula::Or(a, b) | Formula::Implies(a, b) => {
                self.formula(a, context, depth + 1)?;
                self.formula(b, context, depth + 1)?;
            }
            Formula::Forall(s, a) | Formula::Exists(s, a) => {
                if !self.env.sorts.contains(s) {
                    return error("UnknownSymbol", "unknown binder sort");
                }
                context.push(s.clone());
                self.formula(a, context, depth + 1)?;
                context.pop();
            }
        }
        Ok(())
    }
}
/// A definition body: one decoded formula, checked in the argument context
/// (index 0 is the last argument) over an environment below the definition.
pub(crate) fn decode_formula(v: &Value) -> Result<Formula> {
    AstDecoder { nodes: 0 }.formula(v, 1)
}
pub(crate) fn check_in_context(env: &Environment, f: &Formula, context: &[String]) -> Result<()> {
    Checker { env, nodes: 0 }.formula(f, &mut context.to_vec(), 1)
}
pub(crate) fn has_reach(f: &Formula) -> bool {
    match f {
        Formula::Reach(..) => true,
        Formula::Not(a) | Formula::Forall(_, a) | Formula::Exists(_, a) => has_reach(a),
        Formula::And(a, b) | Formula::Or(a, b) | Formula::Implies(a, b) => has_reach(a) || has_reach(b),
        _ => false,
    }
}
struct AstDecoder {
    nodes: usize,
}
impl AstDecoder {
    fn symbol(v: &Value) -> String {
        // Python decodes the entire raw AST before checking symbol types/names.
        // The empty name cannot be declared, so a non-string remains rejected
        // by Checker at its original position after structural decoding succeeds.
        v.as_str().unwrap_or("").into()
    }
    fn node<'a>(&mut self, v: &'a Value, depth: usize, term: bool) -> Result<&'a [Value]> {
        self.nodes += 1;
        if self.nodes > MAX_NODES || depth > MAX_DEPTH + usize::from(term) {
            return error("ResourceLimit", "AST depth or node limit");
        }
        v.as_array()
            .filter(|a| !a.is_empty() && a[0].is_string())
            .map(Vec::as_slice)
            .ok_or_else(|| Error::new("SyntaxError", "expected tagged AST array"))
    }
    fn term(&mut self, v: &Value, depth: usize) -> Result<Term> {
        let a = self.node(v, depth, true)?;
        match a[0].as_str().unwrap() {
            "var" if a.len() == 2 => a[1]
                .as_u64()
                .filter(|n| *n <= MAX_INDEX)
                .map(Term::Var)
                .ok_or_else(|| {
                    Error::new(
                        "UnboundVariable",
                        "index must be a bounded nonnegative integer",
                    )
                }),
            "const" if a.len() == 2 => Ok(Term::Const(Self::symbol(&a[1]))),
            _ => error("SyntaxError", "invalid term tag or arity"),
        }
    }
    fn formula(&mut self, v: &Value, depth: usize) -> Result<Formula> {
        let a = self.node(v, depth, false)?;
        let tag = a[0].as_str().unwrap();
        let arity = crate::wire::formula_tag_arity(tag);
        if a.len() != arity {
            return error("SyntaxError", "invalid formula tag or arity");
        }
        Ok(match tag {
            "top" => Formula::Top,
            "bottom" => Formula::Bottom,
            "unary" => Formula::Unary(Self::symbol(&a[1]), self.term(&a[2], depth + 1)?),
            "binary" => Formula::Binary(
                Self::symbol(&a[1]),
                self.term(&a[2], depth + 1)?,
                self.term(&a[3], depth + 1)?,
            ),
            "eq" => Formula::Eq(self.term(&a[1], depth + 1)?, self.term(&a[2], depth + 1)?),
            "reach" => {
                let edge = a[2].as_array().ok_or_else(|| {
                    Error::new("SyntaxError", "Reach edge must be a tagged array")
                })?;
                let edge = match (edge.first().and_then(Value::as_str), edge.len()) {
                    (Some("named"), 2) => Edge::Named(Self::symbol(&edge[1])),
                    (Some("body"), 3) => Edge::Body(
                        Self::symbol(&edge[1]),
                        Box::new(self.formula(&edge[2], depth + 1)?),
                    ),
                    _ => return error("SyntaxError", "invalid Reach edge tag or arity"),
                };
                let left = self.term(&a[3], depth + 1)?;
                let right = self.term(&a[4], depth + 1)?;
                let kind = match a[1].as_str() {
                    Some("plus") => ReachKind::Plus,
                    Some("star") => ReachKind::Star,
                    _ => ReachKind::Invalid(Self::symbol(&a[1])),
                };
                Formula::Reach(kind, edge, left, right)
            }
            "not" => Formula::Not(Box::new(self.formula(&a[1], depth + 1)?)),
            "and" | "or" | "implies" => {
                let left = Box::new(self.formula(&a[1], depth + 1)?);
                let right = Box::new(self.formula(&a[2], depth + 1)?);
                match tag {
                    "and" => Formula::And(left, right),
                    "or" => Formula::Or(left, right),
                    _ => Formula::Implies(left, right),
                }
            }
            "forall" | "exists" => {
                let sort = Self::symbol(&a[1]);
                let body = Box::new(self.formula(&a[2], depth + 1)?);
                if tag == "forall" {
                    Formula::Forall(sort, body)
                } else {
                    Formula::Exists(sort, body)
                }
            }
            _ => unreachable!(),
        })
    }
}
