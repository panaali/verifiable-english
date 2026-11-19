"""defs-carried-gate-stage1-1119: the report-mode definitions-carried checker (tools/defs_carried.py).

T1 raw detection on the known cases at the pin (FSF/RSP: each repair's merge base), read by blob id; T5 surface
mutants; T9 equivalences; the shared-input selection case (Codex B11); the report-mode exit code; the byte pin of the
counter code; the known-case fixture's counts and quote re-cuts; detectors (b) and (c) and the section 5 lexical bar.
"""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from subprocesses import HANG_TIMEOUT

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import defs_carried as dc  # noqa: E402

DATA = ROOT / "tests" / "data" / "defs_carried"
FIXTURE = json.loads((DATA / "known_cases.json").read_text(encoding="utf-8"))

# The known cases the checker does not reach at the pin, each with its reason (REPORT.md, "Misses"). Every other case
# must be reported not carried. A new miss, or a listed miss that starts to be reached, fails T1.
MISS_REASONS = {
    "defs-asimov-extended-7-1119:R16": "R16 uses lawful_action, which R14 derives from breaks_first_law; the adapter "
                                       "does not follow a derived predicate to the rule that derives it",
    "defs-asimov-laws-2-1119:R9": "R9 names harms_humanity, not breaks_zeroth_law; the audit paired them by meaning",
    "defs-claude-constitution-pilot-1-1119:u0036.s05": "the unit's open meaning names genuine_ambiguity only; no "
                                                       "parsed term of it is the sort claude_instance",
    "defs-udhr-pilot-1-1119:u052": "u052 uses asylum_right_covers_case only in its reading sets (not a dependency "
                                   "source: a reading holds a meaning_id hash and content null)",
    "udhr-D7:u112:exercise_of_declared_right": "the predicate is used only in u112's reading sets",
    "udhr-D7:u114:declaration_implies_destructive_right": "the predicate is used only in u114's reading sets",
}
# defs-eligibility-2 (qualifying week, all 49 rules): the 20 rules that use no predicate whose legend names the
# qualifying week have no VE term for it (the row is a needs-rule-line row: B1 is a date fact).
ELIGIBILITY_2_NO_TERM = 20


@pytest.fixture(scope="module")
def t1():
    return dc.run_known_trees(FIXTURE, repo=ROOT)


def test_t1_every_known_case_is_reported_not_carried_or_a_named_miss(t1):
    """CONDITION TEST (T1 raw detection): at the pin every known case's verdict is below CARRIED-ASSUMED, and the
    pairs the adapters do not reach are exactly the named misses."""
    unread = [x for x in t1["results"] if x["reach"] == "rule-missing" and x["verdict"] is None]
    assert not unread
    assert t1["pairs"] == len(FIXTURE["cases"]) == FIXTURE["counts"]["cases"]
    passing = [x["case"] for x in t1["results"] if x["verdict"] in dc.PASSING]
    assert passing == [], passing
    misses = {x["case"]: x for x in t1["misses"]}
    elig = [c for c in misses if c.startswith("defs-eligibility-2-1119:")]
    assert len(elig) == ELIGIBILITY_2_NO_TERM and all(misses[c]["reach"] == "no-ve-term" for c in elig)
    assert set(misses) - set(elig) == set(MISS_REASONS)
    assert t1["hits"] == t1["pairs"] - len(MISS_REASONS) - ELIGIBILITY_2_NO_TERM


def test_t1_each_of_the_61_known_findings_is_detected(t1):
    """Every P1 row and every FSF/RSP repair (61 findings) but one has at least one reached pair detected not
    carried; the one is udhr-pilot row 1, whose only pair (u052) is a reading-set dependency (a named miss)."""
    by = {}
    for x in t1["results"]:
        k = next(c for c in FIXTURE["cases"] if c["case"] == x["case"])
        if k["prio"] in ("P1", "repair"):
            by.setdefault(k["row"], []).append(x["hit"])
    assert len(by) == FIXTURE["counts"]["known_findings"] == 61
    assert [r for r, hits in by.items() if not any(hits)] == ["defs-udhr-pilot-1-1119"]


