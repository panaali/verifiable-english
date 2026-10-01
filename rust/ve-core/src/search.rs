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
pub(crate) fn increment(values: &mut [usize], limits: &[usize]) -> bool {
    for i in (0..values.len()).rev() {
        if values[i] + 1 < limits[i] {
            values[i] += 1;
            return true;
        }
        values[i] = 0;
    }
    false
}
/// Advance a k-combination of 0..n in lexicographic order.
pub(crate) fn next_combination(indices: &mut [usize], n: usize) -> bool {
    let k = indices.len();
    for i in (0..k).rev() {
        if indices[i] < n - k + i {
            indices[i] += 1;
            for j in i + 1..k {
                indices[j] = indices[j - 1] + 1;
            }
            return true;
        }
    }
    false
}
/// Python `search._domain_sizes`: bounded vectors by total entities, then lexicographically.
pub(crate) fn domain_sizes(minima: &[usize], maximum: usize) -> Vec<Vec<usize>> {
    fn walk(minima: &[usize], suffix: &[usize], maximum: usize, index: usize, remaining: usize,
            prefix: &mut Vec<usize>, out: &mut Vec<Vec<usize>>) {
        if index == minima.len() {
            if remaining == 0 { out.push(prefix.clone()); }
            return;
        }
        let rest = maximum * (minima.len() - index - 1);
        let low = minima[index].max(remaining.saturating_sub(rest));
        let Some(high) = remaining.checked_sub(suffix[index + 1]) else { return };
        for size in low..=high.min(maximum) {
            prefix.push(size);
            walk(minima, suffix, maximum, index + 1, remaining - size, prefix, out);
            prefix.pop();
        }
    }
    let mut suffix = vec![0; minima.len() + 1];
    for index in (0..minima.len()).rev() {
        suffix[index] = minima[index] + suffix[index + 1];
    }
    let mut out = Vec::new();
    for total in suffix[0]..=minima.len() * maximum {
        walk(minima, &suffix, maximum, 0, total, &mut Vec::new(), &mut out);
    }
    out
}
/// Python `search._models` for the relational families, in its exact order:
/// domain sizes by total entities, used-relation subsets by tuple count (a
/// subset violating a permission pair or a data flag is not a candidate),
/// then constant denotations. A model Python rejects with a Background
/// generator is skipped.
struct Models<'a> {
    env: &'a Environment,
    sorts: Vec<String>,
    names: Vec<String>,
    used: BTreeSet<String>,
    sizes: Vec<Vec<usize>>,
    size_index: usize,
    domains: BTreeMap<String, Vec<String>>,
    atoms: Vec<(String, Vec<String>)>,
    subset: Vec<usize>,
    choices: Vec<usize>,
    choice_limits: Vec<usize>,
    ready: bool,
    done: bool,
}
impl<'a> Models<'a> {
    fn new(env: &'a Environment, document: &Document, maximum: usize,
           minimum: usize, guard: Option<&Formula>) -> Self {
        let sorts: Vec<_> = env.model_sorts().into_iter().collect();
        let minima: Vec<_> = sorts
            .iter()
            .map(|s| {
                if s == "$string" {
                    env.constants.values().filter(|t| *t == s).count()
                } else {
                    usize::from(env.constants.values().any(|t| t == s))
                }.max(minimum)
            })
            .collect();
        let mut used = BTreeSet::new();
        for f in document.formulas() {
            f.predicates(&mut used);
        }
        if let Some(formula) = guard {
            formula.predicates(&mut used);
        }
        for (name, (functional, total)) in &env.predicate_flags {
            if *functional || *total {
                used.insert(name.clone());
            }
        }
        // A defined predicate's table is computed; search its base dependencies.
        for (name, _, body) in env.definitions.iter().rev() {
            if used.contains(name) {
                body.predicates(&mut used);
            }
        }
        used.retain(|p| !env.is_defined(p));
        let sizes = domain_sizes(&minima, maximum);
        Self {
            env,
            sorts,
            names: env.constants.keys().cloned().collect(),
            used,
            done: sizes.is_empty(),
            sizes,
            size_index: 0,
            domains: BTreeMap::new(),
            atoms: Vec::new(),
            subset: Vec::new(),
            choices: Vec::new(),
            choice_limits: Vec::new(),
            ready: false,
        }
    }
    fn prepare(&mut self) -> Result<()> {
        self.domains = self.sorts.iter().zip(&self.sizes[self.size_index])
            .map(|(s, n)| (s.clone(), (0..*n).map(|i| format!("e{i}")).collect()))
            .collect();
        let count: usize = self.used.iter()
            .map(|p| self.env.predicates[p].iter().map(|s| self.domains[s].len()).product::<usize>())
            .sum();
        if count > 100_000 {
            return error("ResourceLimit", "used relation atom space exceeds 100,000");
        }
        self.atoms.clear();
        for p in &self.used {
            let sig = &self.env.predicates[p];
            let limits: Vec<_> = sig.iter().map(|s| self.domains[s].len()).collect();
            if limits.contains(&0) { continue; }
            let mut indices = vec![0; sig.len()];
            loop {
                self.atoms.push((p.clone(), indices.iter().zip(sig)
                    .map(|(i, s)| self.domains[s][*i].clone()).collect()));
                if !increment(&mut indices, &limits) { break; }
            }
        }
        self.subset.clear();
        self.choice_limits = self.names.iter().map(|n| self.domains[&self.env.constants[n]].len()).collect();
        self.choices = vec![0; self.names.len()];
        self.ready = true;
        Ok(())
    }
    fn relations(&self) -> BTreeMap<String, Vec<Vec<String>>> {
        let mut relations: BTreeMap<_, Vec<Vec<String>>> = self.env.predicates.keys()
            .filter(|p| !self.env.is_defined(p)).map(|p| (p.clone(), Vec::new())).collect();
        for index in &self.subset {
            let (p, row) = &self.atoms[*index];
            relations.get_mut(p).expect("declared relation").push(row.clone());
        }
        relations
    }
    /// Python `_relation_assignments`' filters: permission pairs and data flags.
    fn candidate(&self, relations: &BTreeMap<String, Vec<Vec<String>>>) -> bool {
        for (required, permitted) in &self.env.profile_pairs {
            if relations[required].iter().any(|row| !relations[permitted].contains(row)) {
                return false;
            }
        }
        for (name, (functional, total)) in &self.env.predicate_flags {
            if !(*functional || *total) || self.env.is_defined(name) { continue; }
            let rows = &relations[name];
            let sources: BTreeSet<&String> = rows.iter().map(|row| &row[0]).collect();
            if *functional && sources.len() != rows.len() { return false; }
            let domain = &self.domains[&self.env.predicates[name][0]];
            if *total && (sources.len() != domain.len()
                          || domain.iter().any(|e| !sources.contains(e))) {
                return false;
            }
        }
        true
    }
    /// The next relation subset (by size, then lexicographically) that is a candidate.
    fn advance_subset(&mut self) -> bool {
        loop {
            let n = self.atoms.len();
            let k = self.subset.len();
            if !(k > 0 && next_combination(&mut self.subset, n)) {
                if k == n { return false; }
                self.subset = (0..k + 1).collect();
            }
            if self.candidate(&self.relations()) { return true; }
        }
    }
    fn next(&mut self) -> Result<Option<FiniteModel>> {
        loop {
            if self.done {
                return Ok(None);
            }
            if !self.ready {
                self.prepare()?;
                // An empty denotation set yields no model for any subset.
                if self.choice_limits.contains(&0)
                    || (!self.candidate(&self.relations()) && !self.advance_subset()) {
                    self.next_sizes();
                    continue;
                }
            }
            let relations = self.relations();
            let constants: BTreeMap<_, _> = self.names.iter().zip(&self.choices)
                .map(|(n, i)| (n, self.domains[&self.env.constants[n]][*i].clone()))
                .collect();
            let model = FiniteModel::from_value(
                self.env,
                &json!({"complete":true,"domains":self.domains,"constants":constants,"relations":relations}),
            );
            if !increment(&mut self.choices, &self.choice_limits) && !self.advance_subset() {
                self.next_sizes();
            }
            match model {
                Ok(model) => return Ok(Some(model)),
                Err(err) if err.code == "InvalidModel"
                    && (err.message.starts_with("literals:") || err.message.ends_with("(literals)")
                        || err.message.starts_with("flags:") || err.message.ends_with("(flags)")
                        || err.message.ends_with("(profile)") || err.message.ends_with("(soft)")) => {
                    continue;
                }
                Err(err) => return Err(err),
            }
        }
    }
    fn next_sizes(&mut self) {
        self.ready = false;
        self.size_index += 1;
        self.done = self.size_index >= self.sizes.len();
    }
}

