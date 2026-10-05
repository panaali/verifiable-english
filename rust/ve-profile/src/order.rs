//! Independent order@0 AST and finite-model route. Proof certificates remain on
//! the Lean route; this evaluator cannot certify entailment.
use crate::search::{domain_sizes, increment as odometer, next_combination};
use num_bigint::BigInt;
use serde_json::{Value, json};
use std::collections::{BTreeMap, BTreeSet};
use ve_kernel::{
    Environment, Error, Result, digest,
    internal::{EnvironmentInternals, error},
};

#[derive(Clone, Eq, PartialEq, Ord, PartialOrd)]
enum Cell {
    Object(String),
    Integer(BigInt),
}

fn array(v: &Value) -> Result<&[Value]> {
    v.as_array()
        .map(Vec::as_slice)
        .ok_or_else(|| Error::new("SyntaxError", "expected array"))
}
fn tag(v: &Value) -> Result<(&str, &[Value])> {
    let a = array(v)?;
    let s = a
        .first()
        .and_then(Value::as_str)
        .ok_or_else(|| Error::new("SyntaxError", "tag missing"))?;
    Ok((s, a))
}
fn decimal(v: &Value) -> Result<BigInt> {
    let s = v
        .as_str()
        .ok_or_else(|| Error::new("SyntaxError", "integer must be a string"))?;
    if s.chars().count() > 40 {
        return error("ResourceLimit", "integer literal length");
    }
    if s.is_empty()
        || s == "-0"
        || s.starts_with('+')
        || (s.starts_with('0') && s.len() > 1)
        || s.starts_with("-0")
        || !s
            .trim_start_matches('-')
            .bytes()
            .all(|b| b.is_ascii_digit())
    {
        return error("SyntaxError", "noncanonical integer");
    }
    s.parse()
        .map_err(|_| Error::new("SyntaxError", "bad integer"))
}
fn term_sort(
    env: &Environment,
    t: &Value,
    ctx: &[String],
    depth: usize,
    nodes: &mut usize,
) -> Result<String> {
    *nodes += 1;
    if *nodes > 10_000 || depth > 64 {
        return error("ResourceLimit", "AST limit");
    }
    let (kind, a) = tag(t)?;
    match (kind, a.len()) {
        ("var", 2) => {
            let i = a[1]
                .as_u64()
                .ok_or_else(|| Error::new("UnboundVariable", "invalid index"))?;
            ctx.get(i as usize)
                .cloned()
                .ok_or_else(|| Error::new("UnboundVariable", "unbound index"))
        }
        ("const", 2) => env
            .constants()
            .get(a[1].as_str().unwrap_or(""))
            .cloned()
            .ok_or_else(|| Error::new("UnknownSymbol", "unknown constant")),
        ("num", 2) => {
            decimal(&a[1])?;
            Ok("$int".into())
        }
        ("add", 3) => {
            if term_sort(env, &a[1], ctx, depth + 1, nodes)? != "$int"
                || term_sort(env, &a[2], ctx, depth + 1, nodes)? != "$int"
            {
                return error("TypeMismatch", "arithmetic requires integers");
            }
            Ok("$int".into())
        }
        ("scale", 3) => {
            decimal(&a[1])?;
            if term_sort(env, &a[2], ctx, depth + 1, nodes)? != "$int" {
                return error("TypeMismatch", "arithmetic requires integers");
            }
            Ok("$int".into())
        }
        _ => error("SyntaxError", "invalid term"),
    }
}
fn formula_check(
    env: &Environment,
    f: &Value,
    ctx: &[String],
    depth: usize,
    nodes: &mut usize,
) -> Result<()> {
    *nodes += 1;
    if *nodes > 10_000 || depth > 64 {
        return error("ResourceLimit", "AST limit");
    }
    let (kind, a) = tag(f)?;
    match (kind, a.len()) {
        ("top" | "bottom", 1) => Ok(()),
        ("unary", 3) | ("binary", 4) => {
            let p = a[1].as_str().unwrap_or("");
            let sig = env
                .predicates()
                .get(p)
                .ok_or_else(|| Error::new("UnknownSymbol", "unknown predicate"))?;
            if sig.len() != a.len() - 2 {
                return error("TypeMismatch", "predicate arity");
            }
            for (v, s) in a[2..].iter().zip(sig) {
                if &term_sort(env, v, ctx, 1, nodes)? != s {
                    return error("TypeMismatch", "predicate argument sort");
                }
            }
            Ok(())
        }
        ("eq" | "lt" | "le", 3) => {
            let l = term_sort(env, &a[1], ctx, 1, nodes)?;
            let r = term_sort(env, &a[2], ctx, 1, nodes)?;
            if l != r || (kind != "eq" && l != "$int") {
                return error("TypeMismatch", "comparison sort");
            }
            Ok(())
        }
        ("not", 2) => formula_check(env, &a[1], ctx, depth + 1, nodes),
        ("and" | "or" | "implies", 3) => {
            formula_check(env, &a[1], ctx, depth + 1, nodes)?;
            formula_check(env, &a[2], ctx, depth + 1, nodes)
        }
        ("forall" | "exists", 3) => {
            let sort = a[1].as_str().unwrap_or("");
            if !env.sorts().contains(sort) {
                return error("UnknownSymbol", "unknown binder sort");
            }
            let mut next = vec![sort.to_owned()];
            next.extend_from_slice(ctx);
            formula_check(env, &a[2], &next, depth + 1, nodes)
        }
        _ => error("SyntaxError", "invalid formula"),
    }
}

