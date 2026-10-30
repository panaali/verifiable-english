use crate::{
    Error, Formula, Result,
    ast::{check_in_context, decode_formula, has_reach},
    canonical_json, dependency_order, digest, error, loads_json,
    model::definition_premise,
    wire::{fields, object},
};
use serde_json::{Value, json};
use std::collections::{BTreeMap, BTreeSet};

pub(crate) const RESERVED: &[&str] = &[
    "true",
    "false",
    "is",
    "equals",
    "not",
    "and",
    "or",
    "if",
    "then",
    "for",
    "every",
    "there",
    "exists",
    "believes",
    "must",
    "eventually",
    "no",
];
pub(crate) fn identifier(s: &str, code: &str) -> Result<()> {
    // Schema names follow Python's character-count check before ASCII syntax.
    // Model local IDs check syntax first, then the length of the ASCII ID.
    if code != "InvalidModel" && s.chars().count() > 64 {
        return error("ResourceLimit", "identifier exceeds 64 bytes");
    }
    if !s.as_bytes().first().is_some_and(u8::is_ascii_lowercase)
        || !s
            .bytes()
            .all(|b| b.is_ascii_lowercase() || b.is_ascii_digit() || b == b'_')
    {
        return error(code, format!("invalid ASCII identifier {s:?}"));
    }
    if s.len() > 64 {
        return error("ResourceLimit", "identifier exceeds 64 bytes");
    }
    Ok(())
}
pub(crate) fn string<'a>(v: &'a Value, code: &str) -> Result<&'a str> {
    v.as_str()
        .ok_or_else(|| Error::new(code, "expected a string"))
}
fn description(v: &Value) -> Result<()> {
    if string(v, "InvalidInput")?.is_empty() {
        return error("InvalidInput", "empty description");
    }
    Ok(())
}
fn verbalisation(v: &Value) -> Result<()> {
    description(v)?;
    if v.as_str().unwrap().chars().count() > 256 {
        return error("ResourceLimit", "verbalisation exceeds 256 characters");
    }
    Ok(())
}
fn entry_fields<'a>(
    v: &'a Value,
    required: &[&str],
    negative: bool,
    regulated: bool,
) -> Result<&'a serde_json::Map<String, Value>> {
    let mut keys = required.to_vec();
    if v.get("verbalisation").is_some() {
        keys.push("verbalisation");
    }
    if negative && v.get("negative_verbalisation").is_some() {
        keys.push("negative_verbalisation");
    }
    if regulated && v.get("regulated").is_some() {
        keys.push("regulated");
    }
    fields(v, &keys, "InvalidInput")
}

/// Python `str.isspace`, the separators of the no-argument `str.split()` that
/// normalises act phrases; wider than `char::is_whitespace` (U+001C..U+001F).
fn py_whitespace(c: char) -> bool {
    matches!(c, '\u{09}'..='\u{0d}' | '\u{1c}'..='\u{20}' | '\u{85}' | '\u{a0}' | '\u{1680}'
        | '\u{2000}'..='\u{200a}' | '\u{2028}' | '\u{2029}' | '\u{202f}' | '\u{205f}' | '\u{3000}')
}

fn py_words(text: &str) -> impl Iterator<Item = &str> {
    text.split(py_whitespace).filter(|word| !word.is_empty())
}

fn act_phrase(value: &Value, arity: usize) -> Result<String> {
    let raw = string(value, "InvalidInput")?;
    let act = py_words(raw).collect::<Vec<_>>().join(" ");
    let slots: Vec<_> = (0..arity).map(|i| format!("{{{i}}}")).collect();
    let mut cursor = 0;
    for slot in &slots {
        if act.matches(slot).count() != 1 {
            return error("InvalidInput", "invalid act phrase slots");
        }
        let Some(i) = act[cursor..].find(slot) else {
            return error("InvalidInput", "invalid act phrase slots");
        };
        cursor += i + slot.len();
    }
    let mut plain = act.clone();
    for slot in slots.iter().rev() {
        plain = plain.replace(slot, "slot");
    }
    if act.chars().count() > 80 || !act.starts_with("{0} ") || py_words(&plain).count() < 2 ||
        py_words(&plain).any(|word|
            !word.as_bytes().first().is_some_and(u8::is_ascii_alphabetic)
            || !word.bytes().all(|b| b.is_ascii_alphabetic() || b == b'\'' || b == b'-')
            || (word != "slot" && RESERVED.contains(&word.to_ascii_lowercase().as_str()))) {
        return error("InvalidInput", "invalid act phrase");
    }
    Ok(act)
}

