"""Fail on a new identity preimage built in Python (architecture plan AR-6, rule 4 of the relay lint; DRI D7).

An identity is a digest under a domain separator, `digest("ve-<domain>\\n", payload)`. Lean owns the meaning,
environment, source, document, report and document-hash domains (D7); Python reads those identities from Lean's
answers. Python owns only its app records (`PYTHON_RECORDS`). Two rules, read with Python's own parser:

1. In a relayed module (`tools/relay_lint.py`: `RELAYED`, its `helpers` and the functions of `RELAYED_FUNCTIONS`),
   no string expression starts with a Lean-owned prefix (`LEAN_PREFIXES`), so no relayed module builds a Lean-owned
   preimage, whatever the hash call (`digest`, `soft_digest`, `hashlib.sha256`) and wherever the text is kept.
   `ve-document@` counts only in domain form (`ve-document@2\\n`); a bare format name is not a preimage.
2. In every `ve/` module, no domain literal: a string expression whose text starts `ve-`, then no whitespace, then a
   newline (the separator form every domain has).

A string expression is a literal, an f-string, a `+` of them or their `.encode()`; each computed part reads as `{}`,
so `(f"ve-source-{v}\\n" + text).encode()` reads `ve-source-{}\\n{}`. A docstring is not one.

Today's sites are listed in `ALLOWLIST`, keyed by module, enclosing scope and domain, one entry per site. A
Lean-owned entry names the batch that removes it (`REMOVERS`); a Python-owned entry names its record (D7). A site
without an entry fails, and so does an entry without its site (stale). With `--base REV` the Lean-owned sites of a
module may not grow against the allowlist at REV (per domain; a site moved to another function of its module is not
growth): the list only shrinks. A revision without the allowlist has no ratchet yet. `--prune` deletes stale
entries and adds none.

Collision rule (merge train): "conflict in `tools/identity-sites.json`: take `main`'s file, run
`python3 tools/identity_lint.py --prune`; a site that moved to another function updates its entry's `scope`".

Usage: ``python tools/identity_lint.py [--base REV] [--prune] [--json] [PATH ...]`` (default: every `ve/` module;
given paths, each is read as a relayed module with an empty allowlist). Exit 1 on a finding.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import relay_lint  # noqa: E402  (one owner of the relayed list)

ALLOWLIST = ROOT / "tools/identity-sites.json"
ALLOWLIST_NAME = "tools/identity-sites.json"
# The Lean-owned domain prefixes of rule 1 (architecture plan AR-6).
LEAN_PREFIXES = ("ve-meaning-", "ve-environment-", "ve-source-", "ve-report-", "ve-document@", "ve-rights-",
                 "ve-soft-norms-", "ve-norms-", "ve-situation-", "ve-model-")
# The records Python owns (D7).
PYTHON_RECORDS = ("assist", "adapters", "proposals", "argument package", "checker build")
# The batches that remove a Lean-owned site (architecture plan AR-6 and AR-15).
REMOVERS = ("AR-15", "lf-16g", "RD-7")
HOLE = "{}"
DOMAIN = re.compile(r"ve-\S*\n")


@dataclass(frozen=True)
class Site:
    path: str
    scope: str
    domain: str
    line: int
    relayed: bool

    @property
    def key(self) -> tuple[str, str, str]:
        return self.path, self.scope, self.domain


def text(node: ast.AST) -> str | None:
    """The text of a string expression with each computed part as `HOLE`, or None when `node` is not one."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (str, bytes)):
        return node.value if isinstance(node.value, str) else node.value.decode("latin-1")
    if isinstance(node, ast.JoinedStr):
        return "".join(part.value if isinstance(part, ast.Constant) else HOLE for part in node.values)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left, right = text(node.left), text(node.right)
        if left is None and right is None:
            return None
        return (HOLE if left is None else left) + (HOLE if right is None else right)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "encode":
        return text(node.func.value)
    return None


def _parts(node: ast.AST) -> list[ast.AST]:
    """The sub-expressions whose text `text(node)` already reads."""
    if isinstance(node, ast.JoinedStr):
        return list(node.values)
    if isinstance(node, ast.BinOp):
        return [node.left, node.right]
    if isinstance(node, ast.Call):
        return [node.func.value]
    return []


def _scoped(tree: ast.Module):
    """Every node with the dotted name of its enclosing functions and classes (`<module>` at the top)."""
    todo: list[tuple[ast.AST, tuple[str, ...]]] = [(tree, ())]
    while todo:
        node, scope = todo.pop()
        yield node, ".".join(scope) or "<module>"
        inner = scope + (node.name,) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) \
            else scope
        todo.extend((child, inner) for child in ast.iter_child_nodes(node))


