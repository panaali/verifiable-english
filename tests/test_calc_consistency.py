"""ME-8: consistency of printed numbers (math-evidence spec 8.1; fixtures C-1, R-5, V-6, V-7, V-7b, V-8, S-3 and
R-10b's outcomes of 13.2, 13.3 and 13.6).

Lean decides every answer here: one Lean file runs each fixture through `VE.Calc.Consistency` and prints it, and the
tests compare the printed lines with the spec's hand-computed answers; no check is computed in Python. The service
tests show that the wire is unchanged: an existing `ve-calc@0` request answers as before, and a `consistent` claim
is still refused (its wire form is me-8b's).
"""
import json
import shutil
import subprocess

import pytest

from subprocesses import HANG_TIMEOUT
from tests.lean_build import LEAN, lean_build
from ve.backends.lean_service import LeanService

HEADER = """import VE.Calc.ConsistencyExamples
open VE.Calc VE.Calc.ConsistencyExamples VE.Numbers

def q (r : Rat) : String := if r.den = 1 then toString r.num else s!"{r.num}/{r.den}"
def say : Option ConsistencyAnswer → String
  | none => "limit"
  | some (.refused (.input n)) => s!"ConsistencyInput: {n}"
  | some (.refused (.name n)) => s!"ConsistencyName: {n}"
  | some (.holds w) => "holds " ++ ", ".intercalate (w.map fun (n, x) => s!"{n} = {q x}")
  | some (.fails j es) => s!"fails output {j} " ++ ", ".intercalate (es.map fun (l, h) => s!"[{q l}, {q h}]")
  | some .undefined => "undefined"
  | some (.unknown u) => UnknownReason.text 6 u
def line (key value : String) : IO Unit := IO.println (key ++ "\\t" ++ value)
"""

V6_PRINTED = "d0 = -1/10, d1 = -133/1000, d2 = 47/500, d3 = -24/125, d4 = 21/1000, d5 = 43/500, d6 = -57/1000, " \
             "d7 = 0, d8 = 61/1000, d9 = -1/20, d10 = -123/500, d11 = -29/1000"

INCONCLUSIVE = "unknown: neither a witness nor an enclosure decides it"

