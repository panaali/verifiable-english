#!/usr/bin/env python3
"""Mechanical mutants of the trusted Lean definitions a branch adds or changes, and the survivors (R16 signs trusted
growth only when "every new trusted definition is exercised by a test that can fail").

    uv run python tools/trust_mutants.py [--base REV] [--jobs N] [--max-mutants N] [--test FILE ...] [--deep]
                                         [--allow FILE] [--json OUT] [--root DIR]

Selected: each declaration tools/trust_map.py counts as trusted (not a theorem or check) whose lines hold a line
the tree adds or changes over REV (default: the merge base of HEAD and main). The `OPERATORS` mutate it inside its
compiled range (lean/declarations.txt), comments and strings excluded, on its changed lines only (all of a new one).

Each mutant is built in a private scratch copy of lean/ (its build restored from tools/lean_share.py's checked build
of this tree, else copied from lean/.lake; the checkout is only read): the mutated module, its proofs cut to `sorry`
(no proof there is a check), then each module that imports it and holds checks for it: a check whose compiled
statement (lean/statements.txt) uses it, every other check in a module of its directory (of the whole cone with
--deep), and the --test files. A check is a command whose outcome Lean computes from definitions alone, never from a
proof (`classify`): `#guard`, `#guard_expr`, `#eval`, `#reduce`, `#check`, or an `example` or theorem proved by
`decide`, `native_decide` or `rfl`, with no other tactic block in it; a `#guard_msgs … in` is what it wraps. Every
other `example` or theorem, a check form with a tactic block inside, and every `#print` (it lists or shows proofs)
is a proof, whatever its statement names. The mutant is
- KILLED when Lean reports an error inside a check or a --test file, and the same build without the mutant (its
  control: the same cuts) passes;
- INVALID when the error is inside the mutated declaration (the compiler, not this text, decides what it means);
- SURVIVOR when every check passes. A failing proof elsewhere is no kill (BUILDER-CHECKLIST 3): it is cut to
  `sorry` (a `#print` blanked) and the build repeated, before any other error is read; and a check that fails in
  the control too reads a cut proof (`#eval` refuses a value that depends on `sorry`), so it is cut the same way;
- UNKNOWN when anything else fails (an error in a definition, or in a command that is no check);
- NOT RUN past --max-mutants (every definition and operator gets its k-th mutant before any gets its k+1-th).

SURVIVOR and UNKNOWN print as `<STATUS> <file>:<line> <definition> <operator>: <before> -> <after>` unless --allow
FILE lists the definition and operator with a reason ({"allow": [{"definition": "VE.X.f", "operator": "lt-le",
"reason": "one line"}]}). Exit 0: all ran, none left; 1: a survivor or UNKNOWN left; 3: none left but some NOT RUN;
2: cannot run. Builder and reviewer evidence only: no gate, merge train or nightly reads it.
"""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
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
sys.path[:0] = [str(ROOT), str(ROOT / "tools"), str(ROOT / "lean")]
from audit import code_only  # noqa: E402
from check_lean_imports import imports  # noqa: E402
from lean_statements import declaration_list, module_name, source_hash, sources  # noqa: E402
from tools import lake_outputs, lean_share, trust_map  # noqa: E402

OPEN, CLOSE = "([{⟨", ")]}⟩"
CHECK_COMMANDS = {"guard", "guard_expr", "eval", "eval!", "reduce", "check"}
TACTIC = re.compile(r"\bby\b")
EXAMPLE = re.compile(r"(?m)^\s*(?:@\[[^\]]*\]\s*)*example\b")
CHECK_PROOF = re.compile(r":=\s*(?:by\s+)?(?:decide|native_decide|rfl)(?:\s+\+\w+)*\s*$")
ERROR = re.compile(r"^error: (?:\./)*(\S+?\.lean):(\d+):\d+: (.*)$", re.M)
STOP = {"then", "else", "do", "with", "in", "fun", "if", "let", "match", "return", "throw", "by", "at", "from", "where",
        "for", "unless", "mut", "have", "show"}
LIST_METHODS = ("find\\?|any|all|contains|map|filter|flatMap|filterMap|length|head\\?|isEmpty|foldl|foldr|zip|lookup|"
                "elem|isPrefixOf|take|drop|reverse|sum|count|findSome\\?|eraseDups|dropLast|tail|getLast\\?|mapM|forM")
LIST_RESULTS = {"map", "filter", "flatMap", "filterMap", "take", "drop", "reverse", "eraseDups", "dropLast", "tail",
                "zip"}
CUTS = {"list-empty": None, "list-first": ".take 1", "list-drop-last": ".dropLast", "list-last": ".reverse.take 1",
        "list-drop-first": ".drop 1"}
