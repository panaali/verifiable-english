"""The encoder theorems (`lean/ResponseShape/Encoders.lean`) can fail (lf-1 recheck 3, B).

`ResponseShape.Encoders.runMode_fits` proves that every row every mode returns fits the skeleton of
the mode's row shape, extracted from `ResponseShape.Schemas` when Lean builds. These tests show the
proofs are not vacuous: the tactic proof of a genuine encoder still goes through on a copy of it,
and fails on each mutant of the encoder (a field added, dropped or renamed, at the top or nested,
or a field the shape ties to another field's value) and on each mutant of the shape (a field
required that the encoder never writes, a field it writes that the shape drops), so a change on
either side fails `lake build` until the two agree again.
"""
from __future__ import annotations

import shutil
import subprocess

import pytest

from subprocesses import HANG_TIMEOUT
from tests.lean_build import LEAN, lean_build

HEADER = """import ResponseShape.FitsTactic
import VE.Service.Protocol
open Lean ResponseShape ResponseShape.Skeletons
"""


@pytest.fixture(scope="module")
def lake():
    path = shutil.which("lake")
    if path is None:
        pytest.skip("lake is not available")
    lean_build("ResponseShape")
    return path


def _check(lake, tmp_path, body: str) -> subprocess.CompletedProcess:
    source = tmp_path / "Mutant.lean"
    source.write_text(HEADER + body)
    return subprocess.run([lake, "env", "lean", str(source)], cwd=LEAN, capture_output=True, text=True,
                          timeout=HANG_TIMEOUT)


# A failure for another reason than the proof (a typo in a mutant) must not count as the proof failing.
NOT_A_PROOF_FAILURE = ("unexpected token", "Unknown identifier", "unknown identifier", "Unknown constant",
                       "unknown constant", "Function expected", "Type mismatch")


def _passes(lake, tmp_path, body: str) -> bool:
    done = _check(lake, tmp_path, body)
    output = done.stdout + done.stderr
    assert not any(marker in output for marker in NOT_A_PROOF_FAILURE), output
    return done.returncode == 0 and "error" not in output


# The soft-norms `soft-certificate` answer (SoftNorms.Run.runSoftKind), as the runner builds it.
CERTIFICATE = '[("valid", .bool v), ("background", toJson b), ("layers", toJson l), ("conditional_on", toJson c)]'


def _certificate(fields: str) -> str:
    return f"""
example (req : Json) (id : String) (v : Bool) (b l : Nat) (c : List String) :
    Fits req (skel% "soft-norms.json#/$defs/certificate") (VE.Route.Wire.ok id {fields}) := by
  simp only [VE.Route.Wire.ok]
  fits
"""


def test_the_genuine_encoder_is_proved(lake, tmp_path):
    assert _passes(lake, tmp_path, _certificate(CERTIFICATE))


@pytest.mark.parametrize("mutant", [
    CERTIFICATE.replace("]", ', ("extra", .bool v)]'),               # a field added
    CERTIFICATE.replace(', ("layers", toJson l)', ""),                # a field dropped
    CERTIFICATE.replace('"layers"', '"layer"'),                       # a field renamed
    CERTIFICATE.replace(']', ', ("valid", .bool v)]'),                # a field written twice
], ids=["field-added", "field-dropped", "field-renamed", "field-twice"])
def test_a_mutated_encoder_fails(lake, tmp_path, mutant):
    assert not _passes(lake, tmp_path, _certificate(mutant))


def _report(claim: str) -> str:
    return f"""
example (req : Json) (n : String) (a : Json) :
    Fits req (skel% "common.json#/$defs/bound_report")
      (Json.mkObj [("root", Json.mkObj {claim}), ("assumptions", Json.arr #[])]) := by
  fits
"""


def test_a_nested_object_is_checked(lake, tmp_path):
    """The report's root claim (Route.Run.claimJson) is closed: name and ast required, label optional."""
    assert _passes(lake, tmp_path, _report('[("name", .str n), ("ast", a)]'))
    assert _passes(lake, tmp_path, _report('[("name", .str n), ("ast", a), ("label", .str n)]'))
    assert not _passes(lake, tmp_path, _report('[("name", .str n)]'))
    assert not _passes(lake, tmp_path, _report('[("name", .str n), ("ast", a), ("note", .str n)]'))


def _packages(verdict: str, detail: bool) -> str:
    fields = (f'[("verdict", .str "{verdict}"), ("status_text", .str t), ("coherent_exhibit", .bool e), '
              '("budget", toJson b), ("targets", toJson ts), ("conditional_on", toJson ts)'
              + (', ("detail", .str t)]' if detail else "]"))
    return f"""
example (id t : String) (e : Bool) (b : Nat) (ts : List String) :
    Fits req (skel% "soft-norms.json#/$defs/packages") (VE.Route.Wire.ok id {fields}) := by
  simp only [VE.Route.Wire.ok]
  fits
"""


def test_a_field_tied_to_a_value_is_checked(lake, tmp_path):
    """packages: `detail` exactly beside UNKNOWN (the if/then/else of the shape)."""
    assert _passes(lake, tmp_path, _packages("UNKNOWN", True))
    assert _passes(lake, tmp_path, _packages("CONFLICT-FREE", False))
    assert not _passes(lake, tmp_path, _packages("UNKNOWN", False))
    assert not _passes(lake, tmp_path, _packages("CONFLICT-FREE", True))


