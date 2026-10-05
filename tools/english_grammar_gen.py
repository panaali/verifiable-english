"""The fixed rules of English in Lean as data: source checks, the Lean table generator and the lock file.

    python tools/english_grammar_gen.py --check [--base REF]
    python tools/english_grammar_gen.py --write [--actions-version V]

docs/spec/english-lean-s2.md 2.9 (S2 plan, S2.0). Each profile's fixed rules are one JSON source under
`ve/english_grammar/` (an array of rows `{"tag", "lhs", "act", <action data>, "rhs", "status"?}`); a row with
`"status": "proposed"` stays in the source and out of the table (2.12). `--write` renders every source as an
`Array (Rule Terminal)` literal in `lean/VE/EnglishGrammar/Fixed/`, with the nonterminal catalogue of 2.4 and
its ranks, the action of each rule as the `act` text of the `english.grammar` export (4.4) and the SHA-256 of
the source; it renders `actionsVersion` from the lock file, and rewrites the lock file
`ve/english_grammar/LOCK.json`: the SHA-256 of each table source, each generated table and every Lean file
that holds a trusted definition of base 2.13 (base 2.12), with `actions_version`.

`--check` fails when a generated file differs from what its source gives (naming the profile and the first
differing rule tag, or the `proposed` row found in the table), when a hashed file differs from the lock
(naming the file and the two hashes), when a Lean file under `lean/VE/Grammar/` or `lean/VE/EnglishGrammar/`
is neither hashed nor listed as untrusted, and, against the lock of `--base` (the commit hook passes HEAD's),
when a hash changed and `actions_version` did not. The fixed rule `k` of a table has `act := k`: `fixedActs`
holds one action per fixed rule, in order (spec 5.2).

The module reads files only through a `read(path) -> bytes | None` and a `listing() -> paths` function, so the
commit hook runs the same checks on staged blobs; it imports nothing outside the standard library.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from typing import Callable, Iterable

ROOT = Path(__file__).resolve().parents[1]
LOCK = "ve/english_grammar/LOCK.json"
LOCK_FORMAT = "ve.english-grammar-lock@1"
VERSION_TARGET = "lean/VE/EnglishGrammar/Fixed/Version.lean"

# profile -> (JSON source, generated Lean module, Lean name of the table)
PROFILES = {
    "relational-fol@0": ("ve/english_grammar/relational-fol@0.json",
                         "lean/VE/EnglishGrammar/Fixed/RelationalFol.lean", "relationalFol"),
}

# The Lean files that hold a trusted definition of base 2.13 (base 2.12): the tokens and their matching, the
# lexer, the derivation checker, well-formedness, the reading relations, lexicon validity, the surface syntax
# and its rejection codes. S2's `lexRules`, action library, `meaning` and AST encoding join this list when
# their modules exist (spec 5.1).
TRUSTED = (
    "lean/VE/Grammar/Basic.lean",
    "lean/VE/Grammar/Derives.lean",
    "lean/VE/Grammar/Meaning.lean",
    "lean/VE/Grammar/Reading.lean",
    "lean/VE/EnglishGrammar/Token.lean",
    "lean/VE/EnglishGrammar/Lexer.lean",
    "lean/VE/EnglishGrammar/Lexicon.lean",
    "lean/VE/EnglishGrammar/Syntax.lean",
)
# Lean files of the same directories that hold no trusted definition, with the reason.
UNTRUSTED = {
    "lean/VE/Grammar/Extension.lean": "rule maps and the extension theorems: proved",
    "lean/VE/Grammar/Table.lean": "the parser: proved against the derivation relation",
    "lean/VE/Grammar/TableInvariant.lean": "parser invariants: proved",
    "lean/VE/Grammar/TableProofs.lean": "parser proofs",
    "lean/VE/EnglishGrammar/EngineExamples.lean": "fixtures",
    "lean/VE/EnglishGrammar/Examples.lean": "fixtures",
    "lean/VE/EnglishGrammar/FoldAgree.lean": "a theorem: foldChar agrees with the discourse fold",
    "lean/VE/EnglishGrammar/LexiconFixtures.lean": "generated fixtures",
    VERSION_TARGET: "generated from this lock file; it holds the version itself",
}
CLASSIFIED_DIRS = ("lean/VE/Grammar/", "lean/VE/EnglishGrammar/")

# The nonterminal catalogue of spec 2.4, in order, with the rank certificate (W3).
CATALOGUE = (
    ("sentence", 4), ("marker", 0), ("formula", 3), ("atom", 2), ("negation", 0), ("compact", 0),
    ("listing", 0), ("universal", 0), ("existential", 0), ("coordination", 2), ("guard", 4),
    ("guard_relative", 4), ("guard_atom", 3), ("relative_pronoun", 0), ("list_marker", 0), ("article", 0),
    ("declaration", 1), ("term", 1), ("noun", 0), ("label", 0), ("constant", 0), ("relative", 2),
    ("object_relative", 2), ("adjective", 0), ("natural", 1), ("natural_some", 0), ("some_tail", 3),
    ("copula_relative", 0), ("copula_adjective", 0), ("natural_no", 0), ("natural_every", 0),
    ("natural_tail", 3), ("natural_subject", 0), ("owner_clause", 0), ("reach", 0), ("count", 0),
    ("relation", 0),
)
NONTERMINAL = {name: i for i, (name, _) in enumerate(CATALOGUE)}
RANK = dict(CATALOGUE)

ORDINALS = ("first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth")
KINDS = ("and", "or", "implies")
BOOL = "bool"
# The actions of spec 2.7 (and 2.12's proposed ones) with the data each row carries: key -> allowed values.
ACTIONS: dict[str, dict[str, object]] = {
    "sentence": {"marked": BOOL}, "mark": {}, "unit": {}, "listMarker": {}, "through": {}, "nest": {},
    "not": {}, "and2": {}, "or2": {}, "implies2": {},
    "listWords": {"kind": KINDS}, "listMarkers": {"kind": KINDS},
    "guardAnd": {}, "guardLeft": {}, "guardRight": {}, "relAnd": {},
    "forallBody": {}, "forallGuardBody": {}, "forallRel": {}, "forallGuardRel": {},
    "existsBody": {}, "existsRel": {},
    "declThat": {}, "declOrdinal": {"ordinal": ORDINALS}, "declNamed": {},
    "termConst": {}, "termIt": {}, "termRef": {"prefix": ("that",) + tuple("the " + o for o in ORDINALS)},
    "termLabel": {}, "top": {}, "bottom": {}, "eq": {},
    "coordSubjects": {"kind": ("and", "or")}, "coordAdjectives": {"kind": ("and", "or")},
    "naturalTop": {}, "someDecl": {}, "copulaAnd": {}, "noDecl": {}, "everySubject": {}, "everyOwner": {},
    "reachNamed": {}, "reachBody": {"listed": BOOL}, "count": {"reflexive": BOOL},
    "orAdjectives": {}, "impliesAnd": {},
}
ROW_KEYS = {"tag", "lhs", "act", "rhs", "status"}
# Punctuation tokens of the lexer that a rule may name; the terminator `.` never occurs in a rule (W4).
PUNCTUATION = frozenset({",", ";", ":", "(", ")", "[", "]", "+", "-", "*", "(a)", "(b)", "(i)", "(ii)"})
WORD = re.compile(r"[a-z]+")
TAG = re.compile(r"[a-z0-9][a-z0-9.-]*")
LETTERS = re.compile(r"[A-Z]+")
VERSION = re.compile(r"[A-Za-z0-9][A-Za-z0-9.-]*")
SHA256 = re.compile(r"[0-9a-f]{64}")


class GrammarSourceError(ValueError):
    """A fixed-rule source, or the lock file, that the generator refuses."""


Read = Callable[[str], "bytes | None"]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _decode(data: bytes, what: str):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise GrammarSourceError(f"{what}: duplicate key {key!r}")
            out[key] = value
        return out

    def constant(name):
        raise GrammarSourceError(f"{what}: {name} is not JSON")

    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=unique, parse_constant=constant)
    except (UnicodeDecodeError, ValueError, RecursionError) as exc:
        if isinstance(exc, GrammarSourceError):
            raise
        raise GrammarSourceError(f"{what}: not JSON: {type(exc).__name__}") from None


# ------------------------------------------------------------------ the source

def _symbol(sym, where: str) -> object:
    if type(sym) is str:
        if not WORD.fullmatch(sym):
            raise GrammarSourceError(f"{where}: keyword {sym!r} is not one lower-case word")
        return sym
    if type(sym) is not dict or not sym:
        raise GrammarSourceError(f"{where}: a symbol is a word or an object, not {sym!r}")
    keys = set(sym)
    if keys == {"n"}:
        if type(sym["n"]) is not str or sym["n"] not in NONTERMINAL:
            raise GrammarSourceError(f"{where}: unknown nonterminal {sym['n']!r}")
    elif keys == {"c"}:
        if type(sym["c"]) is not str or not WORD.fullmatch(sym["c"]):
            raise GrammarSourceError(f"{where}: content {sym['c']!r} is not one lower-case word")
    elif "p" in keys and keys <= {"p", "before", "after"}:
        if type(sym["p"]) is not str or sym["p"] not in PUNCTUATION:
            raise GrammarSourceError(f"{where}: {sym['p']!r} is not a punctuation token a rule may name")
        for flag in ("before", "after"):
            if flag in sym and type(sym[flag]) is not bool:
                raise GrammarSourceError(f"{where}: the {flag} flag of {sym['p']!r} is not true or false")
    elif keys == {"q"}:
        if type(sym["q"]) is not str or not sym["q"] or not all(" " <= c <= "~" for c in sym["q"]):
            raise GrammarSourceError(f"{where}: quoted name {sym['q']!r} is not printable ASCII")
    elif keys == {"cls"} and sym["cls"] == "numeral":
        pass
    elif keys == {"cls", "letter"} and sym["cls"] == "label":
        if type(sym["letter"]) is not str or not LETTERS.fullmatch(sym["letter"]):
            raise GrammarSourceError(f"{where}: label letter {sym['letter']!r}")
    elif keys == {"kwMid"}:
        raise GrammarSourceError(f"{where}: kwMid occurs in no fixed row (spec 2.9); it is lexical")
    else:
        raise GrammarSourceError(f"{where}: unknown symbol {json.dumps(sym, sort_keys=True)}")
    return sym


def parse_source(data: bytes, what: str) -> list[dict]:
    """The rows of a fixed-rule source, checked; `GrammarSourceError` names the first fault."""
    rows = _decode(data, what)
    if type(rows) is not list or not rows:
        raise GrammarSourceError(f"{what}: the source is a non-empty array of rows")
    tags: set[str] = set()
    for k, row in enumerate(rows):
        where = f"{what}: row {k}"
        if type(row) is not dict:
            raise GrammarSourceError(f"{where}: a row is an object")
        tag = row.get("tag")
        if type(tag) is not str or not TAG.fullmatch(tag):
            raise GrammarSourceError(f"{where}: tag {tag!r}")
        where = f"{what}: rule {tag}"
        if tag in tags:
            raise GrammarSourceError(f"{where}: repeated tag")
        tags.add(tag)
        act = row.get("act")
        if type(act) is not str or act not in ACTIONS:
            raise GrammarSourceError(f"{where}: unknown action {act!r}")
        data_keys = ACTIONS[act]
        missing = ({"tag", "lhs", "act", "rhs"} | set(data_keys)) - set(row)
        extra = set(row) - ROW_KEYS - set(data_keys)
        if missing or extra:
            raise GrammarSourceError(f"{where}: fields missing {sorted(missing)}, unknown {sorted(extra)}")
        for key, allowed in data_keys.items():
            value = row[key]
            if allowed == BOOL:
                if type(value) is not bool:
                    raise GrammarSourceError(f"{where}: {act} {key} is not true or false")
            elif type(value) is not str or value not in allowed:
                raise GrammarSourceError(f"{where}: {act} {key} {value!r} is not one of {list(allowed)}")
        if "status" in row and row["status"] != "proposed":
            raise GrammarSourceError(f"{where}: status {row['status']!r} (only \"proposed\")")
        if type(row["lhs"]) is not str or row["lhs"] not in NONTERMINAL:
            raise GrammarSourceError(f"{where}: unknown nonterminal {row['lhs']!r}")
        rhs = row["rhs"]
        if type(rhs) is not list or not rhs:
            raise GrammarSourceError(f"{where}: the right-hand side is a non-empty list (W2)")
        for sym in rhs:
            _symbol(sym, where)
        first = rhs[0]
        if type(first) is dict and "n" in first and not RANK[first["n"]] < RANK[row["lhs"]]:
            raise GrammarSourceError(f"{where}: {first['n']} (rank {RANK[first['n']]}) begins a rule of "
                                     f"{row['lhs']} (rank {RANK[row['lhs']]}): not well-founded (W3)")
    return rows


def table_rows(rows: list[dict]) -> list[dict]:
    """The rows of the generated table: every row that is not `proposed`, in source order."""
    return [row for row in rows if row.get("status") != "proposed"]


def act_text(row: dict) -> str:
    """The `act` of the `english.grammar` export (spec 4.4): the action's name, then its data in the order of
    `ACTIONS`; a flag as `true`/`false`, a kind or an ordinal as the word, a prefix as a JSON string."""
    parts = [row["act"]]
    for key in ACTIONS[row["act"]]:
        value = row[key]
        if type(value) is bool:
            parts.append("true" if value else "false")
        elif key == "prefix":
            parts.append(json.dumps(value))
        else:
            parts.append(value)
    return " ".join(parts)


# ------------------------------------------------------------------ Lean rendering

def lean_string(s: str) -> str:
    if not all(" " <= c <= "~" for c in s):
        raise GrammarSourceError(f"{s!r} is not printable ASCII")
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def lean_symbol(sym) -> str:
    if type(sym) is str:
        return f".t (.kw {lean_string(sym)})"
    if "n" in sym:
        return f".n {NONTERMINAL[sym['n']]}"
    if "c" in sym:
        return f".t (.content {lean_string(sym['c'])})"
    if "p" in sym:
        before = "true" if sym.get("before", False) else "false"
        after = "true" if sym.get("after", False) else "false"
        return f".t (.exact (.punct {lean_string(sym['p'])} {before} {after}))"
    if "q" in sym:
        return f".t (.exact (.quoted {lean_string(sym['q'])}))"
    if sym["cls"] == "numeral":
        return ".t (.cls .numeral)"
    return f".t (.cls (.label {lean_string(sym['letter'])}))"


def lean_rule(row: dict, index: int) -> str:
    rhs = ", ".join(lean_symbol(s) for s in row["rhs"])
    return (f"{{ lhs := {NONTERMINAL[row['lhs']]}, rhs := [{rhs}], act := {index}, "
            f"tag := {lean_string(row['tag'])} }}")


def _lean_array(items: list[str], indent: str = "  ") -> list[str]:
    return [indent + item + ("," if k < len(items) - 1 else "") for k, item in enumerate(items)]


def render_table(profile: str, rows: list[dict], source_sha256: str) -> tuple[bytes, list[str | None]]:
    """The generated module of `profile` and, per line, the tag of the rule on it (None elsewhere)."""
    source, _, name = PROFILES[profile]
    table = table_rows(rows)
    lines: list[str] = [
        "import VE.EnglishGrammar.Token", "",
        f"/-! Generated by `python tools/english_grammar_gen.py --write` from `{source}`; do not edit.",
        f"The fixed rules of the profile `{profile}` (docs/spec/english-lean-s2.md 2.5, 2.9) as a table",
        "literal, the nonterminal catalogue of 2.4 with its ranks, and the action of each rule as the `act` text",
        "of the `english.grammar` export (4.4). Fixed rule `k` has `act := k`: `fixedActs` holds one action per",
        "fixed rule, in this order. Rows with `\"status\": \"proposed\"` are not in the table (2.12).",
        "`tools/english_grammar_gen.py --check` fails when this file differs from its source. -/", "",
        "namespace VE.EnglishGrammar.Fixed", "open VE.Grammar VE.EnglishGrammar", "",
        f"/-- The SHA-256 of `{source}`, which `grammar_id` covers (spec 2.10). -/",
        f"def {name}Sha256 : String := {lean_string(source_sha256)}", "",
        "/-- The nonterminal catalogue of spec 2.4: nonterminal `i` is the `i`-th name. -/",
        "def nonterminals : Array String := #[",
        *_lean_array([lean_string(n) for n, _ in CATALOGUE]), "]", "",
        "/-- The rank certificate of spec 2.4 (W3), one entry per nonterminal. -/",
        "def ranks : Array Nat := #[" + ", ".join(str(r) for _, r in CATALOGUE) + "]", "",
        "/-- The action of fixed rule `k`, as the `act` text of the `english.grammar` export (spec 4.4). -/",
        f"def {name}Acts : Array String := #[",
        *_lean_array([lean_string(act_text(row)) for row in table]), "]", "",
        f"def {name} : Array (Rule Terminal) := #[",
    ]
    tags: list[str | None] = [None] * len(lines)
    for line, row in zip(_lean_array([lean_rule(row, k) for k, row in enumerate(table)]), table):
        lines.append(line)
        tags.append(row["tag"])
    tail = ["]", "",
            f"#guard {name}.size == {len(table)}",
            f"#guard {name}Acts.size == {name}.size",
            f"#guard ({{ rules := {name}, start := 0, rank := ranks : Grammar Terminal }}).wf",
            f"#guard terminatorFree {{ rules := {name}, start := 0, rank := ranks }}", "",
            "end VE.EnglishGrammar.Fixed", ""]
    lines += tail
    tags += [None] * len(tail)
    return "\n".join(lines).encode(), tags


def render_version(version: str) -> bytes:
    return "\n".join([
        "/-! Generated by `python tools/english_grammar_gen.py --write` from `ve/english_grammar/LOCK.json`;",
        "do not edit. `actions_version` of base spec 2.12: raised on every change to a Lean file that holds a",
        "trusted definition of the English reader, which the lock file lists with their hashes. -/", "",
        "namespace VE.EnglishGrammar.Fixed", "",
        "def actionsVersion : String := " + lean_string(version), "",
        "end VE.EnglishGrammar.Fixed", ""]).encode()


# ------------------------------------------------------------------ the lock file

def hashed_files() -> list[str]:
    """Every file the lock hashes: the table sources, the generated tables, the trusted Lean files."""
    return sorted({p for source, target, _ in PROFILES.values() for p in (source, target)} | set(TRUSTED))


def parse_lock(data: bytes, what: str = LOCK) -> dict:
    lock = _decode(data, what)
    if type(lock) is not dict or set(lock) != {"format", "actions_version", "files"}:
        raise GrammarSourceError(f"{what}: fields are format, actions_version, files")
    if lock["format"] != LOCK_FORMAT:
        raise GrammarSourceError(f"{what}: format {lock['format']!r}, expected {LOCK_FORMAT}")
    if type(lock["actions_version"]) is not str or not VERSION.fullmatch(lock["actions_version"]):
        raise GrammarSourceError(f"{what}: actions_version {lock['actions_version']!r}")
    files = lock["files"]
    if type(files) is not dict or not all(type(v) is str and SHA256.fullmatch(v) for v in files.values()):
        raise GrammarSourceError(f"{what}: files maps each path to a SHA-256")
    return lock


def render_lock(version: str, hashes: dict[str, str]) -> bytes:
    return (json.dumps({"format": LOCK_FORMAT, "actions_version": version, "files": dict(sorted(hashes.items()))},
                       indent=1) + "\n").encode()


# ------------------------------------------------------------------ checks

def _drift(profile: str, rows: list[dict], expected: bytes, tags: list[str | None], actual: bytes) -> str:
    target = PROFILES[profile][1]
    text = actual.decode("utf-8", "replace")
    for row in rows:
        if row.get("status") == "proposed" and f"tag := {lean_string(row['tag'])}" in text:
            return f"{profile}: proposed row {row['tag']} is in the generated table {target}"
    want = expected.decode().split("\n")
    got = text.split("\n")
    for k, line in enumerate(want):
        if k >= len(got) or got[k] != line:
            where = f"rule {tags[k]}" if tags[k] else f"line {k + 1} (outside the rules)"
            return f"{profile}: {target} differs from its source at {where}; run --write"
    return f"{profile}: {target} has lines after the generated text; run --write"


def check(read: Read, listing: Callable[[], Iterable[str]], base_lock: bytes | None = None) -> list[str]:
    """Every fault of the generated tables and the lock file, as messages; empty when all agree."""
    errors: list[str] = []
    lock_blob = read(LOCK)
    if lock_blob is None:
        return [f"{LOCK}: missing; run --write --actions-version V"]
    try:
        lock = parse_lock(lock_blob)
    except GrammarSourceError as exc:
        return [str(exc)]
    for profile, (source, target, _) in PROFILES.items():
        data = read(source)
        if data is None:
            errors.append(f"{profile}: source {source} is missing")
            continue
        try:
            rows = parse_source(data, source)
        except GrammarSourceError as exc:
            errors.append(f"{profile}: {exc}")
            continue
        expected, tags = render_table(profile, rows, sha256(data))
        actual = read(target)
        if actual is None:
            errors.append(f"{profile}: generated table {target} is missing; run --write")
        elif actual != expected:
            errors.append(_drift(profile, rows, expected, tags, actual))
    version_file = read(VERSION_TARGET)
    if version_file != render_version(lock["actions_version"]):
        errors.append(f"{VERSION_TARGET}: does not hold actions_version {lock['actions_version']!r} of {LOCK}; "
                      "run --write")
    wanted = hashed_files()
    if sorted(lock["files"]) != wanted:
        errors.append(f"{LOCK}: hashes {sorted(lock['files'])}, expected {wanted}; run --write")
    now: dict[str, str | None] = {}
    for path in sorted(set(wanted) | set(lock["files"])):
        blob = read(path)
        now[path] = None if blob is None else sha256(blob)
        recorded = lock["files"].get(path)
        if blob is None:
            errors.append(f"{path}: hashed by {LOCK} but missing")
        elif recorded is not None and recorded != now[path]:
            errors.append(f"{path}: SHA-256 {recorded} in {LOCK}, {now[path]} now; raise actions_version "
                          "and run --write")
    classified = set(TRUSTED) | set(UNTRUSTED) | {target for _, target, _ in PROFILES.values()}
    for path in sorted(listing()):
        if path.startswith(CLASSIFIED_DIRS) and path.endswith(".lean") and path not in classified:
            errors.append(f"{path}: neither a trusted file of {LOCK} nor listed as untrusted in "
                          "tools/english_grammar_gen.py; classify it")
    if base_lock is not None:
        try:
            base = parse_lock(base_lock, f"{LOCK} at the base")
        except GrammarSourceError as exc:
            errors.append(str(exc))
            return errors
        if base["actions_version"] == lock["actions_version"]:
            for path in sorted(set(base["files"]) | set(now)):
                before, after = base["files"].get(path), now.get(path)
                if before != after:
                    errors.append(f"{path}: SHA-256 {before or 'absent'} at the base, {after or 'absent'} now, "
                                  f"with actions_version {lock['actions_version']!r} unchanged; raise it")
    return errors


# ------------------------------------------------------------------ the command

def file_reader(root: Path) -> Read:
    def read(path: str) -> bytes | None:
        target = root / path
        return target.read_bytes() if target.is_file() else None
    return read


def file_listing(root: Path) -> Callable[[], list[str]]:
    def listing() -> list[str]:
        return [str(PurePosixPath(p.relative_to(root))) for d in CLASSIFIED_DIRS
                for p in (root / d).rglob("*.lean")]
    return listing


def write(root: Path, actions_version: str | None = None) -> list[str]:
    """Regenerate the tables, the version module and the lock; the paths written. A changed hash needs a new
    `actions_version`, which must differ from the lock's."""
    read = file_reader(root)
    old_blob = read(LOCK)
    old = parse_lock(old_blob) if old_blob is not None else None
    if actions_version is not None and not VERSION.fullmatch(actions_version):
        raise GrammarSourceError(f"actions_version {actions_version!r}")
    if old is None and actions_version is None:
        raise GrammarSourceError(f"{LOCK} does not exist yet: give --actions-version")
    outputs: dict[str, bytes] = {}
    for profile, (source, target, _) in PROFILES.items():
        data = read(source)
        if data is None:
            raise GrammarSourceError(f"{profile}: source {source} is missing")
        outputs[target] = render_table(profile, parse_source(data, source), sha256(data))[0]
    hashes = {}
    for path in hashed_files():
        blob = outputs.get(path, read(path))
        if blob is None:
            raise GrammarSourceError(f"{path}: hashed by the lock but missing")
        hashes[path] = sha256(blob)
    version = actions_version or old["actions_version"]
    if old is not None and hashes != old["files"] and version == old["actions_version"]:
        changed = sorted(p for p in set(hashes) | set(old["files"]) if hashes.get(p) != old["files"].get(p))
        raise GrammarSourceError(f"{', '.join(changed)} changed: give a new --actions-version "
                                 f"(now {old['actions_version']!r})")
    outputs[VERSION_TARGET] = render_version(version)
    outputs[LOCK] = render_lock(version, hashes)
    written = []
    for path, blob in outputs.items():
        target = root / path
        if read(path) != blob:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(blob)
            written.append(path)
    return written


def git_blob(root: Path, ref: str, path: str) -> bytes | None:
    done = subprocess.run(["git", "cat-file", "blob", f"{ref}:{path}"], cwd=root, capture_output=True,
                          check=False)
    return done.stdout if done.returncode == 0 else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="fail on drift between sources, tables and lock")
    mode.add_argument("--write", action="store_true", help="regenerate the tables, the version and the lock")
    parser.add_argument("--actions-version", help="the new actions_version (with --write)")
    parser.add_argument("--base", help="a git revision whose lock the version check compares against")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    try:
        if args.write:
            for path in write(args.root, args.actions_version):
                print(path)
            return 0
        base = git_blob(args.root, args.base, LOCK) if args.base else None
        errors = check(file_reader(args.root), file_listing(args.root), base)
    except GrammarSourceError as exc:
        print(f"english_grammar_gen: {exc}", file=sys.stderr)
        return 1
    for error in errors:
        print(f"english_grammar_gen: {error}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
