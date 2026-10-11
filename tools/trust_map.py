#!/usr/bin/env python3
"""Trust budget (bundle TB of docs/CONSOLIDATION-PLAN.md, step 0).

Every Lean declaration under `lean/` gets one class of docs/TRUST-MAP.md section 2:

* `K` core logic, `S` a feature's intended meaning: trusted by definition;
* `D` decoders and encoders, `G` glue, each with a group: `[V]` verdict-bearing, `[R]` reject-only
  or diagnostic, `[I]` identity and provenance; trusted unless tied to K or S by a theorem;
* `C` checked executables, `P` proofs and proof helpers, `T` tests and checks: not trusted.

Theorems are `P`, and `example` and `#guard`-style commands are `T`, by their kind (`KIND_CLASSES`);
a table entry for one of them is a problem, whatever class it names. Every other declaration takes
its class from the side table `tools/trust-classes.json` (open question 11 of the plan: a side
table changes no Lean file hash). A table entry may name the theorems that tie a D or G
declaration (`{"name": ..., "tied": [theorem, ...]}`, at least one theorem); each such theorem
must be in `lean/statements.txt` (bundle ST), and the constants its statement uses (the dump's
`-- uses` line) must include the declaration and some other anchor, the meaning the tie points at.
The anchors are derived from the classification the budget reports, never from a table entry
alone: a declaration of the tree whose class validated and that the budget counts as K, S or
untied [V] (`is_anchor`). A declaration is its full name and its file's module together (`ident`),
as the dump's `name@Module` constants and predicates are: two files nothing imports together may
each define `VE.Demo.anchor`, and a statement about one says nothing about the other. The
predicate list must have read every file of the tree.

The declarations are the compiled environment's, never the source text's: `lean/declarations.txt`
(written by tools/lean_statements.py with the statement and predicate dumps) lists every constant
of each module with its kind and source range, and the hash of the source it was compiled from. A
declaration is a constant whose range no other constant's contains, named as Lean names it (a
quoted `«WellFormed»` is `WellFormed`, an anonymous instance has its generated name), so no
spelling of the source can change what is classified. A file whose source differs from the one
the list was compiled from fails every run.

A declaration's lines run from its docstring (or first attribute line) to the line before the
next declaration or structural command, as in the trust map's method (section 9); the source text
only places these boundaries. `example` and `#`-commands declare nothing and are T. Namespace,
section, `open`, `import` and similar lines, module comments and lines before the first
declaration are `o`. A line that reads as a declaration where Lean records none, and two
declarations on one line, fail the run.

The trusted count is K + S + untied D[V] + untied G[V] + unclassified declarations: a declaration
that is not in the side table is counted as untied [V], so new code is trusted until classified,
and a declaration whose class or tie fails validation is trusted too (and fails the run). The
default report, `--check`, `--write` and `--ledger` all read the tree through one validating pass
(`walk`) and one trust rule (`is_trusted`); none of them exits 0 while a problem stands.

    python3 tools/trust_map.py            # class counts of the tree
    python3 tools/trust_map.py --check    # exit 1 if K, S or untied [V] grew over the base without an allowance
    python3 tools/trust_map.py --since REV    # the same, with commit REV as the base
    python3 tools/trust_map.py --allow --reason TEXT --signed SIGNATURE   # record the growth as allowances
    python3 tools/trust_map.py --write    # the merge train, on main: budget := the measured tree
    python3 tools/trust_map.py --files PATH   # the per-file counts, for the gate record
    python3 tools/trust_map.py --ledger   # measured lines per plan step (E9, tools/consolidation-ledger.json)

The budget is a ratchet (architecture plan AR-4, DRI decision D3). docs/trust-baseline.json keeps
only `budget` (the K, S and untied [V] lines the merge train last measured on main) and
`allowances`, each `{"class": "K"|"S"|"V", "lines": n, "reason", "signature", "commit"}`: growth the
DRI signed, with the commit its lines were counted over. The list is the history: an allowance is
never removed, and one introduced on a branch is merged with the others by the `ve-generated` merge
driver (tools/regen_generated.py), so two branches that each add one merge without a conflict.

`--check` measures the tree against a base commit: `--since REV`, else `git merge-base HEAD main`, or
the first parent when HEAD is main's tip (the merge train after a merge; HEAD itself while the merge
is uncommitted, as in `tools/regen_generated.py --resolve`). The cap of each class is
the base's lines, measured now from the base's committed `lean/` and side table (`measure_rev`),
plus the allowances the tree's file adds to the base's (`introduced`). So the budget falls with
every merge that deletes trusted lines, whether or not the recorded number has caught up, and rises
only by an allowance in the same change. Outside a git work tree the cap is the recorded budget.
`--allow` appends one allowance per class for the growth over that cap; `--signed` is the DRI's
signature, required. `--write` sets `budget` to the measured lines after the same check; it is the
merge train's step on main (a branch only adds allowances), so it refuses on any other branch.

`--seed TRUST-MAP.md` updates the side table: current entries and ties stay, except that a
predicate (`lean/predicates.txt`, a declaration whose type ends in `Prop`) outside K, S, P and T takes
its meaning class and a kernel data type takes K; new declarations are classified by the rules in
`seed_module`, constrained to the classes that the trust map's section 11 row for its module
records (`--fresh` reclassifies everything). It does not touch the baseline.

A predicate is meaning a reviewer reads: classed C, [R] or [I] without a tie it fails every run.
So does a declaration holding a predicate among its parts (a `where` helper or a field inside its
range, or a generated predicate without a range whose name extends it), tied or not: the predicate's
lines are the declaration's, and a tie of the declaration says nothing about them.

Every constant of the compiled dumps is placed, or the run fails, in every entry point (`read_tree`,
`place_tree`): each predicate of the list is part of a declaration of its module's file (a file
with no declaration included), a predicate or a scanned module of no file of the tree fails, and so
does a constant without a source range whose name extends no constant (`generated`: what
`run_elab` or `addDecl` adds, which no line of the file can be classified for).
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, replace
import fnmatch
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "lean"
TABLE = ROOT / "tools/trust-classes.json"
LEDGER = ROOT / "tools/consolidation-ledger.json"
BASELINE = ROOT / "docs/trust-baseline.json"
STATEMENTS = LEAN / "statements.txt"

sys.path.insert(0, str(LEAN))
sys.path.insert(0, str(ROOT / "tools"))
from audit import code_only  # noqa: E402
from lean_statements import (DECLARATIONS, PREDICATES, Declared, declaration_list, module_name,  # noqa: E402
                             parse as parse_statements, predicate_list, predicates as lean_predicates,
                             source_hash, sources, uses)

COLUMNS = ("K", "S", "D", "G", "C", "P", "T", "o")
CLASSES = ("K", "S", "C", "P", "T", *(f"{c}[{g}]" for c in "DG" for g in "VRI"))
GROUPS = ("V", "R", "I")

# Source text places line boundaries only. A line that reads as a declaration must be where Lean
# records one (or an `example`, which declares nothing); names and kinds come from the dump.
DECL = re.compile(
    r"^\s*(?:@\[[^\]]*\]\s*)*(?:(?:private|protected|noncomputable|nonrec|partial|unsafe|scoped|local)\s+)*"
    r"(?P<kind>class\s+inductive|deriving\s+instance|def|abbrev|structure|inductive|class|instance|theorem|"
    r"lemma|example|opaque|axiom|macro_rules|macro|syntax|notation|infixl|infixr|infix|prefix|postfix|elab)\b")
COMMAND = re.compile(r"^\s*#(?:guard_msgs|guard|eval|print|check|reduce|synth)\b")
STRUCTURAL = re.compile(r"^\s*(?:namespace|end|section|noncomputable\s+section|open|variable|universe|"
                        r"set_option|import|attribute|mutual|export)\b")
PREFIX = re.compile(r"^\s*(?:@\[[^\]]*\]\s*)+$|^\s*(?:set_option|open)\b.*\bin\s*$")


@dataclass
class Decl:
    name: str | None
    kind: str
    start: int  # 1-based, inclusive
    end: int  # inclusive
    # The compiled constants that are part of it: those inside its source range (`top_level`) and
    # generated ones without a range whose name extends it (`place`).
    parts: tuple[str, ...] = ()

    @property
    def lines(self) -> int:
        return self.end - self.start + 1


def internal(name: str) -> bool:
    """A name Lean generates (a component starting with `_`, as `_aux_…_macroRules_…`)."""
    return any(part.startswith("_") for part in name.split("."))


def top_level(declared: list[Declared]) -> tuple[list[Declared], dict[str, list[str]], list[str]]:
    """The declarations of one compiled module: every constant whose source range no other
    constant's range contains, the constants inside each one's range (by its name), and the
    problems. A constant inside another's range is part of it (a structure's fields and derived
    instances, a `where` helper, a macro's generated rules): its lines are the declaration's, and
    so is its validation (`classify` checks the predicates among the parts). Of constants with one
    range, the one the others' names extend is the declaration, a generated name never; two
    unrelated names on one range are a problem, since neither can be told apart from the other."""
    ordered = sorted(declared, key=lambda d: (d.start, (-d.end[0], -d.end[1]), internal(d.name), len(d.name), d.name))
    tops: list[Declared] = []
    parts: dict[str, list[str]] = {}
    problems: list[str] = []
    for d in ordered:
        top = tops[-1] if tops else None
        if top is not None and top.start <= d.start and d.end <= top.end:
            if (d.start, d.end) == (top.start, top.end) and not d.name.startswith(top.name + ".") \
                    and not internal(d.name):
                problems.append(f"{d.name} and {top.name} share one source range")
            parts[top.name].append(d.name)
            continue
        tops.append(d)
        parts[d.name] = []
    return tops, parts, problems


def scan(path: Path, declared: list[Declared]) -> tuple[list[Decl], int, list[str]]:
    """The declarations of one Lean file, its line count and the problems found. The declarations,
    their names and kinds are the compiled module's (`declared`, from lean/declarations.txt); the
    source text only places line boundaries. A declaration's lines run from its first line (moved up
    over `set_option … in` and attribute-only lines before it; its docstring is in its range) to
    the line before the next declaration, unnamed command (`example`, `#guard` and the like: T) or
    structural line. A line that reads as a declaration outside every compiled declaration, and two
    declarations starting on one line, are problems (and trusted, unnamed). Lines are counted as
    Lean counts them, split at newlines only."""
    text = path.read_text()
    code = code_only(text).split("\n")
    total = text.count("\n") + (0 if text.endswith("\n") or not text else 1)
    tops, parts, problems = top_level(declared)

    def opened(number: int) -> int:
        """The first line of a declaration or command written at line `number`."""
        start, above = number, number - 1
        while above >= 1 and (not code[above - 1].strip() or PREFIX.match(code[above - 1])):
            if code[above - 1].strip():
                start = above
            above -= 1
        return start

    named: dict[int, list[Declared]] = defaultdict(list)
    for d in tops:
        named[opened(d.start[0])].append(d)
    # Lines inside a declaration's compiled range after its first: nothing written there ends it.
    inside = {n for d in tops for n in range(d.start[0] + 1, d.end[0] + 1)}
    unnamed: dict[int, str] = {}
    boundaries: set[int] = set()
    for number, line in enumerate(code[:total], 1):
        if not line.strip() or PREFIX.match(line) or number in inside:
            continue
        decl = DECL.match(line)
        if COMMAND.match(line) or decl and decl["kind"] == "example":
            unnamed.setdefault(opened(number), "command")
        elif decl:
            if not any(d.start[0] == number for d in tops):
                unnamed.setdefault(opened(number), "unrecorded")
                problems.append(f"line {number} reads as a declaration, but the compiled module records none there")
        elif STRUCTURAL.match(line):
            boundaries.add(number)
    # A module docstring or comment block at top level also ends the declaration before it.
    for number, line in enumerate(text.split("\n")[:total], 1):
        if re.match(r"/-(?!-)", line) and number not in inside:
            boundaries.add(number)
    stops = sorted(set(named) | set(unnamed) | boundaries | {total + 1})
    decls = []
    for start in sorted(set(named) | set(unnamed)):
        end = next(stop for stop in stops if stop > start) - 1
        here = named.get(start, [])
        if len(here) > 1:
            problems.append(f"line {start}: {', '.join(d.name for d in here)} start on one line; "
                            "write each declaration on its own lines")
            decls.append(Decl(None, "unrecorded", start, end))
        elif here:
            decls.append(Decl(here[0].name, here[0].kind, start, end, tuple(parts[here[0].name])))
        else:
            decls.append(Decl(None, unnamed[start], start, end))
    return decls, total, problems


def module_key(path: Path, root: Path = ROOT) -> str:
    return path.relative_to(root / "lean").as_posix()


def load_table(path: Path = TABLE) -> dict[str, dict[str, object]]:
    data = json.loads(path.read_text())
    table: dict[str, dict[str, object]] = {}
    for module, classes in data["modules"].items():
        entries = table.setdefault(module, {})
        for cls, names in classes.items():
            if cls not in CLASSES:
                raise ValueError(f"{path.name}: {module}: unknown class {cls}")
            for name in names:
                entry: object = cls
                if isinstance(name, dict):
                    tied = name.get("tied")
                    if set(name) != {"name", "tied"} or not isinstance(name["name"], str) \
                            or not isinstance(tied, list) or not tied \
                            or not all(isinstance(t, str) and t for t in tied):
                        raise ValueError(f"{path.name}: {module}: a tie must be {{\"name\": str, \"tied\": "
                                         f"[theorem, ...]}} with at least one theorem: {name!r}")
                    entry, name = {"class": cls, "tied": list(tied)}, name["name"]
                if not isinstance(name, str):
                    raise ValueError(f"{path.name}: {module}: {name!r} is not a declaration name")
                if name in entries:
                    raise ValueError(f"{path.name}: {module}: {name} is listed twice")
                entries[name] = entry
    return table


def statements(path: Path = STATEMENTS) -> dict[str, set[tuple[str, str]] | None]:
    """The theorems of lean/statements.txt and the constants on each one's `-- uses` line as
    (defining module, full name) (None for an entry without that line, or one written before it
    carried modules)."""
    if not path.is_file():
        return {}
    return {name: uses(body) for name, body in parse_statements(path.read_text()).items()}


# Declarations whose kind fixes their class: the side table cannot name them. `command` is a
# stretch of source that declares nothing (`example`, `#guard` and the like).
KIND_CLASSES = {"theorem": "P", "command": "T"}


Ident = tuple[str, str]  # (defining Lean module, full name), as the dump's `name@Module`


def ident(module: str, name: str) -> Ident:
    """A declaration named `name` in the file `module` (a path under lean/), as the dump names it."""
    return module_name(module), name


def reads_meaning(cls: str, tied: bool) -> bool:
    """The classes a predicate's lines may take: those a reviewer reads (K, S, untied [V]) and
    proof or test helpers (P, T). An untied C, [R] or [I] class would drop it from the budget unread."""
    return cls in {"K", "S", "P", "T"} or cls[0] in "DG" and cls.endswith("[V]") and not tied


def held_predicates(module: str, decl: Decl, predicates: set[Ident]) -> list[str]:
    """The predicates among the compiled constants that are part of `decl` (`Decl.parts`)."""
    return [part for part in decl.parts if ident(module, part) in predicates]


def place(module: str, decls: list[Decl], predicates: set[Ident]) -> tuple[list[Decl], list[str]]:
    """`decls` (one file's) with every predicate of `module` that has no source range of its own
    (a generated `Path.below`) added to the parts of the declaration its name extends, and the
    problems: a predicate that is neither a declaration, nor inside one's range, nor extends one's
    name would be classed with no line of the file, unread."""
    name = module_name(module)
    placed = {n for d in decls if d.name is not None for n in (d.name, *d.parts)}
    extra: dict[int, list[str]] = defaultdict(list)
    problems = []
    for pred_module, pred in sorted(predicates):
        if pred_module != name or pred in placed:
            continue
        owners = [i for i, d in enumerate(decls) if d.name is not None and pred.startswith(d.name + ".")]
        if not owners:
            problems.append(f"{module}: the predicate {pred} is part of no declaration of the file "
                            "(no source range, and its name extends none); rerun tools/lean_statements.py")
            continue
        extra[max(owners, key=lambda i: len(decls[i].name))].append(pred)
    return [replace(d, parts=d.parts + tuple(extra[i])) if i in extra else d for i, d in enumerate(decls)], problems


def classify(module: str, decl: Decl, table: dict, proved: dict[str, set[Ident] | None],
             trusted: set[Ident] = frozenset(), predicates: set[Ident] = frozenset()) -> tuple[str, bool, list[str]]:
    """(class, tied, problems) of one declaration. A tie holds when every listed theorem is in
    the statement dump and its statement mentions the declaration itself (its full name in its
    own module, not a same-named declaration of another namespace or another module) and some
    other declaration in `trusted`, the K, S or untied [V] meaning it is tied to.

    A declaration in `predicates` (its type ends in `Prop`) is a statement a reviewer reads, not
    executable code: it is K or S, a [V] D or G declaration, P or T (a proof or test helper), or a
    tied C, D or G declaration; an untied C, [R] or [I] class would drop it from the budget
    unread.

    A predicate inside the declaration (`decl.parts`: a `where` helper, a structure field) is
    checked the same way under the declaration's class, which its lines take: the declaration must
    be K, S, untied [V], P or T. A tie of the declaration does not tie it (the theorem is about the
    declaration, not about the meaning inside); a predicate to be tied is declared on its own."""
    entry = table.get(module, {}).get(decl.name) if decl.name is not None else None
    me = ident(module, decl.name) if decl.name is not None else None
    held = held_predicates(module, decl, predicates)
    if decl.kind in KIND_CLASSES:
        cls = KIND_CLASSES[decl.kind]
        if entry is None:
            return cls, False, []
        listed = entry if isinstance(entry, str) else entry["class"]
        return cls, False, [f"{module}: {decl.name}: a {decl.kind} is {cls} by its kind; the table cannot list it "
                            f"(it lists {listed}{' tied' if isinstance(entry, dict) else ''})"]
    if entry is None:
        return "?", False, []
    cls = entry if isinstance(entry, str) else entry["class"]
    if held and not reads_meaning(cls, isinstance(entry, dict)):
        how = "tied " if isinstance(entry, dict) else ""
        return cls, False, [f"{module}: {decl.name}: a declaration holding a predicate ({', '.join(held)}) cannot "
                            f"be {how}{cls}; classify it K or S (or P for a proof helper), or declare the "
                            "predicate on its own (a tie of the declaration does not tie what is inside it)"]
    if isinstance(entry, str):
        if me in predicates and not reads_meaning(entry, False):
            return entry, False, [f"{module}: {decl.name}: a predicate cannot be {entry} unless a theorem ties it; "
                                  "classify it K or S (or P for a proof helper)"]
        return entry, False, []
    problems = []
    if cls[0] not in "CDG":
        problems.append(f"{module}: {decl.name}: only C, D and G declarations can be tied")
    for theorem in entry["tied"]:
        used = proved.get(theorem)
        if theorem not in proved:
            problems.append(f"{module}: {decl.name}: tying theorem {theorem} is not in {STATEMENTS.name}")
        elif used is None:
            problems.append(f"{module}: {decl.name}: {STATEMENTS.name} has no uses line with defining modules "
                            f"for {theorem}; rerun tools/lean_statements.py")
        elif me not in used:
            problems.append(f"{module}: {decl.name}: the statement of {theorem} does not mention {decl.name} "
                            f"of {module_name(module)}")
        elif not used & (trusted - {me}):
            problems.append(f"{module}: {decl.name}: the statement of {theorem} mentions no K, S or untied [V] "
                            "declaration of the tree, validly classified, to tie it to")
    return cls, not problems, problems


def empty_counts() -> dict[str, int]:
    return {**{c: 0 for c in COLUMNS}, **{f"{c}[{g}]": 0 for c in "DG" for g in GROUPS},
            "tied": 0, "unclassified": 0, "trusted": 0, "lines": 0}


def is_trusted(cls: str, tied: bool, problems: list[str]) -> bool:
    """The one rule for what the budget counts as trusted: K, S, untied [V], an unclassified
    declaration, and (failing closed) a declaration whose class or tie did not validate."""
    return bool(problems) or cls in {"K", "S", "?"} or cls[0] in "DG" and cls.endswith("[V]") and not tied


def is_anchor(cls: str, tied: bool, problems: list[str]) -> bool:
    """What a tie can point at: a declaration the budget counts as trusted by its validated
    class (K, S, untied [V]); not one trusted only because it is unclassified or failed validation."""
    return not problems and cls != "?" and is_trusted(cls, tied, problems)


@dataclass
class Classified:
    module: str
    decl: Decl
    cls: str
    tied: bool
    trusted: bool


def scan_tree(root: Path = ROOT, declarations_path: Path | None = None
              ) -> tuple[list[tuple[str, Decl]], dict[str, int], list[str], set[str]]:
    """Every declaration under `root` with its module, the line count of each file, the problems
    found, and the files whose declarations are unknown. The declarations are those of
    lean/declarations.txt; a file whose source is not the one the list was compiled from (or that
    the list lacks) fails, and is scanned without any compiled declaration, so every line in it that
    reads as a declaration is trusted and unnamed. A `generated` constant (no source range, and its
    name extends no constant) fails: no line of its file is its own."""
    path = root / DECLARATIONS.relative_to(ROOT) if declarations_path is None else declarations_path
    problems: list[str] = []
    declared: dict[str, list[Declared]] = {}
    hashes: dict[str, str] = {}
    if not path.is_file():
        problems.append(f"{path.name} is missing; run tools/lean_statements.py")
    else:
        try:
            declared, hashes = declaration_list(path)
        except ValueError as error:
            problems.append(str(error))
    readable = not problems
    decls, lines, unread = [], {}, set()
    for source in sources(root):
        module = module_key(source, root)
        name = module_name(module)
        if hashes.get(name) != source_hash(source):
            if readable:  # an unreadable list is one problem already
                problems.append(f"{module}: {path.name} was not compiled from this source; rerun "
                                "tools/lean_statements.py")
            found, lines[module], _ = scan(source, [])  # one problem for the file, not one per line
            issues = []
            unread.add(module)
        else:
            ranged = [d for d in declared[name] if d.start is not None]
            found, lines[module], issues = scan(source, ranged)
            issues += [f"{d.name} ({d.kind}) has no source range and its name extends no constant (a metaprogram "
                       "such as `run_elab` or `addDecl` made it): no line of the file can be classified for it"
                       for d in declared[name] if d.start is None]
        problems += [f"{module}: {issue}" for issue in issues]
        decls += [(module, decl) for decl in found]
    for name in sorted(set(hashes) - {module_name(m) for m in lines}):
        problems.append(f"{path.name} lists module {name}, which is not a file of the tree; rerun "
                        "tools/lean_statements.py")
    return decls, lines, problems, unread


def place_tree(decls: list[tuple[str, Decl]], files: Iterable[str], predicates: set[Ident],
               unread: set[str] = frozenset()) -> tuple[list[tuple[str, Decl]], list[str]]:
    """`decls` with every predicate of the list placed (`place`), and the problems. The predicate
    list drives it, not the declarations: each predicate is placed in the file of its module, a
    file without any declaration included, and a predicate of a module that is no file of the tree
    (`files`, paths under lean/) fails. The predicates of a file whose declarations are unknown
    (`unread`, already failing) are not placed."""
    by_module: dict[str, list[Decl]] = defaultdict(list)
    for module, decl in decls:
        by_module[module].append(decl)
    modules = list(dict.fromkeys([*files, *by_module]))
    out, problems = [], []
    for module in modules:
        found = by_module.get(module, [])
        if module not in unread:
            found, issues = place(module, found, predicates)
            problems += issues
        out += [(module, decl) for decl in found]
    known = {module_name(module) for module in modules}
    problems += [f"{PREDICATES.name}: the predicate {pred} is of module {pred_module}, which is not a file of the "
                 "tree; rerun tools/lean_statements.py" for pred_module, pred in sorted(predicates) if pred_module not in known]
    return out, problems


def classify_tree(decls: list[tuple[str, Decl]], table: dict, proved: dict[str, set[Ident] | None],
                  predicates: set[Ident], files: Iterable[str],
                  unread: set[str] = frozenset()) -> tuple[list[Classified], list[str]]:
    """Every declaration with its validated class, and the problems found. The anchors a tie may
    point at come from a first pass over the same declarations without any anchor (`is_anchor`:
    a tied declaration never validates there, so ties cannot anchor each other); the second pass
    checks the ties against them. An anchor is a declaration of one module (`ident`): a namesake
    of an anchor in another module anchors nothing. Every predicate of the list is part of one
    declaration of its file (`files`, paths under lean/) first (`place_tree`)."""
    decls, problems = place_tree(decls, files, predicates, unread)
    first = [classify(module, decl, table, proved, frozenset(), predicates) for module, decl in decls]
    trusted = {ident(module, decl.name) for (module, decl), result in zip(decls, first)
               if decl.name is not None and is_anchor(*result)}
    out, seen = [], defaultdict(set)
    for (module, decl), (cls, tied, issues) in zip(decls, first):
        if isinstance(table.get(module, {}).get(decl.name), dict):
            cls, tied, issues = classify(module, decl, table, proved, trusted, predicates)
        problems += issues
        if decl.name is not None:
            seen[module].add(decl.name)
        out.append(Classified(module, decl, cls, tied, is_trusted(cls, tied, issues)))
    for module, entries in table.items():
        if module in unread:  # its declarations are unknown; the file already fails
            continue
        for name in sorted(set(entries) - seen.get(module, set())):
            problems.append(f"{TABLE.name}: {module}: {name} is not a declaration of that file")
    return out, problems


def read_tree(root: Path = ROOT, predicates_path: Path | None = None
              ) -> tuple[list[tuple[str, Decl]], dict[str, int], set[Ident], set[str], list[str]]:
    """The tree as the compiled dumps record it: every declaration with its module (`scan_tree`),
    the line count of each file, the predicates, the files whose declarations are unknown, and the
    problems. The predicate list must have read every file of the tree, and only those: a module
    it read that is no file would hold predicates no file accounts for. Every entry point (`walk`,
    `seed`) reads the tree here."""
    predicates_path = root / PREDICATES.relative_to(ROOT) if predicates_path is None else predicates_path
    problems, predicates, scanned = [], set(), None
    if not predicates_path.is_file():
        problems.append(f"{predicates_path.name} is missing; run tools/lean_statements.py")
    else:
        try:
            predicates, scanned = predicate_list(predicates_path)
        except ValueError as error:
            problems.append(str(error))
    decls, lines, scanned_problems, unread = scan_tree(root)
    problems += scanned_problems
    if scanned is not None:
        # A predicate of a file the scan did not read would be classed without anyone knowing.
        for module in lines:
            if module_name(module) not in scanned:
                problems.append(f"{module}: {predicates_path.name} did not read module {module_name(module)}; "
                                "rerun tools/lean_statements.py")
        for name in sorted(scanned - {module_name(module) for module in lines}):
            problems.append(f"{predicates_path.name} read module {name}, which is not a file of the tree; rerun "
                            "tools/lean_statements.py")
    return decls, lines, predicates, unread, problems


def walk(root: Path = ROOT, table_path: Path = TABLE, statements_path: Path = STATEMENTS,
         predicates_path: Path | None = None) -> tuple[list[Classified], dict[str, int], list[str]]:
    """Every declaration under `root` with its validated class, the line count of each file, and
    the problems found (unknown table entries, entries for theorems, unverified ties, predicates in
    an untrusted class or of no declaration, a missing predicate list, a declaration list not
    compiled from the tree, a generated constant). `measure` and `ledger` both read the tree
    through this one pass, so neither can report numbers whose classification failed validation."""
    table = load_table(table_path)
    proved = statements(statements_path)
    decls, lines, predicates, unread, problems = read_tree(root, predicates_path)
    out, found = classify_tree(decls, table, proved, predicates, lines, unread)
    return out, lines, problems + found


def measure(root: Path = ROOT, table_path: Path = TABLE, statements_path: Path = STATEMENTS,
            predicates_path: Path | None = None) -> tuple[dict[str, dict[str, int]], list[str]]:
    """Per-file counts and the problems `walk` found."""
    decls, lines, problems = walk(root, table_path, statements_path, predicates_path)
    files = {}
    for module, total in lines.items():
        counts = empty_counts()
        counts["lines"] = counts["o"] = total
        files[module] = counts
    for d in decls:
        counts = files[d.module]
        counts["o"] -= d.decl.lines
        if d.trusted:
            counts["trusted"] += d.decl.lines
        if d.cls == "?":
            counts["unclassified"] += d.decl.lines
            continue
        counts[d.cls[0]] += d.decl.lines
        if d.tied:
            counts["tied"] += d.decl.lines
        if d.cls[0] in "DG":
            counts[d.cls] += d.decl.lines
    return files, problems


def totals(files: dict[str, dict[str, int]]) -> dict[str, int]:
    out = empty_counts()
    for counts in files.values():
        for key, value in counts.items():
            out[key] += value
    return out


def budget(counts: dict[str, int]) -> dict[str, int]:
    """The three budget quantities: K, S and untied [V] (unclassified counted as [V])."""
    return {"K": counts["K"], "S": counts["S"], "V": counts["trusted"] - counts["K"] - counts["S"]}


# The budget file ---------------------------------------------------------------------------------

BUDGET = ("K", "S", "V")
ALLOWANCE = ("class", "lines", "reason", "signature", "commit")
COMMIT = re.compile(r"[0-9a-f]{7,40}")
COMMENT = ("The trust budget (tools/trust_map.py, architecture plan AR-4, DRI decision D3): K, S and untied [V] "
           "lines as the merge train last measured them on main (`--write`), and every signed allowance that "
           "raised them (`--allow`). The check measures the base commit; per-file counts are in the gate record "
           "(`--files`), not here.")
# Entries of the baseline before AR-4 that a person rebaselined with `--write --reason` carry no signature.
UNSIGNED = "unsigned: rebaselined with a reason (trust_map.py --write --reason) before AR-4"


def allowance_problems(entry: object) -> list[str]:
    """Why `entry` is not an allowance: exactly the fields of `ALLOWANCE`, a budget class, a positive
    number of lines (an integer, not a boolean), a reason and a signature that are not blank, and the
    commit (hexadecimal) the lines were counted over."""
    if not isinstance(entry, dict) or set(entry) != set(ALLOWANCE):
        return [f"an allowance has exactly the fields {', '.join(ALLOWANCE)}: {entry!r}"]
    problems = []
    if entry["class"] not in BUDGET:
        problems.append(f"class {entry['class']!r} is not one of {', '.join(BUDGET)}")
    if type(entry["lines"]) is not int or entry["lines"] <= 0:
        problems.append(f"lines {entry['lines']!r} is not a positive integer")
    for field in ("reason", "signature"):
        if not isinstance(entry[field], str) or not entry[field].strip():
            problems.append(f"{field} {entry[field]!r} is blank")
    if not isinstance(entry["commit"], str) or not COMMIT.fullmatch(entry["commit"]):
        problems.append(f"commit {entry['commit']!r} is not a commit id")
    return problems


def from_history(old: dict) -> list[dict]:
    """The allowances of a baseline written before AR-4 (`history` and `signed`), without their
    commit: a signed entry's `allow`, a rebaseline's growth from `rebaselined_from` to `to` (a fall is
    no allowance). An entry recorded twice is one allowance."""
    out: list[dict] = []
    for entry in [*old.get("history", []), *old.get("signed", [])]:
        if "allow" in entry:
            grown = entry["allow"]
        elif entry.get("rebaselined_from") and entry.get("to"):
            grown = {c: entry["to"][c] - entry["rebaselined_from"][c] for c in BUDGET}
        else:
            grown = {}
        for cls in BUDGET:
            item = {"class": cls, "lines": grown.get(cls, 0), "reason": entry["change"],
                    "signature": entry.get("signed") or UNSIGNED}
            if item["lines"] > 0 and item not in out:
                out.append(item)
    return out


def parse_baseline(data: object, legacy: bool = False) -> tuple[dict, list[str]]:
    """The budget file's `budget` and `allowances`, and the problems found. `legacy` reads a base
    commit's file written before AR-4 too (its recorded budget and `from_history`)."""
    if legacy and isinstance(data, dict) and ("history" in data or "totals" in data):
        return {"budget": budget(data["totals"]), "allowances": from_history(data)}, []
    if not isinstance(data, dict) or not {"budget", "allowances"} <= set(data) <= {"comment", "budget", "allowances"}:
        return {}, [f"{BASELINE.name} holds exactly `budget` and `allowances` (and a `comment`)"]
    problems = []
    recorded = data["budget"]
    if not isinstance(recorded, dict) or set(recorded) != set(BUDGET) \
            or any(type(v) is not int or v < 0 for v in recorded.values()):
        problems.append(f"{BASELINE.name}: `budget` gives K, S and V as non-negative integers: {recorded!r}")
    if not isinstance(data["allowances"], list):
        problems.append(f"{BASELINE.name}: `allowances` is a list")
    else:
        problems += [f"{BASELINE.name}: allowance {i}: {p}" for i, entry in enumerate(data["allowances"])
                     for p in allowance_problems(entry)]
        if not problems:  # a copy of an allowance grants its lines again: each signed growth is recorded once
            seen = Counter(allowance_key(entry) for entry in data["allowances"])
            problems += [f"{BASELINE.name}: the allowance {key!r} is recorded {n} times"
                         for key, n in seen.items() if n > 1]
    return data, problems


def allowance_key(entry: dict) -> tuple:
    """What makes two allowances the same signed growth: the commit is where it was counted, not what."""
    return entry["class"], entry["lines"], entry["reason"], entry["signature"]


def introduced(allowances: list[dict], base: list[dict]) -> list[dict]:
    """The allowances of `allowances` that `base` does not have (each of `base` inherits one copy)."""
    inherited = Counter(allowance_key(entry) for entry in base)
    out = []
    for entry in allowances:
        if inherited[allowance_key(entry)]:
            inherited[allowance_key(entry)] -= 1
        else:
            out.append(entry)
    return out


def check(files: dict[str, dict[str, int]], cap: dict[str, int], allowances: list[dict],
          base: dict[str, dict[str, int]] | None = None) -> list[str]:
    """The classes whose measured lines exceed `cap` (the base's) plus the `allowances` introduced
    since, each naming the files that grew over `base`'s per-file counts when they are known."""
    now = budget(totals(files))
    allowed = Counter()
    for entry in allowances:
        allowed[entry["class"]] += entry["lines"]
    failures = []
    for key in BUDGET:
        if now[key] > cap[key] + allowed[key]:
            where = ""
            if base is not None:
                grown = sorted(((budget(c)[key] - budget(base.get(m, empty_counts()))[key], m)
                                for m, c in files.items()), reverse=True)
                where = ": " + ", ".join(f"{m} +{d}" for d, m in grown[:8] if d > 0)
            failures.append(f"{key} grew from {cap[key]} to {now[key]} (signed allowance {allowed[key]}){where}")
    return failures


def run_git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)


