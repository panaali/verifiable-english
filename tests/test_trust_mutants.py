"""tools/trust_mutants.py on a tiny Lean package (speed-trustmut step 3): a well-guarded definition has no survivor,
a guard over `[]` leaves survivors, a failing proof is no kill, --allow suppresses exactly its operator, the mutants
are built in a scratch copy (the checkout's bytes and times are unchanged), and --max-mutants lists the rest as
NOT RUN. The package's declaration and predicate lists come from tools/lean_statements.py's own per-module script."""
from __future__ import annotations

import json
import os
from pathlib import Path
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

/-- info: 6 -/
#guard_msgs (whitespace := lax) in
#eval twice 3

#guard_msgs in example : twice 2 = 4 := by decide

def loneFin : Fin 1 := ⟨lone 0, by decide⟩
"""
STATED = ["Demo.Far.half_four", "Demo.double_eq", "Demo.double_two", "Demo.four"]


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


@pytest.fixture(scope="module")
def package(tmp_path_factory) -> Path:
    root = tmp_path_factory.mktemp("package")
    (root / "lean/Demo/Far").mkdir(parents=True)
    (root / "tools").mkdir()
    (root / "lean/lean-toolchain").write_text((ROOT / "lean/lean-toolchain").read_text())
    (root / "lean/lakefile.toml").write_text('name = "demo"\n\n[[lean_lib]]\nname = "Demo"\nglobs = ["Demo.*"]\n')
    (root / ".gitignore").write_text(".lake/\n")
    (root / "tools/trust-classes.json").write_text('{"modules": {}}\n')
    git(root, "init", "-q")
    git(root, "add", ".")
    git(root, "commit", "-qm", "base")
    for name, text in (("Defs", DEFS), ("Proofs", PROOFS), ("Examples", EXAMPLES), ("Far/Check", FAR)):
        (root / f"lean/Demo/{name}.lean").write_text(text)
    dump(root, tmp_path_factory.mktemp("dump"))
    git(root, "add", ".")
    git(root, "commit", "-qm", "head")
    return root


def tool(root: Path, scratch: Path, *args: str) -> tuple[subprocess.CompletedProcess, list[dict]]:
    out = scratch / "evidence.json"
    scratch.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, **PATH, "TMPDIR": str(scratch), "VE_LEAN_SHARE": "off"}
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
    done, mutants = tool(package, tmp_path_factory.mktemp("run"))
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
    assert "SURVIVOR lean/Demo/Defs.lean:7 Demo.evens list-empty: xs.filter (· % 2 == 0) -> []" in printed


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
    """Review F6: a `#guard_msgs` around an `#eval` (its spec in parentheses) or a `decide` example is a check."""
    _, mutants, _, _ = default_run
    twice = of(mutants, "twice")
    assert {m["operator"] for m in twice} == {"lit-plus", "lit-minus"}
    assert all(m["status"] == "KILLED" and m["detail"].split(": ")[0] in (
        "lean/Demo/Examples.lean:18", "lean/Demo/Examples.lean:21") for m in twice), twice


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
    ("example : f 1 = 2 := by\n  simp [f] /- a\n  b -/\n-- c\n", 4, "example : f 1 = 2  := sorry\n\n\n-- c\n")])
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
    ("command", "open Demo", "other")])
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
    `#eval` reads `double_eq`, which the tool cuts up front in Demo/Defs.lean, fails either way: the mutants no
    check kills are UNKNOWN, never KILLED; a mutant that breaks the other file is KILLED by it."""
    (package / "outside").mkdir(exist_ok=True)
    (package / "outside/Value.lean").write_text("import Demo.Defs\n#guard Demo.small 2\n#guard !Demo.small 3\n")
    (package / "outside/Reads.lean").write_text(
        "import Demo.Defs\n"
        "#eval (⟨0, Nat.lt_of_lt_of_eq (by decide) (Demo.double_eq 1).symm⟩ : Fin (Demo.double 1)).val\n")
    done, mutants = tool(package, tmp_path / "run", "--test", "outside/Value.lean", "--test", "outside/Reads.lean")
    before = {m["id"]: m["status"] for m in default_run[1]}
    assert [m for m in mutants if "Reads.lean" in m["detail"] and m["status"] != "UNKNOWN"] == [], done.stdout
    assert "SURVIVOR" in {before[m["id"]] for m in mutants if m["file"] == "Demo/Defs.lean"}
    for m in mutants:
        if before[m["id"]] == "SURVIVOR" and m["file"] == "Demo/Defs.lean":  # Reads.lean imports it only
            assert m["status"] == "UNKNOWN" and m["detail"].endswith("Reads.lean fails without the mutant too"), m
        else:
            assert m["status"] == before[m["id"]], m


@pytest.mark.parametrize("limit", [0, 3])
def test_max_mutants_lists_the_rest_as_not_run(package, tmp_path, limit):
    """A budget of 0 runs nothing and never exits 0 (3: incomplete)."""
    done, mutants = tool(package, tmp_path / "run", "--max-mutants", str(limit))
    ran = [m for m in mutants if m["status"] != "NOT RUN"]
    assert len(ran) == limit and len(mutants) > limit
    printed = [line for line in done.stdout.splitlines() if line.startswith("NOT RUN ")]
    assert len(printed) == len(mutants) - limit
    assert done.returncode == (1 if any(m["status"] == "SURVIVOR" for m in ran) else 3)


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