struct Model {
    domains: BTreeMap<String, Vec<String>>,
    constants: BTreeMap<String, Cell>,
    relations: BTreeMap<String, BTreeSet<Vec<Cell>>>,
    canonical: Value,
}
fn cell(v: &Value, sort: &str, domains: &BTreeMap<String, Vec<String>>) -> Result<Cell> {
    if sort == "$int" {
        return Ok(Cell::Integer(decimal(v)?));
    }
    let s = v
        .as_str()
        .ok_or_else(|| Error::new("InvalidModel", "entity must be string"))?;
    if !domains[sort].iter().any(|x| x == s) {
        return error("InvalidModel", "entity outside sort");
    }
    Ok(Cell::Object(s.into()))
}
fn cell_value(v: &Cell) -> Value {
    match v {
        Cell::Object(s) => json!(s),
        Cell::Integer(i) => json!(i.to_string()),
    }
}
impl Model {
    fn decode(env: &Environment, v: &Value) -> Result<Self> {
        let o = v
            .as_object()
            .ok_or_else(|| Error::new("InvalidModel", "model object required"))?;
        if o.len() != 4 || o.get("complete") != Some(&json!(true)) {
            return error("InvalidModel", "invalid model fields");
        }
        let ds = o
            .get("domains")
            .and_then(Value::as_object)
            .ok_or_else(|| Error::new("InvalidModel", "domains required"))?;
        let cs = o
            .get("constants")
            .and_then(Value::as_object)
            .ok_or_else(|| Error::new("InvalidModel", "constants required"))?;
        let rs = o
            .get("relations")
            .and_then(Value::as_object)
            .ok_or_else(|| Error::new("InvalidModel", "relations required"))?;
        if ds.keys().cloned().collect::<BTreeSet<_>>() != env.model_sorts()
            || cs.keys().ne(env.constants().keys())
            || rs.keys().ne(env.predicates().keys())
        {
            return error("InvalidModel", "model declarations differ");
        }
        ve_kernel::internal::model_limits(ds, rs)?;
        let mut domains = BTreeMap::new();
        for (s, raw) in ds {
            let mut vals = Vec::new();
            for x in array(raw)? {
                let name = x
                    .as_str()
                    .ok_or_else(|| Error::new("InvalidModel", "entity string required"))?;
                ve_kernel::internal::identifier(name, "InvalidModel")?;
                vals.push(name.to_owned());
            }
            if vals.len() > 1000 {
                return error("ResourceLimit", "domain size");
            }
            vals.sort();
            if vals.windows(2).any(|p| p[0] == p[1]) {
                return error("InvalidModel", "duplicate entity");
            }
            domains.insert(s.clone(), vals);
        }
        let mut constants = BTreeMap::new();
        for (name, raw) in cs {
            constants.insert(name.clone(), cell(raw, &env.constants()[name], &domains)?);
        }
        let mut literal_values = BTreeSet::new();
        for (name, sort) in env.constants() {
            if sort == "$string" && !literal_values.insert(&constants[name]) {
                return error(
                    "InvalidModel",
                    format!("$string literals alias at {name} (literals)"),
                );
            }
        }
        let mut relations = BTreeMap::new();
        let mut count = 0;
        for (name, raw) in rs {
            let sig = &env.predicates()[name];
            let mut rows = BTreeSet::new();
            for row in array(raw)? {
                let a = array(row)?;
                if a.len() != sig.len() {
                    return error("InvalidModel", "relation arity");
                }
                let typed = a
                    .iter()
                    .zip(sig)
                    .map(|(v, s)| cell(v, s, &domains))
                    .collect::<Result<Vec<_>>>()?;
                if !rows.insert(typed) {
                    return error("InvalidModel", "duplicate relation row");
                }
                count += 1;
                if count > 100_000 {
                    return error("ResourceLimit", "relation tuple limit");
                }
            }
            relations.insert(name.clone(), rows);
        }
        let canon_constants: BTreeMap<_, _> = constants
            .iter()
            .map(|(k, v)| (k.clone(), cell_value(v)))
            .collect();
        let canon_relations: BTreeMap<_, _> = relations
            .iter()
            .map(|(k, rows)| {
                (
                    k.clone(),
                    rows.iter()
                        .map(|row| row.iter().map(cell_value).collect::<Vec<_>>())
                        .collect::<Vec<_>>(),
                )
            })
            .collect();
        let canonical = json!({"complete":true,"domains":domains,"constants":canon_constants,"relations":canon_relations});
        Ok(Self {
            domains,
            constants,
            relations,
            canonical,
        })
    }
}
fn eval_term(t: &Value, model: &Model, ctx: &[Cell]) -> Cell {
    let (kind, a) = tag(t).expect("checked term");
    match kind {
        "var" => ctx[a[1].as_u64().unwrap() as usize].clone(),
        "const" => model.constants[a[1].as_str().unwrap()].clone(),
        "num" => Cell::Integer(decimal(&a[1]).expect("checked number")),
        "add" | "scale" => {
            let n = if kind == "add" {
                let Cell::Integer(l) = eval_term(&a[1], model, ctx) else {
                    unreachable!()
                };
                let Cell::Integer(r) = eval_term(&a[2], model, ctx) else {
                    unreachable!()
                };
                l + r
            } else {
                let Cell::Integer(r) = eval_term(&a[2], model, ctx) else {
                    unreachable!()
                };
                decimal(&a[1]).unwrap() * r
            };
            Cell::Integer(n)
        }
        _ => unreachable!(),
    }
}
fn eval(f: &Value, model: &Model, ctx: &[Cell], work: &mut u64, limit: u64) -> Result<bool> {
    if *work >= limit {
        return error("ResourceLimit", "evaluation budget");
    }
    *work += 1;
    let (kind, a) = tag(f)?;
    Ok(match kind {
        "top" => true,
        "bottom" => false,
        "unary" | "binary" => model.relations[a[1].as_str().unwrap()].contains(
            &a[2..]
                .iter()
                .map(|t| eval_term(t, model, ctx))
                .collect::<Vec<_>>(),
        ),
        "eq" => eval_term(&a[1], model, ctx) == eval_term(&a[2], model, ctx),
        "lt" | "le" => {
            let Cell::Integer(l) = eval_term(&a[1], model, ctx) else {
                unreachable!()
            };
            let Cell::Integer(r) = eval_term(&a[2], model, ctx) else {
                unreachable!()
            };
            if kind == "lt" { l < r } else { l <= r }
        }
        "not" => !eval(&a[1], model, ctx, work, limit)?,
        "and" => eval(&a[1], model, ctx, work, limit)? && eval(&a[2], model, ctx, work, limit)?,
        "or" => eval(&a[1], model, ctx, work, limit)? || eval(&a[2], model, ctx, work, limit)?,
        "implies" => {
            !eval(&a[1], model, ctx, work, limit)? || eval(&a[2], model, ctx, work, limit)?
        }
        "forall" | "exists" => {
            let universal = kind == "forall";
            let sort = a[1].as_str().unwrap();
            let mut verdict = universal;
            for object in &model.domains[sort] {
                let mut next = vec![Cell::Object(object.clone())];
                next.extend_from_slice(ctx);
                if eval(&a[2], model, &next, work, limit)? != universal {
                    verdict = !universal;
                    break;
                }
            }
            verdict
        }
        _ => unreachable!(),
    })
}

fn py_cell(v: &Cell) -> String {
    match v {
        Cell::Object(s) => format!("'{s}'"),
        Cell::Integer(n) => n.to_string(),
    }
}

fn trace_node(kind: &str, value: bool, bindings: &[(String, String)], detail: String,
              children: Vec<Value>) -> Value {
    let bindings = bindings.iter().enumerate().map(|(index, (sort, local_id))|
        json!({"debruijn_index":index,"sort":sort,"local_id":local_id})).collect::<Vec<_>>();
    json!({"kind":kind,"value":value,"bindings":bindings,"detail":detail,"children":children})
}

