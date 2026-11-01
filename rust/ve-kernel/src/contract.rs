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

// The engine (wire-contract.md 2.1 to 2.8), as `lean/VE/WireContract/Engine.lean` runs a table. Rust has no
// hook, classifier or view: the instance that needs one defers (2.8), so Rust never enters a view and a
// record has no `inner_path`. Every unit of work is charged against a stated limit (the DRI's rule of
// 2026-10-27): one unit for each node of the root, read once by the domain pass; each instance and guard
// literal; each value a pattern step reaches; each node a comparison or a type form reads. A run that would
// spend more is refused with `ResourceLimit`, never cut short into an outcome. The record is built once per
// run, from values the domain pass has charged.

use crate::{Error, Result};
use serde_json::{Map, Value as Json, json};

/// The units one run may spend.
pub const MAX_ENGINE_UNITS: u64 = 1_000_000;

/// 2.8: the outcome of one run; a fault holds its record (2.7).
#[derive(Clone, Debug, PartialEq)]
pub enum Outcome {
    Fault(Json),
    Clean,
    Deferred(String),
}

type Pointer = Vec<String>;

/// Under resolved includes (2.7): their ids, outermost first, their sites concatenated and the outermost `as`.
struct Frame {
    ids: Vec<&'static str>,
    site: Pointer,
    recode: Option<(&'static str, &'static str)>,
}

/// Where an instance is read (2.6): its phase, root, enclosing items (innermost first), the earlier items
/// of the innermost group, and its frame.
struct At<'a> {
    phase: &'static str,
    root: &'a Json,
    items: &'a [Pointer],
    earlier: &'a [Pointer],
    frame: &'a Frame,
}

struct Run<'t> {
    table: &'t Table,
    left: u64,
    limit: u64,
}

/// The outcome within `MAX_ENGINE_UNITS`.
pub fn run(table: &Table, root: &Json) -> Result<Outcome> {
    run_within(table, root, MAX_ENGINE_UNITS).map(|(outcome, _)| outcome)
}

/// The outcome and the units spent, within `limit`. The root is the one the unit's adapter built (2.1);
/// a root outside the domain of 2.1 is evaluated no further and is `clean`, as in Python.
pub fn run_within(table: &Table, root: &Json, limit: u64) -> Result<(Outcome, u64)> {
    let mut r = Run { table, left: limit, limit };
    let mut outcome = Outcome::Clean;
    if r.domain(root, 0)? {
        let top = Frame { ids: vec![], site: vec![], recode: None };
        for phase in table.phases {
            let at = At { phase: phase.name, root, items: &[], earlier: &[], frame: &top };
            outcome = r.entries(&at, phase.entries)?;
            if outcome != Outcome::Clean {
                break;
            }
        }
    }
    Ok((outcome, limit - r.left))
}

