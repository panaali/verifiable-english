use crate::{
    Error, Result, canonical_json, digest, error, loads_json,
    wire::{fields, object},
};
use serde_json::Value;
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

#[derive(Clone, Debug)]
pub struct Environment {
    pub(crate) sorts: BTreeSet<String>,
    pub(crate) predicates: BTreeMap<String, Vec<String>>,
    pub(crate) constants: BTreeMap<String, String>,
    data: Value,
    id: String,
}
impl Environment {
    pub fn from_json(bytes: &[u8]) -> Result<Self> {
        Self::from_value(&loads_json(bytes)?)
    }
    pub fn from_value(data: &Value) -> Result<Self> {
        canonical_json(data)?;
        let obj = fields(
            data,
            &["language", "profile", "spec_revision", "vocabulary"],
            "InvalidInput",
        )?;
        if obj["language"] != "ve.core@0"
            || obj["profile"] != "relational-fol@0"
            || obj["spec_revision"] != "ve-v0-draft-2026-09-20"
        {
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
            description(&fields(decl, &["description"], "InvalidInput")?["description"])?;
        }
        let mut predicates = BTreeMap::new();
        for (name, decl) in preds {
            let d = fields(decl, &["arguments", "description"], "InvalidInput")?;
            let args = d["arguments"]
                .as_array()
                .filter(|a| matches!(a.len(), 1 | 2))
                .ok_or_else(|| Error::new("InvalidInput", "predicate arity must be one or two"))?;
            let mut signature = Vec::new();
            for arg in args {
                let s = string(arg, "UnknownSymbol")?;
                if !sorts.contains_key(s) {
                    return error("UnknownSymbol", "unknown predicate argument sort");
                }
                signature.push(s.to_owned());
            }
            description(&d["description"])?;
            predicates.insert(name.clone(), signature);
        }
        let mut constants = BTreeMap::new();
        for (name, decl) in consts {
            let d = fields(decl, &["sort", "description"], "InvalidInput")?;
            let s = string(&d["sort"], "UnknownSymbol")?;
            if !sorts.contains_key(s) {
                return error("UnknownSymbol", "unknown constant sort");
            }
            description(&d["description"])?;
            constants.insert(name.clone(), s.into());
        }
        Ok(Self {
            sorts: sorts.keys().cloned().collect(),
            predicates,
            constants,
            data: data.clone(),
            id: digest("ve-environment-v0\n", data)?,
        })
    }
    pub fn to_value(&self) -> Value {
        self.data.clone()
    }
    pub fn environment_id(&self) -> &str {
        &self.id
    }
    pub(crate) fn schema_name(&self, s: &str) -> bool {
        self.sorts.contains(s) || self.predicates.contains_key(s) || self.constants.contains_key(s)
    }
}
