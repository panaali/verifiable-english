"""The architecture map (`docs/ARCHITECTURE.md`), its stale-document sweep and the binding ADR (batch AR-7).

The map's tables are rendered from the saved measurement `docs/architecture/numbers.json` (never from a live
measurement of a moving head), every saved number must be shown, the measuring tool is checked on a small tree
built here, each stale statement of the map's section 6 is either gone from its file or marked superseded with a
link to the map (or still waits for its stated reason), and ADR 0001 records D1 as the DRI signed it: its clauses,
each relation's keywords and each leaf class's shapes are held here, its Decision section is pinned, and Lean's
`Shape` constructors, the dialect's keywords and the ADR's tables name one set.
"""
import copy
import hashlib
import json
from pathlib import Path
import re
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import architecture_numbers as numbers  # noqa: E402

MAP = ROOT / "docs/ARCHITECTURE.md"
ADR = ROOT / "docs/adr/0001-response-binding.md"
DIALECT = ROOT / "ve/backends/lean_service_schema/README.md"
SAVED = json.loads((ROOT / numbers.NUMBERS).read_text())
# Dialect keywords that shape or select a value and bind nothing to the request.
STRUCTURAL = {"x-tagged", "x-fuel", "x-case", "x-select", "x-row", "x-same-length", "x-equal-fields"}
# Batch 13b introduced these bounded response checks before D1 classified their
# dialect keywords. Keep the signed Decision section pinned and track the exact
# outstanding set until its owner reviews the extension.
PENDING_D1 = {"x-claim-nodes", "x-max-steps", "x-background-bound", "x-reading-plan"}


def flat(text):
    return " ".join(text.split())


def paragraphs(text):
    return [flat(p) for p in re.split(r"\n\s*\n", text)]


def table(text, header):
    """The rows of the table whose header line is `header`, without the header and its rule, as lists of cells."""
    lines = text.splitlines()
    start = lines.index(header)
    rows = []
    for line in lines[start:]:
        if line.startswith("|"):
            rows.append([cell.strip() for cell in re.split(r"(?<!\\)\|", line.strip().strip("|"))])
        elif rows:
            break
    return rows[2:]


