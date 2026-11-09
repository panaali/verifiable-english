"""tools/trust_mutants.py on a tiny Lean package (speed-trustmut step 3): a well-guarded definition has no survivor,
a guard over `[]` leaves survivors, a failing proof is no kill, --allow suppresses exactly its operator, the mutants
are built in a scratch copy (the checkout's bytes and times are unchanged), and --max-mutants lists the rest as
NOT RUN. The package's declaration and predicate lists come from tools/lean_statements.py's own per-module script."""
from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

import pytest

from subprocesses import HANG_TIMEOUT

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import lake_outputs  # noqa: E402
import lean_statements  # noqa: E402

PATH = {"PATH": f"{Path.home() / '.elan/bin'}{os.pathsep}{os.environ.get('PATH', '')}"}

DEFS = """namespace Demo

/-- Guarded on both sides of its bound. -/
def small (n : Nat) : Bool := n < 3

/-- Guarded over `[]` only. -/
def evens (xs : List Nat) : List Nat := xs.filter (· % 2 == 0)

/-- No guard reads it; three proofs do, one of them a theorem whose statement names it. -/
def double (n : Nat) : Nat := n + n + 0

theorem double_eq (n : Nat) : double n = 2 * n := by unfold double; omega

/-- No guard reads it; two `example`s proved by tactics do. -/
def triple (n : Nat) : Nat := n + n + n + 0

example : triple 1 = 3 := by simp [triple]

/-- Read only by a `decide` check outside this directory whose statement names it. -/
def half (n : Nat) : Nat := n / 2

/-- Read only by tactic `example`s wrapped in `#guard_msgs` (review F6). -/
def quad (n : Nat) : Nat := n + n + n + n + 0

/-- Read only by checks wrapped in `#guard_msgs`: an `#eval` and a `decide` example. -/
def twice (n : Nat) : Nat := 2 * n

/-- Read only by a definition (no check): its error is UNKNOWN. -/
def lone (n : Nat) : Nat := n + 0

/-- Read by subtype definitions, and by checks of their values only (review F8): their errors are UNKNOWN. -/
def boxed (n : Nat) : Nat := n + 0

end Demo
"""
PROOFS = """import Demo.Defs

theorem Demo.four : (2 : Nat) + 2 = 4 := by
  have h : Demo.double 2 = 4 := by simp [Demo.double]
  omega

theorem Demo.double_two : Demo.double 2 = 4 := by simp [Demo.double]
"""
FAR = """import Demo.Defs

theorem Demo.Far.half_four : Demo.half 4 = 2 := by decide
"""
EXAMPLES = """import Demo.Defs
import Demo.Proofs
open Demo

#guard small 2
#guard !small 3
#guard evens [] == []

example : triple 2 = 6 := by simp [triple]

#guard_msgs in
example : quad 1 = 4 := by
  simp [quad]

#guard_msgs in example : quad 2 = 8 := by simp [quad]

-- an `#eval` prints no answer (hunt Q4, Q7, Q8): a `#guard` under the wrapper
#guard_msgs (whitespace := lax) in
#guard twice 3 == 6

#guard_msgs in example : twice 2 = 4 := by decide

def loneFin : Fin 1 := ⟨lone 0, by decide⟩

def boxedEval : {x : Nat // boxed x = x} := ⟨0, by decide⟩

/-- info: 0 -/
#guard_msgs in
#eval boxedEval.val

def boxedGuard : {x : Nat // boxed x = x} := ⟨0, by decide⟩

#guard boxedGuard.val == 0

def boxedDecide : {x : Nat // boxed x = x} := ⟨0, by decide⟩

example : boxedDecide.val = 0 := by decide
"""
STATED = ["Demo.Far.half_four", "Demo.double_eq", "Demo.double_two", "Demo.four"]


def short(value) -> str:
    """A test id without spaces (tools/mutants.py reads failing ids up to the first space)."""
    return re.sub(r"[^\w#!]+", "-", str(value)).strip("-")[:40]


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=root, check=True,
                   capture_output=True, timeout=HANG_TIMEOUT)


def dump(root: Path, folder: Path, stated: list[str] = STATED) -> None:
    """lean/declarations.txt and lean/predicates.txt of the package, as tools/lean_statements.py writes them."""
    modules = lean_statements.tree_modules(root)
    subprocess.run([lake_outputs.lean_executable(None, "lake"), "build", *modules], cwd=root / "lean", check=True,
                   capture_output=True, timeout=HANG_TIMEOUT)
    lines = [line for m in modules for line in lean_statements.run_lean(
        root, folder, f"import Lean\nimport {m}\n" + lean_statements.ALONE, m.replace(".", "_"),
        {"VE_PREDICATE_MODULE": m, **PATH}).splitlines()]
    declarations, pending = [], []
    for line in lines:
        if line.startswith("declaration "):
            pending.append(line.removeprefix("declaration "))
        elif line.startswith("module "):
            m = line.removeprefix("module ")
            source = root / "lean" / (m.replace(".", "/") + ".lean")
            declarations += [f"module {m} {lean_statements.source_hash(source)}", *pending]
            pending = []
    (root / "lean/declarations.txt").write_text(lean_statements.DECLARATIONS_HEADER + "\n".join(declarations) + "\n")
    (root / "lean/predicates.txt").write_text(
        lean_statements.PREDICATES_HEADER + "".join(f"module {m}\n" for m in modules)
        + "".join(line.removeprefix("predicate ") + "\n" for line in lines if line.startswith("predicate ")))
    (folder / "names.txt").write_text("".join(f"{name}\n" for name in stated))
    script = lean_statements.SCRIPT.replace("import VE\n", "".join(f"import {m}\n" for m in modules))
    (root / "lean/statements.txt").write_text(lean_statements.HEADER + lean_statements.run_lean(
        root, folder, script, "Statements", {"VE_STATEMENT_NAMES": str(folder / "names.txt"), **PATH}))


def scaffold(root: Path, *folders: str) -> None:
    """An empty Lean package `Demo` at `root` with the folders under lean/Demo/, committed as the base."""
    for folder in folders:
        (root / "lean/Demo" / folder).mkdir(parents=True)
    (root / "tools").mkdir()
    (root / "lean/lean-toolchain").write_text((ROOT / "lean/lean-toolchain").read_text())
    (root / "lean/lakefile.toml").write_text('name = "demo"\n\n[[lean_lib]]\nname = "Demo"\nglobs = ["Demo.*"]\n')
    (root / ".gitignore").write_text(".lake/\n")
    (root / "tools/trust-classes.json").write_text('{"modules": {}}\n')
    git(root, "init", "-q")
    git(root, "add", ".")
    git(root, "commit", "-qm", "base")


@pytest.fixture(scope="module")
def package(tmp_path_factory) -> Path:
    root = tmp_path_factory.mktemp("package")
    scaffold(root, "Far")
    for name, text in (("Defs", DEFS), ("Proofs", PROOFS), ("Examples", EXAMPLES), ("Far/Check", FAR)):
        (root / f"lean/Demo/{name}.lean").write_text(text)
    dump(root, tmp_path_factory.mktemp("dump"))
    git(root, "add", ".")
    git(root, "commit", "-qm", "head")
    return root


def tool(root: Path, scratch: Path, *args: str, home: dict | None = None
         ) -> tuple[subprocess.CompletedProcess, list[dict]]:
    out = scratch / "evidence.json"
    scratch.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, **PATH, "TMPDIR": str(scratch), "VE_LEAN_SHARE": "off", **(home or {})}
    done = subprocess.run([sys.executable, str(ROOT / "tools/trust_mutants.py"), "--root", str(root), "--base",
                           "HEAD~1", "--jobs", "4", "--json", str(out), *args], env=env, capture_output=True,
                          text=True, timeout=HANG_TIMEOUT)
    return done, json.loads(out.read_text())["mutants"] if out.is_file() else []


def snapshot(root: Path) -> dict[str, tuple[bytes, int]]:
    return {p.relative_to(root).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
            for p in sorted(root.rglob("*")) if p.is_file() and ".git" not in p.relative_to(root).parts}


@pytest.fixture(scope="module")
def default_run(package, tmp_path_factory):
    before = snapshot(package)
    scratch = tmp_path_factory.mktemp("run")
    done, mutants = tool(package, scratch)
    (tmp_path_factory.getbasetemp() / "default-evidence.json").write_text((scratch / "evidence.json").read_text())
    return done, mutants, before, snapshot(package)


def of(mutants: list[dict], name: str) -> list[dict]:
    return [m for m in mutants if m["definition"] == f"Demo.{name}"]


def test_a_well_guarded_definition_has_no_survivor(default_run):
    _, mutants, _, _ = default_run
    small = of(mutants, "small")
    assert {m["operator"] for m in small} >= {"lt-le", "lt-eq", "lit-plus", "lit-minus", "body-true", "body-false"}
    assert all(m["status"] == "KILLED" for m in small), small
    assert all(m["detail"].startswith("lean/Demo/Examples.lean:") for m in small)


def test_a_guard_over_the_empty_list_leaves_survivors(default_run):
    done, mutants, _, _ = default_run
    evens = of(mutants, "evens")
    survivors = [m for m in evens if m["status"] == "SURVIVOR"]
    assert {"list-empty", "list-first", "lit-plus", "eq-ne"} <= {m["operator"] for m in survivors}
    assert done.returncode == 1
    printed = [line for line in done.stdout.splitlines() if line.startswith("SURVIVOR ")]
    assert len(printed) == sum(m["status"] == "SURVIVOR" for m in mutants)
    assert "SURVIVOR lean/Demo/Defs.lean:7 Demo.evens (?, trusted) list-empty: xs.filter (· % 2 == 0) -> []" in printed


def test_a_failing_proof_is_no_kill(default_run):
    """The mutant breaks `double_eq` in its own module, and `four` and `double_two` in another (review F1:
    `double_two`'s statement names `double`, and only its proof script fails); no check reads `double`."""
    _, mutants, _, _ = default_run
    (double,) = of(mutants, "double")
    assert (double["operator"], double["after"], double["status"]) == ("lit-plus", "1", "SURVIVOR")


def test_an_example_proved_by_a_tactic_is_no_kill(default_run):
    """Review F1: an `example` not proved by `decide`/`native_decide`/`rfl` is a proof, cut in the mutated module
    and in the module of its checks alike."""
    _, mutants, _, _ = default_run
    (triple,) = of(mutants, "triple")
    assert (triple["operator"], triple["after"], triple["status"]) == ("lit-plus", "1", "SURVIVOR")


def test_a_proof_wrapped_in_guard_msgs_is_no_kill(default_run):
    """Review F6 (PROBE F6): Lean reports a wrapped proof's failure at its `#guard_msgs` line, written alone or with
    the `example`; the wrapper is the proof's, and it is blanked with the cut (else the `sorry` warning trips it)."""
    _, mutants, _, _ = default_run
    (quad,) = of(mutants, "quad")
    assert (quad["operator"], quad["after"], quad["status"]) == ("lit-plus", "1", "SURVIVOR"), quad


def test_a_check_wrapped_in_guard_msgs_kills(default_run):
    """Review F6: a `#guard_msgs` around a `#guard` (its spec in parentheses) or a `decide` example is a check."""
    _, mutants, _, _ = default_run
    twice = of(mutants, "twice")
    assert {m["operator"] for m in twice} == {"lit-plus", "lit-minus"}
    assert all(m["status"] == "KILLED" and m["detail"].split(": ")[0] in (
        "lean/Demo/Examples.lean:18", "lean/Demo/Examples.lean:19", "lean/Demo/Examples.lean:21") for m in twice), twice


def test_a_run_records_where_its_time_goes(default_run, tmp_path_factory):
    """eff-tm-control: every Lake run of a sweep counts under its step (none under "other"), each step that ran took
    time, the phases add up to the run's seconds, and the one line prints them. The lazy controls' wall phase is near
    0: their probes run inside the mutants' phase, counted under the "control_probes" Lake step (eff-20261108-1)."""
    import trust_mutants as tm
    done, mutants, _, _ = default_run
    data = json.loads((tmp_path_factory.getbasetemp() / "default-evidence.json").read_text())
    steps, built = data["steps"], [m for m in mutants if "moves this line" not in m["detail"]]
    assert tm.timed(steps) and tm.steps_line(steps) in done.stdout.splitlines()
    runs, lake = steps["runs"], steps["lake"]
    assert (runs["control_build"], runs["probe_install"], runs["other"], runs["outside_checks"]) == (1, 1, 0, 0)
    assert runs["mutant_builds"] >= len(built) and min(runs[k] for k in (
        "control_probes", "mutant_checks", "stage_controls", "mutant_probes")) >= 1, runs
    assert all((lake[k] > 0) == (runs[k] > 0) for k in tm.LAKE), steps
    assert all(steps["wall"][k] > 0 for k in ("control_build", "probe_install", "mutants")), steps
    # lazy controls (the default, eff-20261108-1) run inside the mutants' phase, still under their Lake step
    assert data["control_probes"] == "lazy" and lake["control_probes"] > 0, steps
    assert steps["wall"]["control_probes"] < steps["wall"]["mutants"], steps
    # the phases up to the mutants' end are the run's "seconds" (each rounded to 0.1 s, it to 1 s)
    assert abs(sum(steps["wall"][k] for k in tm.WALL[:6]) - data["seconds"]) <= 1.5, (steps, data["seconds"])


def test_steps_count_each_lake_run_under_its_own_threads_step(tmp_path, monkeypatch):
    """`Scratch.lake` counts a run under the step its thread is in: another thread's step, an inner step that ends,
    and a run outside any step ("other") do not leak into it."""
    import shutil
    import threading
    import trust_mutants as tm
    monkeypatch.setattr(tm.lake_outputs, "lean_executable", lambda env, name: shutil.which("true"))
    monkeypatch.setattr(tm, "STEPS", tm.Steps())
    scratch = object.__new__(tm.Scratch)
    scratch.lean = tmp_path
    with tm.STEPS.step("control_build"):
        other = threading.Thread(target=lambda: scratch.lake({}, "build"))
        other.start()
        other.join(HANG_TIMEOUT)
        scratch.lake({}, "build")
        with tm.STEPS.step("control_probes"):
            scratch.lake({}, "lean")
        scratch.lake({}, "build")
    assert tm.STEPS.runs == {**dict.fromkeys(tm.LAKE, 0), "control_build": 2, "control_probes": 1, "other": 1}
    assert all(v >= 0 for v in tm.STEPS.lake.values()) and tm.timed(tm.STEPS.record())
    assert tm.STEPS.wall == dict.fromkeys(tm.WALL, 0.0)


def test_a_guard_msgs_wrapper_is_in_the_span_of_what_it_wraps(tmp_path):
    """Review F6: trust_map.scan opens a command at the `#guard_msgs … in` line before it, as at `set_option … in`,
    so the role of the line Lean reports is the wrapped command's."""
    import trust_map
    import trust_mutants
    path = tmp_path / "A.lean"
    path.write_text("#guard f 1\n\n#guard_msgs in\nexample : f 1 = 2 := by\n  simp [f]\n\n/-- info: 2 -/\n"
                    "#guard_msgs (whitespace := lax) in\n#eval f 1\n")
    decls, _, problems = trust_map.scan(path, [])
    code = trust_mutants.code_only(path.read_text()).split("\n")
    assert problems == []
    assert [(d.start, d.end, trust_mutants.classify(d.kind, "\n".join(code[d.start - 1:d.end]))) for d in decls] == [
        (1, 2, "check"), (3, 7, "proof"), (8, 9, "check")]


@pytest.mark.parametrize(("text", "last", "cut"), [
    ("-- #guard_msgs in\n#guard_msgs in\nexample : f 1 = 2 := by\n  simp [f]\n#guard f 1\n", 4,
     "-- #guard_msgs in\n" + " " * 14 + "\nexample : f 1 = 2  := sorry\n\n#guard f 1\n"),
    ("#guard_msgs in example : f 1 = 2 := by simp [f]\n\n/-- info: 2\n-/\n#guard_msgs in\n#eval f 1\n", 4,
     " " * 15 + "example : f 1 = 2  := sorry\n\n/-- info: 2\n-/\n#guard_msgs in\n#eval f 1\n"),
    ("example : f 1 = 2 := by\n  simp [f] /- a\n  b -/\n-- c\n", 4, "example : f 1 = 2  := sorry\n\n\n-- c\n"),
    ("@[csimp, simp] theorem t : @f = @g := by\n  funext n\n  rfl\n#guard f 1 == 2\n", 3,  # hunt N2: no attribute
     " " * 15 + "theorem t : @f = @g  := sorry\n\n\n#guard f 1 == 2\n")],
    ids=short)
def test_a_cut_proof_loses_its_guard_msgs_wrapper_and_keeps_the_comments_after_it(tmp_path, text, last, cut):
    """Review F6: the cut blanks the wrapper (the `sorry` warning would fail it) and keeps the whole comments after
    the proof (the next `#guard_msgs`'s docstring is in the span before it), every line kept."""
    import trust_mutants
    path = tmp_path / "A.lean"
    path.write_text(text)
    first = 2 if text.startswith("--") else 1
    assert trust_mutants.cut_proof(path, first, last)
    assert path.read_text() == cut


def test_an_error_outside_every_check_is_unknown(default_run):
    """Only an error in a check (or a --test file) kills: `loneFin`'s proof term fails under the mutant, and it is
    a definition, which cannot be cut."""
    _, mutants, _, _ = default_run
    (lone,) = of(mutants, "lone")
    assert (lone["status"], lone["detail"].split(": ")[0]) == ("UNKNOWN", "lean/Demo/Examples.lean:23"), lone


def test_an_error_in_a_definition_beside_a_failing_check_is_unknown(default_run):
    """Review F8: the mutant breaks the `by decide` of three subtype definitions; Lean puts `sorry` there, and the
    `#eval` of one's value refuses it (the value is 0 whatever `boxed` is). The control has no such break, so
    it passes; the definitions' errors still decide: UNKNOWN at the first, never a kill."""
    _, mutants, _, _ = default_run
    (boxed,) = of(mutants, "boxed")
    assert (boxed["status"], boxed["detail"].split(": ")[0]) == ("UNKNOWN", "lean/Demo/Examples.lean:25"), boxed


def test_a_decide_check_outside_the_directory_naming_the_definition_kills(default_run):
    _, mutants, _, _ = default_run
    half = of(mutants, "half")
    assert {m["operator"] for m in half} == {"lit-plus", "lit-minus"}
    assert all(m["status"] == "KILLED" and m["detail"].startswith("lean/Demo/Far/Check.lean:3:") for m in half), half


@pytest.mark.parametrize(("kind", "text", "role"), [
    ("command", "#guard f [] == []", "check"),
    ("command", "#guard_msgs in\n#eval f 1", "check"),
    ("command", "example : f 1 = 2 := by decide", "check"),
    ("command", "@[simp] example : f 1 = 2 :=\n  by native_decide", "check"),
    ("command", "example : f 1 = 2 := rfl", "check"),
    ("theorem", "theorem t : f 1 = 2 := by decide +kernel", "check"),
    ("command", "example (n : Nat) : f n = n := by\n  simp [f]", "proof"),
    ("command", "example (h : p) : q :=\n  t h", "proof"),
    ("command", "example (_h : f 0 = 1) : f 1 = 2 := by decide", "proof"),  # hunt H1: a hypothesis decide never reads
    ("command", "example (_h : f 0 = 1) : f 1 = 2 := rfl", "proof"),
    ("theorem", "theorem t {α} [Inhabited α] : f 1 = 2 := by decide +revert", "proof"),
    ("theorem", "theorem Demo.t : f 1 = 2 :=\n  by decide", "check"),
    ("command", "example : f 5 = f 5 := rfl  example (_h : f 0 = 1) : f 1 = 2 := by decide", "other"),  # hunt N7
    ("command", "#guard_msgs in\nexample : f 1 = 2 := by simp [f]", "proof"),
    ("command", "#guard_msgs in example : f 1 = 2 := by simp [f]", "proof"),
    ("command", "#guard_msgs (drop warning) in\n@[simp] example : f 1 = 2 := by\n  simp [f]", "proof"),
    ("theorem", "#guard_msgs in\ntheorem t : f 1 = 2 := by simp [f]", "proof"),
    ("command", "#guard_msgs in example : f 1 = 2 := by decide", "check"),
    ("command", "#guard_msgs (whitespace := lax) in\n#eval f 1", "check"),
    ("command", "#guard_msgs in\n#guard f 1", "check"),
    ("command", "#guard_msgs (drop\n  info) in\n#eval f 1", "other"),
    ("command", "#guard_msgs", "other"),
    ("theorem", "theorem t : f [] = [] := by\n  simp [f]\n  rfl", "proof"),
    ("theorem", "theorem t : f [] = [] := by simp [f]; decide", "proof"),
    ("def", "def f (n : Nat) : Nat := n", "other"),
    ("command", "open Demo", "other")], ids=short)
def test_only_guards_and_decide_rfl_proofs_are_checks(kind, text, role):
    """Review F1 (and SupExtra.lean's and Status.lean's `example`s): an `example` or theorem is a check only when
    `decide`, `native_decide` or `rfl` proves it, whatever its statement names."""
    import trust_mutants
    assert trust_mutants.classify(kind, text) == role


def test_mutants_are_built_in_a_scratch_copy(default_run):
    _, mutants, before, after = default_run
    assert any(m["status"] == "KILLED" for m in mutants)
    assert after == before


def test_allow_suppresses_exactly_its_operator(package, tmp_path):
    allow = tmp_path / "allow.json"
    allow.write_text(json.dumps({"allow": [{"definition": "Demo.evens", "operator": "list-empty",
                                            "reason": "the fixture's guard is over [] by design"}]}))
    done, mutants = tool(package, tmp_path / "run", "--allow", str(allow))
    evens = of(mutants, "evens")
    allowed = [m for m in evens if m["status"] == "ALLOWED"]
    assert allowed and all(m["operator"] == "list-empty" for m in allowed)
    assert [m for m in evens if m["operator"] == "list-empty" and m["status"] != "ALLOWED"] == []
    assert all(m["status"] != "ALLOWED" for m in mutants if m["definition"] != "Demo.evens")
    assert any(m["status"] == "SURVIVOR" for m in evens) and done.returncode == 1
    assert " list-empty: " not in "".join(line for line in done.stdout.splitlines() if line.startswith("SURVIVOR"))


def test_an_outside_test_that_fails_without_the_mutant_is_no_kill(package, default_run, tmp_path):
    """Review F7: a --test file outside lean/ kills only when it passes without the mutant (its control). One whose
    `#eval` reads `double_eq` fails either way once the tool cuts it (since F11 only a proof the mutant breaks is
    cut: `double`'s): that mutant is UNKNOWN, never KILLED; every other verdict is as without the files."""
    (package / "outside").mkdir(exist_ok=True)
    (package / "outside/Value.lean").write_text("import Demo.Defs\n#guard Demo.small 2\n#guard !Demo.small 3\n")
    (package / "outside/Reads.lean").write_text(
        "import Demo.Defs\n"
        "#eval (⟨0, Nat.lt_of_lt_of_eq (by decide) (Demo.double_eq 1).symm⟩ : Fin (Demo.double 1)).val\n")
    done, mutants = tool(package, tmp_path / "run", "--test", "outside/Value.lean", "--test", "outside/Reads.lean")
    before = {m["id"]: m["status"] for m in default_run[1]}
    assert [m for m in mutants if "Reads.lean" in m["detail"] and m["status"] != "UNKNOWN"] == [], done.stdout
    assert [before[m["id"]] for m in mutants if m["definition"] == "Demo.double"] == ["SURVIVOR"]
    for m in mutants:
        if m["definition"] == "Demo.double":  # it breaks `double_eq`, which Reads.lean reads
            assert m["status"] == "UNKNOWN" and m["detail"].endswith("Reads.lean fails without the mutant too"), m
        else:
            assert m["status"] == before[m["id"]], m


BRIDGED = {  # PROBE F13: outside checks that hold for every `f` and `g`, through instances on proofs of lean/
    "lean/Demo/Defs.lean": "namespace Demo\n\ndef P (n : Nat) : Prop := n < 3\n\ndef f (n : Nat) : Bool := decide (n < 3)"
                           "\n\ndef Q (n : Nat) : Prop := n < 4\n\ndef g (n : Nat) : Bool := decide (n < 4)\n\nend Demo\n",
    # imported by the outside file itself, in the mutated module's directory, with no check
    "lean/Demo/Bridge.lean": "import Demo.Defs\n\nnamespace Demo\n\ntheorem p_iff (n : Nat) : P n ↔ f n = true := by simp "
                             "[P, f]\n\ninstance (n : Nat) : Decidable (P n) := decidable_of_iff (f n = true) (p_iff "
                             "n).symm\n\nend Demo\n",
    # reached only through `Demo.Far.Top`, which the outside file imports, in another directory
    "lean/Demo/Far/Mid.lean": "import Demo.Defs\n\nnamespace Demo\n\ntheorem q_iff (n : Nat) : Q n ↔ g n = true := by "
                              "simp [Q, g]\n\ninstance (n : Nat) : Decidable (Q n) := decidable_of_iff (g n = true) "
                              "(q_iff n).symm\n\nend Demo\n",
    "lean/Demo/Far/Top.lean": "import Demo.Far.Mid\n",
    "checks/Check.lean": "import Demo.Bridge\nimport Demo.Far.Top\n\nopen Demo\n\nexample : ¬ P 3 := by decide\n\n"
                         "example : ¬ Q 4 := by decide\n",
}


def test_probe_f13_an_outside_check_reads_its_imports_built_with_the_mutant(tmp_path):
    """PROBE F13: `lake env lean` builds nothing, so the modules an outside --test file imports (directly, or through
    a module that imports them) kept their pre-mutant `.olean`: the proof the mutant broke there (`p_iff`, `q_iff`)
    was never rechecked, cut or seen by the probe, and `decide` refuted `¬ P 3` through the instance on it (KILLED,
    although it holds for every `f`). Now they are built with the mutant, as a check module is: the broken proof is
    cut and the probe finds it, so UNKNOWN, as the same check inside lean/ gives (hunt H4)."""
    root = tmp_path / "package"
    scaffold(root, "Far")
    (root / "checks").mkdir()
    for name, text in BRIDGED.items():
        (root / name).write_text(text)
    (tmp_path / "dump").mkdir()
    dump(root, tmp_path / "dump", [])
    git(root, "add", ".")
    git(root, "commit", "-qm", "head")
    done, mutants = tool(root, tmp_path / "run", "--max-mutants", "1000", "--test", "checks/Check.lean")
    for name in ("f", "g"):
        mine = of(mutants, name)
        assert mine and not [m for m in mine if m["status"] == "KILLED"], (mine, done.stdout + done.stderr)
        assert [m for m in mine if m["status"] == "UNKNOWN" and "a proof the mutant broke" in m["detail"]], mine


def test_an_outside_test_whose_header_cannot_be_read_stops_the_run(package, tmp_path):
    """Review F13: the modules an outside --test file imports are read from its header; one the tool cannot read
    (an import sharing its line) stops the run (2) before any build, never a run that skips them."""
    (package / "outside").mkdir(exist_ok=True)
    (package / "outside/Header.lean").write_text("import Demo.Defs import Demo.Proofs\n#guard Demo.small 2\n")
    done, mutants = tool(package, tmp_path / "run", "--test", "outside/Header.lean")
    assert done.returncode == 2 and "Header.lean" in done.stderr and mutants == [], done.stdout + done.stderr


def test_a_build_past_its_time_limit_is_unknown(package, tmp_path):
    """Hunt T5w, T7: a mutant can make Lean run forever (an instance chain `Small (n + 0)`), so every build of a
    mutant has `--build-timeout`; past it the process group is killed and the mutant is UNKNOWN, never KILLED or a
    hung run. An expired limit (0 s) is injected: every mutant build is past it at once."""
    done, mutants = tool(package, tmp_path / "run", "--max-mutants", "3", "--build-timeout", "0")
    ran = [m for m in mutants if m["status"] != "NOT RUN"]
    assert len(ran) == 3 and done.returncode == 1, done.stdout + done.stderr
    assert all(m["status"] == "UNKNOWN" and "did not finish in 0 s" in m["detail"] for m in ran), ran


@pytest.mark.parametrize("limit", [0, 3])
def test_max_mutants_lists_the_rest_as_not_run(package, tmp_path, limit):
    """A budget of 0 runs nothing and never exits 0 (3: incomplete)."""
    done, mutants = tool(package, tmp_path / "run", "--max-mutants", str(limit))
    ran = [m for m in mutants if m["status"] != "NOT RUN"]
    assert len(ran) == limit and len(mutants) > limit
    printed = [line for line in done.stdout.splitlines() if line.startswith("NOT RUN ")]
    assert len(printed) == len(mutants) - limit
    assert done.returncode == (1 if any(m["status"] == "SURVIVOR" for m in ran) else 3)


@pytest.fixture(scope="module")
def prefix_run(package, tmp_path_factory) -> Path:
    """The evidence of a run of the first five mutants: four of `small` (KILLED) and one of `evens` (SURVIVOR)."""
    scratch = tmp_path_factory.mktemp("prefix")
    tool(package, scratch, "--max-mutants", "5")
    return scratch / "evidence.json"


def rescored(root: Path, scratch: Path, prev: Path, *args: str, home: dict | None = None
             ) -> tuple[subprocess.CompletedProcess, dict]:
    done, _ = tool(root, scratch, "--rescore", str(prev), *args, home=home)
    out = scratch / "evidence.json"
    return done, json.loads(out.read_text()) if out.is_file() else {}


def test_rescore_after_an_allow_only_edit_builds_nothing(package, prefix_run, tmp_path):
    """speed-tmrescore: on an unchanged tree, a new --allow entry is all that changed. Every verdict is the last
    run's (`reused_from` its head), the survivor it names is ALLOWED (`raw_status` SURVIVOR), and Lake never runs:
    the `lake` first on the tool's PATH records each call and fails."""
    prev = json.loads(prefix_run.read_text())
    ran = [m for m in prev["mutants"] if m["status"] != "NOT RUN"]
    (survivor,) = [m for m in ran if m["status"] == "SURVIVOR"]
    assert len(ran) == 5 and {m["status"] for m in ran} == {"KILLED", "SURVIVOR"} and prev["inputs"], ran
    shim, log = tmp_path / "home/.elan/bin/lake", tmp_path / "lake.log"
    shim.parent.mkdir(parents=True)
    shim.write_text(f"#!/bin/sh\necho \"$*\" >> {log}\nexit 97\n")
    shim.chmod(0o755)
    allow = tmp_path / "allow.json"
    allow.write_text(json.dumps({"allow": [{"definition": survivor["definition"], "operator": survivor["operator"],
                                            "reason": "allowed after the run"}]}))
    done, data = rescored(package, tmp_path / "run", prefix_run, "--max-mutants", "5", "--allow", str(allow),
                          home={"HOME": str(tmp_path / "home"), "ELAN_HOME": str(Path.home() / ".elan")})
    assert not log.exists() and done.returncode == 3, done.stdout + done.stderr
    assert data["rescore"] == {"file": str(prefix_run), "head": prev["head"], "mode": "identical", "changed": [],
                               "reused": 5, "rerun": 0}
    assert f"5 reused from {prev['head'][:12]} (identical inputs)" in done.stdout
    now = {m["id"]: m for m in data["mutants"]}
    for m in ran:
        mine = now[m["id"]]
        assert (mine["reused_from"], mine["raw_status"], mine["detail"] if m is not survivor else "") == (
            prev["head"], m["status"], m["detail"] if m is not survivor else ""), mine
        assert mine["status"] == ("ALLOWED" if m is survivor else m["status"]), mine
    assert not [m for m in data["mutants"] if m["id"] not in {x["id"] for x in ran} and "reused_from" in m]


def test_rescore_runs_the_not_run_mutants_that_now_fit(package, prefix_run, tmp_path):
    """--max-mutants decides which mutants run, never a verdict: a larger one reuses the five and runs two more."""
    done, data = rescored(package, tmp_path / "run", prefix_run, "--max-mutants", "7")
    assert data["rescore"]["reused"] == 5 and data["rescore"]["rerun"] == 2, done.stdout + done.stderr
    fresh = [m for m in data["mutants"] if m["status"] != "NOT RUN" and "reused_from" not in m]
    assert [m["id"] for m in fresh] == ["M006", "M007"] and all(m["raw_status"] == m["status"] for m in fresh)


def test_rescore_reruns_only_the_unknown_mutants(package, default_run, tmp_path, tmp_path_factory):
    """The UNKNOWN mutants of the last run, and they alone, run again. Rescored with an expired build limit (0 s),
    each of them is past it (and only they: every other verdict, KILLED ones included, is the last run's); rescored
    once more with the default limit, those forced UNKNOWNs run alone and give the first run's verdicts back."""
    first = tmp_path_factory.getbasetemp() / "default-evidence.json"
    prev = {m["id"]: m for m in json.loads(first.read_text())["mutants"]}
    unknown = sorted(i for i, m in prev.items() if m["raw_status"] == "UNKNOWN")
    assert unknown and any(m["status"] == "KILLED" for m in prev.values())
    done, forced = rescored(package, tmp_path / "forced", first, "--build-timeout", "0")
    rerun = sorted(m["id"] for m in forced["mutants"] if m["status"] != "NOT RUN" and "reused_from" not in m)
    assert rerun == unknown and forced["rescore"]["rerun"] == len(unknown), done.stdout + done.stderr
    for m in forced["mutants"]:
        if m["id"] in unknown:
            assert m["status"] == "UNKNOWN" and "did not finish in 0 s" in m["detail"], m
        else:
            assert (m["status"], m["detail"]) == (prev[m["id"]]["status"], prev[m["id"]]["detail"]), m
    done, again = rescored(package, tmp_path / "again", tmp_path / "forced/evidence.json")
    assert sorted(m["id"] for m in again["mutants"] if m["status"] != "NOT RUN" and "reused_from" not in m) == unknown
    assert [(m["status"], m["detail"].split(": ")[0]) for m in again["mutants"]] == [
        (m["status"], m["detail"].split(": ")[0]) for m in prev.values()], done.stdout + done.stderr


@pytest.mark.parametrize("old", ["no-inputs", "unreadable"])
def test_rescore_of_an_old_or_unreadable_file_is_a_full_run(package, prefix_run, tmp_path, old):
    """Evidence written before `inputs` existed, or a file that is no evidence, is a full run, said in one line."""
    prev = tmp_path / "prev.json"
    data = json.loads(prefix_run.read_text())
    prev.write_text(json.dumps({k: v for k, v in data.items() if k != "inputs"}) if old == "no-inputs" else "{")
    done, data = rescored(package, tmp_path / "run", prev, "--max-mutants", "2")
    said = [line for line in done.stdout.splitlines() if "a full run, since" in line]
    assert len(said) == 1 and ("records no inputs" if old == "no-inputs" else "cannot be read") in said[0], said
    assert (data["rescore"]["reused"], data["rescore"]["rerun"], data["rescore"]["head"], data["rescore"]["mode"]) == (
        0, 2, None, "full")
    assert not [m for m in data["mutants"] if "reused_from" in m]


