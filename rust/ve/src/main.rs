#![forbid(unsafe_code)]
use serde_json::{Value,json};
use std::io::{self,BufRead,Read,Write};
use ve_core::*;

fn read(path: &str) -> Result<Vec<u8>> {
    let mut out=Vec::new();
    let input: Box<dyn Read>=if path=="-" {Box::new(io::stdin())} else {Box::new(std::fs::File::open(path).map_err(|e| Error::new("InvalidInput",e.to_string()))?)};
    input.take((MAX_PACKAGE_BYTES+1) as u64).read_to_end(&mut out).map_err(|e| Error::new("InvalidInput",e.to_string()))?;
    if out.len()>MAX_PACKAGE_BYTES {return Err(Error::new("ResourceLimit","input exceeds 16 MiB"));} Ok(out)
}
fn field<'a>(v: &'a Value,name: &str) -> Result<&'a Value> {v.get(name).ok_or_else(|| Error::new("InvalidInput",format!("missing {name}")))}
fn case(v: &Value) -> Result<Value> {
    let env=Environment::from_value(field(v,"environment")?)?;
    let doc=if let Some(ast)=v.get("ast") {Document::from_value(&env,ast)?} else {
        parse(&env,field(v,"source")?.as_str().ok_or_else(|| Error::new("SyntaxError","source must be text"))?.as_bytes())?
    };
    if let Some(source)=v.get("source") {
        let parsed=parse(&env,source.as_str().ok_or_else(|| Error::new("SyntaxError","source must be text"))?.as_bytes())?;
        if parsed!=doc {return Err(Error::new("TypeMismatch","source/AST mismatch"));}
    }
    let mut out=json!({"id":v.get("id").cloned().unwrap_or(json!("")),"status":"ok","canonical":print_document(&doc),"ast":doc.to_value(),"environment_id":env.environment_id(),"meaning_id":doc.meaning_id()?,"formula_meaning_ids":(0..doc.formulas().len()).map(|i| doc.formula_meaning_id(i)).collect::<Result<Vec<_>>>()?});
    if let Some(model)=v.get("model") {
        let model=FiniteModel::from_value(&env,model)?;
        let values=(0..doc.formulas().len()).map(|i| evaluate_formula(&doc,i,&model,MAX_EVALUATIONS).and_then(|r| r.value.ok_or_else(|| Error::new("ResourceLimit","evaluation budget exhausted")))).collect::<Result<Vec<_>>>()?;
        out["value"]=json!(values.iter().all(|v| *v)); out["values"]=json!(values); out["model_id"]=json!(model.model_id());
    }
    Ok(out)
}
fn case_record(v: &Value) -> Value {match case(v) {Ok(out)=>out,Err(e)=>json!({"id":v.get("id").cloned().unwrap_or(json!("")),"status":"error","error":e})}}
fn option(args: &[String],name: &str) -> Result<String> {
    args.iter().position(|x| x==name).and_then(|i| args.get(i+1)).cloned().ok_or_else(|| Error::new("InvalidInput",format!("missing {name}")))
}
fn run(args: &[String]) -> Result<i32> {
    let Some(command)=args.first().map(String::as_str) else {help();return Ok(0)};
    match command {
        "--help"|"help"=>{help();Ok(0)},
        "conformance"=>{
            let data=loads_json(&read(args.get(1).map_or("-",String::as_str))?)?;
            let cases=if let Some(a)=data.as_array() {a.clone()} else {vec![data]};
            let out: Vec<_>=cases.iter().map(case_record).collect(); let failed=out.iter().any(|r| r["status"]!="ok");
            println!("{}",json!(out)); Ok(i32::from(failed))
        }
        "jsonl"=>{
            let input: Box<dyn Read>=if args.get(1).is_none_or(|x| x=="-") {Box::new(io::stdin())} else {Box::new(std::fs::File::open(&args[1]).map_err(|e| Error::new("InvalidInput",e.to_string()))?)};
            let mut input=io::BufReader::new(input); let mut stdout=io::BufWriter::new(io::stdout().lock()); let mut failed=false;
            loop {
                let mut line=Vec::new();
                let count=(&mut input).take((MAX_PACKAGE_BYTES+1) as u64).read_until(b'\n',&mut line).map_err(|e| Error::new("InvalidInput",e.to_string()))?;
                if count==0 {break;}
                let out=match loads_json(&line) {Ok(v)=>case_record(&v),Err(e)=>json!({"status":"error","error":e})};
                failed |= out["status"]!="ok";
                writeln!(stdout,"{out}").map_err(|e| Error::new("InvalidInput",e.to_string()))?;
                if count>MAX_PACKAGE_BYTES {break;}
            }
            stdout.flush().map_err(|e| Error::new("InvalidInput",e.to_string()))?; Ok(i32::from(failed))
        }
        "parse"|"format"|"evaluate"=>{
            let env=Environment::from_json(&read(&option(args,"--env")?)?)?;
            let doc=parse(&env,&read(&option(args,"--source")?)?)?;
            if command=="format" {print!("{}",print_document(&doc));return Ok(0);}
            if command=="parse" {println!("{}",json!({"ast":doc.to_value(),"canonical":print_document(&doc),"environment_id":env.environment_id(),"meaning_id":doc.meaning_id()?,"assurance":"experimental","intent":"unconfirmed","proof":"not_checked"}));return Ok(0);}
            let model=FiniteModel::from_json(&env,&read(&option(args,"--model")?)?)?;
            let result=evaluate(&doc,&model,MAX_EVALUATIONS)?;
            println!("{}",serde_json::to_string(&result).unwrap());
            Ok(match result.value {Some(true)=>0,Some(false)=>1,None=>2})
        }
        "canonical-json"=>{let v=loads_json(&read(args.get(1).map_or("-",String::as_str))?)?;io::stdout().write_all(&canonical_json(&v)?).map_err(|e| Error::new("InvalidInput",e.to_string()))?;Ok(0)},
        _=>Err(Error::new("InvalidInput","unknown command; use --help")),
    }
}
fn help() {println!("VE v0 experimental Rust core\nve parse|format --env ENV.json --source SOURCE.ve\nve evaluate --env ENV.json --source SOURCE.ve --model MODEL.json\nve conformance [CASES.json|-]\nve jsonl [CASES.jsonl|-]\nve canonical-json [INPUT.json|-]");}
fn main() {let code=match run(&std::env::args().skip(1).collect::<Vec<_>>()) {Ok(code)=>code,Err(e)=>{eprintln!("{}",json!({"status":"error","error":e}));2}};std::process::exit(code);}