def resolve_base(root: Path, since: str | None) -> tuple[str | None, str | None]:
    """The base commit of the check and a problem. `since` names it; otherwise it is the merge base
    of HEAD and `main`, or HEAD's first parent when HEAD is main's tip, unless a merge is in progress
    (`MERGE_HEAD`: the merge train before its commit, `regen_generated.py --resolve`), whose first
    parent will be HEAD itself. Outside a git work tree whose top is `root` there is none (None,
    None); a work tree without `main` or a merge base is a problem."""
    if since is not None:
        named = run_git(root, "rev-parse", "--verify", "-q", f"{since}^{{commit}}")
        return (named.stdout.strip(), None) if named.returncode == 0 else (None, f"{since} names no commit")
    top = run_git(root, "rev-parse", "--show-toplevel")
    if top.returncode or Path(top.stdout.strip()).resolve() != root.resolve():
        return None, None
    head = run_git(root, "rev-parse", "HEAD").stdout.strip()
    merged = run_git(root, "merge-base", "HEAD", "main")
    if merged.returncode:
        return None, "no merge base of HEAD and `main`; name the base with --since REV"
    base = merged.stdout.strip()
    if base == head and run_git(root, "rev-parse", "-q", "--verify", "MERGE_HEAD").returncode:
        parent = run_git(root, "rev-parse", "--verify", "-q", "HEAD^1")
        if parent.returncode:
            return None, "HEAD is main's tip and has no parent; name the base with --since REV"
        base = parent.stdout.strip()
    return base, None