fn traced_eval(f: &Value, model: &Model, ctx: &[Cell], bindings: &[(String, String)],
               work: &mut u64, limit: u64) -> Result<(bool, Value)> {
    if *work >= limit {
        return error("ResourceLimit", "evaluation budget");
    }
    *work += 1;
    let (kind, a) = tag(f)?;
    let (value, label, detail, children) = match kind {
        "top" => (true, "top", String::new(), vec![]),
        "bottom" => (false, "bottom", String::new(), vec![]),
        "unary" | "binary" => {
            let row = a[2..].iter().map(|t| eval_term(t, model, ctx)).collect::<Vec<_>>();
            let value = model.relations[a[1].as_str().unwrap()].contains(&row);
            let cells = row.iter().map(py_cell).collect::<Vec<_>>();
            let tuple = if cells.len() == 1 { format!("({},)", cells[0]) }
                        else { format!("({})", cells.join(", ")) };
            (value, kind, format!("{}{tuple}", a[1].as_str().unwrap()), vec![])
        }
        "eq" => {
            let left = eval_term(&a[1], model, ctx);
            let right = eval_term(&a[2], model, ctx);
            (left == right, "equality",
             format!("{} equals {}", cell_value(&left).as_str().unwrap(),
                     cell_value(&right).as_str().unwrap()), vec![])
        }
        "lt" | "le" => {
            let Cell::Integer(left) = eval_term(&a[1], model, ctx) else { unreachable!() };
            let Cell::Integer(right) = eval_term(&a[2], model, ctx) else { unreachable!() };
            (if kind == "lt" { left < right } else { left <= right }, "comparison",
             format!("{left} {} {right}", if kind == "lt" { "<" } else { "<=" }), vec![])
        }
        "not" => {
            let (child_value, child) = traced_eval(&a[1], model, ctx, bindings, work, limit)?;
            (!child_value, "not", String::new(), vec![child])
        }
        "and" | "or" | "implies" => {
            let (left, first) = traced_eval(&a[1], model, ctx, bindings, work, limit)?;
            if kind == "and" && !left {
                (false, kind, "right branch not needed".into(), vec![first])
            } else if kind == "or" && left {
                (true, kind, "right branch not needed".into(), vec![first])
            } else if kind == "implies" && !left {
                (true, kind, "vacuously true: antecedent is false".into(), vec![first])
            } else {
                let (right, second) = traced_eval(&a[2], model, ctx, bindings, work, limit)?;
                (if kind == "and" { left && right } else { right }, kind, String::new(),
                 vec![first, second])
            }
        }
        "forall" | "exists" => {
            let universal = kind == "forall";
            let sort = a[1].as_str().unwrap();
            let domain = &model.domains[sort];
            if domain.is_empty() {
                (universal, kind, if universal { "vacuously true: domain is empty" }
                    else { "false: domain is empty" }.into(), vec![])
            } else {
                let mut children = Vec::new();
                let mut decisive = None;
                for entity in domain {
                    let mut next_ctx = vec![Cell::Object(entity.clone())];
                    next_ctx.extend_from_slice(ctx);
                    let mut next_bindings = vec![(sort.to_owned(), entity.clone())];
                    next_bindings.extend_from_slice(bindings);
                    let (child_value, child) = traced_eval(&a[2], model, &next_ctx,
                        &next_bindings, work, limit)?;
                    children.push(child);
                    if child_value != universal {
                        decisive = Some(entity);
                        break;
                    }
                }
                let value = decisive.is_none() == universal;
                let detail = match decisive {
                    Some(entity) if universal => format!("counterexample {entity}"),
                    Some(entity) => format!("witness {entity}"),
                    None if universal => "all entities checked".into(),
                    None => "no witness".into(),
                };
                (value, kind, detail, children)
            }
        }
        _ => unreachable!(),
    };
    Ok((value, trace_node(label, value, bindings, detail, children)))
}
fn print_term(t: &Value, names: &[String]) -> String {
    let (kind, a) = tag(t).expect("checked term");
    match kind {
        "var" => names[a[1].as_u64().unwrap() as usize].clone(),
        "const" => format!("@{}", a[1].as_str().unwrap()),
        "num" => a[1].as_str().unwrap().into(),
        "scale" => {
            let coefficient = a[1].as_str().unwrap();
            if coefficient == "-1" && tag(&a[2]).unwrap().0 != "num" {
                format!("-{}", print_term(&a[2], names))
            } else {
                format!("[{coefficient} * {}]", print_term(&a[2], names))
            }
        }
        "add" => {
            let left = print_term(&a[1], names);
            let (right_kind, right) = tag(&a[2]).unwrap();
            if right_kind == "scale" && right[1] == "-1" {
                format!("[{left} - {}]", print_term(&right[2], names))
            } else {
                format!("[{left} + {}]", print_term(&a[2], names))
            }
        }
        _ => unreachable!(),
    }
}
fn print_formula(f: &Value, names: &[String], counter: &mut usize) -> String {
    let (kind, a) = tag(f).expect("checked formula");
    match kind {
        "top" => "true".into(),
        "bottom" => "false".into(),
        "unary" => format!("{} is {}", print_term(&a[2], names), a[1].as_str().unwrap()),
        "binary" => format!(
            "{} {} {}",
            print_term(&a[2], names),
            a[1].as_str().unwrap(),
            print_term(&a[3], names)
        ),
        "eq" | "lt" | "le" => format!(
            "{} {} {}",
            print_term(&a[1], names),
            if kind == "eq" {
                "equals"
            } else if kind == "lt" {
                "<"
            } else {
                "<="
            },
            print_term(&a[2], names)
        ),
        "not" => format!("not ({})", print_formula(&a[1], names, counter)),
        "and" | "or" => format!(
            "({}) {} ({})",
            print_formula(&a[1], names, counter),
            kind,
            print_formula(&a[2], names, counter)
        ),
        "implies" => format!(
            "if ({}), then ({})",
            print_formula(&a[1], names, counter),
            print_formula(&a[2], names, counter)
        ),
        "forall" | "exists" => {
            let name = format!("x{}", *counter);
            *counter += 1;
            let mut next = vec![name.clone()];
            next.extend_from_slice(names);
            format!(
                "{} {} {name}, ({})",
                if kind == "forall" {
                    "for every"
                } else {
                    "there exists"
                },
                a[1].as_str().unwrap(),
                print_formula(&a[2], &next, counter)
            )
        }
        _ => unreachable!(),
    }
}

