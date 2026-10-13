"""The readings route builds each candidate's document once per request and evaluates a pair lazily (lean-first
plan F5b; batch 3b review B1, B2).

* The compiled route is the oracle for "built once": a script run by the pinned toolchain reads the compiler's own
  IR and walks every function the service's `readings-route` mode can call (`runCaseReported`, by
  `runMode_readingsRoute`; the one-shot `ve_readings_route` and its `main` are gone since batch 1). No path may reach
  `one` (or `build`, which `one` may be inlined into) except through admission's candidate stage, which builds
  each candidate's document once and keeps it in the request's table (`candidateStage`), and the table's reader
  (`oneOf`); `free D` is the document without readings, built once in admission. The same walk from the specified
  functions (`pairFactsSpec`, `candidateJsonSpec`, `admitReadingsSpec`) does reach `one`, so the walk can fail.
  The S2a kinds keep S1's admission (`admitS2` reuses its `WellFormedDoc` through `wellFormedDoc_links`); `build`
  is reached otherwise only by `choiceDoc`, a compatible choice's whole document (composition-s2 4.1), which is
  not a candidate's. `free D` is built in admission and, for the certificate and model kinds, once more by
  `sharedEnv` (the shared vocabulary those kinds decode formulas over): one document per request, a gap recorded in
  docs/lean-first/b3b/DELTA.md (merge of ve-integration); under the unspecified completion once more by `freeU`
  (norm-defaults' author checks, readings-defaults.md 4.1 step 3; docs/readings-defaults/rd2a/DELTA.md). The filled
  document's admission builds its own table through the same staged admission (`admitDecoded`).
* Admission stops at the first diagnostic (`firstSome` is `findSome?`): a document whose first set's candidate is
  ill-formed is refused without validating the 119 candidates after it (4.0 s of CPU before, 0.26 s after).
* No pending candidate's document is built (batch 3b looprecheck B): admission builds the candidates with content
  only, and a set's findings skip a pair with a pending candidate before reading either side.
* The other reading's completions are scanned lazily: `RunExamples.lean` pins the evaluation counts at build time;
  here the review's reproducer (12 cells, ten fixed default rules) runs under a CPU deadline on the service
  (`lean_routes.completed_within`) far below what evaluating all 4,096 completions costs (7.8 s on the batch-3b head) and far above what the scan costs (0.07 s).
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from tests import lean_routes
from tests.subprocesses import HANG_TIMEOUT
from tests.test_readings_s1_lean import (M0, Q0, entry, env_k, k1_document, lean, norm, reading,  # noqa: F401
                                         reading_set, situation_id)
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

/-- A stop and every compiled function named under it (`f._boxed`, `f._lam_0`, `g._at_.f.spec_0`). -/
def under (stops : List Name) (n : Name) : Bool :=
  stops.any (fun s => s.isPrefixOf n || (n.toString.splitOn s!"_at_.{s}.").length > 1)

def main (args : List String) : IO UInt32 := do
  let module :: rest := args | return 2
  initSearchPath (← findSysroot)
  let env ← importModules #[{ module := module.toName }] {}
  let pick := fun (p : String) => rest.filterMap (fun a => (a.dropPrefix? p).map (·.toString.toName))
  let stops := pick "stop="
  let mut out : Array Json := #[]
  for e in pick "entry=" do
    let mut edges : Std.HashMap Name (Array Name) := {}
    let mut todo := #[e]
    let mut found := false
    while h : todo.size > 0 do
      let n := todo[todo.size - 1]
      todo := todo.pop
      if edges.contains n then continue
      let cs := if under stops n then #[] else
        match IR.findEnvDecl env n with
        | some (.fdecl (body := b) ..) => callees b #[]
        | _ => #[]
      if n == e then found := (IR.findEnvDecl env n).isSome
      edges := edges.insert n cs
      todo := todo ++ cs
    out := out.push (Json.mkObj [("entry", toJson e.toString), ("found", toJson found),
      ("edges", Json.mkObj (edges.toList.map (fun (k, v) => (k.toString, toJson (v.map (·.toString))))))])
  IO.println (Json.arr out).compress
  return 0
"""