# The operators and their tiers: --max-mutants runs every earlier tier first.
OPERATORS = {**dict.fromkeys(("arm-true", "arm-false", "arm-default", "body-true", "body-false", "not-drop", "and-or",
                              "or-and", "lt-le", "le-lt", "lt-eq", "le-eq", "eq-le", "eq-ne", "ne-eq", "all-any",
                              "any-all", "bool-flip", "lit-plus", "lit-minus", "list-empty", "append-left",
                              "append-right"), 1), "list-first": 2, "list-drop-last": 2, "list-last": 3,
             "list-drop-first": 3}
LT, LE, EQ = r"(?<![<-])<(?![-|$*;=<>])", r"≤|(?<!<)<=(?!>)", r"(?<![:=!<>])=(?![=>])"
TOKENS = [("not-drop", r"¬\s*|(?<![\w'!?)\]⟩])!(?=[\w(·])", ""), ("and-or", "∧", "∨"),
          ("and-or", r"(?<![&|])&&(?![&|])", "||"), ("or-and", "∨", "∧"), ("or-and", r"(?<!\|)\|\|(?!\|)", "&&"),
          ("lt-le", LT, "≤"), ("lt-eq", LT, "="), ("le-lt", LE, "<"), ("le-eq", LE, "="), ("eq-le", EQ, "≤"),
          ("eq-ne", EQ, "≠"), ("eq-ne", r"(?<!=)==(?!=)", "!="), ("ne-eq", "≠", "="), ("ne-eq", "!=", "=="),
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
    lines: tuple[int, int]  # the mutated declaration's
    before: str
    after: str
    status: str = "NOT RUN"
    detail: str = ""


def group(t: str, i: int, step: int = 1) -> int:
    """From the bracket at t[i], the index past its partner (step 1) or of its partner (step -1)."""
    depth, j = 0, i
    while 0 <= j < len(t):
        depth += (t[j] in OPEN) - (t[j] in CLOSE)
        if depth == 0:
            return j + (step > 0)
        j += step
    return len(t) if step > 0 else 0


def depth0(t: str, lo: int, hi: int, pattern: str) -> int | None:
    """The first match of `pattern` in t[lo:hi] outside every bracket group."""
    depth = 0
    for i in range(lo, hi):
        depth += (t[i] in OPEN) - (t[i] in CLOSE)
        if depth == 0 and re.match(pattern, t[i:hi]):
            return i
    return None


def name_char(t: str, i: int) -> bool:
    return t[i].isalnum() or t[i] in "_'?.·" or t[i] == "!" and i > 0 and t[i - 1].isalnum()


def atom_before(t: str, j: int, lo: int) -> int | None:
    """The start of the dotted name, or bracket group with dotted names after it, that ends at j."""
    i = j
    while i > lo and name_char(t, i - 1):
        i -= 1
    if i > lo and t[i - 1] in CLOSE and (i == j or t[i] == "."):
        i = group(t, i - 1, -1)
    return i if i < j and t[i] != "." else None


def atom_after(t: str, i: int, hi: int, args: bool = True) -> int:
    """The end of the atom at t[i] and (with `args`) the arguments applied to it on its line; i when there is none."""
    j = group(t, i) if t[i] in OPEN else i
    while j < hi and name_char(t, j):
        j += 1
    if t[i:j] in STOP or t[i:j].startswith("."):
        return i
    while args and j + 1 < hi and t[j] == " " and (k := atom_after(t, j + 1, hi, False)) > j + 1:
        j = k
    return min(j, hi)


def cut(atom: str, chain: str | None) -> str:
    if chain is None:
        return "[]"
    single = re.fullmatch(r"[\w'?.!]+", atom) or atom[0] in OPEN and group(atom, 0) == len(atom)
    return f"({atom}{chain})" if single else f"(({atom}){chain})"


def mutants(text: str, kind: str, lo: int, hi: int) -> list[tuple[str, int, int, str]]:
    """(operator, start, end, replacement) for the declaration at text[lo:hi]."""
    t, code = code_only(text), code_only(text)[lo:hi]
    out = [(op, lo + m.start(), lo + m.end(), new) for op, pattern, new in TOKENS for m in re.finditer(pattern, code)]
    out += [("bool-flip", lo + m.start(), lo + m.end(), BOOLS[m[0]])
            for m in re.finditer(r"(?<![\w.'])(?:true|false|True|False)(?![\w'])", code)]
    for m in re.finditer(r"(?<![\w.'])\d+(?![\w.])", code):
        out += [(op, lo + m.start(), lo + m.end(), str(int(m[0]) + d)) for op, d in (("lit-plus", 1), ("lit-minus", -1))
                if int(m[0]) + d >= 0]
    lists: list[tuple[int, int]] = []
    assign, arm = depth0(t, lo, hi, ":="), re.search(r"(?m)^\s*\|", code)
    head = min(x for x in (assign, lo + arm.start() if arm else None, hi) if x is not None)
    colon, depth = None, 0
    for i in range(lo, head):
        depth += (t[i] in OPEN) - (t[i] in CLOSE)
        colon = i if depth == 0 and t[i] == ":" and t[i + 1] != "=" else colon
    result = re.split("→|->", t[colon + 1:head])[-1].strip() if kind == "def" and colon is not None else ""
    consts = {"Prop": ("True", "False"), "Bool": ("true", "false")}.get(result)
    if result and assign == head:  # a body: `:= ...`
        end = depth0(t, assign, hi, r"\b(?:where|termination_by|decreasing_by)\b") or hi
        rest = t[assign + 2:end]
        body = (assign + 2 + len(rest) - len(rest.lstrip()), assign + 2 + len(rest.rstrip()))
        out += [("body-true", *body, consts[0]), ("body-false", *body, consts[1])] if consts else []
        lists += [body] if result.startswith("List") else []
    elif result and arm:  # arms: `| pattern => result`
        starts = [lo + a.start() for a in re.finditer(r"(?m)^[ \t]*\|", code)]
        arms = []
        for a, b in zip(starts, [*starts[1:], hi]):
            if (arrow := depth0(t, a + t[a:b].index("|") + 1, b, "=>")) is not None:
                rhs = t[arrow + 2:b]
                arms.append((t[a:arrow], arrow + 2 + len(rhs) - len(rhs.lstrip()), arrow + 2 + len(rhs.rstrip())))
        default = arms[-1] if arms and re.fullmatch(r"\s*\|[\s_,]*", arms[-1][0]) else None
        for _, s, e in arms:
            if consts:
                out += [("arm-true", s, e, consts[0]), ("arm-false", s, e, consts[1])]
            elif default and (s, e) != default[1:]:
                out.append(("arm-default", s, e, text[default[1]:default[2]]))
    for m in re.finditer(rf"\.({LIST_METHODS})(?![\w?!'])", code):  # a list method's receiver and list result
        if (start := atom_before(t, lo + m.start(), lo)) is not None:
            lists += [(start, lo + m.start())] + ([(start, atom_after(t, start, hi))] if m[1] in LIST_RESULTS else [])
    lists += [(lo + m.end(), e) for m in re.finditer(r"\bfor \w+ in ", code)
              if (e := t.find(" do", lo + m.end(), hi)) > 0]
    for m in re.finditer(r" \+\+ ", code):
        op = lo + m.start()
        left, right = atom_before(t, op, lo), atom_after(t, op + 4, hi)
        if left is not None and right > op + 4:
            lists += [(left, op), (op + 4, right)]
            out += [("append-left", op, right, ""), ("append-right", left, op + 4, "")]
    lists += [(lo + m.start(), group(t, lo + m.start())) for m in re.finditer(r"(?<![\w'?!)\]@#])\[(?!\])", code)]
    for s, e in dict.fromkeys(lists):
        atom = text[s:e]
        if t[s] == "(" and (s + 1, e - 1) in lists or not atom.strip():  # `(xs)` is the list `xs`
            continue
        if atom.startswith("·"):  # `(·.head.contains a)`: the argument is named first
            out += [(op, s - 1, e, f"(fun x_tm => {cut('x_tm' + atom[1:], chain)}") for op, chain in CUTS.items()
                    if t[s - 1] == "("]
            continue
        one = t[s] == "[" and group(t, s) == e and depth0(t, s + 1, e - 1, ",") is None
        out += [(op, s, e, cut(atom, chain)) for op, chain in CUTS.items()
                if not (one and op in ("list-first", "list-last"))]  # `[x].take 1` is `[x]`
    kept: dict[tuple[int, int, str], str] = {}
    for op, s, e, new in out:
        new += "\n" * (text.count("\n", s, e) - new.count("\n"))  # every line stays where it was
        if new != text[s:e]:
            kept.setdefault((s, e, new), op)
    return [(op, s, e, new) for (s, e, new), op in kept.items()]


def git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=False)