CHANGES = {  # one byte of each input, or an option or the base, changed in a copy of the package
    "check-file": lambda r: (r / "lean/Demo/Examples.lean").write_text(
        (r / "lean/Demo/Examples.lean").read_text().replace("#guard small 2", "#guard small 1")),
    "selected-file": lambda r: (r / "lean/Demo/Defs.lean").write_text((r / "lean/Demo/Defs.lean").read_text() + " "),
    "lakefile": lambda r: (r / "lean/lakefile.toml").write_text((r / "lean/lakefile.toml").read_text() + " "),
    "statements": lambda r: (r / "lean/statements.txt").write_text((r / "lean/statements.txt").read_text() + "\n"),
    "trust-table": lambda r: (r / "tools/trust-classes.json").write_text('{"modules": {} }\n'),
    "test-file": lambda r: (r / "outside/T.lean").write_text("import Demo.Defs\n#guard Demo.small 1\n"),
    "pycache": lambda r: (r / "lean/__pycache__").mkdir() or (r / "lean/__pycache__/audit.pyc").write_bytes(b"\0"),
}
# what --rescore makes of each: mode "checks" with the files that changed, mode "identical", or a full run and why
EXPECTED = {"check-file": ["lean/Demo/Examples.lean"], "statements": ["lean/statements.txt"],
            "test-file": ["outside/T.lean"], "pycache": [],
            "selected-file": "its inputs differ (lean): lean/Demo/Defs.lean is a selected declaration's file",
            "lakefile": "its inputs differ (lean): lean/lakefile.toml is no module of lean/",
            "trust-table": ["tools/trust-classes.json"],
            "deep": "its inputs differ (options)", "test-option": "its inputs differ (options)",
            "classes": "its inputs differ (options)",
            "base": ["lean/Demo/Examples.lean"], "tool": "its inputs differ (tool)",
            "no-files": "its inputs differ (lean) and it records no per-file digests"}
EXPECTED_PLAN_ONLY = {"trust-table": ["tools/trust-classes.json"], "base": ["base"]}  # eff-20261104-1


@pytest.mark.parametrize("change", [*CHANGES, "deep", "test-option", "classes", "base", "tool", "no-files"])
def test_any_changed_input_but_checks_gives_a_full_run(package, tmp_path, change):
    """`inputs` digests the bytes, never a commit id (speed-tmrescore), and each file's own (speed-tmchecks). A
    check-only change (a check module outside every selected declaration's file and import closure, an outside
    --test file, a generated inventory) is mode "checks", with the files that changed; a `__pycache__` none at all
    (review F1). One byte of a selected declaration's file or the lakefile, or another tool, --deep, --test or
    --classes, is a full run, even beside a check-only change, and so is PREV with no per-file digests
    (eff-20261026-1b: no verdict carries across another selection). trust_map's table and base go on to the same
    checks (eff-20261104-1: PREV's mutants, here none, still decide)."""
    import shutil
    import trust_mutants
    root = tmp_path / "copy"
    shutil.copytree(package, root, symlinks=True, ignore=shutil.ignore_patterns(".lake"))
    (root / "outside").mkdir(exist_ok=True)
    (root / "outside/T.lean").write_text("import Demo.Defs\n#guard Demo.small 2\n")
    base = "0123456789abcdef" * 2 + "01234567"  # a commit id: `main` resolves it, `inputs` records it as it is

    def digests(deep: bool = False, tests: tuple = (), base: str = base, classes: tuple = ("trusted",)) -> dict:
        return trust_mutants.inputs(root, base, list(tests), [root / "outside/T.lean"], deep, classes)

    def why_not(names: list[str]) -> str | None:
        return trust_mutants.check_only(names, {"Demo/Defs.lean"}, {"outside/T.lean"},
                                        trust_mutants.lake_reads(root, [root / "outside/T.lean"]))
    prev, before = tmp_path / "prev.json", digests()
    prev.write_text(json.dumps({"inputs": before, "head": "h", "mutants": []}))
    assert trust_mutants.previous(prev, digests(), [], why_not) == ("identical", "h", {}, [], [])
    if change in CHANGES:
        CHANGES[change](root)
    else:  # a key no check-only change may move, beside one that may
        CHANGES["check-file"](root)
    now = digests(change == "deep", ("Demo/Examples.lean",) if change == "test-option" else (),
                  base if change != "base" else base[:-1] + ("0" if base[-1] != "0" else "1"),
                  ("all",) if change == "classes" else ("trusted",))
    if change == "tool":
        now["tool"] = "0" * 64
    if change == "no-files":
        prev.write_text(json.dumps({"inputs": {k: v for k, v in before.items() if k != "files"}, "head": "h",
                                    "mutants": []}))
    got, expected = trust_mutants.previous(prev, now, [], why_not), EXPECTED[change]
    if isinstance(expected, list):
        assert got == ("checks" if expected else "identical", "h", {}, expected,
                       EXPECTED_PLAN_ONLY.get(change, [])), got
    else:
        assert isinstance(got, str) and got.startswith(expected), got


def test_the_inputs_digest_the_tools_own_source(tmp_path, monkeypatch):
    """A byte changed in the tool, or in a module of the repository it imports, changes its `inputs`."""
    import types
    import trust_mutants
    (tmp_path / "tools").mkdir()
    (tmp_path / "lean").mkdir()
    source = tmp_path / "tools/helper.py"
    source.write_text("X = 1\n")
    helper = types.ModuleType("tm_helper")
    helper.__file__ = str(source)
    monkeypatch.setattr(trust_mutants, "ROOT", tmp_path)
    monkeypatch.setitem(sys.modules, "tm_helper", helper)
    before = trust_mutants.inputs(tmp_path, "b", [], [], False, ("trusted",))
    source.write_text("X = 2\n")
    after = trust_mutants.inputs(tmp_path, "b", [], [], False, ("trusted",))
    assert [k for k in after if after[k] != before[k]] == ["tool", "tool_files"]
    assert before["tool_files"]["tools/helper.py"] == hashlib.sha256(b"X = 1\n").hexdigest()
    assert after["tool_files"]["tools/helper.py"] == hashlib.sha256(b"X = 2\n").hexdigest()
    assert not {k for k in after["files"] if k.startswith("tools/helper")}


def test_the_overall_tool_digest_is_what_it_was_with_each_modules_beside_it(tmp_path, monkeypatch):
    """eff-20261104-1: `tool_files` is added beside `tool`, whose digest (names, lengths, bytes, sorted) is unchanged."""
    import types
    import trust_mutants
    (tmp_path / "tools").mkdir()
    (tmp_path / "lean").mkdir()
    helpers = {"tools/a.py": b"A = 1\n", "tools/b.py": b"B = 22\n", "lean/c.py": b"C\n"}
    monkeypatch.setattr(trust_mutants, "ROOT", tmp_path)
    for name, data in helpers.items():
        (tmp_path / name).write_bytes(data)
        module = types.ModuleType(name)
        module.__file__ = str(tmp_path / name)
        monkeypatch.setitem(sys.modules, f"tm_{name}", module)
    got = trust_mutants.inputs(tmp_path, "b", [], [], False, ("trusted",))
    whole = hashlib.sha256()
    for name, data in sorted(helpers.items()):
        whole.update(f"{name}\0{len(data)}\0".encode() + data)
    assert got["tool"] == whole.hexdigest()
    assert got["tool_files"] == {name: hashlib.sha256(data).hexdigest() for name, data in helpers.items()}


def test_rescore_of_evidence_whose_mutants_differ_is_a_full_run(tmp_path):
    """Identical inputs give the same plan; evidence whose mutant rows are not the plan's is refused all the same."""
    import trust_mutants
    m = trust_mutants.Mutant("M001", "Demo/Defs.lean", 3, "Demo.small", "lt-le", 0, 1, (3, 3), "<", "≤")
    row = {"id": "M001", "file": "Demo/Defs.lean", "line": 3, "definition": "Demo.small", "operator": "lt-le",
           "before": "<", "after": "≤", "status": "ALLOWED", "raw_status": "SURVIVOR", "detail": "a reason",
           "raw_detail": "", "lines": [3, 3], "trust_class": "C", "trusted": True}
    prev = tmp_path / "prev.json"
    now = dict.fromkeys(trust_mutants.OVERALL, "1")
    unread = [{**row, "raw_status": "PASSED"}, {k: v for k, v in row.items() if k != "raw_status"}, {**row, "reads": 7},
              {**row, "killed_at": [1]}, {**row, "killed_at": [1, True]}, {**row, "line": True},  # tm-shard fix1 F1
              {**row, "status": None, "raw_status": None}, {**row, "detail": 7}, {**row, "raw_status": "ALLOWED"},
              {**row, "status": "OTHER SHARD", "raw_status": "OTHER SHARD", "detail": ""}, {**row, "trusted": 1},
              {**row, "raw_detail": 7}]
    for rows, ok in (([row], True), ([{**row, "after": "="}], False), ([], False),
                     ([{k: v for k, v in row.items() if k != "raw_detail"}], False), *(([r], False) for r in unread)):
        prev.write_text(json.dumps({"inputs": now, "head": "h", "mutants": rows}))
        got = trust_mutants.previous(prev, now, [m], lambda names: None)
        assert (got == ("identical", "h", {"M001": {"status": "SURVIVOR", "detail": "", "reads": "", "killed_at": None}},
                        [], [])) if ok else isinstance(got, str) and (
            "cannot be read" in got) == any(r in unread for r in rows), (rows, got)
    prev.write_text(json.dumps({"inputs": now, "head": "", "mutants": [row]}))
    assert "cannot be read" in trust_mutants.previous(prev, now, [m], lambda names: None)


@pytest.mark.parametrize("operator, raw, allowed", [
    ("ctor-drop", ("SURVIVOR", "the proofs it breaks: lean/Demo/Proofs.lean:3"),
     "a Prop (the proofs it breaks: lean/Demo/Proofs.lean:3)"),
    ("lt-le", ("SURVIVOR", "it builds"), "a reason"), ("lt-le", ("UNKNOWN", "past 0 s"), "a reason"),
    ("lt-le", ("KILLED", "lean/Demo/Examples.lean:5: Expression"), None)])
def test_rescore_reads_the_whole_verdict_before_allow(tmp_path, operator, raw, allowed):
    """Review sc-1ae recheck F6, as a class: --rescore reads every row's verdict as it was before --allow, its status
    (`raw_status`) and its detail (`raw_detail`), whatever the operator and whatever --allow wrote over it. A row
    --allow changed that records no `raw_detail` is refused (a full run), never read with an empty detail: a
    ctor-drop's empty detail means it breaks no proof, which no later --allow allows."""
    import trust_mutants
    m = trust_mutants.Mutant("M001", "Demo/Defs.lean", 3, "Demo.Ev", operator, 0, 1, (3, 3), "<", "≤")
    row = {"id": "M001", "file": "Demo/Defs.lean", "line": 3, "definition": "Demo.Ev", "operator": operator,
           "before": "<", "after": "≤", "raw_status": raw[0], "lines": [3, 3], "trust_class": "C", "trusted": True,
           **({"status": "ALLOWED", "detail": allowed, "raw_detail": raw[1]} if allowed else
              {"status": raw[0], "detail": raw[1]})}
    prev = tmp_path / "prev.json"
    now = dict.fromkeys(trust_mutants.OVERALL, "1")
    prev.write_text(json.dumps({"inputs": now, "head": "h", "mutants": [row]}))
    got = trust_mutants.previous(prev, now, [m], lambda names: None)
    assert got[2]["M001"] == {"status": raw[0], "detail": raw[1], "reads": "", "killed_at": None}, got
    if allowed:
        prev.write_text(json.dumps({"inputs": now, "head": "h", "mutants": [
            {k: v for k, v in row.items() if k != "raw_detail"}]}))
        assert "raw_detail" in trust_mutants.previous(prev, now, [m], lambda names: None)


LAYERED = {  # speed-tmchecks: a definition whose module imports another, and its checks
    "Demo/Base.lean": "namespace Demo\n\ndef limit : Nat := 3\n\nend Demo\n",
    "Demo/Defs.lean": "import Demo.Base\n\nnamespace Demo\n\ndef small (n : Nat) : Bool := n < limit\n\nend Demo\n",
    "Demo/Examples.lean": "import Demo.Defs\nopen Demo\n\n#guard small 2\n#guard !small 3\n",
}
# each change to LAYERED, and whether a KILLED verdict at `#guard !small 3` and an INVALID one in `small` carry
EDITS = [
    ("none", {}, True, True),
    ("check-added-above", {"Demo/Examples.lean": ("#guard small 2\n", "#guard small 1\n#guard small 2\n")},
     True, True),
    ("definition-added-above", {"Demo/Examples.lean": ("#guard small 2\n", "def three := 3\n#guard small 2\n")},
     False, True),
    ("check-edited", {"Demo/Examples.lean": ("!small 3", "!small 4")}, False, True),
    ("closure-edited", {"Demo/Base.lean": ("end Demo", "-- a comment\nend Demo")}, False, False),
]


def layered(root: Path, edits: dict[str, tuple[str, str]]):
    """LAYERED with `edits` (file -> (old, new)) at `root`, and its `Reads`."""
    import trust_mutants
    for f, text in LAYERED.items():
        path = root / "lean" / f
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text.replace(*edits[f]) if f in edits else text)
    files = {lean_statements.module_name(f): f for f in LAYERED}
    tree = trust_mutants.Tree({f: trust_mutants.file_roles(root / "lean" / f) for f in LAYERED}, {}, files, {})
    return trust_mutants.Reads(root, tree, [])


@pytest.mark.parametrize(("name", "edits", "kill", "invalid"), EDITS, ids=[e[0] for e in EDITS])
def test_a_verdict_carries_only_while_what_it_reads_reads_the_same(tmp_path, name, edits, kill, invalid):
    """speed-tmchecks (speed-tmrerun's rule.py, moved into the tool): a KILLED verdict carries while its killing
    check, the lines before it that count and what its file imports read the same (a check added above it moves it:
    its detail follows), and while the build still reads that check; an INVALID one while the mutated declaration's
    file before it and its import closure read the same."""
    import trust_mutants
    before = layered(tmp_path / "before", {})
    m = trust_mutants.Mutant("M001", "Demo/Defs.lean", 5, "Demo.small", "lt-le", 0, 0, (5, 5), "<", "≤")
    m.raw_status, m.raw_detail = "KILLED", "lean/Demo/Examples.lean:5: Expression"
    m.detail = m.raw_detail
    before.verdict(m)
    assert m.reads and m.killed_at == (5, 5), m
    killed = {"status": "KILLED", "detail": m.detail, "reads": m.reads, "killed_at": list(m.killed_at)}
    m.raw_status, m.raw_detail = "INVALID", "unknown identifier"
    m.detail = m.raw_detail
    before.verdict(m)
    refused = {"status": "INVALID", "detail": m.detail, "reads": m.reads, "killed_at": None}
    after = layered(tmp_path / "after", edits)
    built = ["Demo.Defs", "Demo.Examples"]
    line = 6 if name == "check-added-above" else 5
    assert after.carry(m, killed, built) == (("KILLED", f"lean/Demo/Examples.lean:{line}: Expression") if kill else None)
    assert after.carry(m, refused, built) == (("INVALID", "unknown identifier") if invalid else None)
    assert after.carry(m, killed, ["Demo.Defs"]) is None  # a check the build no longer reads kills nothing
    assert after.carry(m, {**killed, "status": "SURVIVOR"}, built) is None


def test_a_check_only_change_lies_outside_every_selected_file_and_its_closure(tmp_path):
    """speed-tmchecks: the files a check-only change may touch: a module of lean/ outside every selected
    declaration's file and import closure (`reach`, read from the imports), an outside --test file or a generated
    inventory, or an unread plan input or Markdown file; any other file is a full run."""
    import trust_mutants
    reads = layered(tmp_path, {})
    m = trust_mutants.Mutant("M001", "Demo/Defs.lean", 5, "Demo.small", "lt-le", 0, 0, (5, 5), "<", "≤")
    reach = trust_mutants.reach(reads, [m])
    assert reach == {"Demo/Defs.lean", "Demo/Base.lean"}
    ok = ["lean/Demo/Examples.lean", "lean/Demo/New.lean", "lean/declarations.txt", "lean/statements.txt",
          "outside/T.lean", "tools/trust-classes.json", "lean/SCOPE.md"]
    lake = trust_mutants.lake_reads(tmp_path, [])
    assert trust_mutants.check_only(ok, reach, {"outside/T.lean"}, lake) is None
    for name, why in (("lean/Demo/Defs.lean", "a selected declaration's file"),
                      ("lean/Demo/Base.lean", "in its import closure"), ("lean/lakefile.toml", "no module"),
                      ("lean/lean-toolchain", "no module"),
                      ("outside/U.lean", "no module")):
        assert why in (trust_mutants.check_only([*ok, name], reach, {"outside/T.lean"}, lake) or ""), name


def test_rescore_after_a_check_only_change_carries_the_kills_it_reads_the_same(package, default_run, tmp_path,
                                                                                tmp_path_factory):
    """speed-tmchecks: after a check module is added (its check kills `evens`' survivors) and a killing check is
    edited (`half_four`, in a module of no selected declaration), --rescore carries every KILLED and INVALID verdict
    but the edited check's (`reused_from`, `carried: "checks"`), and builds the rest: the edited check's mutants and
    the SURVIVOR and UNKNOWN ones. Every verdict is what a full run on the same tree gives."""
    import shutil
    prev_path = tmp_path_factory.getbasetemp() / "default-evidence.json"
    prev = json.loads(prev_path.read_text())
    root = tmp_path / "copy"
    shutil.copytree(package, root, symlinks=True, ignore=shutil.ignore_patterns(".lake"))
    far = root / "lean/Demo/Far/Check.lean"
    assert "Demo.half 4 = 2" in far.read_text()
    far.write_text(far.read_text().replace("Demo.half 4 = 2", "Demo.half 5 = 2"))
    (root / "lean/Demo/More.lean").write_text("import Demo.Defs\nopen Demo\n\n#guard evens [2, 3, 4] == [2, 4]\n")
    (tmp_path / "dump").mkdir()
    dump(root, tmp_path / "dump")
    done, data = rescored(root, tmp_path / "rescore", prev_path)
    full_done, full = tool(root, tmp_path / "full")
    was = {m["id"]: m for m in prev["mutants"]}
    edited = {i for i, m in was.items() if m["raw_status"] == "KILLED" and m["detail"].startswith(
        "lean/Demo/Far/Check.lean:")}
    survivors = {i for i, m in was.items() if m["raw_status"] == "SURVIVOR" and m["definition"] == "Demo.evens"}
    assert edited and survivors, was
    carried = {m["id"] for m in data["mutants"] if m.get("carried") == "checks"}
    assert carried == {i for i, m in was.items() if m["raw_status"] in ("KILLED", "INVALID")} - edited, (
        data["rescore"], done.stdout)
    assert {m["reused_from"] for m in data["mutants"] if m["id"] in carried} == {prev["head"]}
    assert not [m for m in data["mutants"] if m["id"] not in carried and ("reused_from" in m or "carried" in m)]
    changed = ["lean/Demo/Far/Check.lean", "lean/Demo/More.lean", "lean/declarations.txt", "lean/predicates.txt",
               "lean/statements.txt"]
    assert {k: data["rescore"][k] for k in ("head", "mode", "changed", "reused")} == {
        "head": prev["head"], "mode": "checks", "changed": changed, "reused": len(carried)}, data["rescore"]
    assert f"{len(carried)} carried from {prev['head'][:12]} (check-only change: {', '.join(changed)})" in done.stdout
    now = {m["id"]: m for m in data["mutants"]}
    assert all(now[i]["status"] == "KILLED" and now[i]["detail"].startswith("lean/Demo/More.lean:4:")
               for i in survivors), [now[i] for i in survivors]
    assert all(now[i]["status"] == "KILLED" for i in edited), [now[i] for i in edited]
    assert [(m["id"], m["status"], m["detail"].split(": ")[0]) for m in data["mutants"]] == [
        (m["id"], m["status"], m["detail"].split(": ")[0]) for m in full], (done.stdout, full_done.stdout)
    assert done.returncode == full_done.returncode == 1


CLASSED = {  # eff-20261026-1b: one declaration of each kind --classes tells apart
    "Demo/Defs.lean": """namespace Demo

/-- A limit, reject-only (D[R]): guarded on both sides of its bound. -/
def small (n : Nat) : Bool := n < 3

/-- Checked code (C), guarded over `[]` only. -/
def evens (xs : List Nat) : List Nat := xs.filter (· % 2 == 0)

/-- A proof helper (P). -/
def double (n : Nat) : Nat := n + n + 0

theorem double_eq (n : Nat) : double n = 2 * n := by unfold double; omega

/-- Unclassified: trusted. -/
def twice (n : Nat) : Nat := 2 * n

end Demo
""",
    "Demo/Examples.lean": "import Demo.Defs\nopen Demo\n\n#guard small 2\n#guard !small 3\n#guard evens [] == []\n"
                          "#guard twice 3 == 6\n\nexample : double 1 = 2 := by decide\n",
}
TABLE = {"modules": {"Demo/Defs.lean": {"D[R]": ["Demo.small"], "C": ["Demo.evens"], "P": ["Demo.double"]}}}


@pytest.fixture(scope="module")
def classed(tmp_path_factory) -> Path:
    root = tmp_path_factory.mktemp("classed")
    scaffold(root, "")
    for f, text in CLASSED.items():
        (root / "lean" / f).write_text(text)
    (root / "tools/trust-classes.json").write_text(json.dumps(TABLE))
    dump(root, tmp_path_factory.mktemp("classed-dump"), ["Demo.double_eq"])
    git(root, "add", ".")
    git(root, "commit", "-qm", "head")
    return root


@pytest.fixture(scope="module")
def classed_all(classed, tmp_path_factory):
    scratch = tmp_path_factory.mktemp("classed-all")
    done, _ = tool(classed, scratch, "--classes", "all")
    return done, json.loads((scratch / "evidence.json").read_text()), scratch / "evidence.json"


def planned(root: Path, *classes: str) -> list:
    import trust_mutants
    found, _, fatal = trust_mutants.plan(root, "HEAD~1", *([classes] if classes else []))
    assert not fatal, fatal
    return found


def test_with_no_flag_the_plan_selects_exactly_the_trusted_definitions(classed):
    """With no --classes the plan is `trusted`'s, and its declarations are exactly those trust_map counts as trusted
    (read here from trust_map itself): the reject-only, checked and proof-helper ones are skipped."""
    import trust_map
    import trust_mutants
    default = planned(classed)
    assert [asdict(m) for m in default] == [asdict(m) for m in planned(classed, "trusted")]
    classified, _, problems = trust_map.walk(classed, classed / "tools/trust-classes.json",
                                             classed / "lean/statements.txt")
    assert not problems, problems
    trusted = {c.decl.name for c in classified if c.trusted and c.decl.kind not in ("theorem", "command")}
    assert {m.definition for m in default} == trusted == {"Demo.twice"}, default
    assert all(m.trusted and m.trust_class == "?" for m in default)
    assert trust_mutants.classes_of("trusted") == trust_mutants.TRUSTED


def test_classes_all_adds_the_untrusted_definitions_and_keeps_the_default(classed):
    """`--classes all` selects the reject-only and checked definitions the default skips; its trusted mutants are
    the default's, field for field but the ids and run order; a class name picks that class alone."""
    key = ("file", "line", "definition", "operator", "start", "end", "before", "after", "trust_class", "trusted")
    default, wide = planned(classed), planned(classed, "all")
    assert {m.definition for m in wide} == {"Demo.small", "Demo.evens", "Demo.twice"}, wide
    assert sorted(tuple(getattr(m, k) for k in key) for m in wide if m.trusted) == sorted(
        tuple(getattr(m, k) for k in key) for m in default)
    assert {(m.definition, m.trust_class, m.trusted) for m in wide} == {
        ("Demo.small", "D[R]", False), ("Demo.evens", "C", False), ("Demo.twice", "?", True)}
    assert {m.definition for m in planned(classed, "C", "D[R]")} == {"Demo.small", "Demo.evens"}
    assert {m.definition for m in planned(classed, "D[R]")} == {"Demo.small"}


def test_a_theorem_proof_helper_or_check_is_never_selected(classed):
    """P and T are no --classes name, and no list selects a theorem, a proof helper (P) or a check (T)."""
    import trust_mutants
    assert not {"P", "T"} & set(trust_mutants.SELECTABLE)
    for classes in [("all",), trust_mutants.SELECTABLE, ("trusted", *trust_mutants.SELECTABLE)]:
        names = {m.definition for m in planned(classed, *classes)}
        assert not names & {"Demo.double", "Demo.double_eq", None}, (classes, names)


@pytest.mark.parametrize("text", ["P", "T", "C,P", "trusted,T", "X", "c", "", "C,", "all,?"])
def test_an_unknown_class_name_is_refused(classed, tmp_path, text):
    """A name that is not `trusted`, `all` or a selectable trust_map class stops the run (exit 2) before any plan."""
    import trust_mutants
    assert trust_mutants.classes_of(text) is None
    done, mutants = tool(classed, tmp_path / "run", "--classes", text)
    assert done.returncode == 2 and "--classes" in done.stderr and not mutants, done.stdout + done.stderr


def test_classes_names_are_read_from_trust_map():
    """The selectable names are trust_map's CLASSES but its KIND_CLASSES' (one owner); `all` absorbs the rest."""
    import trust_map
    import trust_mutants
    assert set(trust_mutants.SELECTABLE) == set(trust_map.CLASSES) - set(trust_map.KIND_CLASSES.values())
    assert trust_mutants.classes_of(" D[R] ,C,C") == ("C", "D[R]")
    assert trust_mutants.classes_of("trusted,all,G[R]") == ("all",)


def test_classes_all_mutates_a_reject_only_definition_and_names_each_class(classed_all):
    """Under `--classes all` the reject-only limit is mutated and killed by its guards, the checked definition's
    survivors print with its class, the trusted one's with ", trusted", the JSON records the list, each mutant's
    class and the verdicts counted by class, and the summary prints them."""
    done, data, _ = classed_all
    mutants = data["mutants"]
    small, evens, twice = (of(mutants, n) for n in ("small", "evens", "twice"))
    assert small and all(m["status"] == "KILLED" and (m["trust_class"], m["trusted"]) == ("D[R]", False)
                         for m in small), small
    assert {(m["trust_class"], m["trusted"]) for m in evens} == {("C", False)}
    assert {(m["trust_class"], m["trusted"]) for m in twice} == {("?", True)}
    survivors = [line for line in done.stdout.splitlines() if line.startswith("SURVIVOR ")]
    assert survivors and any(" Demo.evens (C) " in line for line in survivors), done.stdout
    assert all(re.search(r" Demo\.\w+ \((C|D\[R\]|\?, trusted)\) [\w-]+: ", line) for line in survivors), survivors
    assert data["classes"] == ["all"]
    for cls, trusted in (("D[R]", False), ("C", False), ("?", True)):
        label = cls + (", trusted" if trusted else "")
        mine = [m["status"] for m in mutants if m["trust_class"] == cls]
        assert data["class_counts"][label] == {s: mine.count(s) for s in set(mine)}, data["class_counts"]
        assert f"trust_mutants: {label}: " in done.stdout
    assert done.returncode == 1


def test_a_default_run_records_its_selection(default_run, tmp_path_factory):
    """With no flag every mutant is trusted, and the JSON says the list was `trusted`."""
    data = json.loads((tmp_path_factory.getbasetemp() / "default-evidence.json").read_text())
    assert data["classes"] == ["trusted"] and json.loads(data["inputs"]["options"])["classes"] == ["trusted"]
    assert data["mutants"] and all(m["trusted"] and m["trust_class"] == "?" for m in data["mutants"])


def test_rescore_carries_only_across_the_same_classes(classed, classed_all, tmp_path):
    """--rescore reuses a verdict only under the same --classes: the same list is mode "identical" (every verdict
    reused, nothing built), another list is a full run even when it selects the very same mutants."""
    _, prev, path = classed_all
    done, same = rescored(classed, tmp_path / "same", path, "--classes", "all")
    ran = [m for m in prev["mutants"] if m["raw_status"] in ("KILLED", "INVALID", "SURVIVOR")]
    assert ran and (same["rescore"]["mode"], same["rescore"]["reused"]) == ("identical", len(ran)), done.stdout
    assert [(m["id"], m["status"]) for m in same["mutants"]] == [(m["id"], m["status"]) for m in prev["mutants"]]
    # every class the package has, named: the plan is `all`'s, the selection's list is not
    names = ("trusted", "C", "D[R]")
    assert [(m.id, m.definition, m.operator) for m in planned(classed, *names)] == [
        (m["id"], m["definition"], m["operator"]) for m in prev["mutants"]]
    done, other = rescored(classed, tmp_path / "other", path, "--classes", ",".join(names), "--max-mutants", "0")
    assert (other["rescore"]["mode"], other["rescore"]["head"]) == ("full", None), done.stdout
    assert other["rescore"]["full_run"] == "its inputs differ (options)"
    assert not [m for m in other["mutants"] if "reused_from" in m]


def test_the_generator_cuts_every_list_a_condition_reads():
    """The list positions of reviews ap-2 F7, F10 and F11 (a method's receiver, `for ... in`, a `++` operand), and
    the token operators; nothing inside a string literal is mutated."""
    import trust_mutants
    text = ('def ok (fs : List (List String)) (ms : List String) : Bool := Id.run do\n'
            '  for f in fs do\n    if (f.find? (· == "x<1")).isSome then return false\n'
            '  return fs.all (·.isEmpty) && (ms ++ ["y"]).length < 3\n')
    found = {(op, text[s:e], new) for op, s, e, new in trust_mutants.mutants(text, "def", 0, len(text))}
    assert {("list-drop-first", "f", "(f.drop 1)"), ("list-drop-last", "fs", "(fs.dropLast)"),
            ("list-first", "ms", "(ms.take 1)"), ("append-left", ' ++ ["y"]', ""), ("lt-le", "<", "≤"),
            ("lit-plus", "3", "4"), ("all-any", "all", "any"), ("and-or", "&&", "||"),
            ("bool-flip", "false", "true")} <= found
    literal = text.index('"x<1"')
    assert not [m for m in trust_mutants.mutants(text, "def", 0, len(text)) if literal <= m[1] < literal + 5]


def test_the_generator_drops_each_middle_element_of_a_literal_list():
    """Review ap-2b F1: `"nor"` and `"to"` of `fillExcl`'s literal list, neither first nor last, were never dropped;
    the list cuts keep or drop only its ends. Each element between the ends is dropped alone (its comma with it),
    across lines and around nested groups; a comma in a string or a nested group splits nothing."""
    import trust_mutants
    text = ('def fillExcl (ws : List String) : List String :=\n'
            '  ["and", "or", "nor", "to", "be"] ++ ws ++ [(1, "a, b").2,\n'
            '    f [x, y], g] ++ ["x", "y"]\n')
    drops = [(text[s:e], new) for op, s, e, new in trust_mutants.mutants(text, "def", 0, len(text))
             if op == "list-drop-middle"]
    # a dropped line's end is put back, so every line after the declaration stays where it was
    assert drops == [(' "or",', ""), (' "nor",', ""), (' "to",', ""), ("\n    f [x, y],", "\n")]
    for before, after in drops:
        mutated = text.replace(before, after, 1)
        assert mutated.count("[") == mutated.count("]") and "[(1, " in mutated


def test_the_generator_drops_each_constructor_of_an_inductive():
    """Review sc-1ae F1: deleting `JsonWF`'s `bool` and `num` broke no proof and no check, and no operator wrote that
    mutant. Each constructor is dropped alone: across lines, its doc comment with it, never a `deriving` clause or a
    `|` inside a bracket; every line after it stays where it was."""
    import trust_mutants
    text = ('inductive Ev : Nat → Prop\n'
            '  | zero : Ev 0\n'
            '  /-- two more,\n      across lines -/\n'
            '  | step (n : Nat) (h : Ev n) :\n      Ev (n + 2)\n'
            '  | odd (h : match 1 with\n  | 0 => True\n  | _ => False) : Ev 1\n'
            'inductive Color where\n  | red\n  | green\n  deriving Repr\n')
    split = text.index("inductive Color")
    drops = [(text[s:e], new) for lo, hi in ((0, split - 1), (split, len(text) - 1))
             for op, s, e, new in trust_mutants.mutants(text, "inductive", lo, hi) if op == "ctor-drop"]
    assert drops == [("  | zero : Ev 0", ""),
                     ("  /-- two more,\n      across lines -/\n  | step (n : Nat) (h : Ev n) :\n      Ev (n + 2)",
                      "\n\n\n"),
                     ("  | odd (h : match 1 with\n  | 0 => True\n  | _ => False) : Ev 1", "\n\n"),
                     ("  | red", ""), ("  | green", "")]
    assert not [m for m in trust_mutants.mutants(text, "def", 0, split - 1) if m[0] == "ctor-drop"]


def test_the_generator_drops_each_constructor_of_json_wf():
    """Review sc-1ae F1's own declaration: each of `JsonWF`'s six constructors, `bool` and `num` among them."""
    import trust_mutants
    text = (ROOT / "lean/VE/Scope/Govern.lean").read_text()
    declared, _ = trust_mutants.declaration_list(lean_statements.inventory_path("lean/declarations.txt"))
    (r,) = [d for d in declared["VE.Scope.Govern"] if d.name == "VE.Scope.JsonWF"]
    starts = [0, *(i + 1 for i, ch in enumerate(text) if ch == "\n")]
    lo, hi = starts[r.start[0] - 1] + r.start[1], starts[r.end[0] - 1] + r.end[1]
    drops = [text[s:e].split()[1] for op, s, e, _ in trust_mutants.mutants(text, "inductive", lo, hi)
             if op == "ctor-drop"]
    assert drops == ["null", "bool", "num", "str", "arr", "obj"]


INDUCTIVE = """namespace Demo

/-- `zero` is read by a proof, `step` by nothing. -/
inductive Ev : Nat → Prop
  | zero : Ev 0
  | step (n : Nat) : Ev n → Ev (n + 2)

end Demo
"""
INDUCTIVE_PROOFS = """import Demo.Defs

theorem Demo.ev_zero : Demo.Ev 0 := .zero
"""
INDUCTIVE_CHECKS = """import Demo.Proofs

#guard (2 : Nat) + 2 == 4
"""