def test_t1_the_fsf_lessons_get_their_classes(t1):
    """F3: the Glossary's Safety Cases sentence sits whole on the safety_case legend, a predicate f12/f13 do not use
    (ELSEWHERE); F6: the SL2+ definition sits only in a '## ' header (UNSHOWN)."""
    v = {x["case"]: x for x in t1["results"]}
    for b in ("f12-p", "f12-u", "f13-p", "f13-u"):
        [x] = [x for c, x in v.items() if c.startswith(f"F3:{b}:governance_found_acceptable_with_safety_case_")]
        assert x["verdict"] == "ELSEWHERE" and x["where"][0].endswith("legend:safety_case")
    assert any(x["verdict"] == "UNSHOWN" and x["where"][0].startswith("header:") for c, x in v.items()
               if c.startswith("F6:"))


def test_the_known_case_fixture_counts_and_rows():
    """52 P1 + 20 P2 rows, 9 repairs, 5 D7 pairs; every row of the committed audit copy gives at least one case."""
    c = FIXTURE["counts"]
    assert (c["rows"], c["rows_P1"], c["rows_P2"], c["repairs"], c["d7_pairs"]) == (72, 52, 20, 9, 5)
    import csv
    ids = set()
    for f in sorted((DATA / "audit").glob("rows-*.tsv")):
        with open(f, encoding="utf-8", newline="") as fh:
            ids |= {r["id"] for r in csv.DictReader(fh, delimiter="\t", quoting=csv.QUOTE_NONE)}
    assert len(ids) == 72
    assert ids == {k["row"] for k in FIXTURE["cases"] if k["prio"] in ("P1", "P2")}
    assert {k["kind"] for k in FIXTURE["cases"] if k["prio"] == "repair"} == {
        "F1", "F2", "F3", "F5", "F6", "F7", "F8", "F9", "R1"}
    assert all(k["passages"] and all(p["text"] for p in k["passages"]) for k in FIXTURE["cases"])


def test_every_passage_is_verbatim_source_text_at_its_tree():
    """A quote is the source as written or a re-cut of it: every non-FSF passage occurs in the document's source at
    the pin (under source_norm), and every re-cut is listed with what it dropped."""
    trees = {}
    for k in FIXTURE["cases"]:
        if k["prio"] == "repair":
            continue
        tree = trees.setdefault(k["tree"], dc.MemTree(FIXTURE["trees"][k["tree"]]["files"], repo=ROOT))
        for p in k["passages"]:
            src = tree.read(p["file"])
            assert src is not None, p["file"]
            body = dc.front_matter(src)[1] if src.startswith("---\n") else src
            assert dc.source_norm(p["text"]) in dc.source_norm(body), (k["case"], p["text"][:80])
    for r in FIXTURE["recut"]:
        assert r["passages"] and r["kind"] in ("cut to the source passage",) or r["kind"].startswith("split into")
    assert len(FIXTURE["recut"]) == FIXTURE["counts"]["recut_quotes"] == 18


# ------------------------------------------------------------------------------------- synthetic documents (T5, T9) ---
ENV = {
    "vocabulary": {
        "sorts": {"robot": {"description": "a robot", "verbalisation": {"singular": "robot", "plural": "robots"}}},
        "predicates": {
            "careful": {"arguments": ["robot"], "description": "{0} is careful", "verbalisation": "{0} is careful"},
            "spare": {"arguments": ["robot"], "description": "{0} is spare", "verbalisation": "{0} is spare"},
        },
        "constants": {"robbie": {"sort": "robot", "description": "Robbie", "verbalisation": "Robbie"}},
    }
}
DEF = "A careful robot checks every step twice before it moves."


