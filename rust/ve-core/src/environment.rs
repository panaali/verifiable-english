use crate::{
    Error, Formula, Result,
    ast::{check_in_context, decode_formula, has_reach},
    canonical_json, dependency_order, digest, error, loads_json,
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
) -> Result<&'a serde_json::Map<String, Value>> {
    let mut keys = required.to_vec();
    if v.get("verbalisation").is_some() {
        keys.push("verbalisation");
    }
    if negative && v.get("negative_verbalisation").is_some() {
        keys.push("negative_verbalisation");
    }
    fields(v, &keys, "InvalidInput")
}

#[derive(Clone, Debug)]
pub struct Environment {
    closure: bool,
    order: bool,
    route: bool,
    profiles: Vec<String>,
    pub(crate) sorts: BTreeSet<String>,
    pub(crate) predicates: BTreeMap<String, Vec<String>>,
    pub(crate) constants: BTreeMap<String, String>,
    /// Identity-bound definitions (W3), in dependency order.
    pub(crate) definitions: Vec<(String, Vec<String>, Formula)>,
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
        let obj = fields(
            data,
            &[
                "language",
                if modern { "profiles" } else { "profile" },
                "spec_revision",
                "vocabulary",
            ],
            "InvalidInput",
        )?;
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
        let vocab = fields(
            &obj["vocabulary"],
            &["sorts", "predicates", "constants"],
            "InvalidInput",
        )?;
        let sorts = object(&vocab["sorts"], "InvalidInput")?;
        let preds = object(&vocab["predicates"], "InvalidInput")?;
        let consts = object(&vocab["constants"], "InvalidInput")?;
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
            let d = entry_fields(decl, &["description"], false)?;
            if let Some(v) = d.get("verbalisation") {
                let v = fields(v, &["singular", "plural"], "InvalidInput")?;
                verbalisation(&v["singular"])?;
                verbalisation(&v["plural"])?;
            }
            description(&d["description"])?;
        }
        let mut predicates = BTreeMap::new();
        let mut defined = Vec::new();
        let definitions_profile = route && profiles.iter().any(|p| p == "definitions@0");
        for (name, decl) in preds {
            let is_defined = definitions_profile && decl.get("defined").is_some();
            if is_defined && order {
                return error(
                    "UnsupportedProfile",
                    "definitions on the order family require an order definition layer",
                );
            }
            let d = entry_fields(
                decl,
                if is_defined {
                    &["arguments", "description", "defined"]
                } else {
                    &["arguments", "description"]
                },
                true,
            )?;
            let args = d["arguments"]
                .as_array()
                .filter(|a| matches!(a.len(), 1 | 2))
                .ok_or_else(|| Error::new("InvalidInput", "predicate arity must be one or two"))?;
            let mut signature = Vec::new();
            for arg in args {
                let s = string(arg, "UnknownSymbol")?;
                if !sorts.contains_key(s) && !(order && s == "$int") {
                    return error("UnknownSymbol", "unknown predicate argument sort");
                }
                signature.push(s.to_owned());
            }
            for key in ["verbalisation", "negative_verbalisation"] {
                if let Some(v) = d.get(key) {
                    verbalisation(v)?;
                }
            }
            description(&d["description"])?;
            if is_defined {
                defined.push((name.clone(), signature.clone(), d["defined"].clone()));
            }
            predicates.insert(name.clone(), signature);
        }
        let mut constants = BTreeMap::new();
        for (name, decl) in consts {
            let literal = route && decl.get("sort") == Some(&json!("$string"));
            let d = fields(
                decl,
                if literal && decl.get("description").is_none() {
                    &["sort"]
                } else {
                    &["sort", "description"]
                },
                "InvalidInput",
            )?;
            let s = string(&d["sort"], "UnknownSymbol")?;
            if !sorts.contains_key(s) && !(order && s == "$int") && !(route && s == "$string") {
                return error("UnknownSymbol", "unknown constant sort");
            }
            if let Some(value) = d.get("description") {
                description(value)?;
            }
            constants.insert(name.clone(), s.into());
        }
        if route && constants.values().filter(|s| *s == "$string").count() > 64 {
            return error("ResourceLimit", "At most 64 declared $string literals");
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
            constants,
            definitions: Vec::new(),
            data: data.clone(),
            id: digest(&format!("ve-environment-{version}\n"), data)?,
        };
        env.definitions = env.elaborate(defined)?;
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
                    format!("Definition {name:?} arguments differ from its declaration"),
                );
            }
            let body = decode_formula(&p["body"])?;
            if has_reach(&body) {
                return error(
                    "UnsupportedProfile",
                    "definition bodies with reachability require a closure definition layer",
                );
            }
            let mut mentions = BTreeSet::new();
            body.predicates(&mut mentions);
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
            check_in_context(&below, &body, &signature)
                .map_err(|_| Error::new("InvalidInput",
                    format!("Definition {name}: the body is not a typed formula over the symbols below it")))?;
            below.predicates.insert(name.clone(), signature.clone());
            result.push((name, signature, body));
        }
        Ok(result)
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
    pub fn order(&self) -> bool {
        self.order
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
        if self.constants.values().any(|sort| sort == "$string") {
            sorts.insert("$string".into());
        }
        sorts
    }
    /// A family the envelope gate accepts but whose checker has not landed:
    /// every checking site rejects it (same diagnostic as Python and Lean).
    pub(crate) fn require_checker(&self) -> Result<()> {
        if self.route
            && self.profiles.iter().any(|p| p == "nary@0")
            && self.profiles.iter().any(|p| p == "closure@0")
        {
            return error(
                "UnsupportedProfile",
                "the closure+n-ary checker is gated until W4 stage 1 lands",
            );
        }
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