/// The checker family of a `ve.core@0.2` profile list (`VE.Route.Gate.classify`).
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) enum Family {
    Fol,
    Order,
    Nary,
}

/// The Lean decoder that judges an environment's argument and constant sorts,
/// chosen as Lean's `environment` mode chooses it
/// (lean/VE/Service/Standalone.lean `reportedEnvironment`, `validatedLayerEnvironment`,
/// `validated`). The one table of every sort fault: the decoder loop asks it and
/// decides nothing about a sort itself.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) enum SortJudge {
    /// `ve.core@0`, `ve.core@0.1`: the frozen decoders (`Standalone.decodeLegacy`);
    /// `order` is the frozen order envelope.
    Legacy { order: bool },
    /// `ve.core@0.2` over the frozen checker profiles (`frozenFamilyProfiles`,
    /// Standalone.lean:350): the located decoder checks the constants before the
    /// family decoder judges a cell it skipped (Standalone.lean:957-958).
    Located(Family),
    /// `VE.Route.Wire.decodeVocabulary` (lean/VE/Route/Wire.lean:170-172, 196): composed
    /// fol and closure lists, the norms route, and soft-norms@0, which decodes its
    /// vocabulary without the checker profiles (lean/VE/SoftNorms/Phases.lean:137-154).
    Route,
    /// `VE.Order.Wire.decodeEnvironment` (lean/VE/Order/Wire.lean:74, 83).
    Order,
    /// `VE.Core.Bridge.decodeEnvironment` (lean/VE/Core/Bridge.lean:38, 51).
    Core,
    /// `VE.Core.Layers.decodeLayered` (lean/VE/Core/Layers.lean:64-80, 229-232): the route
    /// decoder over the binary undefined predicates and the constants, then the core decoder.
    Layered,
}

/// Lean's answer for one undeclared argument cell.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) enum SortVerdict {
    Accepted,
    /// This code at the cell, before the constants.
    AtSort(&'static str),
    /// This code once the constants are checked.
    AfterConstants(&'static str),
}

fn sort_fault<T>(code: &'static str) -> Result<T> {
    error(code, if code == "InvalidInput" { "invalid predicate signature" } else { "unknown predicate argument sort" })
}

const CHECKER_PROFILES: &[&str] =&["relational-fol@0", "closure@0", "nary@0", "order@0"];

impl SortJudge {
    /// `layers`: some predicate carries `defined`, `functional` or `total`
    /// (`VE.Core.Layers.usesLayers`, Standalone.lean:208).
    pub(crate) fn of(route: bool, legacy_order: bool, profiles: &[String], layers: bool) -> Self {
        if !route {
            return SortJudge::Legacy { order: legacy_order };
        }
        let has = |p: &str| profiles.iter().any(|q| q == p);
        let family = if has("order@0") {
            Family::Order
        } else if has("nary@0") {
            Family::Nary
        } else {
            Family::Fol
        };
        if !profiles.is_empty() && profiles.iter().all(|p| CHECKER_PROFILES.contains(&p.as_str())) {
            return SortJudge::Located(family);
        }
        if has("soft-norms@0") {
            return SortJudge::Route;
        }
        match family {
            Family::Order => SortJudge::Order,
            Family::Nary if layers => SortJudge::Layered,
            Family::Nary => SortJudge::Core,
            Family::Fol => SortJudge::Route,
        }
    }

    /// The verdict on an undeclared cell `sort` of a predicate of `arity`
    /// (`defined`: it carries a definition), under `data@0` when `data`.
    pub(crate) fn argument(self, sort: &str, data: bool, arity: usize, defined: bool) -> SortVerdict {
        use SortVerdict::*;
        match self {
            // Bridge.lean:44, Order/Wire.lean:74: only the order envelope adds `$int`.
            SortJudge::Legacy { order } => if order && sort == "$int" { Accepted } else { AtSort("UnknownSymbol") },
            // The family decoder after the located one: the route decoder's
            // "invalid signature" (Route/Wire.lean:170-172), the order and core
            // decoders' unknown sort (Order/Wire.lean:74, Core/Bridge.lean:38).
            SortJudge::Located(Family::Fol) => AfterConstants("InvalidInput"),
            SortJudge::Located(Family::Order) | SortJudge::Order if sort == "$int" => Accepted,
            SortJudge::Located(_) => AfterConstants("UnknownSymbol"),
            SortJudge::Route => if data && sort == "$string" { Accepted } else { AtSort("InvalidInput") },
            SortJudge::Order | SortJudge::Core => AtSort("UnknownSymbol"),
            SortJudge::Layered => match SortJudge::Route.argument(sort, data, arity, defined) {
                AtSort(code) if arity <= 2 && !defined => AtSort(code),
                _ => AfterConstants("UnknownSymbol"),
            },
        }
    }

    /// Whether an undeclared constant sort is admitted: `$string` literals
    /// everywhere on the route, `$int` under the order decoders.
    pub(crate) fn constant_admits(self, sort: &str) -> bool {
        match self {
            SortJudge::Legacy { order } => order && sort == "$int",
            SortJudge::Located(family) => sort == "$string" || (family == Family::Order && sort == "$int"),
            SortJudge::Order => sort == "$string" || sort == "$int",
            SortJudge::Route | SortJudge::Core | SortJudge::Layered => sort == "$string",
        }
    }

    /// The code of an undeclared constant sort: the route decoder's
    /// "unknown constant sort" (Route/Wire.lean:196), else the shared
    /// `constantSort` validator's (Bridge.lean:58).
    pub(crate) fn constant_fault(self) -> &'static str {
        match self {
            SortJudge::Route | SortJudge::Layered => "InvalidInput",
            _ => "UnknownSymbol",
        }
    }
}