def domain_of(value: str, relayed: bool) -> str | None:
    """The domain a string expression builds, or None: its domain form, or under rule 1 its Lean-owned prefix
    up to the first whitespace."""
    form = DOMAIN.match(value)
    if form:
        return form.group()
    if relayed and value.startswith(LEAN_PREFIXES) and not value.startswith("ve-document@"):
        return value.split(maxsplit=1)[0] if value.strip() else value
    return None


def sites(path: Path, relayed: bool | tuple[str, ...] = False) -> list[Site]:
    """The identity sites of a module; `relayed` is True for a relayed module or the names of its relayed top-level
    functions."""
    tree = ast.parse(path.read_text(), filename=str(path))
    where = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)
    docstrings = {id(node.value) for node in ast.walk(tree) if isinstance(node, ast.Expr)}
    inner = {id(part) for node in ast.walk(tree) if text(node) is not None for part in _parts(node)}
    out = []
    for node, scope in _scoped(tree):
        if id(node) in inner or id(node) in docstrings:
            continue
        value = text(node)
        if value is None:
            continue
        in_relay = relayed is True or (bool(relayed) and scope.split(".", 1)[0] in relayed)
        domain = domain_of(value, in_relay)
        if domain is not None:
            out.append(Site(where, scope, domain, node.lineno,
                            in_relay and domain.startswith(LEAN_PREFIXES)))
    return sorted(out, key=lambda site: (site.path, site.line, site.domain))


def relayed_scopes() -> dict[str, bool | tuple[str, ...]]:
    """The relayed modules and functions, as `tools/relay_lint.py` names them."""
    modules = [ROOT / path for path in relay_lint.RELAYED]
    scopes: dict[str, bool | tuple[str, ...]] = {}
    for path in modules + relay_lint.helpers([p for p in modules if p.is_file()]):
        scopes[path.relative_to(ROOT).as_posix()] = True
    for name, functions in relay_lint.RELAYED_FUNCTIONS.items():
        scopes.setdefault(name, tuple(functions))
    return scopes


def tree_sites() -> list[Site]:
    """Every identity site of the `ve/` package."""
    scopes = relayed_scopes()
    found = []
    for path in sorted((ROOT / "ve").rglob("*.py")):
        found += sites(path, scopes.get(path.relative_to(ROOT).as_posix(), False))
    return found


ENTRY_KEYS = {"lean": {"path", "scope", "domain", "owner", "removed_by"},
              "python": {"path", "scope", "domain", "owner", "record"}}


def entry_problems(entries: object) -> list[str]:
    """The allowlist's shape: a list of entries, each Lean-owned with its remover or Python-owned with its D7
    record."""
    if type(entries) is not list:
        return [f"{ALLOWLIST_NAME}: not a list"]
    out = []
    for n, entry in enumerate(entries):
        owner = entry.get("owner") if type(entry) is dict else None
        if owner not in ENTRY_KEYS or set(entry) != ENTRY_KEYS[owner] or \
                not all(type(v) is str and v for v in entry.values()):
            out.append(f"{ALLOWLIST_NAME}[{n}]: not an entry {sorted(ENTRY_KEYS['lean'])} or "
                       f"{sorted(ENTRY_KEYS['python'])} of non-empty strings")
        elif owner == "lean" and entry["removed_by"] not in REMOVERS:
            out.append(f"{ALLOWLIST_NAME}[{n}]: removed_by {entry['removed_by']!r} is not one of {REMOVERS}")
        elif owner == "python" and entry["record"] not in PYTHON_RECORDS:
            out.append(f"{ALLOWLIST_NAME}[{n}]: record {entry['record']!r} is not a Python record of D7")
        elif owner == "python" and entry["domain"].startswith(LEAN_PREFIXES):
            out.append(f"{ALLOWLIST_NAME}[{n}]: {entry['domain']!r} is a Lean-owned domain")
    return out


def _key(entry: dict) -> tuple[str, str, str]:
    return entry["path"], entry["scope"], entry["domain"]