struct Parser<'a> {
    source: &'a str,
    pos: usize,
    names: Vec<String>,
    env: &'a Environment,
}
impl Parser<'_> {
    fn at(&self, s: &str) -> bool {
        self.source[self.pos..].starts_with(s)
    }
    fn eat(&mut self, s: &str) -> bool {
        if self.at(s) {
            self.pos += s.len();
            true
        } else {
            false
        }
    }
    fn expect(&mut self, s: &str) -> Result<()> {
        if self.eat(s) {
            Ok(())
        } else {
            error("SyntaxError", format!("expected {s:?}"))
        }
    }
    fn ident(&mut self) -> Result<String> {
        let start = self.pos;
        let bytes = self.source.as_bytes();
        if !bytes.get(start).is_some_and(u8::is_ascii_lowercase) {
            return error("SyntaxError", "identifier expected");
        }
        self.pos += 1;
        while bytes
            .get(self.pos)
            .is_some_and(|b| b.is_ascii_lowercase() || b.is_ascii_digit() || *b == b'_')
        {
            self.pos += 1;
        }
        if self.pos - start > 64 {
            return error("ResourceLimit", "identifier length");
        }
        Ok(self.source[start..self.pos].into())
    }
    fn numeral(&mut self) -> Result<String> {
        let start = self.pos;
        self.eat("-");
        while self
            .source
            .as_bytes()
            .get(self.pos)
            .is_some_and(u8::is_ascii_digit)
        {
            self.pos += 1;
        }
        let text = &self.source[start..self.pos];
        decimal(&json!(text))?;
        Ok(text.into())
    }
    fn term(&mut self, fuel: usize) -> Result<Value> {
        if fuel == 0 {
            return error("ResourceLimit", "term depth");
        }
        let first = self.source.as_bytes().get(self.pos).copied();
        if first.is_some_and(|b| b.is_ascii_digit())
            || (first == Some(b'-')
                && self
                    .source
                    .as_bytes()
                    .get(self.pos + 1)
                    .is_some_and(u8::is_ascii_digit))
        {
            return Ok(json!(["num", self.numeral()?]));
        }
        if self.eat("-") {
            return Ok(json!(["scale", "-1", self.term(fuel - 1)?]));
        }
        if self.eat("[") {
            let left = self.term(fuel - 1)?;
            if self.eat(" * ") {
                if tag(&left)?.0 != "num" {
                    return error("SyntaxError", "integer coefficient required");
                }
                let right = self.term(fuel - 1)?;
                self.expect("]")?;
                return Ok(json!(["scale", left[1], right]));
            }
            if self.eat(" + ") {
                let right = self.term(fuel - 1)?;
                self.expect("]")?;
                return Ok(json!(["add", left, right]));
            }
            self.expect(" - ")?;
            let right = self.term(fuel - 1)?;
            self.expect("]")?;
            return Ok(json!(["add", left, ["scale", "-1", right]]));
        }
        if self.eat("@") {
            return Ok(json!(["const", self.ident()?]));
        }
        let name = self.ident()?;
        let i = self
            .names
            .iter()
            .rev()
            .position(|x| x == &name)
            .ok_or_else(|| Error::new("UnboundVariable", "unbound variable"))?;
        Ok(json!(["var", i]))
    }
    fn keyword(&self, word: &str) -> bool {
        self.at(word)
            && !self
                .source
                .as_bytes()
                .get(self.pos + word.len())
                .is_some_and(|b| b.is_ascii_lowercase() || b.is_ascii_digit() || *b == b'_')
    }
    fn formula(&mut self, depth: usize) -> Result<Value> {
        if depth > 64 {
            return error("ResourceLimit", "formula depth");
        }
        if self.keyword("true") {
            self.pos += 4;
            return Ok(json!(["top"]));
        }
        if self.keyword("false") {
            self.pos += 5;
            return Ok(json!(["bottom"]));
        }
        if self.eat("not (") {
            let body = self.formula(depth + 1)?;
            self.expect(")")?;
            return Ok(json!(["not", body]));
        }
        if self.eat("if (") {
            let left = self.formula(depth + 1)?;
            self.expect("), then (")?;
            let right = self.formula(depth + 1)?;
            self.expect(")")?;
            return Ok(json!(["implies", left, right]));
        }
        if self.at("for every ") || self.at("there exists ") {
            let universal = self.eat("for every ");
            if !universal {
                self.expect("there exists ")?;
            }
            let sort = self.ident()?;
            if !self.env.sorts().contains(&sort) {
                return error("UnknownSymbol", "unknown binder sort");
            }
            self.expect(" ")?;
            let name = self.ident()?;
            if ve_kernel::internal::RESERVED.contains(&name.as_str())
                || self.env.schema_name(&name)
                || self.names.contains(&name)
            {
                return error("SyntaxError", "invalid binder name");
            }
            self.expect(", (")?;
            self.names.push(name);
            let body = self.formula(depth + 1)?;
            self.names.pop();
            self.expect(")")?;
            return Ok(json!([
                if universal { "forall" } else { "exists" },
                sort,
                body
            ]));
        }
        if self.eat("(") {
            let left = self.formula(depth + 1)?;
            let op = if self.eat(") and (") {
                "and"
            } else {
                self.expect(") or (")?;
                "or"
            };
            let right = self.formula(depth + 1)?;
            self.expect(")")?;
            return Ok(json!([op, left, right]));
        }
        let left = self.term(64)?;
        if self.eat(" equals ") {
            return Ok(json!(["eq", left, self.term(64)?]));
        }
        if self.eat(" <= ") {
            return Ok(json!(["le", left, self.term(64)?]));
        }
        if self.eat(" < ") {
            return Ok(json!(["lt", left, self.term(64)?]));
        }
        if self.eat(" is ") {
            return Ok(json!(["unary", self.ident()?, left]));
        }
        self.expect(" ")?;
        let predicate = self.ident()?;
        self.expect(" ")?;
        Ok(json!(["binary", predicate, left, self.term(64)?]))
    }
    fn document(&mut self) -> Result<Value> {
        let mut formulas = Vec::new();
        while self.pos < self.source.len() {
            formulas.push(self.formula(1)?);
            self.expect(".\n")?;
        }
        if formulas.is_empty() {
            return error("SyntaxError", "empty document");
        }
        Ok(Value::Array(formulas))
    }
}
fn parse_source(env: &Environment, source: &str) -> Result<Value> {
    if source.len() > ve_kernel::MAX_SOURCE_BYTES {
        return error("ResourceLimit", "source limit");
    }
    if !source.is_ascii() {
        return error("SyntaxError", "ASCII order source required");
    }
    Parser {
        env,
        source,
        pos: 0,
        names: Vec::new(),
    }
    .document()
}