def changed_lines(root: Path, base: str) -> dict[str, set[int]]:
    """The lines of each file under lean/ that differ from `base` (difflib's; a line next to a deletion counts)."""
    names = git(root, "diff", "--name-only", "-z", base, "--", "lean").stdout.split("\0")
    names += git(root, "ls-files", "--others", "--exclude-standard", "-z", "--", "lean").stdout.split("\0")
    out: dict[str, set[int]] = {}
    for name in sorted({n for n in names if n.endswith(".lean") and (root / n).is_file()}):
        old = git(root, "show", f"{base}:{name}")
        matcher = difflib.SequenceMatcher(None, old.stdout.split("\n") if old.returncode == 0 else [],
                                          (root / name).read_text().split("\n"), autojunk=False)
        out[name.removeprefix("lean/")] = {n for tag, _, _, j1, j2 in matcher.get_opcodes() if tag != "equal"
                                           for n in (range(j1 + 1, j2 + 1) if j2 > j1 else (j1, j1 + 1))}
    return out


def unwrapped(span: str) -> str:
    """`span` (code only) with its `#guard_msgs … in` wrappers blanked."""
    return trust_map.GUARD_WRAPPER.sub(lambda w: " " * len(w[0]), span)


def command(span: str) -> str | None:
    """The `#` command a span (code only) runs, past its `#guard_msgs … in`, `set_option … in` and `open … in`
    prefixes: `guard`, `eval!`, `print`, ...; None for a declaration or an `example`."""
    found = re.match(r"(?:\s|(?:set_option|open)\b[^\n]*?\bin\b)*#([A-Za-z_]\w*!?)", unwrapped(span))
    return found[1] if found else None