def measure_rev(rev: str, root: Path = ROOT) -> tuple[dict[str, dict[str, int]], list[str], dict | None]:
    """Measure the tree of commit `rev` with this tool's rules: its `lean/` and side table are read
    from git into a scratch directory (no worktree, index or stash is touched). Also returns that
    commit's baseline, or None when it has none. A git failure is a problem, never an empty tree."""
    table = TABLE.relative_to(ROOT).as_posix()
    archive = subprocess.run(["git", "-C", str(root), "archive", "--format=tar", rev, "--", "lean", table],
                             capture_output=True)
    if archive.returncode:
        return {}, [f"git archive {rev}: {archive.stderr.decode(errors='replace').strip()}"], None
    shown = subprocess.run(["git", "-C", str(root), "show", f"{rev}:{BASELINE.relative_to(ROOT).as_posix()}"],
                           capture_output=True)
    try:
        parent_baseline = json.loads(shown.stdout) if shown.returncode == 0 else None
    except ValueError as error:
        return {}, [f"{rev}: {BASELINE.name} is not JSON: {error}"], None
    with tempfile.TemporaryDirectory() as scratch:
        tree = Path(scratch)
        with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as tar:
            tar.extractall(tree, filter="data")
        files, problems = measure(tree, tree / table, tree / STATEMENTS.relative_to(ROOT))
    return files, [f"{rev}: {p}" for p in problems], parent_baseline