/// Rust's order route accepts checked ASTs and supplied finite models. It does
/// not consume proofs; sound certification is provided by Lean's order route.
pub fn order_case(v: &Value) -> Result<Value> {
    let env = Environment::from_value(
        v.get("environment")
            .ok_or_else(|| Error::new("InvalidInput", "environment missing"))?,
    )?;
    if !env.order() {
        return error("UnsupportedProfile", "order profile required");
    }
    if v.get("kind") == Some(&json!("check")) {
        let ast = v.get("ast").ok_or_else(|| Error::new("InvalidInput", "ast missing"))?;
        let items = array(ast)?;
        let formulas = if items.first().is_some_and(Value::is_string) {
            vec![ast]
        } else {
            items.iter().collect::<Vec<_>>()
        };
        if formulas.is_empty() {
            return error("SyntaxError", "empty document");
        }
        let mut nodes = 0;
        for formula in formulas {
            formula_check(&env, formula, &[], 1, &mut nodes)?;
        }
        return Ok(json!({"id":v.get("id").cloned().unwrap_or(json!("")),
            "status":"ok","well_typed":true}));
    }
    if v.get("kind") == Some(&json!("evaluate-budgeted")) {
        let trace = v.get("trace") == Some(&json!(true));
        let formulas = array(v.get("ast").ok_or_else(|| Error::new("InvalidInput", "ast missing"))?)?;
        if formulas.is_empty() {
            return error("SyntaxError", "empty document");
        }
        let mut nodes = 0;
        for formula in formulas {
            formula_check(&env, formula, &[], 1, &mut nodes)?;
        }
        let model = Model::decode(&env,
            v.get("model").ok_or_else(|| Error::new("InvalidInput", "model missing"))?)?;
        let maximum = v.get("max_evaluations").and_then(Value::as_u64)
            .unwrap_or(ve_kernel::MAX_EVALUATIONS);
        if maximum > ve_kernel::MAX_EVALUATIONS {
            return error("ResourceLimit", "evaluation budget exceeds v0 limit");
        }
        if trace {
            let trace_budget = v.get("max_trace_nodes").and_then(Value::as_u64).unwrap_or(10_000);
            let limit = maximum.min(trace_budget);
            let mut work = 0;
            let mut children = Vec::new();
            let mut status = "Satisfied";
            let mut value = Some(true);
            let mut detail = "all statements satisfied".to_owned();
            for (index, formula) in formulas.iter().enumerate() {
                match traced_eval(formula, &model, &[], &[], &mut work, limit) {
                    Ok((true, child)) => children.push(child),
                    Ok((false, child)) => {
                        children.push(child);
                        status = "Violated";
                        value = Some(false);
                        detail = format!("statement {} violated", index + 1);
                        break;
                    }
                    Err(e) if e.code == "ResourceLimit" => {
                        status = "ResourceLimit";
                        value = None;
                        detail = if trace_budget < maximum { "trace-node budget exhausted" }
                            else { "formula-node evaluation budget exhausted" }.to_owned();
                        break;
                    }
                    Err(e) => return Err(e),
                }
            }
            let explanation = json!({"kind":if value.is_some() { "document" } else { "resource_limit" },
                "value":value,"bindings":[],"detail":detail,"children":children});
            return Ok(json!({"id":v.get("id").cloned().unwrap_or(json!("")),
                "status":status,"value":value,"evaluations":work,"explanation":explanation}));
        }
        let mut work = 0;
        let mut value = true;
        for formula in formulas {
            match eval(formula, &model, &[], &mut work, maximum) {
                Ok(result) => {
                    if !result {
                        value = false;
                        break;
                    }
                }
                Err(e) if e.code == "ResourceLimit" => {
                    return Ok(json!({"id":v.get("id").cloned().unwrap_or(json!("")),
                        "status":"ResourceLimit","value":null,"evaluations":work}));
                }
                Err(e) => return Err(e),
            }
        }
        return Ok(json!({"id":v.get("id").cloned().unwrap_or(json!("")),
            "status":if value { "Satisfied" } else { "Violated" },
            "value":value,"evaluations":work}));
    }
    if v.get("kind") == Some(&json!("countermodel")) {
        let premises = array(
            v.get("premises")
                .ok_or_else(|| Error::new("InvalidInput", "premises missing"))?,
        )?;
        let conclusion = v
            .get("conclusion")
            .ok_or_else(|| Error::new("InvalidInput", "conclusion missing"))?;
        ve_kernel::internal::ast_limit(premises.iter().chain([conclusion]))?;
        let mut nodes = 0;
        for premise in premises {
            formula_check(&env, premise, &[], 1, &mut nodes)?;
        }
        formula_check(&env, conclusion, &[], 1, &mut nodes)?;
        let model = Model::decode(
            &env,
            v.get("model")
                .ok_or_else(|| Error::new("InvalidInput", "model missing"))?,
        )?;
        let mut work = 0;
        let mut valid = true;
        for premise in premises {
            if !eval(premise, &model, &[], &mut work, ve_kernel::MAX_EVALUATIONS)? {
                valid = false;
                break;
            }
        }
        if valid {
            valid = !eval(conclusion, &model, &[], &mut work, ve_kernel::MAX_EVALUATIONS)?;
        }
        return Ok(
            json!({"id":v.get("id").cloned().unwrap_or(json!("")),"status":"ok","valid":valid}),
        );
    }
    if v.get("kind").is_none() && v.get("premises").is_some() && v.get("conclusion").is_some()
        && v.get("certificate").is_none() {
        return if v.get("model").is_some() {
            order_countermodel_check(&env, v)
        } else {
            order_search(&env, v, None)
        };
    }
    if v.get("kind") == Some(&json!("distinguishing-model")) {
        let a = v.get("a").ok_or_else(|| Error::new("InvalidInput", "a missing"))?;
        let b = v.get("b").ok_or_else(|| Error::new("InvalidInput", "b missing"))?;
        return order_search(&env, v, Some((a, b)));
    }
    if v.get("kind").is_some_and(|kind| kind != "evaluate")
        || v.get("certificate").is_some()
        || v.get("premises").is_some()
        || v.get("conclusion").is_some()
    {
        return error(
            "UnsupportedProfile",
            "Rust order route supports evaluation and supplied countermodel checking only",
        );
    }
    let parsed = v
        .get("source")
        .map(|source| {
            source
                .as_str()
                .ok_or_else(|| Error::new("SyntaxError", "source must be text"))
                .and_then(|source| parse_source(&env, source))
        })
        .transpose()?;
    let ast = match (v.get("ast"), parsed.as_ref()) {
        (Some(ast), Some(parsed)) if ast != parsed => {
            return error("TypeMismatch", "source/AST mismatch");
        }
        (Some(ast), _) => ast,
        (None, Some(parsed)) => parsed,
        (None, None) => return error("InvalidInput", "source or AST required"),
    };
    let formulas = array(ast)?;
    if formulas.is_empty() {
        return error("SyntaxError", "empty document");
    }
    ve_kernel::internal::ast_limit(formulas)?;
    let mut nodes = 0;
    for f in formulas {
        formula_check(&env, f, &[], 1, &mut nodes)?;
    }
    let meaning = |a: &Value| {
        digest(
            &format!("ve-meaning-{}\n", env.identity_version()),
            &json!({"environment_id":env.environment_id(),"ast":a}),
        )
    };
    let ids = formulas.iter().map(meaning).collect::<Result<Vec<_>>>()?;
    let canonical = formulas
        .iter()
        .map(|f| format!("{}.\n", print_formula(f, &[], &mut 0)))
        .collect::<String>();
    if canonical.len() > ve_kernel::MAX_SOURCE_BYTES {
        return error("ResourceLimit", "canonical source limit");
    }
    let mut out = json!({"id":v.get("id").cloned().unwrap_or(json!("")),"status":"ok","ast":ast,
        "canonical":canonical,"environment_id":env.environment_id(),"meaning_id":meaning(ast)?,"formula_meaning_ids":ids});
    out["canonical_environment"] =
        json!(String::from_utf8(ve_kernel::canonical_json(&env.to_value())?).unwrap());
    out["canonical_ast"] = json!(String::from_utf8(ve_kernel::canonical_json(ast)?).unwrap());
    if let Some(raw) = v.get("model") {
        let model = Model::decode(&env, raw)?;
        let mut values = Vec::new();
        for f in formulas {
            let mut work = 0;
            values.push(eval(f, &model, &[], &mut work, ve_kernel::MAX_EVALUATIONS)?);
        }
        out["value"] = json!(values.iter().all(|x| *x));
        out["values"] = json!(values);
        out["canonical_model"] =
            json!(String::from_utf8(ve_kernel::canonical_json(&model.canonical)?).unwrap());
        out["model_id"] = json!(digest(
            &format!("ve-model-{}\n", env.identity_version()),
            &json!({"environment_id":env.environment_id(),"model":model.canonical})
        )?);
    }
    Ok(out)
}

