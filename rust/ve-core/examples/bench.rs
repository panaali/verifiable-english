#![forbid(unsafe_code)]
//! Timed checked API calls. JSON decoding/setup and process startup are excluded.
use serde_json::{Value, json};
use std::{hint::black_box, time::Instant};
use ve_core::*;
fn run(v: &Value) -> Result<Value> {
    let env = Environment::from_value(&v["environment"])?;
    let doc = Document::from_value(&env, &v["ast"])?;
    let iterations = v["iterations"].as_u64().unwrap();
    let repeats = v["repeats"].as_u64().unwrap();
    let mut samples = Vec::new();
    let mut observations = Value::Null;
    if v["kind"] == "evaluation" {
        let model = FiniteModel::from_value(&env, &v["model"])?;
        evaluate_formula(&doc, 0, &model, MAX_EVALUATIONS)?;
        for _ in 0..repeats {
            let start = Instant::now();
            let mut last = None;
            for _ in 0..iterations {
                last = Some(black_box(evaluate_formula(
                    black_box(&doc),
                    0,
                    black_box(&model),
                    MAX_EVALUATIONS,
                )?));
            }
            samples.push(start.elapsed().as_secs_f64() / iterations as f64);
            let last = last.unwrap();
            observations = json!({"value":last.value,"evaluations":last.evaluations});
        }
    } else {
        let (last, premises) = doc.formulas().split_last().unwrap();
        let problem = CountermodelProblem::new(&env, premises.to_vec(), last.clone())?;
        let bounds = SearchBounds {
            max_domain_size: v["max_domain_size"].as_u64().unwrap() as usize,
            ..Default::default()
        };
        find_countermodel(&env, &problem, bounds)?;
        for _ in 0..repeats {
            let start = Instant::now();
            let mut last = None;
            for _ in 0..iterations {
                last = Some(black_box(find_countermodel(
                    black_box(&env),
                    black_box(&problem),
                    bounds,
                )?));
            }
            samples.push(start.elapsed().as_secs_f64() / iterations as f64);
            let last = last.unwrap();
            observations = json!({"status":last.status,"models_checked":last.models_checked,"evaluations":last.evaluations});
        }
    }
    Ok(json!({"id":v["id"],"seconds_per_call":samples,"observations":observations}))
}
fn main() -> Result<()> {
    let bytes = std::fs::read(std::env::args().nth(1).expect("benchmark input path"))
        .map_err(|e| Error::new("InvalidInput", e.to_string()))?;
    let values = loads_json(&bytes)?;
    let results = values
        .as_array()
        .expect("benchmark array")
        .iter()
        .map(run)
        .collect::<Result<Vec<_>>>()?;
    println!("{}", json!(results));
    Ok(())
}
