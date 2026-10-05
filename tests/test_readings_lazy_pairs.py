"""The readings route evaluates the other reading's side of a pair lazily (batch 3d review B; the DRI note of
2026-10-04 on batch 3b's eager completions).

`completionsOn` built every completion's admissibility before `.all`/`.any` could stop: on a 12-cell query whose
first completion decides both answers it evaluated all 4,096. The route now runs `pairEval`, whose other side goes
through `scanOthers` (each admissibility when the scan reaches it, each value only when needed). The first two
checks pin it; the third checks the answer:

* Without timing, at build time: `lean/VE/Readings/RunExamples.lean` runs `pairEval` in a counting monad and pins
  the evaluations (one admissibility and one value on the 12-cell query, not 4,096). `VE.lean` imports it, so
  `lake build` fails when a count changes.
* The compiled route is the oracle for "the route runs the counted function": a script run by the pinned toolchain
  reads the compiler's IR of `ve_readings_route` and walks every function `main` can call. `pairFactsIn` must call
  `pairEval` and the walk must reach `scanOthers`, so a route that evaluates the completions some other way fails.
* End to end: the review's reproducer (12 cells, ten fixed default rules) gives the specified answer. Its CPU
  limit only stops a runaway route: with each side's layers built once (batch 3d), evaluating all 4,096
  completions here costs 0.37 s against the scan's 0.09 s (seeded mutant M3), and the generated-layer limits
  admit no heavier side, so time cannot tell the two apart. The counts and the IR walk above are the regression.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from tests.subprocesses import HANG_TIMEOUT, run_cpu_bounded
from tests.test_readings_s1_lean import entry, env_k, k1_document, lean, norm  # noqa: F401
from ve.readings_s1 import wire

ROOT = Path(__file__).resolve().parents[1]

WALK = r"""
import Lean
open Lean

partial def callees : IR.FnBody → Array Name → Array Name
  | .vdecl _ _ e b, acc =>
    let acc := match e with
      | .fap c _ | .pap c _ => acc.push c
      | _ => acc
    callees b acc
  | .jdecl _ _ v b, acc => callees b (callees v acc)
  | .case _ _ _ alts, acc => alts.foldl (fun acc a => callees a.body acc) acc
  | b, acc => if b.isTerminal then acc else callees b.body acc

def main (args : List String) : IO UInt32 := do
  let module :: entry :: _ := args | return 2
  initSearchPath (← findSysroot)
  let env ← importModules #[{ module := module.toName }] {}
  let mut edges : Std.HashMap Name (Array Name) := {}
  let mut todo := #[entry.toName]
  while h : todo.size > 0 do
    let n := todo[todo.size - 1]
    todo := todo.pop
    if edges.contains n then continue
    let cs := match IR.findEnvDecl env n with
      | some (.fdecl (body := b) ..) => callees b #[]
      | _ => #[]
    edges := edges.insert n cs
    todo := todo ++ cs
  IO.println (Json.mkObj (edges.toList.map (fun (k, v) => (k.toString, toJson (v.map (·.toString)))))).compress
  return 0
"""

ENTRY = "VE.Readings.Run.main"
PAIR_FACTS = "VE.Readings.Run.pairFactsIn"
PAIR_EVAL = "VE.Readings.pairEval"
SCAN = "VE.Readings.scanOthers"


def named_under(name, function):
    """`name` is `function` or a compiled piece of it: `f._boxed`, `f._lam_0`, `f._redArg`, `g._at_.f.spec_0`."""
    return name == function or name.startswith(function + ".") or f"_at_.{function}." in name


@pytest.fixture(scope="module")
def edges(lean, tmp_path_factory):  # noqa: F811 (the route's build fixture)
    lake = shutil.which("lake")
    assert lake is not None, "lake is required for the complete test suite"
    script = tmp_path_factory.mktemp("walk") / "walk.lean"
    script.write_text(WALK)
    result = subprocess.run([lake, "env", "lean", "--run", str(script), "VE.Readings.Run", ENTRY],
                            cwd=ROOT / "lean", capture_output=True, text=True, timeout=HANG_TIMEOUT, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
    return json.loads(result.stdout)


def test_the_route_runs_the_counted_pair_evaluation(edges):
    assert len(edges) > 1000  # the whole route, the chains' checks included
    facts = [name for name in edges if named_under(name, PAIR_FACTS)]
    assert facts, "the route does not reach pairFactsIn"
    # pairFactsIn reaches the other side only through pairEval: no completion is evaluated beside it.
    called = {callee for name in facts for callee in edges[name]}
    assert any(named_under(callee, PAIR_EVAL) for callee in called), sorted(called)
    assert any(named_under(name, SCAN) for name in edges), "the route does not reach the lazy scan"
    # The eager form is gone from the source, so nothing can reach it.
    assert not any("completionsOn" in name or "separatesWith" in name for name in edges)


def test_the_step_counts_are_built_with_the_library():
    imports = (ROOT / "lean/VE.lean").read_text().splitlines()
    assert "import VE.Readings.RunExamples" in imports
    examples = (ROOT / "lean/VE/Readings/RunExamples.lean").read_text()
    # The review's query: 12 cells, 4,096 completions, one admissibility and one value evaluated.
    assert "(assignments K1 \"rs1\" 1 m12).length == 4096" in examples
    assert "#guard counted K1 \"rs1\" 0 1 σHelp12 == ((false, true, some false, true, none), (1, 1))" in examples


def review_case(raw):
    """The review's reproducer: twelve users (12 cells of the default reading's owned key), ten fixed default
    rules on `avoid_required`, the strict reading as witness on `help_required`, which no rule decides."""
    users = ["u"] + [f"u{k}" for k in range(1, 12)]
    base = {"domains": {"agent": ["a"], "user": users}, "constants": {}, "relations": {"asks": []}}
    probe = {"outcome": {"predicate": "help_required", "tuple": ["a", "u"]}}
    fixed = [(f"fixed{k}", norm(f"fixed{k}", "avoid_required", True, "default")) for k in range(10)]
    document, sid = k1_document(raw, situation=entry(base, "strict", probe, False), fixed_units=fixed)
    return {"id": "review-b", "kind": "readings-separate", "environment": raw, "document": document,
            "set": "rs1", "situation": sid, "other": "default"}, sid


def test_the_review_reproducer_gives_the_specified_answer(lean):  # noqa: F811
    raw = env_k()
    case, sid = review_case(raw)
    completed, cpu = run_cpu_bounded([str(lean), "-"], json.dumps(wire([case])), cpu_seconds=3)
    assert completed.returncode in (0, 1), (completed.returncode, completed.stderr, cpu)
    [row] = json.loads(completed.stdout)
    assert row == {"id": "review-b", "status": "ok", "set": "rs1",
                   "pair": {"situation": sid, "witness": "strict", "separated": False, "witness_admissible": True,
                            "witness_value": False, "other_admissible": True}}
