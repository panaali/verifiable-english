"""kb-9 measurement aid (changes no product code): one RSP item through the ownership trace, with the Lean case
kinds it sends and those sent from inside `check_premises`.

usage (from the worktree root): uv run python docs/kernel/kb-9/measure_item.py <item id> <out.json>

Runs manage-agents/reviews/lean-ownership-20261112/trace_item.py (kb-10d's tools/ownership_trace.py is not on main)
in this process, after wrapping `LeanServicePool.run_bound` to count every case by `mode|kind` and, separately,
those whose call stack is inside the harness's `check_premises`."""
import collections
import json
import runpy
import sys
from pathlib import Path

TRACE = "/home/seyran/code/manage-agents/reviews/lean-ownership-20261112/trace_item.py"
item, out = sys.argv[1:3]
sys.path.insert(0, str(Path.cwd()))
from ve.backends import lean_service  # noqa: E402

calls, from_check = collections.Counter(), collections.Counter()
original = lean_service.LeanServicePool.run_bound


def run_bound(self, mode, cases, **kw):
    frame, inside = sys._getframe(1), False
    while frame is not None:
        if frame.f_code.co_name == "check_premises":
            inside = True
            break
        frame = frame.f_back
    for case in cases:
        key = f"{mode}|{case.get('kind') if isinstance(case, dict) else None}"
        calls[key] += 1
        if inside:
            from_check[key] += 1
    return original(self, mode, cases, **kw)


lean_service.LeanServicePool.run_bound = run_bound
sys.argv = [TRACE, "usecases/anthropic-rsp", item, out]
runpy.run_path(TRACE, run_name="__main__")
record = json.loads(Path(out).read_text())
record = {"id": record["id"], "error": record["error"], "verdict": record["verdict"], "key": record["key"],
          "agree": record["agree"], "python_decision_calls": record["python_decision_calls"],
          "lean_cases": dict(sorted(calls.items())), "lean_cases_from_check_premises": dict(sorted(from_check.items()))}
Path(out).write_text(json.dumps(record, indent=1, default=str) + "\n")
print(json.dumps({k: record[k] for k in ("id", "agree", "lean_cases", "lean_cases_from_check_premises")}))
