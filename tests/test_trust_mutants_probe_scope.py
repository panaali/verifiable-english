"""tools/trust_mutants.py's scoped probe (eff-tm-probe-scope, design reviews/eff-tm-probe-scope-design-20261031.md
section 8): a mutant's probe walks only the checks `settle` reads (`TM_TRUST_ONLY`) and drops the text after the last
of them (`kept`), an entry is whole only with its walk's `done`, a check of the set with no whole entry is read from
the whole file's probe, and `reading` refuses a key `settle` did not hand over. The seeds (real Lean, five modes:
off, on, dual, a cut one line early and the wrong design that leaves the other checks as written) must give the
whole-file probe's verdicts, and the two negative controls must show they can tell."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys

import pytest

from subprocesses import HANG_TIMEOUT
from test_trust_mutants import DECIDE_FALSE, PATH, REFUTE, ROOT, dump, git, scaffold

sys.path.insert(0, str(ROOT / "tools"))
import lake_outputs  # noqa: E402
import trust_mutants as tm  # noqa: E402


def whole(*flags: str, **consts: str) -> dict:
    return {"flags": {"hash 1", *flags, "done"}, "consts": consts}


# --- `Probes`: the keys `settle` hands over, the fallback --------------------------------------------------------


class Probing:
    """A fake `probing(file, only)`: `scoped` is what the scoped run gives, `full` the whole file's; it records the
    calls."""

    def __init__(self, scoped: dict, full: dict, probeable: set):
        self.scoped, self.full, self.probeable, self.calls = scoped, full, probeable, []

    def __call__(self, f: str, only):
        self.calls.append((f, None if only is None else set(only)))
        return (self.full if only is None else self.scoped), self.probeable


def test_reading_refuses_a_key_settle_did_not_hand_over():
    """Review 2 (F5): `settle` hands its keys to the probe before its first `reads`; any other key raises, before a
    probe runs."""
    probing = Probing({(1, 1): whole(), (2, 2): whole()}, {}, {(1, 1), (2, 2)})
    probes = tm.Probes(probing)
    with pytest.raises(LookupError):
        probes(("A.lean", (1, 1)))
    probes.scope({("A.lean", (1, 1))})
    for key in (("A.lean", (2, 2)), ("B.lean", (1, 1))):
        with pytest.raises(LookupError):
            probes(key)
    assert probing.calls == []
    assert probes(("A.lean", (1, 1))) == whole() and probing.calls == [("A.lean", {(1, 1)})]
    assert probes(("A.lean", (1, 1))) == whole() and len(probing.calls) == 1  # one probe per file
    probes.scope({("A.lean", (1, 1)), ("A.lean", (2, 2))})  # a file probed for fewer checks is probed again
    probes(("A.lean", (2, 2)))
    assert probing.calls[-1] == ("A.lean", {(1, 1), (2, 2)})


def test_settle_hands_its_keys_over_before_its_first_read():
    """`settle` calls `scope` once, with the key of every error it judged, before `reads`; a `reads` that refuses
    every other key (`run`'s `reading`) then settles as before. Without `scope` it raises."""
    text = "#guard f 1 == 2\n#guard f 2 == 3\nexample : f 3 = 5 := by decide\n"
    roles = {"A.lean": [(1, 1, "check", None), (2, 2, "check", None), (3, 3, "check", None)]}
    events: list = []
    probes = tm.Probes(lambda f, only: ({s: whole() for s in only}, {(1, 1), (2, 2), (3, 3)}))

    def scope(keys):
        events.append(("scope", set(keys)))
        probes.scope(keys)

    def reads(key):
        events.append(("reads", key))
        return tm.refusal(probes(key), whole())
    errors = [("A.lean", 1, REFUTE), ("A.lean", 3, DECIDE_FALSE)]
    got = tm.settle(errors, lambda f: text, lambda f: text, roles, None, reads, scope=scope)
    assert got[0] == "KILLED"
    assert events[0] == ("scope", {("A.lean", (1, 1)), ("A.lean", (3, 3))}) and len(events) == 3
    assert {e[1] for e in events[1:]} == {("A.lean", (1, 1)), ("A.lean", (3, 3))}
    with pytest.raises(LookupError):
        tm.settle(errors, lambda f: text, lambda f: text, roles, None,
                  lambda key: tm.refusal(tm.Probes(lambda f, only: ({}, set()))(key), whole()))


@pytest.mark.parametrize(("scoped", "probeable", "fallback"), [
    ({(1, 1): whole(), (5, 5): whole()}, {(1, 1), (5, 5)}, False),  # every entry whole
    ({(1, 1): whole(), (5, 5): {"flags": {"hash 1"}, "consts": {}}}, {(1, 1), (5, 5)}, True),  # a walk cut short
    ({(1, 1): whole()}, {(1, 1), (5, 5)}, True),  # a check of the set absent (a cut that changed a parse: F3)
    ({}, {(1, 1), (5, 5)}, True),  # the scoped run timed out or crashed (F4): no entry at all
    ({(1, 1): whole()}, {(1, 1)}, False),  # a check `named` cannot probe is absent in both (F7)
])
def test_a_check_of_the_set_with_no_whole_entry_is_read_from_the_whole_file(scoped, probeable, fallback):
    """Design 2.5, F3, F4: the fallback fires when a check of the set `named` can probe has no entry with `done` in
    the scoped probe, and then every entry read is the whole file's."""
    full = {(1, 1): whole("sorry"), (5, 5): whole("io"), (9, 9): whole()}
    probing = Probing(scoped, full, probeable)
    probes = tm.Probes(probing)
    probes.scope({("A.lean", (1, 1)), ("A.lean", (5, 5))})
    got = probes(("A.lean", (1, 1)))
    assert [only for _, only in probing.calls] == ([{(1, 1), (5, 5)}, None] if fallback else [{(1, 1), (5, 5)}])
    assert got == (full if fallback else scoped)[(1, 1)]


def test_an_entry_without_its_done_marker_is_absent():
    """Review 1: a walk Lean stopped midway leaves `hash` and some `const` lines but no `sorry`; without `done` the
    entry, the mutant's or the control's, reads as absent, never as no reason (a kill)."""
    cut = {"flags": {"hash 1"}, "consts": {"Demo.f": "3"}}
    assert tm.refusal(whole(**{"Demo.f": "3"}), whole(**{"Demo.f": "3"})) is None
    assert tm.complete(whole()) and not tm.complete(cut) and not tm.complete(None)
    for entry, control in ((cut, whole(**{"Demo.f": "3"})), (whole(**{"Demo.f": "3"}), cut), (None, whole())):
        assert tm.refusal(entry, control) == "Lean could not elaborate it in the probe"


# --- `probe(only=...)` and `kept`, without Lean ------------------------------------------------------------------


PROBED = ("import Demo.Defs\n#guard f 1 == 2\ndef g := 1\n#guard f 2 == 3\n\n#guard f 3 == 4\n"
          "example : f 4 = 5 := by decide\n")
PROBED_ROLES = [(2, 2, "check", None), (3, 3, "other", None), (4, 5, "check", None), (6, 6, "check", None),
                (7, 7, "check", None)]


class FakeLake:
    """`probe`'s `lake`: records the env and the text written to the probe's path, and prints each named check's
    entry (`done` included but for the names in `cut`) under the call's nonce."""

    def __init__(self, path: Path, cut: tuple = ()):
        self.path, self.cut, self.calls = path, cut, []

    def __call__(self, env: dict, *args: str):
        text = self.path.read_text()
        self.calls.append((env.get("TM_TRUST_ONLY"), text))
        only = env.get("TM_TRUST_ONLY")
        names = [n for n in re.findall(r"tmChk_\d+", text) if only is None or n in only.split(" ")]
        nonce = env["TM_TRUST_NONCE"]
        said = [f"{nonce} {n} {x}" for n in names for x in ("hash 7", "const Demo.f 11", "done") if
                not (x == "done" and n in self.cut)]
        return 0, "\n".join(["noise", *said, f"{nonce[:-1]}x tmChk_2 sorry"])


def test_probe_walks_only_its_checks_and_drops_the_text_after_them(tmp_path):
    """`only`: the same rewritten text, every check named, cut before the command after the set's last check, and
    `TM_TRUST_ONLY` naming the set's checks; the controls' probe (`only` None) is the whole file, every check walked.
    A set with no check `named` can probe runs no Lean (the whole file's probe has no entry for it either)."""
    path = tmp_path / "A.lean"
    lake = FakeLake(path)
    full = tm.probe(lake, {}, PROBED, PROBED_ROLES, path)
    assert lake.calls[0][0] is None and lake.calls[0][1].count("\n") == PROBED.count("\n")
    assert set(full) == {(2, 2), (4, 5), (6, 6), (7, 7)} and not path.exists()
    assert full[(2, 2)] == {"flags": {"hash 7", "done"}, "consts": {"Demo.f": "11"}}
    scoped = tm.probe(lake, {}, PROBED, PROBED_ROLES, path, only={(2, 2), (4, 5)})
    only, text = lake.calls[1]
    assert only == "tmChk_2 tmChk_4" and set(scoped) == {(2, 2), (4, 5)}
    assert text.split("\n") == lake.calls[0][1].split("\n")[:5]  # lines 1-5: up to the command after (4, 5)
    assert "#tm_trust_guard tmChk_6" not in text and text.startswith("import TmTrustProbe import Demo.Defs")
    assert scoped == {s: full[s] for s in scoped}
    assert tm.probe(lake, {}, PROBED, PROBED_ROLES, path, only={(3, 3)}) == {} and len(lake.calls) == 2
    tm.probe(lake, {}, PROBED, PROBED_ROLES, path, only={(7, 7)})  # the last command: every line kept
    assert lake.calls[2][1] == lake.calls[0][1] and lake.calls[2][0] == "tmChk_7"


def test_probe_keeps_an_entry_whose_walk_did_not_finish_without_done(tmp_path):
    path = tmp_path / "A.lean"
    got = tm.probe(FakeLake(path, cut=("tmChk_4",)), {}, PROBED, PROBED_ROLES, path, only={(2, 2), (4, 5)})
    assert tm.complete(got[(2, 2)]) and not tm.complete(got[(4, 5)])


# F3's shapes (review 5): a `mutual … end` holding a `decide` theorem, `where` and `termination_by` tails, a docstring
# before the next command, `set_option … in`, an attribute on its own line and a multi-line `#guard`.
F3 = """import Demo.Defs
open Demo

mutual
theorem m1 : small 1 = true := by decide
theorem m2 : small 2 = true := by decide
end

def f (n : Nat) : Nat := g n
where
  g (m : Nat) : Nat := m + 1
#guard f 1 == 2
def h : Nat → Nat
  | 0 => 0
  | n + 1 => h n
termination_by n => n
#guard h 3 == 0

/-- a docstring before the next command -/
example : small 0 = true := by decide

set_option maxRecDepth 1000 in
#guard (f 2 ==
  3)
@[simp]
theorem s : f 0 = 1 := rfl
#guard_msgs in
#guard !small 5
"""
F3_THEOREMS = ("theorem m1", "theorem m2", "theorem s")


def f3_roles(path: Path) -> list[tuple]:
    """`file_roles` of F3, its theorems checks (as lean/'s recorded ones are)."""
    lines = F3.split("\n")
    return [(s, e, "check" if any(lines[n].startswith(F3_THEOREMS) for n in range(s - 1, e)) else role, x)
            for s, e, role, x in tm.file_roles(path)]


def f3_line(text: str) -> int:
    return next(n for n, line in enumerate(F3.split("\n"), 1) if line.startswith(text))


@pytest.mark.parametrize(("check", "keeps"), [
    ("theorem m1", "theorem m1"),  # inside `mutual`: cut before m2, the block left open
    ("theorem m2", ""),  # the last of the block: its `end` and the blank line after it kept
    ("#guard f 1 == 2", "#guard f 1 == 2"),  # after a `where` tail, kept whole
    ("#guard h 3 == 0", "/-- a docstring"),  # trust_map's span takes the next command's docstring: left dangling
    ("example : small 0", ""),  # its blank line kept, cut before `set_option … in`
    ("set_option", "  3)"),  # the multi-line `#guard` under `set_option … in`, whole
    ("@[simp]", "theorem s"),  # the attribute on its own line is the theorem's span
    ("#guard_msgs in", ""),  # the last command: every line kept, to the file's last newline
])
def test_kept_cuts_at_the_line_before_the_next_command(tmp_path, check, keeps):
    """F3: `kept` keeps every line up to the one before the first command that starts after the set's last check;
    what the cut leaves at the end is the check's own span (a trailing docstring or blank line included)."""
    path = tmp_path / "F3.lean"
    path.write_text(F3)
    roles = f3_roles(path)
    span = next((s, e) for s, e, *_ in roles if s == f3_line(check))
    lines = F3.split("\n")
    after = next((s for s, *_ in roles if s > span[1]), len(lines) + 1)
    got = tm.kept(lines, roles, span[1])
    assert got == lines[:after - 1] and len(got) >= span[1]
    assert got[-1].startswith(keeps) if keeps else got[-1] == ""


def lake_in(lean: Path):
    def lake(env: dict, *args: str) -> tuple[int, str]:
        done = subprocess.run([lake_outputs.lean_executable(None, "lake"), *args], cwd=lean, env=env,
                              capture_output=True, text=True, timeout=HANG_TIMEOUT)
        return done.returncode, done.stdout + done.stderr
    return lake


@pytest.fixture(scope="module")
def f3_package(tmp_path_factory) -> Path:
    root = tmp_path_factory.mktemp("f3")
    scaffold(root, ".")
    (root / "lean/Demo/Defs.lean").write_text("namespace Demo\n\ndef small (n : Nat) : Bool := n < 3\n\nend Demo\n")
    (root / "lean/Demo/F3.lean").write_text(F3)
    env = {**os.environ, **PATH}
    assert lake_in(root / "lean")(env, "build", "Demo.F3")[0] == 0
    assert tm.install(lambda *a: lake_in(root / "lean")(env, *a), root / "lean")
    return root


def test_a_cut_that_changes_a_parse_fails_closed_in_lean(f3_package, monkeypatch):
    """F3 in Lean: each check of F3 probed alone gives the whole file's entry, or none (then `Probes` reads the
    whole file's): never another whole entry. A cut one line early (the negative control) changes some entries,
    and each of those is absent or refused (`refusal`), never a kill."""
    lean, env = f3_package / "lean", {**os.environ, **PATH}
    path, lake = lean / "Demo/F3.lean", lake_in(lean)
    roles = f3_roles(path)
    full = tm.probe(lake, env, F3, roles, path)
    spans = sorted(full)
    assert len(spans) == 8 and all(tm.complete(full[s]) for s in spans), full
    absent = []
    for span in spans:
        got = tm.probe(lake, env, F3, roles, path, only={span})
        assert set(got) <= {span}
        if tm.complete(got.get(span)):
            assert got[span] == full[span], span
        else:
            absent.append(span)
    assert path.read_text() == F3
    # Lean elaborates the `mutual` block a cut leaves open too (4.x); were it absent, `Probes` would fall back
    assert set(absent) <= {(f3_line("theorem m1"), f3_line("theorem m1"))}, absent
    early = tm.kept
    monkeypatch.setattr(tm, "kept", lambda lines, roles, last: early(lines, roles, last)[:-1])
    changed = 0
    for span in spans:
        got = tm.probe(lake, env, F3, roles, path, only={span})
        if got.get(span) != full[span]:
            changed += 1
            assert tm.refusal(got.get(span), full[span]) is not None, (span, got)
    assert changed, "a cut one line early changed no entry"


# --- `READS`: the gate first, `done` last, no effects ------------------------------------------------------------


GATE = ['  if let some only ← IO.getEnv "TM_TRUST_ONLY" then',
        '    if !((only.splitOn " ").contains k.toString) then return']
EFFECTS = re.compile(r"\b(?:modifyEnv|setEnv|addDecl|addAndCompile|compileDecl|setOption|withOptions|modifyScope|"
                     r"IO\.mkRef|ST\.mkRef|mkRef|initialize|builtin_initialize|pushInfoLeaf|pushInfoTree|logInfo|"
                     r"logWarning|logError|addInstance|setReducibilityStatus|modifyThe|set)\b")


def walk_faults(reads: str) -> list[str]:
    """What breaks design 3(b) in the walk of `reads` (the `READS` text): the `TM_TRUST_ONLY` gate not its first
    statement, `done` not its last line, a statement with an effect a later command could read (F6), or a theorem's
    value in a `const` line (its proof term, which a skipped walk's budget can change: 3b)."""
    lines = reads.split("\n")
    head = lines.index("def tmTrustWalk (k : Name) (roots : List Expr) : MetaM Unit := do")
    end = next(i for i in range(head + 1, len(lines)) if lines[i] and not lines[i].startswith(" "))
    body = [line for line in lines[head + 1:end] if line.strip() and not line.strip().startswith("--")]
    faults = []
    if body[:2] != GATE:
        faults.append("the gate is not the walk's first statement")
    if body[-1] != '  say "done"':
        faults.append("`done` is not the walk's last line")
    if hits := sorted({m for line in body for m in EFFECTS.findall(line)}):
        faults.append(f"effects: {hits}")
    if [line for line in body if "IO.println" in line] != [
            '  let say (s : String) : IO Unit := do IO.println s!"{(← IO.getEnv "TM_TRUST_NONCE").getD ""} {k} {s}"']:
        faults.append("it prints other than through `say`")
    const = [line for line in body if 'say s!"const ' in line]
    if len(const) != 1 or not const[0].strip().startswith("if !(info matches .thmInfo _) && "):
        faults.append("a theorem's value can reach a `const` line")
    return faults


@pytest.mark.parametrize(("edit", "fault"), [
    (None, None),
    (lambda r: r.replace("\n".join(GATE) + "\n  let env ← getEnv\n", "  let env ← getEnv\n" + "\n".join(GATE) + "\n"),
     "first statement"),
    (lambda r: r.replace('  say "done"\n', ""), "`done`"),
    (lambda r: r.replace('  say "done"\n', '  say "done"\n  modifyEnv id\n'), "`done`"),
    (lambda r: r.replace("  let mut seen", "  modifyEnv id\n  let mut seen"), "modifyEnv"),
    (lambda r: r.replace("  let mut seen", "  let r ← IO.mkRef 0\n  let mut seen"), "IO.mkRef"),
    (lambda r: r.replace("  let mut seen", "  setOption `x 0\n  let mut seen"), "setOption"),
    (lambda r: r.replace("  let mut seen", "  logInfo m!\"x\"\n  let mut seen"), "logInfo"),
    (lambda r: r.replace("if !(info matches .thmInfo _) && ", "if "), "theorem"),
    (lambda r: r.replace("  let mut seen", "  IO.println \"x\"\n  let mut seen"), "prints"),
])
def test_the_walk_reads_and_prints_only(edit, fault):
    """F6 (review 9b): in `READS` the `TM_TRUST_ONLY` gate is the walk's first statement, `done` its last line, it
    has no `modifyEnv`/`addDecl`/`setOption`/`IO.mkRef`/`initialize` (nor any other effect a later command reads),
    prints only through `say`, and keeps theorems (`thmInfo`) out of the `const` lines. Each edit is a negative
    control: the check must name it."""
    faults = walk_faults(tm.READS if edit is None else edit(tm.READS))
    if fault is None:
        assert faults == []
    else:
        assert edit(tm.READS) != tm.READS and any(fault in x for x in faults), faults


# --- the seeds, in real Lean, in five modes ----------------------------------------------------------------------


SEED_DEFS = """namespace Demo

def small (n : Nat) : Bool := n < 3

def big (n : Nat) : Bool := 5 < n

def tag (n : Nat) : Nat := n + 1

def lone (n : Nat) : Nat := n + 0

def far (n : Nat) : Nat := n * 2

def gate (n : Nat) : Bool := n < 7

def viaGate (n : Nat) : Bool := gate n && true

end Demo
"""
# S2: a proof in an imported module that the mutant breaks (cut to sorry) and a check that computes through it;
# S3: an import-time failure (a definition of the imported module fails under the mutant: the check file never loads)
SEED_MID = """import Demo.Defs

namespace Demo

theorem small_lt {n : Nat} (h : small n = true) : n < 3 := by simpa [small] using h

def bounded (n : Nat) : Bool := if h : small n = true then (⟨n, small_lt h⟩ : Fin 3).val == n else true

def loneMid : Fin 1 := ⟨lone 0, by decide⟩

end Demo
"""
FILLER = "".join(f"#guard Demo.tag {i} == {i + 1}\n" if i % 3 else f"example : Demo.big {i + 6} = true := by decide\n"
                 for i in range(40))
SEED_EXAMPLES = f"""import Demo.Mid
open Demo

-- S1: a named check theorem outside the verdict's set (it passes under the mutant), read by a check in the set
theorem pre : small 0 = true := by decide

def usesPre : Bool := (⟨0, pre⟩ : {{n : Nat // small n = true}}).1 == 0 && !small 3

#guard small 2
-- S4: a matcher an earlier check outside the set creates, which a later check of the set may reuse
#guard (match small 1 with | true => 1 | false => 0) == 1
#guard tag 0 == 1
{FILLER}#guard (tag 50 ==
  51)

#guard usesPre
#guard (match small 3 with | true => 1 | false => 0) == 0
#guard (bounded 3 && !small 3)
#guard !big 5

/-- S5: the last command, a docstring before it -/
example : big 6 = true := by decide
"""
# S6: a kill by a check whose text never names the mutated definition (`gate`, read through `viaGate`), after a
# check outside the set wrapped in `#guard_msgs`
SEED_SECOND = """import Demo.Defs

#guard Demo.tag 4 == 5

-- S7: an `rfl` check (the `decide` rebuild path)
example : Demo.tag 1 = 2 := rfl

#guard_msgs in example : Demo.gate 2 = true := by decide

#guard !Demo.viaGate 7
"""
SEED_OUTSIDE = """import Demo.Defs

#guard Demo.far 2 == 4
"""
# The modes, test-side only (the tool ships the scoped probe alone): `off` probes the whole file; `dual` also probes
# the whole file beside each scoped probe and logs both; `cut-1` cuts one line early (it must fall back and keep
# every verdict); `naive` leaves the other checks as written (the wrong design: it must change S1).
WRAPPER = r'''
import json, os, sys, threading
sys.path.insert(0, sys.argv[1])
import trust_mutants as tm

mode, log, lock, local = sys.argv[2], sys.argv[3], threading.Lock(), threading.local()
probe, kept, settle, run = tm.probe, tm.kept, tm.settle, tm.run


def norm(d, spans):
    return {f"{s[0]}-{s[1]}": {"flags": sorted(d[s]["flags"]), "consts": d[s]["consts"]} for s in spans if s in d}


def write(row):
    with lock, open(log, "a") as out:
        out.write(json.dumps({"id": getattr(local, "id", None), **row}) + "\n")


def probing(lake, env, text, roles, path, outside=False, only=None):
    row = {"file": path.name, "only": None if only is None else sorted(only)}
    if mode == "naive" and only is not None:
        roles = [r for r in roles if (r[0], r[1]) in only]
    got = probe(lake, env, text, roles, path, outside, None if mode == "off" else only)
    if only is not None:
        row["got"] = norm(got, only)
        if mode in ("dual", "cut-1"):
            row["whole"] = norm(probe(lake, env, text, roles, path, outside), only)
    write(row)
    return got


def settling(*args, **kwargs):
    try:
        args[5](("Nowhere.lean", (0, 0)))
        write({"refused": False})
    except LookupError:
        write({"refused": True})
    return settle(*args, **kwargs)


def running(m, *args, **kwargs):
    local.id = m.id
    try:
        return run(m, *args, **kwargs)
    finally:
        local.id = None


tm.probe, tm.settle, tm.run = probing, settling, running
if mode == "cut-1":
    tm.kept = lambda lines, roles, last: kept(lines, roles, last)[:-1]
sys.exit(tm.main(sys.argv[4:]))
'''
MODES = ("off", "on", "dual", "cut-1", "naive")


def seeded(root: Path, scratch: Path, mode: str) -> tuple[dict, list[dict], str]:
    scratch.mkdir(parents=True, exist_ok=True)
    (wrapper := scratch / "wrapper.py").write_text(WRAPPER)
    log, out = scratch / "probes.jsonl", scratch / "evidence.json"
    env = {**os.environ, **PATH, "TMPDIR": str(scratch), "VE_LEAN_SHARE": "off"}
    done = subprocess.run([sys.executable, str(wrapper), str(ROOT / "tools"), mode, str(log), "--root", str(root),
                           "--base", "HEAD~1", "--jobs", "4", "--json", str(out), "--test", "outside/Check.lean",
                           "--max-mutants", "1000"], env=env, capture_output=True, text=True, timeout=HANG_TIMEOUT)
    mutants = json.loads(out.read_text())["mutants"] if out.is_file() else []
    rows = [json.loads(x) for x in log.read_text().splitlines()] if log.is_file() else []
    return {m["id"]: (m["definition"], m["operator"], m["status"], m["raw_status"], m["detail"])
            for m in mutants}, rows, done.stderr[-3000:]


def test_the_scoped_probe_classifies_the_seeds_as_the_whole_file_probe(tmp_path_factory):
    """Design 6 and review 8: the seed package's mutants get the same status, raw_status and detail with the scoped
    probe (`on`, `dual`, and `cut-1`, which must fall back) as with the whole file's (`off`); in `dual` every scoped
    entry carries `done` and equals the whole file's, none absent in both and none falling back; the controls'
    probes are whole-file in every mode; `reading` refuses a key `settle` did not hand over; and the wrong design
    (`naive`) changes S1. A KILLED detail cites the first kill in Lake's output order, which two check modules built
    at once can swap (without the probe too), so it is compared up to that."""
    root = tmp_path_factory.mktemp("seeds")
    scaffold(root, ".")
    for name, text in (("Defs", SEED_DEFS), ("Mid", SEED_MID), ("Examples", SEED_EXAMPLES), ("Second", SEED_SECOND)):
        (root / f"lean/Demo/{name}.lean").write_text(text)
    (root / "outside").mkdir()
    (root / "outside/Check.lean").write_text(SEED_OUTSIDE)
    dump(root, tmp_path_factory.mktemp("dump"), ["pre", "Demo.small_lt"])
    git(root, "add", ".")
    git(root, "commit", "-qm", "head")
    got, rows = {}, {}
    for mode in MODES:
        got[mode], rows[mode], err = seeded(root, tmp_path_factory.mktemp(mode), mode)
        assert got[mode], (mode, err)
    off = got["off"]
    same = lambda v: v[:4] + (("KILLED",) if v[3] == "KILLED" else (v[4],))  # noqa: E731
    for mode in ("on", "dual", "cut-1"):
        assert {i: same(v) for i, v in got[mode].items()} == {i: same(v) for i, v in off.items()}, mode
    assert {v[2] for v in off.values()} >= {"KILLED", "UNKNOWN"}, off
    # the controls' probes are whole-file; a mutant's probe is scoped, but in `off` and on a fallback
    for mode in MODES:
        assert all(r["only"] is None for r in rows[mode] if r["id"] is None and "file" in r), mode
    scoped = {mode: [r for r in rows[mode] if r["id"] and "file" in r and r["only"] is not None] for mode in MODES}
    fell = {mode: [r for r in rows[mode] if r["id"] and "file" in r and r["only"] is None] for mode in MODES}
    assert scoped["on"] and not fell["on"] and not fell["dual"] and not fell["off"]
    assert fell["cut-1"], "the cut one line early never fell back"
    # `dual`: every scoped entry is whole and is the whole file's; no check of a set is absent in both
    dual = scoped["dual"]
    assert dual and all(r["got"] == r["whole"] for r in dual), [r for r in dual if r["got"] != r["whole"]]
    assert all(len(r["got"]) == len(r["only"]) for r in dual), [r for r in dual if len(r["got"]) != len(r["only"])]
    assert all("done" in e["flags"] for r in dual for e in r["got"].values())
    # `reading` refuses a key `settle` did not hand over, in the tool as run
    refused = [r["refused"] for r in rows["on"] if "refused" in r]
    assert refused and all(refused)
    lines = SEED_EXAMPLES.split("\n")
    at = lambda text: next(n for n, line in enumerate(lines, 1) if line.startswith(text))  # noqa: E731
    by = lambda d, o: [(i, v) for i, v in off.items() if v[:2] == (f"Demo.{d}", o)]  # noqa: E731
    # S1: the named theorem outside the set reads as `sorry` (the probe's own rewrite), so UNKNOWN, as whole-file;
    # the wrong design differs exactly there
    s1 = by("small", "lt-le")
    assert s1 and all(v[2] == "UNKNOWN" and "proof the mutant broke" in v[4] and
                      f"Examples.lean:{at('#guard usesPre')}" in v[4] for _, v in s1), s1
    assert any(got["naive"][i] != v for i, v in s1), "the wrong design kept S1"
    # S2: the check through the cut proof reads `sorry`
    s2 = f"{at('#guard (bounded 3')}-{at('#guard (bounded 3')}"
    assert any("sorry" in r["got"].get(s2, {}).get("flags", []) for r in dual), s2
    # S3: the import-time failure: UNKNOWN at the imported module, and no probe
    s3 = by("lone", "lit-plus")
    assert s3 and all(v[2] == "UNKNOWN" and "Mid.lean" in v[4] for _, v in s3), s3
    assert not any(r["id"] == i for i, _ in s3 for mode in MODES for r in rows[mode] if "file" in r)
    # S4: the matcher check read in a dual row; S5: a kill by the last command, and a cut of 5 lines or more
    assert any(s == at("#guard (match small 3") for r in dual for s, _ in r["only"])
    assert any(s == at("example : big 6") for r in dual for s, _ in r["only"])
    assert any(r["file"] == "Examples.lean" and max(e for _, e in r["only"]) <= len(lines) - 5 for r in dual)
    # S6, S7: kills through `viaGate`, in the outside file, and by the `rfl` check
    assert any(v[2] == "KILLED" and "Second.lean:" in v[4] for _, v in by("gate", "lt-le"))
    s6 = by("far", "lit-plus")
    assert s6 and all(v[2] == "KILLED" and "outside/Check.lean" in v[4] for _, v in s6), s6
    rfl = SEED_SECOND.split("\n").index("example : Demo.tag 1 = 2 := rfl") + 1
    assert any(r["file"] == "Second.lean" and any(s <= rfl <= e for s, e in r["only"]) for r in dual)