def leaves(value, path=()):
    if isinstance(value, dict):
        for key, item in value.items():
            yield from leaves(item, (*path, key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from leaves(item, (*path, index))
    else:
        yield path, value


def test_map_tables_are_rendered_from_the_saved_numbers():
    assert re.fullmatch(r"[0-9a-f]{40}", SAVED["commit"])
    assert numbers.main(["--check"]) == 0


def test_every_saved_number_is_shown():
    """Changing any one saved number changes the rendered map, so no measured number is left out of it."""
    base = numbers.render(SAVED)
    for path, value in leaves(SAVED["numbers"]):
        if not isinstance(value, int):
            continue
        changed = copy.deepcopy(SAVED)
        target = changed["numbers"]
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value + 1_000_003
        assert numbers.render(changed) != base, path


def test_check_fails_on_a_stale_table(tmp_path, monkeypatch):
    doc, saved = tmp_path / "map.md", tmp_path / "numbers.json"
    doc.write_text(MAP.read_text().replace(f"| {SAVED['numbers']['counts']['service_modes']} |", "| 30 |", 1))
    saved.write_text(json.dumps(SAVED))
    monkeypatch.setattr(numbers, "ROOT", tmp_path)
    monkeypatch.setattr(numbers, "DOC", Path("map.md"))
    monkeypatch.setattr(numbers, "NUMBERS", Path("numbers.json"))
    assert numbers.main(["--check"]) == 1


def test_markers_must_match_the_tables():
    rendered = numbers.render(SAVED)
    text = MAP.read_text()
    with pytest.raises(ValueError):
        numbers.apply(text.replace("<!-- /numbers:trust -->", ""), rendered)
    with pytest.raises(ValueError):
        numbers.apply(text, {**rendered, "extra": "x"})


@pytest.mark.parametrize("path, pattern, expected", [
    ("ve/a.py", "ve/**/*.py", True),
    ("ve/b/c/d.py", "ve/**/*.py", True),
    ("ve.py", "ve/**/*.py", False),
    ("vex/a.py", "ve/**/*.py", False),
    ("ve/a.pyc", "ve/**/*.py", False),
    ("s/x.json", "s/*.json", True),
    ("s/t/x.json", "s/*.json", False),
])
def test_glob(path, pattern, expected):
    assert numbers.matches(path, pattern) is expected


def fixture_tree():
    files = {
        "ve/a.py": "1\n2\n", "ve/backends/relay.py": "1\n", "ve/backends/lean_service.py": "1\n2\n3\n",
        "ve/backends/service_schema.py": 'X = 1\nMODES = ("a", "b", "c")\n',
        "ve/backends/lean_service_schema/a.json": "{}\n", "ve/backends/lean_service_schema/sub/b.json": "{\n}\n",
        "lean/VE/A.lean": "a\n", "lean/VE/B/C.lean": "b\nc\n", "lean/ResponseShape/S.lean": "s\n",
        "lean/ResponseDecode.lean": "d\n", "lean/Serve.lean": "",
        **{path: "x\n" for path in numbers.SERVICE_FILES + numbers.INVENTORIES},
        "lean/lakefile.toml": '[[lean_exe]]\nname = "a"\n[[lean_exe]]\nname = "b"\n',
        "rust/Cargo.toml": '[workspace]\nmembers = ["k", "p"]\n',
        "rust/k/src/lib.rs": "1\n", "rust/k/src/m/x.rs": "1\n2\n", "rust/p/src/lib.rs": "1\n2\n3\n",
        "tools/t.py": "1\n", "tests/test_a.py": "1\n", "tests/helpers/b.py": "1\n2\n", "tests/conftest.py": "",
        "conformance/c.py": "1\n",
        "pyproject.toml": '[project]\ndependencies = ["a", "b"]\n',
        "tools/layer-exceptions.json": '{"a -> b": 1}', "tools/lean-layer-exceptions.json": "{}",
        "tools/gate-collection.json": '["t1", "t2", "t3", "t4"]',
        "ve/assurance-manifest.json": '{"lean_decoders": {"total_lines": 77}}',
        "docs/trust-baseline.json": json.dumps({
            "totals": {key: index for index, key in enumerate(numbers.TRUST_TOTALS)} | {"tied": 9},
            "budget": {"K": 1, "S": 2, "V": 3}}),
        "docs/lean-first/big.bin": "", "docs/x.md": "",
    }
    data = {path: text.encode() for path, text in files.items()}
    sizes = {path: len(blob) for path, blob in data.items()}
    sizes["docs/lean-first/big.bin"] = 3 * numbers.MIB
    sizes["docs/x.md"] = numbers.MIB
    return data, sizes


def test_measure_on_a_small_tree():
    data, sizes = fixture_tree()
    got = numbers.measure(data.__getitem__, sizes)
    assert got["lines"] == {"ve_python": 8, "ve_backends_python": 6, "ve_backends_schema_json": 1, "lean": 9,
                            "tools_python": 1, "tests_python": 3, "conformance_python": 1}
    assert got["largest_ve_python"][0] == {"path": "ve/backends/lean_service.py", "lines": 3}
    assert [x["path"] for x in got["largest_ve_python"]] == [
        "ve/backends/lean_service.py", "ve/a.py", "ve/backends/service_schema.py"]
    assert got["rust_lines"] == {"k": 3, "p": 3}
    assert got["files"] == {"lean_ve_modules": 6, "response_shape_lean": 2, "tests_test_modules": 1,
                            "tests_other_modules": 2}
    assert got["mib"] == {"docs": 4, "docs_lean_first": 3, "tracked": 4}
    assert got["counts"] == {"service_modes": 3, "lean_executables": 2, "runtime_dependencies": 2,
                             "python_layer_exceptions": 1, "lean_layer_exceptions": 0,
                             "collected_test_ids": 4, "pinned_decoder_lines": 77}
    assert "tied" not in got["trust"]["totals"] and got["trust"]["totals"]["lines"] == len(numbers.TRUST_TOTALS) - 1


def test_measure_fails_closed():
    data, sizes = fixture_tree()
    del sizes["conformance/c.py"]
    with pytest.raises(ValueError, match="conformance"):
        numbers.measure(data.__getitem__, sizes)
    data, sizes = fixture_tree()
    data["ve/backends/service_schema.py"] = b"MODES = tuple(['a'])\n"
    with pytest.raises(ValueError, match="MODES"):
        numbers.measure(data.__getitem__, sizes)


def stale_rows():
    return table(MAP.read_text(), "| # | Document | It says | Today | Status |")


def stale_file(cell):
    link = re.search(r"\]\(([^)#]+)\)", cell)
    return ROOT / "docs" / link.group(1) if link else ROOT / re.search(r"`([^`]+)`", cell).group(1)


def quotes(cell):
    """The quoted fragments of an 'It says' cell, split at the ellipses."""
    return [part.strip() for quote in re.findall(r'"([^"]+)"', cell) for part in quote.split("…") if part.strip()]


def test_the_sweep_has_the_eleven_statements_of_the_review():
    rows = stale_rows()
    assert [row[0] for row in rows] == [str(n) for n in range(1, 12)]
    for row in rows:
        assert re.fullmatch(r"corrected|waits: .+|recorded here: .+", row[4]), row


@pytest.mark.parametrize("row", stale_rows(), ids=lambda row: row[0])
def test_stale_statement(row):
    number, document, says, _, status = row
    if status.startswith("recorded here"):
        assert "not on `main`" in status and not (ROOT / "docs/LEAN-FIRST-PLAN.md").exists()
        return
    path = stale_file(document)
    text = path.read_text()
    fragments = quotes(says)
    # Every checked row quotes the stale text, one quote per passage it covers; a row without quotes checks nothing.
    assert fragments, number
    if path.suffix == ".json":
        # A JSON inventory: the quotes are keys of the section the row names; AR-4 drops the section.
        section = sorted(backticked(document) - {str(path.relative_to(ROOT))})
        data = json.loads(text)
        assert len(section) == 1, row
        if status.startswith("waits"):
            missing = [f for f in fragments if f not in data.get(section[0], {})]
            assert not missing, (number, missing)
        else:
            assert section[0] not in data, number
        return
    if status.startswith("waits"):
        # Still stale in its file: once the file is fixed the row must say so.
        missing = [f for f in fragments if not any(f in p for p in paragraphs(text))]
        assert not missing, (number, path, missing)
        return
    link = re.compile(r"\]\((\.\./)?ARCHITECTURE\.md[)#]")
    assert link.search(text), path
    for fragment in fragments:
        for paragraph in paragraphs(text):
            if fragment in paragraph:
                assert "Superseded" in paragraph and link.search(paragraph), (number, fragment)


def relative_links(path):
    for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
        if not re.match(r"[a-z]+:", target):
            yield target.split("#", 1)[0]


@pytest.mark.parametrize("path", [MAP, ADR], ids=lambda p: p.name)
def test_links_resolve(path):
    targets = list(relative_links(path))
    assert targets
    for target in targets:
        assert (path.parent / target).exists(), target


def adr_decision():
    adr = ADR.read_text()
    return adr[adr.index("\n## Decision\n"):adr.index("\n## Consequences\n")]


def dialect_keywords():
    return set(re.findall(r"^\| `(x-[a-z-]+)", DIALECT.read_text(), re.M))


def backticked(cell):
    return set(re.findall(r"`([^`]+)`", cell))


# D1 as the DRI signed it (review section 5) and the clauses of T1(a) and T1(b) it adopts. An ADR that drops one
# of them, or loosens it, no longer records the signed decision.
D1_CLAUSES = [
    "Binding is a closed list of relations to the request. A field that names a request item is bound only by "
    "`references` or `equals`.",
    "Derived values are Lean's, proved or checked by `ResponseDecode` invariants, and never recomputed in Python. "
    "Their leaves carry the `derived (guarantee)` mark. An encoder theorem is preferred, because a `ResponseDecode` "
    "invariant is checked only at test time.",
    "The census proves that every leaf is classified, not that it is correctly classified.",
    "**A field that names a request item is bound only by `references` or `equals`** (relation 6 or 2) to the "
    "relevant request set. A format check is not a binding:",
    "An `x-echo` does not bind a named item either, because it accepts `null` when the item is absent.",
    "Python binds a stored value it owns by equality and never by echo (D7).",
    "**Python never recomputes it to check it**.",
    "Its leaf carries the `derived (guarantee)` mark, naming that theorem or invariant",
    "An encoder theorem is preferred wherever it is feasible, because a `ResponseDecode` invariant is checked only "
    "at test time: a value covered only by an invariant is not checked at run time,",
    "a named request item by relation 2 or 6 only, and no row is empty or extra. Nothing else.",
    "`pattern` checks a format and puts a leaf in no class.",
    "**The census proves that every leaf is classified, not that it is correctly classified**",
]
# Each relation's dialect keywords; relation 7 has none until AR-11a adds `x-at-most`.
RELATIONS = {
    "echoes": {"x-echo", "x-digest"},
    "equals": {"x-equals"},
    "counts": {"x-count", "x-count-where", "x-count-presence"},
    "measures": {"x-length"},
    "indexes": {"x-index", "x-zip", "x-zip-or-empty", "x-rows"},
    "references": {"x-references"},
    "is bounded by": set(),
}
# The four leaf classes and the shapes that place a leaf in each; `pattern` places it in none.
CLASSES = {
    "bound": set(),
    "closed domain": {"const", "enum", "lean", "copied", "x-tagged"},
    "derived (guarantee)": {"x-derived"},
    "text": {"x-text"},
}
# Every constructor of Lean's `Shape` (lean/ResponseShape.lean) with the dialect keyword it renders, JSON Schema's
# own keywords (None) or a wrapper rendered as its inner shape ("inner"). A new constructor fails here until it is
# classified, and a new binding keyword fails the relation table until the ADR places it.
SHAPES = {
    **dict.fromkeys(["bool", "type", "const", "enum", "pattern", "minLength", "maxLength", "minimum", "required",
                     "object", "prefixItems", "items", "minItems", "maxItems", "contains", "anyOf", "allOf", "not",
                     "ite", "ref"]),
    **dict.fromkeys(["node", "lean", "copied", "encodedEnvironment"], "inner"),
    "tagged": "x-tagged", "fuel": "x-fuel", "echo": "x-echo", "equals": "x-equals", "length": "x-length",
    "claimNodes": "x-claim-nodes", "maxSteps": "x-max-steps", "backgroundBound": "x-background-bound",
    "readingPlan": "x-reading-plan",
    "count": "x-count", "references": "x-references", "index": "x-index", "digest": "x-digest", "zip": "x-zip",
    "sameLength": "x-same-length", "equalFields": "x-equal-fields",
    "zipOrEmpty": "x-zip-or-empty", "onCase": "x-case", "select": "x-select", "countWhere": "x-count-where",
    "presenceCount": "x-count-presence", "rows": "x-rows", "row": "x-row",
}
# sha256 of the Decision section, whitespace-normalised. It changes only with a new signature of the DRI (D1); a
# batch that changes the section records the signature and updates this pin in the same merge.
ADR_DECISION_SHA256 = "f4f90c1c34a07fe2036377e3199b8afe55342731f1bb17422751dbef4b5ccbc9"


def test_adr_records_d1_as_signed():
    adr = ADR.read_text()
    assert "**Status:** Accepted. Signed by the DRI on 2026-10-10 as decision D1" in adr
    decision = flat(adr_decision())
    missing = [clause for clause in D1_CLAUSES if flat(clause) not in decision]
    assert not missing, missing


def test_adr_decision_is_pinned():
    assert hashlib.sha256(flat(adr_decision()).encode()).hexdigest() == ADR_DECISION_SHA256


def test_adr_relation_keywords():
    adr = adr_decision()
    rows = table(adr, next(line for line in adr.splitlines() if line.startswith("| # | Relation |")))
    assert [row[0] for row in rows] == [str(n) for n in range(1, 8)]
    assert {row[1]: backticked(row[3]) - {"atMost", "x-at-most"} for row in rows} == RELATIONS
    assert rows[6][3].startswith("none yet")
    named = set().union(*RELATIONS.values())
    assert dialect_keywords() - STRUCTURAL - PENDING_D1 == named, (dialect_keywords() - STRUCTURAL - PENDING_D1) ^ named


def test_adr_leaf_classes():
    adr = adr_decision()
    rows = table(adr, "| Class | The leaf … | Shapes |")
    assert {row[0]: backticked(row[2]) for row in rows} == CLASSES
    for row in rows:
        assert "pattern" not in row[2] and "minLength" not in row[2], row


def test_lean_shapes_are_classified():
    """The constructors of Lean's `Shape`, the dialect's extension keywords and the ADR's tables name one set."""
    source = (ROOT / "lean/ResponseShape.lean").read_text()
    body = source[source.index("inductive Shape where"):source.index("deriving Inhabited")]
    assert set(re.findall(r"^  \| (\w+)", body, re.M)) == set(SHAPES)
    keywords = {kw for kw in SHAPES.values() if kw and kw.startswith("x-")}
    assert keywords == dialect_keywords(), keywords ^ dialect_keywords()
    assert keywords == STRUCTURAL | set().union(*RELATIONS.values()) | PENDING_D1
    closed = {name for name, kw in SHAPES.items() if kw is None or kw == "inner"} | {"x-tagged"}
    assert CLASSES["closed domain"] <= closed