def write_baseline(path: Path, recorded: dict[str, int], allowances: list[dict]) -> None:
    """Write the budget file: the recorded budget and the allowances, in the one format the merge
    driver reproduces (indent 1, keys in this order)."""
    data = {"comment": COMMENT, "budget": {c: recorded[c] for c in BUDGET},
            "allowances": [{field: entry[field] for field in ALLOWANCE} for entry in allowances]}
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")


def write_files(path: Path, files: dict[str, dict[str, int]]) -> None:
    """The per-file counts (`--files`): for the gate record, never committed beside the budget."""
    now = totals(files)
    path.write_text(json.dumps({"budget": budget(now), "totals": now, "files": files}, indent=1,
                               ensure_ascii=False) + "\n")


# Seeding the side table from the trust map ------------------------------------------------------

def parse_section11(text: str) -> dict[str, dict[str, int]]:
    """Per-module class counts of TRUST-MAP.md section 11, keyed by the path under lean/."""
    body = text.split("## 11. Per-module line counts", 1)[1]
    rows: dict[str, dict[str, int]] = {}
    group = ""
    for line in body.splitlines():
        if line.startswith("**"):
            group = line
            continue
        if not line.startswith("| ") or line.startswith("| Module") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        name, values = cells[0], cells[1:]
        if "Top-level" in group:
            tot, g, t, o = values[:4]
            values = [tot, "–", "–", "–", g, "–", "–", t, o]
        if len(values) < 9:
            continue

        def numbers(index: int) -> list[int]:
            parts = values[index].split("/")
            return [0 if p.strip() in {"–", ""} else int(p.strip().replace(",", "")) for p in parts]

        def add(module: str, which: int) -> None:
            row = {}
            for i, column in enumerate(("lines", *COLUMNS), 0):
                parts = numbers(i)
                row[column] = parts[min(which, len(parts) - 1)]
            rows[module] = row

        if "Closure/ and Core/" in group:
            label = re.sub(r"\s*\(each\)", "", name)
            if label.startswith(("Core/",)):
                add(label + ".lean", 0)
            elif label.startswith("Closure/"):
                add(label + ".lean", 0)
            else:
                add(f"VE/Closure/{label}.lean", 0)
                add(f"VE/Core/{label}.lean", 1)
            continue
        if "Top-level" in group:
            add(f"{name}.lean", 0)
            continue
        if group.startswith("**VE/ (kernel)"):
            add(f"VE/{name}.lean", 0)
            continue
        add(f"VE/{name}.lean", 0)
    fixed = {}
    for module, row in rows.items():
        if module.startswith("Core/") or module.startswith("Closure/"):
            module = "VE/" + module
        # Rows that cover several files: each file gets the row, marked as shared.
        if " + " in module:
            stem = module.rsplit("/", 1)[0]
            for part in module.removesuffix(".lean").rsplit("/", 1)[1].split(" + "):
                fixed[f"{stem}/{part}.lean"] = {**row, "shared": 1}
        elif module.endswith("/*.lean"):
            for path in sorted((LEAN / module.removesuffix("*.lean")).glob("*.lean")):
                fixed[path.relative_to(LEAN).as_posix()] = {**row, "shared": 1}
        elif "`*Main`" in module:
            for path in sorted(LEAN.glob("*Main.lean")):
                if path.name != "RiskEvalMain.lean":
                    fixed[path.name] = {**row, "shared": 1}
        else:
            fixed[module] = row
    return fixed