def test_a_constructor_no_proof_reads_survives_with_no_proof_named_and_is_never_allowed(tmp_path_factory):
    """Review sc-1ae F1 end to end: a Prop's constructors are exercised only by proofs, so both drops survive; the
    one a proof reads names it (what an --allow reason cites), the one nothing reads names none. The proof is built
    because a module of checks imports it."""
    root = tmp_path_factory.mktemp("inductive")
    scaffold(root, "Far")
    for name, text in (("Defs", INDUCTIVE), ("Proofs", INDUCTIVE_PROOFS), ("Examples", INDUCTIVE_CHECKS)):
        (root / f"lean/Demo/{name}.lean").write_text(text)
    dump(root, tmp_path_factory.mktemp("dump"), ["Demo.ev_zero"])
    git(root, "add", ".")
    git(root, "commit", "-qm", "head")
    run = tmp_path_factory.mktemp("run")
    done, mutants = tool(root, run)
    drops = {m["before"].split()[1]: (m["status"], m["detail"]) for m in of(mutants, "Ev")
             if m["operator"] == "ctor-drop"}
    assert drops == {"zero": ("SURVIVOR", "the proofs it breaks: lean/Demo/Proofs.lean:3"), "step": ("SURVIVOR", "")}, \
        done.stdout + done.stderr
    # --allow never allows the constructor nothing reads; the one it allows keeps the proof it breaks
    allow = tmp_path_factory.mktemp("allow") / "allow.json"
    allow.write_text(json.dumps({"allow": [{"definition": "Demo.Ev", "operator": "ctor-drop", "reason": "a Prop"}]}))
    again = tmp_path_factory.mktemp("again")
    done, mutants = tool(root, again, "--allow", str(allow), "--rescore", str(run / "evidence.json"))
    allowed = {m["before"].split()[1]: (m["status"], m["detail"]) for m in of(mutants, "Ev")
               if m["operator"] == "ctor-drop"}
    assert allowed == {"zero": ("ALLOWED", "a Prop (the proofs it breaks: lean/Demo/Proofs.lean:3)"),
                       "step": ("SURVIVOR", "")}, done.stdout + done.stderr
    assert done.returncode == 1 and [line for line in done.stdout.splitlines()
                                     if line.startswith("SURVIVOR") and "ctor-drop: | step" in line], done.stdout
    # review sc-1ae recheck F6: a --rescore of the allowed run's evidence reuses each drop's verdict before --allow:
    # with the same --allow the allowed drop is still ALLOWED with the proof it breaks, and with none it is the
    # survivor it was
    for extra, want in ((("--allow", str(allow)), allowed), ((), drops)):
        done, mutants = tool(root, tmp_path_factory.mktemp("third"), *extra, "--rescore", str(again / "evidence.json"))
        got = [m for m in of(mutants, "Ev") if m["operator"] == "ctor-drop"]
        assert {m["before"].split()[1]: (m["status"], m["detail"]) for m in got} == want and all(
            m.get("reused_from") for m in got) and done.returncode == 1, done.stdout + done.stderr


# Review F7's truth table: every command form `classify` can see, its class, and two readings of a definition: its
# value (`{v}`, which a check must catch) and a proof the tool cuts (`{p}`, through the witness `{w}`: up front in
# the mutated module, when the mutant breaks it in another). An outcome a cut or broken proof can change must never
# be a kill. `None`: the form has no proof reading of its own (its tactic block is the proof it reads).
FORMS = [  # (form, class, value reading, proof reading, the value reading's mutants: see `table_rows`)
    ("#guard", "check", "#guard {v} == {e}", "#guard {w}.val == 0", "KILLED"),
    # Review F11: definitional equality fails alike when the two sides differ and when a reduction got stuck.
    ("#guard_expr", "check", "#guard_expr {v} =~ {e}", "#guard_expr {w}.val =~ 0", "UNKNOWN"),
    # Review F11: the message an `#eval` throws is the file's own, no refutation Lean states.
    ("#eval", "check", '#eval (do if {v} != {e} then throw (IO.userError "changed") : IO Unit)', "#eval {w}.val",
     "UNKNOWN"),
    # Hunt Q4, Q7, Q8: an `#eval`'s output under its docstring is no answer (instances Lean picks after elaboration
    # format it, and it can read files).
    ("#eval value", "check", "#eval {v}", None, "doc UNKNOWN"),
    # Review F11: `#reduce` prints a stuck term as readily as a value, so its docstring compares no answer.
    ("#reduce", "check", "#reduce {v}", "#reduce {w}.val", "doc UNKNOWN"),
    ("#check", "check", "#check (rfl : {v} = {e})", "#check {w}", "UNKNOWN"),
    ("#print", "proof", "#print {d}", "#print {p}", "SURVIVOR"),
    ("#print axioms", "proof", "#print axioms {d}", "#print axioms {p}", "SURVIVOR"),
    ("decide example", "check", "example : {v} = {e} := by decide", "example : {w}.val = 0 := by decide", "KILLED"),
    # Review F11: `rfl`'s failure kills only when `decide` (or `native_decide`) then refutes the statement.
    ("rfl example", "check", "example : {v} = {e} := rfl", "example : {w}.val = 0 := rfl", "KILLED"),
    ("tactic example", "proof", "example : {v} = {e} := by {tac}", "example : {w}.val = 0 := by {tac}", "SURVIVOR"),
    ("tactic theorem", "proof", "theorem {id}_t : {v} = {e} := by {tac}", "theorem {id}_t : {w}.val = 0 := by {tac}",
     "SURVIVOR"),
    ("#guard with a tactic block", "proof", "#guard (⟨0, by {tac}⟩ : Fin (2 - {n})).val == 0", None, "SURVIVOR"),
    # Review F8's form (the recheck's missing row): a definition with a proof inside it, and a check of its value
    # (0 whatever the definition is) beside it. The mutant breaks the proof: an error in a definition, UNKNOWN.
    ("definition with a proof", "other", "def {id}_s : {{x : Nat // x = 0 ∧ {v} = {e}}} := ⟨0, by decide⟩\n"
     "#guard {id}_s.val == 0", "def {id}_s : Fin ({n}) := {w}\n#guard {id}_s.val == 0", "UNKNOWN"),
]
WRAPS = ("bare", "wrapped", "doc")  # the command alone, under `#guard_msgs in`, and with its docstring too
# A definition's type and body, its values on 0..5, its value at 1, that value as a size `{n}` and the proof `{p}`
# (`{d} 1 = {one}`) turned into `1 = {n}`.
SIMPLE = {"type": "Nat", "body": "n + 0", "e": "[0, 1, 2, 3, 4, 5]", "one": "1", "n": "{d} 1",
          "one_eq": "{p}.symm"}  # one mutant: lit-plus
RICH = {"type": "Bool", "body": "!(n < 1) && (n ≤ 3 || decide (n = 5)) && n != 2 && ([n] ++ [1]).all (· ≥ 1) && "
        "[n, 3].any (· == 3) && true", "e": "[false, true, false, true, false, true]", "one": "true",
        "n": "({d} 1).toNat", "one_eq": "(congrArg Bool.toNat {p}).symm"}  # the sweep's: every operator but the arms


def table_rows(group: bool = True) -> list[dict]:
    """One row per form, reading, wrapping and setting, with the status its definition's mutants must have: a cut
    proof's reading is SURVIVOR; the value's is the form's (FORMS; "doc X": X with its docstring, else SURVIVOR,
    since a bare or info-dropping command compares nothing): KILLED when a check states a refutation of it,
    UNKNOWN when the check fails stating none, or when a command that is no check reads it (review F11: every
    error that is no refutation). With `group`, the rows that must survive share one definition per wrapping,
    setting and reading."""
    rows = []
    for setting in ("mutated", "other"):
        for wrap in WRAPS:
            for reads in ("value", "proof"):
                for form, cls, value, proof, verdict in FORMS:
                    if (text := value if reads == "value" else proof) is not None:
                        expected = "SURVIVOR" if reads == "proof" else verdict.split()[-1] if wrap == "doc" or \
                            not verdict.startswith("doc ") else "SURVIVOR"
                        rows.append({"form": form, "class": cls, "reads": reads, "wrap": wrap, "setting": setting,
                                     "expected": expected, "text": text,
                                     "key": (setting, wrap, reads, form if expected != "SURVIVOR" or not group
                                             else "")})
    names: dict[tuple, str] = {}
    for i, row in enumerate(rows):
        row["d"], row["id"] = names.setdefault(row["key"], f"r{len(names)}"), f"x{i}"
    return rows


def table_package(root: Path, folder: Path, rich: bool = False, group: bool = True) -> list[dict]:
    """The table as a Lean package at `root` (committed over an empty base): Demo/M/Defs.lean holds the mutated
    setting (definitions, proofs and readings in one module), Demo/O/Defs.lean the other setting's definitions and
    Demo/O/Checks.lean their proofs and readings. Each row's docstring is the messages Lean gives its bare command."""
    mode = RICH if rich else SIMPLE
    rows = table_rows(group)
    scaffold(root, "M", "O")
    files = {"mutated": "Demo/M/Defs.lean", "other": "Demo/O/Checks.lean"}

    def write(messages: dict[tuple[str, int], list[str]] | None) -> None:
        texts = {"Demo/M/Defs.lean": ["namespace Demo.M", ""], "Demo/O/Defs.lean": ["namespace Demo.O", ""],
                 "Demo/O/Checks.lean": ["import Demo.O.Defs", "", "namespace Demo.O", ""]}
        seen = set()
        for row in rows:
            d, lines = row["d"], texts[files[row["setting"]]]
            if d not in seen:
                seen.add(d)
                texts["Demo/M/Defs.lean" if row["setting"] == "mutated" else "Demo/O/Defs.lean"] += [
                    f"def {d} (n : Nat) : {mode['type']} := {mode['body']}", ""]
                if row["reads"] == "proof":
                    lines += [f"theorem {d}_p : {d} 1 = {mode['one']} := by exact (by decide)", ""]
            size, one_eq = mode["n"].format(d=d), mode["one_eq"].format(p=f"{d}_p")
            command = row["text"].format(d=d, id=row["id"], p=f"{d}_p", v=f"(List.range 6).map {d}", e=mode["e"],
                                         tac="exact (by decide)", n=size,
                                         w=f"(⟨0, Nat.lt_of_lt_of_eq Nat.zero_lt_one {one_eq}⟩ : Fin ({size}))")
            said = [] if messages is None else messages[files[row["setting"]], row["line"]]
            if messages is None or row["wrap"] == "bare":
                row["line"] = len(lines) + 1
                lines += [*command.split("\n"), ""]
                continue
            if row["wrap"] == "doc":
                lines += ["/--", *"\n---\n".join(said).split("\n"), "-/"] if said else ["/-- -/"]
            row["line"] = len(lines) + 2
            lines += ["#guard_msgs (drop info) in" if said and row["wrap"] == "wrapped" else "#guard_msgs in",
                      *command.split("\n"), ""]
        for name, lines in texts.items():
            (root / "lean" / name).write_text("\n".join([*lines, f"end Demo.{name.split('/')[1]}", ""]))

    write(None)
    lake = lake_outputs.lean_executable(None, "lake")
    subprocess.run([lake, "build", "Demo.O.Defs"], cwd=root / "lean", check=True, capture_output=True,
                   timeout=HANG_TIMEOUT, env={**os.environ, **PATH})
    messages: dict[tuple[str, int], list[str]] = {}
    for name in set(files.values()):
        done = subprocess.run([lake, "env", "lean", "--json", name], cwd=root / "lean", capture_output=True, text=True,
                              timeout=HANG_TIMEOUT, env={**os.environ, **PATH})
        for line in done.stdout.splitlines():
            said = json.loads(line)
            assert said["severity"] == "information", said  # the bare table builds cleanly
            messages.setdefault((name, said["pos"]["line"]), []).append(f"info: {said['data'].rstrip()}")
    for row in rows:
        messages.setdefault((files[row["setting"]], row["line"]), [])
    write(messages)
    helpers: dict[str, list[str]] = {}  # the rows' own definitions are test helpers (T), never mutated
    for row in rows:
        if row["text"].startswith("def "):
            name = files[row["setting"]]
            helpers.setdefault(name, []).append(f"Demo.{name.split('/')[1]}.{row['id']}_s")
    (root / "tools/trust-classes.json").write_text(json.dumps({"modules": {f: {"T": n} for f, n in helpers.items()}}))
    dump(root, folder, [])
    git(root, "add", ".")
    git(root, "commit", "-qm", "head")
    return rows


@pytest.mark.parametrize("wrap", WRAPS)
@pytest.mark.parametrize(("form", "cls", "value", "proof", "verdict"), FORMS,
                         ids=[f[0].replace(" ", "-") for f in FORMS])
def test_classify_truth_table(form, cls, value, proof, verdict, wrap):
    """Review F7: each form's class is the same bare, under `#guard_msgs in` and with a docstring too; a check form
    with a tactic block in it is a proof."""
    import trust_mutants
    for text in (value, proof):
        if text is None:
            continue
        command = text.format(d="f", id="t", p="f_p", v="f 1", e="1", tac="simp [f]", w="(⟨0, f_p⟩ : Fin 2)", n="f 1")
        span = {"bare": command, "wrapped": f"#guard_msgs (drop info) in\n{command}",
                "doc": f"/-- info: 1 -/\n#guard_msgs in\n{command}"}[wrap]
        code = trust_mutants.code_only(span)
        assert trust_mutants.classify("theorem" if form == "tactic theorem" else "command", code) == cls, span


@pytest.mark.parametrize(("text", "cls"), [
    ("#eval! f 1", "check"),
    ("set_option maxRecDepth 100 in\n#eval f 1", "check"),
    ("#guard_msgs in\nset_option maxRecDepth 100 in\n#reduce f 1", "check"),
    ("#eval (⟨0, by simp⟩ : Fin 2)", "proof"),
    ("#guard_msgs in\n#check (by simp : f 1 = 1)", "proof"),
    ("#reduce (⟨0, by decide⟩ : Fin 2)", "proof"),
    ("#print axioms f", "proof"),
    ("#guard_msgs in\n#guard_msgs in\n#print f", "proof"),
    ("#synth Inhabited Nat", "other"),
    ("#check_failure f true", "other"),
    ("#exit", "other"),
    ("example : (⟨0, by simp⟩ : Fin 2).val = 0 := by decide", "proof"),
    ("example : f 1 = 1 := by exact (by decide)", "proof")], ids=short)
def test_classify_reads_every_command(text, cls):
    """Review F7: a check form with a tactic block anywhere in it is a proof; `#print` in any spelling is a proof;
    a command that is none of the check forms is other (an error there is no kill)."""
    import trust_mutants
    assert trust_mutants.classify("command", trust_mutants.code_only(text)) == cls


def test_every_hash_command_opens_its_own_span(tmp_path):
    """Review F7: trust_map opens a span at every `#` command, so `classify` sees the command Lean reports."""
    import trust_map
    import trust_mutants
    path = tmp_path / "A.lean"
    path.write_text("theorem t : True := by\n  trivial\n#check_failure f true\n#guard_expr f 1 =~ 1\n#eval! f 1\n"
                    "def g : Array Nat :=\n  #[1, 2]\n")
    decls, _, problems = trust_map.scan(path, [])
    code = trust_mutants.code_only(path.read_text()).split("\n")
    assert [(d.start, d.end, trust_mutants.classify(d.kind, "\n".join(code[d.start - 1:d.end])))
            for d in decls if d.kind == "command"] == [(3, 3, "other"), (4, 4, "check"), (5, 5, "check")]
    assert [(d.start, d.end) for d in decls if d.kind != "command"] == [(1, 2), (6, 7)]  # `#[` is a term


@pytest.mark.parametrize(("text", "first", "last", "cut"), [
    ("#guard f 1\n/-- info: 1\n-/\n#guard_msgs in\n#eval f 1\n-- c\n", 4, 6,
     "#guard f 1\n" + " " * 11 + "\n  \n" + " " * 14 + "\n" + " " * 9 + "\n-- c\n"),
    ('#eval "a\n-- b"\n#guard_msgs in #print axioms f\n', 3, 3, '#eval "a\n-- b"\n' + " " * 30 + "\n")], ids=short)
def test_a_cut_command_is_blanked_with_its_docstring(tmp_path, text, first, last, cut):
    """Review F7: a `#` command is cut whole, with the comment lines before it (its `#guard_msgs` docstring), but
    never a string the command before it is still writing; every line is kept."""
    import trust_mutants
    path = tmp_path / "A.lean"
    path.write_text(text)
    assert trust_mutants.cut_proof(path, first, last)
    assert path.read_text() == cut


@pytest.fixture(scope="module")
def table_run(tmp_path_factory):
    root = tmp_path_factory.mktemp("table")
    rows = table_package(root, tmp_path_factory.mktemp("table-dump"))
    done, mutants = tool(root, tmp_path_factory.mktemp("table-run"), "--max-mutants", "1000")
    return root, rows, done, mutants


def test_the_truth_table_classes(table_run):
    """Review F7: the role the tool gives each row's command, on the package's own spans (docstrings and wrappers
    in place), is the table's class."""
    import trust_mutants
    root, rows, _, _ = table_run
    _, tree, fatal = trust_mutants.plan(root, "HEAD~1")
    assert fatal == []
    module = {"mutated": "Demo/M/Defs.lean", "other": "Demo/O/Checks.lean"}
    m = trust_mutants.Mutant("M", "Demo/O/Defs.lean", 1, "Demo.O.r0", "lit-plus", 0, 0, (1, 1), "", "")
    assert [trust_mutants.role(tree, module[r["setting"]], r["line"], m) for r in rows] == [r["class"] for r in rows]


def test_the_truth_table_statuses(table_run):
    """Review F7 (the DRI's table): in the mutated module (its proofs cut up front) and in another (a proof the
    mutant breaks is cut there), whether the reading is the value or a cut proof, bare, wrapped or with a
    docstring: a check that compares the value kills, and nothing a cut or broken proof can change ever does; a
    definition whose proof the mutant breaks is UNKNOWN at its own line, whatever check fails beside it (F8)."""
    _, rows, done, mutants = table_run
    module = {"mutated": "lean/Demo/M/Defs.lean", "other": "lean/Demo/O/Checks.lean"}
    space = {"mutated": "Demo.M", "other": "Demo.O"}
    statuses = {m["definition"]: (m["status"], m["detail"].split(": ")[0]) for m in mutants}
    assert len(statuses) == len(mutants) == len({(r["setting"], r["d"]) for r in rows}), done.stdout
    for row in rows:
        status, where = statuses[f"{space[row['setting']]}.{row['d']}"]
        lines = range(row["line"] - (row["wrap"] != "bare"), row["line"] + 1)  # the wrapper's or the command's
        # a SURVIVOR names the proofs it breaks, if any (review sc-1ae F1)
        places = [f"{module[row['setting']]}:{n}" for n in lines] if row["expected"] != "SURVIVOR" else [
            "", "the proofs it breaks"]
        assert status == row["expected"] and where in places, (row, done.stdout)


ARMS = "def f : Nat → List Nat\n  | 0 => [1]\n  | _ => [2,\n   3]"


@pytest.mark.parametrize(("decl", "rest", "before", "new", "mutated"), [
    ("def f :=\n  [1,\n   2]", "\n\n#guard f == [1, 2]\n", "[1,\n   2]", "[]",
     "def f :=\n  []\n\n\n#guard f == [1, 2]\n"),
    (ARMS, "\n\n#guard f 1 == [2, 3]\n", "[1]", "[2,\n   3]",
     "def f : Nat → List Nat\n  | 0 => [2,\n   3]\n  | _ => [2,\n   3]\n#guard f 1 == [2, 3]\n"),
    (ARMS, "\n#guard f 1 == [2, 3]\n", "[1]", "[2,\n   3]", None),
    (ARMS, " /-\n\n-/\n#guard f 1 == [2, 3]\n", "[1]", "[2,\n   3]", None)],
    ids=("fewer", "more", "more-no-blank", "more-blank-in-a-comment"))
def test_an_edit_keeps_every_line_after_its_declaration(decl, rest, before, new, mutated):
    """Review F9: a shorter replacement is padded; a longer one takes its extra line ends from the blank lines right
    after the declaration (never from a comment), else it is written as it is (`mutated` None) and `moved` finds
    the first line it moved, which `run` reports as UNKNOWN."""
    import trust_mutants
    text, s = decl + rest, decl.index(before)
    end, edit = trust_mutants.relined(text, s, s + len(before), new, len(decl))
    after = text[:s] + edit + text[end:]
    assert after == (mutated or text[:s] + new + text[s + len(before):])
    lines = (1, max(decl.count("\n") + 1, text.count("\n", 0, end)))
    assert trust_mutants.moved(text, after, lines) == (None if mutated else decl.count("\n") + 2)


@pytest.mark.parametrize(("after", "lines", "line"), [
    ("def f := [1,\n  2]\n#guard f == [1]\n#guard g\n", (1, 2), 3),
    ("def f := [1,\n  2]\n#guard f == [1]\n#guard g\n", (1, 1), 2),
    ("def f := [2]\n#guard f == [1]\n\n#guard g\n", (1, 1), None),
    ("def f := [1]\n#guard f == [1]\n\n#guard g", (1, 1), 5)], ids=("count-kept", "own-line", "same", "count"))
def test_moved_finds_the_first_line_after_the_declaration_that_moved(after, lines, line):
    """Review F9: `moved` compares each line outside the mutated declaration, not only the line count (an edit that
    took a blank line below a check keeps the count and moves the check)."""
    import trust_mutants
    assert trust_mutants.moved("def f := [1]\n#guard f == [1]\n\n#guard g\n", after, lines) == line


REFUTE = "Expression\n  f 1 == 2\ndid not evaluate to `true`"


@pytest.mark.parametrize(("message", "role", "built", "checkout", "verdict"), [
    (REFUTE, "check", "#guard f 1 == 2", "#guard f 1 == 2", "KILL"),
    ("unexpected token '<;>'; expected command", "check", "  <;> trivial", "#guard f 1 == 2", "UNKNOWN"),
    ("unexpected token '<;>'; expected command", "check", "#guard f 1 == 2", "#guard f 1 == 2", "UNKNOWN"),
    ("expected term", "check", "#guard f 1 == 2", "#guard f 1 == 2", "UNKNOWN"),
    (REFUTE, "check", "  <;> trivial", "#guard f 1 == 2", "UNKNOWN"),
    (REFUTE, "check", "", "", "UNKNOWN"),
    ("Tactic `decide` proved that the proposition\n  f 1 = 2\nis false", "other", "def s := ⟨0, by decide⟩",
     "def s := ⟨0, by decide⟩", "UNKNOWN"),
    ("Tactic `decide` proved that the proposition\n  f 1 = 2\nis false", "proof", "  constructor <;> decide",
     "  constructor <;> decide", "UNKNOWN"),
    (REFUTE, "other", "#guard g", "#guard g", "UNKNOWN"),
    ("unexpected end of input", "other", "#guard g", "#guard g", "UNKNOWN")], ids=short)
def test_only_a_checks_own_error_kills(message, role, built, checkout, verdict):
    """Review F9 (the DRI's step 2) under F11's rule: an error kills only at a check line the mutant and the cuts
    left as the checkout has it, never when Lean's parser reports it (a cut left behind, a moved line), and never
    outside a check, whatever it says (a `decide` inside a tactic proof refutes a goal the tactics made)."""
    import trust_mutants
    assert trust_mutants.judge(message, role, built, checkout, "#guard f 1 == 2") == verdict


GUARD = "❌️ Docstring on `#guard_msgs` does not match generated message:\n\n"
# Review F11, the rule inverted: one row per message form at a check's own line, the check's code, and the verdict.
# KILL only when the message states a refutation; RFL when an `rfl` check failed (`settle` asks `decide` and
# `native_decide`); every other row is a safe case, UNKNOWN.
JUDGED = [
    ("decide-false", "Tactic `decide` proved that the proposition\n  f 1 = 2\nis false",
     "example : f 1 = 2 := by decide", "KILL"),
    ("native-false", "Tactic `native_decide` evaluated that the proposition\n  f 1 = 2\nis false",
     "example : f 1 = 2 := by native_decide", "KILL"),
    ("guard-false", REFUTE, "#guard f 1 == 2", "KILL"),
    ("eval-value-differs", GUARD + "- info: 5\n+ info: 4", "/-- info: 5 -/\n#guard_msgs in\n#eval f 3", "UNKNOWN"),
    ("eval-lines-differ", GUARD + "  info: 1\n- ---\n- info: 2\n+ 3", "#guard_msgs in\n#eval f", "UNKNOWN"),
    ("eval-printed-nothing", GUARD + "- info: 5", "/-- info: 5 -/\n#guard_msgs in\n#eval f 3", "UNKNOWN"),
    ("guard-under-guard-msgs", GUARD + "-\n+ error: Expression\n+   f 1 == 2\n+ did not evaluate to `true`",
     "#guard_msgs in\n#guard f 1 == 2", "KILL"),
    ("decide-under-guard-msgs", GUARD + "-\n+ error: Tactic `decide` proved that the proposition\n+   f 1 = 2\n"
     "+ is false", "#guard_msgs in example : f 1 = 2 := by decide", "KILL"),
    ("rfl-term", "Type mismatch\n  rfl\nhas type\n  ?m.7 = ?m.7\nbut is expected to have type\n  f 3 = 5",
     "example : f 3 = 5 := rfl", "RFL"),
    ("rfl-tactic", "Tactic `rfl` failed: The left-hand side\n  f 3\nis not definitionally equal to the right-hand "
     "side\n  5", "theorem t : f 3 = 5 := by\n  rfl", "RFL"),
    ("rfl-under-guard-msgs", GUARD + "-\n+ error: Type mismatch\n+   rfl", "#guard_msgs in\nexample : f 3 = 5 := rfl",
     "RFL"),
    ("rfl-out-of-budget", "maximum recursion depth has been reached", "example : f 3 = 5 := rfl", "RFL"),
    ("parse-at-rfl", "unexpected token '<;>'; expected command", "example : f 3 = 5 := rfl", "UNKNOWN"),
    # The safe cases: each is UNKNOWN.
    ("rfl-shape-in-a-decide-check", "Type mismatch\n  rfl\nhas type", "example : f 3 = 5 := by decide", "UNKNOWN"),
    ("guard-expr-defeq", "Failed: `f 3` is not definitionally equal to `5`", "#guard_expr f 3 =~ 5", "UNKNOWN"),
    ("check-rfl", "Type mismatch\n  rfl\nhas type", "#check (rfl : f 3 = 5)", "UNKNOWN"),
    ("eval-throws", "changed", '#eval (do if f 3 != 5 then throw (IO.userError "changed") : IO Unit)', "UNKNOWN"),
    ("reduce-info-differs", GUARD + "- info: 0\n+ info: Acc.rec\n+   (fun x₁ h ih =>", "/-- info: 0 -/\n"
     "#guard_msgs in\n#reduce g 4", "UNKNOWN"),
    ("check-info-differs", GUARD + "- info: f 3 : Nat\n+ info: f 4 : Nat", "/-- info: f 3 : Nat -/\n#guard_msgs in\n"
     "#check f 3", "UNKNOWN"),
    ("eval-info-quotes-budget", GUARD + "- info: 3\n+ info: [Error pretty printing: maximum recursion depth has been "
     "reached", "/-- info: 3 -/\n#guard_msgs in\n#eval f 3", "UNKNOWN"),
    ("eval-budget-error", GUARD + "- info: 3\n+ error: maximum recursion depth has been reached",
     "/-- info: 3 -/\n#guard_msgs in\n#eval f 3", "UNKNOWN"),
    ("expected-budget-error", GUARD + "- error: maximum recursion depth has been reached\n+ info: 3",
     "/-- error: maximum recursion depth has been reached -/\n#guard_msgs in\n#eval f 3", "UNKNOWN"),
    ("eval-warning", GUARD + "- info: 3\n+ warning: declaration uses 'sorry'\n+ info: 3", "#guard_msgs in\n#eval f 3",
     "UNKNOWN"),
    ("no-diff", GUARD + "info: 4", "/-- info: 5 -/\n#guard_msgs in\n#eval f 3", "UNKNOWN"),
    ("refutation-with-more", "Tactic `decide` proved that the proposition\n  f 1 = 2\nis false\nNote: more",
     "example : f 1 = 2 := by decide", "UNKNOWN"),
    ("refutation-quoted", "note: Tactic `decide` proved that the proposition\n  f 1 = 2\nis false",
     "example : f 1 = 2 := by decide", "UNKNOWN"),
    ("decide-stuck", "Tactic `decide` failed for proposition\n  f 1 = 2\nbecause its `Decidable` instance\n"
     "  instDecidableEqNat (f 1) 2\ndid not reduce to `isTrue` or `isFalse`.", "example : f 1 = 2 := by decide",
     "UNKNOWN"),
    ("unsolved-goals", "unsolved goals\n⊢ False", "example : f 1 = 2 := by decide", "UNKNOWN"),
    ("unclassified", "something Lean 4.25 may say", "#guard f 1 == 2", "UNKNOWN"),
]


@pytest.mark.parametrize(("name", "message", "span", "verdict"), JUDGED, ids=[j[0] for j in JUDGED])
def test_a_check_kills_only_when_its_message_states_a_refutation(name, message, span, verdict):
    """Review F11 (the DRI's note 2026-10-19c, step 1): KILL needs a message that states a refutation (`REFUTED`,
    whole, or a `#guard_msgs` diff between refutations; no `info`: hunt Q4, Q7, Q8); an `rfl` check is RFL (its
    message is the same when the reduction got stuck); every other message is UNKNOWN, one test each."""
    import trust_mutants
    line = span.split("\n")[-1]
    assert trust_mutants.judge(message, "check", line, line, trust_mutants.code_only(span)) == verdict


DECIDE_FALSE = "Tactic `decide` proved that the proposition\n  f 3 = 5\nis false"


def test_settle_kills_only_when_every_error_is_a_checks_refutation_of_the_definition():
    """Review F8, F11 and hunt H4/H5 on `settle` alone (its builds faked): every error must be KILL, an `rfl` check's
    only when `decide` then refutes its statement, and each check must read the mutated definition."""
    import trust_mutants
    text = "#guard f 1 == 2\ndef s := ⟨0, by decide⟩\nexample : f 3 = 5 := rfl\n"
    roles = {"A.lean": [(1, 1, "check", None), (2, 2, "other", "s"), (3, 3, "check", None)]}
    rebuilt: list = []

    def settle(errors, reads=lambda key: None):
        def rebuild(now):
            assert now["A.lean"].split("\n")[2] == "example : f 3 = 5 := by decide"
            return rebuilt.pop()
        return trust_mutants.settle(errors, lambda f: text, lambda f: text, roles, rebuild, reads)
    assert settle([("A.lean", 1, REFUTE)]) == ("KILLED", f"lean/A.lean:1: {REFUTE.split(chr(10))[0]}")
    assert settle([("A.lean", 1, REFUTE), ("A.lean", 2, DECIDE_FALSE)])[0] == "UNKNOWN"  # F8: beside a definition
    assert settle([("A.lean", 2, DECIDE_FALSE), ("A.lean", 1, REFUTE)])[0] == "UNKNOWN"
    assert settle([("A.lean", 1, REFUTE)], reads=lambda key: "no" if key == ("A.lean", (1, 1)) else None) == (
        "UNKNOWN", f"lean/A.lean:1: {REFUTE.split(chr(10))[0]} (no)")  # hunt H4, H5, N1, N2
    rfl = ("A.lean", 3, "Type mismatch\n  rfl")
    for answer, verdict in (([("A.lean", 3, DECIDE_FALSE)], "KILLED"), ([], "UNKNOWN"), (None, "UNKNOWN"),
                            ([("A.lean", 3, "Tactic `decide` failed for proposition")], "UNKNOWN"),
                            ([("A.lean", 3, DECIDE_FALSE), ("A.lean", 2, "unsolved goals")], "UNKNOWN")):
        rebuilt.append(answer)
        assert settle([rfl])[0] == verdict, answer  # F11: a stuck or unanswered `rfl` refutes nothing
    rebuilt.append([("A.lean", 3, DECIDE_FALSE)])
    assert settle([rfl], reads=lambda key: "no")[0] == "UNKNOWN" and rebuilt


@pytest.mark.parametrize(("text", "first", "last", "after"), [
    ("example : f 3 = 5 := rfl\n#guard g\n", 1, 1, "example : f 3 = 5 := by decide\n#guard g\n"),
    ("#guard g\ntheorem t : f 3 = 5 := by\n  rfl -- c\n#guard h\n", 2, 3,
     "#guard g\ntheorem t : f 3 = 5 := by decide\n -- c\n#guard h\n"),
    ("#guard_msgs in\nexample : f 3 = 5 := rfl\n", 1, 2, "#guard_msgs in\nexample : f 3 = 5 := by decide\n"),
    ("example : f 3 = 5 := by decide\n", 1, 1, "example : f 3 = 5 := by decide\n")], ids=short)
def test_decided_rewrites_only_the_rfl_and_keeps_every_line(text, first, last, after):
    """Review F11: the follow-up asks `decide` of the `rfl` check's own statement, in place (hunt H7: never
    `native_decide`, which evaluates compiled code an `rfl` check does not read)."""
    import trust_mutants
    assert trust_mutants.decided(text, first, last) == after


