"""The tests whose result can depend on git history: `tests/history-dependent.json` and its lint.

A test reads history when it starts git or reads a `.git` directory or file: its result can then change when
commits, refs or the object store change, with every tracked file the same. Such a result binds the commit it
ran on and is never carried to another commit (docs/test-architecture/histdep/REPORT.md says where each
record binds it). The list is an inventory and a lint only: no gate, merge or nightly run skips or reuses a
test because of it.

Where the list comes from, two inputs, no hand edits:

* `tests/history-map.json`, saved from the coverage map the selector uses (`tools/test_map.py`) by
  `history_tests.py save-map`: each test unit the map records starting git, and each function the unit ran
  that starts git or reads `.git` in the source (`sites`), so a read the map's recorder cannot see (it skips
  `.git`, tools/test_map_recorder.py) is still found through the function that does it.
* the source of each test unit itself, scanned now (`own_sites`): a new test that starts git is found
  before any map has recorded it.

`--write` writes the list from both; `--check` is the lint. It fails when a unit that starts git or reads
`.git` is not listed (`missing`), when an entry differs from what `--write` gives (`changed`), or when the
file is malformed; it reports, without failing, an entry whose unit no longer reads history (`stale`: the
unit is gone, or none of the functions that made it read history still does). `tests/test_history_tests.py`
runs the lint on the tree, so it fails in the gate. The lint reads the two inputs and Python sources only:
it starts no git itself.

A site is found by the shape of the code (`sites`): a list or tuple whose first element is the string "git"
(an argument vector), a process call whose command string starts with "git", or a path made from ".git".
The map then says which units ran each site's function; a unit's own file counts whatever ran.
"""
from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
LIST = "tests/history-dependent.json"
MAP_EXTRACT = "tests/history-map.json"
FORMAT = "ve-history-tests@1"
MAP_FORMAT = "ve-history-map@1"
START, READ = "starts git", "reads .git"
# Calls that start a process from a command whose first word is the program.
PROCESS_CALLS = frozenset({"run", "Popen", "check_output", "check_call", "call", "system", "popen", "getoutput",
                           "getstatusoutput", "create_subprocess_exec", "create_subprocess_shell", "spawnlp",
                           "spawnvp", "execlp", "execvp", "execvpe", "posix_spawn", "posix_spawnp"})
# String methods that compare or split a name: a ".git" handed to one is matched, not opened.
NAME_METHODS = frozenset({"startswith", "endswith", "split", "rsplit", "partition", "rpartition", "replace",
                          "index", "find", "rfind", "count", "removeprefix", "removesuffix", "strip"})
# Options git takes before its subcommand that have a separate value.
GIT_VALUE_OPTIONS = frozenset({"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path",
                               "--config-env"})


@dataclass(frozen=True, order=True)
class Site:
    """Code that starts git (`kind` START, with its subcommand when the source names it) or reads `.git`."""
    file: str
    qualname: str
    kind: str
    line: int
    command: str = ""

    def text(self) -> str:
        what = f"git {self.command}" if self.kind == START and self.command else (
            "git" if self.kind == START else ".git")
        return f"{self.file}:{self.qualname} ({what}, line {self.line})"