def problems(found: list[Site], entries: list[dict]) -> list[str]:
    """The sites without an allowlist entry and the entries without their site (counted per key)."""
    shape = entry_problems(entries)
    if shape:
        return shape
    allowed = Counter(_key(e) for e in entries)
    present = Counter(site.key for site in found)
    out = []
    for site in found:
        if allowed[site.key] > 0:
            allowed[site.key] -= 1
            continue
        rule = "a relayed module builds the Lean-owned identity preimage" if site.relayed else \
            "a ve- domain literal outside the allowlist:"
        out.append(f"{site.path}:{site.line}: {rule} {site.domain!r} (in {site.scope})")
    for (path, scope, domain), extra in sorted(allowed.items()):
        if extra > 0:
            out.append(f"{ALLOWLIST_NAME}: stale entry {path} {scope} {domain!r}: {extra} site(s) gone "
                       f"({present[(path, scope, domain)]} left)")
    return out


def growth(base: list[dict], head: list[dict]) -> list[str]:
    """The Lean-owned sites of `head` beyond those of `base`, per module and domain (a site moved to another
    function of its module is not growth): the allowlist only shrinks."""
    def lean(entries):
        return Counter((e["path"], e["domain"]) for e in entries if type(e) is dict and e.get("owner") == "lean")
    return [f"{ALLOWLIST_NAME}: Lean-owned site {path} {domain!r} added since the base"
            for (path, domain), n in sorted((lean(head) - lean(base)).items()) for _ in range(n)]


def base_entries(rev: str) -> list[dict] | None:
    """The allowlist at `rev`, or None when `rev` has none (the ratchet starts at the commit that adds it). A bad
    revision fails."""
    subprocess.run(["git", "rev-parse", "--verify", f"{rev}^{{commit}}"], cwd=ROOT, check=True,
                   capture_output=True)
    if subprocess.run(["git", "cat-file", "-e", f"{rev}:{ALLOWLIST_NAME}"], cwd=ROOT,
                      capture_output=True).returncode != 0:
        return None
    return json.loads(subprocess.run(["git", "show", f"{rev}:{ALLOWLIST_NAME}"], cwd=ROOT, check=True,
                                     capture_output=True, text=True).stdout)


def prune(found: list[Site], entries: list[dict]) -> list[dict]:
    """`entries` without the stale ones; nothing is added."""
    present = Counter(site.key for site in found)
    kept = []
    for entry in entries:
        if present[_key(entry)] > 0:
            present[_key(entry)] -= 1
            kept.append(entry)
    return kept


def census(found: list[Site], entries: list[dict]) -> dict:
    """The counts the batch report states, from the tree and the allowlist."""
    lean = [e for e in entries if e["owner"] == "lean"]
    return {"sites": len(found), "modules": len({site.path for site in found}),
            "relayed_sites": sum(site.relayed for site in found),
            "lean_owned": len(lean), "python_owned": len(entries) - len(lean),
            "lean_modules": len({e["path"] for e in lean}),
            "by_remover": dict(sorted(Counter(e["removed_by"] for e in lean).items())),
            "by_record": dict(sorted(Counter(e["record"] for e in entries if e["owner"] == "python").items())),
            "by_domain": dict(sorted(Counter(site.domain for site in found).items()))}


def write(entries: list[dict]) -> None:
    """One entry per line, so that two branches removing different sites merge without a conflict."""
    ALLOWLIST.write_text("[\n" + ",\n".join(json.dumps(e, ensure_ascii=False) for e in entries) + "\n]\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--base", help="fail when a Lean-owned site was added since this revision")
    parser.add_argument("--prune", action="store_true", help="delete stale entries from the allowlist")
    parser.add_argument("--json", action="store_true", help="print the census as JSON")
    args = parser.parse_args(argv)
    if args.paths:
        missing = [p for p in args.paths if not Path(p).is_file()]
        if missing:
            print("\n".join(f"module not found: {p}" for p in missing))
            return 1
        found = [site for p in args.paths for site in sites(Path(p).resolve(), True)]
        entries: list[dict] = []
    else:
        found = tree_sites()
        entries = json.loads(ALLOWLIST.read_text())
        if args.prune and not entry_problems(entries):
            entries = prune(found, entries)
            write(entries)
    out = problems(found, entries)
    base = base_entries(args.base) if args.base is not None and not out else None
    if base is not None:
        out = growth(base, entries)
    if out:
        print("\n".join(out))
        return 1
    numbers = census(found, entries)
    if args.json:
        print(json.dumps(numbers, indent=1, sort_keys=True))
    else:
        print(f"PASS: {numbers['sites']} identity site(s) in {numbers['modules']} module(s), each allowlisted: "
              f"{numbers['lean_owned']} Lean-owned {numbers['by_remover']}, {numbers['python_owned']} "
              f"Python-owned records; {numbers['relayed_sites']} in relayed modules")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
