use crate::{
    Error, Result, canonical_json, digest, error, loads_json,
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

fn act_phrase(value: &Value, arity: usize) -> Result<String> {
    let raw = string(value, "InvalidInput")?;
    let act = raw.split_whitespace().collect::<Vec<_>>().join(" ");
    let slots: Vec<_> = (0..arity).map(|i| format!("{{{i}}}")).collect();
    let mut cursor = 0;
    for slot in &slots {
        let Some(i) = act[cursor..].find(slot) else {
            return error("InvalidInput", "invalid act phrase slots");
        };
        cursor += i + slot.len();
    }
    let mut plain = act.clone();
    for slot in slots.iter().rev() {
        plain = plain.replace(slot, "slot");
    }
    if act.len() > 80 || plain.split_whitespace().count() < 2 ||
        plain.split_whitespace().any(|word| !word.bytes().all(|b|
            b.is_ascii_alphabetic() || b == b'\'' || b == b'-')) {
        return error("InvalidInput", "invalid act phrase");
    }
    Ok(act)
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
    pub(crate) profile_pairs: Vec<(String, String)>,
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
        for (name, decl) in preds {
            let d = entry_fields(decl, &["arguments", "description"], true,
                                 route && profiles.iter().any(|p| p == "norms@0"))?;
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
            if let Some(raw) = d.get("regulated") {
                let r = object(raw, "InvalidInput")?;
                let role = r.get("role").map(|v| string(v, "InvalidInput")).transpose()?
                    .ok_or_else(|| Error::new("InvalidInput", "regulated role is required"))?;
                let default = r.get("default").map(|v| string(v, "InvalidInput")).transpose()?
                    .ok_or_else(|| Error::new("InvalidInput", "regulated default is required"))?;
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
            predicates.insert(name.clone(), signature);
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
        Ok(Self {
            closure,
            order,
            route,
            profiles,
            sorts: sorts.keys().cloned().collect(),
            predicates,
            constants,
            profile_pairs,
            data: canonical_data.clone(),
            id: digest(&format!("ve-environment-{version}\n"), &canonical_data)?,
        })
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