def _string(node) -> str | None:
    """The text of a string constant, or the literal start of an f-string."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr) and node.values and isinstance(node.values[0], ast.Constant) \
            and isinstance(node.values[0].value, str):
        return node.values[0].value
    return None


def _subcommand(arguments) -> str:
    """The git subcommand an argument vector names after its options, or "" when the source does not say."""
    skip = False
    for node in arguments:
        if skip:
            skip = False
            continue
        text = _string(node)
        if text is None or not isinstance(node, ast.Constant):
            return ""
        if text.startswith("-"):
            skip = text in GIT_VALUE_OPTIONS
            continue
        return text
    return ""


def _callee(call: ast.Call) -> str:
    return call.func.attr if isinstance(call.func, ast.Attribute) else (
        call.func.id if isinstance(call.func, ast.Name) else "")


def _names_git_path(text: str) -> bool:
    return text == ".git" or text.startswith(".git/") or "/.git/" in text or text.endswith("/.git")


class _Scanner(ast.NodeVisitor):
    """Each site of one file, under the qualified name of the code object that runs it (`co_qualname`)."""

    def __init__(self, file: str, tree: ast.Module):
        self.file = file
        self.scope = ["<module>"]
        self.prefix = [""]
        self.parents: list[ast.AST] = []
        self.found: set[Site] = set()
        # A module's or class's named argument vector (`GIT = ("git", "-c", ...)`) starts nothing where it is
        # bound: the code that uses the name does.
        self.vectors: dict[str, ast.AST] = {}
        for body in [tree.body, *(node.body for node in tree.body if isinstance(node, ast.ClassDef))]:
            for statement in body:
                if isinstance(statement, (ast.Assign, ast.AnnAssign)) and self._vector(statement.value):
                    targets = statement.targets if isinstance(statement, ast.Assign) else [statement.target]
                    if all(isinstance(target, ast.Name) for target in targets):
                        self.vectors.update((target.id, statement.value) for target in targets)
        self.bound = {id(node) for node in self.vectors.values()}

    def _add(self, kind: str, node: ast.AST, command: str = "") -> None:
        self.found.add(Site(self.file, self.scope[-1], kind, node.lineno, command))

    def _enter(self, name: str, node: ast.AST, inner: str) -> None:
        qualname = self.prefix[-1] + name
        self.scope.append(qualname)
        self.prefix.append(qualname + inner)
        self.parents.append(node)

    def _leave(self) -> None:
        self.scope.pop()
        self.prefix.pop()
        self.parents.pop()

    def _outer(self, nodes) -> None:
        for node in nodes:
            if node is not None:
                self.visit(node)

    def visit_FunctionDef(self, node) -> None:
        # Decorators, defaults and annotations run in the enclosing code object.
        self._outer([*node.decorator_list, *node.args.defaults, *node.args.kw_defaults])
        self._enter(node.name, node, ".<locals>.")
        for statement in node.body:
            self.visit(statement)
        self._leave()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node) -> None:
        self._outer([*node.decorator_list, *node.bases, *node.keywords])
        self._enter(node.name, node, ".")
        for statement in node.body:
            self.visit(statement)
        self._leave()

    def visit_Lambda(self, node) -> None:
        self._outer([*node.args.defaults, *node.args.kw_defaults])
        self._enter("<lambda>", node, ".<locals>.")
        self.visit(node.body)
        self._leave()

    def visit_GeneratorExp(self, node) -> None:
        # The first iterable is evaluated outside; list, set and dict comprehensions are inlined (PEP 709).
        self.visit(node.generators[0].iter)
        self._enter("<genexpr>", node, ".<locals>.")
        self.visit(node.elt)
        for number, generator in enumerate(node.generators):
            if number:
                self.visit(generator.iter)
            self.visit(generator.target)
            for condition in generator.ifs:
                self.visit(condition)
        self._leave()

    def generic_visit(self, node) -> None:
        self.parents.append(node)
        super().generic_visit(node)
        self.parents.pop()

    def visit_List(self, node) -> None:
        self._argument_vector(node)
        self.generic_visit(node)

    visit_Tuple = visit_List

    def visit_Call(self, node) -> None:
        if node.args and _callee(node) in PROCESS_CALLS:
            text = _string(node.args[0])
            if text is not None and (text == "git" or text.startswith("git ")):
                words = text.split()
                self._add(START, node, words[1] if len(words) > 1 and isinstance(node.args[0], ast.Constant)
                          and not words[1].startswith("-") else "")
        self.generic_visit(node)

    def visit_Constant(self, node) -> None:
        if isinstance(node.value, str) and _names_git_path(node.value) and self._opened(node):
            self._add(READ, node)

    def visit_Name(self, node) -> None:
        if isinstance(node.ctx, ast.Load) and node.id in self.vectors:
            vector = self.vectors[node.id]
            arguments = vector.elts[1:]
            parent = self.parents[-1] if self.parents else None
            if isinstance(parent, ast.Starred) and len(self.parents) > 1 and \
                    isinstance(self.parents[-2], (ast.List, ast.Tuple)):
                elements = self.parents[-2].elts
                arguments = [*arguments, *elements[[e is parent for e in elements].index(True) + 1:]]
            self._add(START, node, _subcommand(arguments))

    @staticmethod
    def _vector(node) -> bool:
        return isinstance(node, (ast.List, ast.Tuple)) and bool(node.elts) \
            and isinstance(node.elts[0], ast.Constant) and node.elts[0].value == "git"

    def _argument_vector(self, node) -> None:
        if self._vector(node) and id(node) not in self.bound:
            self._add(START, node, _subcommand(node.elts[1:]))

    def _opened(self, node) -> bool:
        """Whether a ".git" string is used as a path: joined to another path, handed to a call or named,
        but not compared, not one name in a list of names and not handed to a string method that matches
        names. A path with a separator in it (".git/HEAD") counts wherever else it stands."""
        child = node
        for parent in reversed(self.parents):
            if isinstance(parent, ast.Compare):
                return False
            if isinstance(parent, (ast.Tuple, ast.List, ast.Set)):
                if child is node and len(parent.elts) > 1:
                    return False
            elif isinstance(parent, ast.Call):
                return not (_callee(parent) in NAME_METHODS and child is not parent.func)
            elif isinstance(parent, (ast.Assign, ast.AnnAssign, ast.NamedExpr)):
                return True
            elif not isinstance(parent, (ast.BinOp, ast.keyword)):
                return child is not node or "/" in node.value
            child = parent
        return True


def sites(file: str, root: Path = ROOT) -> set[Site]:
    """Every site in one Python file (root-relative); none when it is missing or does not parse."""
    try:
        tree = ast.parse((root / file).read_text(encoding="utf-8"), file)
    except (OSError, SyntaxError, UnicodeDecodeError, ValueError):
        return set()
    scanner = _Scanner(file, tree)
    scanner.visit(tree)
    return scanner.found


def _test_map():
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        import test_map
    finally:
        sys.path.remove(str(ROOT / "tools"))
    return test_map


def units(root: Path = ROOT) -> list[str]:
    """The test units, as the coverage map names them (tools/test_map.py)."""
    return _test_map().units(root)


class _Sources:
    """The sites of each file, scanned once."""

    def __init__(self, root: Path):
        self.root = root
        self.scanned: dict[str, set[Site]] = {}

    def of(self, file: str) -> set[Site]:
        if file not in self.scanned:
            self.scanned[file] = sites(file, self.root)
        return self.scanned[file]

    def at(self, file: str, qualname: str) -> set[Site]:
        return {site for site in self.of(file) if site.qualname == qualname}


def extract(data: dict, root: Path = ROOT) -> dict:
    """The part of a coverage map (`tools/test_map.py` `load`) the list is derived from: each unit that started
    git, with the functions it ran that start git in the source, and each unit that ran a function that reads
    `.git`, which the map's recorder does not record. A function that starts git counts only for a unit the map
    saw start git (it may not have reached the call); a `.git` read has no such record, so running the function
    counts."""
    sources = _Sources(root)
    tests = data["tests"]
    started = {tests[i] for i in data["programs"].get("git", ())}
    found: dict[str, set[str]] = {}
    for file, qualnames in data["functions"].items():
        for qualname, indices in qualnames.items():
            kinds = {site.kind for site in sources.at(file, qualname)}
            for i in indices:
                if READ in kinds or START in kinds and tests[i] in started:
                    found.setdefault(tests[i], set()).add(f"{file}:{qualname}")
    return {"format": MAP_FORMAT,
            "map": {"commit": data["commit"], "version": data["version"], "created": data["created"],
                    "tests": len(tests)},
            "units": {unit: {"git": unit in started, "sites": sorted(found.get(unit, ()))}
                      for unit in sorted(started | set(found))}}


def _why(found: set[Site], recorded_without_site: bool) -> str:
    parts = []
    starts = sorted(site for site in found if site.kind == START)
    if starts:
        commands = sorted({f"git {site.command}" for site in starts if site.command})
        parts.append("starts git" + (f" ({', '.join(commands)})" if commands else "") + " in "
                     + ", ".join(sorted({site.file for site in starts})))
    reads = sorted(site for site in found if site.kind == READ)
    if reads:
        parts.append("reads .git in " + ", ".join(sorted({site.file for site in reads})))
    if recorded_without_site:
        parts.append("the coverage map records it starting git from code with no site in the tree's Python")
    return "; ".join(parts)


def _via(found: set[Site]) -> list[str]:
    by_function: dict[tuple[str, str], set[str]] = {}
    for site in found:
        what = (f"git {site.command}" if site.command else "git") if site.kind == START else ".git"
        by_function.setdefault((site.file, site.qualname), set()).add(what)
    return [f"{file}:{qualname}: {', '.join(sorted(whats))}" for (file, qualname), whats in sorted(by_function.items())]


def generate(saved: dict, root: Path = ROOT) -> dict:
    """The list: each unit whose own source has a site, or that ran a function of `saved` (the map extract) that
    still has one, or that the map saw start git from code with no site at all."""
    sources = _Sources(root)
    present = units(root)
    rows = []
    for unit in present:
        record = saved["units"].get(unit, {"git": False, "sites": []})
        carried = set().union(*(sources.at(*site.split(":", 1)) for site in record["sites"]))
        own = sources.of(unit)
        unexplained = record["git"] and not record["sites"]
        if not (carried or own or unexplained):
            continue
        recorded = (["coverage map"] if carried or unexplained else []) + (["source"] if own else [])
        rows.append({"test": unit, "why": _why(carried | own, unexplained), "recorded": recorded,
                     "via": _via(carried | own)})
    return {"format": FORMAT, "map": saved["map"], "tests": rows}


def validate_extract(data) -> list[str]:
    errors = []
    if not isinstance(data, dict) or data.get("format") != MAP_FORMAT:
        return [f"{MAP_EXTRACT}: format is not {MAP_FORMAT}"]
    header = data.get("map")
    if not isinstance(header, dict) or not isinstance(header.get("commit"), str) \
            or type(header.get("version")) is not int or not isinstance(header.get("created"), str) \
            or type(header.get("tests")) is not int:
        errors.append(f"{MAP_EXTRACT}: map is not {{commit, version, created, tests}}")
    records = data.get("units")
    if not isinstance(records, dict):
        return errors + [f"{MAP_EXTRACT}: units is not an object"]
    for unit, record in records.items():
        if not isinstance(record, dict) or set(record) != {"git", "sites"} or type(record["git"]) is not bool \
                or not isinstance(record["sites"], list) or not all(
                    isinstance(site, str) and ":" in site for site in record["sites"]) \
                or not (record["git"] or record["sites"]):
            errors.append(f"{MAP_EXTRACT}: {unit}: not {{git: bool, sites: [\"file:qualname\", ...]}} with "
                          "git or a site")
    return errors


def validate_list(data) -> list[str]:
    if not isinstance(data, dict) or data.get("format") != FORMAT or set(data) != {"format", "map", "tests"}:
        return [f"{LIST}: not {{format: {FORMAT}, map, tests}}"]
    rows = data["tests"]
    if not isinstance(rows, list):
        return [f"{LIST}: tests is not a list"]
    errors = []
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"test", "why", "recorded", "via"} \
                or not isinstance(row["test"], str) or not isinstance(row["why"], str) or not row["why"] \
                or not isinstance(row["recorded"], list) or not row["recorded"] \
                or not set(row["recorded"]) <= {"coverage map", "source"} \
                or not isinstance(row["via"], list) or not all(isinstance(item, str) for item in row["via"]):
            errors.append(f"{LIST}: an entry is not {{test, why, recorded, via}} with a reason: {row!r:.200}")
    names = [row.get("test") for row in rows if isinstance(row, dict)]
    if len(set(names)) != len(names):
        errors.append(f"{LIST}: a test is listed twice")
    return errors


@dataclass
class Findings:
    errors: list[str]    # the lint fails
    stale: list[str]     # reported only


def lint(root: Path = ROOT) -> Findings:
    """Compare the committed list with the one `generate` derives from the saved map extract and the tree."""
    def read(name):
        try:
            return json.loads((root / name).read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            return error

    saved, listed = read(MAP_EXTRACT), read(LIST)
    errors = [f"{name}: unreadable ({value})" for name, value in ((MAP_EXTRACT, saved), (LIST, listed))
              if isinstance(value, Exception)]
    if errors:
        return Findings(errors, [])
    errors = validate_extract(saved) + validate_list(listed)
    if errors:
        return Findings(errors, [])
    return compare(listed, generate(saved, root), root)


def compare(listed: dict, expected: dict, root: Path = ROOT) -> Findings:
    """The lint's findings for the committed list `listed` against the generated `expected`."""
    errors = []
    if listed["map"] != expected["map"]:
        errors.append(f"{LIST}: names map {listed['map']}, but {MAP_EXTRACT} was saved from {expected['map']}")
    have = {row["test"]: row for row in listed["tests"]}
    want = {row["test"]: row for row in expected["tests"]}
    for unit in sorted(want.keys() - have.keys()):
        errors.append(f"missing: {unit} reads history and is not listed ({want[unit]['why']})")
    for unit in sorted(want.keys() & have.keys()):
        if have[unit] != want[unit]:
            errors.append(f"changed: {unit} is listed as {have[unit]}, the tree gives {want[unit]}")
    if [row["test"] for row in listed["tests"]] != sorted(have):
        errors.append(f"{LIST}: the tests are not in order")
    stale = [f"stale: {unit} is listed but no longer reads history"
             + ("" if (root / unit).is_file() else " (the unit is gone)") for unit in sorted(have.keys() - want.keys())]
    if errors:
        errors.append(f"run `python tools/history_tests.py --write` and commit {LIST}")
    return Findings(errors, stale)


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true", help="the lint (exit 1 on a missing or changed entry)")
    action.add_argument("--write", action="store_true", help=f"write {LIST} from {MAP_EXTRACT} and the tree")
    action.add_argument("--save-map", action="store_true",
                        help=f"save {MAP_EXTRACT} from a coverage map (default: the map the selector uses for "
                             "the merge base of HEAD and main)")
    parser.add_argument("--map", type=Path, help="the coverage map --save-map reads")
    parser.add_argument("--base", default=None, help="the commit whose map --save-map finds (default: the merge "
                                                     "base of HEAD and main)")
    args = parser.parse_args(argv)
    if args.save_map:
        test_map = _test_map()
        base = args.base or test_map.git("merge-base", "HEAD", "main")
        path = args.map or test_map.find_map(base)
        if path is None:
            print(f"no usable coverage map for {base}: record one with tools/test_map.py record", file=sys.stderr)
            return 1
        saved = extract(test_map.load(path))
        write_json(ROOT / MAP_EXTRACT, saved)
        print(f"saved {MAP_EXTRACT} from {path}: {len(saved['units'])} units")
        return 0
    if args.write:
        saved = json.loads((ROOT / MAP_EXTRACT).read_text(encoding="utf-8"))
        errors = validate_extract(saved)
        if errors:
            print("\n".join(errors), file=sys.stderr)
            return 1
        listed = generate(saved)
        write_json(ROOT / LIST, listed)
        print(f"wrote {LIST}: {len(listed['tests'])} tests read history")
        return 0
    findings = lint()
    for line in findings.stale:
        print(line)
    if findings.errors:
        print("\n".join(findings.errors), file=sys.stderr)
        return 1
    print(f"{LIST}: every test that reads history is listed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