/// Python's conservative non-vacuity filter. It is a search constraint, never
/// a proof rule: every visited node and semantic-clause disjunct is charged.
fn nonvacuous(model: &FiniteModel, formula: &Formula, maximum: u64,
               semantic: bool) -> (bool, u64, bool) {
    fn clause_guards<'a>(node: &'a Formula, evaluator: &mut Evaluator<'a>,
                         guards: &mut Vec<&'a Formula>) -> Result<()> {
        evaluator.tick()?;
        match node {
            Formula::Or(left, right) => {
                clause_guards(left, evaluator, guards)?;
                clause_guards(right, evaluator, guards)?;
            }
            Formula::Not(body) => guards.push(body),
            _ => {}
        }
        Ok(())
    }
    fn hit<'a>(guards: &[&'a Formula], bindings: &mut Vec<usize>, path: &[usize],
               evaluator: &mut Evaluator<'a>, hits: &mut BTreeMap<Vec<usize>, bool>) -> Result<()> {
        let mut value = true;
        for guard in guards {
            value &= evaluator.formula(guard, bindings)?;
            if !value { break; }
        }
        *hits.entry(path.to_vec()).or_insert(false) |= value;
        Ok(())
    }
    fn walk<'a>(node: &'a Formula, model: &FiniteModel, evaluator: &mut Evaluator<'a>,
                bindings: &mut Vec<usize>, path: &mut Vec<usize>, universal: bool,
                in_clause: bool, semantic: bool, ok: &mut bool,
                hits: &mut BTreeMap<Vec<usize>, bool>) -> Result<()> {
        evaluator.tick()?;
        match node {
            Formula::Implies(left, right) => {
                hit(&[left], bindings, path, evaluator, hits)?;
                path.push(0);
                walk(left, model, evaluator, bindings, path, universal, false, semantic, ok, hits)?;
                path.pop(); path.push(1);
                walk(right, model, evaluator, bindings, path, universal, false, semantic, ok, hits)?;
                path.pop();
            }
            Formula::And(left, right) | Formula::Or(left, right) => {
                let is_or = matches!(node, Formula::Or(..));
                if semantic && universal && is_or && !in_clause {
                    let mut guards = Vec::new();
                    clause_guards(node, evaluator, &mut guards)?;
                    if !guards.is_empty() {
                        hit(&guards, bindings, path, evaluator, hits)?;
                    }
                }
                path.push(0);
                walk(left, model, evaluator, bindings, path, universal, is_or, semantic, ok, hits)?;
                path.pop(); path.push(1);
                walk(right, model, evaluator, bindings, path, universal, is_or, semantic, ok, hits)?;
                path.pop();
            }
            Formula::Not(body) => {
                path.push(0);
                walk(body, model, evaluator, bindings, path, universal, false, semantic, ok, hits)?;
                path.pop();
            }
            Formula::Forall(sort, body) | Formula::Exists(sort, body) => {
                let domain = &model.domains[sort];
                if domain.is_empty() { *ok = false; }
                for entity in 0..domain.len() {
                    bindings.push(entity); path.push(0);
                    walk(body, model, evaluator, bindings, path,
                         universal || matches!(node, Formula::Forall(..)), false,
                         semantic, ok, hits)?;
                    path.pop(); bindings.pop();
                }
            }
            _ => {}
        }
        Ok(())
    }
    let mut evaluator = Evaluator::new(model, maximum);
    let mut ok = true;
    let mut hits = BTreeMap::new();
    let result = walk(formula, model, &mut evaluator, &mut Vec::new(), &mut Vec::new(),
                      false, false, semantic, &mut ok, &mut hits);
    (ok && hits.values().all(|v| *v) && result.is_ok(), evaluator.work, result.is_err())
}
/// Exhaustive bounded search modulo the extensions of predicates absent from
/// the formulas. Unused predicates have empty extensions in every witness.
/// Neither NotFound nor ResourceLimit is evidence of entailment.
pub fn find_countermodel(
    env: &Environment,
    problem: &CountermodelProblem,
    bounds: SearchBounds,
) -> Result<SearchResult> {
    find_countermodel_min(env, problem, bounds, 0)
}