def _rules_doc(where, text=DEF):
    env = json.loads(json.dumps(ENV))
    rules = 'Rule 1. Every robot is classified as "careful", if that robot is classified as "careful".\n'
    if where == "legend":
        env["vocabulary"]["predicates"]["careful"]["description"] += " " + text
    elif where == "constant":
        env["vocabulary"]["constants"]["robbie"]["description"] += " " + text
    elif where == "sort":
        env["vocabulary"]["sorts"]["robot"]["description"] += " " + text
    elif where == "verbalisation":
        env["vocabulary"]["predicates"]["careful"]["negative_verbalisation"] = text
    elif where == "unused":
        env["vocabulary"]["predicates"]["spare"]["description"] += " " + text
    elif where == "comment":
        rules += "# " + text + "\n"
    elif where == "rule":
        rules = rules.rstrip("\n").rstrip(".") + ", unless " + text + "\n"
    files = {"usecases/asimov-laws/rules.ve": rules,
             "usecases/asimov-laws/environment.json": json.dumps(env),
             "usecases/asimov-laws/source.md": text + "\n"}
    return dc.build_doc("asimov-laws", dc.MemTree(files))


def _verdict(doc, rule, text=DEF):
    return dc.verdict(doc, doc.rules[rule], text)["verdict"]


@pytest.mark.parametrize("where", ["constant", "sort", "verbalisation", "unused", "comment"])
def test_t5_a_definition_off_the_shown_surface_is_not_carried(where):
    v = _verdict(_rules_doc(where), "R1")
    assert v == "UNSHOWN", (where, v)


def test_t5_the_shown_surface_carries_but_only_as_assumed_outside_the_counter():
    """A non-counter document's surface is not established: whole in a used predicate's legend or in the rule line is
    CARRIED-ASSUMED, never CARRIED, and the document is labelled VISIBILITY-UNESTABLISHED."""
    for where in ("legend", "rule"):
        assert _verdict(_rules_doc(where), "R1") == "CARRIED-ASSUMED"
    rep = dc.run_document("asimov-laws", dc.MemTree({
        "usecases/asimov-laws/rules.ve": 'Rule 1. Every robot is classified as "careful".\n',
        "usecases/asimov-laws/environment.json": json.dumps(ENV),
        "usecases/asimov-laws/source.md": "x\n"}))
    assert rep["visibility"] == "VISIBILITY-UNESTABLISHED"


def test_t5_open_term_factor_and_header_and_constant_table():
    """An open-term factor (.ve.md) is never shown; in the counter format a '## ' header and a constant table in
    vocabulary.py are never shown either, while the used predicate's legend is CARRIED."""
    fm = {"format": "ve-document@1", "environment": {"vocabulary": ENV["vocabulary"]},
          "open_terms": [{"name": "caution", "arguments": ["robot"], "factors": [DEF]}],
          "units": [{"id": "u1", "kind": "norm", "meaning": {"open": ["caution"]}, "span": [0, 1]}]}
    vemd = "---\n" + json.dumps(fm) + "\n---\nbody\n"
    doc = dc.build_doc("udhr-pilot", dc.MemTree({"usecases/udhr-pilot/run-20261010T1400Z/translation.ve.md": vemd}))
    assert doc.rules["u1"]["terms"] == ["caution", "robot"]
    assert _verdict(doc, "u1") == "UNSHOWN"
    assert _verdict(_counter_doc("header"), "b1") == "UNSHOWN"
    assert _verdict(_counter_doc("table"), "b1") == "UNSHOWN"
    assert _verdict(_counter_doc("legend"), "b1") == "CARRIED"


def _counter_doc(where, text=DEF, source_bytes=1000):
    env = json.loads(json.dumps(ENV))
    head = "## b1 | always | 1.1" + (" " + text if where == "header" else "")
    rules = head + '\nEvery robot is classified as "careful".\n## b2 | always | 1.2\nEvery robot is spare.\n'
    if where == "legend":
        env["vocabulary"]["predicates"]["careful"]["description"] += " " + text
    if where == "elsewhere":
        env["vocabulary"]["predicates"]["spare"]["description"] += " " + text
    vocab = 'LEVELS = {"robbie": "' + (text if where == "table" else "Robbie") + '"}\n'
    pins = {"sources": {"safety-framework": {"path": "nowhere/fsf.txt", "text_bytes": source_bytes,
                                             "text_sha256": "0" * 64}}}
    return dc.build_doc("safety-framework", dc.MemTree({
        "usecases/safety-framework/rules.d1.ve": rules, "usecases/safety-framework/facts.d1.ve": "",
        "usecases/safety-framework/environment.d1.json": json.dumps(env),
        "usecases/safety-framework/vocabulary.py": vocab, "usecases/pinned_sources.json": json.dumps(pins)}))