ONE = "VE.Readings.one"
BUILD = "VE.Readings.build"
TABLE = ("VE.Readings.Wire.candidateStage", "VE.Readings.Wire.oneOf")
FREE = "VE.Readings.free"
CHOICE = "VE.Readings.choiceDoc"
SHARED = "VE.Readings.sharedEnv"
ENTRY = "VE.Readings.Run.runCaseReported"  # the service mode readings-route (`runMode_readingsRoute`)
SPECIFIED = ("VE.Readings.Run.pairFactsSpec", "VE.Readings.Run.candidateJsonSpec",
             "VE.Readings.Wire.admitReadingsSpec")


def named_under(name, function):
    """`name` is `function` or a compiled piece of it: `f._boxed`, `f._lam_0`, `g._at_.f.spec_0`."""
    return name == function or name.startswith(function + ".") or f"_at_.{function}." in name


@pytest.fixture(scope="module")
def walks(lean, tmp_path_factory):  # noqa: F811 (the route's build fixture)
    lake = shutil.which("lake")
    assert lake is not None, "lake is required for the complete test suite"
    script = tmp_path_factory.mktemp("walk") / "walk.lean"
    script.write_text(WALK)
    arguments = [f"entry={name}" for name in (ENTRY, *SPECIFIED)] + [f"stop={name}" for name in (*TABLE, FREE)]
    result = subprocess.run([lake, "env", "lean", "--run", str(script), "VE.Readings.Run", *arguments],
                            cwd=ROOT / "lean", capture_output=True, text=True, timeout=HANG_TIMEOUT, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
    walked = {walk["entry"]: walk for walk in json.loads(result.stdout)}
    for name, walk in walked.items():
        assert walk["found"], f"{name} has no compiled code"
    return {name: walk["edges"] for name, walk in walked.items()}


def callers(edges, function):
    return {caller for caller, callees in edges.items() for callee in callees if named_under(callee, function)}


def test_the_route_builds_a_candidates_document_only_in_the_request_table(walks):
    edges = walks[ENTRY]
    assert len(edges) > 1000  # the whole route, the chains' checks included
    built = sorted(name for name in edges if named_under(name, ONE))
    assert built == [], [(name, sorted(callers(edges, name))) for name in built]
    # `build` itself only for S2a's choice documents, never inlined into another caller.
    assert {caller for caller in callers(edges, BUILD) if not named_under(caller, BUILD)} == {CHOICE}
    # The table is built by admission alone, once per admitted document, and read through `oneOf`: `admitDecoded`
    # is S1's admission after decoding, which `admitReadings` runs on the decoded document and, under the unspecified
    # completion, `admitNDFull` on the filled document (readings-defaults.md 4.1 step 4) and, under the soft
    # completion, `admitUnsaid` on the document's items over the filled author vocabulary (rd-9-soft-chain.md 4.2),
    # each with its own table.
    assert callers(edges, TABLE[0]) == {"VE.Readings.Wire.admitDecoded"}
    assert {caller for caller in callers(edges, "VE.Readings.Wire.admitDecoded")
            if not named_under(caller, "VE.Readings.Wire.admitDecoded")} == \
        {"VE.Readings.Wire.admitReadings", "VE.Readings.Wire.admitNDFull", "VE.Readings.Wire.admitUnsaid"}
    assert "VE.Readings.Wire.onesOf" not in edges  # the table as specified
    assert "VE.Readings.Wire.oneOf" in edges
    assert {caller for caller in callers(edges, TABLE[1]) if not named_under(caller, TABLE[1])} == \
        {"VE.Readings.Wire.Admitted.side"}
    # `free D` once more under the unspecified completion: norm-defaults' author checks read it as a UDoc
    # (`ndTextWith`, readings-defaults.md 4.1 step 3), one document per request, a gap recorded in
    # docs/readings-defaults/rd2a/DELTA.md beside `sharedEnv`'s.
    assert callers(edges, FREE) == {"VE.Readings.Wire.frontText", SHARED, "VE.Readings.Wire.ndTextWith"}


ADMIT = ("VE.Readings.Wire.admitReadings", "VE.Readings.Wire.admitS2")
# Admission from the case's JSON for the replay theorems' entry points; the route admits once and passes the result.
JSON_ADMISSIONS = ("VE.Readings.Wire.admitNDFullJ", "VE.Readings.Wire.admitND", "VE.Readings.Wire.replaySup",
                   "VE.Readings.Wire.replayCertificate", "VE.Readings.Wire.replayModel")


def test_the_route_admits_the_case_document_once(walks):
    """Review B2 (and C2): under the completion `readings-validate` and `readings-separate` ran `admitReadings`, then
    `admitNDFullJ`, whose `admitS2` admitted the author's document again, and `runS2ND` admitted it again through
    `runS2` for a document with no content-bearing set. Now each case is admitted once (S1's `admitReadings`,
    continued by `admitS2Of` and `admitNDFull`, or `admitS2` for the S2a kinds). With companion components,
    `admitComponent` admits each part once before `runAdmitted` answers any of them; the answer path does not
    admit again. No JSON admission is reachable."""
    edges = walks[ENTRY]
    # Calls of the admissions themselves (their compiled helpers, such as the unit-id check `admitS2Of` shares,
    # admit nothing).
    calling = {admit: {caller for caller, callees in edges.items() if admit in callees} for admit in ADMIT}
    in_run_case = {n for n in edges if any(named_under(n, f"VE.Readings.Run.{f}")
                                           for f in ("runOne", "validateOne", "elaborateOne", "admitComponent",
                                                     "admitPart", "admitChecked"))}
    assert not any(named_under(n, "VE.Readings.Run.runCase") for n in set().union(*calling.values()))
    assert calling[ADMIT[1]] and calling[ADMIT[1]] <= in_run_case, sorted(calling[ADMIT[1]])
    assert calling[ADMIT[0]] and calling[ADMIT[0]] <= in_run_case | {ADMIT[1]}, sorted(calling[ADMIT[0]])
    assert not {n for n, callees in edges.items() if named_under(n, "VE.Readings.Run.runAdmitted")
                and set(callees) & set(ADMIT)}
    assert [n for n in edges if any(named_under(n, f) for f in JSON_ADMISSIONS)] == []
    # `admitS2Of` continues an admission: it never admits S1 again.
    assert not ({c for n, cs in edges.items() if named_under(n, "VE.Readings.Wire.admitS2Of") for c in cs} & set(ADMIT))


@pytest.mark.parametrize("specified", SPECIFIED)
def test_the_walk_finds_one_where_the_specified_computation_builds_it(walks, specified):
    assert ONE in walks[specified]


def review_case(raw):
    """The review's reproducer: twelve users (12 cells of the default reading's owned key), ten fixed default
    rules on `avoid_required`, the strict reading as witness on `help_required`, which no rule regulates."""
    users = ["u"] + [f"u{k}" for k in range(1, 12)]
    base = {"domains": {"agent": ["a"], "user": users}, "constants": {}, "relations": {"asks": []}}
    probe = {"outcome": {"predicate": "help_required", "tuple": ["a", "u"]}}
    fixed = [(f"fixed{k}", norm(f"fixed{k}", "avoid_required", True, "default")) for k in range(10)]
    document, sid = k1_document(raw, situation=entry(base, "strict", probe, False), fixed_units=fixed)
    return {"id": "review-b1", "kind": "readings-separate", "environment": raw, "document": document,
            "set": "rs1", "situation": sid, "other": "default"}, sid


def test_the_other_side_is_scanned_lazily_on_the_review_reproducer(lean):  # noqa: F811
    raw = env_k()
    case, sid = review_case(raw)
    completed = lean_routes.completed_within(lean, wire([case]), cpu_seconds=3)
    assert completed.returncode in (0, 1), (completed.returncode, completed.stderr)
    [row] = json.loads(completed.stdout)
    assert row == {"id": "review-b1", "status": "ok", "set": "rs1",
                   "pair": {"situation": sid, "witness": "strict", "separated": False, "witness_admissible": True,
                            "witness_value": False, "other_admissible": True}}


def first_error_document(raw, sets=60, fixed=10):
    """`sets` twin sets over `fixed` fixed default rules; only the first set's default candidate is ill-formed (a
    rule on `avoid_required` over the strict rule `hard` on `help_required`)."""
    units = [{"id": "hard", "kind": "norm", "content": norm("hard", "help_required", True)}]
    units += [{"id": f"f{k}", "kind": "norm", "content": norm(f"f{k}", "avoid_required", True, "default")}
              for k in range(fixed)]
    reading_sets = []
    for s in range(sets):
        sigma = entry(M0, "default", Q0, False, decisions=[{"key": {"excepted": f"r{s}"}, "tuples": [["a", "u"]]}])
        sid = situation_id(raw, sigma)
        over = ("hard",) if s == 0 else ()
        reading_sets.append(reading_set(f"rs{s}", f"u{s}", [
            reading("strict", norm(f"r{s}", "avoid_required", True), {"default": sid}),
            reading("default", norm(f"r{s}", "avoid_required", True, "default", over=over), {"strict": sid})],
            {sid: sigma}))
        units.append({"id": f"u{s}"})
    return {"units": units, "reading_sets": reading_sets}


def test_admission_stops_at_the_first_ill_formed_candidate(lean):  # noqa: F811
    raw = env_k()
    case = {"id": "first", "kind": "readings-validate", "environment": raw, "document": first_error_document(raw)}
    completed = lean_routes.completed_within(lean, wire([case]), cpu_seconds=2)
    assert completed.returncode == 1, (completed.returncode, completed.stderr)
    assert json.loads(completed.stdout) == [{"id": "first", "status": "error", "error":
        "PrecedenceAcrossPredicates: rule r0 on avoid_required, rule hard on help_required under rs0@1:1"}]


def pending_document(sets, per_set, fixed=10):
    """`fixed` fixed default rules and `sets` sets of `per_set` readings each, all pending except the first set's
    first reading (a strict rule on `help_required`)."""
    units = [{"id": f"f{k}", "kind": "norm", "content": norm(f"f{k}", "avoid_required", True, "default")}
             for k in range(fixed)]
    reading_sets = []
    for s in range(sets):
        readings = [reading(f"p{k}", None, {}) for k in range(per_set)]
        if s == 0:
            readings[0] = reading("p0", norm("active", "help_required", True), {})
        reading_sets.append(reading_set(f"rs{s}", f"u{s}", readings, {}))
        units.append({"id": f"u{s}"})
    return {"units": units, "reading_sets": reading_sets}


def assert_one_active_row(row, per_set):
    assert row["status"] == "ok" and row["content_bearing"], row
    [answered] = row["sets"]
    assert (answered["set"], answered["pairs"], answered["findings"]) == ("rs0", [], [])
    candidates = answered["candidates"]
    assert [(c["id"], c["pending"]) for c in candidates] == [("p0", False)] + [(f"p{k}", True)
                                                                             for k in range(1, per_set)]
    assert candidates[0]["findings"] == [] and candidates[0]["owned"] == []
    assert [entry["name"] for entry in candidates[0]["shared"]] == [f"soft__excepted__f{k}" for k in range(10)]


@pytest.mark.parametrize("sets, per_set", [(60, 2), (120, 2), (1, 60)], ids=["many-sets", "more-sets", "one-set"])
def test_no_pending_candidates_document_is_built(lean, sets, per_set):  # noqa: F811
    """Batch 3b looprecheck B: admission built the 119 pending candidates' documents of `many-sets` (the review's
    reproducer) though 4.4 skips them (1.1-2.2 s of CPU before, 0.09-0.22 s after); `more-sets` doubles the sets,
    which makes the head before the fix five times the limit (5.0 s, against 0.16 s). The table now holds the
    candidates with content alone (`onesOf_active`), so the findings of `one-set` must not read a pending
    candidate's side either: each of its 1,770 pairs would rebuild both documents outside the table (5.0 s)."""
    raw = env_k()
    case = {"id": "pending", "kind": "readings-validate", "environment": raw,
            "document": pending_document(sets, per_set)}
    completed = lean_routes.completed_within(lean, wire([case]), cpu_seconds=1)
    assert completed.returncode == 0, (completed.returncode, completed.stderr)
    [row] = json.loads(completed.stdout)
    assert_one_active_row(row, per_set)