def classify(kind: str, span: str) -> str:
    """check, proof or other, for a declaration of `kind` whose code (comments and strings blanked) is `span`. A
    check is a command whose outcome Lean computes from definitions alone, never from a proof: `#guard`,
    `#guard_expr`, `#eval`, `#reduce`, `#check`, or an `example` or theorem proved by `decide`, `native_decide` or
    `rfl`, with no other tactic block (`by`) in it. Every other `example` or theorem is a proof (review F1), and so
    is a check form with a tactic block inside (a mutant can break the tactic and nothing else) and every `#print`
    (`#print axioms` lists `sorryAx` once the tool cuts a proof, and `#print` shows the definition's text and its
    proofs: review F7). A `#guard_msgs … in` is the command it wraps (trust_map puts both in one span: review F6).
    Any other command, and one this cannot read, is other: an error there is no kill. A check whose outcome a cut
    proof still changes (`#eval` refuses a value that depends on `sorry`) is caught by the control build in `run`."""
    bare = unwrapped(span)
    proved = CHECK_PROOF.search(bare)
    tactics = len(TACTIC.findall(bare)) - (len(TACTIC.findall(proved[0])) if proved else 0)
    if kind == "theorem" or kind == "command" and EXAMPLE.search(bare):
        return "check" if proved and not tactics else "proof"
    name = command(span) if kind == "command" else None
    if name == "print" or name in CHECK_COMMANDS and tactics:
        return "proof"
    return "check" if name in CHECK_COMMANDS else "other"


@dataclass
class Tree:
    roles: dict[str, list[tuple[int, int, str, str | None]]]  # file -> (first, last line, check|proof|other, name)
    uses: dict[str, set[tuple[str, str]] | None]  # theorem -> the constants its statement uses
    files: dict[str, str]  # module -> file under lean/
    importers: dict[str, set[str]]


