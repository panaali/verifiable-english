"""Mutants of the act trees' and the table's data types each fail a fixture (ap-3 review F1).

`lean/VE/Acts/Tree.lean` (`Join`, `Part`, `Filler`, `Modifier`, `Atom`, `Act`) and `lean/VE/Acts/Table.lean`
(`Simple`, `Op`) declare trusted data types. The review found that deleting `Join.and` or `Join.nor`, swapping the names
of `Act.all`'s or `Act.any`'s Bool fields or of `Atom.toWord` and `beWord`, giving `Part`'s indices type `Int`, or
adding a constructor to `Filler` or `Simple` kept every fixture passing. This test reads each type from Lean (its
constructors, their fields and types, and the declaration's source range; `DUMP`) and generates every mutant of the
kinds `OPERATORS` names from that reading, never from the source text: each constructor dropped, one added (a field,
for a structure), each field dropped, the names of two fields of one type swapped, and each `Nat` field retyped `Int`
(the one retyping every fixture's numerals still elaborate under). Swapping two constructors is not a mutant: every use
matches them by name, and the derived `DecidableEq` and `Repr` do not depend on their order.

Each mutant replaces the declaration's range by the mutated declaration, rendered from Lean's reading, in one file
with the bodies of `Tree.lean`, `Linearize.lean`, `Table.lean` (theorems cut, by their ranges) and
`TableExamples.lean`, elaborated with `lake env lean`. A mutant is KILLED when the product code elaborates and the
fixtures do not, and REFUSED when Lean refuses the product code itself for an unknown or missing name, a missing case or
a type that does not fit (the trusted `table` or rendering (ap-3b) names that constructor or field, so the mutant
cannot be written). No mutant may survive. The rendering
of the unmutated types must elaborate cleanly, so a refusal is the mutant's and not the rendering's.
"""
from __future__ import annotations

import itertools
import json
import re
import shutil
import subprocess

import pytest

from subprocesses import HANG_TIMEOUT
from tests.lean_build import LEAN, lean_build

ACTS = LEAN / "VE/Acts"
MODULES = ("VE.Acts.Tree", "VE.Acts.Linearize", "VE.Acts.Table")
EXAMPLES = "VE.Acts.TableExamples"
TYPES = ("Join", "Part", "Filler", "Modifier", "Atom", "Act", "Simple", "Op")
DERIVING = "  deriving DecidableEq, Repr"
RETYPE = {"Nat": "Int"}
OPERATORS = ("drop-constructor", "add-constructor", "drop-field", "swap-names", "retype")
# Lean's codes and texts for a declaration it refuses: a name that is gone, a case that is missing or redundant, a
# term whose type no longer fits.
REFUSED = re.compile(r"lean\.unknownIdentifier|[Uu]nknown (?:constant|identifier)|Missing cases|Redundant alternative|"
                     r"Type mismatch|type mismatch|Invalid pattern|Invalid field|Function expected|Too many arguments|"
                     r"Application type mismatch|has type|is not a field of structure")
ERROR = re.compile(r"^\S+?\.lean:(\d+):\d+: error(?:\(([\w.]+)\))?: ((?:.*)(?:\n(?!\S+?\.lean:\d+:\d+: ).*)*)", re.M)

DUMP = """import Lean
import VE.Acts.Table
open Lean Meta

def apRange (n : Name) : CoreM Json := do
  let some r ← findDeclarationRanges? n | return Json.null
  return Json.arr #[r.range.pos.line, r.range.pos.column, r.range.endPos.line, r.range.endPos.column]

#eval show MetaM Unit from do
  let env ← getEnv
  let mut out : Array Json := #[]
  for (n, ci) in env.constants.map₁.toList do
    let some m := env.getModuleIdxFor? n | continue
    let mn := env.header.moduleNames[m.toNat]!
    unless (@MODULES@ : List Name).contains mn do continue
    match ci with
    | .inductInfo v =>
      let mut cs : Array Json := #[]
      for c in v.ctors do
        let fs ← forallTelescope (← getConstInfo c).type fun xs _ => xs.mapM fun x => do
          let d ← x.fvarId!.getDecl
          let ty ← withOptions (pp.fullNames.set · true) (ppExpr d.type)
          return Json.arr #[toJson d.userName.toString, toJson (toString ty)]
        cs := cs.push (Json.mkObj [("name", toJson c.toString), ("fields", Json.arr fs)])
      out := out.push (Json.mkObj [("type", toJson n.toString), ("module", toJson mn.toString),
        ("structure", toJson (isStructure env n)), ("range", ← apRange n), ("constructors", Json.arr cs)])
    | .thmInfo _ =>
      let r ← apRange n
      unless r.isNull do
        out := out.push (Json.mkObj [("theorem", toJson n.toString), ("module", toJson mn.toString), ("range", r)])
    | _ => pure ()
  IO.println (Json.arr out).compress
"""