DEFINITION = "def bS : {n : Nat // n + 0 = n} := ⟨3, by simp (config := { maxSteps := 9 })⟩ + (by exact 1)\n"
# Review F12, the rule inverted for INVALID: the message an error in the mutated declaration gives, whether it is
# inside a tactic block there, and the verdict. INVALID only when Lean refused the text; every other row is UNKNOWN.
REFUSALS = [
    ("parse", "unexpected token ']'; expected term", False, "INVALID"),
    ("parse-elsewhere", "unexpected token '<;>'; expected command", True, "UNKNOWN"),  # hunt R3
    ("unknown-identifier", "Unknown identifier `A`", False, "INVALID"),
    ("unknown-constant", "Unknown constant `VE.Cardinality.Body.all`", False, "INVALID"),
    ("invalid-field", "Invalid field `take`: The environment does not contain `Option.take`", False, "INVALID"),
    ("invalid-projection", "Invalid projection: Type of", False, "INVALID"),
    ("invalid-pattern", "Invalid pattern", False, "INVALID"),
    ("missing-cases", "Missing cases:\n(Nat.succ _)", False, "INVALID"),
    # The safe cases: each is UNKNOWN.
    ("simp-steps", "`simp` failed: maximum number of steps exceeded", True, "UNKNOWN"),
    ("unsolved-goals", "unsolved goals\n⊢ 4 + 0 = 4", True, "UNKNOWN"),
    ("omega", "omega could not prove the goal:", True, "UNKNOWN"),
    ("decide-stuck", "Tactic `decide` failed for proposition", True, "UNKNOWN"),
    ("decide-false", "Tactic `decide` proved that the proposition\n  4 = 3\nis false", True, "UNKNOWN"),
    ("name-in-tactic", "Unknown identifier `A`", True, "UNKNOWN"),
    ("type-mismatch", "Type mismatch\n  \"a\"\nhas type\n  String", False, "UNKNOWN"),
    ("rfl-stuck", "Application type mismatch: The argument\n  rfl\nhas type\n  ?m.10 = ?m.10", False, "UNKNOWN"),
    ("termination", "fail to show termination for\n  Demo.h3", False, "UNKNOWN"),
    # Hunt H2, H3: instance search fails alike on a missing instance and on its own size or heartbeat budget.
    ("synthesize", "failed to synthesize\n  LE Bool", False, "UNKNOWN"),
    ("synthesize-budget", "failed to synthesize\n  Small 79\n(deterministic) timeout at `typeclass`, maximum number "
     "of heartbeats (200) has been reached", False, "UNKNOWN"),
    ("implicit", "don't know how to synthesize implicit argument `α`", False, "UNKNOWN"),
    ("function-expected", "Function expected at\n  x", False, "UNKNOWN"),  # hunt N5: a coercion's search, out of size
    ("refusal-quoting-budget", "Invalid field `x`: maximum recursion depth has been reached", False, "UNKNOWN"),
    ("recursion", "maximum recursion depth has been reached", False, "UNKNOWN"),
    ("heartbeats", "(deterministic) timeout at `whnf`, maximum number of heartbeats (200000) has been reached",
     False, "UNKNOWN"),
    ("unclassified", "something Lean 4.25 may say", False, "UNKNOWN"),
]


@pytest.mark.parametrize(("name", "message", "inside", "verdict"), REFUSALS, ids=[r[0] for r in REFUSALS])
def test_invalid_only_when_lean_refuses_the_mutated_text(name, message, inside, verdict):
    """Review F12 (the DRI's note, step 1): an error in the mutated declaration is INVALID only when Lean refused its
    text (a parse error, or a name, field, pattern or instance error outside its tactic blocks); a tactic that
    fails, Lean's budget, a type mismatch (a false or stuck proof term gives one too) and anything else are
    UNKNOWN, which counts toward the exit code."""
    import trust_mutants
    assert ("INVALID" if trust_mutants.refused(message, inside) else "UNKNOWN") == verdict


@pytest.mark.parametrize(("errors", "verdict"), [
    ([("A.lean", 1, "Invalid field `take`", 32)], "INVALID"),
    ([("A.lean", 1, "Invalid field `take`", 32), ("A.lean", 1, "unsolved goals", 62)], "UNKNOWN"),
    ([("A.lean", 1, "unsolved goals", 62), ("A.lean", 1, "Invalid field `take`", 32)], "UNKNOWN"),
    ([("A.lean", 1, "Invalid field `take`", 62)], "UNKNOWN"),
    ([("A.lean", 1, "Invalid field `symm`", 44)], "UNKNOWN"),  # hunt Q9: outside the mutant's text
    ([("A.lean", 1, "unexpected token ')'; expected term", 34)], "INVALID"),
    ([("A.lean", 1, "unexpected token; expected command", 44)], "UNKNOWN"),  # hunt R3: the tool's padding
    ([("A.lean", 1, "Unknown identifier `x`", 62)], "UNKNOWN")],  # the edit itself inside a tactic block
    ids=("refusal", "beside-a-tactic", "after-a-tactic", "in-a-tactic", "outside-the-edit", "parse-in-the-edit",
         "parse-outside-the-edit", "edit-in-a-tactic"))
def test_invalid_needs_every_error_of_the_mutated_declaration_to_be_a_refusal(errors, verdict):
    """Review F12: a tactic or budget failure in the mutated declaration is UNKNOWN even beside a refusal (it may have
    caused one, or followed from it), a refusal inside a tactic block is a tactic's, and one outside the text the
    mutant wrote is a proof term's or another's (hunt Q9), a parse error there too (the tool's line padding: R3)."""
    import trust_mutants
    text = "def f (o : Option Nat) : Nat := (o.take 1).length + (by exact 0)\n"
    assert text[32] == "(" and text[62] == "0"
    edit = (62, 63) if errors[0][3] == 62 and "`x`" in errors[0][2] else (32, 42)  # `(o.take 1)`, or the `0`
    assert trust_mutants.invalid(errors, text, (1, 1), edit)[0] == verdict


def test_named_writes_each_check_as_a_declaration_of_what_it_states():
    """Hunt H4, H5, N1, N2, N8: `dependencies` asks Lean, at each check's own position (its section variables
    included), what its statement reads: `named` hands each check that can kill to `READS`'s elaborators, its
    wrapper and a command's docstring blanked."""
    import trust_mutants
    text = ("/-- info: 3 -/\n#guard_msgs in\n#eval f 3\n#guard f 3 == 3 -- c\n"
            "@[simp] theorem Demo.t : f 1 = 2 :=\n  by decide\nexample : f 1 = 2 := by simp\n#reduce f 3\n")
    roles = [(1, 3, "check", None), (4, 4, "check", None), (5, 6, "check", None), (7, 7, "proof", None),
             (8, 8, "check", None)]
    named, spans = trust_mutants.named(text, roles)
    assert named == ("/-- info: 3 -/\n#guard_msgs in\n#eval f 3\n#tm_trust_guard tmChk_4 f 3 == 3 -- c\n"
                     "@[simp] theorem Demo.t : f 1 = 2 := by tm_trust_probe tmChk_5; exact sorry\n\n"
                     "example : f 1 = 2 := by simp\n#reduce f 3\n")  # every line kept (hunt Q6)
    assert spans == {"tmChk_4": (4, 4), "tmChk_5": (5, 6)}  # an `#eval` prints no answer (hunt Q4, Q7, Q8)


@pytest.mark.parametrize(("token", "inside"), [("simp", True), ("maxSteps", True), ("⟨3", False), ("bS", False),
                                               ("+ (", False), ("exact", True), ("1)", True), ("n + 0", False)])
def test_in_tactic_reads_each_tactic_block_to_its_bracket(token, inside):
    """Review F12: a tactic block runs from its `by` to the end of the bracket group it is in."""
    import trust_mutants
    code = trust_mutants.code_only(DEFINITION)
    assert trust_mutants.in_tactic(code, DEFINITION.index(token), 0, len(DEFINITION)) is inside


# Review F9's axis: an operator whose replacement can span lines, with fewer, the same or more lines than what it
# replaces; each definition is followed by a tactic proof over three lines (cut up front in the mutated module: a
# cut at moved lines leaves `<;> trivial` behind) and then by its check. `arm-true`/`arm-false` write one token and
# the list cuts and `append-*` one line or fewer, so only `arm-default` has "more". "tight": no blank line follows the
# definition, so the longer replacement cannot keep the lines after it, and the mutant is UNKNOWN.
LINES = [  # (shape, the definition after its name, what the reading check compares, [(operator, before, lines)])
    ("default-more", " : Nat → List Nat\n  | 0 => [7]\n  | _ => [2,\n      3]", "({d} 0, {d} 1) == ([7], [2, 3])",
     [("arm-default", "[7]", "more")]),
    ("default-more-tight", " : Nat → List Nat\n  | 0 => [7]\n  | _ => [2,\n      3]",
     "({d} 0, {d} 1) == ([7], [2, 3])", [("arm-default", "[7]", "more")]),
    ("default-fewer", " : Nat → List Nat\n  | 0 => [7,\n      8]\n  | _ => [2]", "({d} 0, {d} 1) == ([7, 8], [2])",
     [("arm-default", "[7,\n      8]", "fewer")]),
    ("default-same", " : Nat → List Nat\n  | 0 => [7]\n  | _ => [2]", "({d} 0, {d} 1) == ([7], [2])",
     [("arm-default", "[7]", "same")]),
    ("arm-bool", " : Nat → Bool\n  | 0 => 1 <\n      2\n  | _ => 2 < 1", "{d} 0 && !{d} 1",
     [("arm-false", "1 <\n      2", "fewer"), ("arm-true", "2 < 1", "same")]),
    ("list-multi", " (n : Nat) : List Nat := [n,\n    5]", "({d} 0, {d} 1) == ([0, 5], [1, 5])",
     [("list-first", "[n,\n    5]", "same"), ("list-drop-last", "[n,\n    5]", "same"),
      ("list-empty", "[n,\n    5]", "fewer")]),
    ("list-single", " (n : Nat) : List Nat := [n, 5]", "({d} 0, {d} 1) == ([0, 5], [1, 5])",
     [("list-first", "[n, 5]", "same"), ("list-drop-last", "[n, 5]", "same"), ("list-empty", "[n, 5]", "same")]),
    ("append-left-multi", " (n : Nat) : List Nat := [n] ++ [5,\n    6]", "{d} 0 == [0, 5, 6]",
     [("append-left", " ++ [5,\n    6]", "fewer"), ("append-right", "[n] ++ ", "same")]),
    ("append-right-multi", " (n : Nat) : List Nat := [n,\n    5] ++ [6]", "{d} 0 == [0, 5, 6]",
     [("append-right", "[n,\n    5] ++ ", "fewer"), ("append-left", " ++ [6]", "same")]),
]


def lines_package(root: Path, folder: Path) -> list[dict]:
    """The axis as a Lean package at `root` (committed over an empty base): each shape read by a check that compares
    it and by one that reads nothing (`#guard true`), in the mutated module (Demo/LM/Defs.lean) and in another
    (Demo/LO/Checks.lean, its definitions and proofs in Demo/LO/Defs.lean)."""
    scaffold(root, "LM", "LO")
    texts = {"LM/Defs": ["namespace Demo.LM", ""], "LO/Defs": ["namespace Demo.LO", ""],
             "LO/Checks": ["import Demo.LO.Defs", "", "namespace Demo.LO", ""]}
    rows = []
    for setting, defs, checks in (("mutated", "LM/Defs", "LM/Defs"), ("other", "LO/Defs", "LO/Checks")):
        for shape, body, compares, targets in LINES:
            for reads in (True, False):
                d = f"s{len(rows)}"
                texts[defs] += [*f"def {d}{body}".split("\n"), *([""] if not shape.endswith("tight") else []),
                                f"theorem {d}_ok : True := by", "  skip", "  <;> trivial"]
                rows.append({"shape": shape, "setting": setting, "reads": reads, "d": d, "targets": targets,
                             "file": f"lean/Demo/{checks}.lean", "line": len(texts[checks]) + 1,
                             "space": f"Demo.{checks.split('/')[0]}"})
                texts[checks] += [f"#guard {compares.format(d=d)}" if reads else "#guard true", ""]
    for name, lines in texts.items():
        (root / f"lean/Demo/{name}.lean").write_text("\n".join([*lines, f"end Demo.{name.split('/')[0]}", ""]))
    dump(root, folder, [])
    git(root, "add", ".")
    git(root, "commit", "-qm", "head")
    return rows


@pytest.fixture(scope="module")
def lines_run(tmp_path_factory):
    root = tmp_path_factory.mktemp("lines")
    rows = lines_package(root, tmp_path_factory.mktemp("lines-dump"))
    done, mutants = tool(root, tmp_path_factory.mktemp("lines-run"), "--max-mutants", "100000")
    return rows, done, mutants


def lines_problems(rows: list[dict], mutants: list[dict]) -> list[tuple]:
    """The rows of the line axis whose mutants break its rule (the test's and sweep.py's one reading of it): a
    target's lines are those the axis names and its status is KILLED under the check that compares the value,
    SURVIVOR under the one that reads nothing, UNKNOWN when it is longer and no blank line can take its lines; every
    other mutant is KILLED only by the comparing check at its line, UNKNOWN only as such a target, else SURVIVOR or
    INVALID."""
    problems = []
    for row in rows:
        mine = [m for m in mutants if m["definition"] == f"{row['space']}.{row['d']}"]
        tight = row["shape"].endswith("tight")
        for operator, before, lines in row["targets"]:
            found = [m for m in mine if (m["operator"], m["before"]) == (operator, before)]
            if len(found) != 1:
                problems.append((row, operator, before, "not one mutant", found))
                continue
            m = found[0]
            change = m["after"].rstrip("\n").count("\n") - before.count("\n")
            expected = "UNKNOWN" if tight and lines == "more" else "KILLED" if row["reads"] else "SURVIVOR"
            if not {"fewer": change < 0, "same": change == 0, "more": change > 0}[lines] or m["status"] != expected:
                problems.append((row, m, f"expected {expected} with {lines} lines"))
        for m in mine:
            allowed = {"KILLED": row["reads"] and m["detail"].startswith(f"{row['file']}:{row['line']}: "),
                       "UNKNOWN": tight and m["operator"] == "arm-default" and "moves this line" in m["detail"],
                       "SURVIVOR": True, "INVALID": True}
            if not allowed.get(m["status"]):
                problems.append((row, m))
    return problems


def test_a_replacement_of_any_line_count_is_decided_by_the_checks(lines_run):
    """Review F9 (PROBE F9's form is the default-more row of the mutated module that no check reads): with fewer, the
    same or more lines, in the mutated module or another, a mutant is KILLED only by the check that compares the
    value, at that check's line; one no check reads survives; a longer replacement no blank line can take is
    UNKNOWN (`lines_problems`)."""
    rows, done, mutants = lines_run
    assert done.returncode in (0, 1) and mutants, done.stdout + done.stderr
    assert lines_problems(rows, mutants) == []


# Review F10: Lean's messages when it gives no answer, as Lean 4.24 prints them at a check (the budget ones
# end-to-end in `BUDGET`), and the refutations beside them, which still kill.
NO_ANSWERS = [
    "maximum recursion depth has been reached\nuse `set_option maxRecDepth <num>` to increase limit",
    "(deterministic) timeout at `whnf`, maximum number of heartbeats (1000) has been reached\n\nNote: Use `set_option "
    "maxHeartbeats <num>` to set the limit.",
    "[Error pretty printing: maximum recursion depth has been reached\nuse `set_option maxRecDepth <num>` to increase",
    "❌️ Docstring on `#guard_msgs` does not match generated message:\n\n- info: 3\n+ error: maximum recursion depth "
    "has been reached",
    "Tactic `decide` failed for proposition\n  bigS 3 = 0\nbecause its `Decidable` instance\n  instDecidableEqNat "
    "(bigS 3) 0\ndid not reduce to `isTrue` or `isFalse`.",
    "Tactic `decide` failed. Internal error: The elaborator is able to reduce the `Decidable` instance, but the "
    "kernel is not able to",
    "Tactic `native_decide` failed: Could not evaluate decidable instance. Error: stack overflow",
    "(kernel) deep recursion detected", "(kernel) deterministic timeout", "(kernel) interrupted"]
ANSWERS = ["Tactic `decide` proved that the proposition\n  bigF 3 = 3\nis false",
           "Tactic `native_decide` evaluated that the proposition\n  bigF 3 = 3\nis false",
           "Expression\n  f 1 == 2\ndid not evaluate to `true`"]


@pytest.mark.parametrize("message", NO_ANSWERS + ANSWERS, ids=short)
def test_a_check_that_gives_no_answer_never_kills(message):
    """Review F10: a check that runs out of budget, or whose decision procedure gets stuck, did not refute the
    mutant: `judge` refuses it at the check's own line (since F11 because no such message states a refutation)."""
    import trust_mutants
    line = "example : (List.replicate size true).length = size := by decide"
    span = "/-- info: 3 -/\n#guard_msgs in\n#eval f 3\n" if "#guard_msgs" in message else line
    assert trust_mutants.judge(message, "check", line, line, trust_mutants.code_only(span)) == (
        "KILL" if message in ANSWERS else "UNKNOWN")
    assert trust_mutants.brief(message).startswith("no answer: ") is (message not in ANSWERS)


def test_an_error_is_read_with_its_whole_message():
    """Review F10: `ERROR` reads each located error to the next line Lake or Lean starts, so a `#guard_msgs` that
    quotes a budget error on a later line, or a message with blank lines, is read whole (Lake's output, verbatim)."""
    import trust_mutants
    output = ("✖ [2/2] Building Demo.A (5.4s)\ntrace: .> LEAN_PATH=x lean Demo/A.lean\n"
              "error: Demo/A.lean:6:61: maximum recursion depth has been reached\nuse `set_option maxRecDepth <num>` "
              "to increase limit\nerror: Demo/A.lean:11:0: ❌️ Docstring on `#guard_msgs` does not match generated "
              "message:\n\n- info: 100000\n+ error: maximum recursion depth has been reached\n"
              "error: ./Demo/A.lean:15:61: (deterministic) timeout at `whnf`, maximum number of heartbeats (1000) has "
              "been reached\n\nNote: Use `set_option maxHeartbeats <num>` to set the limit.\n\n"
              "warning: Demo/B.lean:2:0: declaration uses 'sorry'\n"
              "error: Demo/A.lean:18:27: Tactic `decide` proved that the proposition\n  bigF 3 = 3\nis false\n"
              "error: Lean exited with code 1\nSome required targets logged failures:\n- Demo.A\nerror: build failed\n")
    found = trust_mutants.located(output)
    assert [(f, n, c) for f, n, c, _ in found] == [("Demo/A.lean", 6, 61), ("Demo/A.lean", 11, 0),
                                                   ("Demo/A.lean", 15, 61), ("Demo/A.lean", 18, 27)]
    assert found[1][3].endswith("+ error: maximum recursion depth has been reached")
    assert found[2][3].endswith("to set the limit.") and found[3][3].endswith("is false")
    assert [bool(trust_mutants.NO_ANSWER.search(m)) for *_, m in found] == [True, True, True, False]


def test_an_outside_files_errors_are_read_with_their_whole_message():
    """Review F11: `lake env lean` writes `<file>:<line>:<column>: error: …` (verbatim below); `LEAN_ERROR` reads each
    whole, to the next message Lean starts, info and diff lines included in theirs."""
    import trust_mutants
    output = ("/t/T.lean:2:29: error: Tactic `decide` proved that the proposition\n  Demo.k 3 = 5\nis false\n"
              "/t/T.lean:3:0: info: 4\n/t/T.lean:4:0: error: ❌️ Docstring on `#guard_msgs` does not match generated "
              "message:\n\n-\n+ error: Expression\n+   Demo.k 3 == 5\n+ did not evaluate to `true`\n"
              "/t/T.lean:6:26: error: Type mismatch\n  rfl\nhas type\n  ?m.7 = ?m.7\n")
    found = trust_mutants.located(output, trust_mutants.LEAN_ERROR)
    assert [(f, n, c) for f, n, c, _ in found] == [("/t/T.lean", 2, 29), ("/t/T.lean", 4, 0), ("/t/T.lean", 6, 26)]
    assert found[0][3].endswith("is false") and found[1][3].endswith("did not evaluate to `true`")
    assert trust_mutants.refutes(found[1][3], "guard") and found[2][3].endswith("?m.7 = ?m.7")


# Review F10's package: each definition is `if n ≤ 3 then n else 100000`, read at 3 by a check that holds for every
# value (and so cannot catch a mutant) but that Lean cannot finish at 100000 (`le-lt` and `lit-minus` of the 3 send
# it there): the mutant must never be KILLED. `refuted` is the same definition read by a check that does catch it.
# `size` is PROBE F10's form (124 passes, 125 hits the recursion limit on Lean 4.24).
BUDGET = [  # (definition, the check(s) after it; {d} is the definition, `in` says where the check is)
    ("decide", "example : (List.replicate ({d} 3) true).length = {d} 3 := by decide"),
    ("rfl", "example : (List.replicate ({d} 3) true).length = {d} 3 := rfl"),
    ("reduce", "#reduce (List.replicate ({d} 3) true).length"),
    ("guard-msgs", "/-- info: 3 -/\n#guard_msgs in\n#reduce (List.replicate ({d} 3) true).length"),
    ("heartbeats", "set_option maxRecDepth 100000 in\nset_option maxHeartbeats 1000 in\n"
                   "example : (List.replicate ({d} 3) true).length = {d} 3 := by decide"),
    ("kernel", "example : (List.replicate ({d} 3) true).length = {d} 3 := by decide +kernel"),
    ("stuck", "example : {d} 3 = {d} 3 + 0 := by decide"),
    ("in-definition", "def {d}Fin : Fin 5 := ⟨(List.replicate ({d} 3) true).length, by decide⟩"),
    ("outside", None),
    ("refuted", "example : {d} 3 = 3 := by decide"),
    ("refuted-outside", None)]


def budget_package(root: Path, folder: Path) -> None:
    scaffold(root, "")
    (root / "lean/Demo/Wf.lean").write_text(  # in the base: well-founded, so `decide` cannot unfold it
        "namespace Demo\n\ndef wf (n : Nat) : Nat := if _ : n = 0 then 0 else wf (n - 1)\ntermination_by n\n\n"
        "end Demo\n")
    git(root, "add", ".")
    git(root, "commit", "-qm", "wf")
    text = ["import Demo.Wf\n\nnamespace Demo\n\ndef size : Nat := 124\n\n"
            "example : (List.replicate size true).length = size := by decide\n"]
    for name, check in BUDGET:
        d = "b" + name.title().replace("-", "")
        text.append(f"\ndef {d} (n : Nat) : Nat := if n ≤ 3 then n else {'wf 1' if name == 'stuck' else '100000'}\n\n"
                    + (check.replace("{d}", d) + "\n" if check else ""))
    (root / "lean/Demo/Defs.lean").write_text("".join(text) + "\nend Demo\n")
    (root / "outside").mkdir()
    (root / "outside/Budget.lean").write_text(
        "import Demo.Defs\nexample : (List.replicate (Demo.bOutside 3) true).length = Demo.bOutside 3 := by decide\n")
    (root / "outside/Refute.lean").write_text("import Demo.Defs\nexample : Demo.bRefutedOutside 3 = 3 := by decide\n")
    dump(root, folder, [])
    git(root, "add", ".")
    git(root, "commit", "-qm", "head")


@pytest.fixture(scope="module")
def budget_run(tmp_path_factory):
    root = tmp_path_factory.mktemp("budget")
    budget_package(root, tmp_path_factory.mktemp("budget-dump"))
    return tool(root, tmp_path_factory.mktemp("budget-run"), "--max-mutants", "1000", "--test", "outside/Budget.lean",
                "--test", "outside/Refute.lean")


def test_probe_f10_a_check_out_of_budget_is_no_kill(budget_run):
    """PROBE F10: `size` 124 -> 125 sends the `decide` check over Lean's recursion limit; it holds for every `size`,
    so no mutant of `size` is KILLED."""
    done, mutants = budget_run
    size = of(mutants, "size")
    assert size and not [m for m in size if m["status"] == "KILLED"], done.stdout + done.stderr


@pytest.mark.parametrize(("name", "check"), BUDGET, ids=[b[0] for b in BUDGET])
def test_a_check_out_of_budget_or_stuck_is_unknown(budget_run, name, check):
    """Review F10, every way Lean gives no answer at a check: the mutants that send it to 100000 (`le-lt`, `lit-minus`
    of the 3) are UNKNOWN with "no answer", never KILLED (nor INVALID, when it is inside the mutated definition's own
    proof), the others SURVIVOR; the refuting checks still kill them, inside lean/ and in a --test file."""
    done, mutants = budget_run
    mine = {(m["operator"], m["before"]): m for m in of(mutants, "b" + name.title().replace("-", ""))}
    far = {("le-lt", "≤"), ("lit-minus", "3")}
    assert far <= set(mine), (sorted(mine), done.stdout + done.stderr)
    for key, m in mine.items():
        if name.startswith("refuted"):
            expected = ("KILLED", "proved that") if key in far else ("SURVIVOR", "")
        else:
            expected = ("UNKNOWN", "no answer") if key in far else ("SURVIVOR", "")
        assert m["status"] == expected[0] and expected[1] in m["detail"], m
    if name == "in-definition":  # the Fin's own mutant 3 -> 4: Lean runs out of budget inside it, never INVALID
        own = [m for m in of(mutants, "bInDefinitionFin") if (m["operator"], m["before"]) == ("lit-plus", "3")]
        assert [(m["status"], "no answer" in m["detail"]) for m in own] == [("UNKNOWN", True)], own