def plan(root: Path, base: str) -> tuple[list[Mutant], Tree, list[str]]:
    """The mutants in run order, the tree's checks and imports, and the problems that stop the run."""
    classified, _, problems = trust_map.walk(root, root / "tools/trust-classes.json", root / "lean/statements.txt")
    declared, hashes = declaration_list(root / "lean/declarations.txt")
    changed = changed_lines(root, base)
    fatal = [p for p in problems if "not compiled from this source" in p or "missing" in p]
    fatal += [f"lean/declarations.txt was not compiled from lean/{f}; rerun tools/lean_statements.py"
              for f in changed if hashes.get(module_name(f)) != source_hash(root / "lean" / f)]
    texts = {f: (root / "lean" / f).read_text() for f in {c.module for c in classified}}
    masked = {f: code_only(text).split("\n") for f, text in texts.items()}
    roles: dict[str, list] = {}
    found: list[Mutant] = []
    for c in classified:
        d, text = c.decl, texts[c.module]
        span = "\n".join(masked[c.module][d.start - 1:d.end])
        roles.setdefault(c.module, []).append((d.start, d.end, classify(d.kind, span), d.name))
        lines = changed.get(c.module, set())
        if not (c.trusted and d.name and d.kind not in ("theorem", "command", "unrecorded")
                and lines & set(range(d.start, d.end + 1))):
            continue
        ranged = [x for x in declared.get(module_name(c.module), []) if x.name == d.name and x.start]
        if not ranged:
            fatal.append(f"lean/{c.module}: {d.name} has no compiled range; rerun tools/lean_statements.py")
            continue
        starts = [0, *(i + 1 for i, ch in enumerate(text) if ch == "\n")]
        r = ranged[0]
        for op, s, e, new in sorted(mutants(text, d.kind, starts[r.start[0] - 1] + r.start[1],
                                            starts[r.end[0] - 1] + r.end[1]), key=lambda x: x[1]):
            first = text.count("\n", 0, s) + 1
            if lines & set(range(first, first + text.count("\n", s, e) + 1)):
                found.append(Mutant("", c.module, first, d.name, op, s, e, (r.start[0], r.end[0]), text[s:e], new))
    seen: Counter = Counter()  # each tier in turn; in it, the k-th of every (definition, operator) first
    keys = []
    for i, m in enumerate(found):
        keys.append((OPERATORS[m.operator], seen[m.definition, m.operator], list(OPERATORS).index(m.operator), i))
        seen[m.definition, m.operator] += 1
    out = [m for _, m in sorted(zip(keys, found), key=lambda x: x[0])]
    for i, m in enumerate(out, 1):
        m.id = f"M{i:03d}"
    files, importers = {}, {}
    for path in sources(root):
        key = path.relative_to(root / "lean").as_posix()
        files[module_name(key)] = key
        try:
            for imported in imports(path.read_text()):
                importers.setdefault(imported, set()).add(module_name(key))
        except ValueError as error:
            fatal.append(f"lean/{key}: {error}")
    return out, Tree(roles, trust_map.statements(root / "lean/statements.txt"), files, importers), fatal


def stated(tree: Tree, theorem: str | None, m: Mutant) -> bool:
    return (module_name(m.file), m.definition) in (tree.uses.get(theorem) or ())


def targets(tree: Tree, m: Mutant, tests: list[str], deep: bool = False) -> list[str]:
    """The mutated module, then the --test modules and the modules of its cone that hold checks for it."""
    module, home = module_name(m.file), m.file.rpartition("/")[0]
    cone, todo = {module}, [module]
    while todo:
        new = tree.importers.get(todo.pop(), set()) - cone
        cone |= new
        todo += new
    checks = {x for x in cone for s, e, r, n in tree.roles.get(tree.files[x], ())
              if r == "check" and (deep or tree.files[x].rpartition("/")[0] == home or stated(tree, n, m))}
    return [module, *sorted((checks | {module_name(t) for t in tests}) - {module})]


def role(tree: Tree, file: str, line: int, m: Mutant) -> str:
    """mutated (inside the mutated declaration), else the role `classify` gave the declaration at `line`."""
    if file == m.file and m.lines[0] <= line <= m.lines[1]:
        return "mutated"
    return next((r for s, e, r, _ in tree.roles.get(file, ()) if s <= line <= e), "other")


def cut_proof(path: Path, first: int, last: int) -> bool:
    """The theorem or `example` on lines first..last of `path` with its proof replaced by `sorry` and its
    `#guard_msgs … in` wrappers blanked (the `sorry` warning would fail them: review F6), or the `#` command there
    blanked whole with the comments before it (it declares nothing; its docstring is the `#guard_msgs`'s: review
    F7), every line kept. The comment lines after the span stay: a docstring there is the next command's
    (trust_map's span ends before that command's first code line), and a `#guard_msgs` reads its docstring."""
    text = path.read_text()
    starts = [0, *(i + 1 for i, ch in enumerate(text) if ch == "\n"), len(text) + 1]
    lo, hi, t = starts[first - 1], starts[min(last, len(starts) - 1)] - 1, code_only(text)
    if command(t[lo:hi]):
        begin = lo  # back over the lines with no code before it, to the first outside every string and comment
        while begin and not t[starts[n := text.count("\n", 0, begin) - 1]:lo].strip():
            begin = starts[n]
        while not code_only(text[:begin] + "X").endswith("X"):  # a string or comment still open there
            begin = text.index("\n", begin) + 1
        end = lo + len(t[lo:hi].rstrip())
        path.write_text(text[:begin] + re.sub(r"[^\n]", " ", text[begin:end]) + text[end:])
        return True
    arm = re.search(r"(?m)^\s*\|", t[lo:hi])
    found = [x for x in (depth0(t, lo, hi, ":="), lo + arm.start() if arm else None) if x is not None]
    if found:
        head, at = list(text), min(found)
        for w in trust_map.GUARD_WRAPPER.finditer(t, lo, at):
            head[w.start():w.end()] = re.sub(r"[^\n]", " ", w[0])
        end = next((s for s in starts if at < s <= hi and not t[s:hi].strip() and not code_only(text[s:hi]).strip()),
                   hi)  # the first line from which only whole comments are left
        path.write_text("".join(head[:at]) + " := sorry" + "\n" * text.count("\n", at, end) + text[end:])
    return bool(found)