/// Python `search.ORDER_SEARCH_MAGNITUDE`: integer constants range over
/// [-3, 3] plus every numeral and its neighbours.
const ORDER_SEARCH_MAGNITUDE: i64 = 3;
const SEARCH_SPACE: &str = "search relation atom space exceeds runtime limit";

fn by_magnitude(values: BTreeSet<BigInt>) -> Vec<BigInt> {
    let mut values: Vec<_> = values.into_iter().collect();
    values.sort_by(|a, b| (a.magnitude(), a).cmp(&(b.magnitude(), b)));
    values
}

/// Python `search._int_terms`: integer terms in predicate argument positions,
/// and every numeral (and scale coefficient) occurring anywhere in a term.
fn int_terms(f: &Value, ints: &BTreeSet<String>, arguments: &mut Vec<Value>,
             numerals: &mut BTreeSet<BigInt>) {
    fn term(t: &Value, argument: bool, ints: &BTreeSet<String>, arguments: &mut Vec<Value>,
            numerals: &mut BTreeSet<BigInt>) {
        let Ok((kind, a)) = tag(t) else { return };
        if argument && kind != "var"
            && !(kind == "const" && !a.get(1).and_then(Value::as_str).is_some_and(|c| ints.contains(c))) {
            arguments.push(t.clone());
        }
        match kind {
            "num" => { if let Ok(n) = decimal(&a[1]) { numerals.insert(n); } }
            "add" => {
                term(&a[1], false, ints, arguments, numerals);
                term(&a[2], false, ints, arguments, numerals);
            }
            "scale" => {
                if let Ok(n) = decimal(&a[1]) { numerals.insert(n); }
                term(&a[2], false, ints, arguments, numerals);
            }
            _ => {}
        }
    }
    let Ok((kind, a)) = tag(f) else { return };
    match kind {
        "unary" | "binary" => for t in &a[2..] { term(t, true, ints, arguments, numerals) },
        "eq" | "lt" | "le" => {
            term(&a[1], false, ints, arguments, numerals);
            term(&a[2], false, ints, arguments, numerals);
        }
        "and" | "or" | "implies" => {
            int_terms(&a[1], ints, arguments, numerals);
            int_terms(&a[2], ints, arguments, numerals);
        }
        "not" => int_terms(&a[1], ints, arguments, numerals),
        "forall" | "exists" => int_terms(&a[2], ints, arguments, numerals),
        _ => {}
    }
}

fn int_value(t: &Value, numbers: &BTreeMap<String, BigInt>) -> BigInt {
    let (kind, a) = tag(t).expect("checked term");
    match kind {
        "num" => decimal(&a[1]).expect("checked number"),
        "add" => int_value(&a[1], numbers) + int_value(&a[2], numbers),
        "scale" => decimal(&a[1]).expect("checked number") * int_value(&a[2], numbers),
        _ => numbers[a[1].as_str().expect("checked constant")].clone(),
    }
}

fn used_predicates(f: &Value, used: &mut BTreeSet<String>) {
    let Ok((kind, a)) = tag(f) else { return };
    match kind {
        "unary" | "binary" => { used.insert(a[1].as_str().unwrap_or("").to_owned()); }
        "and" | "or" | "implies" => { used_predicates(&a[1], used); used_predicates(&a[2], used); }
        "not" => used_predicates(&a[1], used),
        "forall" | "exists" => used_predicates(&a[2], used),
        _ => {}
    }
}

/// Python `search._order_models`, in its exact order: domain sizes, integer
/// constant assignments over the search values, used-relation subsets by
/// size, then object constant denotations. `visit` returns true to stop.
/// A model Python rejects with a Background generator is skipped.
fn order_models(env: &Environment, formulas: &[&Value], minimum: usize, maximum: usize,
                used: &BTreeSet<String>,
                visit: &mut dyn FnMut(Model) -> Result<bool>) -> Result<()> {
    let sorts: Vec<String> = env.model_sorts().into_iter().collect();
    let int_constants: Vec<&String> = env.constants().iter()
        .filter(|(_, sort)| *sort == "$int").map(|(name, _)| name).collect();
    let object_constants: Vec<&String> = env.constants().iter()
        .filter(|(_, sort)| *sort != "$int").map(|(name, _)| name).collect();
    let ints: BTreeSet<String> = int_constants.iter().map(|c| (*c).clone()).collect();
    let mut arguments = Vec::new();
    let mut numerals = BTreeSet::new();
    for f in formulas {
        int_terms(f, &ints, &mut arguments, &mut numerals);
    }
    let mut values: BTreeSet<BigInt> =
        (-ORDER_SEARCH_MAGNITUDE..=ORDER_SEARCH_MAGNITUDE).map(BigInt::from).collect();
    for k in &numerals {
        values.insert(k - 1);
        values.insert(k.clone());
        values.insert(k + 1);
    }
    let values = by_magnitude(values);
    let minima: Vec<usize> = sorts.iter().map(|sort| {
        let mut least = minimum;
        if object_constants.iter().any(|c| &env.constants()[*c] == sort) {
            least = least.max(1);
        }
        if sort == "$string" {
            least = least.max(env.constants().values().filter(|s| *s == "$string").count());
        }
        least
    }).collect();
    let relation_names: Vec<&String> = env.predicates().keys().filter(|p| !env.is_defined(p)).collect();
    for sizes in domain_sizes(&minima, maximum) {
        let domains: BTreeMap<&String, Vec<String>> = sorts.iter().zip(&sizes)
            .map(|(sort, n)| (sort, (0..*n).map(|i| format!("e{i}")).collect())).collect();
        let mut assignment = vec![0; int_constants.len()];
        let assignment_limits = vec![values.len(); int_constants.len()];
        loop {
            let numbers: BTreeMap<String, BigInt> = int_constants.iter().zip(&assignment)
                .map(|(c, i)| ((*c).clone(), values[*i].clone())).collect();
            let cells = by_magnitude(arguments.iter().map(|t| int_value(t, &numbers)).collect());
            let pool = |sort: &str| -> Vec<Value> {
                if sort == "$int" { cells.iter().map(|n| json!(n.to_string())).collect() }
                else { domains.get(&sort.to_owned()).map_or_else(Vec::new,
                    |d| d.iter().map(|e| json!(e)).collect()) }
            };
            let possible: usize = used.iter()
                .map(|p| env.predicates()[p].iter().map(|s| pool(s).len()).product::<usize>()).sum();
            if possible > 100_000 {
                return error("ResourceLimit", SEARCH_SPACE);
            }
            let mut atoms: Vec<(&String, Vec<Value>)> = Vec::new();
            for p in used {
                let pools: Vec<Vec<Value>> = env.predicates()[p].iter().map(|s| pool(s)).collect();
                if pools.iter().any(Vec::is_empty) { continue; }
                let limits: Vec<usize> = pools.iter().map(Vec::len).collect();
                let mut row = vec![0; pools.len()];
                loop {
                    atoms.push((p, row.iter().zip(&pools).map(|(i, pool)| pool[*i].clone()).collect()));
                    if !odometer(&mut row, &limits) { break; }
                }
            }
            let choice_limits: Vec<usize> = object_constants.iter()
                .map(|c| domains[&env.constants()[*c]].len()).collect();
            let choosable = choice_limits.iter().all(|n| *n > 0);
            for size in 0..=atoms.len() {
                let mut subset: Vec<usize> = (0..size).collect();
                loop {
                    let mut relations: BTreeMap<&String, Vec<Value>> =
                        relation_names.iter().map(|p| (*p, Vec::new())).collect();
                    for index in &subset {
                        let (p, row) = &atoms[*index];
                        relations.get_mut(p).expect("declared relation").push(json!(row));
                    }
                    let mut choice = vec![0; object_constants.len()];
                    while choosable {
                        let mut constants: BTreeMap<&String, Value> = numbers.iter()
                            .map(|(c, n)| (int_constants.iter().find(|x| **x == c).copied()
                                .expect("integer constant"), json!(n.to_string()))).collect();
                        for (c, i) in object_constants.iter().zip(&choice) {
                            constants.insert(c, json!(domains[&env.constants()[*c]][*i]));
                        }
                        let raw = json!({"complete":true,"domains":domains,
                            "constants":constants,"relations":relations});
                        match Model::decode(env, &raw) {
                            Ok(model) => if visit(model)? { return Ok(()); },
                            Err(e) if e.code == "InvalidModel" && e.message.ends_with("(literals)") => {}
                            Err(e) => return Err(e),
                        }
                        if !odometer(&mut choice, &choice_limits) { break; }
                    }
                    if size == 0 || !next_combination(&mut subset, atoms.len()) { break; }
                }
            }
            if !odometer(&mut assignment, &assignment_limits) { break; }
        }
    }
    Ok(())
}