pub fn find_countermodel_min(
    env: &Environment,
    problem: &CountermodelProblem,
    bounds: SearchBounds,
    minimum: usize,
) -> Result<SearchResult> {
    find_countermodel_with_nonvacuity(env, problem, bounds, minimum, None, false)
}

pub fn find_countermodel_with_nonvacuity(
    env: &Environment, problem: &CountermodelProblem, bounds: SearchBounds,
    minimum: usize, guard: Option<&Formula>, semantic: bool,
) -> Result<SearchResult> {
    problem.document.belongs_to(env)?;
    if bounds.max_domain_size > 1000 || bounds.max_evaluations > MAX_EVALUATIONS
        || minimum > bounds.max_domain_size {
        return error("ResourceLimit", "search bounds exceed v0 envelope");
    }
    let mut models = Models::new(env, &problem.document, bounds.max_domain_size, minimum, guard);
    let mut result = SearchResult {
        status: "NotFound",
        model: None,
        models_checked: 0,
        evaluations: 0,
        bounds,
        detail: if guard.is_some() {
            "all used-relation interpretations satisfying the non-vacuity constraints within the domain bound were exhausted"
        } else { "all finite models within the domain bound were exhausted" },
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
        if let Some(formula) = guard {
            let (suitable, used, exhausted) = nonvacuous(
                &model, formula, bounds.max_evaluations - result.evaluations, semantic);
            result.evaluations += used;
            if exhausted {
                result.models_checked += 1;
                result.status = "ResourceLimit";
                result.detail = "evaluation budget exhausted";
                return Ok(result);
            }
            if !suitable {
                result.models_checked += 1;
                continue;
            }
        }
        let (status, _, _, work) = problem.values(
            &model, bounds.max_evaluations - result.evaluations)?;
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

/// Find a finite model on which two closed formulas differ. Neither exhaustion
/// nor a budget limit is a proof of equivalence.
pub fn find_distinguishing_model(
    env: &Environment,
    a: Formula,
    b: Formula,
    bounds: SearchBounds,
    minimum: usize,
) -> Result<SearchResult> {
    find_distinguishing_model_with_nonvacuity(env, a, b, bounds, minimum, None, false)
}

pub fn find_distinguishing_model_with_nonvacuity(
    env: &Environment, a: Formula, b: Formula, bounds: SearchBounds,
    minimum: usize, guard: Option<&Formula>, semantic: bool,
) -> Result<SearchResult> {
    env.require_checker()?;
    let document = Document::check(env, vec![a, b])?;
    if bounds.max_domain_size > 1000 || bounds.max_evaluations > MAX_EVALUATIONS
        || minimum > bounds.max_domain_size {
        return error("ResourceLimit", "search bounds exceed v0 envelope");
    }
    let mut models = Models::new(env, &document, bounds.max_domain_size, minimum, guard);
    let mut result = SearchResult {
        status: "NotFound", model: None, models_checked: 0, evaluations: 0,
        bounds, detail: if guard.is_some() {
            "all used-relation interpretations satisfying the non-vacuity constraints within the domain bound were exhausted"
        } else { "all finite models within the domain bound were exhausted" },
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
            || result.evaluations >= bounds.max_evaluations {
            result.status = "ResourceLimit";
            result.detail = "model-attempt or evaluation budget exhausted";
            return Ok(result);
        }
        if let Some(formula) = guard {
            let (suitable, used, exhausted) = nonvacuous(
                &model, formula, bounds.max_evaluations - result.evaluations, semantic);
            result.evaluations += used;
            if exhausted {
                result.models_checked += 1;
                result.status = "ResourceLimit";
                result.detail = "evaluation budget exhausted";
                return Ok(result);
            }
            if !suitable {
                result.models_checked += 1;
                continue;
            }
        }
        let mut evaluator = Evaluator::new(&model, bounds.max_evaluations - result.evaluations);
        let left = evaluator.formula(&document.formulas()[0], &mut Vec::new());
        evaluator.clear_closures();
        let right = if left.is_ok() {
            evaluator.formula(&document.formulas()[1], &mut Vec::new())
        } else {
            left.clone()
        };
        result.models_checked += 1;
        result.evaluations += evaluator.work;
        match (left, right) {
            (Ok(a), Ok(b)) if a != b => {
                result.status = "Found";
                result.detail = "";
                result.model = Some(model);
                return Ok(result);
            }
            (Ok(_), Ok(_)) => {}
            _ => {
                result.status = "ResourceLimit";
                result.detail = "evaluation budget exhausted";
                return Ok(result);
            }
        }
    }
}
