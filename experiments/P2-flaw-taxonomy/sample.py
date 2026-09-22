import json, random, csv, pandas as pd
from datasets import load_dataset, load_from_disk
SEED=20260922
out={}
# 1 ProcessBench: 13/12/13/12 across splits, label>=0
pb=load_dataset("Qwen/ProcessBench")
items=[]
for sp,n in [("gsm8k",12),("math",13),("olympiadbench",13),("omnimath",12)]:
    ds=[r for r in pb[sp] if r["label"]>=0]
    rng=random.Random(SEED); 
    for r in rng.sample(ds,n):
        items.append(dict(id=r["id"],problem=r["problem"][:900],prev=r["steps"][max(0,r["label"]-2):r["label"]],err_step=r["label"],step=r["steps"][r["label"]], nsteps=len(r["steps"])))
out["processbench"]=items
# 2 BBM logical deduction
rows=[json.loads(l) for l in open("bbm/logical_deduction.jsonl")]
bad=[(i,r) for i,r in enumerate(rows) if r.get("mistake_index") is not None]
print("bbm ld with mistake",len(bad),"of",len(rows))
rng=random.Random(SEED)
out["bbm_ld"]=[dict(id=f"ld_{i}",input=r["input"],prev=r["steps"][max(0,r["mistake_index"]-1):r["mistake_index"]],mi=r["mistake_index"],step=r["steps"][r["mistake_index"]],target=r.get("target")) for i,r in rng.sample(bad,50)]
# 3 MathArena USAMO25+IMO25 judge-1 on failed solutions
ma=[]
for n in ["MathArena__usamo_2025_outputs","MathArena__imo_2025_outputs"]:
    ds=load_from_disk(n)["train"]
    for i,r in enumerate(ds):
        if r["points_judge_1"] is not None and float(r["points_judge_1"])<float(r["max_points_judge_1"]):
            gd=json.loads(r["grading_details_judge_1"]) if r["grading_details_judge_1"] else []
            ma.append(dict(id=f"{n.split('__')[1].split('_outputs')[0]}_p{r['problem_idx']}_{r['model_name']}_{r['idx_answer']}",problem=r["problem"][:500],cat=r["error_judge_1"],pts=r["points_judge_1"],details=[(g.get("title"),g.get("points"),g.get("max_points"),g.get("desc")) for g in gd]))
print("matharena failed",len(ma))
rng=random.Random(SEED); out["matharena"]=rng.sample(ma,50)
# 4 OPC incorrect with feedback (exclude matharena split to avoid overlap)
opc=load_from_disk("INSAIT-Institute__OPC")
cand=[]
for sp in ["generic","best_of_n","pass_at_n","putnambench"]:
    for r in opc[sp]:
        if r["score"] and r["score"][0]==0 and r["feedback"] and r["feedback"][0] and len(r["feedback"][0])>30:
            cand.append(dict(id=f"{sp}:{r['problem_id']}:{r['model_id']}:{r['judge_id'][0]}",problem=r["problem"][:500],feedback=r["feedback"][0][:1500]))
print("opc cand",len(cand))
rng=random.Random(SEED); out["opc"]=rng.sample(cand,50)
# 5 LogicClimate
df=pd.read_csv("logic/data/climate_all.csv").dropna(subset=["source_article"]).reset_index(drop=True)
print(df.logical_fallacies.value_counts())
rng=random.Random(SEED); idx=rng.sample(range(len(df)),50)
out["logicclimate"]=[dict(id=f"climate_all_row{i}",label=df.iloc[i]["logical_fallacies"],text=df.iloc[i]["source_article"][:700]) for i in idx]
json.dump(out,open("samples.json","w"),indent=1)