@pytest.fixture(scope="module")
def lake():
    path = shutil.which("lake")
    if path is None:
        pytest.skip("lake is not available")
    lean_build("VE")
    return path


def _elaborate(lake: str, where, name: str, source: str) -> subprocess.CompletedProcess:
    file = where / f"{name}.lean"
    file.write_text(source)
    return subprocess.run([lake, "env", "lean", str(file)], cwd=LEAN, capture_output=True, text=True,
                          timeout=HANG_TIMEOUT)


@pytest.fixture(scope="module")
def shapes(lake, tmp_path_factory):
    """Lean's reading of the modules: {"types": {short name: entry}, "theorems": [entry]}."""
    modules = "[" + ", ".join(f"`{m}" for m in MODULES) + "]"
    done = _elaborate(lake, tmp_path_factory.mktemp("dump"), "ApTreeDump",
                      DUMP.replace("@MODULES@", modules))
    assert done.returncode == 0, done.stdout + done.stderr
    rows = json.loads(done.stdout)
    types = {row["type"].rsplit(".", 1)[1]: row for row in rows if "type" in row}
    return {"types": types, "theorems": [row for row in rows if "theorem" in row]}


def _short(name: str) -> str:
    return name.rsplit(".", 1)[1]


def render(entry: dict, constructors: list[tuple[str, list[tuple[str, str]]]]) -> str:
    """The declaration of a type with these constructors (name, [(field, type)]), as `Tree.lean` writes it."""
    name = _short(entry["type"])
    if entry["structure"]:
        [(_, fields)] = constructors
        return f"structure {name} where\n" + "".join(f"  {f} : {t}\n" for f, t in fields) + DERIVING
    arms = " ".join(f"| {c}" + "".join(f" ({f} : {t})" for f, t in fields) for c, fields in constructors)
    return f"inductive {name} {arms}\n{DERIVING}"


def constructors_of(entry: dict) -> list[tuple[str, list[tuple[str, str]]]]:
    return [(_short(c["name"]), [tuple(f) for f in c["fields"]]) for c in entry["constructors"]]


def mutants(entry: dict) -> dict[str, list[tuple[str, list[tuple[str, str]]]]]:
    """{id: mutated constructors} for one type, every operator of `OPERATORS` applied at every place it applies."""
    cs, out = constructors_of(entry), {}
    if len(cs) > 1:
        for i, (c, _) in enumerate(cs):
            out[f"drop-constructor {c}"] = cs[:i] + cs[i + 1:]
    if entry["structure"]:
        out["add-constructor (a field: extra : Bool)"] = [(cs[0][0], cs[0][1] + [("extra", "Bool")])]
    else:
        out["add-constructor extra"] = cs + [("extra", [])]
    for i, (c, fields) in enumerate(cs):
        def at(new_fields, i=i, c=c):
            return cs[:i] + [(c, new_fields)] + cs[i + 1:]
        for j, (f, t) in enumerate(fields):
            out[f"drop-field {c}.{f}"] = at(fields[:j] + fields[j + 1:])
            if t in RETYPE:
                out[f"retype {c}.{f} {t} -> {RETYPE[t]}"] = at(fields[:j] + [(f, RETYPE[t])] + fields[j + 1:])
        for (j, (f, t)), (k, (g, u)) in itertools.combinations(enumerate(fields), 2):
            if t == u:
                swapped = list(fields)
                swapped[j], swapped[k] = (g, t), (f, u)
                out[f"swap-names {c}.{f} {c}.{g}"] = at(swapped)
    return out