/// Python `search._check_countermodel_values`: premises in order, then the
/// conclusion, sharing one budget.
fn countermodel_values(premises: &[Value], conclusion: &Value, model: &Model, maximum: u64)
    -> Result<(&'static str, Vec<bool>, Option<bool>, u64)> {
    let mut work = 0;
    let mut values = Vec::new();
    for f in premises {
        match eval(f, model, &[], &mut work, maximum) {
            Ok(value) => {
                values.push(value);
                if !value { return Ok(("NotCountermodel", values, None, work)); }
            }
            Err(e) if e.code == "ResourceLimit" => return Ok(("ResourceLimit", values, None, work)),
            Err(e) => return Err(e),
        }
    }
    match eval(conclusion, model, &[], &mut work, maximum) {
        Ok(value) => Ok((if value { "NotCountermodel" } else { "Valid" }, values, Some(value), work)),
        Err(e) if e.code == "ResourceLimit" => Ok(("ResourceLimit", values, None, work)),
        Err(e) => Err(e),
    }
}

/// Python `search._nonvacuous` over order formulas: (suitable, work, exhausted).
fn nonvacuous(formula: &Value, model: &Model, maximum: u64, semantic: bool) -> (bool, u64, bool) {
    struct Walk<'a> {
        model: &'a Model,
        maximum: u64,
        work: u64,
        semantic: bool,
        ok: bool,
        hits: BTreeMap<Vec<usize>, bool>,
    }
    impl Walk<'_> {
        fn tick(&mut self) -> Result<()> {
            if self.work >= self.maximum {
                return error("ResourceLimit", "evaluation budget");
            }
            self.work += 1;
            Ok(())
        }
        fn hit(&mut self, guards: &[&Value], ctx: &[Cell], path: &[usize]) -> Result<()> {
            self.hits.entry(path.to_vec()).or_insert(false);
            let mut value = true;
            for guard in guards {
                value &= eval(guard, self.model, ctx, &mut self.work, self.maximum)?;
                if !value { break; }
            }
            *self.hits.get_mut(path).expect("hit entry") |= value;
            Ok(())
        }
        fn clause_guards<'v>(&mut self, node: &'v Value) -> Result<Vec<&'v Value>> {
            let mut guards = Vec::new();
            let mut stack = vec![node];
            while let Some(disjunct) = stack.pop() {
                self.tick()?;
                let (kind, a) = tag(disjunct)?;
                if kind == "or" {
                    stack.push(&a[2]);
                    stack.push(&a[1]);
                } else if kind == "not" {
                    guards.push(&a[1]);
                }
            }
            Ok(guards)
        }
        fn walk(&mut self, node: &Value, ctx: &[Cell], path: &mut Vec<usize>, universal: bool,
                in_clause: bool) -> Result<()> {
            self.tick()?;
            let (kind, a) = tag(node)?;
            match kind {
                "implies" => {
                    self.hit(&[&a[1]], ctx, path)?;
                    path.push(0);
                    self.walk(&a[1], ctx, path, universal, false)?;
                    path.pop(); path.push(1);
                    self.walk(&a[2], ctx, path, universal, false)?;
                    path.pop();
                }
                "and" | "or" => {
                    let is_or = kind == "or";
                    if self.semantic && universal && is_or && !in_clause {
                        let guards = self.clause_guards(node)?;
                        if !guards.is_empty() {
                            self.hit(&guards, ctx, path)?;
                        }
                    }
                    for (index, child) in [&a[1], &a[2]].into_iter().enumerate() {
                        path.push(index);
                        self.walk(child, ctx, path, universal, is_or)?;
                        path.pop();
                    }
                }
                "not" => {
                    path.push(0);
                    self.walk(&a[1], ctx, path, universal, false)?;
                    path.pop();
                }
                "forall" | "exists" => {
                    let domain = &self.model.domains[a[1].as_str().expect("checked sort")];
                    if domain.is_empty() { self.ok = false; }
                    for entity in domain.clone() {
                        let mut next = vec![Cell::Object(entity)];
                        next.extend_from_slice(ctx);
                        path.push(0);
                        self.walk(&a[2], &next, path, universal || kind == "forall", false)?;
                        path.pop();
                    }
                }
                _ => {}
            }
            Ok(())
        }
    }
    let mut state = Walk { model, maximum, work: 0, semantic, ok: true, hits: BTreeMap::new() };
    match state.walk(formula, &[], &mut Vec::new(), false, false) {
        Ok(()) => (state.ok && state.hits.values().all(|v| *v), state.work, false),
        Err(_) => (false, state.work, true),
    }
}