/// The located decoder's pass over the predicates (Standalone.lean:942-967), which
/// precedes every family decoder on `ve.core@0.2`: a cell it does not skip
/// (Standalone.lean:957-958) and that it does not admit is UnknownSymbol, unless an
/// earlier located fault ends the pass first.
fn located_argument_fault(
    preds: &serde_json::Map<String, Value>,
    sorts: &serde_json::Map<String, Value>,
    profiles: &[String],
) -> Result<()> {
    const OPTIONAL: &[&str] = &["defined", "functional", "total", "regulated", "argument_units",
        "instruction_of", "verbalisation", "negative_verbalisation"];
    let has = |p: &str| profiles.iter().any(|q| q == p);
    let (order, data) = (has("order@0"), has("data@0"));
    let maximum = if has("nary@0") { 6 } else { 2 };
    for entry in preds.values() {
        let Some(entry) = entry.as_object() else { return Ok(()) };
        if !entry.contains_key("arguments") || !entry.contains_key("description")
            || entry.keys().any(|k| k != "arguments" && k != "description" && !OPTIONAL.contains(&k.as_str())) {
            return Ok(());
        }
        let Some(cells) = entry["arguments"].as_array().filter(|a| (1..=maximum).contains(&a.len())) else {
            return Ok(());
        };
        let skipped = (!data && cells.contains(&json!("$string"))) || (!order && cells.contains(&json!("$int")));
        if !skipped && cells.iter().any(|cell| !cell.as_str().is_some_and(|s|
                sorts.contains_key(s) || (order && s == "$int") || (data && s == "$string"))) {
            return error("UnknownSymbol", "unknown predicate argument sort");
        }
        if let Some(defined) = entry.get("defined") {
            if fields(defined, &["arguments", "body"], "InvalidInput").is_err() {
                return Ok(());
            }
        }
        if description(&entry["description"]).is_err() {
            return Ok(());
        }
    }
    Ok(())
}

