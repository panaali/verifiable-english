#!/usr/bin/env python3
"""Mechanical mutants of the trusted Lean definitions a branch adds or changes, and the survivors (standing ruling
R16 signs trusted growth only when "every new trusted definition is exercised by a test that can fail").

    uv run python tools/trust_mutants.py [--base REV] [--jobs N] [--max-mutants N] [--test FILE ...]
                                         [--allow FILE] [--json OUT] [--root DIR]

Selection: the declarations tools/trust_map.py counts as trusted on the tree (K, S, untied [V], unclassified),
not theorems or checks, whose lines hold a line the tree adds or changes over REV (default: the merge base of HEAD
and main). Each is mutated inside its compiled range (lean/declarations.txt), comments and strings excluded, by
the operators of `OPERATORS` (`mutants`). A mutant Lean does not elaborate is INVALID, never a kill or a survivor:
the compiler, not this tool's reading of the text, decides what a mutant means.

Checks: a `#guard` or `#guard_msgs` command, an `example`, and a theorem proved by `decide`, `native_decide` or
`rfl` alone (`CHECK_PROOF`); and every Lean file named with --test (any error in it). Each mutant is built in a
private scratch copy of lean/ (its build restored from tools/lean_share.py's stored build of this tree when there is
one, else copied from lean/.lake; the checkout is only read): `lake build` of the mutated module and of every module
that imports it and holds checks. The mutant is
- KILLED when Lean reports an error inside a check (or a --test file fails);
- INVALID when the error is inside the mutated declaration;
- SURVIVOR when every check passes. A failing proof is no kill (BUILDER-CHECKLIST 3): a theorem whose proof fails
  outside the checks has its proof replaced by `sorry` in the scratch copy, and the build runs again, so the
  checks after it still run;
- UNKNOWN when anything else fails (an error outside every check, proof and the mutated declaration, a statement
  that fails even with its proof cut, a failed build with no located error);
- NOT RUN past --max-mutants (the order gives every definition its first operators before any its later ones).

Each SURVIVOR and UNKNOWN prints as `<STATUS> <file>:<line> <definition> <operator>: <before> -> <after>`, unless
--allow FILE lists its definition and operator with a reason: {"allow": [{"definition": "VE.X.f", "operator":
"lt-le", "reason": "one line: why the mutant is equivalent"}]}. Exit 0: every mutant ran and none is left; 1: a
survivor or UNKNOWN is left; 3: none is left but some did NOT RUN; 2: the tool cannot run (stale dumps, a check
that fails without a mutant). --json OUT writes every mutant with its status as evidence. This is builder and
reviewer evidence only: no gate, merge train or nightly reads it.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
import difflib
import json
import os
from pathlib import Path
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "lean"))
from audit import code_only  # noqa: E402
from check_lean_imports import imports  # noqa: E402
from lean_statements import declaration_list, module_name, source_hash, sources  # noqa: E402
from tools import lake_outputs, lean_share, trust_map  # noqa: E402

OPEN, CLOSE = "([{⟨", ")]}⟩"
CHECK_COMMAND = re.compile(r"(?m)^\s*(?:@\[[^\]]*\]\s*)*(?:#guard_msgs|#guard|example)\b")
CHECK_PROOF = re.compile(r":=\s*(?:by\s+)?(?:decide|native_decide|rfl)(?:\s+\+\w+)*\s*$")
ERROR = re.compile(r"^error: (?:\./)*(\S+?\.lean):(\d+):\d+: (.*)$", re.M)
STOP_WORDS = {"then", "else", "do", "with", "in", "fun", "if", "let", "match", "return", "throw", "by", "at",
              "from", "where", "for", "unless", "mut", "have", "show"}
LIST_METHODS = ("find?", "any", "all", "contains", "map", "filter", "flatMap", "filterMap", "length", "head?",
                "isEmpty", "foldl", "foldr", "zip", "lookup", "elem", "isPrefixOf", "take", "drop", "reverse", "sum",
                "count", "findSome?", "eraseDups", "dropLast", "tail", "getLast?", "mapM", "forM", "lookup", "join")
LIST_RESULTS = {"map", "filter", "flatMap", "filterMap", "take", "drop", "reverse", "eraseDups", "dropLast", "tail",
                "zip"}
CUTS = {"list-empty": None, "list-first": ".take 1", "list-drop-last": ".dropLast", "list-last": ".reverse.take 1",
        "list-drop-first": ".drop 1"}
# Each operator with its tier: --max-mutants keeps the earlier tiers of every definition first.
OPERATORS = {**dict.fromkeys(("arm-true", "arm-false", "arm-default", "body-true", "body-false", "not-drop",
                              "and-or", "or-and", "lt-le", "le-lt", "lt-eq", "le-eq", "eq-le", "gt-ge", "ge-gt",
                              "eq-ne", "ne-eq", "all-any", "any-all", "bool-flip", "lit-plus", "lit-minus",
                              "list-empty", "append-left", "append-right"), 1),
             "list-first": 2, "list-drop-last": 2, "list-last": 3, "list-drop-first": 3}
TOKENS = [  # (operator, pattern on the blanked code, replacement)
    ("not-drop", r"¬\s*|(?<![\w'!?)\]⟩])!(?=[\w(·])", ""), ("and-or", r"∧", "∨"),
    ("and-or", r"(?<![&|])&&(?![&|])", "||"), ("or-and", r"∨", "∧"), ("or-and", r"(?<!\|)\|\|(?!\|)", "&&"),
    ("lt-le", r"(?<![<-])<(?![-|$*;=<>])", "≤"), ("lt-eq", r"(?<![<-])<(?![-|$*;=<>])", "="),
    ("le-lt", r"≤|(?<![<])<=(?![>])", "<"), ("le-eq", r"≤|(?<![<])<=(?![>])", "="),
    ("gt-ge", r"(?<![=\-|>$*;])>(?![>=])", "≥"), ("ge-gt", r"≥|(?<![>])>=", ">"),
    ("eq-le", r"(?<![:=!<>])=(?![=>])", "≤"), ("eq-ne", r"(?<![:=!<>])=(?![=>])", "≠"),
    ("eq-ne", r"(?<![=])==(?![=])", "!="), ("ne-eq", r"≠", "="), ("ne-eq", r"!=", "=="),
    ("all-any", r"(?<=\.)all\b", "any"), ("any-all", r"(?<=\.)any\b", "all")]
BOOLS = {"true": "false", "false": "true", "True": "False", "False": "True"}


@dataclass
class Mutant:
    id: str
    file: str  # under lean/
    line: int
    definition: str
    operator: str
    start: int  # offsets in the file's text
    end: int
    lines: tuple[int, int]  # the mutated declaration's lines
    before: str
    after: str
    status: str = "NOT RUN"
    detail: str = ""


def group_end(t: str, i: int) -> int:
    """The index after the bracket group opening at t[i]."""
    depth = 0
    for j in range(i, len(t)):
        depth += (t[j] in OPEN) - (t[j] in CLOSE)
        if depth == 0:
            return j + 1
    return len(t)


def group_start(t: str, j: int) -> int:
    """The index of the bracket that opens the group closing at t[j - 1]."""
    depth = 0
    for i in range(j - 1, -1, -1):
        depth += (t[i] in CLOSE) - (t[i] in OPEN)
        if depth == 0:
            return i
    return 0


def name_char(t: str, i: int) -> bool:
    c = t[i]
    return c.isalnum() or c in "_'?.·" or c == "!" and i > 0 and t[i - 1].isalnum()


def atom_before(t: str, j: int, lo: int) -> int | None:
    """The start of the atom (a dotted name, or a bracket group with any dotted names after it) that ends at j."""
    i = j
    while i > lo and name_char(t, i - 1):
        i -= 1
    if i > lo and t[i - 1] in CLOSE and (i == j or t[i] == "."):
        i = group_start(t, i)
    return i if i < j and t[i] != "." else None


def atom_after(t: str, i: int, hi: int) -> int:
    """The end of the atom starting at t[i] (i itself when there is none)."""
    j = group_end(t, i) if t[i] in OPEN else i
    while j < hi and name_char(t, j):
        j += 1
    word = t[i:j]
    return i if word in STOP_WORDS or word.startswith(".") else min(j, hi)


def application_after(t: str, i: int, hi: int) -> int:
    """The end of an atom and the arguments applied to it on its line."""
    j = atom_after(t, i, hi)
    while j > i and j + 1 < hi and t[j] == " " and (k := atom_after(t, j + 1, hi)) > j + 1:
        j = k
    return j


def depth0(t: str, lo: int, hi: int, pattern: str) -> int | None:
    """The first match of `pattern` in t[lo:hi] outside every bracket group."""
    depth = 0
    for i in range(lo, hi):
        depth += (t[i] in OPEN) - (t[i] in CLOSE)
        if depth == 0 and re.match(pattern, t[i:hi]):
            return i
    return None


def cut(atom: str, chain: str | None) -> str:
    if chain is None:
        return "[]"
    single = re.fullmatch(r"[\w'?.!]+", atom) or atom[0] in OPEN and group_end(atom, 0) == len(atom)
    return f"({atom}{chain})" if single else f"(({atom}){chain})"


def mutants(text: str, kind: str, lo: int, hi: int) -> list[tuple[str, int, int, str]]:
    """(operator, start, end, replacement) for one declaration at text[lo:hi]."""
    t = code_only(text)
    out = [(op, lo + m.start(), lo + m.end(), new) for op, pattern, new in TOKENS
           for m in re.finditer(pattern, t[lo:hi])]
    out += [("bool-flip", lo + m.start(), lo + m.end(), BOOLS[m[0]])
            for m in re.finditer(r"(?<![\w.'])(?:true|false|True|False)(?![\w'])", t[lo:hi])]
    for m in re.finditer(r"(?<![\w.'])\d+(?![\w.])", t[lo:hi]):
        out.append(("lit-plus", lo + m.start(), lo + m.end(), str(int(m[0]) + 1)))
        if int(m[0]):
            out.append(("lit-minus", lo + m.start(), lo + m.end(), str(int(m[0]) - 1)))
    lists: list[tuple[int, int]] = []
    if kind in ("def", "instance", "opaque"):
        assign = depth0(t, lo, hi, r":=")
        arm = re.search(r"(?m)^\s*\|", t[lo:hi])
        head_end = min(x for x in (assign, lo + arm.start() if arm else None, hi) if x is not None)
        colon, depth = None, 0
        for i in range(lo, head_end):
            depth += (t[i] in OPEN) - (t[i] in CLOSE)
            colon = i if depth == 0 and t[i] == ":" and t[i + 1] != "=" else colon
        result = re.split(r"→|->", t[colon + 1:head_end])[-1].strip() if colon is not None else ""
        consts = {"Prop": ("True", "False"), "Bool": ("true", "false")}.get(result)
        if assign is not None and (arm is None or assign < lo + arm.start()):
            stop = depth0(t, assign, hi, r"\b(?:where|termination_by|decreasing_by)\b") or hi
            body = (assign + 2 + len(t[assign + 2:stop]) - len(t[assign + 2:stop].lstrip()), stop)
            body = (body[0], body[0] + len(t[body[0]:stop].rstrip()))
            if consts:
                out += [("body-true", *body, consts[0]), ("body-false", *body, consts[1])]
            if result.startswith("List") and body[0] < body[1]:
                lists.append(body)
        elif arm is not None:
            arms = [lo + a.start() for a in re.finditer(r"(?m)^[ \t]*\|", t[lo:hi])]
            spans = []
            for a, b in zip(arms, [*arms[1:], hi]):
                arrow = depth0(t, a + t[a:b].index("|") + 1, b, r"=>")
                if arrow is not None:
                    rhs = t[arrow + 2:b]
                    spans.append((t[a:arrow], arrow + 2 + len(rhs) - len(rhs.lstrip()), arrow + 2 + len(rhs.rstrip())))
            default = spans[-1] if spans and re.fullmatch(r"\s*\|[\s_,]*", spans[-1][0]) else None
            for pattern, s, e in spans:
                if consts:
                    out += [("arm-true", s, e, consts[0]), ("arm-false", s, e, consts[1])]
                elif default and (s, e) != default[1:]:
                    out.append(("arm-default", s, e, text[default[1]:default[2]]))
    for m in re.finditer(r"\.(" + "|".join(re.escape(x) for x in LIST_METHODS) + r")(?![\w?!'])", t[lo:hi]):
        dot = lo + m.start()
        start = atom_before(t, dot, lo)
        if start is not None:
            lists.append((start, dot))
            if m[1] in LIST_RESULTS:
                lists.append((start, application_after(t, start, hi)))
    for m in re.finditer(r"\bfor \w+ in ", t[lo:hi]):
        s = lo + m.end()
        e = t.find(" do", s, hi)
        if e > s:
            lists.append((s, e))
    for m in re.finditer(r" \+\+ ", t[lo:hi]):
        op = lo + m.start()
        left, right = atom_before(t, op, lo), application_after(t, op + 4, hi)
        if left is not None and right > op + 4:
            lists += [(left, op), (op + 4, right)]
            out += [("append-left", op, right, ""), ("append-right", left, op + 4, "")]
    for m in re.finditer(r"(?<![\w'?!)\]@#])\[(?!\])", t[lo:hi]):
        lists.append((lo + m.start(), group_end(t, lo + m.start())))
    for s, e in dict.fromkeys(lists):
        atom = text[s:e]
        if atom.startswith("·") and s > 0 and t[s - 1] == "(":  # `(·.head.contains a)`: name the argument first
            for op, chain in CUTS.items():
                out.append((op, s - 1, e, f"(fun x_tm => {cut('x_tm' + atom[1:], chain)}"))
        elif not atom.startswith("·") and atom.strip():
            out += [(op, s, e, cut(atom, chain)) for op, chain in CUTS.items()]
    seen, kept = set(), []
    for op, s, e, new in out:
        old = text[s:e]
        new += "\n" * (old.count("\n") - new.count("\n"))  # keep every line where it was
        if new != old and (s, e, new) not in seen:
            seen.add((s, e, new))
            kept.append((op, s, e, new))
    return kept


def git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=False)


def changed_lines(root: Path, base: str) -> dict[str, set[int]]:
    """For each Lean file under lean/ that differs from `base`, the lines of the tree's file that differ (a line
    next to a deletion counts), as difflib finds them; keys are paths under lean/."""
    names = git(root, "diff", "--name-only", "-z", base, "--", "lean").stdout.split("\0")
    names += git(root, "ls-files", "--others", "--exclude-standard", "-z", "--", "lean").stdout.split("\0")
    out: dict[str, set[int]] = {}
    for name in sorted({n for n in names if n.endswith(".lean") and (root / n).is_file()}):
        old = git(root, "show", f"{base}:{name}")
        new_lines = (root / name).read_text().split("\n")
        old_lines = old.stdout.split("\n") if old.returncode == 0 else []
        lines = set()
        for tag, _, _, j1, j2 in difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False).get_opcodes():
            if tag != "equal":
                lines |= set(range(j1 + 1, j2 + 1)) if j2 > j1 else {j1, j1 + 1}
        out[name.removeprefix("lean/")] = lines
    return out


@dataclass
class Tree:
    roles: dict[str, list[tuple[int, int, str, str | None]]]  # file -> (first line, last, check|theorem|other, name)
    uses: dict[str, set[tuple[str, str]] | None]  # theorem -> the constants its statement uses (lean/statements.txt)
    files: dict[str, str]  # module -> file under lean/
    importers: dict[str, set[str]]  # module -> the modules that import it


def plan(root: Path, base: str) -> tuple[list[Mutant], Tree, list[str]]:
    """The mutants of every selected definition (module docstring), the tree's checks and imports, and the fatal
    problems."""
    classified, _, problems = trust_map.walk(root, root / "tools/trust-classes.json", root / "lean/statements.txt")
    declared, hashes = declaration_list(root / "lean/declarations.txt")
    changed = changed_lines(root, base)
    fatal = [f"lean/declarations.txt was not compiled from lean/{f}; rerun tools/lean_statements.py"
             for f in changed if hashes.get(module_name(f)) != source_hash(root / "lean" / f)]
    texts = {f: (root / "lean" / f).read_text() for f in {c.module for c in classified}}
    masked = {f: code_only(text).split("\n") for f, text in texts.items()}
    roles: dict[str, list[tuple[int, int, str, str | None]]] = {}
    found: list[tuple[int, int, Mutant]] = []
    for c in classified:
        d = c.decl
        span = "\n".join(masked[c.module][d.start - 1:d.end])
        check = d.kind == "command" and CHECK_COMMAND.search(span) or d.kind == "theorem" and CHECK_PROOF.search(span)
        roles.setdefault(c.module, []).append((d.start, d.end, "check" if check else
                                               "theorem" if d.kind == "theorem" else "other", d.name))
        if not (c.trusted and d.name and d.kind not in ("theorem", "command", "unrecorded")
                and changed.get(c.module, set()) & set(range(d.start, d.end + 1))):
            continue
        ranged = [x for x in declared.get(module_name(c.module), []) if x.name == d.name and x.start]
        if not ranged:
            fatal.append(f"lean/{c.module}: {d.name} has no compiled range; rerun tools/lean_statements.py")
            continue
        text = texts[c.module]
        starts = [0, *(i + 1 for i, ch in enumerate(text) if ch == "\n")]
        lo = starts[ranged[0].start[0] - 1] + ranged[0].start[1]
        hi = starts[ranged[0].end[0] - 1] + ranged[0].end[1]
        for op, s, e, new in sorted(mutants(text, d.kind, lo, hi), key=lambda x: x[1]):
            found.append(Mutant("", c.module, text.count("\n", 0, s) + 1, d.name, op, s, e,
                                (ranged[0].start[0], ranged[0].end[0]), text[s:e], new))
    # Round robin: each tier in turn; in a tier, the k-th mutant of every (definition, operator) before any k+1-th.
    seen: dict[tuple[str, str], int] = {}
    keyed = []
    for i, m in enumerate(found):
        k = seen[(m.definition, m.operator)] = seen.get((m.definition, m.operator), -1) + 1
        keyed.append(((OPERATORS[m.operator], k, list(OPERATORS).index(m.operator), i), m))
    out = [m for _, m in sorted(keyed, key=lambda x: x[0])]
    for i, m in enumerate(out, 1):
        m.id = f"M{i:03d}"
    importers: dict[str, set[str]] = {}
    files = {}
    for path in sources(root):
        key = path.relative_to(root / "lean").as_posix()
        files[module_name(key)] = key
        try:
            for imported in imports(path.read_text()):
                importers.setdefault(imported, set()).add(module_name(key))
        except ValueError as error:
            fatal.append(f"lean/{key}: {error}")
    if any("not compiled from this source" in p or "missing" in p for p in problems):
        fatal += [p for p in problems if "not compiled from this source" in p or "missing" in p]
    return out, Tree(roles, trust_map.statements(root / "lean/statements.txt"), files, importers), fatal


def cone(tree: Tree, module: str) -> set[str]:
    """`module` and every module that imports it, directly or not."""
    out, todo = {module}, [module]
    while todo:
        for importer in tree.importers.get(todo.pop(), ()):
            if importer not in out:
                out.add(importer)
                todo.append(importer)
    return out


def stated(tree: Tree, theorem: str | None, m: Mutant) -> bool:
    return (module_name(m.file), m.definition) in (tree.uses.get(theorem) or ())


def targets(tree: Tree, m: Mutant, tests: list[str]) -> list[str]:
    """The mutated module, the modules of its cone that hold checks for it, and the --test modules."""
    module = module_name(m.file)
    checks = {x for x in cone(tree, module) if any(r == "check" or r == "theorem" and stated(tree, name, m)
                                                   for *_, r, name in tree.roles.get(tree.files[x], ()))}
    return [module, *sorted((checks | {module_name(t) for t in tests if module_name(t) in tree.files}) - {module})]


class Scratch:
    """A private copy of lean/ (sources and build, never the checkout's files) that mutants are built in."""

    def __init__(self, lean: Path, parent: Path, source: "Scratch | None" = None):
        self.lean = Path(tempfile.mkdtemp(prefix="lean-", dir=parent))
        self.lean.rmdir()
        if source is not None:  # another scratch: its .olean files are linked (Lake replaces them by renaming)
            shutil.copytree(source.lean, self.lean, symlinks=True, copy_function=lambda s, d: os.link(s, d)
                            if s.endswith(".olean") else shutil.copy2(s, d))
            self.seeded = "cloned"
            return
        shutil.copytree(lean, self.lean, symlinks=True, ignore=shutil.ignore_patterns(".lake", ".cache"))
        self.seeded = self._restore(lean) or self._copy(lean)

    def _restore(self, lean: Path) -> str | None:
        """lean_share's checked build of this tree, without its executables; None when there is none."""
        store = lean_share.default_store()
        try:
            entry = store / "v1" / lean_share.entry_id(lean_share.key(lean))
            seal = lean_share.check_entry(entry)
        except (lean_share.Refused, OSError, RuntimeError, TypeError, subprocess.SubprocessError):
            return None
        for name, record in seal["files"].items():
            if not name.startswith("build/bin/"):
                target = self.lean / ".lake" / name
                if not lean_share._place(entry / "lake" / name, target, record["link"]):
                    os.chmod(target, record["mode"] | 0o200)
        return f"restored {entry.name[:16]}"

    def _copy(self, lean: Path) -> str:
        if (lean / ".lake").is_dir():
            shutil.copytree(lean / ".lake", self.lean / ".lake", symlinks=True,
                            ignore=lambda d, names: ["bin"] if Path(d).name == "build" else [])
        return "copied lean/.lake"

    def build(self, modules: list[str], env: dict) -> tuple[int, str]:
        done = subprocess.run([lake_outputs.lean_executable(env, "lake"), "build", *(f"+{m}" for m in modules)],
                              cwd=self.lean, env=env, capture_output=True, text=True, check=False)
        return done.returncode, done.stdout + done.stderr

    def elaborate(self, file: Path, env: dict) -> int:
        return subprocess.run([lake_outputs.lean_executable(env, "lake"), "env", "lean", str(file)], cwd=self.lean,
                              env=env, capture_output=True, check=False).returncode


def role(tree: Tree, file: str, line: int, m: Mutant) -> str:
    """check, proof or other: a theorem is a check when its statement uses the mutated definition and it is not in
    the mutated module (a failing proof script there is no kill), else a proof, whose failure is cut."""
    for s, e, r, name in tree.roles.get(file, ()):
        if s <= line <= e:
            return r if r != "theorem" else "check" if file != m.file and stated(tree, name, m) else "proof"
    return "other"


def cut_proof(path: Path, first: int, last: int) -> bool:
    """Replace the proof of the theorem on lines first..last of `path` by `sorry`, keeping every line."""
    text = path.read_text()
    starts = [0, *(i + 1 for i, ch in enumerate(text) if ch == "\n"), len(text) + 1]
    lo, hi = starts[first - 1], starts[min(last, len(starts) - 1)] - 1
    t = code_only(text)
    at = depth0(t, lo, hi, r":=")
    if at is None:
        arm = re.search(r"(?m)^\s*\|", t[lo:hi])
        at = lo + arm.start() if arm else None
    if at is None:
        return False
    path.write_text(text[:at] + " := sorry" + "\n" * text.count("\n", at, hi) + text[hi:])
    return True


def run(m: Mutant, scratch: Scratch, tree: Tree, tests: list[str], outside: list[Path], env: dict) -> tuple[str, str]:
    """(status, detail) of one mutant, built in `scratch`, whose files are restored afterwards."""
    touched: dict[Path, bytes] = {}

    def keep(path: Path) -> Path:
        touched.setdefault(path, path.read_bytes())
        return path

    path = keep(scratch.lean / m.file)
    text = path.read_text()
    path.write_text(text[:m.start] + m.after + text[m.end:])
    cut: set[tuple[str, int]] = set()
    try:
        for _ in range(8):
            code, output = scratch.build(targets(tree, m, tests), env)
            if code == 0:
                for test in outside:
                    if scratch.elaborate(test, env):
                        return "KILLED", f"{test} fails"
                return "SURVIVOR", ""
            errors = [(f, int(n), message) for f, n, message in ERROR.findall(output)]
            if not errors:
                return "UNKNOWN", "the build failed with no located error: " + output[-300:]
            found = [(f, n, message, role(tree, f, n, m)) for f, n, message in errors]
            for f, n, message, r in found:
                if r == "check" or module_name(f) in map(module_name, tests):
                    return "KILLED", f"lean/{f}:{n}: {message[:120]}"
            for f, n, message, r in found:
                if f == m.file and m.lines[0] <= n <= m.lines[1]:
                    return "INVALID", message[:200]
            proofs = {(f, s, e) for f, n, _, r in found if r == "proof"
                      for s, e, *_ in tree.roles[f] if s <= n <= e}
            other = [(f, n, message) for f, n, message, r in found if r != "proof"]
            if other or not proofs or {(f, s) for f, s, _ in proofs} <= cut:
                f, n, message = (other or errors)[0]
                return "UNKNOWN", f"lean/{f}:{n}: {message[:200]}"
            for f, s, e in proofs:
                if (f, s) not in cut and not cut_proof(keep(scratch.lean / f), s, e):
                    return "UNKNOWN", f"lean/{f}:{s}: the failing proof cannot be cut"
                cut.add((f, s))
        return "UNKNOWN", "the proof cuts did not settle"
    finally:
        for p, data in touched.items():
            p.write_bytes(data)


def load_allow(path: Path | None) -> dict[tuple[str, str], str]:
    if path is None:
        return {}
    entries = json.loads(path.read_text()).get("allow")
    if not isinstance(entries, list):
        raise SystemExit(f"{path}: expected {{\"allow\": [...]}}")
    out = {}
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"definition", "operator", "reason"} \
                or not all(isinstance(entry[k], str) and entry[k].strip() for k in entry) \
                or "\n" in entry["reason"] or entry["operator"] not in OPERATORS:
            raise SystemExit(f"{path}: each entry is {{definition, operator (one of OPERATORS), reason: one line}}: "
                             f"{entry!r}")
        out[(entry["definition"], entry["operator"])] = entry["reason"]
    return out