# Review F11 and F12's package (the DRI's note 2026-10-19c): each definition is `if n ≤ 3 then n else <far>`, read at
# 3 by the check after it; `le-lt` and `lit-minus` of the 3 send it to <far>. `wf` (well-founded, in the base) is a
# value no reduction unfolds: `wf 1` is 0, so `n + wf 1` is the same value as `n` (the check holds for the mutant)
# and `wf 1` alone a different one; `100` is a different one any reduction reaches. The far mutants must be the
# row's verdict, every other mutant SURVIVOR. Before the fix every UNKNOWN row but `eval-throws`'s value was KILLED.
STUCK = [  # (row, <far>, the check after the definition ({d} is the definition), the far mutants' verdict, detail)
    ("rfl", "wf 1", "example : {d} 3 + 0 = 0 + {d} 3 := rfl", "UNKNOWN", "does not refute"),  # PROBE F11
    ("by-rfl", "wf 1", "theorem {d}_t : {d} 3 + 0 = 0 + {d} 3 := by rfl", "UNKNOWN", "does not refute"),
    ("rfl-equal", "n + wf 1", "example : {d} 3 = 3 := rfl", "UNKNOWN", "does not refute"),
    ("rfl-decide", "100", "example : {d} 3 = 3 := rfl", "KILLED", "(`decide`: Tactic `decide` proved"),
    # Hunt H7: `native_decide` would evaluate compiled code, which an `rfl` check never reads, so only `decide` asks.
    ("rfl-native", "wf 1", "example : {d} 3 = 3 := rfl", "UNKNOWN", "does not refute"),
    ("rfl-wrapped", "100", "#guard_msgs in\nexample : {d} 3 = 3 := rfl", "KILLED", "(`decide`:"),
    ("guard-expr", "n + wf 1", "#guard_expr {d} 3 =~ 3", "UNKNOWN", "Failed:"),
    ("reduce-doc", "n + wf 1", "/-- info: 3 -/\n#guard_msgs in\n#reduce {d} 3", "UNKNOWN", "Docstring"),
    ("eval-doc", "n + wf 1", "/-- info: 3 -/\n#guard_msgs in\n#eval {d} 3", "SURVIVOR", ""),
    ("eval-doc-refuted", "wf 1", "/-- info: 3 -/\n#guard_msgs in\n#eval {d} 3", "UNKNOWN", "Docstring"),  # Q8
    ("check-rfl", "100", "#check (rfl : {d} 3 = 3)", "UNKNOWN", "Type mismatch"),
    ("eval-throws", "100", '#eval (do if {d} 3 != 3 then throw (IO.userError "changed") : IO Unit)', "UNKNOWN",
     "changed"),
    ("rfl-in-definition", "100", "def {d}Sub : {x : Nat // x = 3} := ⟨{d} 3, rfl⟩", "UNKNOWN", "mismatch"),
    ("outside-decide", "100", None, "KILLED", "(`decide`: Tactic `decide` proved"),
    ("outside-equal", "n + wf 1", None, "UNKNOWN", "does not refute"),
]
F12_FORM = "def {d} : {n : Nat // n + 0 = n} := ⟨3, by simp (config := { maxSteps := 9 })⟩"  # PROBE F12
# The forms the adversarial hunt found (the DRI's note, step 2): (row, the text, the definition whose mutants must
# have none of the statuses). H1: `decide` reads the goal, not the hypothesis the mutant falsifies; H4: the instance
# rests on a theorem the tool cut, so `decide` computes through the mutated definition although `HSmallP 2` does not
# read it; H5: a cut `@[csimp]` lemma sends the compiled `hRef` through the mutated `hImpl`; H2: instance search
# stops at its size budget (128), which is no refusal of the text.
HUNT = [
    ("H1", "def hHyp (n : Nat) : Nat := n + 1\n\nexample (_h : hHyp 0 = 1) : hHyp 1 = 2 := by decide", "hHyp",
     {"KILLED"}),
    ("H1r", "def hHypRfl (n : Nat) : Nat := n + 1\n\nexample (_h : hHypRfl 0 = 1) : hHypRfl 1 = 2 := rfl", "hHypRfl",
     {"KILLED"}),
    ("H4", "def hFast (n : Nat) : Bool := n < 3\n\ntheorem hFast_iff (n : Nat) : hFast n = true ↔ n < 3 := by\n"
     "  simp [hFast]\n\ndef HSmallP (n : Nat) : Prop := n < 3\n\ninstance (n : Nat) : Decidable (HSmallP n) := "
     "decidable_of_iff _ (hFast_iff n)\n\nexample : HSmallP 2 := by decide", "hFast", {"KILLED"}),
    ("H5", "def hRef (n : Nat) : Nat := 2 * n\n\ndef hImpl (n : Nat) : Nat := n <<< 1\n\n@[csimp] theorem hRef_eq : "
     "@hRef = @hImpl := by\n  funext n\n  simp [hRef, hImpl, Nat.shiftLeft_eq]\n  omega\n\n#guard hRef 3 == 6", "hImpl",
     {"KILLED"}),
    ("H2", "class HSize (n : Nat) where\n  val : Nat\n\ninstance : HSize 0 := ⟨0⟩\n\ninstance [s : HSize n] : "
     "HSize (n + 1) := ⟨s.val + 1⟩\n\ndef hSize : Nat := HSize.val 127\n\n#guard hSize == 127", "hSize", {"INVALID"}),
    # The second hunt. N1, N1g: the statement names the mutated definition in a tautology, and `decide` (or the
    # compiled `#guard`) still computes through the instance on the cut theorem; N2: the same with the cut `@[csimp]`
    # lemma; N3 (in Demo/Meta.lean): an `#eval` that prints the definition's text; N5: a coercion's instance search
    # out of its size budget says "Function expected"; N7: a second command on the check's line; N8: a section
    # `variable` hypothesis; N10: another command on the mutated declaration's last line.
    ("N1", "def nFast (n : Nat) : Bool := n < 3\n\ntheorem nFast_iff (n : Nat) : nFast n = true ↔ n < 3 := by\n"
     "  simp [nFast]\n\ndef NSmallP (n : Nat) : Prop := n < 3\n\ninstance (n : Nat) : Decidable (NSmallP n) := "
     "decidable_of_iff _ (nFast_iff n)\n\nexample : nFast 7 = nFast 7 ∧ NSmallP 2 := by decide", "nFast", {"KILLED"}),
    ("N1g", "def nFastG (n : Nat) : Bool := n < 3\n\ntheorem nFastG_iff (n : Nat) : nFastG n = true ↔ n < 3 := by\n"
     "  simp [nFastG]\n\ndef NSmallG (n : Nat) : Prop := n < 3\n\ninstance (n : Nat) : Decidable (NSmallG n) := "
     "decidable_of_iff _ (nFastG_iff n)\n\n#guard nFastG 7 == nFastG 7 && decide (NSmallG 2)", "nFastG", {"KILLED"}),
    ("N2", "def nRef (n : Nat) : Nat := 2 * n\n\ndef nImpl (n : Nat) : Nat := n <<< 1\n\n@[csimp] theorem nRef_eq : "
     "@nRef = @nImpl := by\n  funext n\n  simp [nRef, nImpl, Nat.shiftLeft_eq]\n  omega\n\n"
     "#guard nImpl 0 == nImpl 0 && nRef 3 == 6", "nImpl", {"KILLED"}),
    ("N3", None, "nZ", {"KILLED"}),
    ("N5", "class NSize (n : Nat) where\n  val : Nat\n\ninstance : NSize 0 := ⟨0⟩\n\ninstance [s : NSize n] : "
     "NSize (n + 1) := ⟨s.val + 1⟩\n\nstructure NW (n : Nat) where\n  k : Nat\n\ninstance [NSize n] : CoeFun (NW n) "
     "(fun _ => Nat → Nat) := ⟨fun w m => w.k + m + NSize.val n⟩\n\ndef nG (x : NW 126) : Nat := x 1\n\n"
     "#guard nG ⟨0⟩ == 127", "nG", {"INVALID"}),
    ("N7", "def nTwo (n : Nat) : Nat := n + 1\n\nexample : nTwo 5 = nTwo 5 := rfl  example (_h : nTwo 0 = 1) : "
     "nTwo 1 = 2 := by decide", "nTwo", {"KILLED"}),
    ("N8", "def nVar (n : Nat) : Nat := n + 1\n\nsection\n\nvariable (_h : nVar 0 = 1)\n\nexample : nVar 1 = 2 := "
     "by decide\n\nend", "nVar", {"KILLED"}),
    ("N10", "def NT (n : Nat) : Type := if n = 2 then Nat → Nat else Nat\n\ndef nD : Nat := 2  example (x : NT nD) : "
     "Nat := x 1", "nD", {"INVALID"}),
    # The third hunt: the bridge on a cut proof reached otherwise. P1: a private theorem; P2: an instance typed by
    # an abbreviation of `Decidable`; P3: `attribute [csimp]` on its own line; P4 (in Demo/Meta.lean): reflection
    # through the MetaM API; P5 (the instance in Demo/Inst.lean): a theorem that only passes a cut one on; P7: the
    # theorem as a class's proof field; P8: the mutant changes which instance Lean picks; P9: an `#eval!` of a Prop.
    ("P1", "def pFast (n : Nat) : Bool := n < 3\n\nprivate theorem pFast_iff (n : Nat) : pFast n = true ↔ n < 3 := by\n"
     "  simp [pFast]\n\ndef PSmall (n : Nat) : Prop := n < 3\n\ninstance (n : Nat) : Decidable (PSmall n) := "
     "decidable_of_iff _ (pFast_iff n)\n\n#guard pFast 7 == pFast 7 && decide (PSmall 2)", "pFast", {"KILLED"}),
    ("P2", "structure PVer where\n  v : Nat\n\ndef pFastLe (a b : PVer) : Bool := a.v ≤ b.v\n\ntheorem pFastLe_iff "
     "(a b : PVer) : pFastLe a b = true ↔ a.v ≤ b.v := by\n  simp [pFastLe]\n\ninstance : LE PVer := ⟨fun a b => "
     "a.v ≤ b.v⟩\n\ninstance : DecidableLE PVer := fun a b => decidable_of_iff _ (pFastLe_iff a b)\n\n"
     "#guard (⟨2⟩ : PVer) ≤ ⟨3⟩", "pFastLe", {"KILLED"}),
    ("P3", "def pRef (n : Nat) : Nat := 2 * n\n\ndef pImpl (n : Nat) : Nat := n <<< 1\n\ntheorem pRef_eq : @pRef = "
     "@pImpl := by\n  funext n\n  simp [pRef, pImpl, Nat.shiftLeft_eq]\n  omega\n\nattribute [csimp] pRef_eq\n\n"
     "#guard pImpl 0 == pImpl 0 && pRef 3 == 6", "pImpl", {"KILLED"}),
    ("P4", None, "pZ", {"KILLED"}),
    ("P5", "def pFast5 (n : Nat) : Bool := n < 3\n\ntheorem pFast5_iff (n : Nat) : pFast5 n = true ↔ n < 3 := by\n"
     "  simp [pFast5]", "pFast5", {"KILLED"}),
    ("P7", "class POrdered (α : Type) where\n  le : α → α → Prop\n  leb : α → α → Bool\n  leb_iff : ∀ a b, leb a b = "
     "true ↔ le a b\n\ninstance [POrdered α] (a b : α) : Decidable (POrdered.le a b) := decidable_of_iff _ "
     "(POrdered.leb_iff a b)\n\ndef pFastLeN (a b : Nat) : Bool := a ≤ b\n\ntheorem pFastLeN_iff (a b : Nat) : "
     "pFastLeN a b = true ↔ a ≤ b := by\n  simp [pFastLeN]\n\ninstance : POrdered Nat := ⟨(· ≤ ·), pFastLeN, "
     "pFastLeN_iff⟩\n\n#guard POrdered.le 2 3", "pFastLeN", {"KILLED"}),
    ("P8", "abbrev pK : Nat := 3\n\ndef PSmallK (n : Nat) : Prop := n ≤ 3\n\ninstance (n : Nat) : Decidable (PSmallK n) "
     ":= Nat.decLe n 3\n\ntheorem pSmall_K : (pK == 3) = true ↔ PSmallK pK := by simp [pK, PSmallK]\n\ninstance : "
     "Decidable (PSmallK pK) := decidable_of_iff _ pSmall_K\n\n#guard pK == pK && decide (PSmallK 2)", "pK",
     {"KILLED"}),
    ("P9", "def pFast9 (n : Nat) : Bool := n < 3\n\ntheorem pFast9_iff (n : Nat) : pFast9 n = true ↔ n < 3 := by\n"
     "  simp [pFast9]\n\ndef PSmall9 (n : Nat) : Prop := n < 3\n\ninstance (n : Nat) : Decidable (PSmall9 n) := "
     "decidable_of_iff _ (pFast9_iff n)\n\n/-- info: true -/\n#guard_msgs in\n#eval! pFast9 7 = pFast9 7 ∧ PSmall9 2",
     "pFast9", {"KILLED"}),
    # The fourth hunt. Q1-Q3: the cut proof passed explicitly to `decidable_of_iff`, inside a definition, behind an
    # `opaque`; Q4, Q8: an `#eval`'s output, formatted by an instance Lean picks after elaboration (one on a cut
    # proof, one out of its size budget); Q5 (Demo/Q5Defs.lean, Demo/Q5Inst.lean): `native_decide` through a cut
    # `@[csimp]` lemma of what the synthesized instance reads; Q6, Q7, Q12 (Demo/Src6.lean, Src7.lean, Src12.lean):
    # a check that reads the source text; Q9: a proof term the mutant broke outside its own text; Q10: an instance
    # search out of budget picks another instance silently.
    ("Q1", "def qFast1 (n : Nat) : Bool := n < 3\n\ntheorem qFast1_iff (n : Nat) : qFast1 n = true ↔ n < 3 := by\n"
     "  simp [qFast1]\n\ndef QSmall1 (n : Nat) : Prop := n < 3\n\n#guard qFast1 7 == qFast1 7 && @decide (QSmall1 2) "
     "(decidable_of_iff _ (qFast1_iff 2))", "qFast1", {"KILLED"}),
    ("Q2", "def qFast2 (n : Nat) : Bool := n < 3\n\ntheorem qFast2_iff (n : Nat) : qFast2 n = true ↔ n < 3 := by\n"
     "  simp [qFast2]\n\ndef QSmall2 (n : Nat) : Prop := n < 3\n\ndef qIsSmall2 (n : Nat) : Bool := @decide "
     "(QSmall2 n) (decidable_of_iff _ (qFast2_iff n))\n\n#guard qFast2 7 == qFast2 7 && qIsSmall2 2", "qFast2",
     {"KILLED"}),
    ("Q3", "def qFast3 (n : Nat) : Bool := n < 3\n\ntheorem qFast3_iff (n : Nat) : qFast3 n = true ↔ n < 3 := by\n"
     "  simp [qFast3]\n\ndef QSmall3 (n : Nat) : Prop := n < 3\n\nopaque qSmallDec3 (n : Nat) : Decidable (QSmall3 n) "
     ":= decidable_of_iff _ (qFast3_iff n)\n\n#guard qFast3 7 == qFast3 7 && @decide (QSmall3 2) (qSmallDec3 2)",
     "qFast3", {"KILLED"}),
    ("Q4", "def qFast4 (n : Nat) : Bool := n < 3\n\ntheorem qFast4_iff (n : Nat) : qFast4 n = true ↔ n < 3 := by\n"
     "  simp [qFast4]\n\ndef QSmall4 (n : Nat) : Prop := n < 3\n\ninstance (n : Nat) : Decidable (QSmall4 n) := "
     "decidable_of_iff _ (qFast4_iff n)\n\nstructure QVer4 where\n  v : Nat\n\ninstance : Repr QVer4 := ⟨fun x _ => "
     "if QSmall4 x.v then \"small\" else \"big\"⟩\n\n/-- info: (true, small) -/\n#guard_msgs in\n#eval! (qFast4 7 == "
     "qFast4 7, (⟨2⟩ : QVer4))", "qFast4", {"KILLED"}),
    ("Q5", None, "qImpl5", {"KILLED"}),
    ("Q6", None, "qRef6", {"KILLED"}),
    ("Q7", None, "qRef7", {"KILLED"}),
    ("Q8", "class QSize8 (n : Nat) where\n  val : Nat\n\ninstance : QSize8 0 := ⟨0⟩\n\ninstance [s : QSize8 n] : "
     "QSize8 (n + 1) := ⟨s.val + 1⟩\n\nstructure QW8 (n : Nat) where\n  k : Nat\n\ninstance [QSize8 n] : Repr (QW8 n) "
     ":= ⟨fun _ _ => \"w\"⟩\n\nabbrev qG8 : Nat := 126\n\n/-- info: w -/\n#guard_msgs in\n#eval (⟨0⟩ : QW8 qG8)", "qG8",
     {"KILLED"}),
    ("Q9", "def qPick (n : Nat) (h : n = 3) : Fin 4 := ⟨n, h.symm ▸ Nat.lt_succ_self 3⟩\n\n#guard (qPick 3 rfl).val == 3",
     "qPick", {"INVALID"}),
    ("Q10", "class QSize10 (n : Nat) where\n  val : Nat\n\ninstance : QSize10 0 := ⟨0⟩\n\ninstance [s : QSize10 n] : "
     "QSize10 (n + 1) := ⟨s.val + 1⟩\n\nstructure QW10 (n : Nat) where\n  k : Nat\n\ninstance (priority := low) "
     "qFallback10 : BEq (QW10 n) := ⟨fun _ _ => false⟩\n\ninstance qSmall10 [QSize10 n] : BEq (QW10 n) := ⟨fun _ _ => "
     "true⟩\n\nabbrev qG10 : Nat := 126\n\n#guard (⟨0⟩ : QW10 qG10) == ⟨0⟩", "qG10", {"KILLED"}),
    ("Q12", None, "qRef12", {"KILLED"}),
    # The fifth hunt. R1: a `partial def`'s compiled body (`_unsafe_rec`) through the cut proof; R2: an
    # `implemented_by` that reads the source file (`unsafeIO`); R3: the tool's own line padding makes a parse error
    # below the mutant's text; R5: a package's `leanOptions` decide which instance Lean picks (the probe elaborates as
    # the build does); R6: an `initialize`d value; R7: a `#guard_msgs` diff between two printings of one refutation (an
    # unexpander reads the mutated definition); R8: `include_str` in a definition the check reads.
    ("R1", "def rFast1 (n : Nat) : Bool := n < 3\n\ntheorem rFast1_iff (n : Nat) : rFast1 n = true ↔ n < "
     "3 := by\n  simp [rFast1]\n\ndef RSmall1 (n : Nat) : Prop := n < 3\n\ninstance (n : Nat) : Decidable "
     "(RSmall1 n) := decidable_of_iff _ (rFast1_iff n)\n\npartial def rLoop1 (n : Nat) : Bool := if "
     "n > 100 then rLoop1 (n - 1) else decide (RSmall1 n)\n\n#guard rFast1 7 == rFast1 7 && rLoop1 "
     "2", "rFast1", {"KILLED"}),
    ("R2", None, "rRef2", {"KILLED"}),
    ("R3", "def rG3 (xs : List Nat) (k : Nat := 0) : List Nat := xs ++ [k]\n\ndef rPick3 (n : Nat) : List "
     "Nat := by\n  exact rG3 [n,\n    3] 5\n\n#guard rPick3 2 == [2, 3, 5]", "rPick3", {"INVALID"}),
    ("R5", "class RDeep5 (n : Nat) where\n  val : Nat\n\ninstance : RDeep5 0 := ⟨0⟩\n\ninstance [s : RDeep5 "
     "n] : RDeep5 (n + 1) := ⟨s.val + 1⟩\n\ndef rFast5 (n : Nat) : Bool := n < 3\n\ntheorem rFast5_iff "
     "(n : Nat) : rFast5 n = true ↔ n < 3 := by\n  simp [rFast5]\n\ndef RSmall5 (n : Nat) : Prop := "
     "n < 3\n\ninstance (priority := low) rSlow5 (n : Nat) : Decidable (RSmall5 n) := Nat.decLt n 3\n"
     "\ninstance rFastDec5 (n : Nat) [RDeep5 130] : Decidable (RSmall5 n) := decidable_of_iff _ (rFast5_iff "
     "n)\n\n#guard rFast5 7 == rFast5 7 && decide (RSmall5 2)", "rFast5", {"KILLED"}),
    ("R6", None, "rFast6", {"KILLED"}),
    ("R7", None, "rTag7", {"KILLED"}),
    ("R8", None, "rRef8", {"KILLED"}),
    # The sixth hunt. S1, S2: a definition named under the mutated one (`g.same`, a structure's `Limits.same`) is
    # compared too; S3: one first reached through the mutated definition is compared where reached otherwise; S5: IO
    # without the `unsafe*IO` names; S6 (a required package): IO in a dependency; S7: a check's `#eval` printing a
    # probe line; S8: a library's `leanOptions` (its roots named); S9: a `local` `@[csimp]` lemma.
    ("S1", "class SSize1 (n : Nat) where\n  val : Nat\n\ninstance : SSize1 0 := ⟨0⟩\n\ninstance [s : SSize1 "
     "n] : SSize1 (n + 1) := ⟨s.val + 1⟩\n\nstructure SW1 (n : Nat) where\n  k : Nat\n\ninstance (priority "
     ":= low) sFallback1 : BEq (SW1 n) := ⟨fun _ _ => false⟩\n\ninstance sSmall1 [SSize1 n] : BEq (SW1 "
     "n) := ⟨fun _ _ => true⟩\n\nabbrev sG1 : Nat := 126\n\ndef sG1.same : Bool := (⟨0⟩ : SW1 sG1) == "
     "⟨0⟩\n\n#guard sG1.same", "sG1", {"KILLED"}),
    ("S2", "class SSize2 (n : Nat) where\n  val : Nat\n\ninstance : SSize2 0 := ⟨0⟩\n\ninstance [s : SSize2 "
     "n] : SSize2 (n + 1) := ⟨s.val + 1⟩\n\nstructure SW2 (n : Nat) where\n  k : Nat\n\ninstance (priority "
     ":= low) sFallback2 : BEq (SW2 n) := ⟨fun _ _ => false⟩\n\ninstance sSmall2 [SSize2 n] : BEq (SW2 "
     "n) := ⟨fun _ _ => true⟩\n\nstructure SLimits2 where\n  depth : Nat := 126\n\ndef SLimits2.same : "
     "Bool := (⟨0⟩ : SW2 ({} : SLimits2).depth) == ⟨0⟩\n\n#guard SLimits2.same", "SLimits2", {"KILLED"}),
    ("S3", None, "sRef3", {"KILLED"}),
    ("S5", None, "sRef5", {"KILLED"}),
    ("S6", None, "sRef6", {"KILLED"}),
    ("S7", None, "sRef7", {"KILLED"}),
    ("S8", None, "sFast8", {"KILLED"}),
    ("S9", "def sRef9 (n : Nat) : Nat := 2 * n\n\ndef sImpl9 (n : Nat) : Nat := n <<< 1\n\ntheorem sRef9_eq "
     ": @sRef9 = @sImpl9 := by\n  funext n\n  simp [sRef9, sImpl9, Nat.shiftLeft_eq]\n  omega\n\nsection\n"
     "\nattribute [local csimp] sRef9_eq\n\ndef sH9 (n : Nat) : Nat := sRef9 n\n\nend\n\n#guard sH9 3 == "
     "6", "sImpl9", {"KILLED"}),
    # The seventh hunt. T1: an `axiom` in place of a proof; T2: a `@[csimp]` lemma for a core function; T3: source
    # text read only through the mutated definition (its `lt-le` wrote the `≤` it reads); T5: a `partial def`'s
    # `_unsafe_rec` named under the mutated structure (owned by its own declaration: Lean's declaration ranges).
    ("T1", "def tFast1 (n : Nat) : Bool := n < 3\n\naxiom tFast1_iff (n : Nat) : tFast1 n = true ↔ n < 3\n"
     "\ndef TSmall1 (n : Nat) : Prop := n < 3\n\ninstance (n : Nat) : Decidable (TSmall1 n) := decidable_of_iff "
     "_ (tFast1_iff n)\n\nexample : TSmall1 2 := by decide", "tFast1", {"KILLED"}),
    ("T2", "def tMax2 (n m : Nat) : Nat := if n ≤ m then m else n\n\ntheorem tMax2_eq : @Nat.max = @tMax2 "
     ":= by\n  funext n m\n  rfl\n\nattribute [csimp] tMax2_eq\n\nexample : Nat.max 2 3 = 3 := by native_decide", "tMax2", {"KILLED"}),
    ("T3", None, "tRef3", {"KILLED:lt-le"}),
    ("T5", "class TSize5 (n : Nat) where\n  val : Nat\n\ninstance : TSize5 0 := ⟨0⟩\n\ninstance [s : TSize5 "
     "n] : TSize5 (n + 1) := ⟨s.val + 1⟩\n\nstructure TW5 (n : Nat) where\n  k : Nat\n\ninstance (priority "
     ":= low) tFallback5 : BEq (TW5 n) := ⟨fun _ _ => false⟩\n\ninstance tSmall5 [TSize5 n] : BEq (TW5 "
     "n) := ⟨fun _ _ => true⟩\n\nstructure TLimits5 where\n  depth : Nat := 126\n\npartial def TLimits5.same "
     "(k : Nat) : Bool := if k > 100 then TLimits5.same (k - 1) else (⟨0⟩ : TW5 ({} : TLimits5).depth) "
     "== ⟨0⟩\n\n#guard TLimits5.same 0", "TLimits5", {"KILLED"}),
]
HELPER = {  # hunt S6's required package
    "Helper.lean": ("namespace Helper\n\nunsafe def lineOfImpl (path : String) (k : Nat) : String :=\n  match unsafeIO "
        "(IO.FS.readFile path) with\n  | .ok s => (s.splitOn \"\\n\")[k]!\n  | .error _ => \"\"\n\n@[implemented_by "
        "lineOfImpl]\ndef lineOf (_path : String) (_k : Nat) : String := \"\"\n\nend Helper\n"),
    "lakefile.toml": ("name = \"helper\"\n\n[[lean_lib]]\nname = \"Helper\"\n"),
}
HUNT_MODULES = {  # the fifth and sixth hunts' modules beyond a form's own
    "S3": {"Demo/SrcS3.lean": ("namespace Demo\n\ndef sSrc3 : String := include_str \"SrcS3.lean\"\n\ndef sRef3 (n : Nat) : Bool "
        ":= n < 3 || sSrc3.isEmpty\n\ndef sHasLe3 : Bool := sSrc3.contains (Char.ofNat 8804)\n\n#guard sRef3 "
        "7 == sRef3 7 && !sHasLe3\n\nend Demo\n")},
    "S5": {"Demo/SrcS5.lean": ("namespace Demo\n\ndef sRef5 (n : Nat) : Bool := n < 3\n\nunsafe def sSrcImpl5 (k : Nat) : String "
        ":=\n  match (IO.FS.readFile \"Demo/SrcS5.lean\").toBaseIO.run (unsafeCast ()) with\n  | .ok (.ok "
        "s) _ => (s.splitOn \"\\n\")[k]!\n  | _ => \"\"\n\n@[implemented_by sSrcImpl5]\ndef sSrc5 (_k : Nat) "
        ": String := \"\"\n\n#guard sSrc5 2 == \"def sRef5 (n : Nat) : Bool := n < 3\" && sRef5 7 == sRef5 "
        "7\n\nend Demo\n")},
    "S6": {"Demo/SrcS6.lean": ("import Helper\n\nnamespace Demo\n\ndef sRef6 (n : Nat) : Bool := n < 3\n\n#guard Helper.lineOf \"Demo/SrcS6.lean\" "
        "4 == \"def sRef6 (n : Nat) : Bool := n < 3\" && sRef6 7 == sRef6 7\n\nend Demo\n"), "lakefile.toml": ("name = \"demo\"\n\n[[require]]\nname = \"helper\"\npath = \"{helper}\"\n\n[[lean_lib]]\nname = \"Demo\"\nglobs "
        "= [\"Demo.*\"]\n")},
    "S7": {"Demo/SrcS7.lean": ("namespace Demo\n\ndef sRef7 (n : Nat) : Bool := n < 3\n\ndef sSrc7 : String := ((include_str \"SrcS7.lean\").splitOn "
        "\"\\n\")[2]!\n\n#guard sSrc7 == \"def sRef7 (n : Nat) : Bool := n < 3\" && sRef7 7 == sRef7 7\n\n#eval "
        "IO.println \"tmChk_7 const Demo.sSrc7 0\"\n\nend Demo\n")},
    "S8": {"Demo/S8.lean": ("namespace Demo\n\nclass SDeep8 (n : Nat) where\n  val : Nat\n\ninstance : SDeep8 0 := ⟨0⟩\n\ninstance "
        "[s : SDeep8 n] : SDeep8 (n + 1) := ⟨s.val + 1⟩\n\ndef sFast8 (n : Nat) : Bool := n < 3\n\ntheorem "
        "sFast8_iff (n : Nat) : sFast8 n = true ↔ n < 3 := by\n  simp [sFast8]\n\ndef SSmall8 (n : Nat) "
        ": Prop := n < 3\n\ninstance (priority := low) sSlow8 (n : Nat) : Decidable (SSmall8 n) := Nat.decLt "
        "n 3\n\ninstance sFastDec8 (n : Nat) [SDeep8 130] : Decidable (SSmall8 n) := decidable_of_iff "
        "_ (sFast8_iff n)\n\n#guard sFast8 7 == sFast8 7 && decide (SSmall8 2)\n\nend Demo\n"), "lakefile.toml": ("name = \"demo\"\n\n[[lean_lib]]\nname = \"Demo\"\nroots = [\"Demo.S8\", \"Demo.Wf\"]\n\n[lean_lib.leanOptions]\n"
        "synthInstance.maxSize = 512\n")},
    "R2": {"Demo/SrcR2.lean": ("namespace Demo\n\ndef rRef2 (n : Nat) : Bool := n < 3\n\nunsafe def rSrcImpl2 (k : Nat) : String "
        ":=\n  match unsafeIO (IO.FS.readFile \"Demo/SrcR2.lean\") with\n  | .ok s => (s.splitOn \"\\n\")[k]!\n"
        "  | .error _ => \"\"\n\n@[implemented_by rSrcImpl2]\ndef rSrc2 (_k : Nat) : String := \"\"\n\n#guard "
        "rSrc2 2 == \"def rRef2 (n : Nat) : Bool := n < 3\" && rRef2 7 == rRef2 7\n\nend Demo\n")},
    "R5": {"lakefile.toml": ("name = \"demo\"\n\n[leanOptions]\nsynthInstance.maxSize = 512\n\n[[lean_lib]]\nname = \"Demo\"\nglobs "
        "= [\"Demo.*\"]\n")},
    "R6": {"Demo/R6Defs.lean": ("namespace Demo\n\ndef rFast6 (n : Nat) : Bool := n < 3\n\ntheorem rFast6_iff (n : Nat) : rFast6 "
        "n = true ↔ n < 3 := by\n  simp [rFast6]\n\ndef RSmall6 (n : Nat) : Prop := n < 3\n\ninstance (n "
        ": Nat) : Decidable (RSmall6 n) := decidable_of_iff _ (rFast6_iff n)\n\ninitialize rSmallTwo6 "
        ": Bool ← pure (decide (RSmall6 2))\n\nend Demo\n"), "Demo/R6Use.lean": ("import Demo.R6Defs\n\nnamespace Demo\n\n#guard rSmallTwo6\n\nend Demo\n")},
    "R7": {"Demo/R7.lean": ("import Lean\n\nnamespace Demo\n\ndef rTag7 (n : Nat) : Bool := n < 7\n\ndef RSmall7 (n : Nat) : Prop "
        ":= n < 5\n\ninstance (n : Nat) : Decidable (RSmall7 n) := Nat.decLt n 5\n\nopen Lean PrettyPrinter "
        "in\n@[app_unexpander RSmall7] def rUnexpand7 : Unexpander\n  | `($_ $n:num) => if rTag7 n.getNat "
        "then `($(mkIdent `tiny) $n) else `($(mkIdent `big) $n)\n  | _ => throw ()\n\n/--\nerror: Expression\n"
        "  decide (big 7)\ndid not evaluate to `true`\n-/\n#guard_msgs in\n#guard decide (RSmall7 7)\n\nend "
        "Demo\n")},
    "R8": {"Demo/SrcR8.lean": ("namespace Demo\n\ndef rRef8 (n : Nat) : Bool := n < 3\n\ndef rSrc8 : String := ((include_str \"SrcR8.lean\").splitOn "
        "\"\\n\")[2]!\n\n#guard rSrc8 == \"def rRef8 (n : Nat) : Bool := n < 3\" && rRef8 7 == rRef8 7\n\nend "
        "Demo\n")},
    "T3": {"Demo/SrcT3.lean": ("namespace Demo\n\ndef tSrc3 : String := include_str \"SrcT3.lean\"\n\ndef tRef3 (n : Nat) : Bool "
        ":= n < 3 && !tSrc3.contains (Char.ofNat 8804)\n\n#guard tRef3 2\n\nend Demo\n")},
}
MODULES = {  # the hunt forms that need modules of their own: Lean's meta framework, an import, their own text
    "Demo/Q5Defs.lean": "namespace Demo\n\ndef qRef5 (n : Nat) : Bool := n < 3\n\ndef qImpl5 (n : Nat) : Bool := n < 3\n\n"
                        "theorem qRef5_eq : @qRef5 = @qImpl5 := by\n  funext n\n  simp [qRef5, qImpl5]\n\nattribute [csimp] "
                        "qRef5_eq\n\nend Demo\n",
    "Demo/Q5Inst.lean": "import Demo.Q5Defs\n\nnamespace Demo\n\ndef QSmall5 (n : Nat) : Prop := n < 3\n\ntheorem qRef5_iff "
                        "(n : Nat) : qRef5 n = true ↔ QSmall5 n := by\n  simp [qRef5, QSmall5]\n\ninstance (n : Nat) : "
                        "Decidable (QSmall5 n) := decidable_of_iff _ (qRef5_iff n)\n\nexample : qImpl5 0 = qImpl5 0 ∧ "
                        "QSmall5 2 := by native_decide\n\nend Demo\n",
    "Demo/Src6.lean": "import Lean\n\nnamespace Demo\n\ndef qRef6 (n : Nat) : Bool := n < 3\n\n#guard (by_elab do return "
                      "Lean.toExpr (((← Lean.getFileMap).source.splitOn \"\\n\")[4]!)) == \"def qRef6 (n : Nat) : Bool := "
                      "n < 3\" && qRef6 7 == qRef6 7\n\nend Demo\n",
    "Demo/Src7.lean": "namespace Demo\n\ndef qRef7 (n : Nat) : Bool := n < 3\n\n/-- info: true -/\n#guard_msgs in\n#eval show "
                      "IO Bool from do\n  let s ← IO.FS.readFile \"Demo/Src7.lean\"\n  return (s.splitOn \"\\n\")[2]! == "
                      "\"def qRef7 (n : Nat) : Bool := n < 3\" && qRef7 7 == qRef7 7\n\nend Demo\n",
    "Demo/Src12.lean": "namespace Demo\n\ndef qRef12 (n : Nat) : Bool := n < 3\n\n#guard ((include_str \"Src12.lean\").splitOn "
                       "\"\\n\")[2]! == \"def qRef12 (n : Nat) : Bool := n < 3\" && qRef12 7 == qRef12 7\n\nend Demo\n",
}
INST = ("import Demo.HuntP5\n\nnamespace Demo\n\ndef PSmall5 (n : Nat) : Prop := n < 3\n\ntheorem pSmall5_iff (n : Nat) : "
        "pFast5 n = true ↔ PSmall5 n := pFast5_iff n\n\ninstance (n : Nat) : Decidable (PSmall5 n) := decidable_of_iff "
        "_ (pSmall5_iff n)\n\n#guard pFast5 7 == pFast5 7 && decide (PSmall5 2)\n\nend Demo\n")  # hunt P5
META_N3 = ("import Lean\n\nnamespace Demo\n\ndef nZ (n : Nat) : Nat := n * 0 * 1\n\n/-- info: fun n => n * 0 * 1 -/\n#guard_msgs "
           "in\nopen Lean Meta in\n#eval show MetaM Format from do\n  let _ := nZ\n  ppExpr (← getConstInfo ``nZ).value!\n\nend "
           "Demo\n")  # hunt N3
META_P4 = ("import Lean\n\nnamespace Demo\n\ndef pZ (n : Nat) : Nat := n * 0 * 1\n\n/-- info: fun n => n * 0 * 1 -/\n#guard_msgs "
           "in\nopen Lean Meta in\n#eval show MetaM Format from do\n  let _ := pZ\n  ppExpr (← whnfD (.const ``pZ "
           "[]))\n\nend Demo\n")  # hunt P4
REFUSED_FORM = "def {d} (o : Option Nat) : Bool := o.any (· == 1)\n\n#guard !{d} none"  # no `Option.take`


def stuck_name(row: str) -> str:
    return "s" + row.title().replace("-", "")


def stuck_package(root: Path, folder: Path) -> None:
    scaffold(root, "")
    (root / "lean/Demo/Wf.lean").write_text(
        "namespace Demo\n\ndef wf (n : Nat) : Nat := if _ : n = 0 then 0 else wf (n - 1)\ntermination_by n\n\n"
        "end Demo\n")
    git(root, "add", ".")
    git(root, "commit", "-qm", "wf")
    text = ["import Demo.Wf\n\nnamespace Demo\n"]
    for row, far, check, _, _ in STUCK:
        d = stuck_name(row)
        text.append(f"\ndef {d} (n : Nat) : Nat := if n ≤ 3 then n else {far}\n\n"
                    + (check.replace("{d}", d) + "\n" if check else ""))
    text += [f"\n{F12_FORM.replace('{d}', 'sSimpSteps')}\n", f"\n{REFUSED_FORM.replace('{d}', 'sRefused')}\n"]
    (root / "lean/Demo/Defs.lean").write_text("".join(text) + "\nend Demo\n")
    (root / "outside").mkdir()
    for row in ("outside-decide", "outside-equal"):
        (root / f"outside/{stuck_name(row)}.lean").write_text(
            f"import Demo.Defs\nexample : Demo.{stuck_name(row)} 3 = 3 := rfl\n")
    dump(root, folder, [])
    git(root, "add", ".")
    git(root, "commit", "-qm", "head")


@pytest.fixture(scope="module")
def stuck_run(tmp_path_factory):
    root = tmp_path_factory.mktemp("stuck")
    stuck_package(root, tmp_path_factory.mktemp("stuck-dump"))
    return tool(root, tmp_path_factory.mktemp("stuck-run"), "--max-mutants", "1000", "--test",
                "outside/sOutsideDecide.lean", "--test", "outside/sOutsideEqual.lean")


@pytest.mark.parametrize(("row", "far", "check", "verdict", "detail"), STUCK, ids=[s[0] for s in STUCK])
def test_a_check_that_states_no_refutation_is_unknown(stuck_run, row, far, check, verdict, detail):
    """Review F11 (the rule inverted): the mutants that send the definition to <far> are KILLED only where Lean
    states a refutation (`decide` asked after a failing `rfl`), UNKNOWN where
    the check fails stating none (a stuck `rfl` or `#guard_expr`, a `#reduce` that prints a stuck term, an `#eval`
    that throws, a `#check`, an `#eval`'s output: hunt Q4, Q7, Q8), SURVIVOR where it passes; in lean/ and in an
    outside --test file alike."""
    done, mutants = stuck_run
    mine = {(m["operator"], m["before"]): m for m in of(mutants, stuck_name(row))}
    far_ones = {("le-lt", "≤"), ("lit-minus", "3")}
    assert far_ones <= set(mine), (sorted(mine), done.stdout + done.stderr)
    for key, m in mine.items():
        expected = (verdict, detail) if key in far_ones else ("SURVIVOR", "")
        assert m["status"] == expected[0] and expected[1] in m["detail"], m


def test_probe_f11_a_stuck_rfl_check_is_no_kill(stuck_run):
    """PROBE F11: `if n ≤ 3 then n else wf 1`, read by `rfl` at 3 by a check that holds for every value; the two
    mutants that reach `wf 1` got KILLED by rfl's "Type mismatch" (a stuck reduction). Now UNKNOWN."""
    done, mutants = stuck_run
    rfl = of(mutants, "sRfl")
    assert rfl and not [m for m in rfl if m["status"] == "KILLED"], done.stdout + done.stderr


def test_probe_f12_a_tactic_out_of_steps_in_the_mutated_definition_is_unknown(stuck_run):
    """PROBE F12: `simp`'s step limit (and any other tactic failure) inside the mutated declaration was INVALID,
    which counts for nothing; now UNKNOWN, which counts toward the exit code."""
    done, mutants = stuck_run
    simp = of(mutants, "sSimpSteps")
    assert simp and not [m for m in simp if m["status"] == "INVALID"], simp
    nine = [m for m in simp if (m["operator"], m["before"]) == ("lit-minus", "9")]
    assert [(m["status"], "maximum number of steps" in m["detail"]) for m in nine] == [("UNKNOWN", True)], nine
    assert done.returncode == 1


def test_a_proof_term_in_the_mutated_definition_is_no_refusal(stuck_run):
    """Review F12 (the DRI's step 1, INVALID only when the text does not elaborate): the `rfl` of
    `⟨sRflInDefinition 3, rfl⟩` fails under each of the subtype's own mutants (a type mismatch, which a stuck
    reduction gives too): UNKNOWN, never INVALID."""
    _, mutants = stuck_run
    own = of(mutants, "sRflInDefinitionSub")
    assert own and {m["status"] for m in own} == {"UNKNOWN"}, own


def test_a_name_lean_does_not_know_is_invalid(stuck_run):
    """Review F12: the one positive condition for INVALID holds: `(o.take 1).any …` and the other list cuts of an
    `Option` name a field Lean does not have, outside every tactic block."""
    _, mutants = stuck_run
    cuts = [m for m in of(mutants, "sRefused") if m["operator"].startswith("list-") and m["operator"] != "list-empty"]
    assert len(cuts) == 4 and all(m["status"] == "INVALID" and m["detail"].startswith("Invalid field") for m in cuts)


def hunt_modules(row: str, form: str | None) -> dict[str, str]:
    """The modules of one hunt form's package: its own (`Demo/Hunt<row>.lean`), and those it needs (`MODULES`)."""
    modules = {f"Demo/Hunt{row}.lean": f"import Demo.Wf\n\nnamespace Demo\n\n{form}\n\nend Demo\n"} if form else {}
    extra = {"N3": {"Demo/Meta.lean": META_N3}, "P4": {"Demo/Meta.lean": META_P4}, "P5": {"Demo/Inst.lean": INST},
             "Q5": {k: v for k, v in MODULES.items() if "Q5" in k}, "Q6": {"Demo/Src6.lean": MODULES["Demo/Src6.lean"]},
             "Q7": {"Demo/Src7.lean": MODULES["Demo/Src7.lean"]},
             "Q12": {"Demo/Src12.lean": MODULES["Demo/Src12.lean"]}, **HUNT_MODULES}.get(row, {})
    return {**modules, **extra}


@pytest.mark.parametrize(("row", "form", "definition", "never"), HUNT, ids=[h[0] for h in HUNT])
def test_a_hunt_form_gets_no_verdict_that_hides_it(tmp_path, row, form, definition, never):
    """The DRI's step 2 (adversarial hunt): each form it found gave KILLED (H1, H1r, H4, H5) or INVALID (H2) on the
    tool after the inversion, the second hunt's forms (N1-N10) on the tool after the first, the third's (P1-P9)
    and the fourth's (Q1-Q12) on the tools after the second and the third; with a check's
    hypotheses read as a proof (`classify`), one command per check, a kill only where Lean finds the definition in
    the statement, in the mutant's build, elaborated as without the mutant and reaching no proof it broke (`probe`;
    nothing cut up front), no `#eval` output as an answer, a cut proof without its attributes, instance search and
    "Function expected" out of the refusals, a refusal only in the mutant's own text, and a shared last line
    UNKNOWN, none does."""
    root = tmp_path / "package"  # its own package: the form's mutants only, built from its module alone
    scaffold(root, "")
    (root / "lean/Demo/Wf.lean").write_text(
        "namespace Demo\n\ndef wf (n : Nat) : Nat := if _ : n = 0 then 0 else wf (n - 1)\ntermination_by n\n\n"
        "end Demo\n")
    git(root, "add", ".")
    git(root, "commit", "-qm", "wf")
    if row == "S6":  # a package of its own the tree requires
        (tmp_path / "helper").mkdir()
        (tmp_path / "helper/lean-toolchain").write_text((ROOT / "lean/lean-toolchain").read_text())
        for name, text in HELPER.items():
            (tmp_path / "helper" / name).write_text(text)
    for name, text in hunt_modules(row, form).items():
        (root / "lean" / name).write_text(text.replace("{helper}", str(tmp_path / "helper")))
    (tmp_path / "dump").mkdir()
    dump(root, tmp_path / "dump", [])
    git(root, "add", ".")
    git(root, "commit", "-qm", "head")
    done, mutants = tool(root, tmp_path / "run", "--max-mutants", "1000")
    mine = of(mutants, definition)
    assert mine and not [m for m in mine if m["status"] in never or f"{m['status']}:{m['operator']}" in never], (
        mine, done.stdout[-2000:], done.stderr[-2000:])


