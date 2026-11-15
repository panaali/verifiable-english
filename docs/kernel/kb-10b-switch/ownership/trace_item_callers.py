"""reviews/lean-ownership-20261112/trace_item.py with one addition: for each Python decision function called, the
distinct call chains from the harness (usecases/) frame down to it ("where it is called from").
usage: python3 trace_item_callers.py <case-dir> <item id> <out.json> (run from the VE worktree root)."""
import json, os, sys, threading, importlib.util
case_dir, item_id, out = sys.argv[1:4]
ROOT = os.path.abspath("ve") + os.sep
UC = os.path.abspath("usecases") + os.sep
sys.path.insert(0, os.getcwd())
spec = importlib.util.spec_from_file_location("rsp_run", os.path.join(case_dir, "run.py"))
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
key = {k["id"]: k for k in json.load(open(os.path.join(case_dir, "answer-key.json")))["items"]}
entry = key[item_id]
DECISION = {("norms.py", "selection"), ("norms.py", "outcome"), ("norms.py", "_expand"), ("norms.py", "selected_rules"),
            ("norms.py", "_check_conflict_python")}
def qual(code):
    return getattr(code, "co_qualname", code.co_name)
def decision(f, q):
    return (f, q.rsplit(".", 1)[-1]) in DECISION or (f == "evaluate.py" and q.startswith("_Evaluator"))
seen = set(); chains = {}
def prof(frame, event, arg):
    if event == "call":
        f = frame.f_code.co_filename
        if f.startswith(ROOT):
            q = qual(frame.f_code); rel = f[len(ROOT):]
            seen.add((rel, q))
            if decision(rel, q):
                key_ = f"{rel}:{q}"
                bucket = chains.setdefault(key_, set())
                if len(bucket) < 12:
                    chain, fr = [], frame.f_back
                    while fr is not None:
                        ff = fr.f_code.co_filename
                        if ff.startswith(UC):
                            chain.append(f"{ff[len(UC):]}:{qual(fr.f_code)}:{fr.f_lineno}"); break
                        if ff.startswith(ROOT):
                            chain.append(f"{ff[len(ROOT):]}:{qual(fr.f_code)}")
                        fr = fr.f_back
                    bucket.add(" <- ".join(chain))
sys.setprofile(prof); threading.setprofile(prof)
err = None
try:
    result = mod.answer({n: entry[n] for n in ("id", "case", "item")})
except Exception as e:
    result = None; err = f"{type(e).__name__}: {e}"
finally:
    sys.setprofile(None); threading.setprofile(None)
dec = sorted(f"{f}:{q}" for f, q in seen if decision(f, q))
json.dump({"id": item_id, "family": item_id.split("-")[0].rstrip("0123456789") or item_id[0],
           "error": err, "route": (result or {}).get("route"),
           "verdict": None if result is None else mod.verdict(result), "key": entry["key"],
           "agree": False if result is None else mod.same_set(entry["key"], result),
           "python_decision_calls": dec, "called_from": {k: sorted(v) for k, v in sorted(chains.items())},
           "functions": sorted(f"{f}:{q}" for f, q in seen)}, open(out, "w"), indent=1, default=str)
