#!/usr/bin/env python3
"""Trust budget (bundle TB of docs/CONSOLIDATION-PLAN.md, step 0).

Every Lean declaration under `lean/` gets one class of docs/TRUST-MAP.md section 2:

* `K` core logic, `S` a feature's intended meaning: trusted by definition;
* `D` decoders and encoders, `G` glue, each with a group: `[V]` verdict-bearing, `[R]` reject-only
  or diagnostic, `[I]` identity and provenance; trusted unless tied to K or S by a theorem;
* `C` checked executables, `P` proofs and proof helpers, `T` tests and checks: not trusted.

Theorems are `P`, and `example` and `#guard`-style commands are `T`, by their kind. Every other
declaration takes its class from the side table `tools/trust-classes.json` (open question 11 of
the plan: a side table changes no Lean file hash). A table entry may name the theorems that tie a
D or G declaration (`{"name": ..., "tied": [theorem, ...]}`, at least one theorem); each such
theorem must be in `lean/statements.txt` (bundle ST), and the constants its statement uses (the
dump's `-- uses` line, full names) must include the declaration and some other K, S or untied
[V] declaration, the meaning the tie points at.

A declaration's lines run from its docstring (or first attribute line) to the line before the
next declaration or structural command, as in the trust map's method (section 9). Namespace,
section, `open`, `import` and similar lines, module comments and lines before the first
declaration are `o`.

The trusted count is K + S + untied D[V] + untied G[V] + unclassified declarations: a declaration
that is not in the side table is counted as untied [V], so new code is trusted until classified.

    python3 tools/trust_map.py            # per-file counts against docs/trust-baseline.json
    python3 tools/trust_map.py --check    # exit 1 if K, S or untied [V] grew without a signed entry
    python3 tools/trust_map.py --write    # rewrite the baseline from the current tree
    python3 tools/trust_map.py --ledger   # measured lines per plan step (E9, tools/consolidation-ledger.json)

Growth of K, S or untied [V] (unclassified included) over the baseline fails `--check` unless the
baseline's `signed` list allows it: each entry is `{"change", "signed", "allow": {"K": n, "S": n,
"V": n}}`, a note signed by the DRI. `--write` moves the signed entries into `history`; growth
beyond them (a reclassification, not new code) needs `--reason`, which `history` keeps.

`--seed TRUST-MAP.md` updates the side table: current entries and ties stay, except that a
predicate (`lean/predicates.txt`, a declaration whose type ends in `Prop`) outside K, S, P and T takes
its meaning class and a kernel data type takes K; new declarations are classified by the rules in
`seed_module`, constrained to the classes that the trust map's section 11 row for its module
records (`--fresh` reclassifies everything). It does not touch the baseline; `--seed --write`
also keeps the section 11 counts in the baseline next to the measured ones.

A predicate is meaning a reviewer reads: classed C, [R] or [I] without a tie it fails every run.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
import fnmatch
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "lean"
TABLE = ROOT / "tools/trust-classes.json"
LEDGER = ROOT / "tools/consolidation-ledger.json"
BASELINE = ROOT / "docs/trust-baseline.json"
STATEMENTS = LEAN / "statements.txt"

sys.path.insert(0, str(LEAN))
sys.path.insert(0, str(ROOT / "tools"))
from audit import code_only  # noqa: E402
from lean_statements import PREDICATES, parse as parse_statements, predicates as lean_predicates, uses  # noqa: E402

COLUMNS = ("K", "S", "D", "G", "C", "P", "T", "o")
CLASSES = ("K", "S", "C", "P", "T", *(f"{c}[{g}]" for c in "DG" for g in "VRI"))
GROUPS = ("V", "R", "I")

DECL = re.compile(
    r"^\s*(?:@\[[^\]]*\]\s*)*(?:(?:private|protected|noncomputable|nonrec|partial|unsafe|scoped|local)\s+)*"
    r"(?P<kind>class\s+inductive|deriving\s+instance|def|abbrev|structure|inductive|class|instance|theorem|"
    r"lemma|example|opaque|axiom|macro_rules|macro|syntax|notation|infixl|infixr|infix|prefix|postfix|elab)"
    r"\b(?P<rest>.*)$")
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

    @property
    def lines(self) -> int:
        return self.end - self.start + 1


def doc_starts(text: str) -> dict[int, int]:
    """Map the last line of each `/-- ... -/` docstring to its first line (both 1-based)."""
    found, i, depth, start, quoted = {}, 0, 0, None, False
    while i < len(text):
        pair = text[i:i + 2]
        if depth:
            if pair == "/-":
                depth, i = depth + 1, i + 2
                continue
            if pair == "-/":
                depth, i = depth - 1, i + 2
                if depth == 0 and start is not None:
                    found[text.count("\n", 0, i) + 1] = start
                continue
        elif quoted:
            if text[i] == "\\":
                i += 2
                continue
            quoted = text[i] != '"'
        elif pair == "--":
            end = text.find("\n", i)
            i = len(text) if end < 0 else end
            continue
        elif pair == "/-":
            start = text.count("\n", 0, i) + 1 if text.startswith("/--", i) else None
            depth, i = 1, i + 2
            continue
        elif text[i] == '"':
            quoted = True
        i += 1
    return found


def item_name(kind: str, rest: str, scopes: list[str]) -> str | None:
    kind = " ".join(kind.split())
    if kind == "example":
        return None
    words = rest.split()
    if kind in {"def", "abbrev", "structure", "inductive", "class", "class inductive", "theorem", "lemma",
                "opaque", "axiom"} and words:
        base = words[0]
    elif kind == "instance" and words and not words[0].startswith((":", "(", "[", "{", "⦃")) \
            and not words[0].startswith("priority"):
        base = words[0]
    else:
        signature = re.split(r"\s(?:where|:=)(?:\s|$)", " " + rest.strip())[0].strip()
        return f"{kind}:{' '.join(signature.removeprefix(':').split())}"
    if base.startswith("_root_."):
        return base.removeprefix("_root_.")
    return ".".join([s for s in scopes if s] + [base])


def scan(path: Path) -> tuple[list[Decl], int]:
    """The declarations of one Lean file and its line count."""
    text = path.read_text()
    code = code_only(text).splitlines()
    docs = doc_starts(text)
    total = len(text.splitlines())
    scopes: list[str] = []
    starts: list[tuple[int, str, str | None]] = []  # (line, kind, name)
    boundaries: set[int] = set()
    pending: int | None = None
    for number, line in enumerate(code, 1):
        if not line.strip():
            continue
        if PREFIX.match(line):
            pending = pending or number
            continue
        decl = DECL.match(line)
        command = COMMAND.match(line)
        if decl or command:
            start = pending or number
            start = docs.get(start - 1, start)
            if decl:
                kind = " ".join(decl["kind"].split())
                starts.append((start, kind, item_name(kind, decl["rest"], scopes)))
            else:
                starts.append((start, "command", None))
            pending = None
            continue
        pending = None
        structural = STRUCTURAL.match(line)
        if structural:
            boundaries.add(number)
            namespace = re.match(r"\s*namespace\s+(\S+)", line)
            if namespace:
                scopes.append(namespace[1])
            elif re.match(r"\s*(?:noncomputable\s+)?section\b", line):
                scopes.append("")
            elif re.match(r"\s*end(?:\s|$)", line) and scopes:
                scopes.pop()
    # A module docstring or comment block at top level also ends the declaration before it.
    for number, line in enumerate(text.splitlines(), 1):
        if re.match(r"/-(?!-)", line):
            boundaries.add(number)
    stops = sorted({s for s, _, _ in starts} | boundaries | {total + 1})
    decls = []
    for start, kind, name in starts:
        following = next(stop for stop in stops if stop > start)
        decls.append(Decl(name, kind, start, following - 1))
    return decls, total


def sources(root: Path = ROOT) -> list[Path]:
    lean = root / "lean"
    return [p for p in sorted(lean.rglob("*.lean")) if ".lake" not in p.relative_to(lean).parts]


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


def statements(path: Path = STATEMENTS) -> dict[str, set[str] | None]:
    """The theorems of lean/statements.txt and the full names on each one's `-- uses` line
    (None for an entry without that line)."""
    if not path.is_file():
        return {}
    return {name: uses(body) for name, body in parse_statements(path.read_text()).items()}


def anchors(table: dict) -> set[str]:
    """Declarations a tie can point at: those the budget counts as trusted (K, S, untied [V])."""
    return {name for entries in table.values() for name, entry in entries.items()
            if isinstance(entry, str) and (entry in {"K", "S"} or entry.endswith("[V]"))}


def classify(module: str, decl: Decl, table: dict, proved: dict[str, set[str] | None],
             trusted: set[str] = frozenset(), predicates: set[str] = frozenset()) -> tuple[str, bool, list[str]]:
    """(class, tied, problems) of one declaration. A tie holds when every listed theorem is in
    the statement dump and its statement mentions the declaration itself (its full name, not a
    same-named declaration of another namespace) and some other declaration in `trusted`, the
    K, S or untied [V] meaning it is tied to.

    A declaration in `predicates` (its type ends in `Prop`) is a statement a reviewer reads, not
    executable code: it is K or S, a [V] D or G declaration, P or T (a proof or test helper), or a
    tied C, D or G declaration; an untied C, [R] or [I] class would drop it from the budget
    unread."""
    if decl.kind in {"theorem", "lemma"}:
        return "P", False, []
    if decl.kind in {"example", "command"}:
        return "T", False, []
    entry = table.get(module, {}).get(decl.name)
    if entry is None:
        return "?", False, []
    if isinstance(entry, str):
        if decl.name in predicates and (entry == "C" or entry[0] in "DG" and not entry.endswith("[V]")):
            return entry, False, [f"{module}: {decl.name}: a predicate cannot be {entry} unless a theorem ties it; "
                                  "classify it K or S (or P for a proof helper)"]
        return entry, False, []
    cls, problems = entry["class"], []
    if cls[0] not in "CDG":
        problems.append(f"{module}: {decl.name}: only C, D and G declarations can be tied")
    if decl.name is None or ":" in decl.name:
        problems.append(f"{module}: {decl.name}: an unnamed declaration cannot be tied")
    for theorem in entry["tied"]:
        used = proved.get(theorem)
        if theorem not in proved:
            problems.append(f"{module}: {decl.name}: tying theorem {theorem} is not in {STATEMENTS.name}")
        elif used is None:
            problems.append(f"{module}: {decl.name}: {STATEMENTS.name} has no uses line for {theorem}; "
                            "rerun tools/lean_statements.py")
        elif decl.name not in used:
            problems.append(f"{module}: {decl.name}: the statement of {theorem} does not mention {decl.name}")
        elif not used & (trusted - {decl.name}):
            problems.append(f"{module}: {decl.name}: the statement of {theorem} mentions no K, S or untied [V] "
                            "declaration to tie it to")
    return cls, not problems, problems


def empty_counts() -> dict[str, int]:
    return {**{c: 0 for c in COLUMNS}, **{f"{c}[{g}]": 0 for c in "DG" for g in GROUPS},
            "tied": 0, "unclassified": 0, "trusted": 0, "lines": 0}


def measure(root: Path = ROOT, table_path: Path = TABLE, statements_path: Path = STATEMENTS,
            predicates_path: Path | None = None) -> tuple[dict[str, dict[str, int]], list[str]]:
    """Per-file counts and the problems found (unknown table entries, unverified ties, predicates
    in an untrusted class)."""
    table = load_table(table_path)
    proved = statements(statements_path)
    trusted = anchors(table)
    predicates_path = root / PREDICATES.relative_to(ROOT) if predicates_path is None else predicates_path
    files, problems, seen = {}, [], defaultdict(set)
    if not predicates_path.is_file():
        problems.append(f"{predicates_path.name} is missing; run tools/lean_statements.py")
    predicates = lean_predicates(predicates_path)
    for path in sources(root):
        module = module_key(path, root)
        decls, total = scan(path)
        counts = empty_counts()
        counts["lines"] = total
        covered = 0
        for decl in decls:
            cls, tied, issues = classify(module, decl, table, proved, trusted, predicates)
            problems += issues
            if decl.name is not None:
                seen[module].add(decl.name)
            covered += decl.lines
            if cls == "?":
                counts["unclassified"] += decl.lines
                counts["trusted"] += decl.lines
                continue
            counts[cls[0]] += decl.lines
            if tied:
                counts["tied"] += decl.lines
            if cls[0] in "DG":
                counts[cls] += decl.lines
                if not tied and cls.endswith("[V]"):
                    counts["trusted"] += decl.lines
            elif cls in {"K", "S"}:
                counts["trusted"] += decl.lines
        counts["o"] = total - covered
        files[module] = counts
    for module, entries in table.items():
        for name in sorted(set(entries) - seen.get(module, set())):
            problems.append(f"{TABLE.name}: {module}: {name} is not a declaration of that file")
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


def check(files: dict[str, dict[str, int]], baseline: dict) -> list[str]:
    now = budget(totals(files))
    before = budget(baseline["totals"])
    allowed = Counter()
    for entry in baseline.get("signed", []):
        if not entry.get("signed"):
            return [f"signed entry {entry.get('change')!r} has no signature"]
        allowed.update(entry.get("allow", {}))
    failures = []
    for key in ("K", "S", "V"):
        if now[key] > before[key] + allowed[key]:
            grown = sorted(((counts_v - budget(baseline["files"].get(m, empty_counts()))[key], m)
                            for m, c in files.items()
                            if (counts_v := budget(c)[key]) > budget(baseline["files"].get(m, empty_counts()))[key]),
                           reverse=True)
            where = ", ".join(f"{m} +{d}" for d, m in grown[:8])
            failures.append(f"{key} grew from {before[key]} to {now[key]} (signed allowance {allowed[key]}): {where}")
    return failures


def write_baseline(files: dict[str, dict[str, int]], path: Path = BASELINE, section11: dict | None = None,
                   reason: str | None = None) -> None:
    """Rewrite the baseline. Growth beyond the signed allowances (`check`) is absorbed only with
    a `reason`, kept in `history` with the budget before and after."""
    old = json.loads(path.read_text()) if path.is_file() else {}
    unexplained = check(files, old) if old else []
    if unexplained and not reason:
        raise ValueError("the budget grew beyond the signed allowances; rebaseline with a reason: "
                         + "; ".join(unexplained))
    history = old.get("history", [])
    for entry in old.get("signed", []):
        history.append({**entry, "rebaselined_from": budget(old["totals"])})
    if reason:
        history.append({"change": reason, "rebaselined_from": budget(old["totals"]) if old else None,
                        "to": budget(totals(files))})
    data = {
        "comment": "Generated by tools/trust_map.py --write; see docs/CONSOLIDATION-PLAN.md step 0.",
        "totals": totals(files),
        "budget": budget(totals(files)),
        "signed": [],
        "history": history,
        "section11": section11 if section11 is not None else old.get("section11", {}),
        "files": files,
    }
    path.write_text(json.dumps(data, indent=1, sort_keys=False, ensure_ascii=False) + "\n")


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
                predicates: set[str] = frozenset(), kept: dict[str, object] | None = None) -> dict[str, object]:
    """Seeded classes of the named non-theorem declarations of one file.

    `kept` is the file's current table: its ties and classes stay, except that a predicate not
    already K, S, P or T takes `predicate_class` and a data type of a kernel module takes K. The other
    declarations are new. The classes a file may use are those its section 11 row records (a file
    without a row gets G, so it counts as trusted). Inside that set a new declaration takes the
    first class whose name rule matches (`SEED_RULES`) while that class has room left in the row; the rest fill the
    classes with the most room left, largest declaration first.
    """
    kept = kept or {}
    sizes: dict[str, int] = {}
    kinds: dict[str, str] = {}
    for decl in decls:
        if decl.kind in {"theorem", "lemma", "example", "command"} or decl.name is None:
            continue
        sizes[decl.name] = sizes.get(decl.name, 0) + decl.lines
        kinds.setdefault(decl.name, decl.kind)
    short = {name: name.rsplit(".", 1)[-1].split(":", 1)[-1] for name in sizes}
    allowed = [c for c in ("K", "S", "D", "G", "C") if row is not None and row.get(c, 0) > 0]
    test_module = re.search(r"Examples|Checks|ResponseDecode|RiskEvalMain", module) is not None
    out: dict[str, object] = {}
    for name in sizes:
        old = kept.get(name)
        if isinstance(old, dict):  # a tie is a reviewed fact, checked on every run
            out[name] = old
        elif name in predicates:
            # K, S, P and T are reviewed choices for a predicate; any other class is not allowed.
            out[name] = old if old in {"K", "S", "P", "T"} else predicate_class(module, row)
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
    predicates = lean_predicates(root / PREDICATES.relative_to(ROOT))
    old = {} if fresh or not table_path.is_file() else load_table(table_path)
    for path in sources(root):
        module = module_key(path, root)
        decls, _ = scan(path)
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
           statements_path: Path = STATEMENTS) -> tuple[list[dict], list[str]]:
    """Measured lines of each step of the ledger, and the problems found (a selector that names no
    declaration). For each of `removed`, `tied` and `reclassified`: the trusted lines (K, S,
    untied [V]) of the declarations its selectors name, each declaration credited to the first
    step that names it, and the untrusted lines they name; `net` is removed + tied − `adds_est`,
    `score` is net ÷ (days × risk)."""
    table = load_table(table_path)
    proved = statements(statements_path)
    trusted_names = anchors(table)
    predicates = lean_predicates(root / PREDICATES.relative_to(ROOT))
    decls = []  # (module, name, lines, trusted)
    for source in sources(root):
        module = module_key(source, root)
        for decl in scan(source)[0]:
            if decl.kind in {"theorem", "lemma", "example", "command"} or decl.name is None:
                continue
            cls, tied, _ = classify(module, decl, table, proved, trusted_names, predicates)
            trusted = cls in {"K", "S", "?"} or cls[0] in "DG" and cls.endswith("[V]") and not tied
            decls.append((module, decl.name, decl.lines, trusted))
    credited: set[tuple[str, str]] = set()
    rows, problems = [], []
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
                for module, name, lines, trusted in hits:
                    if (module, name) in credited:
                        continue
                    credited.add((module, name))
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


def report(files: dict[str, dict[str, int]], baseline: dict | None) -> None:
    now = totals(files)
    print("class lines: " + ", ".join(f"{c} {now[c]}" for c in COLUMNS))
    print("D/G groups: " + ", ".join(f"{k} {now[k]}" for k in now if "[" in k))
    print(f"tied {now['tied']}, unclassified {now['unclassified']}, trusted {now['trusted']} "
          f"(K + S + untied [V] + unclassified), {now['lines']} lines in {len(files)} files")
    if baseline:
        before = baseline["totals"]
        print("against the baseline: " + ", ".join(
            f"{k} {now[k] - before.get(k, 0):+d}" for k in ("K", "S", "D", "G", "tied", "unclassified", "trusted")))
        changed = [(m, now_c["trusted"] - baseline["files"].get(m, empty_counts())["trusted"])
                   for m, now_c in files.items()]
        changed += [(m, -c["trusted"]) for m, c in baseline["files"].items() if m not in files]
        for module, delta in sorted((x for x in changed if x[1]), key=lambda x: -abs(x[1]))[:20]:
            print(f"  {module}: trusted {delta:+d}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="fail if K, S or untied [V] grew without a signed entry")
    parser.add_argument("--write", action="store_true", help="rewrite docs/trust-baseline.json")
    parser.add_argument("--seed", type=Path, metavar="TRUST-MAP.md",
                        help="classify new declarations in tools/trust-classes.json (with --write, also "
                             "keep the section 11 counts in the baseline)")
    parser.add_argument("--fresh", action="store_true", help="with --seed, ignore the current table")
    parser.add_argument("--reason", help="with --write, why the budget grew beyond the signed allowances "
                                         "(a reclassification); kept in the baseline's history")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--ledger", action="store_true",
                        help="print the measured E9 ledger of tools/consolidation-ledger.json")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    table_path = root / TABLE.relative_to(ROOT)
    baseline_path = root / BASELINE.relative_to(ROOT)
    statements_path = root / STATEMENTS.relative_to(ROOT)
    if args.ledger:
        rows, problems = ledger(root, root / LEDGER.relative_to(ROOT), table_path, statements_path)
        for problem in problems:
            print(problem, file=sys.stderr)
        print_ledger(rows)
        return 1 if problems else 0
    section11 = seed(args.seed, root, table_path, fresh=args.fresh) if args.seed else None
    files, problems = measure(root, table_path, statements_path)
    for problem in problems:
        print(problem, file=sys.stderr)
    baseline = json.loads(baseline_path.read_text()) if baseline_path.is_file() else None
    report(files, None if args.write else baseline)
    if problems:
        return 1
    if args.write:
        try:
            write_baseline(files, baseline_path, section11, args.reason)
        except ValueError as error:
            print(f"BUDGET: {error}", file=sys.stderr)
            return 1
        print(f"wrote {baseline_path.relative_to(root)}")
        return 0
    if args.check:
        if baseline is None:
            print(f"no baseline at {baseline_path}; run --write first", file=sys.stderr)
            return 2
        failures = check(files, baseline)
        for failure in failures:
            print(f"BUDGET: {failure}", file=sys.stderr)
        if failures:
            return 1
        print("PASS: K, S and untied [V] within the baseline and its signed allowances")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
