"""df-5 loop recheck F1: the zone wire's tied definitions are bound to the request's values, not only to its types.

DELTA T1 leaves the request decoders of `lean/VE/Defaults/ZoneWire.lean` (and `ZoneReplay.min`, `zoneSizes` and the
rows' selectors) out of the trusted count because a theorem ties each of them. The recheck showed the ties bound only
membership and type: `recordEntry` with its recorded Bool flipped kept `recordEntry_sound`'s statement and proof.
Each mutant below changes one tied definition's value and nothing else; planted alone in a copy of the file under
`tmp_path` and elaborated with `lake env lean` (nothing imports the copy), it must elaborate as a definition and break
the named theorem's proof, and only that theorem's. The copy unchanged must elaborate with no error, so a failure is
the mutant's. The words tables' text is not a theorem's (as `VE.Calc.Run.words`): `tests/test_defaults_zone.py` reads
it against spec 4.
"""
import re
import shutil
import subprocess

import pytest

from subprocesses import HANG_TIMEOUT
from tests.lean_build import LEAN, lean_build

SOURCE = LEAN / "VE/Defaults/ZoneWire.lean"

# (id, tied definition, the theorems that may break (at least one must, and no other), find, replace)
MUTANTS = [
    ("recordEntry-value", "recordEntry", "recordEntry_sound",
     '  pure ((n, ← tupleIn M ss e), ← (← e.getObjVal? "value").getBool?)',
     '  pure ((n, ← tupleIn M ss e), !(← (← e.getObjVal? "value").getBool?))'),
    ("obsEntry-value", "obsEntry", "obsEntry_sound",
     '  pure ((r, ← tupleIn M (VE.NormDefaults.sortsOf L.U.D r.name) e), ← (← e.getObjVal? "value").getBool?)',
     '  pure ((r, ← tupleIn M (VE.NormDefaults.sortsOf L.U.D r.name) e), !(← (← e.getObjVal? "value").getBool?))'),
    ("decisionOf-key", "decisionOf", "decisionOf_key",
     '.outweighs <$> s "outweighs" <*> s "lower" <*> s "higher"',
     '.outweighs <$> s "outweighs" <*> s "higher" <*> s "lower"'),
    ("decisionOf-lookup", "decisionOf", "decisionOf_mem",
     "match (keyedDecisions L.D).find? (·.1 == k) with",
     "match (keyedDecisions L.D).find? (fun _ => true) with"),
    ("outcomeOf-name", "outcomeOf", "outcomeOf_mem",
     "match L.U.D.T.regulated.find? (·.name == n) with",
     "match L.U.D.T.regulated.find? (fun _ => true) with"),
    ("tupleIn-order", "tupleIn", "tupleIn_typed",
     "(·.val) <$> VE.NormDefaults.Wire.tupleOf",
     "(·.val.reverse) <$> VE.NormDefaults.Wire.tupleOf"),
    ("replayZoneOn-order", "replayZoneOn", "replayZoneOn_sound",
     "← obsJ.toList.mapM (obsEntry v.L S.M)",
     "← obsJ.toList.reverse.mapM (obsEntry v.L S.M)"),
    ("replayZoneOn-sibling", "replayZoneOn", "replayZoneOn_sound",
     'let recordJ ← (← j.getObjVal? "record").getArr?',
     'let recordJ ← (← j.getObjVal? "observations").getArr?'),
    ("min-early", "ZoneReplay.min", "ZoneReplay.min_early",
     "  | some z => .error z",
     '  | some _ => .error (.unknown (.branch [] "size"))'),
    ("zoneSizes-reason", "zoneSizes", "zoneSizes_observations",
     'if maxZoneObservations < obs then some (.unknown (.branch [] "observations size")) else none',
     'if maxZoneObservations < obs then some (.unknown (.branch [] "size")) else none'),
    ("zoneSizes-bound", "zoneSizes", "zoneSizes_none_iff zoneSizes_observations",
     "if maxZoneObservations < obs then",
     "if maxZoneObservations + 1 < obs then"),
    ("row-label", "ZoneLine.row", "zoneLine_rows_distinct",
     '| .stated .. => "DE11" | .forced .. => "DE10f"',
     '| .stated .. => "DE10f" | .forced .. => "DE10f"'),
    ("kind-label", "ZoneLine.kind", "zoneLine_rows_distinct",
     '| .assumed (.off ..) _ => "off"',
     '| .assumed (.off ..) _ => "excepted"'),
]