def _offset(text: str, line: int, column: int) -> int:
    lines = text.split("\n")
    return sum(len(x) + 1 for x in lines[:line - 1]) + column


def _replace_ranges(text: str, edits: list[tuple[list[int], str, str]]) -> str:
    """`text` with each Lean range [line, column, end line, end column] replaced, last first. Each range must hold the
    declaration Lean names for it (`inductive Join`, `theorem table_one`): an olean older than the source fails here."""
    spans = sorted(((_offset(text, r[0], r[1]), _offset(text, r[2], r[3]), new, decl) for r, new, decl in edits),
                   reverse=True)
    for start, end, new, decl in spans:
        assert re.search(rf"^(?:{decl})\b", text[start:end], re.M), f"stale build: {decl!r} is not at its range"
        text = text[:start] + new + text[end:]
    return text


def _body(text: str) -> tuple[list[str], str]:
    lines = text.split("\n")
    return [x for x in lines if x.startswith("import ")], "\n".join(x for x in lines if not x.startswith("import "))


def assemble(shapes: dict, replaced: dict[str, list[tuple[str, list]]]) -> tuple[str, list[tuple[str, int, int]]]:
    """One file: each module's body with its types rendered (`replaced` gives some types other constructors) and its
    theorems cut, then the fixtures. Returns the text and each part's lines [first, last]."""
    imports, parts, regions, line = [], [], [], 1
    for module in (*MODULES, EXAMPLES):
        text = (LEAN / (module.replace(".", "/") + ".lean")).read_text()
        edits = [(e["range"], render(e, replaced.get(name, constructors_of(e))), f"(?:inductive|structure) {name}")
                 for name, e in shapes["types"].items() if e["module"] == module]
        edits += [(t["range"], "", f"theorem {_short(t['theorem'])}") for t in shapes["theorems"] if t["module"] == module]
        found, body = _body(_replace_ranges(text, edits))
        imports += [x for x in found if x.split()[1] not in (*MODULES, EXAMPLES) and x not in imports]
        parts.append(body)
        regions.append((module, line, line + body.count("\n")))
        line += body.count("\n") + 1
    head = "\n".join(imports) + "\n"
    shift = head.count("\n")
    return head + "\n".join(parts), [(m, a + shift, b + shift) for m, a, b in regions]


def errors(out: str, regions) -> list[tuple[str, str, str]]:
    """(module, code, message) of each error of a run."""
    def module(line: int) -> str:
        return next((m for m, a, b in regions if a <= line <= b), "?")
    return [(module(int(m.group(1))), m.group(2) or "", m.group(3)) for m in ERROR.finditer(out)]


def verdict(found: list[tuple[str, str, str]]) -> str:
    if not found:
        return "SURVIVOR"
    product = [(code, text) for m, code, text in found if m in MODULES]
    if product:
        refused = all(REFUSED.search(code + " " + text) for code, text in product)
        return "REFUSED" if refused else "UNKNOWN"
    return "KILLED" if all(m == EXAMPLES for m, _, _ in found) else "UNKNOWN"


def run_type(lake, where, shapes: dict, name: str) -> dict[str, tuple[str, list]]:
    """{mutant id: (verdict, errors)} for every mutant of one type."""
    entry, out = shapes["types"][name], {}
    for k, (mid, cs) in enumerate(sorted(mutants(entry).items())):
        source, regions = assemble(shapes, {name: cs})
        done = _elaborate(lake, where, f"ApTreeMutant{k}", source)
        found = errors(done.stdout + done.stderr, regions)
        out[mid] = ("SURVIVOR" if done.returncode == 0 else verdict(found)), found
    return out


def test_every_data_type_of_the_trees_and_the_table_is_swept(shapes):
    """`TYPES` is every inductive type the two modules declare, as Lean lists them; a new type joins the sweep."""
    assert sorted(shapes["types"]) == sorted(TYPES)
    assert all(e["range"] for e in shapes["types"].values())