class Scratch:
    """A private copy of lean/, sources and build, that mutants are built in; the checkout is only read."""

    def __init__(self, lean: Path, parent: Path, source: Scratch | None = None):
        self.lean = Path(tempfile.mkdtemp(prefix="lean-", dir=parent)) / "lean"
        if source:  # another scratch's .olean files are linked: Lake replaces them by renaming, never in place
            shutil.copytree(source.lean, self.lean, symlinks=True,
                            copy_function=lambda s, d: os.link(s, d) if s.endswith(".olean") else shutil.copy2(s, d))
            return
        shutil.copytree(lean, self.lean, symlinks=True, ignore=shutil.ignore_patterns(".lake", ".cache"))
        try:  # lean_share's checked build of this tree, without its executables
            entry = lean_share.default_store() / "v1" / lean_share.entry_id(lean_share.key(lean))
            for name, record in lean_share.check_entry(entry)["files"].items():
                if not name.startswith("build/bin/") and not lean_share._place(
                        entry / "lake" / name, self.lean / ".lake" / name, record["link"]):
                    os.chmod(self.lean / ".lake" / name, record["mode"] | 0o200)
        except (lean_share.Refused, OSError, RuntimeError, TypeError, subprocess.SubprocessError):
            shutil.rmtree(self.lean / ".lake", ignore_errors=True)
            if (lean / ".lake").is_dir():
                shutil.copytree(lean / ".lake", self.lean / ".lake", symlinks=True,
                                ignore=lambda d, names: ["bin"] if Path(d).name == "build" else [])

    def lake(self, env: dict, *args: str) -> tuple[int, str]:
        done = subprocess.run([lake_outputs.lean_executable(env, "lake"), *args], cwd=self.lean, env=env,
                              capture_output=True, text=True, check=False)
        return done.returncode, done.stdout + done.stderr