FIXTURES = [
    # R-5 (C-1's k1 and k2): k1 refuted by its enclosure [13/20, 3/4]; k2 witnessed at a's lower endpoint 7/20.
    ("r5-k1", "say (run C1 inA [k1])", "fails output 0 [13/20, 3/4]"),
    ("r5-k2", "say (run C1 inA [k2])", "holds a = 7/20"),
    ("r5-k2-printed-point", "toString (witnessCheck .tiesUp inA [lt (.add a (.lit (3 / 10))) (.lit (66 / 100))] "
                            "[(\"a\", 2 / 5)])", "false"),
    ("r5-order", "say (run C1 inA [k2, k1])", "fails output 1 [13/20, 3/4]"),
    # C-1's k3 and the name rule through a definition; the inputs' rule.
    ("c1-k3", "say (run C1 inA [lt (.add a (.val \"f\")) (.lit 1)])", "ConsistencyName: f"),
    ("c1-through-definition", "say (run C1 inA [lt (.val \"g\") (.lit 1)])", "ConsistencyName: f"),
    ("input-free", "say (run C1 [(\"f\", ⟨4, 1⟩)] [k2])", "ConsistencyInput: f"),
    ("input-twice", "say (run C1 [(\"a\", ⟨4, 1⟩), (\"a\", ⟨4, 1⟩)] [k2])", "ConsistencyInput: a"),
    ("complement", "say (run C1 inA [ge (.sub (.lit 1) a) (.lit (56 / 100))])", "holds a = 2/5"),
    # R-10b's two outcomes, read from counted values: a budget that ran out, and a value that has none.
    ("r10b-unknown", "say (run C1 inA [lt a (.val \"n\")])", "unknown: the budget of 6 evaluation steps ran out"),
    ("r10b-undefined", "say (run C1 inA [lt a (.val \"m\")])", "undefined"),
    ("inconclusive", "say (run C1 inA [.compare ⟨.eq, false⟩ a (.lit (41 / 100))])",
     INCONCLUSIVE),
    ("witness-points", "say (run D12 twelve [.compare ⟨.eq, false⟩ (.val \"d0\") (.lit (41 / 100))])",
     "unknown: the consistency search tried its 4,096 candidate points"),
    # V-6: the printed per-template values are the witness of the three printed roots.
    ("v6", "say (run V6 V6in V6outs)", f"holds {V6_PRINTED}"),
    # The limit: none at 0 units; C-1's 8,191-node chain ends at its work, one unit short is refused.
    ("limit-zero", "say (consistencyRun 0 C1 .tiesUp inA [k2])", "limit"),
    ("chain-at-work", "say (consistencyRun 8716291 (chain 12) .tiesUp inA [lt (.val \"a12\") (.lit 2000)])",
     "holds a = 2/5"),
    ("chain-short", "say (consistencyRun 8716290 (chain 12) .tiesUp inA [lt (.val \"a12\") (.lit 2000)])", "limit"),
    ("search-short", "say (consistencyRun 1000000 Dhundred .tiesUp hundred [d0IsNot])", "limit"),
    ("search-at-max-work", "say (run Dhundred hundred [d0IsNot])",
     "unknown: the consistency search tried its 4,096 candidate points"),
    # The review's two chains at the runner's limit: answered without walking 2^41 and 2^24 nodes.
    ("add-chain-max-work", "say (run (chain 40) inA [lt (.val \"a40\") (.lit 1)])", INCONCLUSIVE),
    ("mul-chain-max-work", "say (run (squares 23) inA [lt (.val \"a23\") (.lit 1)])", INCONCLUSIVE),
    # The node limit holds the outputs together, after a refusal or a fault, before either phase.
    ("nodes-at-limit", "say (run C1 inA [atCap])", "holds a = 2/5"),
    ("nodes-past-limit", "say (run C1 inA [pastCap])", INCONCLUSIVE),
    ("nodes-together", "say (run (chain 12) inA [lt (.val \"a12\") (.lit 2000), lt (.val \"a12\") (.lit 2000)])",
     INCONCLUSIVE),
    ("nodes-before-refutation", "say (run C1 inA [k1, pastCap])", INCONCLUSIVE),
    ("nodes-after-fault", "say (run C1 inA [pastCap, lt a (.val \"m\")])", "undefined"),
    ("nodes-after-refusal", "say (run C1 inA [pastCap, lt a (.val \"f\")])", "ConsistencyName: f"),
    # The digit hold, on each side of the limit: an enclosure past it is none, and its points still decide.
    ("hold-a11-refutes", "toString ((run (squares 11) inA [lt (.val \"a11\") (.lit 0)]).map (·matches .fails ..))",
     "(some true)"),
    ("hold-a12-no-enclosure", "say (run (squares 12) inA [lt (.val \"a12\") (.lit 0)])", INCONCLUSIVE),
    ("hold-a12-witness", "say (run (squares 12) inA [lt (.val \"a12\") (.lit 1)])", "holds a = 2/5"),
    ("hold-at-limit", "toString (noEnclosure big)", "false"),
    ("hold-either-endpoint", "toString [edge (10 ^ 4096 / 2), edge (-(10 ^ 4096 / 2)), edge (10 ^ 4096 / 2 - 1), "
                             "edge (-(10 ^ 4096 / 2 - 1))]", "[true, true, false, false]"),
    ("hold-past-limit", "toString ([Expr.lit (10 ^ 4096), .add big (.lit 1), .mul e2048 e2048, "
                        ".div e2048 (.lit (1 / 10 ^ 2048)), .pow e2048 2].map noEnclosure)",
     "[true, true, true, true, true]"),
    # V-7 and V-8 (1/512, ties up, then half to even) and V-7b (1/4,096, both rules).
    ("v7-ties-up", "toString (V7.map (grainRefutes 512 .tiesUp))",
     "[false, false, false, true, false, false, false, false]"),
    ("v7-half-even", "toString (V7.map (grainRefutes 512 .halfEven))",
     "[false, false, false, false, false, false, false, false]"),
    ("v7b", "toString (V7b.map fun p => (grainRefutes 4096 .tiesUp p, grainRefutes 4096 .halfEven p))",
     "[(false, false), (false, false), (false, false), (false, false), (false, false), (false, false)]"),
    # S-3 (GRIM): five integers, means printed 3.47, 3.40 and 3.4.
    ("s3", "toString [grainRefutes 5 .tiesUp ⟨347, 2⟩, grainRefutes 5 .tiesUp ⟨340, 2⟩, grainRefutes 5 .tiesUp ⟨34, 1⟩]",
     "[true, false, false]"),
]