#[derive(Clone, Debug)]
pub struct Environment {
    closure: bool,
    order: bool,
    route: bool,
    profiles: Vec<String>,
    pub(crate) sorts: BTreeSet<String>,
    pub(crate) predicates: BTreeMap<String, Vec<String>>,
    pub(crate) predicate_flags: BTreeMap<String, (bool, bool)>,
    pub(crate) constants: BTreeMap<String, String>,
    pub(crate) profile_pairs: Vec<(String, String)>,
    /// Identity-bound definitions (W3), in dependency order.
    pub(crate) definitions: Vec<(String, Vec<String>, Formula)>,
    /// Premises a validated soft document adds to Background (Python's
    /// `soft_premises` slot); never part of the environment JSON or identity.
    pub(crate) soft_premises: Vec<Formula>,
    data: Value,
    id: String,
}
impl Environment {
    pub fn from_json(bytes: &[u8]) -> Result<Self> {
        Self::from_value(&loads_json(bytes)?)
    }
    pub fn from_value(data: &Value) -> Result<Self> {
        canonical_json(data)?;
        let route = data.get("language") == Some(&json!("ve.core@0.2"));
        let modern = route || data.get("language") == Some(&json!("ve.core@0.1"));
        let order = data.get("profiles") == Some(&json!(["order@0", "relational-fol@0"]));
        let closure = modern && !route && !order;
        let reports = route && data.get("profiles").and_then(Value::as_array)
            .is_some_and(|p| p.contains(&json!("reports@0")));
        let envelope = vec!["language", if modern { "profiles" } else { "profile" },
                            "spec_revision", "vocabulary"];
        let obj = fields(data, &envelope, "InvalidInput")?;
        let profiles: Vec<String> = if route {
            obj["profiles"]
                .as_array()
                .ok_or_else(|| {
                    Error::new(
                        "UnsupportedProfile",
                        "profiles must be a sorted unique array",
                    )
                })?
                .iter()
                .map(|p| string(p, "UnsupportedProfile").map(str::to_owned))
                .collect::<Result<_>>()?
        } else {
            Vec::new()
        };
        if route {
            let mut sorted = profiles.clone();
            sorted.sort();
            sorted.dedup();
            if profiles != sorted {
                return error("UnsupportedProfile", "profiles must be sorted and unique");
            }
            const ALLOWED: &[&str] = &[
                "closure@0",
                "data@0",
                "definitions@0",
                "documents@1",
                "nary@0",
                "norms@0",
                "order@0",
                "relational-fol@0",
                "reports@0",
                "soft-norms@0",
                "time@0",
            ];
            for p in &profiles {
                if !ALLOWED.contains(&p.as_str()) {
                    return error("UnsupportedProfile", format!("Unsupported profile {p}"));
                }
            }
            if !profiles.iter().any(|p| p == "relational-fol@0") {
                return error("UnsupportedProfile", "Missing profile relational-fol@0");
            }
            let has = |name: &str| profiles.iter().any(|p| p == name);
            if has("reports@0") {
                if obj["vocabulary"].get("reports").is_none() {
                    return error("UnsupportedProfile", "reports@0 needs a reports block");
                }
                for other in ["norms@0", "definitions@0", "data@0", "closure@0", "nary@0", "order@0"] {
                    if has(other) {
                        return error("UnsupportedProfile", format!("reports@0 with {other} layers"));
                    }
                }
                let block = fields(&obj["vocabulary"]["reports"], &["holders", "evidence"], "InvalidInput")?;
                let holders = block["holders"].as_array().ok_or_else(|| Error::new("InvalidInput", "reports holders"))?;
                if holders.is_empty() || holders.len() > 8 {
                    return error("ResourceLimit", "reports holders");
                }
                let mut seen = BTreeSet::new();
                for holder in holders {
                    let holder = string(holder, "UnknownSymbol")?;
                    if !seen.insert(holder) { return error("DuplicateDeclaration", "holder sort"); }
                }
                string(&block["evidence"], "UnknownSymbol")?;
            }
            if has("soft-norms@0") && !has("norms@0") {
                return error("UnsupportedProfile", "soft-norms@0 requires norms@0");
            }
            if has("order@0") && (has("closure@0") || has("nary@0")) {
                let pair = if has("closure@0") {
                    "closure@0"
                } else {
                    "nary@0"
                };
                return error(
                    "UnsupportedProfile",
                    format!("Unsupported profile combination {pair} x order@0"),
                );
            }
            if has("nary@0") && !has("closure@0") {
                return error(
                    "UnsupportedProfile",
                    "Unsupported profile nary@0 without closure@0",
                );
            }
        }
        let order = if route {
            profiles.iter().any(|p| p == "order@0")
        } else {
            order
        };
        let closure = if route {
            profiles.iter().any(|p| p == "closure@0")
        } else {
            closure
        };
        let supported = if route {
            obj["spec_revision"] == "ve-v0.2-expand2-2026-09-25"
        } else if order {
            obj["language"] == "ve.core@0.1" && obj["spec_revision"] == "ve-v0.1-order-2026-09-22"
        } else if closure {
            obj["profiles"] == json!(["closure@0", "relational-fol@0"])
                && obj["spec_revision"] == "ve-v0.1-closure-2026-09-21"
        } else {
            obj["language"] == "ve.core@0"
                && obj["profile"] == "relational-fol@0"
                && obj["spec_revision"] == "ve-v0-draft-2026-09-20"
        };
        if !supported && route {
            let revision = match &obj["spec_revision"] {
                Value::String(r) => r.clone(),
                other => other.to_string(),
            };
            return error(
                "UnsupportedProfile",
                format!("Unsupported specification revision {revision}"),
            );
        }
        if !supported {
            return error(
                "UnsupportedProfile",
                "unsupported language, profile or specification revision",
            );
        }
        // soft-norms@0 declares parties and ranks (the `soft` block and each
        // predicate's `instruction_of`); they bind identity and carry no
        // semantics this route checks.
        let soft = route && profiles.iter().any(|p| p == "soft-norms@0");
        let mut vocab_keys = vec!["sorts", "predicates", "constants"];
        if reports { vocab_keys.push("reports"); }
        if soft && obj["vocabulary"].get("soft").is_some() { vocab_keys.push("soft"); }
        let vocab = fields(&obj["vocabulary"], &vocab_keys, "InvalidInput")?;
        let sorts = object(&vocab["sorts"], "InvalidInput")?;
        let preds = object(&vocab["predicates"], "InvalidInput")?;
        let consts = object(&vocab["constants"], "InvalidInput")?;
        if reports {
            let block = &vocab["reports"];
            for holder in block["holders"].as_array().unwrap() {
                if !sorts.contains_key(holder.as_str().unwrap()) {
                    return error("UnknownSymbol", "holder sort");
                }
            }
            if !sorts.contains_key(block["evidence"].as_str().unwrap()) {
                return error("UnknownSymbol", "evidence sort");
            }
        }
        if sorts.len() > 32 || preds.len() > 256 {
            return error("ResourceLimit", "vocabulary limit");
        }
        let mut seen = BTreeSet::new();
        for name in sorts.keys().chain(preds.keys()).chain(consts.keys()) {
            identifier(name, "InvalidInput")?;
            let generated = name
                .strip_prefix('x')
                .is_some_and(|tail| !tail.is_empty() && tail.bytes().all(|b| b.is_ascii_digit()));
            if !seen.insert(name) || RESERVED.contains(&name.as_str()) || generated {
                return error(
                    "DuplicateDeclaration",
                    format!("duplicate or reserved schema name {name:?}"),
                );
            }
        }
        for decl in sorts.values() {
            let d = entry_fields(decl, &["description"], false, false)?;
            if let Some(v) = d.get("verbalisation") {
                let v = fields(v, &["singular", "plural"], "InvalidInput")?;
                verbalisation(&v["singular"])?;
                verbalisation(&v["plural"])?;
            }
            description(&d["description"])?;
        }
        let mut predicates = BTreeMap::new();
        let mut regulated = BTreeMap::<String, (String, String, Option<String>, Option<String>)>::new();
        let mut canonical_data = data.clone();
        let mut predicate_flags = BTreeMap::new();
        let mut defined = Vec::new();
        // The first fault Lean's family decoder reports only after the constants.
        let mut deferred_sort_fault: Option<&'static str> = None;
        let definitions_profile = route && profiles.iter().any(|p| p == "definitions@0");
        let data_profile = route && profiles.iter().any(|p| p == "data@0");
        let layers = preds.values().any(|decl| ["defined", "functional", "total"]
            .iter().any(|key| decl.get(*key).is_some()));
        let judge = SortJudge::of(route, order, &profiles, layers);
        if route {
            located_argument_fault(preds, sorts, &profiles)?;
        }
        for (name, decl) in preds {
            let flagged = decl.get("functional").is_some() || decl.get("total").is_some();
            if flagged && decl.get("defined").is_some() {
                return error("UnsupportedProfile", "Defined predicates cannot carry functional or total flags");
            }
            if flagged && !(route && profiles.iter().any(|p| p == "data@0")) {
                return error("UnsupportedProfile", "Predicate flags require data@0");
            }
            let has_definition = decl.get("defined").is_some();
            let is_defined = definitions_profile && has_definition;
            if decl.get("regulated").is_some() && is_defined {
                return error("InvalidInput", format!("RegulatedDefinedPredicate: {name}"));
            }
            if decl.get("regulated").is_some() && flagged {
                return error("InvalidInput", format!("RegulatedFlag: {name}"));
            }
            if is_defined && order {
                return error("UnsupportedProfile", "definitions on the order family require an order definition layer");
            }
            let mut keys = vec!["arguments", "description"];
            if has_definition { keys.push("defined"); }
            // The order decoder has no data flag fields (Order/Wire.lean:66).
            let flag_fields = !matches!(judge, SortJudge::Order);
            if flag_fields && decl.get("functional").is_some() { keys.push("functional"); }
            if flag_fields && decl.get("total").is_some() { keys.push("total"); }
            if soft && decl.get("instruction_of").is_some() { keys.push("instruction_of"); }
            let d = entry_fields(decl, &keys, true,
                route && profiles.iter().any(|p| p == "norms@0"))?;
            let maximum_arity = if route && profiles.iter().any(|p| p == "nary@0") { 6 } else { 2 };
            let args = d["arguments"]
                .as_array()
                .filter(|a| (1..=maximum_arity).contains(&a.len()))
                .ok_or_else(|| Error::new("InvalidInput", format!("predicate arity must be one to {maximum_arity}")))?;
            let mut signature = Vec::new();
            for arg in args {
                let s = arg.as_str().unwrap_or("");
                if !arg.is_string() || !sorts.contains_key(s) {
                    match judge.argument(s, data_profile, args.len(), has_definition) {
                        // `""` (a cell that is not a string) is never accepted.
                        SortVerdict::Accepted => {}
                        SortVerdict::AtSort(code) => return sort_fault(code),
                        SortVerdict::AfterConstants(code) => {
                            deferred_sort_fault.get_or_insert(code);
                        }
                    }
                }
                signature.push(s.to_owned());
            }
            if flagged && signature.len() != 2 {
                return error("InvalidInput", "Functional and total flags require a binary predicate");
            }
            let functional = match d.get("functional") {
                None => false,
                Some(Value::Bool(value)) => *value,
                _ => return error("InvalidInput", "functional must be a Boolean"),
            };
            let total = match d.get("total") {
                None => false,
                Some(Value::Bool(value)) => *value,
                _ => return error("InvalidInput", "total must be a Boolean"),
            };
            for key in ["verbalisation", "negative_verbalisation"] {
                if let Some(v) = d.get(key) {
                    verbalisation(v)?;
                }
            }
            description(&d["description"])?;
            if let Some(raw) = d.get("regulated") {
                let r = object(raw, "InvalidInput")?;
                let role = r.get("role").map(|v| string(v, "InvalidInput")).transpose()?
                    .ok_or_else(|| Error::new("InvalidInput", "regulated role is required"))?;
                let default = r.get("default").map(|v| string(v, "InvalidInput")).transpose()?
                    .ok_or_else(|| Error::new("InvalidInput", "regulated default is required"))?;
                if default == "unspecified" && ["permission", "obligation", "plain"].contains(&role) {
                    // norm-defaults 2.1: Rust decodes no norm-defaults@0 environment.
                    return error("UnsupportedProfile",
                                 "UnsupportedProfile: unspecified completion requires norm-defaults@0");
                }
                if !["permission", "obligation", "plain"].contains(&role)
                    || !["allow", "deny"].contains(&default) {
                    return error("InvalidInput", "invalid regulated role or default");
                }
                let mut keys = vec!["role", "default"];
                let act = if role == "plain" { None } else {
                    keys.push("act");
                    Some(act_phrase(r.get("act").ok_or_else(|| Error::new("InvalidInput", "act is required"))?,
                                    signature.len())?)
                };
                if role == "obligation" && r.contains_key("permission") {
                    keys.push("permission");
                }
                fields(raw, &keys, "InvalidInput")?;
                let permission = r.get("permission").map(|v| string(v, "InvalidInput")
                    .map(str::to_owned)).transpose()?;
                if let Some(ref phrase) = act {
                    canonical_data["vocabulary"]["predicates"][name]["regulated"]["act"] = json!(phrase);
                }
                regulated.insert(name.clone(), (role.into(), default.into(), act, permission));
            }
            if has_definition {
                defined.push((name.clone(), signature.clone(), d["defined"].clone()));
            }
            predicates.insert(name.clone(), signature);
            predicate_flags.insert(name.clone(), (functional, total));
        }
        if regulated.len() > 64 {
            return error("ResourceLimit", "regulated predicates");
        }
        let mut acts = BTreeMap::new();
        for (name, (role, _, act, _)) in &regulated {
            if let Some(act) = act {
                let key = (predicates[name].clone(), act.clone(), role.clone());
                if acts.insert(key, name.clone()).is_some() {
                    return error("InvalidInput", format!("DuplicateActRole: {role}, {act}"));
                }
            }
        }
        let mut profile_pairs = Vec::new();
        for (name, (role, _, act, permission)) in &regulated {
            if role != "obligation" { continue; }
            let expected = acts.get(&(predicates[name].clone(), act.clone().unwrap(), "permission".into()));
            if permission.is_none() && expected.is_some() {
                return error("InvalidInput", format!("MissingPermissionDual: {name}, {}", expected.unwrap()));
            }
            if let Some(dual) = permission {
                let Some((target_role, _, target_act, _)) = regulated.get(dual) else {
                    return error("InvalidInput", format!("MissingPermissionDual: {name}, {dual}"));
                };
                if target_role != "permission" {
                    return error("InvalidInput", format!("MissingPermissionDual: {name}, {dual}"));
                }
                if predicates[name] != predicates[dual] {
                    return error("InvalidInput", format!("DualSortMismatch: {name}, {dual}"));
                }
                if act != target_act {
                    return error("InvalidInput", format!("DualActMismatch: {name}, {dual}"));
                }
                profile_pairs.push((name.clone(), dual.clone()));
            }
        }
        let mut constants = BTreeMap::new();
        for (name, decl) in consts {
            let literal = route && decl.get("sort") == Some(&json!("$string"));
            let mut keys = vec!["sort"];
            if !literal || decl.get("description").is_some() { keys.push("description"); }
            if reports && decl.get("verbalisation").is_some() { keys.push("verbalisation"); }
            let d = fields(decl, &keys, "InvalidInput")?;
            let s = string(&d["sort"], "UnknownSymbol")?;
            if !sorts.contains_key(s) && !judge.constant_admits(s) {
                return error(judge.constant_fault(), "unknown constant sort");
            }
            if let Some(value) = d.get("description") {
                description(value)?;
            }
            if let Some(value) = d.get("verbalisation") {
                verbalisation(value)?;
                // As Python and Lean: ASCII case-insensitively, no holder displays as the assessment.
                let holder = vocab["reports"]["holders"].as_array().is_some_and(|h| h.contains(&json!(s)));
                if holder && value.as_str().is_some_and(|w| w.to_ascii_lowercase() == "the stated assessment") {
                    return error("InvalidInput", "holder verbalisation reserved");
                }
            }
            constants.insert(name.clone(), s.into());
        }
        if route && constants.values().filter(|s| *s == "$string").count() > 64 {
            return error("ResourceLimit", "At most 64 declared $string literals");
        }
        if let Some(code) = deferred_sort_fault {
            return sort_fault(code);
        }
        let version = if route {
            format!("v0.2:{}", profiles.join(","))
        } else if order {
            "v0.1-order".into()
        } else if closure {
            "v0.1".into()
        } else {
            "v0".into()
        };
        let mut env = Self {
            closure,
            order,
            route,
            profiles,
            sorts: sorts.keys().cloned().collect(),
            predicates,
            predicate_flags,
            constants,
            profile_pairs,
            definitions: Vec::new(),
            soft_premises: Vec::new(),
            data: canonical_data.clone(),
            id: digest(&format!("ve-environment-{version}\n"), &canonical_data)?,
        };
        env.definitions = env.elaborate(defined)?;
        // Lean decodes a submitted definition body before rejecting the
        // unsupported field on a plain relational environment. Keep the
        // field check, but let a malformed nested body own its diagnostic.
        if !definitions_profile {
            for (_, decl) in preds {
                if decl.get("defined").is_some() {
                    let mut keys = vec!["arguments", "description"];
                    if decl.get("functional").is_some() { keys.push("functional"); }
                    if decl.get("total").is_some() { keys.push("total"); }
                    if soft && decl.get("instruction_of").is_some() { keys.push("instruction_of"); }
                    entry_fields(decl, &keys, true,
                        route && env.profiles.iter().any(|p| p == "norms@0"))?;
                }
            }
        }
        // soft-norms@0 phase 3, after the vocabulary it decodes without the
        // checker profiles (lean/VE/SoftNorms/Phases.lean:195-203).
        if soft {
            if env.profiles.iter().any(|p| ["closure@0", "nary@0", "order@0"].contains(&p.as_str())) {
                return error("UnsupportedProfile", "the norms route admits FOL documents only");
            }
            if !env.definitions.is_empty() {
                return error("UnsupportedProfile", "norms route with definitions is not implemented");
            }
            if env.predicate_flags.values().any(|(functional, total)| *functional || *total) {
                return error("UnsupportedProfile", "norms route with data flags is not implemented");
            }
        }
        Ok(env)
    }
    /// Order the identity-bound definitions by the one dependency DAG and check
    /// each body over the symbols strictly below it (Python `compile_definitions`).
    fn elaborate(
        &self,
        raw: Vec<(String, Vec<String>, Value)>,
    ) -> Result<Vec<(String, Vec<String>, Formula)>> {
        let mut decoded = BTreeMap::new();
        let mut nodes = Vec::new();
        for (name, signature, payload) in raw {
            let p = fields(&payload, &["arguments", "body"], "InvalidInput")?;
            if p["arguments"] != json!(signature) {
                return error(
                    "InvalidInput",
                    format!("Definition '{name}' arguments differ from its declaration"),
                );
            }
            // Python decodes only an array body; any other value reaches the typing
            // check below undecoded, mentioning nothing (Lean `Wire.bodyFault`).
            let body = match &p["body"] {
                Value::Array(_) => Some(decode_formula(&p["body"])?),
                _ => None,
            };
            if body.as_ref().is_some_and(has_reach) {
                return error(
                    "UnsupportedProfile",
                    "definition bodies with reachability require a closure definition layer",
                );
            }
            let mut mentions = BTreeSet::new();
            if let Some(body) = &body {
                body.predicates(&mut mentions);
            }
            nodes.push((name.clone(), mentions.into_iter().collect()));
            decoded.insert(name, (signature, body));
        }
        let order = dependency_order(&nodes)?;
        let mut below = self.clone();
        below
            .predicates
            .retain(|name, _| !decoded.contains_key(name));
        let mut result = Vec::new();
        for name in order {
            let (signature, body) = decoded.remove(&name).expect("ordered node");
            let not_typed = || Error::new("InvalidInput",
                format!("Definition {name}: the body is not a typed formula over the symbols below it"));
            let body = body.ok_or_else(not_typed)?;
            check_in_context(&below, &body, &signature).map_err(|_| not_typed())?;
            below.predicates.insert(name.clone(), signature.clone());
            // The generated biconditional has the AST limits of any formula,
            // 10,000 nodes and depth 64 (Python checks `premise(definition)`
            // after the body, in dependency order).
            check_in_context(&below, &definition_premise(&name, &signature, &body), &[])?;
            result.push((name, signature, body));
        }
        Ok(result)
    }
    /// This environment with the premises a validated soft document adds to
    /// Background: models must satisfy them (`InvalidModel(soft)`).
    pub fn with_soft_premises(mut self, premises: Vec<Formula>) -> Self {
        self.soft_premises = premises;
        self
    }
    pub(crate) fn is_defined(&self, name: &str) -> bool {
        self.definitions.iter().any(|(n, _, _)| n == name)
    }
    pub fn to_value(&self) -> Value {
        self.data.clone()
    }
    pub fn environment_id(&self) -> &str {
        &self.id
    }
    pub fn closure(&self) -> bool {
        self.closure
    }
    pub fn nary(&self) -> bool {
        self.route && self.profiles.iter().any(|p| p == "nary@0")
    }
    pub fn order(&self) -> bool {
        self.order
    }
    pub(crate) fn has_profile(&self, name: &str) -> bool {
        self.profiles.iter().any(|profile| profile == name)
    }
    pub fn identity_version(&self) -> String {
        if self.route {
            return format!("v0.2:{}", self.profiles.join(","));
        }
        if self.order {
            "v0.1-order".into()
        } else if self.closure {
            "v0.1".into()
        } else {
            "v0".into()
        }
    }
    pub(crate) fn model_sorts(&self) -> BTreeSet<String> {
        let mut sorts = self.sorts.clone();
        if self.constants.values().any(|sort| sort == "$string")
            || self.predicates.values().any(|args| args.iter().any(|sort| sort == "$string")) {
            sorts.insert("$string".into());
        }
        sorts
    }
    /// A family the envelope gate accepts but whose checker has not landed:
    /// every checking site rejects it (same diagnostic as Python and Lean).
    pub(crate) fn require_checker(&self) -> Result<()> {
        Ok(())
    }
    pub(crate) fn validate_background(&self, constants: &BTreeMap<String, usize>) -> Result<()> {
        self.require_checker()?;
        let mut seen = BTreeSet::new();
        for (name, sort) in &self.constants {
            if sort == "$string" && !seen.insert(constants[name]) {
                return error(
                    "InvalidModel",
                    format!("$string literals alias at {name} (literals)"),
                );
            }
        }
        Ok(())
    }
    pub(crate) fn schema_name(&self, s: &str) -> bool {
        self.sorts.contains(s) || self.predicates.contains_key(s) || self.constants.contains_key(s)
    }
}
