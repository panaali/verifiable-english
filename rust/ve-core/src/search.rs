use crate::{
    Document, Environment, FiniteModel, Formula, MAX_EVALUATIONS, Result, error,
    eval::{Evaluator, compatible},
};
use serde::Serialize;
use serde_json::{Value, json};
use std::collections::{BTreeMap, BTreeSet};

/// Ordered premises followed by one conclusion, checked as one aggregate AST.
#[derive(Clone, Debug)]
pub struct CountermodelProblem {
    document: Document,
}
#[derive(Clone, Debug, Serialize)]
pub struct CountermodelCheck {
    pub valid: bool,
    pub premise_values: Vec<bool>,
    pub conclusion_value: Option<bool>,
    pub evaluations: u64,
    pub environment_id: String,
    pub model_id: String,
    pub status: &'static str,
    pub premise_meaning_ids: Vec<String>,
    pub conclusion_meaning_id: String,
}
impl CountermodelProblem {
    pub fn new(env: &Environment, mut premises: Vec<Formula>, conclusion: Formula) -> Result<Self> {
        env.require_checker()?;
        premises.push(conclusion);
        Ok(Self {
            document: Document::check(env, premises)?,
        })
    }
    fn values(
        &self,
        model: &FiniteModel,
        maximum: u64,
    ) -> Result<(&'static str, Vec<bool>, Option<bool>, u64)> {
        compatible(&self.document, model, maximum)?;
        let mut ev = Evaluator::new(model, maximum);
        let mut values = Vec::new();
        let (conclusion, premises) = self
            .document
            .formulas()
            .split_last()
            .expect("nonempty checked AST");
        for f in premises {
            // Python witness checking starts a fresh closure cache per premise.
            ev.clear_closures();
            match ev.formula(f, &mut Vec::new()) {
                Ok(v) => {
                    values.push(v);
                    if !v {
                        return Ok(("NotCountermodel", values, None, ev.work));
                    }
                }
                Err(_) => return Ok(("ResourceLimit", values, None, ev.work)),
            }
        }
        ev.clear_closures();
        match ev.formula(conclusion, &mut Vec::new()) {
            Ok(v) => Ok((
                if v { "NotCountermodel" } else { "Valid" },
                values,
                Some(v),
                ev.work,
            )),
            Err(_) => Ok(("ResourceLimit", values, None, ev.work)),
        }
    }
    /// Independently check a witness and bind it to the exact ordered inference.
    pub fn check_countermodel(
        &self,
        model: &FiniteModel,
        maximum: u64,
    ) -> Result<CountermodelCheck> {
        let (status, premise_values, conclusion_value, evaluations) =
            self.values(model, maximum)?;
        let n = self.document.formulas().len() - 1;
        Ok(CountermodelCheck {
            valid: status == "Valid",
            premise_values,
            conclusion_value,
            evaluations,
            status,
            environment_id: self.document.environment_id().into(),
            model_id: model.model_id().into(),
            premise_meaning_ids: (0..n)
                .map(|i| self.document.formula_meaning_id(i))
                .collect::<Result<_>>()?,
            conclusion_meaning_id: self.document.formula_meaning_id(n)?,
        })
    }
}
#[derive(Clone, Copy, Debug)]
pub struct SearchBounds {
    pub max_domain_size: usize,
    pub max_models: u64,
    pub max_evaluations: u64,
}
impl Default for SearchBounds {
    fn default() -> Self {
        Self {
            max_domain_size: 2,
            max_models: 10_000,
            max_evaluations: MAX_EVALUATIONS,
        }
    }
}
#[derive(Clone, Debug)]
pub struct SearchResult {
    pub status: &'static str,
    pub model: Option<FiniteModel>,
    pub models_checked: u64,
    pub evaluations: u64,
    pub bounds: SearchBounds,
    pub detail: &'static str,
}
impl SearchResult {
    pub fn to_value(&self) -> Value {
        json!({"status":self.status,"model":self.model.as_ref().map(FiniteModel::to_value),"models_checked":self.models_checked,"evaluations":self.evaluations,"max_domain_size":self.bounds.max_domain_size,"max_models":self.bounds.max_models,"detail":self.detail})
    }
}
/// Increment a mixed-radix counter, last entry fastest. Empty product has one state.
fn increment(values: &mut [usize], minima: &[usize], limits: &[usize]) -> bool {
    for i in (0..values.len()).rev() {
        if values[i] + 1 < limits[i] {
            values[i] += 1;
            return true;
        }
        values[i] = minima[i];
    }
    false
}
struct Models<'a> {
    env: &'a Environment,
    maximum: usize,
    sorts: Vec<String>,
    names: Vec<String>,
    used: BTreeSet<String>,
    sizes: Vec<usize>,
    minima: Vec<usize>,
    choices: Vec<usize>,
    choice_limits: Vec<usize>,
    atoms: Vec<(String, Vec<String>)>,
    bits: Vec<bool>,
    ready: bool,
    done: bool,
}
impl<'a> Models<'a> {
    fn new(env: &'a Environment, problem: &CountermodelProblem, maximum: usize) -> Self {
        let sorts: Vec<_> = env.model_sorts().into_iter().collect();
        let minima: Vec<_> = sorts
            .iter()
            .map(|s| {
                if s == "$string" {
                    env.constants.values().filter(|t| *t == s).count()
                } else {
                    usize::from(env.constants.values().any(|t| t == s))
                }
            })
            .collect();
        let mut used = BTreeSet::new();
        for f in problem.document.formulas() {
            f.predicates(&mut used);
        }
        for (name, (functional, total)) in &env.predicate_flags {
            if *functional || *total {
                used.insert(name.clone());
            }
        }
        Self {
            env,
            maximum,
            sorts,
            names: env.constants.keys().cloned().collect(),
            used,
            sizes: minima.clone(),
            done: minima.iter().any(|n| *n > maximum),
            minima,
            choices: vec![0; env.constants.len()],
            choice_limits: Vec::new(),
            atoms: Vec::new(),
            bits: Vec::new(),
            ready: false,
        }
    }
    fn prepare(&mut self) -> Result<()> {
        self.atoms.clear();
        let sizes: BTreeMap<_, _> = self.sorts.iter().zip(self.sizes.iter().copied()).collect();
        let count: usize = self
            .used
            .iter()
            .map(|p| {
                self.env.predicates[p]
                    .iter()
                    .map(|s| sizes[s])
                    .product::<usize>()
            })
            .sum();
        if count > 100_000 {
            return error("ResourceLimit", "used relation atom space exceeds 100,000");
        }
        // Reverse predicate order: lowest bit corresponds to last predicate,
        // matching Python's lexicographic product of subset masks when all are used.
        for p in self.used.iter().rev() {
            let sig = &self.env.predicates[p];
            for i in 0..sizes[&sig[0]] {
                if sig.len() == 1 {
                    self.atoms.push((p.clone(), vec![format!("e{i}")]));
                } else {
                    for j in 0..sizes[&sig[1]] {
                        self.atoms
                            .push((p.clone(), vec![format!("e{i}"), format!("e{j}")]));
                    }
                }
            }
        }
        self.bits = vec![false; self.atoms.len()];
        self.choices.fill(0);
        self.choice_limits = self
            .names
            .iter()
            .map(|n| sizes[&self.env.constants[n]])
            .collect();
        self.ready = true;
        Ok(())
    }
    fn advance(&mut self) {
        for bit in &mut self.bits {
            if !*bit {
                *bit = true;
                return;
            }
            *bit = false;
        }
        if increment(
            &mut self.choices,
            &vec![0; self.names.len()],
            &self.choice_limits,
        ) {
            return;
        }
        self.ready = false;
        if !increment(
            &mut self.sizes,
            &self.minima,
            &vec![self.maximum + 1; self.sorts.len()],
        ) {
            self.done = true;
        }
    }
    fn next(&mut self) -> Result<Option<FiniteModel>> {
        loop {
            if self.done {
                return Ok(None);
            }
            if !self.ready {
                self.prepare()?;
            }
            let domains: BTreeMap<_, Vec<_>> = self
                .sorts
                .iter()
                .zip(&self.sizes)
                .map(|(s, n)| (s, (0..*n).map(|i| format!("e{i}")).collect()))
                .collect();
            let constants: BTreeMap<_, _> = self
                .names
                .iter()
                .zip(&self.choices)
                .map(|(n, i)| (n, format!("e{i}")))
                .collect();
            let mut relations: BTreeMap<_, Vec<Vec<String>>> = self
                .env
                .predicates
                .keys()
                .map(|p| (p.clone(), Vec::new()))
                .collect();
            for ((p, row), bit) in self.atoms.iter().zip(&self.bits) {
                if *bit {
                    relations.get_mut(p).unwrap().push(row.clone());
                }
            }
            let model = FiniteModel::from_value(
                self.env,
                &json!({"complete":true,"domains":domains,"constants":constants,"relations":relations}),
            );
            self.advance();
            match model {
                Ok(model) => return Ok(Some(model)),
                Err(err) if err.code == "InvalidModel"
                    && (err.message.starts_with("literals:") || err.message.ends_with("(literals)")
                        || err.message.starts_with("flags:") || err.message.ends_with("(flags)")) => {
                    continue;
                }
                Err(err) => return Err(err),
            }
        }
    }
}
/// Exhaustive bounded search modulo the extensions of predicates absent from
/// the formulas. Unused predicates have empty extensions in every witness.
/// Neither NotFound nor ResourceLimit is evidence of entailment.
pub fn find_countermodel(
    env: &Environment,
    problem: &CountermodelProblem,
    bounds: SearchBounds,
) -> Result<SearchResult> {
    problem.document.belongs_to(env)?;
    if bounds.max_domain_size > 1000 || bounds.max_evaluations > MAX_EVALUATIONS {
        return error("ResourceLimit", "search bounds exceed v0 envelope");
    }
    let mut models = Models::new(env, problem, bounds.max_domain_size);
    let mut result = SearchResult {
        status: "NotFound",
        model: None,
        models_checked: 0,
        evaluations: 0,
        bounds,
        detail: "all finite models within the domain bound were exhausted",
    };
    loop {
        let model = match models.next() {
            Ok(None) => return Ok(result),
            Ok(Some(model)) => model,
            Err(e) if e.code == "ResourceLimit" => {
                result.status = "ResourceLimit";
                result.detail = "search relation atom space exceeds runtime limit";
                return Ok(result);
            }
            Err(e) => return Err(e),
        };
        if result.models_checked >= bounds.max_models
            || result.evaluations >= bounds.max_evaluations
        {
            result.status = "ResourceLimit";
            result.detail = "model-attempt or evaluation budget exhausted";
            return Ok(result);
        }
        let (status, _, _, work) =
            problem.values(&model, bounds.max_evaluations - result.evaluations)?;
        result.models_checked += 1;
        result.evaluations += work;
        if status == "ResourceLimit" {
            result.status = status;
            result.detail = "evaluation budget exhausted";
            return Ok(result);
        }
        if status == "Valid" {
            result.status = "Found";
            result.model = Some(model);
            result.detail = "";
            return Ok(result);
        }
    }
}
