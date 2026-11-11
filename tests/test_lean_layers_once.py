"""Every route the service runs computes a document's layers once (lean-first batch 7 review B1).

`subst` reads each layer symbol through `expTable`, and `envAt` re-sorts the stratum DAG, for every formula; the
checks and outputs built on them (`semanticCheck`, `checkSoft`, `softSemanticCheck`, `targets`, `InFragment`) were
quartic in the regulated predicates of the environment: about 2 s of the service's CPU for one rights request over
the UDHR pilot's 62, which the readings route paid once per candidate. Each has a hoisted twin, proved equal to it,
registered with `@[csimp]` so that compiled code calls the twin (`VE/Norms/Once.lean`, `VE/Norms/LayersOnce.lean`,
`VE/SoftNorms/Once.lean`).

* The class, from the compiler's own records: a script run by the pinned toolchain reads the `@[csimp]` registry and
  the IR, and walks every function the service's route modes can call. No walk may reach an original that a
  registered `VE` twin replaces: a function compiled before the twin was registered (or in a module that does not
  import it) still calls the original, and the walk finds it. The walk from such a function (`validateSoft`'s own
  body, compiled before its twins) does reach the originals, so the walk can fail.
* The cost, on the service: one rights request over 64 regulated predicates stays far below what the originals
  spent on 62 (`lean_routes.completed_within`).
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from tests import lean_routes
from tests.subprocesses import HANG_TIMEOUT

ROOT = Path(__file__).resolve().parents[1]
ROUTE = "ve_rights_route"  # the service mode `rights`, through tests/lean_routes.py


@pytest.fixture(scope="module")
def lean():
    if not lean_routes.SERVICE.exists():
        pytest.skip("the Lean service has not been built")
    return ROUTE

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
  let module :: entries := args | return 2
  initSearchPath (← findSysroot)
  let env ← importModules #[{ module := module.toName }] {} (loadExts := true)
  let pairs := ((Compiler.CSimp.ext.getState env).map.toList).filter (fun (_, g) => (`VE).isPrefixOf g)
  let originals : NameSet := pairs.foldl (fun s (f, _) => s.insert f) {}
  let mut out : Array Json := #[]
  for e in entries do
    let e := e.toName
    let mut seen : NameSet := {}
    let mut todo := #[e]
    let mut reached : Array Json := #[]
    while h : todo.size > 0 do
      let n := todo[todo.size - 1]
      todo := todo.pop
      if seen.contains n then continue
      seen := seen.insert n
      let cs := match IR.findEnvDecl env n with
        | some (.fdecl (body := b) ..) => callees b #[]
        | _ => #[]
      for c in cs do
        if originals.contains c then
          reached := reached.push (Json.mkObj [("caller", toJson n.toString), ("original", toJson c.toString)])
      todo := todo ++ cs
    out := out.push (Json.mkObj [("entry", toJson e.toString), ("found", toJson (IR.findEnvDecl env e).isSome),
      ("size", toJson seen.size), ("reached", Json.arr reached)])
  IO.println (Json.mkObj [("pairs", toJson (pairs.map (fun (f, g) => [f.toString, g.toString]))),
    ("walks", Json.arr out)]).compress
  return 0
"""

# The service's route modes (`VE.Service.runMode`): every one of them, so a route that decodes a soft or rights
# source through another module is walked too.
ENTRY = "VE.Service.runMode"
COMPILED_BEFORE = "VE.SoftNorms.validateSoft"  # its compiled body calls `checkSoft` and `softSemanticCheck`
# The originals the twins replace, by the twins' modules.
TWINNED = {"VE.Norms.semanticCheck", "VE.Norms.validate", "VE.Norms.WellFormed", "VE.Norms.targets",
           "VE.Norms.InFragment", "VE.SoftNorms.checkSoft", "VE.SoftNorms.softSemanticCheck",
           "VE.SoftNorms.validateSoft", "VE.SoftNorms.WellFormedSoft", "VE.SoftNorms.InFragment"}


@pytest.fixture(scope="module")
def walks(lean, tmp_path_factory):
    lake = shutil.which("lake")
    assert lake is not None, "lake is required for the complete test suite"
    script = tmp_path_factory.mktemp("walk") / "walk.lean"
    script.write_text(WALK)
    result = subprocess.run([lake, "env", "lean", "--run", str(script), "VE.Service.Protocol", ENTRY,
                             COMPILED_BEFORE], cwd=ROOT / "lean", capture_output=True, text=True,
                            timeout=HANG_TIMEOUT, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads(result.stdout)
    for walk in data["walks"]:
        assert walk["found"], f"{walk['entry']} has no compiled code"
    return {tuple(pair) for pair in data["pairs"]}, {walk["entry"]: walk for walk in data["walks"]}


def test_every_twin_is_registered(walks):
    pairs, _ = walks
    assert {original for original, _ in pairs} >= TWINNED


def test_no_route_of_the_service_calls_a_twinned_original(walks):
    _, walked = walks
    walk = walked[ENTRY]
    assert walk["size"] > 10000  # every route mode, the chains' checks included
    assert walk["reached"] == [], sorted({(r["caller"], r["original"]) for r in walk["reached"]})


def test_the_walk_finds_an_original_from_code_compiled_before_its_twin(walks):
    _, walked = walks
    reached = {r["original"] for r in walked[COMPILED_BEFORE]["reached"]}
    assert {"VE.SoftNorms.checkSoft", "VE.SoftNorms.softSemanticCheck"} <= reached


def wide_rights_environment(count):
    """A rights environment with `count` regulated predicates (W1's limit is 64), each a permission over
    (state, person), and no rights source line: the cost measured is the environment's alone."""
    from tests.test_rights import rights_env
    from tests.test_norms import permission
    raw = rights_env()
    for index in range(count - len(raw["vocabulary"]["predicates"])):
        word = "".join(chr(ord("a") + int(digit)) for digit in str(index))  # act phrases are words of letters
        raw["vocabulary"]["predicates"][f"act{index}_permitted"] = permission(
            "allow", act=f"{{0}} act {word}word on {{1}}", args=("state", "person"))
    return raw


@pytest.mark.live_service
def test_a_rights_request_over_a_wide_environment_is_cheap(lean):
    from ve.backends.relay import decide
    from ve.rights_route import _wire
    raw = wide_rights_environment(64)
    case = {"id": "wide", "kind": "rights-elaborate", "environment": _wire(raw), "document": [{"source_units": []}]}
    assert decide("rights", [case])[0]["status"] == "ok"
    # Before the twins this request spent 1.6-2.0 s of CPU (62 predicates, UDHR pilot); now well under 0.2 s.
    completed = lean_routes.completed_within(lean, [case], cpu_seconds=0.5)
    assert completed.returncode == 0, (completed.returncode, completed.stderr)
