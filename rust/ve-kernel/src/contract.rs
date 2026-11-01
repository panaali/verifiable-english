//! Wire contract tables (docs/spec/wire-contract-s4-2.md 3): one type per type of
//! `lean/VE/WireContract/Table.lean`, same constructors, same fields, same order. A generated
//! table (`contract_tables.rs`) is a static value of `Table` that the compiler type-checks. The
//! types are data only; the engine at the end of this file (wire-contract-s4-2.md 7) runs a table
//! as `lean/VE/WireContract/Engine.lean` does. It decides no verdict: its outcome is compared with
//! Lean's, never trusted alone.

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Step {
    Tok(&'static str),
    Star,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Base {
    Root,
    /// The item of the n-th enclosing group; 0 is the innermost.
    Item(u32),
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Pattern {
    pub base: Base,
    pub steps: &'static [Step],
}

/// A scalar literal of a contract (base spec 2.3); it has no `null`.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Value {
    Bool(bool),
    Int(u64),
    Str(&'static str),
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Atom {
    Null,
    Boolean,
    Integer,
    String,
    Array,
    Object,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum TypeForm {
    Atom(Atom),
    ArrayOf(Atom),
    Tuple(&'static [Atom]),
}

/// A literal of a `when` guard.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Lit {
    Present(Pattern),
    Absent(Pattern),
    Equals(Pattern, Value),
    Differs(Pattern, Value),
    IsType(Pattern, &'static [TypeForm]),
    NotType(Pattern, &'static [TypeForm]),
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct NameClass {
    /// Inclusive code point ranges.
    pub first: Option<&'static [(u32, u32)]>,
    pub rest: Option<&'static [(u32, u32)]>,
    pub min_bytes: Option<u64>,
    pub max_bytes: Option<u64>,
    pub forbid_prefix: &'static [&'static str],
    pub forbid_infix: &'static [&'static str],
    pub one_of: Option<&'static [&'static str]>,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Renderer {
    Raw,
    Json,
    Index,
    Count,
    List,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Piece {
    Lit(&'static str),
    Arg(&'static str, Renderer),
}

/// One check of a classifier set (base spec 2.5).
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Member {
    pub id: &'static str,
    pub code: &'static str,
    pub cls: &'static str,
    pub text: &'static [Piece],
    pub inherited: bool,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Kind {
    HasType(&'static [TypeForm]),
    ExactKeys(&'static [&'static str]),
    Keys(&'static [&'static str], &'static [&'static str]),
    Const(Value),
    OneOf(&'static [Value]),
    MaxItems(u64),
    MaxBytes(u64),
    MaxCount(Pattern, u64),
    Name(NameClass, bool),
    SortedUnique,
    UniqueSoFar,
    DeclaredIn(Pattern),
    RequiresMember(&'static str),
    RequiresItem(Value),
    ExcludesMember(&'static str),
    ExcludesItem(Value),
    Hook(&'static str),
    Classifier(&'static str, &'static [Member]),
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Check {
    pub id: &'static str,
    /// `at`
    pub loc: Pattern,
    /// `when`
    pub guard: &'static [Lit],
    pub kind: Kind,
    pub code: &'static str,
    pub cls: &'static str,
    pub text: &'static [Piece],
    pub args: &'static [(&'static str, Pattern)],
    pub inherited: bool,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Entry {
    Check(Check),
    Each(&'static str, Pattern, &'static [Lit], &'static [Entry]),
    /// A resolved `include`: its id, `at`, view, the `as` code with its class, and the inlined entries.
    Scope(&'static str, Pattern, Option<&'static str>, Option<(&'static str, &'static str)>, &'static [Entry]),
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Phase {
    pub name: &'static str,
    pub entries: &'static [Entry],
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Table {
    pub contract: &'static str,
    pub revision: u64,
    /// The residual code and its class.
    pub residual: (&'static str, &'static str),
    pub phases: &'static [Phase],
}

/// A file a generated module was generated from, as its lock names it (wire-contract-s4-2.md 4).
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Source {
    pub file: &'static str,
    pub revision: u64,
    pub sha256: &'static str,
}

// The engine (wire-contract.md 2.1 to 2.8, as `lean/VE/WireContract/Engine.lean`). Rust has no hook,
// classifier or view, so the instance that needs one defers (2.8). Every unit of work is charged against
// a stated limit (the DRI's rule of 2026-10-27): one unit for each node of the root (read once, by the
// domain pass), each instance and guard literal, each value a pattern step reaches, each node a
// comparison, a type form or a rendering reads. A run that would spend more is refused with
// `ResourceLimit`, never cut short into an outcome.

use crate::{Error, Result};
use serde_json::{Map, Value as Json, json};

/// The units one run may spend.
pub const MAX_ENGINE_UNITS: u64 = 1_000_000;
const MAX_SAFE: u64 = (1 << 53) - 1;

/// 2.8: the outcome of one run. A fault holds its record (2.7).
#[derive(Clone, Debug, PartialEq)]
pub enum Outcome {
    Fault(Json),
    Clean,
    Deferred(String),
}

type Pointer = Vec<String>;

struct Frame {
    ids: Vec<&'static str>,
    site: Pointer,
    view_site: Option<Pointer>,
    recode: Option<(&'static str, &'static str)>,
}

struct Run<'t> {
    table: &'t Table,
    left: u64,
    limit: u64,
}

/// 2.1, 2.6 to 2.8 within `MAX_ENGINE_UNITS`.
pub fn run(table: &Table, root: &Json) -> Result<Outcome> {
    run_within(table, root, MAX_ENGINE_UNITS).map(|(outcome, _)| outcome)
}

/// The outcome and the units spent, within `limit` units. The root is the one the unit's adapter
/// built (2.1); a root outside the domain of 2.1 is evaluated no further and is `clean`, as in Python.
pub fn run_within(table: &Table, root: &Json, limit: u64) -> Result<(Outcome, u64)> {
    let mut r = Run { table, left: limit, limit };
    if !r.domain(root, 0)? {
        return Ok((Outcome::Clean, limit - r.left));
    }
    let top = Frame { ids: vec![], site: vec![], view_site: None, recode: None };
    for phase in table.phases {
        let outcome = r.entries(phase.name, root, &[], &[], &top, phase.entries)?;
        if outcome != Outcome::Clean {
            return Ok((outcome, limit - r.left));
        }
    }
    Ok((Outcome::Clean, limit - r.left))
}

/// 2.8, the overlay without Lean: the legacy rejection with `diagnostic` set to the fault record, the
/// residual record when the run is clean, or the deferred record. `code`, `message` and `span` are kept.
pub fn overlay(table: &Table, legacy: Error, outcome: &Outcome) -> Error {
    let diagnostic = match outcome {
        Outcome::Fault(record) => record.clone(),
        Outcome::Clean => json!({"contract": table.contract, "revision": table.revision, "check": "residual",
            "phase": "residual", "code": table.residual.0, "class": table.residual.1, "path": "",
            "text": legacy.message, "args": {}}),
        Outcome::Deferred(id) => json!({"contract": table.contract, "revision": table.revision,
            "deferred": id, "text": legacy.message}),
    };
    Error { diagnostic: Some(diagnostic), ..legacy }
}

fn step<'r>(v: &'r Json, token: &str) -> Option<&'r Json> {
    match v {
        Json::Object(m) => m.get(token),
        Json::Array(a) => {
            let index = !token.is_empty()
                && token.bytes().all(|b| b.is_ascii_digit())
                && (token.len() == 1 || !token.starts_with('0'));
            if index { token.parse::<usize>().ok().and_then(|n| a.get(n)) } else { None }
        }
        _ => None,
    }
}

/// An object's members in code point order of the keys (2.1), or an array's elements with their indices.
fn children(v: &Json) -> Vec<(String, &Json)> {
    match v {
        Json::Object(m) => {
            let mut members: Vec<(String, &Json)> = m.iter().map(|(k, w)| (k.clone(), w)).collect();
            members.sort_by(|a, b| a.0.cmp(&b.0));
            members
        }
        Json::Array(a) => a.iter().enumerate().map(|(n, w)| (n.to_string(), w)).collect(),
        _ => vec![],
    }
}

fn concrete(items: &[Pointer], p: &Pattern) -> Pointer {
    let mut out = match p.base {
        Base::Root => vec![],
        Base::Item(n) => items.get(n as usize).cloned().unwrap_or_default(),
    };
    out.extend(p.steps.iter().filter_map(|s| match s {
        Step::Tok(t) => Some(t.to_string()),
        Step::Star => None,
    }));
    out
}

fn pointer_text(p: &[String]) -> String {
    p.iter().map(|s| format!("/{}", s.replace('~', "~0").replace('/', "~1"))).collect()
}

fn scalar(v: &Json, x: &Value) -> bool {
    match (v, x) {
        (Json::Bool(a), Value::Bool(b)) => a == b,
        (Json::Number(a), Value::Int(b)) => a.as_u64() == Some(*b),
        (Json::String(a), Value::Str(b)) => a == b,
        _ => false,
    }
}

fn admits(atom: Atom, v: &Json) -> bool {
    matches!((atom, v), (Atom::Null, Json::Null) | (Atom::Boolean, Json::Bool(_)) | (Atom::Integer, Json::Number(_))
        | (Atom::String, Json::String(_)) | (Atom::Array, Json::Array(_)) | (Atom::Object, Json::Object(_)))
}

fn strings(v: &Json) -> Option<Vec<&str>> {
    match v {
        Json::Array(xs) => xs.iter().map(Json::as_str).collect(),
        _ => None,
    }
}

fn keys(v: &Json) -> Option<Vec<&str>> {
    v.as_object().map(|m| m.keys().map(String::as_str).collect())
}

fn in_ranges(ranges: &[(u32, u32)], c: char) -> bool {
    ranges.iter().any(|&(lo, hi)| lo <= c as u32 && c as u32 <= hi)
}

/// 2.4: a string is in a lexical class when every member present is satisfied.
fn name_admits(k: &NameClass, s: &str) -> bool {
    let size = s.len() as u64;
    k.first.is_none_or(|rs| s.chars().next().is_some_and(|c| in_ranges(rs, c)))
        && k.rest.is_none_or(|rs| s.chars().skip(1).all(|c| in_ranges(rs, c)))
        && k.min_bytes.is_none_or(|n| n <= size)
        && k.max_bytes.is_none_or(|n| size <= n)
        && k.forbid_prefix.iter().all(|x| !s.starts_with(x))
        && k.forbid_infix.iter().all(|x| !s.contains(x))
        && k.one_of.is_none_or(|xs| xs.contains(&s))
}

/// The longest prefix of whole characters within 80 bytes in UTF-8, with `...` added, for a longer string.
fn cut(s: String) -> String {
    if s.len() <= 80 {
        return s;
    }
    let mut end = 0;
    for (i, c) in s.char_indices() {
        if i + c.len_utf8() > 80 {
            break;
        }
        end = i + c.len_utf8();
    }
    format!("{}...", &s[..end])
}

impl Run<'_> {
    fn charge(&mut self, units: u64) -> Result<()> {
        if self.left < units {
            return Err(Error::new("ResourceLimit", format!("wire contract engine exceeds {} units", self.limit)));
        }
        self.left -= units;
        Ok(())
    }

    /// 2.1: the restricted values, each node charged once.
    fn domain(&mut self, v: &Json, depth: usize) -> Result<bool> {
        self.charge(1)?;
        if depth > 256 {
            return Ok(false);
        }
        Ok(match v {
            Json::Null | Json::Bool(_) => true,
            Json::Number(n) => n.as_u64().is_some_and(|n| n <= MAX_SAFE),
            Json::String(_) => true,
            Json::Array(xs) => {
                for x in xs {
                    if !self.domain(x, depth + 1)? {
                        return Ok(false);
                    }
                }
                true
            }
            Json::Object(m) => {
                for x in m.values() {
                    if !self.domain(x, depth + 1)? {
                        return Ok(false);
                    }
                }
                true
            }
        })
    }

    /// 2.1: every match of a pattern with its pointer, in order.
    fn collect<'r>(&mut self, root: &'r Json, items: &[Pointer], p: &Pattern) -> Result<Vec<(Pointer, &'r Json)>> {
        let start = match p.base {
            Base::Root => Some((vec![], root)),
            Base::Item(n) => match items.get(n as usize) {
                None => None,
                Some(at) => {
                    let mut v = Some(root);
                    for token in at {
                        self.charge(1)?;
                        v = v.and_then(|v| step(v, token));
                    }
                    v.map(|v| (at.clone(), v))
                }
            },
        };
        let mut found: Vec<(Pointer, &'r Json)> = start.into_iter().collect();
        for s in p.steps {
            let mut next = Vec::new();
            for (at, v) in found {
                let reached: Vec<(String, &Json)> = match s {
                    Step::Tok(t) => step(v, t).map(|w| (t.to_string(), w)).into_iter().collect(),
                    Step::Star => children(v),
                };
                self.charge(reached.len() as u64)?;
                for (token, w) in reached {
                    let mut p = at.clone();
                    p.push(token);
                    next.push((p, w));
                }
            }
            found = next;
        }
        Ok(found)
    }

    fn resolve<'r>(&mut self, root: &'r Json, items: &[Pointer], p: &Pattern) -> Result<Option<(Pointer, &'r Json)>> {
        Ok(self.collect(root, items, p)?.into_iter().next())
    }

    /// 2.1: the same JSON type and content, one unit per node read.
    fn same(&mut self, a: &Json, b: &Json) -> Result<bool> {
        self.charge(1)?;
        Ok(match (a, b) {
            (Json::Array(x), Json::Array(y)) => {
                if x.len() != y.len() {
                    return Ok(false);
                }
                for (v, w) in x.iter().zip(y) {
                    if !self.same(v, w)? {
                        return Ok(false);
                    }
                }
                true
            }
            (Json::Object(x), Json::Object(y)) => {
                if x.len() != y.len() {
                    return Ok(false);
                }
                for (k, v) in x {
                    match y.get(k) {
                        Some(w) if self.same(v, w)? => {}
                        _ => return Ok(false),
                    }
                }
                true
            }
            (Json::Array(_) | Json::Object(_), _) | (_, Json::Array(_) | Json::Object(_)) => false,
            _ => a == b,
        })
    }

    /// 2.3: a value of one of the forms.
    fn has_type(&mut self, forms: &[TypeForm], v: &Json) -> Result<bool> {
        for form in forms {
            self.charge(1 + v.as_array().map_or(0, |xs| xs.len() as u64))?;
            let holds = match (form, v) {
                (TypeForm::Atom(a), _) => admits(*a, v),
                (TypeForm::ArrayOf(a), Json::Array(xs)) => xs.iter().all(|x| admits(*a, x)),
                (TypeForm::Tuple(parts), Json::Array(xs)) => {
                    xs.len() == parts.len() && parts.iter().zip(xs).all(|(a, x)| admits(*a, x))
                }
                _ => false,
            };
            if holds {
                return Ok(true);
            }
        }
        Ok(false)
    }

    /// 2.3: every literal of the guard holds.
    fn guard(&mut self, root: &Json, items: &[Pointer], literals: &[Lit]) -> Result<bool> {
        for lit in literals {
            self.charge(1)?;
            let (Lit::Present(p) | Lit::Absent(p) | Lit::Equals(p, _) | Lit::Differs(p, _) | Lit::IsType(p, _)
                | Lit::NotType(p, _)) = lit;
            let found = self.resolve(root, items, p)?.map(|(_, v)| v);
            let holds = match (lit, found) {
                (Lit::Present(_), w) => w.is_some(),
                (Lit::Absent(_), w) => w.is_none(),
                (Lit::Equals(_, x), Some(w)) => scalar(w, x),
                (Lit::Differs(_, x), Some(w)) => !scalar(w, x),
                (Lit::IsType(_, t), Some(w)) => self.has_type(t, w)?,
                (Lit::NotType(_, t), Some(w)) => !self.has_type(t, w)?,
                (Lit::Differs(..) | Lit::NotType(..), None) => true,
                (Lit::Equals(..) | Lit::IsType(..), None) => false,
            };
            if !holds {
                return Ok(false);
            }
        }
        Ok(true)
    }

    fn entries(&mut self, phase: &'static str, root: &Json, items: &[Pointer], earlier: &[Pointer], frame: &Frame,
               list: &'static [Entry]) -> Result<Outcome> {
        for entry in list {
            let outcome = self.entry(phase, root, items, earlier, frame, entry)?;
            if outcome != Outcome::Clean {
                return Ok(outcome);
            }
        }
        Ok(Outcome::Clean)
    }

    /// 2.6: the instances of one entry, evaluated in order; the first that does not hold is the outcome.
    fn entry(&mut self, phase: &'static str, root: &Json, items: &[Pointer], earlier: &[Pointer], frame: &Frame,
             entry: &'static Entry) -> Result<Outcome> {
        match entry {
            Entry::Check(c) => {
                self.charge(1)?;
                if !self.guard(root, items, c.guard)? {
                    return Ok(Outcome::Clean);
                }
                self.eval(phase, root, items, earlier, frame, c)
            }
            Entry::Each(_, over, guard, inner) => {
                if !self.guard(root, items, guard)? {
                    return Ok(Outcome::Clean);
                }
                let group: Vec<Pointer> = self.collect(root, items, over)?.into_iter().map(|(p, _)| p).collect();
                for (n, p) in group.iter().enumerate() {
                    let mut within = vec![p.clone()];
                    within.extend_from_slice(items);
                    let outcome = self.entries(phase, root, &within, &group[..n], frame, inner)?;
                    if outcome != Outcome::Clean {
                        return Ok(outcome);
                    }
                }
                Ok(Outcome::Clean)
            }
            Entry::Scope(id, at, view, recode, inner) => {
                let Some((p, v)) = self.resolve(root, items, at)? else {
                    return Ok(Outcome::Clean);
                };
                if view.is_some() {
                    return Ok(Outcome::Deferred(check_id(frame, id)));
                }
                let mut site = frame.site.clone();
                site.extend(p);
                let inside = Frame {
                    ids: frame.ids.iter().copied().chain([*id]).collect(),
                    site,
                    view_site: frame.view_site.clone(),
                    recode: frame.recode.or(*recode),
                };
                self.entries(phase, v, &[], &[], &inside, inner)
            }
        }
    }

    /// 2.4, 2.5: one instance. A hook or classifier defers.
    fn eval(&mut self, phase: &'static str, root: &Json, items: &[Pointer], earlier: &[Pointer], frame: &Frame,
            c: &'static Check) -> Result<Outcome> {
        let target = self.resolve(root, items, &c.loc)?;
        let extra = match c.kind {
            Kind::Hook(_) | Kind::Classifier(..) => return Ok(Outcome::Deferred(check_id(frame, c.id))),
            Kind::MaxCount(of, limit) => {
                let n = self.collect(root, items, &of)?.len() as u64;
                if n <= limit {
                    return Ok(Outcome::Clean);
                }
                let place = Instance { phase, root, items, earlier, frame, check: c };
                let found = target.map(|(_, v)| v);
                return self.finding(&place, &concrete(items, &c.loc), found, &[("count", json!(n)), ("limit", json!(limit))]);
            }
            _ => match target {
                None => return Ok(Outcome::Clean),
                Some((ref p, v)) => match self.fails_on(root, items, earlier, c, p, v)? {
                    None => return Ok(Outcome::Clean),
                    Some(extra) => extra,
                },
            },
        };
        let (p, v) = target.expect("a failing declarative check has a target");
        let place = Instance { phase, root, items, earlier, frame, check: c };
        self.finding(&place, &p, Some(v), &extra)
    }

    /// 2.4: the extra arguments of a failing declarative check on its present target `v` at `p`, or `None`.
    fn fails_on(&mut self, root: &Json, items: &[Pointer], earlier: &[Pointer], c: &Check, p: &Pointer, v: &Json)
                -> Result<Option<Vec<(&'static str, Json)>>> {
        let bad = |b: bool| if b { Some(vec![]) } else { None };
        Ok(match c.kind {
            Kind::HasType(t) => bad(!self.has_type(t, v)?),
            Kind::ExactKeys(ks) => bad(keys(v).is_none_or(|a| !(a.iter().all(|x| ks.contains(x))
                && ks.iter().all(|x| a.contains(x))))),
            Kind::Keys(req, opt) => bad(keys(v).is_none_or(|a| !(req.iter().all(|x| a.contains(x))
                && a.iter().all(|x| req.contains(x) || opt.contains(x))))),
            Kind::Const(x) => bad(!scalar(v, &x)),
            Kind::OneOf(xs) => bad(!xs.iter().any(|x| scalar(v, x))),
            Kind::MaxItems(n) => {
                let m = match v {
                    Json::Array(xs) => Some(xs.len() as u64),
                    Json::Object(m) => Some(m.len() as u64),
                    _ => None,
                };
                m.filter(|m| n < *m).map(|m| vec![("count", json!(m)), ("limit", json!(n))])
            }
            Kind::MaxBytes(n) => match v {
                Json::String(s) if n < s.len() as u64 => Some(vec![("count", json!(s.len())), ("limit", json!(n))]),
                _ => None,
            },
            Kind::Name(k, false) => bad(v.as_str().is_none_or(|s| !name_admits(&k, s))),
            Kind::Name(k, true) => bad(!name_admits(&k, p.last().map_or("", String::as_str))),
            Kind::SortedUnique => bad(strings(v).is_some_and(|ss| ss.windows(2).any(|w| w[0] >= w[1]))),
            Kind::UniqueSoFar => {
                let mut seen = false;
                for e in earlier {
                    let mut at = vec![e.clone()];
                    at.extend_from_slice(&items[1.min(items.len())..]);
                    if let Some((_, w)) = self.resolve(root, &at, &c.loc)?
                        && self.same(w, v)?
                    {
                        seen = true;
                        break;
                    }
                }
                bad(seen)
            }
            Kind::DeclaredIn(set) => {
                let mut declared = false;
                for (_, w) in self.collect(root, items, &set)? {
                    if self.same(v, w)? {
                        declared = true;
                        break;
                    }
                }
                bad(!declared)
            }
            Kind::RequiresMember(key) => bad(keys(v).is_some_and(|a| !a.contains(&key))),
            Kind::ExcludesMember(key) => bad(keys(v).is_some_and(|a| a.contains(&key))),
            Kind::RequiresItem(x) | Kind::ExcludesItem(x) => match v {
                Json::Array(xs) => {
                    self.charge(xs.len() as u64)?;
                    let present = xs.iter().any(|w| scalar(w, &x));
                    bad(present == matches!(c.kind, Kind::ExcludesItem(_)))
                }
                _ => None,
            },
            Kind::MaxCount(..) | Kind::Hook(_) | Kind::Classifier(..) => None,
        })
    }

    /// 2.7: the record of an instance that does not hold, at the local pointer `p`.
    fn finding(&mut self, i: &Instance, p: &Pointer, target: Option<&Json>, extra: &[(&'static str, Json)])
               -> Result<Outcome> {
        let c = i.check;
        let mut text = String::new();
        let mut args = Map::new();
        for piece in c.text {
            match piece {
                Piece::Lit(s) => text.push_str(s),
                Piece::Arg(name, renderer) => {
                    let rendered = match *name {
                        "value" => self.render(*renderer, target)?,
                        "key" => {
                            let key = i.items.first().and_then(|p| p.last()).cloned().unwrap_or_default();
                            self.render(*renderer, Some(&Json::String(key)))?
                        }
                        "index" => self.render(*renderer, Some(&json!(i.earlier.len())))?,
                        _ => match extra.iter().find(|(n, _)| n == name) {
                            Some((_, v)) => self.render(*renderer, Some(v))?,
                            None => match c.args.iter().find(|(n, _)| n == name) {
                                Some((_, at)) => {
                                    let found = self.resolve(i.root, i.items, at)?;
                                    self.render(*renderer, found.map(|(_, v)| v))?
                                }
                                None => String::new(),
                            },
                        },
                    };
                    text.push_str(&rendered);
                    args.entry(name.to_string()).or_insert(Json::String(rendered));
                }
            }
        }
        let (code, cls) = i.frame.recode.unwrap_or((c.code, c.cls));
        let mut local = i.frame.site.clone();
        local.extend(p.iter().cloned());
        let path = match &i.frame.view_site {
            Some(site) => {
                args.insert("inner_path".into(), Json::String(pointer_text(&local)));
                pointer_text(site)
            }
            None => pointer_text(&local),
        };
        Ok(Outcome::Fault(json!({"contract": self.table.contract, "revision": self.table.revision,
            "check": check_id(i.frame, c.id), "phase": i.phase, "code": code, "class": cls, "path": path,
            "text": text, "args": args})))
    }

    /// 2.7: the closed renderer set; every renderer is total and an absent value renders as `""`.
    fn render(&mut self, r: Renderer, v: Option<&Json>) -> Result<String> {
        let Some(v) = v else { return Ok(String::new()) };
        match (r, v) {
            (Renderer::Raw, Json::String(s)) => Ok(s.clone()),
            (Renderer::List, _) if strings(v).is_some() => {
                let mut ss = strings(v).unwrap_or_default();
                self.charge(ss.len() as u64)?;
                ss.sort();
                Ok(ss.join(", "))
            }
            _ => {
                let mut out = String::new();
                self.encode(v, &mut out)?;
                Ok(cut(out))
            }
        }
    }

    /// Compact JSON, keys in code point order, `"`, `\` and characters below U+0020 escaped (`\u00xx`);
    /// it stops once past 80 bytes, which is all `cut` reads.
    fn encode(&mut self, v: &Json, out: &mut String) -> Result<()> {
        self.charge(1)?;
        if out.len() > 80 {
            return Ok(());
        }
        match v {
            Json::Null => out.push_str("null"),
            Json::Bool(b) => out.push_str(if *b { "true" } else { "false" }),
            Json::Number(n) => out.push_str(&n.to_string()),
            Json::String(s) => {
                out.push('"');
                for c in s.chars() {
                    if out.len() > 80 {
                        return Ok(());
                    }
                    match c {
                        '"' => out.push_str("\\\""),
                        '\\' => out.push_str("\\\\"),
                        c if (c as u32) < 0x20 => out.push_str(&format!("\\u{:04x}", c as u32)),
                        c => out.push(c),
                    }
                }
                out.push('"');
            }
            Json::Array(xs) => {
                out.push('[');
                for (n, x) in xs.iter().enumerate() {
                    if n > 0 {
                        out.push(',');
                    }
                    self.encode(x, out)?;
                    if out.len() > 80 {
                        return Ok(());
                    }
                }
                out.push(']');
            }
            Json::Object(_) => {
                out.push('{');
                for (n, (k, x)) in children(v).into_iter().enumerate() {
                    if n > 0 {
                        out.push(',');
                    }
                    self.encode(&Json::String(k), out)?;
                    out.push(':');
                    self.encode(x, out)?;
                    if out.len() > 80 {
                        return Ok(());
                    }
                }
                out.push('}');
            }
        }
        Ok(())
    }
}

struct Instance<'a> {
    phase: &'static str,
    root: &'a Json,
    items: &'a [Pointer],
    earlier: &'a [Pointer],
    frame: &'a Frame,
    check: &'static Check,
}

/// 2.7: each include id and a `/`, outermost first, then the check's or the include's id.
fn check_id(frame: &Frame, id: &str) -> String {
    frame.ids.iter().copied().chain([id]).collect::<Vec<_>>().join("/")
}