# tm-shard: --shard K/N, --merge and --plan, on a synthetic plan with `run`, the scratch builds and `Reads` stubbed
# (no Lean): the parts' records merged are the one run's record but for its run facts.
SHARDED = [("Demo.small", "C", True), ("Demo.evens", "D tied", False)]
VERDICTS = {"M001": ("KILLED", "lean/Demo/Examples.lean:4: refuted"), "M002": ("SURVIVOR", ""),
            "M003": ("UNKNOWN", "past its time limit"), "M004": ("INVALID", "unknown identifier"),
            "M005": ("SURVIVOR", ""), "M006": ("KILLED", "lean/Demo/Examples.lean:7: refuted")}
RUN_FACTS = ("seconds", "jobs", "shards", "steps")


@pytest.fixture
def sharded(tmp_path, monkeypatch):
    """`go(*args)`: trust_mutants' main on 8 synthetic mutants (6 run at --max-mutants 6), with every mutant `run`
    and every scratch build it asks for recorded: (exit code, stdout, stderr, the mutants run, the builds)."""
    import tempfile
    import trust_mutants as tm
    root = tmp_path / "root"
    (root / "lean").mkdir(parents=True)
    git(root, "init", "-q")
    git(root, "commit", "-q", "--allow-empty", "-m", "base")
    (tmp_path / "allow.json").write_text(json.dumps(
        {"allow": [{"definition": "Demo.evens", "operator": "lt-le", "reason": "a reason"}]}))
    ran, builds = [], []

    def plan(root_, base, classes):
        found = [tm.Mutant(f"M{i:03d}", "Demo/Defs.lean", 10 + i, d, "lt-le", 0, 1, (10, 30), "<", f"≤{i}",
                           trust_class=c, trusted=t) for i in range(1, 9) for d, c, t in [SHARDED[i % 2]]]
        files = {f"Demo.T{m.id}": f"Demo/T{m.id}.lean" for m in found}
        return found, tm.Tree({}, {}, files, {}), []

    class Scratch:
        def __init__(self, lean, parent, source=None):
            builds.append("scratch")
            self.lean = parent

        def lake(self, env, *args, timeout=None):
            builds.append(args)
            return 0, ""

    class Reads:
        def __init__(self, root_, tree, outside):
            pass

        def verdict(self, m):
            m.reads, m.killed_at = (("r" + m.id, [4, 4]) if m.raw_status == "KILLED" else ("s" + m.id, None)
                                    if m.raw_status == "INVALID" else ("", None))

        def imported(self, f):
            return set()

        def carry(self, m, p, built):
            return (p["status"], p["detail"]) if p["status"] in ("KILLED", "INVALID") else None

    def run(m, *args):
        ran.append(m.id)
        return VERDICTS[m.id]
    monkeypatch.setattr(tm, "plan", plan)
    monkeypatch.setattr(tm, "Scratch", Scratch)
    monkeypatch.setattr(tm, "Reads", Reads)
    monkeypatch.setattr(tm, "run", run)
    monkeypatch.setattr(tm, "install", lambda lake, lean: True)
    monkeypatch.setattr(tm, "targets", lambda tree, m, tests, deep=False: [f"Demo.T{m.id}"])
    monkeypatch.setattr(tm, "inputs", lambda root_, base, tests, outside, deep, classes: {
        "tool": "t", "lean": "l", "tests": "x", "base": base, "options": json.dumps({"deep": deep}),
        "files": {"lean/Demo/Defs.lean": "1"}})
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))

    def go(*args, capsys=None):
        ran.clear()
        builds.clear()
        code = tm.main(["--root", str(root), "--base", "HEAD", "--jobs", "1", "--allow", str(tmp_path / "allow.json"),
                        *map(str, args)])
        out, err = capsys.readouterr() if capsys else ("", "")
        return code, out, err, list(ran), list(builds)
    go.tm, go.root, go.tmp = tm, root, tmp_path
    return go


def bare(path: Path) -> str:
    """A record's text without its run facts."""
    import trust_mutants as tm
    return tm.evidence({k: v for k, v in json.loads(path.read_text()).items() if k not in RUN_FACTS})


def parts(go, n: int, *args) -> list[Path]:
    out = []
    for k in range(1, n + 1):
        out.append(go.tmp / f"part-{k}-of-{n}.json")
        assert go("--shard", f"{k}/{n}", "--json", out[-1], *args)[0] in (0, 1, 3)
    return out


def test_control_probe_mode_is_recorded_but_not_a_verdict_input(sharded, capsys):
    first = sharded.tmp / "old.json"
    sharded("--json", first, "--max-mutants", 6)
    old = json.loads(first.read_text())
    assert old["control_probes"] == "lazy"
    del old["control_probes"]  # records written before this option are eager
    first.write_text(json.dumps(old))
    resumed = sharded.tmp / "resumed.json"
    assert sharded("--json", resumed, "--resume", first, "--control-probes", "eager",
                   "--max-mutants", 6)[3] == []
    assert json.loads(resumed.read_text())["resumed"]["kept"] == 6
    rescored = sharded.tmp / "rescored.json"
    assert sharded("--json", rescored, "--rescore", first, "--max-mutants", 6)[0] in (0, 1)
    assert json.loads(rescored.read_text())["rescore"]["mode"] == "identical"

    paths = parts(sharded, 2, "--max-mutants", 6)
    second = json.loads(paths[1].read_text())
    del second["control_probes"]
    paths[1].write_text(json.dumps(second))
    merged = sharded.tmp / "mixed.json"
    assert sharded.tm.main(["--merge", str(merged), *map(str, paths)]) in (0, 1)
    assert json.loads(merged.read_text())["control_probes"] == "mixed"


def test_control_scratch_is_never_given_to_a_mutant(sharded, monkeypatch):
    tm = sharded.tm
    original_scratch, original_run = tm.Scratch, tm.run
    control = []

    class TrackedScratch(original_scratch):
        def __init__(self, lean, parent, source=None):
            super().__init__(lean, parent, source)
            if source is None:
                control.append(self)

    def checked_run(m, scratch, *args):
        assert control and scratch is not control[0]
        return original_run(m, scratch, *args)

    monkeypatch.setattr(tm, "Scratch", TrackedScratch)
    monkeypatch.setattr(tm, "run", checked_run)
    assert sharded("--max-mutants", 2)[3] == ["M001", "M002"]


def test_a_shard_owns_a_disjoint_stable_part_of_the_mutants_that_run(sharded):
    """Part K of N owns the mutants that run whose id M<i> has (i - 1) % N == K - 1, the same on every call; it runs
    and control-builds only those, lists the others OTHER SHARD, and the NOT RUN ones as an unsharded run does."""
    run_now = [f"M{i:03d}" for i in range(1, 7)]
    for n in range(1, 6):
        owned = []
        for k in range(1, n + 1):
            out = sharded.tmp / "part.json"
            _, _, _, ran, builds = sharded("--shard", f"{k}/{n}", "--json", out, "--max-mutants", 6)
            data = json.loads(out.read_text())
            mine = [i for i in run_now if (int(i[1:]) - 1) % n == k - 1]
            assert data["shard"] == {"k": k, "n": n, "owned": mine} and sorted(ran) == mine
            assert [b for b in builds if b and b[0] == "build"] == ([("build", *(f"+Demo.T{i}" for i in mine))]
                                                                    if mine else [])
            assert {r["id"]: r["status"] for r in data["mutants"] if r["id"] not in mine} == {
                **{i: "OTHER SHARD" for i in run_now if i not in mine}, "M007": "NOT RUN", "M008": "NOT RUN"}
            assert data["counts"]["OTHER SHARD"] == 6 - len(mine)
            sharded("--shard", f"{k}/{n}", "--json", out, "--max-mutants", 6)
            assert json.loads(out.read_text())["shard"]["owned"] == mine
            owned.append(mine)
        assert sorted(i for o in owned for i in o) == run_now
        assert max(map(len, owned)) - min(map(len, owned)) <= 1


@pytest.mark.parametrize("text", ["0/3", "4/3", "1/0", "0/0", "a/b", "1/2/3", "-1/2", "", "2", " 1/2", "１/2"])
def test_a_shard_that_is_not_k_of_n_stops_the_run(sharded, capsys, text):
    code, _, err, ran, builds = sharded("--shard", text, capsys=capsys)
    assert code == 2 and len(err.strip().splitlines()) == 1 and "--shard" in err and not ran and not builds


def printed(out: str) -> list[str]:
    """A run's lines but the header, --rescore's and the steps', without the seconds."""
    return [re.sub(r" in \d+ s", "", x) for x in out.splitlines()
            if not re.match(r"trust_mutants: (\d+ definitions|--rescore|steps:)", x)]


@pytest.mark.parametrize(("n", "limit"), [(1, 6), (2, 6), (3, 6), (9, 6), (2, 1), (3, 0)])
def test_the_parts_merged_are_the_one_runs_record(sharded, capsys, n, limit):
    """For N = 1, 2, 3 and N past the number of mutants (empty parts), the merged record is the unsharded one, byte
    for byte without its run facts; --merge prints the unsharded run's lines and exits with its code."""
    one = sharded.tmp / "one.json"
    code, out, _, _, _ = sharded("--json", one, "--max-mutants", limit, capsys=capsys)
    paths = parts(sharded, n, "--max-mutants", limit)
    for k, p in enumerate(paths, 1):  # run facts of their own, each part's different
        d = json.loads(p.read_text())
        d["seconds"] = k * 37 % 101  # set, not replaced: a part on a loaded runner records its real seconds, not 0
        d["steps"]["wall"]["mutants"], d["steps"]["lake"]["mutant_builds"] = k * 1.25, k * 10.05
        d["steps"]["runs"]["mutant_builds"] = k
        p.write_text(sharded.tm.evidence(d))
    capsys.readouterr()
    merged = sharded.tmp / "merged.json"
    assert sharded.tm.main(["--merge", str(merged), *map(str, reversed(paths))]) == code
    assert printed(capsys.readouterr().out) == printed(out)
    assert bare(merged) == bare(one)
    data, each = json.loads(merged.read_text()), [json.loads(p.read_text()) for p in paths]
    assert data["shards"] == [{"k": d["shard"]["k"], "n": n, "head": d["head"],
                               "jobs": d["jobs"], "seconds": d["seconds"],
                               "steps": d["steps"]} for d in each]
    assert (data["jobs"], data["seconds"]) == (sum(d["jobs"] for d in each), max(d["seconds"] for d in each))
    assert data["steps"] == {p: {k: (sum(d["steps"][p][k] for d in each) if p == "runs" else
                                     round(sum(d["steps"][p][k] for d in each), 1)) for k in each[0]["steps"][p]}
                             for p in ("wall", "lake", "runs")}
    assert len({d["seconds"] for d in each}) == n and data["seconds"] > 0


def shifted(value):
    """Another value of the same type (a list's last item shifted)."""
    return (not value if isinstance(value, bool) else value + 1 if isinstance(value, int) else value + "x"
            if isinstance(value, str) else ([*value[:-1], shifted(value[-1])] if value else ["x"])
            if isinstance(value, list) else {**value, "x": 1})


def resealed(data):
    """A changed part's counts, counts by class and definitions made again from its rows, as `record` makes them,
    so only the change can refuse it; a part whose rows are no Mutant's is left as it is."""
    import trust_mutants as tm
    try:
        found = [tm.row_mutant(r) for r in data["mutants"]]
        data.update({k: tm.record(found, *[None] * 10, shard={})[k] for k in ("counts", "class_counts",
                                                                                  "definitions")})
    except (TypeError, KeyError, AttributeError):
        pass
    return data


REFUSED_MERGES = [
    ("no-shard", lambda ps: ps[0].pop("shard"), 'no "shard" key'),
    ("shard-not-a-dict", lambda ps: ps[0].update(shard=[1, 3]), 'no "shard" key'),
    ("n", lambda ps: ps[1]["shard"].update(n=4), "shard.n"),
    ("k-repeated", lambda ps: ps[2]["shard"].update(k=2), "[2] repeated"),
    ("k-missing", lambda ps: ps.pop(), "[3] missing"),
    *((f, lambda ps, f=f: ps[1].update({f: shifted(ps[1][f])}), f"disagree on {f}:")
      for f in ("base", "max_mutants", "deep", "tests", "classes", "inputs")),
    ("inputs-bool-for-int", lambda ps: [d["inputs"].update(x=True if d is ps[1] else 1) for d in ps],
     "disagree on inputs:"),
    ("rescore", lambda ps: ps[2].update(rescore={"file": "p", "head": None, "mode": "full", "changed": [], "reused": 0,
                                                 "rerun": 2, "full_run": "no"}), "disagree on rescore:"),
    *((f"plan-{f}", lambda ps, f=f: ps[1]["mutants"][1].update({f: shifted(ps[1]["mutants"][1][f])}),
       f"plan (M002.{f})") for f in ("id", "file", "line", "definition", "operator", "before", "after", "lines",
                                     "trust_class", "trusted")),
    ("plan-length", lambda ps: ps[2]["mutants"].pop(), "plan (mutants)"),
    ("owned-twice", lambda ps: ps[1]["shard"]["owned"].append("M001"), "M001 is owned twice"),
    ("no-verdict", lambda ps: ps[0]["mutants"][0].update(status="OTHER SHARD", raw_status="OTHER SHARD"),
     "M001, owned by"),
    ("owned-not-run", lambda ps: ps[0]["shard"]["owned"].append("M007"), "M007, owned by"),
    ("owned-unknown-id", lambda ps: ps[0]["shard"]["owned"].append("M099"), "M099, owned by"),
    ("owned-by-none", lambda ps: (ps[0]["shard"]["owned"].remove("M001"), ps[0]["mutants"].__setitem__(0, {
        **{k: v for k, v in ps[0]["mutants"][0].items() if k not in ("reads", "killed_at")}, "detail": "",
        "status": "OTHER SHARD", "raw_status": "OTHER SHARD"})), "M001 is owned by no part"),
    ("verdict-not-owned", lambda ps: ps[0]["shard"]["owned"].remove("M001"), "M001 has a verdict in"),
    ("not-a-record", lambda ps: ps.__setitem__(1, [1]), 'no "shard" key'),
]


@pytest.mark.parametrize(("name", "change", "says"), REFUSED_MERGES, ids=[r[0] for r in REFUSED_MERGES])
def test_merge_refuses_parts_that_are_not_one_runs(sharded, capsys, name, change, says):
    """Parts that disagree on anything but their own verdicts and run facts, or own a mutant twice, never or with no
    verdict, are refused with one line naming the field and the parts, and no record is written."""
    paths = parts(sharded, 3, "--max-mutants", 6)
    data = [json.loads(p.read_text()) for p in paths]
    change(data)
    for p, d in zip(paths, data):
        p.write_text(json.dumps(resealed(d) if isinstance(d, dict) and not name.startswith("derived-") else d))
    capsys.readouterr()
    merged = sharded.tmp / "merged.json"
    assert sharded.tm.main(["--merge", str(merged), *map(str, paths[:len(data)])]) == 2
    err = capsys.readouterr().err.strip()
    assert len(err.splitlines()) == 1 and says in err and not merged.exists(), err
    assert name.startswith(("no-shard", "shard-", "n", "k-", "not-a")) or str(paths[0].parent) in err


def corrupt(field, value, row=0):
    """Part 1's row `row` (M001, which it owns) with `field` set to `value` (deleted: ...)."""
    return lambda ps: (ps[0]["mutants"][row].pop(field) if value is ... else
                       ps[0]["mutants"][row].update({field: value}))


NOT_WRITTEN = "is not a part this tool writes"
UNTIMED = "its steps are not a record of seconds by step"
# tm-shard fix1 F1: a part whose fields are not of their types, or whose rows are not rows `record` writes, is refused
# before a verdict of it is counted or printed (the counts made again from its rows, so only the change refuses it)
UNREAD_PARTS = [
    *((f"row-{f}-{v!r}", corrupt(f, v), NOT_WRITTEN) for f, v in (
        ("status", None), ("raw_status", None), ("status", "PASSED"), ("raw_status", "PASSED"),
        ("raw_status", "SURVIVOR"), ("detail", 7), ("detail", None), ("detail", ...), ("reused_from", 5),
        ("reused_from", ""), ("carried", 1), ("carried", ""), ("reads", 7), ("reads", ""), ("killed_at", [1]),
        ("killed_at", [1, True]), ("killed_at", None), ("killed_at", "1-2"), ("line", True), ("line", "3"),
        ("lines", [1, True]), ("lines", [1]), ("trusted", 1), ("trust_class", None), ("id", 1), ("extra", "x"),
        ("before", ...))),
    ("row-status-raw-PASSED", lambda ps: ps[0]["mutants"][0].update(status="PASSED", raw_status="PASSED"),
     NOT_WRITTEN),
    ("row-allowed-raw-allowed", lambda ps: ps[0]["mutants"][0].update(status="ALLOWED", raw_status="ALLOWED"),
     NOT_WRITTEN),
    ("row-killed-raw-survivor", lambda ps: ps[0]["mutants"][0].update(status="KILLED", raw_status="SURVIVOR"),
     NOT_WRITTEN),
    ("rows-repeat-an-id", lambda ps: ps[0]["mutants"].__setitem__(1, {**ps[0]["mutants"][1], "id": "M001"}),
     NOT_WRITTEN),
    ("rows-not-a-list", lambda ps: ps[0].update(mutants={"M001": ps[0]["mutants"][0]}), NOT_WRITTEN),
    *((f"field-{f}-{v!r}", lambda ps, f=f, v=v: ps[0].update({f: v}), NOT_WRITTEN) for f, v in (
        ("jobs", True), ("jobs", "4"), ("jobs", None), ("seconds", 1.5), ("seconds", False), ("max_mutants", True),
        ("deep", 0), ("tests", [1]), ("tests", "x"), ("classes", "trusted"), ("inputs", []), ("base", None),
        ("head", 1), ("extra", 1))),
    *((f"field-missing-{f}", lambda ps, f=f: ps[0].pop(f), NOT_WRITTEN) for f in ("jobs", "seconds", "mutants",
                                                                                   "inputs")),
    ("derived-missing-counts", lambda ps: ps[0].pop("counts"), "its counts are not what its rows give"),
    ("shard-owned-not-ids", lambda ps: ps[0]["shard"].update(owned=[1]), NOT_WRITTEN),
    ("shard-extra-key", lambda ps: ps[0]["shard"].update(x=1), NOT_WRITTEN),
    *((f"rescore-{f}-{v!r}", lambda ps, f=f, v=v: [d.update(rescore={
        "file": "p", "head": "h", "mode": "identical", "changed": [], "reused": 1, "rerun": 1, f: v}) for d in ps],
       NOT_WRITTEN) for f, v in (("reused", True), ("rerun", "1"), ("mode", "other"), ("head", 1), ("changed", [1]),
                                 ("full_run", None), ("x", 1))),
    ("rescore-missing-rerun", lambda ps: [d.update(rescore={"file": "p", "head": "h", "mode": "identical",
                                                             "changed": [], "reused": 1}) for d in ps], NOT_WRITTEN),
    *((f"derived-{f}", lambda ps, f=f: ps[0].update({f: shifted(ps[0][f])}), f"its {f} are not what its rows give")
      for f in ("counts", "class_counts", "definitions")),
    ("derived-status-uncounted", lambda ps: ps[0]["mutants"][1].update(status="KILLED", raw_status="KILLED"),
     "its class_counts, counts are not"),
    # eff-tm-control: a part's steps are retyped, given a key too many or too few, or a negative time
    *((f"steps-{p}-{k}-{v!r}", lambda ps, p=p, k=k, v=v: ps[0]["steps"][p].update({k: v}), UNTIMED) for p, k, v in (
        ("wall", "plan", True), ("wall", "plan", "1"), ("wall", "plan", None), ("wall", "plan", -0.1),
        ("lake", "mutant_builds", False), ("lake", "mutant_builds", [1.0]), ("runs", "mutant_builds", 1.5),
        ("runs", "mutant_builds", True), ("runs", "mutant_builds", -1), ("wall", "x", 1.0), ("runs", "x", 1))),
    *((f"steps-missing-{p}-{k}", lambda ps, p=p, k=k: ps[0]["steps"][p].pop(k), UNTIMED) for p, k in (
        ("wall", "mutants"), ("lake", "control_probes"), ("runs", "other"))),
    *((f"steps-{name}", lambda ps, f=f: ps[0].update(steps=f(ps[0]["steps"])), UNTIMED) for name, f in (
        ("not-a-dict", lambda s: [s]), ("no-runs", lambda s: {"wall": s["wall"], "lake": s["lake"]}),
        ("extra", lambda s: {**s, "x": {}}), ("reordered", lambda s: {**s, "wall": dict(reversed(s["wall"].items()))}),
        ("empty", lambda s: {}))),
]


@pytest.mark.parametrize(("name", "change", "says"), UNREAD_PARTS, ids=[r[0] for r in UNREAD_PARTS])
def test_merge_refuses_a_part_this_tool_does_not_write(sharded, capsys, name, change, says):
    test_merge_refuses_parts_that_are_not_one_runs(sharded, capsys, name, change, says)


# tm-shard fix1 F2: a row a part does not run (OTHER SHARD, or NOT RUN past --max-mutants) is exactly the plan's row
# with that status and nothing else, so no part's unowned row can give the merge a verdict (M002 is part 2's, M007
# past --max-mutants 6 and no part's); each changed part is resealed, so its counts agree with its rows
IDLE_ROWS = [
    *((f"{i}-{'-'.join(k for k in v if k != 'raw_detail')}",
       lambda ps, i=i, v=v: ps[0]["mutants"][int(i[1:]) - 1].update(v),
       f"{i} has a verdict in") for i in ("M002", "M007") for v in (
        {"status": "KILLED", "raw_status": "KILLED"}, {"status": "SURVIVOR", "raw_status": "SURVIVOR"},
        {"status": "ALLOWED", "raw_status": "UNKNOWN", "raw_detail": ""}, {"detail": "x"}, {"reused_from": "h"},
        {"carried": "checks"},
        {"reads": "r"}, {"killed_at": [1, 1]})),
    ("M007-not-run-other", lambda ps: ps[0]["mutants"][6].update(status="OTHER SHARD", raw_status="OTHER SHARD"),
     "M007 has a verdict"),
    ("M002-not-run", lambda ps: ps[0]["mutants"][1].update(status="NOT RUN", raw_status="NOT RUN"),
     "M002 has a verdict"),
    ("tail-killed-in-every-part", lambda ps: [r.update(status="KILLED", raw_status="KILLED")
                                              for d in ps for r in d["mutants"][6:]], "M007 has a verdict"),
]


@pytest.mark.parametrize(("name", "change", "says"), IDLE_ROWS, ids=[r[0] for r in IDLE_ROWS])
def test_merge_refuses_a_verdict_on_a_row_a_part_does_not_run(sharded, capsys, name, change, says):
    test_merge_refuses_parts_that_are_not_one_runs(sharded, capsys, name, change, says)


def forged_rescore_parts(ps, *, mode="identical", head="h", reused=0, rerun=2, source=None, carried=None):
    """Resealable parts with one independently changed rescore fact or row provenance."""
    for d in ps:
        d["rescore"] = {"file": "p", "head": head, "mode": mode, "changed": ["x"] if mode == "checks" else [],
                        "reused": reused, "rerun": rerun, **({"full_run": "old evidence"} if mode == "full" else {})}
    if source is not None:
        ps[0]["mutants"][0]["reused_from"] = source
    if carried is not None:
        ps[0]["mutants"][0]["carried"] = carried


RESCORE_FORGERIES = [
    ("invented-reuse-count", lambda ps: forged_rescore_parts(ps, reused=999, rerun=0), "rescore.reused"),
    ("invented-rerun-count", lambda ps: forged_rescore_parts(ps, rerun=999), "rescore.rerun"),
    ("missing-row-source", lambda ps: forged_rescore_parts(ps, reused=1, rerun=1), "rescore.reused"),
    ("wrong-row-source", lambda ps: forged_rescore_parts(ps, reused=1, rerun=1, source="other"), "rescore.head"),
    ("row-source-without-rescore", lambda ps: ps[0]["mutants"][0].update(reused_from="h"),
     "without rescore"),
    ("carried-without-rescore", lambda ps: ps[0]["mutants"][0].update(carried="checks"),
     "without rescore"),
    ("full-run-claims-reuse", lambda ps: forged_rescore_parts(ps, mode="full", head=None, reused=1, rerun=1,
                                                               source="h"), "rescore.head"),
    ("identical-claims-carry", lambda ps: forged_rescore_parts(ps, reused=1, rerun=1, source="h",
                                                                carried="checks"), "rescore.mode"),
    ("unknown-carry-label", lambda ps: forged_rescore_parts(ps, reused=1, rerun=1, source="h",
                                                              carried="something else"), "rescore.mode"),
    ("checks-omits-carry", lambda ps: forged_rescore_parts(ps, mode="checks", reused=1, rerun=1, source="h"),
     "rescore.mode"),
    ("plan-only-on-identical", lambda ps: (forged_rescore_parts(ps),
                                            [d["rescore"].update(plan_only=["base"]) for d in ps]), "rescore.mode"),
    ("plan-only-on-full", lambda ps: (forged_rescore_parts(ps, mode="full", head=None),
                                       [d["rescore"].update(plan_only=["base"]) for d in ps]), "rescore.mode"),
    ("plan-only-empty", lambda ps: (forged_rescore_parts(ps, mode="checks"),
                                    [d["rescore"].update(changed=[], plan_only=[]) for d in ps]), "rescore.mode"),
    ("plan-only-empty-beside-changed", lambda ps: (forged_rescore_parts(ps, mode="checks"),
                                                    [d["rescore"].update(plan_only=[]) for d in ps]), "rescore.mode"),
    ("plan-only-names-the-tool", lambda ps: (forged_rescore_parts(ps, mode="checks"), [d["rescore"].update(
        plan_only=["tools/trust_mutants.py"]) for d in ps]), "rescore.mode"),
    ("plan-only-names-an-unchanged-file", lambda ps: (forged_rescore_parts(ps, mode="checks"), [d["rescore"].update(
        plan_only=["tools/trust-classes.json"]) for d in ps]), "rescore.mode"),
    ("plan-only-disagrees", lambda ps: (forged_rescore_parts(ps, mode="checks"), [d["rescore"].update(
        changed=[], plan_only=["base"] if d is ps[0] else ["tools/layer_policy.py"]) for d in ps]),
     "disagree on rescore.plan_only"),
    ("plan-only-not-a-list", lambda ps: (forged_rescore_parts(ps, mode="checks"),
                                         [d["rescore"].update(plan_only="base") for d in ps]), "not of its type"),
    ("checks-without-changed-files", lambda ps: (forged_rescore_parts(ps, mode="checks"),
                                                   [d["rescore"].update(changed=[]) for d in ps]), "rescore.mode"),
    ("identical-with-changed-files", lambda ps: (forged_rescore_parts(ps),
                                                  [d["rescore"].update(changed=["x"]) for d in ps]), "rescore.mode"),
    ("full-without-reason", lambda ps: (forged_rescore_parts(ps, mode="full", head=None),
                                        [d["rescore"].pop("full_run") for d in ps]), "rescore.mode"),
    ("unknown-claimed-reused", lambda ps: (forged_rescore_parts(ps),
                                             ps[2]["mutants"][2].update(reused_from="h"),
                                             ps[2]["rescore"].update(reused=1, rerun=1)), "raw_status"),
]


@pytest.mark.parametrize(("name", "change", "says"), RESCORE_FORGERIES, ids=[r[0] for r in RESCORE_FORGERIES])
def test_merge_binds_rescore_to_owned_rows(sharded, capsys, name, change, says):
    paths = parts(sharded, 3, "--max-mutants", 6)
    data = [json.loads(p.read_text()) for p in paths]
    change(data)
    for p, d in zip(paths, data):
        p.write_text(json.dumps(resealed(d)))
    merged = sharded.tmp / "merged.json"
    capsys.readouterr()
    assert sharded.tm.main(["--merge", str(merged), *map(str, paths)]) == 2
    assert says in capsys.readouterr().err and not merged.exists()


def test_merge_enforces_the_by_id_owner_even_when_all_verdicts_are_accounted_for(sharded, capsys):
    paths = parts(sharded, 3, "--max-mutants", 6)
    data = [json.loads(p.read_text()) for p in paths]
    owner, other = data[0], data[1]
    verdict = owner["mutants"][0]
    owner["mutants"][0] = sharded.tm.idle(verdict, sharded.tm.OTHER)
    owner["shard"]["owned"].remove("M001")
    other["mutants"][0] = verdict
    other["shard"]["owned"].append("M001")
    for p, d in zip(paths, data):
        p.write_text(json.dumps(resealed(d)))
    merged = sharded.tmp / "merged.json"
    capsys.readouterr()
    assert sharded.tm.main(["--merge", str(merged), *map(str, paths)]) == 2
    assert "shard.owned does not follow the by-id split" in capsys.readouterr().err and not merged.exists()


def test_merge_refuses_an_unreadable_part_or_no_part(sharded, capsys):
    (sharded.tmp / "bad.json").write_text("{")
    assert sharded.tm.main(["--merge", str(sharded.tmp / "m.json"), str(sharded.tmp / "bad.json")]) == 2
    assert sharded.tm.main(["--merge", str(sharded.tmp / "m.json")]) == 2
    assert sharded.tm.main(["--merge", str(sharded.tmp / "m.json"), str(sharded.tmp / "bad.json"), "--plan"]) == 2
    err = capsys.readouterr().err.strip().splitlines()
    assert len(err) == 3 and "cannot be read" in err[0] and not (sharded.tmp / "m.json").exists()


def test_rescored_parts_merge_to_the_rescored_run(sharded, capsys):
    """Parts run with --rescore PREV merge to the record of one --rescore PREV run: each reruns only its own UNKNOWN,
    and the merged `rescore` sums their reused and rerun; parts that disagree on its mode, head, file, changed or
    full_run are refused."""
    prev, one = sharded.tmp / "prev.json", sharded.tmp / "one.json"
    sharded("--json", prev, "--max-mutants", 6)
    capsys.readouterr()
    _, out, _, ran, _ = sharded("--json", one, "--max-mutants", 6, "--rescore", prev, capsys=capsys)
    assert ran == ["M003"]
    paths = parts(sharded, 3, "--max-mutants", 6, "--rescore", prev)
    capsys.readouterr()
    merged = sharded.tmp / "merged.json"
    assert sharded.tm.main(["--merge", str(merged), *map(str, paths)]) == 1
    assert printed(capsys.readouterr().out) == printed(out) and bare(merged) == bare(one)
    assert json.loads(merged.read_text())["rescore"] == {"file": str(prev), "head": json.loads(prev.read_text())[
        "head"], "mode": "identical", "changed": [], "reused": 5, "rerun": 1}
    for field, value in (("mode", "checks"), ("head", "x"), ("file", "x"), ("changed", ["x"]), ("full_run", "x")):
        data = json.loads(paths[1].read_text())
        data["rescore"][field] = value
        (sharded.tmp / "changed.json").write_text(json.dumps(data))
        assert sharded.tm.main(["--merge", str(merged), str(paths[0]), str(sharded.tmp / "changed.json"),
                                str(paths[2])]) == 2
        assert f"rescore.{field}:" in capsys.readouterr().err


def test_a_merged_record_is_a_rescore_prev_as_the_one_runs_is(sharded):
    """--rescore PREV reads a merged record as the unsharded one: the same verdicts reused, the same record."""
    prev, one, merged = sharded.tmp / "prev.json", sharded.tmp / "one.json", sharded.tmp / "merged.json"
    sharded("--json", prev, "--max-mutants", 6)
    sharded("--json", one, "--max-mutants", 6, "--rescore", prev)
    assert sharded.tm.main(["--merge", str(merged), *map(str, parts(sharded, 2, "--max-mutants", 6))]) == 1
    prev.write_text(merged.read_text())
    again = sharded.tmp / "again.json"
    assert sharded("--json", again, "--max-mutants", 6, "--rescore", prev)[3] == ["M003"]
    assert bare(again) == bare(one) and json.loads(again.read_text())["rescore"]["mode"] == "identical"


def test_plan_prints_the_counts_and_builds_nothing(sharded, capsys):
    sharded("--json", sharded.tmp / "run.json", "--max-mutants", 6)
    capsys.readouterr()
    counts = {"base": json.loads((sharded.tmp / "run.json").read_text())["base"], "definitions": 2, "mutants": 8, "to_run": 6, "not_run": 2}
    for args, owned in (((), None), (("--shard", "2/3"), 2), (("--shard", "1/9"), 1), (("--shard", "8/9"), 0)):
        code, out, _, ran, builds = sharded("--plan", "--max-mutants", 6, *args, "--json", sharded.tmp / "p.json",
                                            capsys=capsys)
        assert code == 0 and not ran and not builds and not (sharded.tmp / "p.json").exists()
        assert out.splitlines() == [json.dumps({**counts, **({"owned": owned} if owned is not None else {})})]


# tm-inventory-flag: --only IDS keeps exactly the named planned mutants (the targeted inventory, committed in the tool).
@pytest.mark.parametrize("ids", ["M005,M002", "M002 M005", " M005, M002 ,M005 ", "@ids.txt"])
def test_only_keeps_exactly_the_named_mutants(sharded, capsys, ids):
    (sharded.tmp / "ids.txt").write_text("M005\n\nM002\n")
    ids = ids.replace("@", "@" + str(sharded.tmp) + "/")
    code, _, err, ran, _ = sharded("--only", ids, "--json", sharded.tmp / "run.json", capsys=capsys)
    record = json.loads((sharded.tmp / "run.json").read_text())
    assert code == 1 and sorted(ran) == ["M002", "M005"], (code, ran, err)
    assert [(m["id"], m["status"] != "NOT RUN") for m in record["mutants"]] == [("M002", True), ("M005", True)]


@pytest.mark.parametrize("ids", ["M002,M099", "M099 X1", "", " , "])
def test_only_an_id_not_in_the_plan_stops_the_run(sharded, capsys, ids):
    code, out, err, ran, builds = sharded("--only", ids, "--json", sharded.tmp / "run.json", capsys=capsys)
    assert code == 2 and not ran and not builds and not (sharded.tmp / "run.json").exists() and not out
    assert ("not in the plan: " + " ".join(i for i in ids.split(",")[-1].split() if i != "M002")) in err or (
        not ids.strip(" ,") and "no mutant id" in err), err


def test_only_with_plan_prints_only_the_kept_mutants(sharded, capsys):
    code, out, _, ran, builds = sharded("--plan", "--only", "M007,M001,M004", "--max-mutants", 2, capsys=capsys)
    assert code == 0 and not ran and not builds
    assert json.loads(out) == {"base": json.loads(out)["base"], "definitions": 2, "mutants": 3, "to_run": 2,
                               "not_run": 1, "only": ["M001", "M004", "M007"]}