SEED_RULES: list[tuple[str, str]] = [
    # (class, regular expression on the last name component); first allowed match wins.
    ("D", r"(?i)sha256|digest|hash|canon|^enc|^dec|decode|encode|json|parse|print|render|^pp|repr|lex|token|"
          r"^field|^str|strings|^read|^write|show|format|wire|text|quote|escape|utf|char"),
    ("G", r"(?i)^run|^main|dispatch|case|route|report|serve|handle|usage|envelope|answer|reply|output|"
          r"^max|limit|budget|^mode|kinds?$|protocol|request|response|service|handshake|status"),
    ("C", r"(?i)check|replay|^eval|evaluate|^elab|elaborate|verify|valid|admit|refute|search|count|"
          r"inline|soften|correlate|lower|fill|derive|witness|tableau|closed|step|close|expand|subst"),
    ("K", r"(?i)^formula$|denote|entails|^structure$|^env|^term|^sort|^model|holds|^sat$|admissible|^atom|"
          r"^pred|^var|^value$|^interp"),
    ("S", r"(?i)intended|conflict|followable|^value|permitted|required|forbidden|meaning|semantic|^sat|"
          r"holds|admissible|^acc|right|duty|norm|risk|status|outcome"),
]
IDENTITY = re.compile(r"(?i)sha256|digest|hash|nonce|identity|^id$|Id$|binding|canon")
REJECT = re.compile(r"(?i)diagnos|error|message|lint|usage|explain|reject|warn|limit|^max|fault|hint|"
                    r"rejection|unsupported|invalid")