def _shape(required: str, allowed: str) -> str:
    return f"""
def certificateShape : List File :=
  Schemas.files.map fun f => if f.name != "soft-norms.json" then f else
    {{ f with defs := f.defs.map fun (k, d) => if k != "certificate" then (k, d) else
        (k, .schema (n [obj, .required {required}, closed ({allowed}.map (·, .bool true))])) }}

elab "mutant%" : term => do
  match skeleton certificateShape "soft-norms.json#/$defs/certificate" with
  | .ok (k, _) => pure (Lean.toExpr k)
  | .error e => throwError e

example (req : Json) (id : String) (v : Bool) (b l : Nat) (c : List String) :
    Fits req mutant% (VE.Route.Wire.ok id {CERTIFICATE}) := by
  simp only [VE.Route.Wire.ok]
  fits
"""


GENUINE = '["id", "status", "valid", "background", "layers", "conditional_on"]'


def test_a_mutated_shape_fails(lake, tmp_path):
    """The skeleton follows the shape: the same proof fails once the shape lists other fields."""
    assert _passes(lake, tmp_path, _shape(GENUINE, GENUINE))
    with_extra = GENUINE.replace("]", ', "exhibit"]')
    assert not _passes(lake, tmp_path, _shape(with_extra, with_extra))          # required, never written
    without_layers = GENUINE.replace(', "layers"', "")
    assert not _passes(lake, tmp_path, _shape(without_layers, without_layers))  # written, not allowed


def _route_error(valid: bool, certificate: bool) -> str:
    fields = '[("id", .str id), ("status", .str "error"), ("error", .str m)' + (', ("valid", .bool false)]' if valid else "]")
    kind = "certificate" if certificate else "evaluate"
    return f"""
example (req : Json) (id m : String) (h : req.getObjValD "kind" = .str "{kind}") :
    Fits req Skeletons.route (Json.mkObj {fields}) := by
  fits
  all_goals case_cond
"""


def test_a_field_tied_to_the_case_is_checked(lake, tmp_path):
    """route's error row: `valid` exactly beside a certificate case (a condition on the request, `x-case`)."""
    assert _passes(lake, tmp_path, _route_error(valid=True, certificate=True))
    assert _passes(lake, tmp_path, _route_error(valid=False, certificate=False))
    assert not _passes(lake, tmp_path, _route_error(valid=False, certificate=True))
    assert not _passes(lake, tmp_path, _route_error(valid=True, certificate=False))


def _quantity_lower(field: str) -> str:
    return f'''
example (id x : String) :
    Fits (Json.mkObj [("kind", .str "lower")]) Skeletons.quantity
      (VE.Time.Wire.ok id [("{field}", .str x)]) := by
  simp only [VE.Time.Wire.ok]
  fits
  all_goals decide
'''


def test_quantity_select_keeps_the_request_kind(lake, tmp_path):
    """A lower answer must have coordinate; render's amount cannot satisfy the lower selector."""
    assert _passes(lake, tmp_path, _quantity_lower("coordinate"))
    assert not _passes(lake, tmp_path, _quantity_lower("amount"))
    assert not _passes(lake, tmp_path, _quantity_lower("error"))


def _generated_predicate(fields: str) -> str:
    return f'''
example (req : Json) (ss : List String) :
    Fits req (skel% "common.json#/$defs/environment_predicate")
      (Json.mkObj {fields}) := by
  fits
'''


def test_generated_environment_predicate_has_arguments(lake, tmp_path):
    assert _passes(lake, tmp_path, _generated_predicate('[ ("arguments", toJson ss), ("description", .str "generated") ]'))
    assert not _passes(lake, tmp_path, _generated_predicate('[ ("description", .str "generated") ]'))


def _prime_environment(value: str) -> str:
    return f'''
example (req : Json) (D : VE.SoftNorms.SoftDoc) (env : Json) :
    Fits req (skel% "common.json#/$defs/environment") {value} := by
  first
    | (apply Fits.softEnvironment D env
       intro p hp
       unfold VE.SoftNorms.Wire.decisionEntry
       fits
       rfl)
    | skip
'''


def test_environment_field_is_bound_to_the_prime_encoder(lake, tmp_path):
    prime = '((VE.SoftNorms.Wire.primeJson D env).toOption.getD .null)'
    assert _passes(lake, tmp_path, _prime_environment(prime))
    assert not _passes(lake, tmp_path, _prime_environment('(Json.mkObj [])'))


def _assembled_decisions(entry: str) -> str:
    return f'''
def mutantWithDecisions (D : VE.SoftNorms.SoftDoc) (environment : Json) : Except String Json := do
  VE.Norms.Wire.appendPredicates environment
    ((VE.SoftNorms.decisions D).map fun (n, ss) => (n, {entry}))

example (D : VE.SoftNorms.SoftDoc) (env : Json) :
    mutantWithDecisions D env =
      VE.Norms.Wire.appendPredicates env
        ((VE.SoftNorms.decisions D).map fun (n, ss) =>
          (n, VE.SoftNorms.Wire.decisionEntry ss)) := by
  rfl
'''


def test_assembled_environment_uses_the_proved_entries(lake, tmp_path):
    assert _passes(lake, tmp_path, _assembled_decisions('VE.SoftNorms.Wire.decisionEntry ss'))
    assert not _passes(lake, tmp_path, _assembled_decisions('Json.mkObj []'))