def test_t5_elsewhere_and_oversize():
    """Whole on the legend of a predicate only another block uses: ELSEWHERE. Carried, but in a block whose prompt
    (pinned source bytes + the unit render) exceeds ARG_LIMIT 131000: OVERSIZE."""
    assert _verdict(_counter_doc("elsewhere"), "b1") == "ELSEWHERE"
    big = _counter_doc("legend", source_bytes=dc.ARG_LIMIT)
    assert big.rules["b1"]["oversize"] and _verdict(big, "b1") == "OVERSIZE"
    assert not _counter_doc("legend", source_bytes=dc.ARG_LIMIT - 5000).rules["b1"]["oversize"]


def test_fragment_partial_and_not_carried():
    doc = _rules_doc("legend", text="A careful robot checks every step.")
    assert _verdict(doc, "R1", DEF) == "FRAGMENT"
    doc = _rules_doc("legend", text="twice before it moves; a careful robot checks every step")
    assert _verdict(doc, "R1", "A careful robot checks every step, twice before it moves.") == "PARTIAL"
    assert _verdict(_rules_doc("none"), "R1") == "NOT CARRIED"


@pytest.mark.parametrize("source, carrier", [
    ("A robot’s “care” rule holds.", "A robot's \"care\" rule holds."),           # curly quotes
    ("A careful robot is cata-\nstrophically slow.", "A careful robot is catastrophically slow."),  # line-break hyphen
    ("A careful robot checks every step.", "A careful robot (1.3.2) checks every step."),  # citation strip
    ("Operators: Companies that build products.", "**Operators:** Companies that build products."),  # bold lead-in
])
def test_t9_equivalences_carry(source, carrier):
    doc = _rules_doc("legend", text=carrier)
    assert _verdict(doc, "R1", source) == "CARRIED-ASSUMED"
    assert dc.source_norm(source) in dc.source_norm(carrier)


# ----------------------------------------------------------------------------------------------- detectors (b), (c) ---
def test_marker_grep_hits_definitions_lead_ins_and_table_rows():
    text = ("Intro line.\n\"Partner\" means a member of a couple. Other text.\n**Operators:** Companies that build.\n"
            "| Level | Description |\n|---|---|\n| SL2 | Baseline security |\n")
    hits = dc.marker_grep("s.md", text)
    kinds = [(h["line"], h["marker"]) for h in hits]
    assert (2, "means") in kinds and (3, "lead-in") in kinds and (6, "table-row") in kinds
    assert ["partner"] in dc.defined_phrases(hits[0]["passage"], hits[0]["marker"])


def test_lexical_matcher_finds_phrases_inside_identifiers_f3():
    """Detector (c), aliases off: F3's predicate name holds "safety case" and "CCL"."""
    doc = _counter_doc("legend")
    doc.declare("governance_found_acceptable_with_safety_case_where_ccl_reached", "predicate", {})
    idx = dc.lexical_index(doc)
    for phrase in ("Safety Cases", "CCL"):
        hits = dc.lexical_match(idx, dc.phrase_tokens(phrase))
        assert ("governance_found_acceptable_with_safety_case_where_ccl_reached", None, "name") in hits, phrase
    assert dc.lexical_match(idx, dc.phrase_tokens("careful"), single_word_legends=False) == [("careful", None, "name")]


