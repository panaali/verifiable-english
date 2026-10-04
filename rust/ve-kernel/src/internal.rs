//! Kernel items the profile and surface crates use but the public API does not offer: they were
//! `pub(crate)` while the three groups shared one crate. The `ve-core` facade does not re-export
//! this module. Checked values stay read-only: accessors return shared references, never public
//! fields. These are thin forwards rather than `pub use` re-exports, which the intra-crate module
//! check (`tools/check_rust_deps.py`) accepts only at the top level of `lib.rs`.
use crate::{Document, Environment, FiniteModel, Formula, Result};
use serde_json::{Map, Value};
use std::collections::{BTreeMap, BTreeSet};

pub const RESERVED: &[&str] = crate::environment::RESERVED;
pub const FORMULA_ARITY: &[(&str, usize)] = crate::wire::FORMULA_ARITY;

pub type Evaluator<'a> = crate::semantics::Evaluator<'a>;

pub fn error<T>(code: &str, message: impl Into<String>) -> Result<T> {
    crate::error(code, message)
}

pub fn identifier(s: &str, code: &str) -> Result<()> {
    crate::environment::identifier(s, code)
}

pub fn ast_limit<'a>(formulas: impl IntoIterator<Item = &'a Value>) -> Result<()> {
    crate::ast::ast_limit(formulas)
}

pub fn model_limits(ds: &Map<String, Value>, rs: &Map<String, Value>) -> Result<()> {
    crate::model::model_limits(ds, rs)
}

pub fn compatible(doc: &Document, model: &FiniteModel, maximum: u64) -> Result<()> {
    crate::semantics::compatible(doc, model, maximum)
}

/// Read access to a checked environment's signature, and its crate-private checks.
pub trait EnvironmentInternals {
    fn sorts(&self) -> &BTreeSet<String>;
    fn predicates(&self) -> &BTreeMap<String, Vec<String>>;
    fn predicate_flags(&self) -> &BTreeMap<String, (bool, bool)>;
    fn constants(&self) -> &BTreeMap<String, String>;
    fn profile_pairs(&self) -> &[(String, String)];
    fn definitions(&self) -> &[(String, Vec<String>, Formula)];
    fn is_defined(&self, name: &str) -> bool;
    fn model_sorts(&self) -> BTreeSet<String>;
    fn require_checker(&self) -> Result<()>;
    fn schema_name(&self, s: &str) -> bool;
}

impl EnvironmentInternals for Environment {
    fn sorts(&self) -> &BTreeSet<String> {
        &self.sorts
    }
    fn predicates(&self) -> &BTreeMap<String, Vec<String>> {
        &self.predicates
    }
    fn predicate_flags(&self) -> &BTreeMap<String, (bool, bool)> {
        &self.predicate_flags
    }
    fn constants(&self) -> &BTreeMap<String, String> {
        &self.constants
    }
    fn profile_pairs(&self) -> &[(String, String)] {
        &self.profile_pairs
    }
    fn definitions(&self) -> &[(String, Vec<String>, Formula)] {
        &self.definitions
    }
    fn is_defined(&self, name: &str) -> bool {
        Environment::is_defined(self, name)
    }
    fn model_sorts(&self) -> BTreeSet<String> {
        Environment::model_sorts(self)
    }
    fn require_checker(&self) -> Result<()> {
        Environment::require_checker(self)
    }
    fn schema_name(&self, s: &str) -> bool {
        Environment::schema_name(self, s)
    }
}

/// Read access to a checked model's domains.
pub trait FiniteModelInternals {
    fn domains(&self) -> &BTreeMap<String, Vec<String>>;
}

impl FiniteModelInternals for FiniteModel {
    fn domains(&self) -> &BTreeMap<String, Vec<String>> {
        &self.domains
    }
}

/// The predicates a formula mentions.
pub trait FormulaInternals {
    fn predicates(&self, result: &mut BTreeSet<String>);
}

impl FormulaInternals for Formula {
    fn predicates(&self, result: &mut BTreeSet<String>) {
        Formula::predicates(self, result)
    }
}

/// Whether a checked document was checked against an environment.
pub trait DocumentInternals {
    fn belongs_to(&self, env: &Environment) -> Result<()>;
}

impl DocumentInternals for Document {
    fn belongs_to(&self, env: &Environment) -> Result<()> {
        Document::belongs_to(self, env)
    }
}