# Review F7's truth table: every command form `classify` can see, its class, and two readings of a definition: its
# value (`{v}`, which a check must catch) and a proof the tool cuts (`{p}`, through the witness `{w}`: up front in
# the mutated module, when the mutant breaks it in another). An outcome a cut or broken proof can change must never
# be a kill. `None`: the form has no proof reading of its own (its tactic block is the proof it reads).
FORMS = [  # (form, class, value reading, proof reading)
    ("#guard", "check", "#guard {v} == {e}", "#guard {w}.val == 0"),
    ("#guard_expr", "check", "#guard_expr {v} =~ {e}", "#guard_expr {w}.val =~ 0"),
    ("#eval", "check", '#eval (do if {v} != {e} then throw (IO.userError "changed") : IO Unit)', "#eval {w}.val"),
    ("#reduce", "check", "#reduce {v}", "#reduce {w}.val"),
    ("#check", "check", "#check (rfl : {v} = {e})", "#check {w}"),
    ("#print", "proof", "#print {d}", "#print {p}"),
    ("#print axioms", "proof", "#print axioms {d}", "#print axioms {p}"),
    ("decide example", "check", "example : {v} = {e} := by decide", "example : {w}.val = 0 := by decide"),
    ("rfl example", "check", "example : {v} = {e} := rfl", "example : {w}.val = 0 := rfl"),
    ("tactic example", "proof", "example : {v} = {e} := by {tac}", "example : {w}.val = 0 := by {tac}"),
    ("tactic theorem", "proof", "theorem {id}_t : {v} = {e} := by {tac}", "theorem {id}_t : {w}.val = 0 := by {tac}"),
    ("#guard with a tactic block", "proof", "#guard (⟨0, by {tac}⟩ : Fin (2 - {n})).val == 0", None),
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
    """One row per form, reading, wrapping and setting, with the status its definition's mutants must have: KILLED
    when a check compares the value (a bare or info-dropping `#reduce` compares nothing), else SURVIVOR. With
    `group`, the rows that must not kill share one definition per wrapping, setting and reading."""
    rows = []
    for setting in ("mutated", "other"):
        for wrap in WRAPS:
            for reads in ("value", "proof"):
                for form, cls, value, proof in FORMS:
                    if (text := value if reads == "value" else proof) is not None:
                        kills = reads == "value" and cls == "check" and (form != "#reduce" or wrap == "doc")
                        rows.append({"form": form, "class": cls, "reads": reads, "wrap": wrap, "setting": setting,
                                     "expected": "KILLED" if kills else "SURVIVOR", "text": text,
                                     "key": (setting, wrap, reads, form if kills or not group else "")})
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
    (root / "lean/Demo/M").mkdir(parents=True)
    (root / "lean/Demo/O").mkdir(parents=True)
    (root / "tools").mkdir()
    (root / "lean/lean-toolchain").write_text((ROOT / "lean/lean-toolchain").read_text())
    (root / "lean/lakefile.toml").write_text('name = "demo"\n\n[[lean_lib]]\nname = "Demo"\nglobs = ["Demo.*"]\n')
    (root / ".gitignore").write_text(".lake/\n")
    (root / "tools/trust-classes.json").write_text('{"modules": {}}\n')
    git(root, "init", "-q")
    git(root, "add", ".")
    git(root, "commit", "-qm", "base")
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
                lines += [command, ""]
                continue
            if row["wrap"] == "doc":
                lines += ["/--", *"\n---\n".join(said).split("\n"), "-/"] if said else ["/-- -/"]
            row["line"] = len(lines) + 2
            lines += ["#guard_msgs (drop info) in" if said and row["wrap"] == "wrapped" else "#guard_msgs in", command,
                      ""]
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
    dump(root, folder, [])
    git(root, "add", ".")
    git(root, "commit", "-qm", "head")
    return rows


@pytest.mark.parametrize("wrap", WRAPS)
@pytest.mark.parametrize(("form", "cls", "value", "proof"), FORMS)
def test_classify_truth_table(form, cls, value, proof, wrap):
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
    ("example : f 1 = 1 := by exact (by decide)", "proof")])
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
    ('#eval "a\n-- b"\n#guard_msgs in #print axioms f\n', 3, 3, '#eval "a\n-- b"\n' + " " * 30 + "\n")])
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
    docstring: a check that compares the value kills, and nothing a cut or broken proof can change ever does."""
    _, rows, done, mutants = table_run
    module = {"mutated": "lean/Demo/M/Defs.lean", "other": "lean/Demo/O/Checks.lean"}
    space = {"mutated": "Demo.M", "other": "Demo.O"}
    statuses = {m["definition"]: (m["status"], m["detail"].split(": ")[0]) for m in mutants}
    assert len(statuses) == len(mutants) == len({(r["setting"], r["d"]) for r in rows}), done.stdout
    for row in rows:
        status, where = statuses[f"{space[row['setting']]}.{row['d']}"]
        lines = range(row["line"] - (row["wrap"] != "bare"), row["line"] + 1)  # the wrapper's or the command's
        places = [f"{module[row['setting']]}:{n}" for n in lines] if row["expected"] == "KILLED" else [""]
        assert status == row["expected"] and where in places, (row, done.stdout)