def test_lexical_bar_on_the_known_cases():
    """Section 5 bar: 100% of known (entry, term) pairs whose phrase occurs as tokens in the term's identifier or
    legend are linked; the rest are alias-only and listed in the REPORT."""
    r = dc.lexical_recall_trees(FIXTURE, repo=ROOT)
    eligible = [x for x in r if x["eligible"]]
    assert eligible and all(x["found"] for x in eligible), [x for x in eligible if not x["found"]]
    assert any(x["term"] == "governance_found_acceptable_with_safety_case_where_ccl_reached" for x in eligible)


@pytest.mark.parametrize("variant", [
    "A\u00a0careful robot checks every step.",        # NBSP
    "A careful\trobot checks  every step.",           # tab, double space
    "A careful robot\r\nchecks every step.",          # CR LF
    "A CAREFUL ROBOT checks every step.",              # case
])
def test_source_norm_whitespace_and_case_variants_carry(variant):
    assert dc.source_norm(variant) == dc.source_norm("A careful robot checks every step.")


def test_source_norm_keeps_distinct_letters_distinct():
    """NFKC folds the Kelvin sign to K; a dotted capital I is not folded to i (conservative: no silent widening)."""
    assert dc.source_norm("\u212a level") == dc.source_norm("K level")
    assert dc.source_norm("\u0130tem") != dc.source_norm("Item")


@pytest.mark.parametrize("bad", ["7", "true", "null", "[]", "{}", '{"vocabulary": []}', '{"vocabulary": {"predicates": 7}}',
                                 '{"vocabulary": {"predicates": {"careful": 7}}}', '{"units": {"u1": 1}}',
                                 '{"rules": {"R1": {}}}', '{"rules": [{"id": 7}, {"id": "R1", "gloss": 7, "source": []}]}'])
def test_malformed_inputs_never_crash_and_never_pass(bad):
    """Every JSON input replaced by a scalar, a list, an empty object or a mistyped node: each document still reports
    (problems listed, no exception), and a definition stays not carried."""
    for name, path in (("asimov-laws", "usecases/asimov-laws/environment.json"),
                       ("udhr-pilot", "usecases/udhr-pilot/run-20261010T1400Z/translation.ve.md"),
                       ("eligibility", "usecases/eligibility/rules.json"),
                       ("safety-framework", "usecases/safety-framework/environment.d1.json")):
        text = "---\n" + bad + "\n---\nbody\n" if path.endswith(".ve.md") else bad
        files = {path: text, "usecases/asimov-laws/rules.ve": 'Rule 1. Every robot is classified as "careful".\n',
                 "usecases/safety-framework/rules.d1.ve": "## b1 | always | 1\nEvery robot is careful.\n",
                 "usecases/eligibility/environment.json": bad}
        rep = dc.run_document(name, dc.MemTree(files), known=[
            {"case": "k", "doc": name, "rule": "R1", "term": "careful", "passages": [{"text": DEF}]}])
        assert rep["known"][0]["verdict"] not in dc.PASSING


def test_every_use_case_is_checked_or_named_out_of_scope():
    """A new document under usecases/ fails here until it gets an adapter (DOCS) or an out-of-scope reason."""
    dirs = {p.name for p in (ROOT / "usecases").iterdir() if p.is_dir() and not p.name.startswith(("_", "."))}
    assert dirs == set(dc.DOCS) | set(dc.OUT_OF_SCOPE)
    assert len(dc.DOCS) == 15 and len(dc.OUT_OF_SCOPE) == 5


# ------------------------------------------------------------------------------------------------------- selection ---
def test_selection_shared_input_selects_every_reader():
    """Codex B11: an edit to a shared input selects every document that reads it; the checker, the pinned counter code
    and the known-case fixture select all."""
    assert dc.select_documents(["usecases/asimov-laws/source.md"]) == ["asimov-extended", "asimov-laws"]
    assert dc.select_documents(["usecases/asimov-extended/rules.ve"]) == ["asimov-extended"]
    for p in dc.SELECT_ALL:
        assert dc.select_documents([p]) == sorted(dc.DOCS)
    assert dc.select_documents(["docs/unrelated.md"]) == []
    assert "eligibility" in dc.select_documents(["usecases/eligibility/source/wfp-print.txt"])


