"""tools/trust_mutants.py never settles on a list Lean capped at `maxErrors` (tm-nightly-unknown-disposition-2; the
nightly's M186 and M417: `lean/VE/Presupposition/Examples.lean:0: maximum number of errors (100; from option
`maxErrors`) reached, exiting`, UNKNOWN on every resume). Lean reads the cap from its command line only, so the capped
file is checked again by `lake env lean -DmaxErrors=0` and the verdict is read from the whole list under the same rule
(`settle`: a kill only when every error is a check's own refutation); a whole list that cannot be read stays UNKNOWN
naming maxErrors. Every build here is a stub (`run`'s own build path: Lake's output, `located`, `build`, `whole`,
`settle`); no Lean runs."""
from __future__ import annotations

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import trust_mutants as tm  # noqa: E402

DEFS = "def f (n : Nat) : Nat := n + 1\n"
CHECKS = "import Demo.Defs\n#guard f 1 == 3\n#guard f 2 == 4\n#guard f 3 == 5\n#guard f 4 == 6\n"
ROLES = [(n, n, "check", None) for n in (2, 3, 4, 5)]


def refutation(n: int) -> str:
    return f"Expression\n  f {n - 1} == {n + 1}\ndid not evaluate to `true`"


def lake_line(n: int, message: str) -> str:  # `lake build`'s form (`ERROR`)
    return f"error: Demo/Check.lean:{n}:0: {message}\n"


def lean_line(f: str, n: int, message: str) -> str:  # `lake env lean`'s form (`LEAN_ERROR`)
    return f"{f}:{n}:0: error: {message}\n"


CAP = "maximum number of errors (2; from option `maxErrors`) reached, exiting"
# Lean stopped after two errors: the build's own list holds two refutations and the cap's line
CAPPED_BUILD = (lake_line(2, refutation(2)) + lake_line(3, refutation(3)) + lake_line(0, CAP)
                + "error: Lean exited with code 1\nSome required targets logged failures:\n- Demo.Check\n"
                "error: build failed\n")


def whole_list(*rows: tuple[int, str]) -> str:
    return "".join(lean_line("Demo/Check.lean", n, message) for n, message in rows)


ALL_REFUTE = whole_list(*((n, refutation(n)) for n in (2, 3, 4, 5)))


class Stub:
    """A scratch copy whose Lake answers from the mutated file's text: the mutant's build of Demo.Check is capped,
    its control (the same build without the mutant) passes, and `lake env lean` answers `answers` by argument list."""

    def __init__(self, lean: Path, answers: dict[tuple, tuple[int, str]]):
        self.lean, self.answers, self.calls = lean, answers, []

    def mutated(self) -> bool:
        return (self.lean / "Demo/Defs.lean").read_text() != DEFS

    def lake(self, env, *args, timeout=None):
        self.calls.append(args)
        if args[0] == "build":
            return (1, CAPPED_BUILD) if "+Demo.Check" in args and self.mutated() else (0, "")
        return self.answers[args](self) if callable(self.answers[args]) else self.answers[args]


class NoProbe:  # the check reads the mutated definition (`probe`'s answer is not under test here)
    def __init__(self, probing):
        pass

    def scope(self, keys):
        pass

    def __call__(self, key):
        return None


@pytest.fixture
def setup(tmp_path, monkeypatch):
    lean = tmp_path / "lean"
    (lean / "Demo").mkdir(parents=True)
    (lean / "Demo/Defs.lean").write_text(DEFS)
    (lean / "Demo/Check.lean").write_text(CHECKS)
    start = DEFS.index("n + 1")
    m = tm.Mutant("M186", "Demo/Defs.lean", 1, "f", "lit-plus", start, start + 5, (1, 1), "n + 1", "n + 2",
                  edit=(start + 5, "n + 2"))
    monkeypatch.setattr(tm, "targets", lambda tree, m, tests, deep=False: ["Demo.Defs", "Demo.Check"])
    monkeypatch.setattr(tm, "Probes", NoProbe)
    monkeypatch.setattr(tm, "refusal", lambda entry, control: None)
    tree = tm.Tree({"Demo/Check.lean": ROLES}, {}, {"Demo.Defs": "Demo/Defs.lean", "Demo.Check": "Demo/Check.lean"},
                   {})
    return lean, m, tree


