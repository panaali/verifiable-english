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
example (id : String) (v : Bool) (b l : Nat) (c : List String) :
    Fits Γ (skel% "soft-norms.json#/$defs/certificate") (VE.Route.Wire.ok id {fields}) := by
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
])
def test_a_mutated_encoder_fails(lake, tmp_path, mutant):
    assert not _passes(lake, tmp_path, _certificate(mutant))


def _report(claim: str) -> str:
    return f"""
example (n : String) (a : Json) :
    Fits Γ (skel% "common.json#/$defs/bound_report")
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
    Fits Γ (skel% "soft-norms.json#/$defs/packages") (VE.Route.Wire.ok id {fields}) := by
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

example (id : String) (v : Bool) (b l : Nat) (c : List String) :
    Fits Γ mutant% (VE.Route.Wire.ok id {CERTIFICATE}) := by
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