def test_unparsed_rules_print_the_full_set_and_candidates():
    fm = {"format": "ve-document@1", "environment": {"vocabulary": ENV["vocabulary"]}, "open_terms": [],
          "units": [{"id": "u1", "kind": "norm", "meaning": "specified", "span": [0, 1]}]}
    tree = dc.MemTree({"usecases/udhr-pilot/run-20261010T1400Z/translation.ve.md": "---\n" + json.dumps(fm) + "\n---\nx\n"})
    rep = dc.run_document("udhr-pilot", tree)
    [u] = rep["unparsed"]
    assert u["rule"] == "u1" and u["dependencies"] == "unknown: any of the document's 4 declared terms"
    assert set(u["candidates"]) == {"careful", "spare", "robbie", "robot"}


# ----------------------------------------------------------------------------------------------------- report mode ---
def _tiny_checkout(root):
    for path, text in {
        "usecases/asimov-laws/rules.ve": 'Rule 1. Every robot is classified as "careful".\n',
        "usecases/asimov-laws/environment.json": json.dumps(ENV),
        "usecases/asimov-laws/source.md": '"Careful" means that a careful robot checks every step twice.\n',
    }.items():
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_text(text, encoding="utf-8")
    known = {"cases": [{"case": "k1", "doc": "asimov-laws", "rule": "R1", "term": "careful", "row": "k",
                        "passages": [{"file": "usecases/asimov-laws/source.md", "text": DEF}]}]}
    (root / "known.json").write_text(json.dumps(known), encoding="utf-8")


def test_report_mode_exits_0_with_findings(tmp_path):
    """The tool exits 0 when it finds definitions not carried (report mode: it never fails a build or a gate)."""
    _tiny_checkout(tmp_path)
    out = tmp_path / "rep.json"
    r = subprocess.run([sys.executable, "-I", str(ROOT / "tools" / "defs_carried.py"), "--root", str(tmp_path),
                        "--doc", "asimov-laws", "--known", str(tmp_path / "known.json"), "--json", str(out),
                        "--summary-dir", str(tmp_path / "sum")],
                       capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert r.returncode == 0, r.stderr
    rep = json.loads(out.read_text(encoding="utf-8"))
    doc = rep["documents"]["asimov-laws"]
    assert doc["known"][0]["verdict"] == "NOT CARRIED" and doc["known"][0]["hit"]
    assert doc["findings_by_verdict"] and sum(doc["findings_by_verdict"].values()) >= 1
    assert rep["mode"] == "report" and "exit 0" in r.stdout
    assert (tmp_path / "sum" / "asimov-laws.txt").read_text(encoding="utf-8").startswith("asimov-laws (rules.ve)")


# ------------------------------------------------------------------------------------------------- counter byte pin ---
def test_the_counter_code_is_a_byte_copy_of_the_pinned_source():
    """Each copied piece of tools/defs_carried_counter.py hashes to the record taken from the counter's file."""
    pin = json.loads((DATA / "counter_pin.json").read_text(encoding="utf-8"))
    raw = (ROOT / "tools" / "defs_carried_counter.py").read_bytes()
    lines = raw.decode("utf-8").splitlines(keepends=True)
    pieces = {}
    for nd in ast.parse(raw).body:
        name = getattr(nd, "name", None) or (nd.targets[0].id if isinstance(nd, ast.Assign)
                                            and isinstance(nd.targets[0], ast.Name) else None)
        if name:
            pieces[name] = hashlib.sha256("".join(lines[nd.lineno - 1:nd.end_lineno]).encode()).hexdigest()
    want = {k: v["sha256"] for f in pin["files"] for k, v in f["pieces"].items()}
    assert len(want) == 11
    assert {k: pieces.get(k) for k in want} == want
    assert pin["files"][0]["sha256"] == "d618d963fcccbc443a33a83dea88c408a59e578f7c143d725ce02ef380d801dc"