WHOLE_CALL = ("env", "lean", "-DmaxErrors=0", "Demo/Check.lean")
CASES = [
    # the whole list: every error a check's own refutation -> KILLED (the capped list alone gave UNKNOWN at line 0)
    ("whole-all-refute", (1, ALL_REFUTE), "KILLED", "lean/Demo/Check.lean:2: Expression"),
    # past the cap, a check whose message states no refutation -> UNKNOWN there, never KILLED on the first two
    ("whole-one-past-the-cap-refutes-nothing",
     (1, whole_list((2, refutation(2)), (3, refutation(3)), (4, refutation(4)), (5, "unsolved goals\n⊢ False"))),
     "UNKNOWN", "lean/Demo/Check.lean:5: unsolved goals"),
    # the whole list cannot be read: UNKNOWN naming maxErrors
    ("whole-capped-again", (1, whole_list((2, refutation(2))) + ":0:0: error: " + CAP + "\n"), "UNKNOWN",
     "lean/Demo/Check.lean: maxErrors: Lean stopped at its error cap and the whole list could not be read "
     "(capped again)"),
    ("whole-timed-out", (tm.TIMED_OUT, "lake env did not finish in 1800 s (--build-timeout)"), "UNKNOWN",
     "maxErrors: Lean stopped at its error cap and the whole list could not be read (lake env did not finish"),
    ("whole-no-located-error", (1, "error: object file of module Demo.Defs does not exist\n"), "UNKNOWN",
     "the whole list could not be read (no located error)"),
    ("whole-in-another-file", (1, lean_line("Demo/Other.lean", 2, refutation(2))), "UNKNOWN",
     "the whole list could not be read (an error in Demo/Other.lean)"),
]


@pytest.mark.parametrize(("case", "answer", "verdict", "detail"), CASES, ids=[c[0] for c in CASES])
def test_a_list_lean_capped_at_max_errors_is_never_the_one_settled(setup, case, answer, verdict, detail):
    """M186: the build stops at Lean's error cap with two refutations read. The verdict comes from the file's whole
    list, read with the cap lifted, under the existing rule; on the old code every case ended UNKNOWN at the cap's
    line 0 ("maximum number of errors"), whatever the errors past it."""
    lean, m, tree = setup
    scratch = Stub(lean, {WHOLE_CALL: answer})
    status, got = tm.run(m, scratch, tree, [], [], {})
    assert (status, detail in got) == (verdict, True), got
    assert "Demo/Check.lean:0" not in got  # never the cap's own line
    assert WHOLE_CALL in scratch.calls
    assert (lean / "Demo/Defs.lean").read_text() == DEFS  # restored


def test_the_cap_line_in_a_file_the_output_does_not_name_is_unknown():
    """`whole` alone: Lean's cap line with no file (as `lake env lean` prints it) cannot say which list was cut."""
    out = "info: Demo/Check.lean: building\n:0:0: error: " + CAP + "\nerror: build failed\n"
    rows = tm.whole(out, tm.located(out), lambda *a: pytest.fail(f"no file to check again: {a}"))
    assert rows[0][0] == "" and rows[0][3].startswith("maxErrors: ") and len(rows) == 1


def test_an_uncapped_build_is_read_as_before():
    out = lake_line(2, refutation(2))
    assert tm.whole(out, tm.located(out), lambda *a: pytest.fail(f"checked again: {a}")) == tm.located(out)


def test_an_outside_check_is_read_with_the_cap_lifted_and_never_capped(tmp_path, setup, monkeypatch):
    """An outside --test file is checked by `lake env lean`, whose cap line names no file, so `LEAN_ERROR` never
    located it: the capped list was settled as if whole (a kill on the first 100 refutations). Now every such check
    runs with WHOLE, and output still capped is UNKNOWN naming maxErrors."""
    lean, m, tree = setup
    monkeypatch.setattr(tm, "targets", lambda tree, m, tests, deep=False: ["Demo.Defs"])
    outside = tmp_path / "outside" / "O.lean"
    outside.parent.mkdir()
    outside.write_text("import Demo.Defs\n#guard f 1 == 3\n#guard f 2 == 4\n")
    call = ("env", "lean", "-DmaxErrors=0", str(outside))
    passes = Stub(lean, {call: (0, "")})
    assert tm.run(m, passes, tree, [], [outside], {}) == ("SURVIVOR", "")
    assert call in passes.calls and ("env", "lean", str(outside)) not in passes.calls

    capped = lean_line(str(outside), 2, refutation(2)) + ":0:0: error: " + CAP + "\n"
    stub = Stub(lean, {call: lambda s: (1, capped) if s.mutated() else (0, "")})
    status, detail = tm.run(m, stub, tree, [], [outside], {})
    assert (status, "maxErrors" in detail) == ("UNKNOWN", True), detail