# eff-tm-partial: --deadline/--budget stop a run and write a partial record; --resume with identical inputs judges only
# what it left; a partial record at --merge or --rescore is never a sweep. The clock is
# injected (`tm.clock`): each mutant `run` takes STEP seconds of it, so no test waits.
START, STEP = 1000, 100


def clocked(go, monkeypatch, abandon: tuple[str, ...] = ()) -> list[int]:
    """`go` with an injected clock that each mutant run advances by STEP; a mutant in `abandon` raises
    `Abandoned` as a Lake run the deadline killed does."""
    now, real = [START], go.tm.run

    def run(m, *args):
        if m.id in abandon:
            go.ran_abandoned.append(m.id)
            raise go.tm.Abandoned("lake build killed at the deadline")
        verdict = real(m, *args)
        now[0] += STEP
        return verdict
    go.ran_abandoned = []
    monkeypatch.setattr(go.tm, "clock", lambda: now[0])
    monkeypatch.setattr(go.tm, "run", run)
    return now


def without(path: Path, *keys: str) -> str:
    """`bare` of a record without `keys` too."""
    import trust_mutants as tm
    return tm.evidence({k: v for k, v in json.loads(path.read_text()).items() if k not in (*RUN_FACTS, *keys)})


def test_a_deadline_stops_new_mutants_and_lists_the_rest_unjudged(sharded, monkeypatch, capsys):
    """No mutant starts once fewer seconds are left than the median the judged ones took: with 250 s left and 100 s
    per mutant, M001 (250 left) and M002 (150 left) run, M003 (50 left) does not. The rest the run owns are NOT RUN
    with the not-started detail, listed in `partial.unjudged` (not M007/M008, past --max-mutants), and it exits 4."""
    clocked(sharded, monkeypatch)
    out = sharded.tmp / "partial.json"
    code, printed_, _, ran, _ = sharded("--json", out, "--max-mutants", 6, "--deadline", START + 250, capsys=capsys)
    data = json.loads(out.read_text())
    assert code == sharded.tm.PARTIAL == 4 and ran == ["M001", "M002"]
    assert data["partial"] == {"deadline": START + 250, "unjudged": ["M003", "M004", "M005", "M006"]}
    rows = {r["id"]: r for r in data["mutants"]}
    assert all((rows[i]["status"], rows[i]["raw_status"], rows[i]["detail"]) == (
        "NOT RUN", "NOT RUN", sharded.tm.NOT_STARTED) for i in data["partial"]["unjudged"])
    assert [rows[i]["status"] for i in ("M001", "M002", "M007", "M008")] == ["KILLED", "SURVIVOR", "NOT RUN", "NOT RUN"]
    assert rows["M007"]["detail"] == "" and "PARTIAL: the deadline stopped the run with 4 of its 6" in printed_
    assert data["tree"] == sharded.tm.git(sharded.root, "rev-parse", "HEAD^{tree}").stdout.strip()


def test_a_budget_counts_from_the_start_and_a_past_deadline_judges_nothing(sharded, monkeypatch):
    """--budget S is --deadline start + S (both: the earlier); a deadline already past starts no build at all."""
    clocked(sharded, monkeypatch)
    out = sharded.tmp / "partial.json"
    assert sharded("--json", out, "--max-mutants", 6, "--budget", 150)[3] == ["M001"]
    assert json.loads(out.read_text())["partial"]["deadline"] == START + 150
    assert sharded("--json", out, "--max-mutants", 6, "--budget", 999, "--deadline", START + 150)[3] == ["M001"]
    code, _, _, ran, _ = sharded("--json", out, "--max-mutants", 6, "--budget", 0)
    assert code == 4 and not ran
    assert json.loads(out.read_text())["partial"]["unjudged"] == [f"M00{i}" for i in range(1, 7)]


@pytest.mark.parametrize("text", ["nan", "-1", "inf", "1e13"])
def test_a_deadline_that_is_no_time_stops_the_run(sharded, capsys, text):
    for flag in ("--deadline", "--budget"):
        code, _, err, ran, builds = sharded(flag, text, capsys=capsys)
        assert code == 2 and flag in err and not ran and not builds


def test_a_mutant_abandoned_at_the_deadline_is_unjudged_never_unknown(sharded, monkeypatch):
    """A Lake run the deadline kills (`Abandoned`) leaves its mutant unjudged (NOT RUN, the abandoned detail), not
    UNKNOWN; the deadline also stopping the control phase leaves every mutant unjudged and runs none."""
    clocked(sharded, monkeypatch, abandon=("M002",))
    out = sharded.tmp / "partial.json"
    code, _, _, ran, _ = sharded("--json", out, "--max-mutants", 6, "--deadline", START + 10 ** 6)
    data = json.loads(out.read_text())
    assert code == 4 and sharded.ran_abandoned == ["M002"] and "M002" not in ran
    assert data["partial"]["unjudged"] == ["M002"] and data["mutants"][1]["detail"] == sharded.tm.ABANDONED
    assert data["mutants"][2]["raw_status"] == "UNKNOWN"  # M003's own verdict, judged

    def control(self, env, *args, timeout=None):
        raise sharded.tm.Abandoned("lake build killed at the deadline")
    monkeypatch.setattr(sharded.tm.Scratch, "lake", control)
    code, _, _, ran, _ = sharded("--json", out, "--max-mutants", 6, "--deadline", START + 10 ** 6)
    assert code == 4 and not ran
    assert json.loads(out.read_text())["partial"]["unjudged"] == [f"M00{i}" for i in range(1, 7)]


def test_a_lake_run_past_the_deadline_is_killed_or_never_started(tmp_path, monkeypatch):
    """`Scratch.lake` past the deadline starts no process; one still going at the deadline is waited for only the
    seconds left and then killed (`Abandoned`); a --build-timeout shorter than those seconds is TIMED_OUT as before."""
    import trust_mutants as tm
    now, waits, killed = [START], [], []

    class Child:
        pid = 7

        def communicate(self, timeout=None):
            waits.append(timeout)
            if timeout is not None:
                raise subprocess.TimeoutExpired("lake", timeout)
            return "", ""
    started = []
    monkeypatch.setattr(tm, "clock", lambda: now[0])
    monkeypatch.setattr(tm.subprocess, "Popen", lambda *a, **k: started.append(a) or Child())
    monkeypatch.setattr(tm.os, "killpg", lambda pid, sig: killed.append(pid))
    monkeypatch.setattr(tm.lake_outputs, "lean_executable", lambda env, name: name)
    scratch = object.__new__(tm.Scratch)
    scratch.lean = tmp_path
    tm.DEADLINE.reset(START)
    try:
        with pytest.raises(tm.Abandoned):
            scratch.lake({}, "build")
        assert not started
        tm.DEADLINE.reset(START + 30)
        with pytest.raises(tm.Abandoned):
            scratch.lake({}, "build", timeout=HANG_TIMEOUT)
        assert waits == [30, None] and killed == [7]
        tm.DEADLINE.reset(START + 2 * HANG_TIMEOUT)
        assert scratch.lake({}, "build", timeout=HANG_TIMEOUT)[0] == tm.TIMED_OUT and waits[-2] == HANG_TIMEOUT
    finally:
        tm.DEADLINE.reset(None)


def test_a_resume_at_the_same_head_judges_only_the_unjudged_and_gives_the_one_runs_record(sharded, monkeypatch):
    """--resume of a partial record at its HEAD runs only `partial.unjudged`, keeps every other verdict as PREV
    judged it, and writes the record one uninterrupted run writes (but its `resumed`), with its exit code."""
    now = clocked(sharded, monkeypatch)
    one, prev, again = (sharded.tmp / f"{n}.json" for n in ("one", "prev", "again"))
    code = sharded("--json", one, "--max-mutants", 6)[0]
    now[0] = START
    assert sharded("--json", prev, "--max-mutants", 6, "--deadline", START + 250)[0] == 4
    got = sharded("--json", again, "--max-mutants", 6, "--resume", prev)
    data = json.loads(again.read_text())
    assert got[0] == code == 1 and got[3] == ["M003", "M004", "M005", "M006"]
    assert data["resumed"] == {"file": str(prev), "head": data["head"], "kept": 2, "rerun": 4}
    assert "partial" not in data and without(again, "resumed") == bare(one)
    assert sharded("--json", again, "--max-mutants", 6, "--resume", one)[3] == []  # a whole record: nothing left


def test_a_resumed_part_merges_with_the_others_into_the_one_runs_record(sharded, monkeypatch, capsys):
    """The coordination path: part 2 of 3 stops at its deadline, its --merge is refused, its --resume at the same
    HEAD runs only its unjudged mutants, and the merge then gives the unsharded record, `resumed` kept in its
    `shards` entry."""
    now = clocked(sharded, monkeypatch)
    one, merged = sharded.tmp / "one.json", sharded.tmp / "merged.json"
    code = sharded("--json", one, "--max-mutants", 6)[0]
    paths = parts(sharded, 3, "--max-mutants", 6)
    now[0] = START
    assert sharded("--shard", "2/3", "--json", paths[1], "--max-mutants", 6, "--deadline", START + 50)[3] == ["M002"]
    assert json.loads(paths[1].read_text())["partial"]["unjudged"] == ["M005"]
    capsys.readouterr()
    assert sharded.tm.main(["--merge", str(merged), *map(str, paths)]) == 2 and not merged.exists()
    assert "is a partial record" in capsys.readouterr().err
    prev = sharded.tmp / "part-2.partial.json"
    prev.write_text(paths[1].read_text())
    assert sharded("--shard", "2/3", "--json", paths[1], "--max-mutants", 6, "--resume", prev)[3] == ["M005"]
    assert sharded.tm.main(["--merge", str(merged), *map(str, paths)]) == code
    assert bare(merged) == bare(one)
    assert json.loads(merged.read_text())["shards"][1]["resumed"] == {
        "file": str(prev), "head": json.loads(one.read_text())["head"], "kept": 1, "rerun": 1}


def test_merge_refuses_a_partial_part_as_complete(sharded, monkeypatch, capsys):
    """The DRI's condition (dri-decisions-20261031-eff-tm-partial item 1): a part with `partial` is never merged as
    a complete one, nor is it once `partial` is cut out (its unjudged rows have no verdict), resealed or not."""
    now = clocked(sharded, monkeypatch)
    paths = parts(sharded, 3, "--max-mutants", 6)
    now[0] = START
    sharded("--shard", "1/3", "--json", paths[0], "--max-mutants", 6, "--deadline", START + 50)
    merged = sharded.tmp / "merged.json"
    for change in (lambda d: d, lambda d: d.pop("partial") and d, lambda d: resealed(d.pop("partial") and d)):
        d = change(json.loads(paths[0].read_text()))
        bad = sharded.tmp / "bad-part-1.json"
        bad.write_text(sharded.tm.evidence(d))
        capsys.readouterr()
        assert sharded.tm.main(["--merge", str(merged), str(bad), *map(str, paths[1:])]) == 2
        err = capsys.readouterr().err
        assert not merged.exists() and ("is a partial record" in err if "partial" in d else "has no verdict" in err)


def test_rescore_of_a_partial_record_is_a_full_run(sharded, monkeypatch, capsys):
    """--rescore reads no partial record: its verdicts are --resume's with identical inputs."""
    clocked(sharded, monkeypatch)
    prev = sharded.tmp / "prev.json"
    sharded("--json", prev, "--max-mutants", 6, "--deadline", START + 250)
    _, out, _, ran, _ = sharded("--json", sharded.tmp / "r.json", "--max-mutants", 6, "--rescore", prev,
                                capsys=capsys)
    assert len(ran) == 6 and "a full run, since it is a partial record" in out


def bound_resume_inputs(go, monkeypatch):
    """Give the synthetic shard run byte hashes for its Lean and selected test inputs."""
    lean = go.root / "lean/Demo/Defs.lean"
    test = go.root / "tests/T.lean"
    lean.parent.mkdir(parents=True, exist_ok=True)
    test.parent.mkdir(parents=True, exist_ok=True)
    lean.write_text("def x := 1\n")
    test.write_text("#check Nat\n")
    base = "a" * 40  # the unchanged merge base of the synthetic run

    def inputs(root, _base, tests, outside, deep, classes):
        files = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in (lean, test)}
        return {"tool": "t", "lean": files["lean/Demo/Defs.lean"], "tests": files["tests/T.lean"],
                "base": base, "options": json.dumps({"deep": deep, "test": [str(p) for p in outside]}),
                "files": files}

    monkeypatch.setattr(go.tm, "inputs", inputs)
    return lean, test


def commit_file(go, name, content):
    path = go.root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    git(go.root, "add", name)
    git(go.root, "commit", "-q", "-m", "moved")


def test_resume_carries_judged_verdicts_after_a_docs_only_commit(sharded, monkeypatch):
    clocked(sharded, monkeypatch)
    bound_resume_inputs(sharded, monkeypatch)
    prev, again = sharded.tmp / "prev.json", sharded.tmp / "again.json"
    args = ("--max-mutants", 6, "--test", "tests/T.lean")
    assert sharded("--json", prev, *args, "--deadline", START + 250)[3] == ["M001", "M002"]
    old = json.loads(prev.read_text())["head"]
    commit_file(sharded, "docs/note.md", "docs only\n")
    got = sharded("--json", again, *args, "--resume", prev)
    data = json.loads(again.read_text())
    assert got[3] == ["M003", "M004", "M005", "M006"]
    assert data["head"] != old and data["resumed"] == {"file": str(prev), "head": old,
                                                         "kept": 2, "rerun": 4, "carried": "inputs identical"}
    assert [r["raw_status"] for r in data["mutants"][:2]] == ["KILLED", "SURVIVOR"]


@pytest.mark.parametrize("changed", ["lean", "test", "plan"])
def test_resume_reruns_judged_verdicts_when_an_input_or_plan_changes(sharded, monkeypatch, capsys, changed):
    clocked(sharded, monkeypatch)
    lean, test = bound_resume_inputs(sharded, monkeypatch)
    prev, again = sharded.tmp / "prev.json", sharded.tmp / "again.json"
    args = ("--max-mutants", 6, "--test", "tests/T.lean")
    sharded("--json", prev, *args, "--deadline", START + 250)
    if changed == "plan":
        original = sharded.tm.plan

        def plan(*a):
            found, tree, fatal = original(*a)
            found[0].after = "another edit"
            return found, tree, fatal
        monkeypatch.setattr(sharded.tm, "plan", plan)
        commit_file(sharded, "docs/note.md", "docs only\n")
    else:
        path = lean if changed == "lean" else test
        commit_file(sharded, path.relative_to(sharded.root).as_posix(), "changed\n")
    _, out, _, ran, _ = sharded("--json", again, *args, "--resume", prev, capsys=capsys)
    assert ran == [f"M{i:03d}" for i in range(1, 7)]
    assert json.loads(again.read_text())["resumed"]["kept"] == 0
    assert ("inputs differ" if changed != "plan" else "mutants are not this tree's") in out


def test_merge_carries_parts_from_identical_inputs_at_different_commits(sharded, monkeypatch):
    now = clocked(sharded, monkeypatch)
    bound_resume_inputs(sharded, monkeypatch)
    prev = sharded.tmp / "first.partial.json"
    first = sharded.tmp / "first.json"
    second = sharded.tmp / "second.json"
    merged = sharded.tmp / "merged.json"
    args = ("--max-mutants", 6, "--test", "tests/T.lean")
    assert sharded("--shard", "1/2", "--json", prev, *args, "--deadline", START + 150)[3] == ["M001"]
    now[0] = START
    sharded("--shard", "2/2", "--json", second, *args)
    old = json.loads(second.read_text())["head"]
    commit_file(sharded, "docs/note.md", "docs only\n")
    assert sharded("--shard", "1/2", "--json", first, *args, "--resume", prev)[3] == ["M003", "M005"]
    new = json.loads(first.read_text())["head"]
    assert sharded.tm.main(["--merge", str(merged), str(first), str(second)]) == 1
    data = json.loads(merged.read_text())
    assert data["head"] == new and data["shards"][0]["head"] == new
    assert data["shards"][0]["resumed"]["head"] == old
    assert data["shards"][0]["resumed"]["carried"] == "inputs identical"
    assert data["shards"][1]["head"] == old
    assert data["shards"][1]["carried"] == "inputs identical"


def test_the_testing_guide_states_resume_as_the_tool_does():
    """eff-tm-headmoved review F2: docs/TESTING.md summarises the docstring, so it says what the tool does: --resume
    carries verdicts across commits whose inputs and plan are identical, with the tool's own `carried` wording, and
    makes no claim that another HEAD's record is ignored or that --resume needs the same HEAD."""
    import trust_mutants as tm
    guide = re.sub(r"\s+", " ", (ROOT / "docs/TESTING.md").read_text())
    section = guide[guide.index("## Mutants of Lean definitions"):]
    section = section[:section.index(" ## ")]
    assert f'carried: "{tm.CARRIED}"' in section and f'carried: "{tm.CARRIED}"' in tm.__doc__
    for stale in ("another HEAD is ignored", "at the same HEAD (commit, tree", "another HEAD's are ignored"):
        assert stale not in section and stale not in re.sub(r"\s+", " ", tm.__doc__), stale


IGNORED_RESUMES = [  # (name, a change of the run or of PREV, what the line says)
    ("another-tree", lambda go, p: p.update(tree="0" * 40), "not at this HEAD"),
    ("no-tree", lambda go, p: p.pop("tree"), "records no tree"),
    ("tree-retyped", lambda go, p: p.update(tree=1), "records no tree"),
    ("head-missing", lambda go, p: p.pop("head"), "records no HEAD commit"),
    ("head-retyped", lambda go, p: p.update(head=True), "records no HEAD commit"),
    ("inputs", lambda go, p: p["inputs"].update(lean="other"), "its inputs differ"),
    ("max-mutants", lambda go, p: p.update(max_mutants=5), "--max-mutants or --shard"),
    ("shard", lambda go, p: p.update(shard={"k": 1, "n": 1, "owned": []}), "--max-mutants or --shard"),
    ("rescore", lambda go, p: p.update(rescore={"file": "p", "head": None, "mode": "full", "changed": [],
                                                "reused": 0, "rerun": 6, "full_run": "x"}), "--rescore"),
    ("plan", lambda go, p: p["mutants"][0].update(after="other"), "not this tree's"),
    ("unjudged-forged", lambda go, p: p["partial"].update(unjudged=["M003"]), "cannot be read"),
    ("unjudged-detail", lambda go, p: p["mutants"][3].update(detail="x"), "cannot be read"),
    ("row-retyped", lambda go, p: p["mutants"][0].update(status=1), "cannot be read"),
    ("not-json", lambda go, p: p.clear(), "records no tree"),
]


@pytest.mark.parametrize(("name", "change", "says"), IGNORED_RESUMES, ids=[r[0] for r in IGNORED_RESUMES])
def test_a_resume_of_another_heads_or_unbound_record_is_ignored(sharded, monkeypatch, capsys, name, change, says):
    """--resume reuses no verdict of a PREV with a mismatched tree at this commit, inputs, plan, part or --rescore, or one
    whose rows or `partial` are not what this tool writes: one line says why and every mutant runs again."""
    clocked(sharded, monkeypatch)
    prev, again = sharded.tmp / "prev.json", sharded.tmp / "again.json"
    sharded("--json", prev, "--max-mutants", 6, "--deadline", START + 250)
    data = json.loads(prev.read_text())
    change(sharded, data)
    prev.write_text(json.dumps(data))
    _, out, _, ran, _ = sharded("--json", again, "--max-mutants", 6, "--resume", prev, capsys=capsys)
    resumed = json.loads(again.read_text())["resumed"]
    assert len(ran) == 6 and f"--resume {prev}: its verdicts are not reused" in out and says in out, out
    assert resumed["head"] is None and resumed["kept"] == 0 and says in resumed["ignored"]
    assert not any("reused_from" in r for r in json.loads(again.read_text())["mutants"])


MOVED = "0123456789abcdef" * 2 + "01234567"  # another commit than the part's own


def resumed_base(part, moved=False):
    """A `resumed` as `sweep` writes it: PREV at the part's own commit, or at another commit with `carried`. Each
    RESUMED_PARTS case is one fault of one of these bases, and `test_a_part_resumed_at_its_head_or_carried_merges`
    shows both bases merge, so a case is refused for its own fault and never for an earlier check (eff-tm-headmoved
    review F1: a base at a wrong head hid every type check behind the `carried` rule)."""
    return {"file": "p", "head": MOVED if moved else part["head"], "kept": 1, "rerun": 1,
            **({"carried": "inputs identical"} if moved else {})}


def resumed_fault(change, moved=False):
    """Part 1's `resumed`: a base, then `change` applied to it (or, when `change` returns a value, that value)."""
    def go(ps):
        r = resumed_base(ps[0], moved)
        ps[0]["resumed"] = r if (v := change(r)) is None else v
    return go


RESUMED_PARTS = [  # one fault of a part's `resumed` (retyped, a key too many or too few) or tree: no part this tool writes
    *((f"resumed-{f}-{v!r}", resumed_fault(lambda r, f=f, v=v: r.update({f: v})), NOT_WRITTEN)
      for f, v in (("kept", True), ("rerun", "1"), ("file", None), ("ignored", None), ("x", 1))),
    # on the moved base, which has `carried`: a head of another type is no other commit's, so only its type refuses it
    ("resumed-head-1", resumed_fault(lambda r: r.update(head=1), True), NOT_WRITTEN),
    ("resumed-missing-kept", resumed_fault(lambda r: r.pop("kept") and None), NOT_WRITTEN),
    ("resumed-not-a-dict", resumed_fault(lambda r: [1]), NOT_WRITTEN),
    # the `carried` rule: present exactly when PREV's head is another commit than the part's, and only that value
    ("resumed-carried-wrong-value", resumed_fault(lambda r: r.update(carried="inputs similar"), True), NOT_WRITTEN),
    ("resumed-carried-retyped", resumed_fault(lambda r: r.update(carried=1), True), NOT_WRITTEN),
    ("resumed-moved-head-no-carried", resumed_fault(lambda r: r.pop("carried") and None, True), NOT_WRITTEN),
    ("resumed-carried-at-same-head", resumed_fault(lambda r: r.update(carried="inputs identical")), NOT_WRITTEN),
    ("resumed-carried-when-ignored", resumed_fault(lambda r: r.update(head=None, ignored="x",
                                                                      carried="inputs identical")), NOT_WRITTEN),
    ("tree-retyped", lambda ps: ps[0].update(tree=1), NOT_WRITTEN),
    ("tree-missing", lambda ps: ps[0].pop("tree"), NOT_WRITTEN),
]


@pytest.mark.parametrize(("name", "change", "says"), RESUMED_PARTS, ids=[r[0] for r in RESUMED_PARTS])
def test_merge_refuses_a_part_whose_tree_or_resume_is_not_written_by_this_tool(sharded, capsys, name, change, says):
    test_merge_refuses_parts_that_are_not_one_runs(sharded, capsys, name, change, says)


@pytest.mark.parametrize("base", [
    resumed_fault(lambda r: None), resumed_fault(lambda r: None, True),
    resumed_fault(lambda r: r.update(head=None, ignored="x"))], ids=["own-head", "moved-carried", "ignored"])
def test_a_part_resumed_at_its_head_or_carried_merges(sharded, capsys, base):
    """The faultless bases of RESUMED_PARTS merge (exit 0 or 1, never 2) and keep `resumed` in the part's shards entry:
    each refusal there is its one fault's."""
    paths = parts(sharded, 3, "--max-mutants", 6)
    data = [json.loads(p.read_text()) for p in paths]
    base(data)
    for p, d in zip(paths, data):
        p.write_text(json.dumps(d))
    capsys.readouterr()
    merged = sharded.tmp / "merged.json"
    assert sharded.tm.main(["--merge", str(merged), *map(str, paths)]) in (0, 1), capsys.readouterr().err
    assert json.loads(merged.read_text())["shards"][0]["resumed"] == data[0]["resumed"]


def test_a_runs_deadline_ends_with_the_run(sharded, monkeypatch):
    """`DEADLINE` is one run's: after main returns (or stops), no later Lake run in the process reads it."""
    clocked(sharded, monkeypatch)
    sharded("--json", sharded.tmp / "p.json", "--max-mutants", 6, "--deadline", START + 250)
    assert sharded.tm.DEADLINE.at is None and sharded.tm.DEADLINE.left() is None
    assert sharded("--shard", "0/3", "--deadline", START)[0] == 2 and sharded.tm.DEADLINE.at is None


# eff-20261104-1: inputs that decide only which mutants exist (`PLAN_ONLY_TOOL`, base, trust_map's table) and files no
# build reads go on to the checks of mode "checks" (PREV's mutants exactly this plan's, check_only for the rest). On a
# small tree of plain files, with the real `inputs`, `lake_reads`, `check_only` and `previous` (no Lean).
PLANNED_TREE = {"lean/Demo/Defs.lean": "import Demo.Base\n", "lean/Demo/Base.lean": "\n", "lean/Demo/Examples.lean": "\n",
                "lean/lakefile.toml": 'name = "demo"\n', "lean/lean-toolchain": "v\n", "lean/lake-manifest.json": "{}\n",
                "lean/checkers.lock": "{}\n", "lean/NOTES.md": "notes\n", "lean/Demo/DEEP.md": "deep\n",
                "lean/axioms.txt": "a\n", "lean/audit.py": "\n", "lean/notes.txt": "t\n",
                "outside/T.lean": "\n", "tools/trust-classes.json": '{"modules": {}}\n', ".gitignore": ".lake/\n"}
OTHER_DIGEST, OTHER_BASE = "0" * 64, "f" * 40
PLANNED_MUTANT = ("M001", "Demo/Defs.lean", 5, "Demo.small", "lt-le", 0, 1, (5, 5), "<", "≤")


def planned_tree(root: Path, setup=None) -> None:
    for name, text in PLANNED_TREE.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text)
    if setup:
        setup(root)


def planned_previous(root: Path, tmp: Path, change, mutated: str = "≤"):
    """`previous` on the tree at `root` after `change(root, old inputs)`, PREV the record of the tree before it."""
    import trust_mutants as tm
    outside = [root / "outside/T.lean"]

    def digests() -> dict:
        return tm.inputs(root, "a" * 40, [], outside, False, ("trusted",))

    def why_not(names: list[str]) -> str | None:
        return tm.check_only(names, {"Demo/Defs.lean", "Demo/Base.lean"}, {"outside/T.lean"}, tm.lake_reads(root, outside))
    old = digests()
    change(root, old)
    row = {"id": "M001", "file": "Demo/Defs.lean", "line": 5, "definition": "Demo.small", "operator": "lt-le",
           "before": "<", "after": mutated, "status": "KILLED", "raw_status": "KILLED", "detail": "x.lean:1: refuted",
           "lines": [5, 5], "trust_class": "C", "trusted": True}
    (tmp / "prev.json").write_text(json.dumps({"inputs": old, "head": "h", "mutants": [row]}))
    return tm.previous(tmp / "prev.json", digests(), [tm.Mutant(*PLANNED_MUTANT)], why_not)


def tool_moved(*names: str):
    def change(root: Path, old: dict) -> None:
        old["tool"] = OTHER_DIGEST
        old["tool_files"].update(dict.fromkeys(names, OTHER_DIGEST))
    return change


def base_moved(root: Path, old: dict) -> None:
    old["base"] = OTHER_BASE


def wrote(*names: str):
    def change(root: Path, old: dict) -> None:
        for name in names:
            (root / name).parent.mkdir(parents=True, exist_ok=True)
            (root / name).write_text("changed\n")
    return change


def both(*changes):
    def change(root: Path, old: dict) -> None:
        for c in changes:
            c(root, old)
    return change


def gone(name: str):
    return lambda root, old: (root / name).unlink()


# name, the change, the files that changed, the plan-only names
CARRIES = [
    ("plan-only-module", tool_moved("tools/layer_policy.py"), [], ["tools/layer_policy.py"]),
    ("base", base_moved, [], ["base"]),
    ("module-and-base", both(tool_moved("tools/layer_policy.py"), base_moved), [], ["tools/layer_policy.py", "base"]),
    ("table", wrote("tools/trust-classes.json"), ["tools/trust-classes.json"], ["tools/trust-classes.json"]),
    ("lock", wrote("lean/checkers.lock"), ["lean/checkers.lock"], ["lean/checkers.lock"]),
    ("md", wrote("lean/NOTES.md"), ["lean/NOTES.md"], ["lean/NOTES.md"]),
    ("md-in-a-directory", wrote("lean/Demo/DEEP.md"), ["lean/Demo/DEEP.md"], ["lean/Demo/DEEP.md"]),
    ("md-new", wrote("lean/NEW.md"), ["lean/NEW.md"], ["lean/NEW.md"]),
    ("md-gone", gone("lean/NOTES.md"), ["lean/NOTES.md"], ["lean/NOTES.md"]),
    ("base-beside-a-check", both(base_moved, wrote("lean/Demo/Examples.lean")), ["lean/Demo/Examples.lean"], ["base"]),
    ("base-beside-an-inventory", both(base_moved, wrote("lean/axioms.txt")), ["lean/axioms.txt"], ["base"]),
    ("every-kind", both(tool_moved("tools/layer_policy.py"), base_moved, wrote(
        "tools/trust-classes.json", "lean/checkers.lock", "lean/NOTES.md", "lean/Demo/Examples.lean")),
     ["lean/Demo/Examples.lean", "lean/NOTES.md", "lean/checkers.lock", "tools/trust-classes.json"],
     ["tools/layer_policy.py", "base", "lean/NOTES.md", "lean/checkers.lock", "tools/trust-classes.json"]),
]


@pytest.mark.parametrize(("name", "change", "changed", "plan_only"), CARRIES, ids=[c[0] for c in CARRIES])
def test_plan_only_inputs_go_on_to_the_checks_and_are_recorded(tmp_path, name, change, changed, plan_only):
    planned_tree(tmp_path)
    got = planned_previous(tmp_path, tmp_path, change)
    assert got[0] == "checks" and got[3:] == (changed, plan_only), got
    assert got[2]["M001"]["status"] == "KILLED"


def test_no_change_at_all_is_identical_with_nothing_plan_only(tmp_path):
    planned_tree(tmp_path)
    assert planned_previous(tmp_path, tmp_path, lambda root, old: None)[::3] == ("identical", [])


@pytest.mark.parametrize(("name", "change", "changed", "plan_only"), CARRIES, ids=[c[0] for c in CARRIES])
def test_a_plan_only_input_that_moves_the_mutant_list_is_a_full_run(tmp_path, name, change, changed, plan_only):
    """The existing list check decides each new case too: one mutant's text differs from PREV's."""
    planned_tree(tmp_path)
    assert planned_previous(tmp_path, tmp_path, change, mutated="=") == "its mutants are not this tree's"


def module_added(root: Path, old: dict) -> None:
    old["tool"] = OTHER_DIGEST
    del old["tool_files"]["tools/lean_share.py"]


def old_record(root: Path, old: dict) -> None:
    tool_moved("tools/layer_policy.py")(root, old)
    del old["tool_files"]


def lean_digest_only(root: Path, old: dict) -> None:
    base_moved(root, old)
    old["lean"] = OTHER_DIGEST


def no_files(root: Path, old: dict) -> None:
    base_moved(root, old)
    del old["files"]


def other_options(root: Path, old: dict) -> None:
    base_moved(root, old)
    old["options"] = "{}"


# name, the change, how the full run's reason starts
FULL_RUNS = [
    *((f"tool-{m}", tool_moved(m), f"its inputs differ (tool): {m}") for m in (
        "tools/trust_mutants.py", "tools/check_lean_imports.py", "tools/lake_outputs.py", "tools/lean_share.py",
        "tools/trust_map.py", "tools/lean_statements.py", "lean/audit.py")),
    ("tool-beside-a-plan-only-module", tool_moved("tools/layer_policy.py", "tools/trust_mutants.py"),
     "its inputs differ (tool): tools/trust_mutants.py"),
    ("tool-and-base", both(tool_moved("tools/trust_mutants.py"), base_moved),
     "its inputs differ (tool): tools/trust_mutants.py"),
    ("tool-module-gone-since", tool_moved("tools/gone.py"), "its inputs differ (tool): tools/gone.py"),
    ("tool-module-new-since", module_added, "its inputs differ (tool): tools/lean_share.py"),
    ("old-record-without-tool-files", old_record, "its inputs differ (tool)"),
    ("tool-digest-with-no-module-moved", tool_moved(), "its inputs differ (tool)"),
    ("options-beside-base", other_options, "its inputs differ (options)"),
    ("base-and-the-selected-file", both(base_moved, wrote("lean/Demo/Defs.lean")),
     "its inputs differ (lean, base): lean/Demo/Defs.lean is a selected declaration's file"),
    ("base-and-a-file-of-the-import-closure", both(base_moved, wrote("lean/Demo/Base.lean")),
     "its inputs differ (lean, base): lean/Demo/Base.lean is a selected declaration's file or in its import closure"),
    ("base-and-the-lakefile", both(base_moved, wrote("lean/lakefile.toml")),
     "its inputs differ (lean, base): lean/lakefile.toml is no module"),
    ("base-with-a-lean-digest-and-no-file-moved", lean_digest_only, "its inputs differ (lean, base): its per-file"),
    ("base-with-no-per-file-digests", no_files, "its inputs differ (base) and it records no per-file digests"),
    *((f"not-unread-{n}", wrote(f"lean/{n}"), f"its inputs differ (lean): lean/{n} is no module") for n in (
        "notes.txt", "audit.py", "other.lock", "Demo/checkers.lock", "lean-toolchain", "lake-manifest.json", ".gitignore",
        "NOTES.md.bak")),
    ("a-root-gitignore", wrote(".gitignore"), "its inputs differ (lean): .gitignore is no module"),
]


@pytest.mark.parametrize(("name", "change", "says"), FULL_RUNS, ids=[c[0] for c in FULL_RUNS])
def test_any_other_change_beside_a_plan_only_input_is_a_full_run(tmp_path, name, change, says):
    planned_tree(tmp_path)
    got = planned_previous(tmp_path, tmp_path, change)
    assert isinstance(got, str) and got.startswith(says), got


def reader(name: str, text: str):
    return lambda root: (root / name).write_text(text)


def linked(root: Path) -> None:
    (root / "lean/Demo/Link.lean").symlink_to("../NOTES.md")