fn step<'r>(v: &'r Json, token: &str) -> Option<&'r Json> {
    match v {
        Json::Object(m) => m.get(token),
        Json::Array(a) if token == "0" || !token.starts_with('0') && token.bytes().all(|b| b.is_ascii_digit()) => {
            token.parse::<usize>().ok().and_then(|n| a.get(n))
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

/// 2.1: the pointer formed from the base and the tokens, without looking at the value.
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

/// A contract literal equals a value of the same JSON type and content (2.1).
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
    v.as_array().and_then(|xs| xs.iter().map(Json::as_str).collect())
}

fn keys(v: &Json) -> Option<Vec<&str>> {
    v.as_object().map(|m| m.keys().map(String::as_str).collect())
}

/// 2.4: a string is in a lexical class when every member present is satisfied.
fn name_admits(k: &NameClass, s: &str) -> bool {
    let within = |rs: &[(u32, u32)], c: char| rs.iter().any(|&(lo, hi)| lo <= c as u32 && c as u32 <= hi);
    let size = s.len() as u64;
    k.first.is_none_or(|rs| s.chars().next().is_some_and(|c| within(rs, c)))
        && k.rest.is_none_or(|rs| s.chars().skip(1).all(|c| within(rs, c)))
        && k.min_bytes.is_none_or(|n| n <= size)
        && k.max_bytes.is_none_or(|n| size <= n)
        && k.forbid_prefix.iter().all(|x| !s.starts_with(x))
        && k.forbid_infix.iter().all(|x| !s.contains(x))
        && k.one_of.is_none_or(|xs| xs.contains(&s))
}

/// The `json` renderer (2.7): compact, keys in code point order, every character below U+0020 written
/// `\u00xx` in lower case; longer than 80 bytes in UTF-8, the longest prefix of whole characters within
/// 80 bytes and `...`.
fn render_json(v: &Json) -> String {
    let compact = v.to_string();
    let mut out = String::new();
    let mut chars = compact.chars();
    while let Some(c) = chars.next() {
        out.push(c);
        if c == '\\' {
            let next = chars.next().unwrap_or_default();
            match "btnfr".find(next) {
                Some(n) => out.push_str(["u0008", "u0009", "u000a", "u000c", "u000d"][n]),
                None => out.push(next),
            }
        }
    }
    if out.len() <= 80 {
        return out;
    }
    let end = out.char_indices().map(|(i, c)| i + c.len_utf8()).take_while(|&e| e <= 80).last().unwrap_or(0);
    format!("{}...", &out[..end])
}

/// 2.7: the closed renderer set; each is total, and an absent value renders as `""`.
fn render(r: Renderer, v: Option<&Json>) -> String {
    match (r, v) {
        (_, None) => String::new(),
        (Renderer::Raw, Some(Json::String(s))) => s.clone(),
        (Renderer::List, Some(v)) if strings(v).is_some() => {
            let mut ss = strings(v).unwrap_or_default();
            ss.sort();
            ss.join(", ")
        }
        (_, Some(v)) => render_json(v),
    }
}

/// 2.7: each include id and a `/`, outermost first, then the id.
fn check_id(frame: &Frame, id: &str) -> String {
    frame.ids.iter().copied().chain([id]).collect::<Vec<_>>().join("/")
}

impl Run<'_> {
    fn charge(&mut self, units: u64) -> Result<()> {
        if self.left < units {
            return Err(Error::new("ResourceLimit", format!("wire contract engine exceeds {} units", self.limit)));
        }
        self.left -= units;
        Ok(())
    }

    /// 2.1: the restricted values (nesting within 256, integers from 0 to 2^53 - 1), each node charged once.
    fn domain(&mut self, v: &Json, depth: usize) -> Result<bool> {
        self.charge(1)?;
        let inner: Vec<&Json> = match v {
            Json::Number(n) => return Ok(n.as_u64().is_some_and(|n| n < 1 << 53)),
            Json::Array(xs) => xs.iter().collect(),
            Json::Object(m) => m.values().collect(),
            _ => vec![],
        };
        for x in inner {
            if depth >= 256 || !self.domain(x, depth + 1)? {
                return Ok(false);
            }
        }
        Ok(true)
    }

    /// 2.1: every match of a pattern with its pointer, in order.
    fn collect<'r>(&mut self, root: &'r Json, items: &[Pointer], p: &Pattern) -> Result<Vec<(Pointer, &'r Json)>> {
        let mut found: Vec<(Pointer, &'r Json)> = match p.base {
            Base::Root => vec![(vec![], root)],
            Base::Item(n) => match items.get(n as usize) {
                None => vec![],
                Some(at) => {
                    self.charge(at.len() as u64)?;
                    let v = at.iter().try_fold(root, |v, token| step(v, token));
                    v.map(|v| (at.clone(), v)).into_iter().collect()
                }
            },
        };
        for s in p.steps {
            let mut next = Vec::new();
            for (at, v) in found {
                let reached: Vec<(String, &Json)> = match s {
                    Step::Tok(t) => step(v, t).map(|w| (t.to_string(), w)).into_iter().collect(),
                    Step::Star => children(v),
                };
                self.charge(reached.len() as u64)?;
                next.extend(reached.into_iter().map(|(token, w)| ([at.as_slice(), &[token]].concat(), w)));
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
        let pairs: Vec<(&Json, &Json)> = match (a, b) {
            (Json::Array(x), Json::Array(y)) if x.len() == y.len() => x.iter().zip(y).collect(),
            (Json::Object(x), Json::Object(y)) if x.len() == y.len() => {
                match x.iter().map(|(k, v)| y.get(k).map(|w| (v, w))).collect() {
                    Some(pairs) => pairs,
                    None => return Ok(false),
                }
            }
            (Json::Array(_) | Json::Object(_), _) | (_, Json::Array(_) | Json::Object(_)) => return Ok(false),
            _ => return Ok(a == b),
        };
        for (v, w) in pairs {
            if !self.same(v, w)? {
                return Ok(false);
            }
        }
        Ok(true)
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
    fn guard(&mut self, at: &At, literals: &[Lit]) -> Result<bool> {
        for lit in literals {
            self.charge(1)?;
            let (Lit::Present(p) | Lit::Absent(p) | Lit::Equals(p, _) | Lit::Differs(p, _) | Lit::IsType(p, _)
                | Lit::NotType(p, _)) = lit;
            let found = self.resolve(at.root, at.items, p)?.map(|(_, v)| v);
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

    /// 2.6: the instances of each entry, in list order; the first that does not hold is the outcome.
    fn entries(&mut self, at: &At, list: &'static [Entry]) -> Result<Outcome> {
        for entry in list {
            let outcome = self.entry(at, entry)?;
            if outcome != Outcome::Clean {
                return Ok(outcome);
            }
        }
        Ok(Outcome::Clean)
    }

    fn entry(&mut self, at: &At, entry: &'static Entry) -> Result<Outcome> {
        match entry {
            Entry::Check(c) => {
                self.charge(1)?;
                if !self.guard(at, c.guard)? {
                    return Ok(Outcome::Clean);
                }
                self.eval(at, c)
            }
            // Item-major: every instance of one item before the next item's.
            Entry::Each(_, over, guard, inner) => {
                if !self.guard(at, guard)? {
                    return Ok(Outcome::Clean);
                }
                let group: Vec<Pointer> = self.collect(at.root, at.items, over)?.into_iter().map(|(p, _)| p).collect();
                for (n, p) in group.iter().enumerate() {
                    let items = [std::slice::from_ref(p), at.items].concat();
                    let outcome = self.entries(&At { items: &items, earlier: &group[..n], ..*at }, inner)?;
                    if outcome != Outcome::Clean {
                        return Ok(outcome);
                    }
                }
                Ok(Outcome::Clean)
            }
            // A scope whose view Rust lacks contributes one instance, which defers (2.8).
            Entry::Scope(id, loc, view, recode, inner) => match self.resolve(at.root, at.items, loc)? {
                None => Ok(Outcome::Clean),
                Some(_) if view.is_some() => Ok(Outcome::Deferred(check_id(at.frame, id))),
                Some((p, v)) => {
                    let frame = Frame {
                        ids: [at.frame.ids.as_slice(), &[*id]].concat(),
                        site: [at.frame.site.as_slice(), &p].concat(),
                        recode: at.frame.recode.or(*recode),
                    };
                    self.entries(&At { root: v, items: &[], earlier: &[], frame: &frame, ..*at }, inner)
                }
            },
        }
    }

    /// 2.4, 2.5: one instance; a hook or classifier defers.
    fn eval(&mut self, at: &At, c: &'static Check) -> Result<Outcome> {
        let target = self.resolve(at.root, at.items, &c.loc)?;
        let (p, extra) = match (c.kind, &target) {
            (Kind::Hook(_) | Kind::Classifier(..), _) => return Ok(Outcome::Deferred(check_id(at.frame, c.id))),
            (Kind::MaxCount(of, limit), _) => {
                let n = self.collect(at.root, at.items, &of)?.len() as u64;
                if n <= limit {
                    return Ok(Outcome::Clean);
                }
                (concrete(at.items, &c.loc), vec![("count", json!(n)), ("limit", json!(limit))])
            }
            (_, None) => return Ok(Outcome::Clean),
            (_, Some((p, v))) => match self.fails_on(at, c, p, v)? {
                None => return Ok(Outcome::Clean),
                Some(extra) => (p.clone(), extra),
            },
        };
        self.finding(at, c, &p, target.map(|(_, v)| v), &extra)
    }

    /// 2.4: the extra arguments of a failing declarative check on its present target `v` at `p`, or `None`.
    fn fails_on(&mut self, at: &At, c: &Check, p: &Pointer, v: &Json) -> Result<Option<Vec<(&'static str, Json)>>> {
        let bad = |b: bool| if b { Some(vec![]) } else { None };
        let over = |n: u64, m: Option<u64>| m.filter(|m| n < *m).map(|m| vec![("count", json!(m)), ("limit", json!(n))]);
        Ok(match c.kind {
            Kind::HasType(t) => bad(!self.has_type(t, v)?),
            Kind::ExactKeys(ks) => {
                bad(keys(v).is_none_or(|a| !(a.iter().all(|x| ks.contains(x)) && ks.iter().all(|x| a.contains(x)))))
            }
            Kind::Keys(req, opt) => bad(keys(v).is_none_or(|a| {
                !(req.iter().all(|x| a.contains(x)) && a.iter().all(|x| req.contains(x) || opt.contains(x)))
            })),
            Kind::Const(x) => bad(!scalar(v, &x)),
            Kind::OneOf(xs) => bad(!xs.iter().any(|x| scalar(v, x))),
            Kind::MaxItems(n) => over(n, v.as_array().map(Vec::len).or(v.as_object().map(Map::len)).map(|m| m as u64)),
            Kind::MaxBytes(n) => over(n, v.as_str().map(|s| s.len() as u64)),
            Kind::Name(k, false) => bad(v.as_str().is_none_or(|s| !name_admits(&k, s))),
            Kind::Name(k, true) => bad(!name_admits(&k, p.last().map_or("", String::as_str))),
            Kind::SortedUnique => bad(strings(v).is_some_and(|ss| ss.windows(2).any(|w| w[0] >= w[1]))),
            Kind::UniqueSoFar => {
                let mut seen = false;
                for e in at.earlier {
                    let items = [std::slice::from_ref(e), &at.items[1.min(at.items.len())..]].concat();
                    if let Some((_, w)) = self.resolve(at.root, &items, &c.loc)?
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
                for (_, w) in self.collect(at.root, at.items, &set)? {
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
                    bad(xs.iter().any(|w| scalar(w, &x)) == matches!(c.kind, Kind::ExcludesItem(_)))
                }
                _ => None,
            },
            Kind::MaxCount(..) | Kind::Hook(_) | Kind::Classifier(..) => None,
        })
    }

    /// 2.7: the record of an instance that does not hold, at the local pointer `p`.
    fn finding(&mut self, at: &At, c: &Check, p: &Pointer, target: Option<&Json>, extra: &[(&str, Json)])
               -> Result<Outcome> {
        let (mut text, mut args) = (String::new(), Map::new());
        for piece in c.text {
            let (name, renderer) = match piece {
                Piece::Lit(s) => {
                    text.push_str(s);
                    continue;
                }
                Piece::Arg(name, renderer) => (*name, *renderer),
            };
            let key = at.items.first().and_then(|p| p.last()).cloned().unwrap_or_default();
            let named = extra.iter().find(|(n, _)| *n == name).map(|(_, v)| v.clone());
            let value = match (name, named, c.args.iter().find(|(n, _)| *n == name)) {
                ("value", ..) => target.cloned(),
                ("key", ..) => Some(Json::String(key)),
                ("index", ..) => Some(json!(at.earlier.len())),
                (_, Some(v), _) => Some(v),
                (_, None, Some((_, loc))) => self.resolve(at.root, at.items, loc)?.map(|(_, v)| v.clone()),
                (_, None, None) => None,
            };
            let rendered = render(renderer, value.as_ref());
            text.push_str(&rendered);
            args.entry(name).or_insert(Json::String(rendered));
        }
        let (code, cls) = at.frame.recode.unwrap_or((c.code, c.cls));
        Ok(Outcome::Fault(json!({"contract": self.table.contract, "revision": self.table.revision,
            "check": check_id(at.frame, c.id), "phase": at.phase, "code": code, "class": cls,
            "path": pointer_text(&[at.frame.site.as_slice(), p].concat()), "text": text, "args": args})))
    }
}