def group_of(cls: str, short: str) -> str:
    if cls in {"D", "G"}:
        return f"{cls}[{'I' if IDENTITY.search(short) else 'R' if REJECT.search(short) else 'V'}]"
    return cls


# The logic itself (TRUST-MAP 4.1): v0, closure, core, order and time syntax, typing, structures
# and semantics, and the route layer. Their data types are K, as their predicates are.
KERNEL = re.compile(r"^VE/(?:(?:Closure|Core|Order|Time)/)?(?:Syntax|Semantics|Finite|Consequence|Paths)\.lean$"
                    r"|^VE/Route/(?:Layer|Checker)\.lean$")


def predicate_class(module: str, row: dict[str, int] | None) -> str:
    """The seeded class of a predicate (a declaration whose type ends in `Prop`): the meaning
    class its row allows (K in the kernel modules, otherwise S first), else trusted [V] glue,
    else a proof or test helper. Never C, [R] or [I]: those leave it out of the budget unread."""
    if row is None:
        return "S"
    if row.get("K", 0) > 0 and (KERNEL.match(module) or not row.get("S", 0)):
        return "K"
    if row.get("S", 0) > 0:
        return "S"
    if row.get("K", 0) > 0:
        return "K"
    if row.get("G", 0) > 0 or row.get("D", 0) > 0:
        return "G[V]" if row.get("G", 0) >= row.get("D", 0) else "D[V]"
    return "T" if row.get("T", 0) > row.get("P", 0) else "P"