def show(text: str) -> str:
    text = " ".join(text.split())
    return text if len(text) <= 100 else text[:97] + "..."


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--base", help="the commit the tree is compared with (default: merge base of HEAD and main)")
    parser.add_argument("--root", type=Path, default=ROOT, help="the checkout (default: this one); only read")
    parser.add_argument("--jobs", type=int, help="mutants built at once (default: min(8, cores - 5-min load))")
    parser.add_argument("--max-mutants", type=int, default=60)
    parser.add_argument("--test", action="append", default=[], help="a Lean file (path under lean/ or the "
                        "checkout) that must fail for a kill too; repeatable")
    parser.add_argument("--allow", type=Path)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    allow = load_allow(args.allow)
    base = args.base or git(root, "merge-base", "HEAD", "main").stdout.strip()
    if not base or git(root, "rev-parse", "--verify", "-q", base + "^{commit}").returncode:
        return print(f"no base commit {base!r}", file=sys.stderr) or 2
    tests = [t.removeprefix("lean/") for t in args.test if (root / "lean" / t.removeprefix("lean/")).is_file()]
    outside = [(root / t).resolve() for t in args.test if t.removeprefix("lean/") not in tests]
    if missing := [t for t in outside if not t.is_file() or t.suffix != ".lean"]:
        return print(f"--test: no Lean file {missing}", file=sys.stderr) or 2
    started = time.monotonic()
    found, tree, fatal = plan(root, base)
    if fatal:
        return print("\n".join(fatal), file=sys.stderr) or 2
    jobs = args.jobs or max(1, min(8, (os.cpu_count() or 1) - int(os.getloadavg()[1])))
    run_now, not_run = found[:max(0, args.max_mutants)], found[max(0, args.max_mutants):]
    env = {**os.environ, "PATH": f"{Path.home() / '.elan/bin'}{os.pathsep}{os.environ.get('PATH', '')}"}
    definitions = sorted({(m.file, m.definition) for m in found})
    print(f"trust_mutants: {len(definitions)} definitions, {len(found)} mutants ({len(run_now)} to run), "
          f"{jobs} jobs, base {base[:12]}", flush=True)
    with tempfile.TemporaryDirectory(prefix="trust-mutants-") as scratch_dir:
        pool: queue.Queue = queue.Queue()
        if run_now:
            first = Scratch(root / "lean", Path(scratch_dir))
            modules = sorted({t for m in run_now for t in targets(tree, m, tests)})
            code, output = first.build(modules, env)
            failing = [t for t in outside if first.elaborate(t, env)]
            if code or failing:
                print(f"the checks fail without a mutant ({first.seeded}):\n{output[-3000:]}{failing}",
                      file=sys.stderr)
                return 2
            pool.put(first)
            for _ in range(min(jobs, len(run_now)) - 1):
                pool.put(Scratch(root / "lean", Path(scratch_dir), first))

        def one(m: Mutant) -> Mutant:
            scratch = pool.get()
            try:
                m.status, m.detail = run(m, scratch, tree, tests, outside, env)
            finally:
                pool.put(scratch)
            return m

        with ThreadPoolExecutor(max_workers=jobs) as executor:
            for future in as_completed([executor.submit(one, m) for m in run_now]):
                m = future.result()
                if m.status in ("SURVIVOR", "UNKNOWN") and (m.definition, m.operator) in allow:
                    m.status, m.detail = "ALLOWED", allow[(m.definition, m.operator)]
                if m.status in ("SURVIVOR", "UNKNOWN"):
                    print(f"{m.status} lean/{m.file}:{m.line} {m.definition} {m.operator}: {show(m.before)} -> "
                          f"{show(m.after)}{' (' + show(m.detail) + ')' if m.detail else ''}", flush=True)
    for m in not_run:
        print(f"NOT RUN lean/{m.file}:{m.line} {m.definition} {m.operator}: {show(m.before)} -> {show(m.after)}")
    counts = {s: sum(m.status == s for m in found) for s in
              ("KILLED", "SURVIVOR", "UNKNOWN", "INVALID", "ALLOWED", "NOT RUN")}
    seconds = round(time.monotonic() - started)
    print("trust_mutants: " + ", ".join(f"{n} {s}" for s, n in counts.items()) + f" in {seconds} s")
    if args.json:
        args.json.write_text(json.dumps({
            "base": git(root, "rev-parse", base).stdout.strip(), "head": git(root, "rev-parse", "HEAD").stdout.strip(),
            "jobs": jobs, "max_mutants": args.max_mutants, "tests": args.test, "seconds": seconds, "counts": counts,
            "definitions": [f"lean/{f}: {d}" for f, d in definitions],
            "mutants": [{k: v for k, v in asdict(m).items() if k not in ("start", "end")} for m in found]},
            indent=1, ensure_ascii=False) + "\n")
    if counts["SURVIVOR"] or counts["UNKNOWN"]:
        return 1
    return 3 if not_run else 0


if __name__ == "__main__":
    sys.exit(main())