def run(m: Mutant, scratch: Scratch, tree: Tree, tests: list[str], outside: list[Path], env: dict,
        deep: bool = False, controls: dict | None = None) -> tuple[str, str]:
    """(status, detail) of one mutant, built in `scratch`, whose files are restored afterwards. The mutated module's
    proofs are cut up front, and a proof that fails elsewhere is cut and the build repeated, before any other error
    is read: a check may fail only because a proof it reads failed. An error in a check is a kill only when its
    control, the same build without the mutant (the same cuts; `controls` caches it across mutants), passes: what
    fails there too reads a cut proof (review F7: `#eval` refuses a value that depends on `sorry`), so it is cut as
    well and never a kill."""
    controls = {} if controls is None else controls
    built = targets(tree, m, tests, deep)
    texts: dict[str, str] = {}  # file -> the checkout's text, written back at the end
    cuts: dict[str, list[tuple[int, int]]] = {}  # file -> the spans cut in it

    def write(f: str, mutated: bool) -> None:
        path = scratch.lean / f
        text = texts.setdefault(f, path.read_text())
        path.write_text(text[:m.start] + m.after + text[m.end:] if mutated and f == m.file else text)
        for s, e in cuts.get(f, ()):
            cut_proof(path, s, e)

    def build(stage: list[str]) -> tuple[int, list[tuple[str, int, str]]]:
        for attempt in range(3):  # again: Lake can fail with no located error under load
            code, output = scratch.lake(env, "build", *(f"+{x}" for x in stage))
            found = [(f, int(n), message) for f, n, message in ERROR.findall(output)]
            if code == 0 or found:
                return code, found
        return code, [("", 0, "the build failed with no located error: " + output[-300:])]

    def state() -> tuple:
        return tuple(sorted((f, tuple(c)) for f, c in cuts.items() if c))

    def each(found: list[tuple]) -> list[tuple[str, int, str]]:
        """The first error of each declaration in `found`."""
        first: dict[tuple[str, int], tuple[str, int, str]] = {}
        for f, n, message, *_ in found:
            first.setdefault((f, next((s for s, e, *_ in tree.roles.get(f, ()) if s <= n <= e), n)), (f, n, message))
        return list(first.values())

    def cut(f: str, n: int, why: str) -> str | None:
        """Cuts the proof, check or `#` command at f:n, unless already cut; else the reason (UNKNOWN)."""
        found = next(((s, e, r) for s, e, r, _ in tree.roles.get(f, ()) if s <= n <= e), None)
        why = f"lean/{f}:{n}: {why}" if f else why
        if found is None or role(tree, f, n, m) == "mutated" or found[:2] in cuts.get(f, ()):
            return why
        s, e, r = found
        path = scratch.lean / f
        texts.setdefault(f, path.read_text())
        if r == "other" and not command("\n".join(code_only(path.read_text()).split("\n")[s - 1:e])) \
                or not cut_proof(path, s, e):
            return why
        cuts.setdefault(f, []).append((s, e))
        return None

    try:
        write(m.file, True)
        for first, last, r, _ in sorted(tree.roles[m.file], reverse=True):
            if r == "proof" and not first <= m.line <= last and cut_proof(scratch.lean / m.file, first, last):
                cuts.setdefault(m.file, []).append((first, last))
        for stage in (built[:1], built[1:]):  # the mutated module alone first: most mutants end there
            for _ in range(12):
                code, found = build(stage) if stage else (0, [])
                if code == 0:
                    break
                if not found[0][0]:
                    return "UNKNOWN", found[0][2]
                roles = [(f, n, message, role(tree, f, n, m)) for f, n, message in found]
                if mutated := next((x for x in roles if x[3] == "mutated"), None):
                    return "INVALID", mutated[2][:200]
                if proofs := [x for x in roles if x[3] == "proof" and x[0] not in tests]:
                    for f, n, message in each(proofs):  # cut first: a check may fail only because it reads one
                        if why := cut(f, n, f"the failing proof cannot be cut: {message[:200]}"):
                            return "UNKNOWN", why
                    continue
                key = (tuple(stage), state())
                if key not in controls:  # the same build without the mutant
                    write(m.file, False)
                    controls[key] = build(stage)[1]
                    write(m.file, True)
                    if controls[key][:1] and not controls[key][0][0]:  # no located error: not kept for others
                        return "UNKNOWN", f"its control: {controls.pop(key)[0][2]}"
                for f, n, message in each(controls[key]):  # it fails there too: it reads a cut proof, so cut it
                    if why := cut(f, n, f"fails without the mutant too: {message[:200]}"):
                        return "UNKNOWN", why
                if controls[key]:
                    continue
                kill = next((x for x in roles if x[3] == "check" or x[0] in tests), None)
                f, n, message, _ = kill or roles[0]
                return ("KILLED", f"lean/{f}:{n}: {message[:120]}") if kill else (
                    "UNKNOWN", f"lean/{f}:{n}: {message[:200]}")
            else:
                return "UNKNOWN", "the proof cuts did not settle"
        failing = [test for test in outside if scratch.lake(env, "env", "lean", str(test))[0]]
        if not failing:
            return "SURVIVOR", ""
        key = ("outside", tuple(built), state())
        if key not in controls:
            write(m.file, False)
            ok = all(build(stage)[0] == 0 for stage in (built[:1], built[1:]) if stage)
            controls[key] = [t for t in outside if not ok or scratch.lake(env, "env", "lean", str(t))[0]]
        if kill := next((t for t in failing if t not in controls[key]), None):
            return "KILLED", f"{kill} fails"
        return "UNKNOWN", f"{failing[0]} fails without the mutant too"
    finally:
        for f, text in texts.items():
            (scratch.lean / f).write_text(text)


def evidence(data: dict) -> str:
    """The --json text: one mutant per line."""
    rows = ",\n".join(json.dumps(m, ensure_ascii=False) for m in data["mutants"])
    head = json.dumps({k: v for k, v in data.items() if k != "mutants"}, ensure_ascii=False)
    return f'{head[:-1]}, "mutants": [\n{rows}\n]}}\n'