def seed_module(module: str, decls: list[Decl], row: dict[str, int] | None,
                predicates: set[Ident] = frozenset(), kept: dict[str, object] | None = None) -> dict[str, object]:
    """Seeded classes of the named non-theorem declarations of one file.

    `kept` is the file's current table: its ties and classes stay, except that a predicate (or a
    declaration with a predicate among its parts, tied or not) not already K, S, P or T takes
    `predicate_class` and a data type of a kernel module takes K. The other
    declarations are new. The classes a file may use are those its section 11 row records (a file
    without a row gets G, so it counts as trusted). Inside that set a new declaration takes the
    first class whose name rule matches (`SEED_RULES`) while that class has room left in the row; the rest fill the
    classes with the most room left, largest declaration first.
    """
    kept = kept or {}
    sizes: dict[str, int] = {}
    kinds: dict[str, str] = {}
    holds: set[str] = set()  # declarations with a predicate inside (`held_predicates`)
    for decl in decls:
        if decl.kind in KIND_CLASSES or decl.name is None:
            continue
        sizes[decl.name] = sizes.get(decl.name, 0) + decl.lines
        kinds.setdefault(decl.name, decl.kind)
        if held_predicates(module, decl, predicates):
            holds.add(decl.name)
    short = {name: name.rsplit(".", 1)[-1] for name in sizes}
    allowed = [c for c in ("K", "S", "D", "G", "C") if row is not None and row.get(c, 0) > 0]
    test_module = re.search(r"Examples|Checks|ResponseDecode|RiskEvalMain", module) is not None
    out: dict[str, object] = {}
    for name in sizes:
        old = kept.get(name)
        if isinstance(old, dict) and name not in holds:  # a tie is a reviewed fact, checked on every run
            out[name] = old
        elif ident(module, name) in predicates or name in holds:
            # K, S, P and T are reviewed choices for a predicate (or a declaration holding one, which
            # a tie does not cover: `classify`); any other class is not allowed.
            out[name] = old if old in ("K", "S", "P", "T") else predicate_class(module, row)
        elif KERNEL.match(module) and "K" in allowed and kinds[name] in {"structure", "inductive"}:
            out[name] = "K"
        elif old is not None:
            out[name] = old
        elif row is not None and row.get("T", 0) > 0 and test_module \
                and (kinds[name] not in {"structure", "inductive"} or not allowed):
            out[name] = "T"
    rest = [name for name in sizes if name not in out]
    if row is None:
        return {**out, **{name: group_of("G", short[name]) for name in rest}}
    if not allowed:
        fill = "T" if row.get("T", 0) > row.get("P", 0) else "P"
        return {**out, **{name: fill for name in rest}}
    if len(allowed) == 1:
        return {**out, **{name: group_of(allowed[0], short[name]) for name in rest}}
    room = Counter({c: row[c] for c in allowed})
    for name, entry in out.items():
        room[(entry if isinstance(entry, str) else entry["class"])[0]] -= sizes[name]
    chosen: dict[str, str] = {}
    for name in sorted(rest, key=lambda n: -sizes[n]):
        for c, pattern in SEED_RULES:
            if c in allowed and re.search(pattern, short[name]) and room[c] >= sizes[name] / 2:
                chosen[name] = c
                room[c] -= sizes[name]
                break
    for name in sorted(rest, key=lambda n: -sizes[n]):
        if name not in chosen:
            c = max(allowed, key=lambda c: room[c])
            chosen[name] = c
            room[c] -= sizes[name]
    return {**out, **{name: group_of(c, short[name]) for name, c in chosen.items()}}


def seed(trust_map: Path, root: Path = ROOT, table_path: Path = TABLE,
         fresh: bool = False) -> dict[str, dict[str, int]]:
    """Rewrite the side table: the current entries are kept (`seed_module`), new declarations
    seeded; `fresh` ignores the current table."""
    section11 = parse_section11(trust_map.read_text())
    modules: dict[str, dict[str, list[str]]] = {}
    old = {} if fresh or not table_path.is_file() else load_table(table_path)
    scanned, lines, predicates, unread, problems = read_tree(root)
    placed, placing = place_tree(scanned, lines, predicates, unread)
    if problems + placing:
        raise SystemExit("cannot seed from compiled dumps that fail: " + "; ".join((problems + placing)[:5]))
    by_module: dict[str, list[Decl]] = defaultdict(list)
    for module, decl in placed:
        by_module[module].append(decl)
    for path in sources(root):
        module = module_key(path, root)
        decls = by_module[module]
        classes: dict[str, list] = defaultdict(list)
        for name, entry in seed_module(module, decls, section11.get(module), predicates, old.get(module)).items():
            if isinstance(entry, dict):
                classes[entry["class"]].append({"name": name, "tied": entry["tied"]})
            else:
                classes[entry].append(name)
        if classes:
            modules[module] = {c: sorted(classes[c], key=lambda e: e if isinstance(e, str) else e["name"])
                               for c in CLASSES if classes.get(c)}
    table_path.write_text(json.dumps({
        "comment": ("Trust classes of Lean declarations (docs/TRUST-MAP.md section 2), read by "
                    "tools/trust_map.py. Seeded by `tools/trust_map.py --seed` from the trust map's "
                    "section 11 module rows, lean/predicates.txt and name rules; a reseed keeps "
                    "every entry except predicates outside K and S and kernel data types (see "
                    "seed_module). A tie is written {\"name\": ..., \"tied\": [theorem, ...]}."),
        "modules": modules}, indent=1, ensure_ascii=False) + "\n")
    return section11


# The E9 ledger -----------------------------------------------------------------------------------

def expand(pattern: str) -> list[str]:
    """A glob with `{a,b}` alternatives as plain fnmatch globs."""
    match = re.search(r"\{([^{}]*)\}", pattern)
    if not match:
        return [pattern]
    return [g for part in match[1].split(",")
            for g in expand(pattern[:match.start()] + part + pattern[match.end():])]


def ledger(root: Path = ROOT, path: Path = LEDGER, table_path: Path = TABLE,
           statements_path: Path = STATEMENTS, predicates_path: Path | None = None) -> tuple[list[dict], list[str]]:
    """Measured lines of each step of the ledger, and the problems found: every problem of `walk`
    (the same validation `measure` runs; a ledger over a table that fails it is not a measurement)
    and a selector that names no declaration. For each of `removed`, `tied` and `reclassified`: the
    trusted lines (`is_trusted`) of the declarations its selectors name, each declaration credited
    to the first step that names it, and the untrusted lines they name; `net` is removed + tied −
    `adds_est`, `score` is net ÷ (days × risk)."""
    walked, _, problems = walk(root, table_path, statements_path, predicates_path)
    # Proofs and tests are left out unless the trust rule counts them (failing closed). An unnamed
    # declaration (one the compiled module does not record) has the empty name: only a selector
    # without a name pattern names it.
    decls = [(d.module, d.decl.name or "", d.decl.lines, d.trusted, d.decl.start) for d in walked
             if d.decl.kind not in KIND_CLASSES or d.trusted]
    credited: set[tuple[str, int]] = set()
    rows = []
    for step in json.loads(path.read_text())["steps"]:
        row = {"step": step["step"], "title": step["title"], "days": step["days"], "risk": step["risk"],
               "adds_est": step.get("adds_est", 0)}
        for column in ("removed", "tied", "reclassified"):
            trusted_lines = untrusted_lines = 0
            for selector in step.get(column, []):
                globs = expand(selector["module"])
                names = re.compile(selector.get("names", ""))
                hits = [d for d in decls if any(fnmatch.fnmatchcase(d[0], g) for g in globs) and names.search(d[1])]
                if not hits:
                    problems.append(f"{path.name}: step {step['step']} {column}: {selector} names no declaration")
                for module, name, lines, trusted, start in hits:
                    if (module, start) in credited:
                        continue
                    credited.add((module, start))
                    if trusted:
                        trusted_lines += lines
                    else:
                        untrusted_lines += lines
            row[column] = trusted_lines
            row[f"{column}_untrusted"] = untrusted_lines
        row["net"] = row["removed"] + row["tied"] - row["adds_est"]
        row["score"] = round(row["net"] / (row["days"] * row["risk"]), 1)
        rows.append(row)
    return rows, problems


def print_ledger(rows: list[dict]) -> None:
    print("| Step | Removed | Tied | Reclassified [V]→[R] | Adds (est.) | Net | Days | Risk | Score |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        print(f"| {r['step']} {r['title']} | {r['removed']} | {r['tied']} | {r['reclassified']} | {r['adds_est']} | "
              f"{r['net']} | {r['days']} | {r['risk']} | {r['score']} |")