TOP = re.compile(r"^(/--|/-!|theorem |def |structure |inductive |namespace |end |open )")
ERROR = re.compile(r":(\d+):\d+: error")


def theorem_lines(text: str, name: str) -> range:
    """The source lines (1-based) of `theorem <name>`, from its doc comment (where Lean reports a failed `rfl`) up to
    the next top-level command or doc comment."""
    lines = text.splitlines()
    start = [i for i, line in enumerate(lines, 1) if re.match(rf"theorem {re.escape(name)}\b", line)]
    assert len(start) == 1, (name, start)
    end = next((i for i, line in enumerate(lines, 1) if i > start[0] and TOP.match(line)), len(lines) + 1)
    first = start[0]
    if lines[first - 2].rstrip().endswith("-/"):
        first = next(i for i in range(first - 1, 0, -1) if lines[i - 1].startswith("/--"))
    return range(first, end)


def plant(text: str, find: str, replace: str) -> str:
    assert text.count(find) == 1, find
    return text.replace(find, replace)


def error_lines(output: str) -> list[int]:
    return [int(m.group(1)) for m in ERROR.finditer(output)]


def test_each_mutant_plants_once_and_names_a_theorem_of_the_file():
    text = SOURCE.read_text()
    tied = {"decisionOf", "outcomeOf", "tupleIn", "recordEntry", "obsEntry", "replayZoneOn", "ZoneReplay.min",
            "zoneSizes", "ZoneLine.row", "ZoneLine.kind"}
    assert {m[1] for m in MUTANTS} == tied
    for _, _, theorems, find, replace in MUTANTS:
        assert plant(text, find, replace) != text
        assert all(len(theorem_lines(text, theorem)) > 1 for theorem in theorems.split())


def test_error_lines_and_theorem_lines_read_lean_s_positions():
    assert error_lines("x.lean:12:4: error: a\nx.lean:3:0: warning: b\ny.lean:40:2: error(lean.x): c") == [12, 40]
    text = "def a := 1\n\ntheorem t : a = 1 := by\n  rfl\n\n/-- d\n  e -/\ntheorem u : True := trivial\n"
    assert theorem_lines(text, "t") == range(3, 6)
    assert theorem_lines(text, "u") == range(6, 9)


@pytest.fixture(scope="module")
def lake():
    found = shutil.which("lake")
    if found is None:
        pytest.skip("lake is not available")
    lean_build("VE")
    return found


def elaborate(lake, path):
    run = subprocess.run([lake, "env", "lean", str(path)], cwd=LEAN, capture_output=True, text=True,
                         timeout=HANG_TIMEOUT)
    return run.returncode, run.stdout + run.stderr


def test_the_unmutated_copy_elaborates(lake, tmp_path):
    copy = tmp_path / "ZoneWire.lean"
    copy.write_text(SOURCE.read_text())
    code, output = elaborate(lake, copy)
    assert code == 0 and not error_lines(output), output


@pytest.mark.parametrize("mutant", MUTANTS, ids=[m[0] for m in MUTANTS])
def test_review_f1_each_value_mutant_breaks_its_tied_theorem(lake, tmp_path, mutant):
    _, _, theorems, find, replace = mutant
    text = plant(SOURCE.read_text(), find, replace)
    copy = tmp_path / "ZoneWire.lean"
    copy.write_text(text)
    code, output = elaborate(lake, copy)
    lines = error_lines(output)
    assert code != 0 and lines, output
    inside = [theorem_lines(text, theorem) for theorem in theorems.split()]
    assert all(any(line in r for r in inside) for line in lines), (theorems, inside, output)