@pytest.fixture(scope="module")
def lean(tmp_path_factory):
    lake = shutil.which("lake")
    if lake is None:
        pytest.skip("lake is not available")
    lean_build("VE")
    path = tmp_path_factory.mktemp("consistency") / "Consistency.lean"
    path.write_text(HEADER + "".join(f"#eval line {json.dumps(key)} ({expression})\n"
                                     for key, expression, _ in FIXTURES))
    done = subprocess.run([lake, "env", "lean", str(path)], cwd=LEAN, capture_output=True, text=True,
                          timeout=HANG_TIMEOUT)
    assert done.returncode == 0, done.stdout + done.stderr
    return dict(row.split("\t", 1) for row in done.stdout.splitlines())


@pytest.mark.parametrize("key, expected", [pytest.param(key, expected, id=key) for key, _, expected in FIXTURES])
def test_fixture(lean, key, expected):
    assert lean[key] == expected


def test_every_fixture_printed_once(lean):
    assert sorted(lean) == sorted(key for key, _, _ in FIXTURES)


SHARES = [{"name": "a", "words": "the first printed share", "stated": "0.4"},
          {"name": "b", "words": "the second printed share", "stated": "0.3"}]
SUM = ["add", ["val", "a"], ["val", "b"]]
# The answer main gives to this request (recorded at the merge base; ME-8 changes no wire, runner or display).
BEFORE = {"meaning_id": "f1f730335c0b4b9573161023f170f32b81d673dc8155b6c0ba4ef700bf57a328", "status": "ok", "rows": [
    {"claim": "c1", "claim_id": "fb4b1f661a73acf057df1adbc0a968cdc4b8629ad6cf3e4bc5cccdb58b070f40", "display": "0.700",
     "finding": None, "kind": "claim", "outcome": "holds", "reason": None, "reproduction": None, "sides": ["7/10"],
     "status": "ok", "tie": False,
     "line": "The sum of the first printed share and the second printed share is 0.7 when rounded to one decimal "
             "place, with exact ties going up."}]}


@pytest.fixture(scope="module")
def service():
    with LeanService(lean_build("ve_service") / "ve_service", timeout=HANG_TIMEOUT) as running:
        yield running


def answer(service, claim: list) -> dict:
    case = {"format": "ve-calc@0", "values": SHARES, "claims": [{"id": "c1", "claim": claim}]}
    _, response = service.exchange("calc", json.dumps([case]), 1, timeout=HANG_TIMEOUT)
    return response["results"][0]["result"]


def test_an_existing_request_answers_as_before(service):
    assert answer(service, ["rounds", SUM, "0.7"]) == BEFORE


def test_a_consistency_claim_is_not_on_the_wire_yet(service):
    assert answer(service, ["consistent", ["a"], [["rounds", SUM, "0.9"]]]) == {
        "status": "error", "error": "InvalidInput: claims.0.claim must be a claim"}