def report(files: dict[str, dict[str, int]], base: dict[str, dict[str, int]] | None = None,
           label: str = "") -> None:
    """The class counts of the tree and, against a measured `base`, the change per class and the
    files whose trusted lines changed most."""
    now = totals(files)
    print("class lines: " + ", ".join(f"{c} {now[c]}" for c in COLUMNS))
    print("D/G groups: " + ", ".join(f"{k} {now[k]}" for k in now if "[" in k))
    print(f"tied {now['tied']}, unclassified {now['unclassified']}, trusted {now['trusted']} "
          f"(K + S + untied [V] + unclassified), {now['lines']} lines in {len(files)} files")
    if base is not None:
        before = totals(base)
        print(f"against {label}: " + ", ".join(
            f"{k} {now[k] - before[k]:+d}" for k in ("K", "S", "D", "G", "tied", "unclassified", "trusted")))
        changed = [(m, c["trusted"] - base.get(m, empty_counts())["trusted"]) for m, c in files.items()]
        changed += [(m, -c["trusted"]) for m, c in base.items() if m not in files]
        for module, delta in sorted((x for x in changed if x[1]), key=lambda x: -abs(x[1]))[:20]:
            print(f"  {module}: trusted {delta:+d}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true",
                        help="fail if K, S or untied [V] grew over the base without an allowance introduced since")
    parser.add_argument("--since", metavar="REV", help="--check with commit REV as the base")
    parser.add_argument("--allow", action="store_true",
                        help="append an allowance per class for the growth over the base (with --reason, --signed)")
    parser.add_argument("--reason", help="with --allow, what the growth is")
    parser.add_argument("--signed", metavar="SIGNATURE", help="with --allow, the DRI's signature")
    parser.add_argument("--write", action="store_true",
                        help="the merge train, on main: set the budget to the measured tree after the check")
    parser.add_argument("--files", type=Path, metavar="PATH", help="write the per-file counts to PATH")
    parser.add_argument("--seed", type=Path, metavar="TRUST-MAP.md",
                        help="classify new declarations in tools/trust-classes.json")
    parser.add_argument("--fresh", action="store_true", help="with --seed, ignore the current table")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--ledger", action="store_true",
                        help="print the measured E9 ledger of tools/consolidation-ledger.json")
    args = parser.parse_args(argv)
    if (args.reason is not None or args.signed is not None) and not args.allow:
        parser.error("--reason and --signed go with --allow")
    if args.allow and not ((args.reason or "").strip() and (args.signed or "").strip()):
        parser.error("--allow needs a --reason and the DRI's --signed signature")
    if args.allow and args.write:
        parser.error("--allow is a branch's step and --write the merge train's; run one")
    root = args.root.resolve()
    table_path = root / TABLE.relative_to(ROOT)
    baseline_path = root / BASELINE.relative_to(ROOT)
    statements_path = root / STATEMENTS.relative_to(ROOT)
    if args.ledger:
        rows, problems = ledger(root, root / LEDGER.relative_to(ROOT), table_path, statements_path)
        for problem in problems:
            print(problem, file=sys.stderr)
        if problems:
            print("FAIL: the ledger is not reported while the table fails validation", file=sys.stderr)
            return 1
        print_ledger(rows)
        return 0
    if args.seed:
        seed(args.seed, root, table_path, fresh=args.fresh)
    files, problems = measure(root, table_path, statements_path)
    for problem in problems:
        print(problem, file=sys.stderr)
    if problems:
        report(files)
        return 1
    if args.files:
        write_files(args.files, files)
    if not (args.check or args.since or args.allow or args.write):
        report(files)
        return 0
    return gate(args, root, files, baseline_path)


def fail(message: str, code: int = 1) -> int:
    print(message, file=sys.stderr)
    return code


def gate(args: argparse.Namespace, root: Path, files: dict[str, dict[str, int]], baseline_path: Path) -> int:
    """`--check`, `--since`, `--allow` and `--write` over the measured tree (`main`)."""
    baseline = None
    if baseline_path.is_file():
        try:
            baseline, bad = parse_baseline(json.loads(baseline_path.read_text()))
        except ValueError as error:
            baseline, bad = None, [f"{baseline_path.name} is not JSON: {error}"]
        if bad:
            report(files)
            return fail("\n".join(bad))
    base, problem = resolve_base(root, args.since)
    if problem:
        report(files)
        return fail(f"FAIL: {problem}")
    allowances = baseline["allowances"] if baseline else []
    if base is None:  # outside a git work tree: the recorded budget, and no allowance is new
        report(files)
        if baseline is None:
            if args.write:  # the starting budget of a new tree
                write_baseline(baseline_path, budget(totals(files)), [])
                print(f"wrote {baseline_path.relative_to(root)}")
                return 0
            return fail(f"no baseline at {baseline_path}; run --write first", 2)
        if args.allow:
            return fail("FAIL: --allow counts growth over a base commit; run it in a git work tree")
        cap, new, measured_base, label = baseline["budget"], [], None, "the recorded budget"
    else:
        measured_base, base_problems, base_data = measure_rev(base, root)
        if base_problems:
            report(files)
            return fail("\n".join(base_problems) + f"\nFAIL: the tree of {base} does not measure cleanly")
        base_baseline, bad = parse_baseline(base_data, legacy=True) if base_data is not None \
            else ({"allowances": []}, [])
        if bad:
            report(files)
            return fail("\n".join(f"{base}: {p}" for p in bad))
        cap, label = budget(totals(measured_base)), base[:12]
        new = introduced(allowances, base_baseline["allowances"])
        gone = introduced(base_baseline["allowances"], allowances)  # the history only grows
        if gone:
            report(files)
            return fail("\n".join(f"FAIL: the allowance {allowance_key(entry)!r} of {base[:12]} was removed; "
                                  "the allowances are the history and are never removed" for entry in gone))
        report(files, measured_base, label)
        recorded = base_baseline.get("budget")
        if recorded is not None and {c: recorded[c] for c in BUDGET} != cap:
            print(f"note: {base[:12]} records the budget {recorded}; measured there {cap} (the merge train's "
                  "--write has not run since)")
    if args.allow:
        now, granted = budget(totals(files)), Counter()
        for entry in new:
            granted[entry["class"]] += entry["lines"]
        added = [{"class": c, "lines": now[c] - cap[c] - granted[c], "reason": args.reason.strip(),
                  "signature": args.signed.strip(), "commit": base} for c in BUDGET if now[c] > cap[c] + granted[c]]
        if not added:
            print(f"no growth over {label} beyond the allowances introduced since; nothing to allow")
            return 0
        write_baseline(baseline_path, baseline["budget"] if baseline else cap, [*allowances, *added])
        for entry in added:
            print(f"allowed {entry['class']} +{entry['lines']} over {label}")
        return 0
    failures = check(files, cap, new, measured_base)
    for failure in failures:
        print(f"BUDGET against {label}: {failure}", file=sys.stderr)
    if failures:
        return 1
    if args.write:
        branch = run_git(root, "symbolic-ref", "--short", "-q", "HEAD")
        if base is not None and branch.stdout.strip() != "main":
            return fail("FAIL: the budget is written by the merge train on main; on a branch, record growth "
                        "with --allow --reason ... --signed ...")
        write_baseline(baseline_path, budget(totals(files)), allowances)
        print(f"wrote {baseline_path.relative_to(root)}: budget {budget(totals(files))}")
        return 0
    print(f"PASS: K, S and untied [V] within {label} and the allowances introduced since")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