fn model_id(env: &Environment, model: &Model) -> Result<String> {
    digest(&format!("ve-model-{}\n", env.identity_version()),
           &json!({"environment_id":env.environment_id(),"model":model.canonical}))
}

fn number(v: &Value, name: &str, default: u64) -> Result<u64> {
    match v.get(name) {
        None => Ok(default),
        Some(value) => value.as_u64().ok_or_else(|| Error::new("InvalidInput", format!("{name} must be a nonnegative integer"))),
    }
}

/// Bounded order search: a countermodel (`premises`, `conclusion`) or a
/// distinguishing model (`a`, `b`), with Python's options and counters.
fn order_search(env: &Environment, v: &Value, pair: Option<(&Value, &Value)>) -> Result<Value> {
    let premises: Vec<Value> = match pair {
        Some(_) => Vec::new(),
        None => array(v.get("premises").ok_or_else(|| Error::new("InvalidInput", "premises missing"))?)?.to_vec(),
    };
    let conclusion = v.get("conclusion");
    let guard = v.get("nonvacuous_for");
    let semantic = v.get("semantic_nonvacuity") == Some(&json!(true));
    let maximum_size = usize::try_from(number(v, "max_domain_size", 2)?)
        .map_err(|_| Error::new("ResourceLimit", "domain bound overflow"))?;
    let max_models = number(v, "max_models", 10_000)?;
    let max_evaluations = number(v, "max_evaluations", ve_kernel::MAX_EVALUATIONS)?;
    let minimum = usize::try_from(number(v, "min_domain_size", 0)?)
        .map_err(|_| Error::new("ResourceLimit", "minimum domain bound overflow"))?
        .max(usize::from(v.get("nonempty_domains") == Some(&json!(true))));
    if maximum_size > 1000 || max_evaluations > ve_kernel::MAX_EVALUATIONS || minimum > maximum_size {
        return error("ResourceLimit", "search bounds exceed v0 envelope");
    }
    let mut formulas: Vec<&Value> = match pair {
        Some((a, b)) => vec![a, b],
        None => premises.iter().chain(conclusion).collect(),
    };
    ve_kernel::internal::ast_limit(formulas.iter().copied())?;
    let mut nodes = 0;
    for f in &formulas {
        formula_check(env, f, &[], 1, &mut nodes)?;
    }
    if let Some(g) = guard {
        formula_check(env, g, &[], 1, &mut 0)?;
        formulas.push(g);
    }
    let mut used = BTreeSet::new();
    for f in &formulas {
        used_predicates(f, &mut used);
    }
    let conclusion = conclusion.cloned();
    let (mut checked, mut work) = (0u64, 0u64);
    let mut outcome: Option<(&'static str, Option<Value>, &'static str)> = None;
    let search = order_models(env, &formulas, minimum, maximum_size, &used, &mut |model| {
        if checked >= max_models {
            outcome = Some(("ResourceLimit", None, "model-attempt budget exhausted"));
            return Ok(true);
        }
        if work >= max_evaluations {
            outcome = Some(("ResourceLimit", None, "evaluation budget exhausted"));
            return Ok(true);
        }
        if let Some(g) = guard {
            let (suitable, spent, exhausted) = nonvacuous(g, &model, max_evaluations - work, semantic);
            work += spent;
            if exhausted {
                checked += 1;
                outcome = Some(("ResourceLimit", None, "evaluation budget exhausted"));
                return Ok(true);
            }
            if !suitable {
                checked += 1;
                return Ok(false);
            }
        }
        let found = match pair {
            None => {
                let (status, _, _, spent) = countermodel_values(
                    &premises, conclusion.as_ref().expect("conclusion"), &model, max_evaluations - work)?;
                checked += 1;
                work += spent;
                if status == "ResourceLimit" {
                    outcome = Some(("ResourceLimit", None, "evaluation budget exhausted"));
                    return Ok(true);
                }
                status == "Valid"
            }
            Some((a, b)) => {
                let mut spent = 0;
                let left = eval(a, &model, &[], &mut spent, max_evaluations - work);
                let left = match left {
                    Ok(value) => value,
                    Err(e) if e.code == "ResourceLimit" => {
                        checked += 1;
                        work += spent;
                        outcome = Some(("ResourceLimit", None, "evaluation budget exhausted"));
                        return Ok(true);
                    }
                    Err(e) => return Err(e),
                };
                let right = eval(b, &model, &[], &mut spent, max_evaluations - work);
                checked += 1;
                work += spent;
                match right {
                    Ok(value) => left != value,
                    Err(e) if e.code == "ResourceLimit" => {
                        outcome = Some(("ResourceLimit", None, "evaluation budget exhausted"));
                        return Ok(true);
                    }
                    Err(e) => return Err(e),
                }
            }
        };
        if found {
            outcome = Some(("Found", Some(model.canonical.clone()), ""));
            return Ok(true);
        }
        Ok(false)
    });
    let (status, model, detail) = match search {
        Ok(()) => outcome.unwrap_or(("NotFound", None, "")),
        Err(e) if e.code == "ResourceLimit" && e.message == SEARCH_SPACE => ("ResourceLimit", None, SEARCH_SPACE),
        Err(e) => return Err(e),
    };
    Ok(json!({"id":v.get("id").cloned().unwrap_or(json!("")),"status":status,"model":model,
        "models_checked":checked,"evaluations":work,"max_domain_size":maximum_size,
        "max_models":max_models,"detail":detail}))
}

/// A supplied order countermodel, as Python's `check_countermodel` reports it.
fn order_countermodel_check(env: &Environment, v: &Value) -> Result<Value> {
    let premises = array(v.get("premises").ok_or_else(|| Error::new("InvalidInput", "premises missing"))?)?;
    let conclusion = v.get("conclusion").ok_or_else(|| Error::new("InvalidInput", "conclusion missing"))?;
    ve_kernel::internal::ast_limit(premises.iter().chain([conclusion]))?;
    let mut nodes = 0;
    for f in premises.iter().chain([conclusion]) {
        formula_check(env, f, &[], 1, &mut nodes)?;
    }
    let model = Model::decode(env, v.get("model").ok_or_else(|| Error::new("InvalidInput", "model missing"))?)?;
    let maximum = number(v, "max_evaluations", ve_kernel::MAX_EVALUATIONS)?;
    let (status, values, conclusion_value, work) = countermodel_values(premises, conclusion, &model, maximum)?;
    let meaning = |a: &Value| digest(&format!("ve-meaning-{}\n", env.identity_version()),
                                      &json!({"environment_id":env.environment_id(),"ast":a}));
    Ok(json!({"id":v.get("id").cloned().unwrap_or(json!("")),"valid":status == "Valid",
        "premise_values":values,"conclusion_value":conclusion_value,"evaluations":work,
        "environment_id":env.environment_id(),"model_id":model_id(env, &model)?,"status":status,
        "premise_meaning_ids":premises.iter().map(meaning).collect::<Result<Vec<_>>>()?,
        "conclusion_meaning_id":meaning(conclusion)?}))
}
