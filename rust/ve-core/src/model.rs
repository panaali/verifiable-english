use crate::{
    Environment, Error, Result, digest,
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
    environment_id: String,
    model_id: String,
    data: Value,
}
impl FiniteModel {
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
        if ds.keys().cloned().collect::<BTreeSet<_>>() != env.sorts
            || cs.keys().ne(env.constants.keys())
            || rs.keys().ne(env.predicates.keys())
        {
            return error(
                "InvalidModel",
                "model must contain exactly the declared sorts, constants and predicates",
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
        let constant_data: BTreeMap<_, _> = constants
            .iter()
            .map(|(n, i)| (n, &domains[&env.constants[n]][*i]))
            .collect();
        let relation_data: BTreeMap<_, Vec<Vec<&str>>> = relations
            .iter()
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