def show(text: str) -> str:
    text = " ".join(text.split())
    return text if len(text) <= 100 else text[:97] + "..."


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--base", help="the commit compared with (default: the merge base of HEAD and main)")
    parser.add_argument("--root", type=Path, default=ROOT, help="the checkout (default: this one); only read")
    parser.add_argument("--jobs", type=int, help="mutants built at once (default: min(8, cores - 5-min load))")
    parser.add_argument("--max-mutants", type=int, default=60)
    parser.add_argument("--test", action="append", default=[], help="a Lean file that must fail for a kill too")
    parser.add_argument("--deep", action="store_true", help="every check module of the cone, not only its directory's")
    parser.add_argument("--allow", type=Path)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    entries = json.loads(args.allow.read_text()).get("allow") if args.allow else []
    if not isinstance(entries, list) or not all(
            isinstance(e, dict) and set(e) == {"definition", "operator", "reason"} and e["operator"] in OPERATORS
            and all(isinstance(v, str) and v.strip() and "\n" not in v for v in e.values()) for e in entries):
        return print('--allow: {"allow": [{"definition", "operator", "reason": one line}, ...]}', file=sys.stderr) or 2
    allow = {(e["definition"], e["operator"]): e["reason"] for e in entries}
    base = args.base or git(root, "merge-base", "HEAD", "main").stdout.strip()
    if not base or git(root, "rev-parse", "--verify", "-q", base + "^{commit}").returncode:
        return print(f"no base commit {base!r}", file=sys.stderr) or 2
    tests = [t.removeprefix("lean/") for t in args.test if (root / "lean" / t.removeprefix("lean/")).is_file()]
    outside = [(root / t).resolve() for t in args.test if t.removeprefix("lean/") not in tests]
    if bad := [t for t in [*outside, *(root / "lean" / t for t in tests)] if t.suffix != ".lean" or not t.is_file()]:
        return print(f"--test: not a Lean file: {bad}", file=sys.stderr) or 2
    started = time.monotonic()
    found, tree, fatal = plan(root, base)
    if fatal:
        return print("\n".join(fatal), file=sys.stderr) or 2
    jobs = args.jobs or max(1, min(8, (os.cpu_count() or 1) - int(os.getloadavg()[1])))
    run_now, not_run = found[:max(0, args.max_mutants)], found[max(0, args.max_mutants):]
    env = {**os.environ, "PATH": f"{Path.home() / '.elan/bin'}{os.pathsep}{os.environ.get('PATH', '')}"}
    definitions = sorted({(m.file, m.definition) for m in found})
    print(f"trust_mutants: {len(definitions)} definitions, {len(found)} mutants ({len(run_now)} to run), {jobs} jobs, "
          f"base {base[:12]}", flush=True)
    with tempfile.TemporaryDirectory(prefix="trust-mutants-") as scratch_dir:
        pool: queue.Queue = queue.Queue()
        controls: dict = {}  # the builds without a mutant, by stage and cuts: shared by every scratch
        if run_now:
            first = Scratch(root / "lean", Path(scratch_dir))
            code, output = first.lake(env, "build", *sorted({f"+{x}" for m in run_now for x in targets(tree, m, tests,
                                                                                                    args.deep)}))
            failing = [t for t in outside if first.lake(env, "env", "lean", str(t))[0]]
            if code or failing:
                return print(f"the checks fail without a mutant:\n{output[-3000:]}{failing}", file=sys.stderr) or 2
            pool.put(first)
            for _ in range(min(jobs, len(run_now)) - 1):
                pool.put(Scratch(root / "lean", Path(scratch_dir), first))

        def one(m: Mutant) -> None:
            scratch = pool.get()
            try:
                m.status, m.detail = run(m, scratch, tree, tests, outside, env, args.deep, controls)
            finally:
                pool.put(scratch)
            if m.status in ("SURVIVOR", "UNKNOWN") and (m.definition, m.operator) in allow:
                m.status, m.detail = "ALLOWED", allow[(m.definition, m.operator)]
            if m.status in ("SURVIVOR", "UNKNOWN"):
                print(f"{m.status} lean/{m.file}:{m.line} {m.definition} {m.operator}: {show(m.before)} -> "
                      f"{show(m.after)}{' (' + show(m.detail) + ')' if m.detail else ''}", flush=True)

        with ThreadPoolExecutor(max_workers=jobs) as executor:
            list(executor.map(one, run_now))
    for m in not_run:
        print(f"NOT RUN lean/{m.file}:{m.line} {m.definition} {m.operator}: {show(m.before)} -> {show(m.after)}")
    counts = {s: sum(m.status == s for m in found) for s in ("KILLED", "SURVIVOR", "UNKNOWN", "INVALID", "ALLOWED",
                                                            "NOT RUN")}
    seconds = round(time.monotonic() - started)
    print("trust_mutants: " + ", ".join(f"{n} {s}" for s, n in counts.items()) + f" in {seconds} s")
    if args.json:
        args.json.write_text(evidence({
            "base": git(root, "rev-parse", base).stdout.strip(), "head": git(root, "rev-parse", "HEAD").stdout.strip(),
            "jobs": jobs, "max_mutants": args.max_mutants, "deep": args.deep, "tests": args.test, "seconds": seconds,
            "counts": counts, "definitions": [f"lean/{f}: {d}" for f, d in definitions],
            "mutants": [{k: v for k, v in asdict(m).items() if k not in ("start", "end")} for m in found]}))
    return 1 if counts["SURVIVOR"] or counts["UNKNOWN"] else 3 if not_run else 0


if __name__ == "__main__":
    sys.exit(main())
