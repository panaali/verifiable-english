use crate::{
    Environment, Error, MAX_EVALUATIONS, Result, digest,
    eval::Evaluator,
    environment::{identifier, string},
    error, loads_json,
    wire::{fields, object},
};
use serde_json::{Value, json};
use std::collections::{BTreeMap, BTreeSet};

#[derive(Clone, Debug)]
pub struct FiniteModel {
    pub(crate) domains: BTreeMap<String, Vec<String>>,
    pub(crate) constants: BTreeMap<String, usize>,
    pub(crate) relations: BTreeMap<String, BTreeSet<Vec<usize>>>,
    predicate_sorts: BTreeMap<String, Vec<String>>,
    constant_sorts: BTreeMap<String, String>,
    environment_id: String,
    model_id: String,
    data: Value,
}
impl FiniteModel {
    pub(crate) fn predicate_sort(&self, name: &str, position: usize) -> &str {
        &self.predicate_sorts[name][position]
    }

    pub(crate) fn constant_sort(&self, name: &str) -> &str {
        &self.constant_sorts[name]
    }

    pub fn from_json(env: &Environment, bytes: &[u8]) -> Result<Self> {
        Self::from_value(env, &loads_json(bytes)?)
    }
    pub fn from_value(env: &Environment, v: &Value) -> Result<Self> {
        if env.order() {
            return error(
                "UnsupportedProfile",
                "use the order model route for order@0",
            );
        }
        let obj = fields(
            v,
            &["complete", "domains", "constants", "relations"],
            "InvalidModel",
        )?;
        if obj["complete"] != Value::Bool(true) {
            return error("InvalidModel", "complete must be Boolean true");
        }
        let ds = object(&obj["domains"], "InvalidModel")?;
        let cs = object(&obj["constants"], "InvalidModel")?;
        let rs = object(&obj["relations"], "InvalidModel")?;
        if ds.keys().cloned().collect::<BTreeSet<_>>() != env.model_sorts()
            || cs.keys().ne(env.constants.keys())
        {
            return error(
                "InvalidModel",
                "model must contain exactly the declared sorts, constants and predicates",
            );
        }
        // Defined tables are computed from their bodies; a supplied one is invalid.
        if rs.keys().any(|k| env.is_defined(k)) {
            return error(
                "InvalidModel",
                "supplied table for defined predicate (definitions)",
            );
        }
        if rs.keys().ne(env.predicates.keys().filter(|p| !env.is_defined(p))) {
            return error(
                "InvalidModel",
                "model must contain exactly the declared sorts, constants and base predicates",
            );
        }
        let mut domains = BTreeMap::new();
        for (sort, v) in ds {
            let a = v
                .as_array()
                .ok_or_else(|| Error::new("InvalidModel", "domain must be an array"))?;
            if a.len() > 1000 {
                return error("ResourceLimit", "domain exceeds 1,000 entities");
            }
            let mut domain = Vec::new();
            for entity in a {
                let s = string(entity, "InvalidModel")?;
                identifier(s, "InvalidModel")?;
                domain.push(s.to_owned());
            }
            domain.sort();
            if domain.windows(2).any(|w| w[0] == w[1]) {
                return error("InvalidModel", "duplicate entity");
            }
            domains.insert(sort.clone(), domain);
        }
        let mut constants = BTreeMap::new();
        for (name, v) in cs {
            let s = string(v, "InvalidModel")?;
            identifier(s, "InvalidModel")?;
            let index = domains[&env.constants[name]]
                .binary_search_by(|x| x.as_str().cmp(s))
                .map_err(|_| Error::new("InvalidModel", "constant outside its sort"))?;
            constants.insert(name.clone(), index);
        }
        let mut relations = BTreeMap::new();
        let mut count = 0;
        for (name, v) in rs {
            let rows = v
                .as_array()
                .ok_or_else(|| Error::new("InvalidModel", "relation must be an array"))?;
            count += rows.len();
            if count > 100_000 {
                return error("ResourceLimit", "relation tuple limit");
            }
            let sig = &env.predicates[name];
            let mut relation = BTreeSet::new();
            for row in rows {
                let row = row
                    .as_array()
                    .filter(|a| a.len() == sig.len())
                    .ok_or_else(|| Error::new("InvalidModel", "relation tuple arity"))?;
                let mut tuple = Vec::new();
                for (entity, sort) in row.iter().zip(sig) {
                    let s = string(entity, "InvalidModel")?;
                    identifier(s, "InvalidModel")?;
                    let index = domains[sort]
                        .binary_search_by(|x| x.as_str().cmp(s))
                        .map_err(|_| Error::new("InvalidModel", "dangling or wrong-sort entity"))?;
                    tuple.push(index);
                }
                if !relation.insert(tuple) {
                    return error("InvalidModel", "duplicate relation tuple");
                }
            }
            relations.insert(name.clone(), relation);
        }
        let mut model = Self {
            domains,
            constants,
            relations,
            predicate_sorts: env.predicates.clone(),
            constant_sorts: env.constants.clone(),
            environment_id: String::new(),
            model_id: String::new(),
            data: Value::Null,
        };
        for (name, (functional, total)) in &env.predicate_flags {
            if !*functional && !*total { continue; }
            let relation = &model.relations[name];
            let mut values = BTreeMap::new();
            for row in relation {
                if *functional && values.insert(row[0], row[1]).is_some_and(|prior| prior != row[1]) {
                    return error("InvalidModel", format!("flags: {name} has two values"));
                }
                if !*functional { values.insert(row[0], row[1]); }
            }
            if *total && values.len() != model.domains[&env.predicates[name][0]].len() {
                return error("InvalidModel", format!("flags: {name} is not total"));
            }
        }
        env.validate_background(&model.constants)?;
        let mut budget = MAX_EVALUATIONS;
        for (name, sig, body) in &env.definitions {
            let sizes: Vec<usize> = sig.iter().map(|s| model.domains[s].len()).collect();
            let mut table = BTreeSet::new();
            let mut row = vec![0; sig.len()];
            let mut more = sizes.iter().all(|n| *n > 0);
            while more {
                let mut ev = Evaluator::new(&model, budget);
                let value = ev.formula(body, &mut row.clone()).map_err(|_| {
                    Error::new("ResourceLimit", "Definition model evaluation budget exhausted")
                })?;
                budget -= ev.work;
                if value {
                    count += 1;
                    if count > 100_000 {
                        return error("ResourceLimit", "relation tuple limit");
                    }
                    table.insert(row.clone());
                }
                more = false;
                for i in (0..row.len()).rev() {
                    if row[i] + 1 < sizes[i] {
                        row[i] += 1;
                        more = true;
                        break;
                    }
                    row[i] = 0;
                }
            }
            model.relations.insert(name.clone(), table);
        }
        for (required, permitted) in &env.profile_pairs {
            if !model.relations[required].is_subset(&model.relations[permitted]) {
                return error("InvalidModel", format!(
                    "required relation {required} exceeds permission {permitted} (profile)"));
            }
        }
        let Self {
            domains,
            constants,
            relations,
            ..
        } = model;
        let constant_data: BTreeMap<_, _> = constants
            .iter()
            .map(|(n, i)| (n, &domains[&env.constants[n]][*i]))
            .collect();
        let relation_data: BTreeMap<_, Vec<Vec<&str>>> = relations
            .iter()
            .filter(|(n, _)| !env.is_defined(n))
            .map(|(n, rows)| {
                (
                    n,
                    rows.iter()
                        .map(|row| {
                            row.iter()
                                .zip(&env.predicates[n])
                                .map(|(i, s)| domains[s][*i].as_str())
                                .collect()
                        })
                        .collect(),
                )
            })
            .collect();
        let data = json!({"complete":true,"domains":domains,"constants":constant_data,"relations":relation_data});
        let environment_id = env.environment_id().to_owned();
        let model_id = digest(
            &format!("ve-model-{}\n", env.identity_version()),
            &json!({"environment_id":environment_id,"model":data}),
        )?;
        Ok(Self {
            domains,
            constants,
            relations,
            predicate_sorts: env.predicates.clone(),
            constant_sorts: env.constants.clone(),
            environment_id,
            model_id,
            data,
        })
    }
    pub fn to_value(&self) -> Value {
        self.data.clone()
    }
    pub fn model_id(&self) -> &str {
        &self.model_id
    }
    pub fn environment_id(&self) -> &str {
        &self.environment_id
    }
}