def test_every_operator_applies_somewhere(shapes):
    """Each operator generates at least one mutant over the types, so none is dead code."""
    ids = [mid for e in shapes["types"].values() for mid in mutants(e)]
    assert all(any(mid.startswith(op) for mid in ids) for op in OPERATORS), ids
    for review in ("drop-constructor and", "drop-constructor nor", "swap-names all.shared all.split",
                   "swap-names any.nor any.split", "swap-names mk.toWord mk.beWord", "retype slot.i Nat -> Int",
                   "retype fixed.i Nat -> Int", "add-constructor extra"):
        assert review in ids, review


def test_the_rendered_unmutated_types_elaborate_cleanly(lake, tmp_path, shapes):
    source, _ = assemble(shapes, {})
    done = _elaborate(lake, tmp_path, "ApTreeUnmutated", source)
    assert done.returncode == 0 and "error" not in done.stdout + done.stderr, done.stdout + done.stderr


def test_each_mutant_changes_its_declaration(shapes):
    for name, entry in shapes["types"].items():
        original = render(entry, constructors_of(entry))
        for mid, cs in mutants(entry).items():
            assert render(entry, cs) != original, (name, mid)


@pytest.mark.parametrize("name", TYPES)
def test_every_mutant_of_a_data_type_is_killed_or_refused(lake, tmp_path, shapes, name):
    results = run_type(lake, tmp_path, shapes, name)
    bad = {mid: found for mid, (v, found) in results.items() if v not in ("KILLED", "REFUSED")}
    assert not bad, json.dumps(bad, indent=1)
    if name in ("Join", "Part", "Filler", "Modifier", "Atom"):
        # Only the rendering (ap-3b) matches these types, by constructor and by field name: it refuses a dropped or
        # added constructor and a retyped index, but two fields of one type swapped by name still elaborate there, so
        # only a fixture can catch them.
        assert all(v == "KILLED" for m, (v, _) in results.items() if m.startswith("swap-names")), \
            {m: v for m, (v, _) in results.items()}


def test_the_verdict_reads_where_each_error_is():
    """A mutant whose errors are all in the fixtures is killed; one refused by the product code is refused only for a
    reason of `REFUSED`; any other product error, or none, is not a kill."""
    assert verdict([(EXAMPLES, "", "Expression\n  x\ndid not evaluate to `true`")]) == "KILLED"
    assert verdict([("VE.Acts.Table", "lean.unknownIdentifier", "Unknown identifier `x`"),
                    (EXAMPLES, "", "x")]) == "REFUSED"
    assert verdict([("VE.Acts.Linearize", "", "`toWord` is not a field of structure `Atom`")]) == "REFUSED"
    assert verdict([("VE.Acts.Tree", "", "unexpected token 'where'")]) == "UNKNOWN"
    assert verdict([("?", "", "x")]) == "UNKNOWN"
    assert verdict([]) == "SURVIVOR"
    region = [("VE.Acts.Tree", 3, 5), (EXAMPLES, 6, 9)]
    out = "/t/F.lean:4:0: error(lean.unknownIdentifier): Unknown identifier `x`\n/t/F.lean:7:2: error: Expression\n  y\n"
    assert errors(out, region) == [("VE.Acts.Tree", "lean.unknownIdentifier", "Unknown identifier `x`"),
                                   (EXAMPLES, "", "Expression\n  y\n")]


def test_a_range_that_does_not_hold_its_declaration_fails_closed():
    """Ranges come from the oleans: when they are older than the source, nothing is replaced in the wrong place."""
    text = "theorem a : True := trivial\ninductive Join | and\n"
    assert _replace_ranges(text, [([2, 0, 2, 20], "inductive Join | or", "(?:inductive|structure) Join")]) == \
        "theorem a : True := trivial\ninductive Join | or\n"
    with pytest.raises(AssertionError, match="stale build"):
        _replace_ranges(text, [([1, 0, 1, 27], "", "theorem b")])