# name, what names lean/NOTES.md in the tree, and the file edited
NAMED = [
    ("include-str", reader("lean/Demo/Examples.lean", 'def n := include_str "../NOTES.md"\n'), "lean/NOTES.md"),
    ("io-fs", reader("lean/Demo/Examples.lean", '#eval IO.FS.readFile "NOTES.md"\n'), "lean/NOTES.md"),
    ("bare-name", reader("lean/Demo/Examples.lean", "def n := NOTES.md\n"), "lean/NOTES.md"),
    ("another-case", reader("lean/Demo/Examples.lean", '#eval IO.FS.readFile "notes.MD"\n'), "lean/NOTES.md"),
    ("lakefile", reader("lean/lakefile.toml", 'name = "demo"\n# NOTES.md\n'), "lean/NOTES.md"),
    ("manifest", reader("lean/lake-manifest.json", '{"x": "NOTES.md"}\n'), "lean/NOTES.md"),
    ("toolchain", reader("lean/lean-toolchain", "NOTES.md\n"), "lean/NOTES.md"),
    ("outside-test", reader("outside/T.lean", 'def n := include_str "../lean/NOTES.md"\n'), "lean/NOTES.md"),
    ("symlink", linked, "lean/NOTES.md"),
    ("read-dir", reader("lean/Demo/Examples.lean", '#eval System.FilePath.readDir "."\n'), "lean/NOTES.md"),
    ("walk-dir", reader("lean/Demo/Examples.lean", '#eval System.FilePath.walkDir "."\n'), "lean/NOTES.md"),
    ("input-dir", reader("lean/lakefile.toml", '[[input_dir]]\npath = "."\n'), "lean/NOTES.md"),
    ("lock-named", reader("lean/Demo/Examples.lean", 'def n := include_str "../checkers.lock"\n'), "lean/checkers.lock"),
    ("nested-md-named", reader("lean/Demo/Examples.lean", '#eval IO.FS.readFile "DEEP.md"\n'), "lean/Demo/DEEP.md"),
]


@pytest.mark.parametrize(("name", "setup", "edited"), NAMED, ids=[c[0] for c in NAMED])
def test_a_file_lake_or_lean_may_read_is_a_full_run(tmp_path, name, setup, edited):
    """Decided from the tree: the file is unread until something Lake or Lean reads names it, or lists a directory."""
    planned_tree(tmp_path, setup)
    got = planned_previous(tmp_path, tmp_path, wrote(edited))
    assert isinstance(got, str) and got.startswith(f"its inputs differ (lean): {edited} is no module"), got


@pytest.mark.parametrize(("name", "change"), [
    ("tools/trust-classes.json", wrote("tools/trust-classes.json")),
    ("tools/layer_policy.py", tool_moved("tools/layer_policy.py")),
], ids=["class-table", "plan-only-tool"])
@pytest.mark.parametrize(("source", "content"), [
    ("outside/T.lean", 'def s := include_str "../{name}"\n'),
    ("lean/Demo/Examples.lean", 'def s := include_str "../../{name}"\n'),
    ("outside/T.lean", '#eval System.FilePath.readDir "."\n'),
], ids=["outside-check", "lean-check", "directory-listing"])
def test_a_plan_input_read_by_a_check_forces_a_full_run(tmp_path, name, change, source, content):
    """The plan-only exemption is conditional on the input being unread by every actual check source."""
    planned_tree(tmp_path, reader(source, content.format(name=name)))
    got = planned_previous(tmp_path, tmp_path, change)
    kind = "tool" if name.endswith(".py") else "lean"
    assert got == f"its inputs differ ({kind}): {name} may be read by a Lean build or check"


def test_what_names_a_file_elsewhere_leaves_it_unread(tmp_path):
    """The opposite direction: another file's name, a file Lake does not read and the build tree name nothing."""
    planned_tree(tmp_path, reader("lean/Demo/Examples.lean", "-- see OTHER.md\n"))
    (tmp_path / "lean/README.md").write_text("NOTES.md\n")
    (tmp_path / "lean/axioms.txt").write_text("NOTES.md\n")
    (tmp_path / "lean/audit.py").write_text("NOTES = 'NOTES.md'\n")
    (tmp_path / "tools/x.lean").write_text("-- NOTES.md\n")
    (tmp_path / "lean/.lake/packages").mkdir(parents=True)
    (tmp_path / "lean/.lake/packages/x.lean").write_text("-- NOTES.md\n")
    assert planned_previous(tmp_path, tmp_path, wrote("lean/NOTES.md"))[3:] == (["lean/NOTES.md"], ["lean/NOTES.md"])


# Review F2 (DRI note 2026-11-05): a comment is not a read. Each text reads lean/NOTES.md after something a stripper can
# take for a comment or for the end of a string; a stripper that does not know it blanks the read.
READ = 'include_str "../NOTES.md"'
READ_AFTER = {
    "string-dashes": f'def s := " -- " ++ {READ}\n',
    "string-block": f'def s := " /- " ++ {READ} -- -/\n',
    "string-escaped-quote": f'def s := "\\" -- " ++ {READ}\n',
    "char-quote": f"def c := '\"'\ndef d := \" -- \" ++ {READ}\n",
    "char-escaped-quote": f"def c := '\\\"'\ndef d := \" -- \" ++ {READ}\n",
    "raw-string": f'def r := r#"a" -- "# ++ {READ}\n',
    "raw-string-backslash": f'def r := r"\\" ++ " -- " ++ {READ}\n',
    "interpolated": f'def i := s!"a {{" -- "}} b" ++ {READ}\n',
    "interpolated-nested": f'def i := s!"{{s!"{{1}} -- "}}" ++ " -- " ++ {READ}\n',
    "interpolated-hole-brace": f'def i := s!"{{ {{ x := " -- " }} }}" ++ {READ}\n',
    "holes-no-prefix-says": f'def i := throwError "a {{" -- "}} b" ++ {READ}\n',
    "brace-in-a-plain-string": f'def i := "{{" ++ " -- " ++ "}}" ++ {READ}\n',
    "escaped-identifier": f"def « --b» := {READ}\n",
    "primed-word": f"def a' := 1\ndef b' := \" -- \" ++ {READ}\n",
    "nested-block-end": f"/- a /- b -/ c -/ def n := {READ} -- -/\n",
    "block-opener-in-a-line-comment": f"-- /-\ndef n := {READ} -- -/\n",
    "dashes-in-a-block": f"/- -- -/ def n := {READ}\n",
    "doc-comment-end": f"/--/ a -/ def n := {READ}\n",
    "dashes-inside-a-token": f"def l := do let a <--{READ}\n",
    "block-opener-inside-a-token": f"def l := {{ x : Int //-x = {READ} }}\n",
    "unterminated-comment": "/- NOTES.md\n",
    "unterminated-nested-comment": "/- /- -/ NOTES.md\n",
    "unterminated-string": '"NOTES.md\n',
    "unterminated-raw-string": 'r#"NOTES.md"\n',
    "unterminated-hole": 's!"{NOTES.md\n',
    "unterminated-escaped-identifier": "«NOTES.md\n",
    "no-char-literal": "def c := 'ab' -- NOTES.md\n",
    "number-then-quote": "def c := 1'a' -- NOTES.md\n",
}


@pytest.mark.parametrize("text", READ_AFTER.values(), ids=READ_AFTER)
def test_a_read_after_comment_like_text_is_still_a_read(tmp_path, text):
    """The stripper knows strings and fails towards a full run where it cannot tell (`lean_code`)."""
    planned_tree(tmp_path, reader("lean/Demo/Examples.lean", text))
    got = planned_previous(tmp_path, tmp_path, wrote("lean/NOTES.md"))
    assert isinstance(got, str) and got.startswith("its inputs differ (lean): lean/NOTES.md is no module"), got


COMMENTS = {
    "line": "-- {}\ndef n := 1\n",
    "line-after-code": "def n := 1 -- {}\n",
    "doc": "/-- {} -/\ndef n := 1\n",
    "module-doc": "/-! {} -/\n",
    "block": "/- {} -/\n",
    "nested-block": "/- a /- b -/ {} /- c -/ d -/\n",
    "block-closing-at-once": "/-/ {} -/\n",
    "doc-with-a-quote": "/-- it's \"{} -/\n",
    "comment-after-a-string": 'def s := "--" -- {}\n',
    "comment-after-a-char": "def c := '\"' -- {}\n",
    "comment-in-a-hole": 'def s := s!"{{1 /- {} -/}}"\n',
    "comment-with-unicode": "-- α {} ₁\n",
}


@pytest.mark.parametrize("named", ["tools/trust-classes.json", "tools/layer_policy.py", "lean/checkers.lock",
                                   "lean/NOTES.md", "lean/Demo/DEEP.md"], ids=lambda n: Path(n).name)
@pytest.mark.parametrize("comment", COMMENTS.values(), ids=COMMENTS)
def test_a_name_only_in_a_lean_comment_carries(tmp_path, comment, named):
    """Every input of `unread_by_build` searches the same text, under lean/ and in an outside --test file."""
    import trust_mutants as tm
    planned_tree(tmp_path)
    for where in ("lean/Demo/Examples.lean", "outside/T.lean"):
        (tmp_path / where).write_text(comment.format(Path(named).name))
        lake = tm.lake_reads(tmp_path, [tmp_path / "outside/T.lean"])
        assert Path(named).name.casefold() not in lake
        assert tm.check_only([named], set(), set(), lake) is None
        (tmp_path / where).write_text("\n")


@pytest.mark.parametrize("listing", ["readDir", "walkDir", "input_dir"])
def test_a_directory_listing_named_only_in_a_comment_is_no_listing(tmp_path, listing):
    import trust_mutants as tm
    (tmp_path / "lean/Demo").mkdir(parents=True)
    (tmp_path / "lean/Demo/Examples.lean").write_text(f"-- {listing}\n")
    assert tm.check_only(["lean/NOTES.md"], set(), set(), tm.lake_reads(tmp_path, [])) is None


@pytest.mark.parametrize(("name", "text"), [
    ("lean/lakefile.toml", "-- NOTES.md\n"), ("lean/lean-toolchain", "/- NOTES.md -/\n"),
    ("lean/lake-manifest.json", "/- NOTES.md -/\n"), ("outside/T.txt", "-- NOTES.md\n"),
], ids=["lakefile-toml", "toolchain", "manifest", "outside-test-not-lean"])
def test_a_file_that_is_no_lean_source_stays_whole(tmp_path, name, text):
    import trust_mutants as tm
    (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / "lean").mkdir(exist_ok=True)
    (tmp_path / name).write_text(text)
    lake = tm.lake_reads(tmp_path, [tmp_path / name] if name.startswith("outside/") else [])
    assert tm.check_only(["lean/NOTES.md"], set(), set(), lake) is not None


def test_a_lakefile_in_lean_loses_its_comments_and_a_symlink_keeps_its_target(tmp_path):
    import trust_mutants as tm
    (tmp_path / "lean").mkdir()
    (tmp_path / "lean/lakefile.lean").write_text("-- NOTES.md\n")
    assert tm.check_only(["lean/NOTES.md"], set(), set(), tm.lake_reads(tmp_path, [])) is None
    (tmp_path / "lean/Link.lean").symlink_to("NOTES.md")
    (tmp_path / "lean/NOTES.md").write_text("notes\n")
    assert tm.check_only(["lean/NOTES.md"], set(), set(), tm.lake_reads(tmp_path, [])) is not None


def test_text_nested_past_the_recursion_limit_stays_whole():
    """The comment before it is blanked, and the nesting is unsure, no crash."""
    import trust_mutants as tm
    deep = 's!"{' * 100_000
    assert tm.lean_code(f"-- a\n{deep} -- b\n") == f"    \n{deep} -- b\n"


def test_the_real_trees_comments_cost_no_full_run():
    """PROBE F2: lean/VE/Calc/Ties.lean's doc comment names the table, which forced a full run on every table change."""
    import trust_mutants as tm
    assert tm.check_only([tm.CLASS_TABLE], set(), set(), tm.lake_reads(tm.ROOT, [])) is None


def test_the_docstring_states_the_condition_where_it_claims_the_carry():
    """PROBE F3: the table and `PLAN_ONLY_TOOL` modules carry only when nothing Lake or Lean reads names them."""
    import trust_mutants as tm
    doc = " ".join(tm.__doc__.split())
    assert "generated inventory, trust_map's table, or a lean/*.md" not in doc
    assert ("Trust_map's table, those `PLAN_ONLY_TOOL` modules, a lean/*.md and lean/checkers.lock carry only when "
            "nothing Lake or Lean reads names them outside a comment") in doc


# Lean's own parser as the oracle for `lean_code`: every token it reads, with its byte position (doc comments left out).
LEAN_TOKENS = """import Lean
open Lean Parser

partial def tokens (stx : Syntax) (out : Array (Nat × String)) : Array (Nat × String) :=
  match stx with
  | .node _ k args =>
    if k == ``Command.docComment || k == ``Command.moduleDoc then out
    else args.foldl (fun o a => tokens a o) out
  | .atom (.original _ p _ _) v => out.push (p.byteIdx, v)
  | .ident (.original _ p _ _) raw _ _ => out.push (p.byteIdx, raw.toString)
  | _ => out

def main (paths : List String) : IO Unit := do
  initSearchPath (← findSysroot)
  let env ← importModules #[{module := `Lean}] {} (loadExts := true)
  let pmctx : ParserModuleContext := {env, options := {}}
  for path in paths do
    let ctx := mkInputContext (← IO.FS.readFile path) path
    let mut (head, state, log) ← parseHeader ctx
    let mut out := tokens head.raw #[]
    repeat
      let (cmd, s, l) := parseCommand ctx pmctx state log
      state := s
      log := l
      out := tokens cmd out
      if isTerminalCommand cmd then break
    IO.println (Json.compress (Json.mkObj [("errors", toJson log.hasErrors),
      ("tokens", toJson (out.map fun (p, v) => Json.arr #[toJson p, toJson v]))]))
"""
# (commands, whether `lean_code` is sure of them): comments and literals in every form it reads.
LEAN_PIECES = [
    ("-- it's \"a\n", True), ("/- a /- \" b -/ ' c -/\n", True), ("/-- doc ' -/\ndef d0 := 1\n", True),
    ("/-! module ' \" -/\n", True), ("/--/ doc -/\ndef d1 := 1\n", True), ("/-/ block -/\n", True),
    ("/- α -/ def d2 := 1 -- ₁\n", True), ('def s0 := "--" ++ " -- "\n', True), ('def s1 := " /- " /- c -/\n', True),
    ('def s2 := "\\" -- " -- c\n', True), ('def s3 := "gap\\\n   -- "\n', True), ('def s4 := "\\x22\\u0022--"\n', True),
    ("def c0 := '\"'\n", True), ("def c1 := '\\''\n", True), ("def c2 := '\\\\'\n", True), ("def c3 := '\\x41'\n", True),
    ("def c4 := '-'\n", True), ("def c5 := '\\u0041'\n", True), ("def c6 := '{'\n", True),
    ('def r0 := r" -- "\n', True), ('def r1 := r"\\" -- c\n', True), ('def r2 := r#"a" -- "#\n', True),
    ('def r3 := r##"a"# -- "##\n', True), ('def i0 := s!"a {" -- "} b"\n', True), ('def i1 := s!"{s!"{1} -- "} /-"\n', True),
    ('def i2 := s!"\\{ -- "\n', True), ('def i3 := s! "x {1 /- c -/} y"\n', True), ('def i4 := f!"{1}"\n', True),
    ('def i5 := m!"{" -- "}"\n', True), ('def i6 := s!"{1 -- c\n}"\n', True), ("def i7 := s!\"{'}'} -- \"\n", True),
    ('def i8 := s!"{ ({ a := " -- " } : T) }"\n', True), ('def p0 := "{x} -"\n', True), ('def p1 := "} {x - 1}"\n', True),
    ("def x' := x'' -- c\n", True), ("def α' := β₁' -- c\n", True), ("def é' := ℕ' -- c\n", True),
    ("def «a b--c» := 1\n", True), ("def n0 := 0xff + 1_000 + 1.5e3 + 0b1 + 0o7 -- c\n", True),
    ("def a.b' := a.«c d».e' -- c\n", True), ("def n1 := `x' -- c\n", True), ("def n2 := ``Nat.add' -- c\n", True),
    ('def q0 := "{" ++ " -- " ++ "}"\n', False), ('def t0 : IO Unit := throwError "a {" -- "}"\n', False),
    ("def l0 := do\n  let a <--1\n  pure a\n", False), ("def e0 := { x : Int //-x = 1 }\n", False), ("def j0 := (1)--c\n", False),
    ("def j1 := (1)/-c-/\n", False),
]


def test_lean_code_blanks_what_lean_skips_and_nothing_it_reads(tmp_path):
    """Differential, in the two directions, on every piece and on seeded mixtures of them: every token Lean's parser
    reads stands at its place in `lean_code`, and when the stripper is sure, nothing else is left."""
    import random

    import trust_mutants as tm
    pick = random.Random(20261105)
    documents = [[piece] for piece in LEAN_PIECES] + [pick.choices(LEAN_PIECES, k=pick.randint(2, 12)) for _ in range(300)]
    paths = []
    for i, pieces in enumerate(documents):
        paths.append(tmp_path / f"D{i}.lean")
        paths[-1].write_text("".join(text for text, _ in pieces))
    (tmp_path / "Tokens.lean").write_text(LEAN_TOKENS)
    done = subprocess.run(["lean", "--run", str(tmp_path / "Tokens.lean"), *map(str, paths)], capture_output=True, text=True,
                          timeout=HANG_TIMEOUT, cwd=ROOT / "lean", env={**os.environ, **PATH}, check=False)
    assert done.returncode == 0, done.stderr[-2000:]
    answers = [json.loads(line) for line in done.stdout.splitlines()]
    assert len(answers) == len(documents)
    for pieces, path, answer in zip(documents, paths, answers):
        raw = path.read_bytes()
        text, code = raw.decode(), tm.lean_code(raw.decode())
        assert not answer["errors"], text
        assert len(code) == len(text) and [i for i, c in enumerate(code) if c == "\n"] == [
            i for i, c in enumerate(text) if c == "\n"]
        read: set[int] = set()
        for position, token in answer["tokens"]:
            at = len(raw[:position].decode())
            assert code[at:at + len(token)] == token, (text, token)
            read |= set(range(at, at + len(token)))
        if all(sure for _, sure in pieces):
            assert {i for i, c in enumerate(code) if not c.isspace()} <= read, (text, code)


def test_no_file_is_unread_when_no_tree_was_read():
    import trust_mutants as tm
    assert tm.no_build_reads("lean/NOTES.md", "") and tm.no_build_reads("lean/checkers.lock", "")
    assert not tm.no_build_reads("lean/NOTES.md", None) and not tm.no_build_reads("docs/NOTES.md", "")
    assert tm.check_only(["lean/checkers.lock"], set(), set()) is not None  # no `lake` given: fails closed
    assert all(tm.check_only([name], set(), set()) is not None for name in tm.PLAN_INPUTS)


def test_a_file_that_cannot_be_read_is_a_full_run(tmp_path):
    """A broken symlink where a Lean file should be: `lake_reads` cannot read it, so it is no acceptance."""
    planned_tree(tmp_path, lambda root: (root / "lean/Demo/Broken.lean").symlink_to("../absent.lean"))
    got = planned_previous(tmp_path, tmp_path, wrote("lean/NOTES.md"))
    assert isinstance(got, str) and got.startswith("it cannot be read"), got


def test_the_plan_only_argument_still_holds():
    """Each line of `PLAN_ONLY_TOOL`'s argument, read off the sources of the modules the tool loads: only
    tools/check_lean_imports.py imports tools/layer_policy.py; the tool reads one name of that module, `imports`,
    which reaches neither of layer_policy's names, nor anything derived from them; layer_policy's module level has
    no effect on anything else and its ROOT is this repository. A module added to the set needs its own argument."""
    import ast
    import builtins
    import check_lean_imports
    import layer_policy
    import trust_mutants as tm
    assert tm.PLAN_ONLY_TOOL == {"tools/layer_policy.py"}
    code = "import json, sys; import trust_mutants; print(json.dumps([getattr(m, '__file__', None) for m in " \
           "list(sys.modules.values())]))"
    done = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=HANG_TIMEOUT,
                          env={**os.environ, "PYTHONPATH": str(ROOT / "tools")}, check=True)
    loaded = {Path(f).resolve() for f in json.loads(done.stdout.splitlines()[-1]) if f}
    tool = {p.relative_to(ROOT).as_posix(): ast.parse(p.read_text()) for p in loaded
            if p.is_relative_to(ROOT / "tools") or p.is_relative_to(ROOT / "lean")}
    assert "tools/layer_policy.py" in tool and "tools/check_lean_imports.py" in tool

    def imported(tree: ast.Module) -> set[str]:
        return {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names} | {
            n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
    assert sorted(f for f, tree in tool.items() if imported(tree) & {"layer_policy", "tools.layer_policy"}) == [
        "tools/check_lean_imports.py"]
    assert sorted(f for f, tree in tool.items() if imported(tree) & {"check_lean_imports", "tools.check_lean_imports"}
                  ) == ["tools/trust_mutants.py"]
    assert [[a.name for a in n.names] for n in ast.walk(tool["tools/trust_mutants.py"]) if isinstance(n, ast.ImportFrom)
            and n.module == "check_lean_imports"] == [["imports"]]
    # `imports` and what it reaches of its module: none of layer_policy's names or of what the module derives from them
    tree = tool["tools/check_lean_imports.py"]
    defs = {n.name: n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
    derived = {"ROOT", "lean_layer"}
    derived |= {t.id for n in tree.body if isinstance(n, ast.Assign) and {
        x.id for x in ast.walk(n.value) if isinstance(x, ast.Name)} & derived for t in n.targets
        if isinstance(t, ast.Name)}
    seen, todo = set(), ["imports"]
    while todo:
        names = {x.id for x in ast.walk(defs[todo.pop()]) if isinstance(x, ast.Name)}
        assert not names & derived, names & derived
        todo += [x for x in names - seen if x in defs]
        seen |= names
    assert check_lean_imports.imports("import A.B\n") == ["A.B"]
    # layer_policy's module level: pure tables and functions, and the repository's ROOT
    policy = tool["tools/layer_policy.py"]
    assert imported(policy) <= {"__future__", "ast", "functools", "pathlib", "tomllib"}, imported(policy)
    for n in policy.body:
        assert isinstance(n, (ast.Import, ast.ImportFrom, ast.Assign, ast.AnnAssign, ast.FunctionDef)) or (
            isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant)), type(n).__name__
    top = [n for n in policy.body if not isinstance(n, ast.FunctionDef)]
    named = {x.id for n in top for x in ast.walk(n) if isinstance(x, ast.Name)}
    assert not named & {"exec", "eval", "compile", "setattr", "delattr", "globals", "__import__", "open", "print"}
    assert named & set(dir(builtins)) <= {"frozenset", "set", "dict", "list", "tuple", "sorted", "range", "len", "str"}
    assert layer_policy.ROOT == ROOT


def rewritten(evidence: Path, out: Path, change) -> Path:
    data = json.loads(evidence.read_text())
    change(data["inputs"])
    out.write_text(json.dumps(data))
    return out


def plan_only_copy(package: Path, tmp_path: Path) -> Path:
    import shutil
    shutil.copytree(package, tmp_path / "copy", symlinks=True)
    return tmp_path / "copy"


def same_tree_other_base(root: Path) -> str:
    """A commit with the base's tree and another id: the plan selects the same lines, as after a sync that moved no
    Lean line of this branch."""
    done = subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit-tree", "HEAD~1^{tree}", "-p",
                           "HEAD~1", "-m", "moved"], cwd=root, capture_output=True, text=True, timeout=HANG_TIMEOUT,
                          check=True)
    return done.stdout.strip()


# name, the change to the copy of the package, or to PREV's inputs; the arguments; `changed`, `plan_only`
def module_was_other(inputs: dict) -> None:
    inputs["tool"] = OTHER_DIGEST
    inputs["tool_files"]["tools/layer_policy.py"] = OTHER_DIGEST


REAL_CARRIES = ["plan-only-module", "base", "table", "lock", "md"]


def test_rescore_on_a_real_tree_carries_across_every_plan_only_input_and_agrees_with_a_full_run(
        package, default_run, tmp_path, tmp_path_factory):
    """All of them at once, on the package's whole evidence: every KILLED verdict is carried (it has no INVALID one),
    each other verdict runs, and all of them are what a full run on that tree gives."""
    root = plan_only_copy(package, tmp_path)
    moved = same_tree_other_base(root)
    (root / "tools/trust-classes.json").write_text('{"comment": "no class moved", "modules": {}}\n')
    (root / "lean/checkers.lock").write_text("{}\n")
    (root / "lean/NOTES.md").write_text("notes\n")
    prev = json.loads((tmp_path_factory.getbasetemp() / "default-evidence.json").read_text())
    path = rewritten(tmp_path_factory.getbasetemp() / "default-evidence.json", tmp_path / "prev.json", module_was_other)
    done, data = rescored(root, tmp_path / "rescore", path, "--base", moved)
    full_done, full = tool(root, tmp_path / "full", "--base", moved)
    was = {m["id"]: m for m in prev["mutants"]}
    expected = {i for i, m in was.items() if m["raw_status"] in ("KILLED", "INVALID")}
    assert {m["raw_status"] for m in was.values()} >= {"KILLED", "SURVIVOR"}, was  # an INVALID one: the sweep below
    assert {m["id"] for m in data["mutants"] if m.get("carried") == "checks"} == expected, (done.stdout, data["rescore"])
    assert not [m for m in data["mutants"] if m["id"] not in expected and ("reused_from" in m or "carried" in m)]
    assert {k: data["rescore"][k] for k in ("head", "mode", "changed", "plan_only", "reused", "rerun")} == {
        "head": prev["head"], "mode": "checks", "changed": ["lean/NOTES.md", "lean/checkers.lock",
                                                             "tools/trust-classes.json"],
        "plan_only": ["tools/layer_policy.py", "base", "lean/NOTES.md", "lean/checkers.lock",
                      "tools/trust-classes.json"], "reused": len(expected), "rerun": len(was) - len(expected)}
    assert "plan-only: tools/layer_policy.py, base, lean/NOTES.md" in done.stdout, done.stdout
    assert [(m["id"], m["status"], m["detail"].split(": ")[0]) for m in data["mutants"]] == [
        (m["id"], m["status"], m["detail"].split(": ")[0]) for m in full], (done.stdout, full_done.stdout)
    assert done.returncode == full_done.returncode


@pytest.mark.parametrize("name", REAL_CARRIES)
def test_rescore_on_a_real_tree_carries_across_each_plan_only_input(package, prefix_run, tmp_path, name):
    """One at a time, on a prefix of four KILLED mutants and one SURVIVOR: the KILLED ones carried, the other run."""
    root, base, prev = plan_only_copy(package, tmp_path), [], prefix_run
    plan_only = [{"plan-only-module": "tools/layer_policy.py", "base": "base", "table": "tools/trust-classes.json",
                  "lock": "lean/checkers.lock", "md": "lean/NOTES.md"}[name]]
    if name == "plan-only-module":
        prev = rewritten(prefix_run, tmp_path / "prev.json", module_was_other)
    elif name == "base":
        base = ["--base", same_tree_other_base(root)]
    else:
        (root / plan_only[0]).write_text('{"comment": "no class moved", "modules": {}}\n')
    done, data = rescored(root, tmp_path / "rescore", prev, "--max-mutants", "5", *base)
    rows = {m["id"]: m for m in json.loads(prefix_run.read_text())["mutants"]}
    killed = {i for i, m in rows.items() if m["raw_status"] == "KILLED"}
    assert len(killed) == 4, rows
    assert {m["id"] for m in data["mutants"] if m.get("carried") == "checks"} == killed, (done.stdout, done.stderr)
    assert not [m for m in data["mutants"] if m["id"] not in killed and "reused_from" in m]
    assert (data["rescore"]["mode"], data["rescore"]["plan_only"], data["rescore"]["reused"], data["rescore"]["rerun"]
            ) == ("checks", plan_only, 4, 1), data["rescore"]
    assert data["rescore"]["changed"] == ([] if name in ("plan-only-module", "base") else plan_only)
    assert [m["status"] for m in data["mutants"]][:5] == [rows[f"M{i:03d}"]["status"] for i in range(1, 6)]


def test_rescore_on_a_real_tree_across_the_tool_itself_is_a_full_run(package, prefix_run, tmp_path):
    def tool_was_other(inputs: dict) -> None:
        inputs["tool"] = OTHER_DIGEST
        inputs["tool_files"]["tools/trust_mutants.py"] = OTHER_DIGEST
    prev = rewritten(prefix_run, tmp_path / "prev.json", tool_was_other)
    done, data = rescored(package, tmp_path / "rescore", prev, "--max-mutants", "5")
    assert (data["rescore"]["mode"], data["rescore"]["reused"], data["rescore"]["rerun"]) == ("full", 0, 5), done.stdout
    assert data["rescore"]["full_run"] == "its inputs differ (tool): tools/trust_mutants.py"
    assert "plan_only" not in data["rescore"] and not [m for m in data["mutants"] if "reused_from" in m]


def test_rescore_on_a_real_tree_across_a_table_that_moves_the_mutants_is_a_full_run(package, prefix_run, tmp_path):
    """The table takes `small` (the first four mutants) out of the selection: the same bytes-level case as the carry
    above, and the mutant list refuses it."""
    root = plan_only_copy(package, tmp_path)
    (root / "tools/trust-classes.json").write_text('{"modules": {"Demo/Defs.lean": {"T": ["Demo.small"]}}}\n')
    done, data = rescored(root, tmp_path / "rescore", prefix_run, "--max-mutants", "5")
    assert (data["rescore"]["mode"], data["rescore"]["reused"]) == ("full", 0), (done.stdout, done.stderr)
    assert data["rescore"]["full_run"] == "its mutants are not this tree's"


def test_rescore_on_a_real_tree_across_a_base_that_moves_the_mutants_is_a_full_run(package, prefix_run, tmp_path):
    """The base itself holds the selected lines: no mutant is left, so the list refuses it."""
    done, data = rescored(package, tmp_path / "rescore", prefix_run, "--base", "HEAD")
    assert (data["rescore"]["mode"], data["rescore"]["reused"]) == ("full", 0), (done.stdout, done.stderr)
    assert data["rescore"]["full_run"] == "its mutants are not this tree's"


@pytest.fixture
def plan_only_sweep(sharded, monkeypatch):
    """`sharded` whose `inputs` hold `tool_files`, and PREV: the evidence of its six mutants that run."""
    tm, real = sharded.tm, sharded.tm.inputs

    def inputs(*args):
        return {**real(*args), "tool_files": {"tools/layer_policy.py": "1", "tools/trust_mutants.py": "2"}}
    monkeypatch.setattr(tm, "inputs", inputs)
    prev = sharded.tmp / "prev.json"
    assert sharded("--json", prev, "--max-mutants", 6)[0] == 1
    return sharded, prev


# what PREV's inputs held, what the run makes of it (the plan-only names, or the full run's reason)
SWEEPS = [
    ("module", {"tool": "t0", "tool_files": {"tools/layer_policy.py": "0", "tools/trust_mutants.py": "2"}},
     ["tools/layer_policy.py"]),
    ("base", {"base": OTHER_BASE}, ["base"]),
    ("named-table", {"files": {"lean/Demo/Defs.lean": "1", "tools/trust-classes.json": "0"}, "lean": "l0"},
     ["tools/trust-classes.json"]),
    ("unread-md", {"files": {"lean/Demo/Defs.lean": "1", "lean/NOTES.md": "0"}, "lean": "l0"}, ["lean/NOTES.md"]),
    ("the-tool", {"tool": "t0", "tool_files": {"tools/layer_policy.py": "1", "tools/trust_mutants.py": "0"}},
     "its inputs differ (tool): tools/trust_mutants.py"),
    ("old-record", {"tool": "t0", "tool_files": None}, "its inputs differ (tool)"),
]


@pytest.mark.parametrize(("name", "old", "says"), SWEEPS, ids=[s[0] for s in SWEEPS])
def test_a_plan_only_rescore_in_one_run_and_in_parts_gives_one_record(plan_only_sweep, name, old, says):
    """The whole path in `main` and `--merge` (no Lean): on a carry only the SURVIVOR and UNKNOWN verdicts run, the
    record names what crossed, and --merge accepts parts with no changed file and gives the one run's record; a full
    run runs all of them and names no plan-only input."""
    go, prev = plan_only_sweep
    data = json.loads(prev.read_text())
    data["inputs"].update(old)
    data["inputs"] = {k: v for k, v in data["inputs"].items() if v is not None}
    prev.write_text(json.dumps(data))
    one = go.tmp / "one.json"
    code, _, _, ran, _ = go("--json", one, "--max-mutants", 6, "--rescore", prev)
    record = json.loads(one.read_text())
    rescore = record["rescore"]
    if isinstance(says, list):
        assert rescore["mode"] == "checks" and rescore["plan_only"] == says and "full_run" not in rescore, rescore
        assert sorted(ran) == ["M002", "M003", "M005"]
        assert {m["id"] for m in record["mutants"] if m.get("carried") == "checks"} == {"M001", "M004", "M006"}
        assert (rescore["reused"], rescore["rerun"]) == (3, 3)
    else:
        assert rescore["mode"] == "full" and rescore["full_run"] == says and "plan_only" not in rescore, rescore
        assert sorted(ran) == [f"M{i:03d}" for i in range(1, 7)]
    merged = go.tmp / "merged.json"
    assert go.tm.main(["--merge", str(merged), *map(str, parts(go, 3, "--max-mutants", 6, "--rescore", prev))]) == code
    together = json.loads(merged.read_text())
    assert {k: v for k, v in together.items() if k not in RUN_FACTS} == {
        k: v for k, v in record.items() if k not in RUN_FACTS}


def test_a_resume_needs_the_same_plan_only_facts(plan_only_sweep, capsys):
    """--resume compares --rescore's facts: a record that names another plan-only input is another run's."""
    go, prev = plan_only_sweep
    data = json.loads(prev.read_text())
    data["inputs"]["base"] = OTHER_BASE
    prev.write_text(json.dumps(data))
    first = go.tmp / "first.json"
    go("--json", first, "--max-mutants", 6, "--rescore", prev)
    assert go("--json", go.tmp / "kept.json", "--max-mutants", 6, "--rescore", prev, "--resume", first)[3] == []
    assert json.loads((go.tmp / "kept.json").read_text())["resumed"]["kept"] == 6
    forged = json.loads(first.read_text())
    forged["rescore"]["plan_only"] = ["tools/layer_policy.py"]
    first.write_text(json.dumps(forged))
    _, out, _, ran, _ = go("--json", go.tmp / "again.json", "--max-mutants", 6, "--rescore", prev, "--resume", first,
                           capsys=capsys)
    assert "its --rescore is not this run's" in out and sorted(ran) == ["M002", "M003", "M005"]
