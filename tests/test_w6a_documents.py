"""W6a quantity documents: Lean admission (`ve_quantity` case `document`) against
Python early admission and Rust regeneration, the news-article document, the
whole-grammar English gate, and every provenance/binding rejection class."""
from collections import Counter
import copy
import json
from pathlib import Path
import re
import subprocess

import pytest

from tests import lean_routes

from tests.subprocesses import HANG_TIMEOUT
from tests.test_units_lean_w6a import LEAN, lean, rust
from tests.test_w6a_review_regressions import money, named, raw_environment
from ve.admission import admit_document
from ve.document import check_document, load_document, quantity_admission_input
from ve.environment import Environment
from ve.errors import AmbiguousDerivation, UnsupportedProfile, VEError
from ve.evaluate import evaluate
from ve.model import FiniteModel
from ve.readings import active_reading_sets
from ve.surface.time import parse_w6_sentence
from ve.units import core_formula, erased_environment, prove_quantity, quantity_meaning_id

ROOT = Path(__file__).resolve().parents[1]
NEWS = ROOT / "usecases" / "news-article"
pytestmark = pytest.mark.skipif(not lean_routes.SERVICE.exists(), reason="build the Lean service first")


def q(formula):
    return {"format": "ve-quantity@1", "formula": formula}


def doc_env():
    return raw_environment({"bp": {"scale": "100", "display": {"kind": "percent"}},
                            "usd_cent": money("USD", "$")},
                           {"low": named("bp", "the low rate"), "high": named("bp", "the high rate"),
                            "cost": named("usd_cent", "the cost"), "price": named("usd_cent", "the price")}) | {
        "profiles": ["documents@1", "order@0", "relational-fol@0", "time@0"]}


LOW = q(["eq", ["const", "bp", "low"], ["decimal", "bp", "3.75"]])
HIGH = q(["eq", ["const", "bp", "high"], ["decimal", "bp", "4.00"]])
ORDER = q(["lt", ["const", "bp", "low"], ["const", "bp", "high"]])


def base_document(env):
    certificate = prove_quantity(env, [LOW, HIGH], ORDER)
    return {"units": [{"id": "u_low", "span": [0, 10], "kind": "asserted", "content": LOW},
                      {"id": "u_high", "span": [10, 20], "kind": ["attributed", "fed", "says", "asserted"],
                       "content": HIGH}],
            "graph": {"root": "order", "nodes": [
                {"name": "low", "quantity": LOW, "unit": "u_low"},
                {"name": "high", "quantity": HIGH, "label": "bridge:accepts(fed,u_high)"},
                {"name": "order", "quantity": ORDER, "premises": ["low", "high"],
                 "certificate": certificate}]}}


def three_ways(raw, document):
    """Python admission, Lean admission and Rust regeneration of one document."""
    try:
        python = admit_document(Environment(raw), document)
    except VEError as exc:
        python = exc
    [got] = lean([{"id": "d", "kind": "document", "environment": raw, "document": document}])
    [other] = rust([{"id": "d", "kind": "quantity", "mode": "document", "environment": raw,
                     "document": document}])
    return python, got, other


def test_document_admission_agrees_three_ways():
    raw = doc_env()
    env = Environment(raw)
    document = base_document(env)
    python, got, other = three_ways(raw, document)
    assert got["status"] == "ok" and got["assurance"] == "lean-admitted", got
    assert got["report_id"] == python["report_id"] and got["report"] == python["report"]
    assert got["kinds"] == python["kinds"] == [u["kind"] for u in document["units"]]
    labels = [(a["name"], a.get("label", "asserted")) for a in got["report"]["assumptions"]]
    assert labels == [("low", "asserted"), ("high", "bridge:accepts(fed,u_high)")]
    # The report binds the annotated statements, not their erasures.
    assert got["report"]["root"]["meaning_id"] == quantity_meaning_id(env, ORDER)
    assert other["status"] == "ok" and other["assurance"] == "regeneration-only"
    assert other["node_meaning_ids"] == [quantity_meaning_id(env, x) for x in (LOW, HIGH, ORDER)]


def mutate(document, path, value):
    result = copy.deepcopy(document)
    target = result
    for key in path[:-1]:
        target = target[key]
    if value is DELETE:
        del target[path[-1]]
    else:
        target[path[-1]] = value
    return result


DELETE = object()
MONEY_LOW = q(["eq", ["const", "usd_cent", "cost"], ["decimal", "usd_cent", "3.75"]])


def rejection_cases(env):
    document = base_document(env)
    certificate = document["graph"]["nodes"][2]["certificate"]
    money_order = q(["lt", ["const", "usd_cent", "cost"], ["const", "usd_cent", "price"]])
    return [
        # A quoted unit's content used as the author's own assertion.
        ("quoted as asserted", mutate(document, ["graph", "nodes", 1],
                                      {"name": "high", "quantity": HIGH, "unit": "u_high"}),
         "quoted content of unit u_high is used without a bridge leaf"),
        # A leaf whose statement differs from its unit, by value and by tag.
        ("value differs", mutate(document, ["graph", "nodes", 0, "quantity"],
                                 q(["eq", ["const", "bp", "low"], ["decimal", "bp", "3.76"]])),
         "node low is not admitted under label asserted"),
        ("bridge to wrong agent", mutate(document, ["graph", "nodes", 1, "label"],
                                         "bridge:accepts(ecb,u_high)"),
         "node high is not admitted"),
        # Leaves the units-only layer never admits.
        ("background leaf", mutate(document, ["graph", "nodes", 0],
                                   {"name": "low", "quantity": LOW, "label": "background:literals"}),
         "not admitted"),
        ("open leaf undeclared", mutate(document, ["graph", "nodes", 0],
                                        {"name": "low", "quantity": LOW, "label": "open:vague"}),
         "node low is not admitted under label open:vague"),
        # Graph binding: order, dangling premises, relabelled or raw evidence.
        ("premises swapped", mutate(document, ["graph", "nodes", 2, "premises"], ["high", "low"]),
         "graph rejected"),
        ("dangling premise", mutate(document, ["graph", "nodes", 2, "premises"], ["low", "ghost"]),
         "graph rejected"),
        ("raw core certificate", mutate(document, ["graph", "nodes", 2, "certificate"], certificate["core"]),
         "Invalid quantity certificate"),
        ("relabelled to money", mutate(mutate(mutate(document, ["units", 0, "content"], MONEY_LOW),
                                              ["graph", "nodes", 0, "quantity"], MONEY_LOW),
                                       ["graph", "nodes", 2, "quantity"], money_order),
         "graph rejected"),
        ("root missing", mutate(document, ["graph", "root"], "absent"), "graph rejected"),
        ("duplicate name", mutate(document, ["graph", "nodes", 1, "name"], "low"), "graph rejected"),
        # A claimed Q that differs from regeneration.
        ("forged Q", mutate(document, ["graph", "nodes", 0, "quantity"],
                            {**LOW, "Q": ["eq", ["const", "bp", "low"], ["num", "bp", "376"]]}),
         "Q differs"),
        ("unit mismatch", mutate(document, ["units", 0, "content"],
                                 q(["eq", ["const", "bp", "low"], ["decimal", "usd_cent", "3.75"]])),
         "UnitMismatch(bp,usd_cent)"),
        # A citation needs a checked lemma (tests/test_w6a_citations.py has every class).
        ("cite without lemma", mutate(document, ["graph", "nodes", 0],
                                      {"name": "low", "quantity": LOW, "label": "cite:bundle/lemma"}),
         "node low is not admitted under label cite:bundle/lemma"),
        ("unchecked lemma", {**document, "lemmas": [{"name": "bundle/lemma", "conclusion": q(["top"]),
                                                     "leaves": []}]},
         "fields"),
    ]


@pytest.mark.parametrize("index", range(15))
def test_every_rejection_class_agrees(index):
    raw = doc_env()
    name, document, message = rejection_cases(Environment(raw))[index]
    python, got, _ = three_ways(raw, document)
    assert isinstance(python, VEError) and message in str(python), (name, python)
    assert got["status"] == "error" and message in got["error"], (name, got)


def test_rust_rejects_the_statement_classes():
    raw = doc_env()
    cases = {name: document for name, document, _ in rejection_cases(Environment(raw))}
    for name, message in (("forged Q", "Q differs"), ("unit mismatch", "UnitMismatch(bp,usd_cent)"),
                          ("unchecked lemma", "fields")):
        [other] = rust([{"id": name, "kind": "quantity", "mode": "document", "environment": raw,
                         "document": cases[name]}])
        assert other["status"] == "error" and message in other["error"]["message"], (name, other)


def test_documents_need_the_documents_profile_three_ways():
    raw = doc_env() | {"profiles": ["order@0", "relational-fol@0", "time@0"]}
    python, got, other = three_ways(raw, base_document(Environment(doc_env())))
    assert isinstance(python, UnsupportedProfile) and "documents@1" in str(python)
    assert "documents@1" in got["error"] and "documents@1" in other["error"]["message"]


def test_reading_choices_bind_and_must_agree():
    raw = doc_env()
    env = Environment(raw)
    readings = [q(["le", ["decimal", "bp", "3.75"], ["const", "bp", "low"]]),
                q(["eq", ["const", "bp", "low"], ["decimal", "bp", "3.75"]])]
    disjunction = q(["or", readings[0]["formula"], readings[1]["formula"]])
    lower = q(["le", ["decimal", "bp", "3.75"], ["const", "bp", "low"]])
    certificate = prove_quantity(env, [disjunction], lower)
    document = {"units": [{"id": "u", "span": [0, 5], "kind": "asserted"}],
                "reading_sets": [{"id": "rs", "version": 1, "readings": readings}],
                "graph": {"root": "c", "nodes": [
                    {"name": "all", "quantity": disjunction, "label": "readings:rs@1:all"},
                    {"name": "c", "quantity": lower, "premises": ["all"], "certificate": certificate}]}}
    python, got, other = three_ways(raw, document)
    assert got["status"] == "ok" and got["report_id"] == python["report_id"], got
    assert other["status"] == "ok"
    # Two different concrete choices of one set are incompatible.
    pair = q(["and", readings[0]["formula"], readings[1]["formula"]])
    both = {**document, "graph": {"root": "c", "nodes": [
        {"name": "r0", "quantity": readings[0], "label": "readings:rs@1:0"},
        {"name": "r1", "quantity": readings[1], "label": "readings:rs@1:1"},
        {"name": "c", "quantity": pair, "premises": ["r0", "r1"],
         "certificate": prove_quantity(env, readings, pair)}]}}
    python, got, _ = three_ways(raw, both)
    assert "incompatible reading choices" in str(python)
    assert "incompatible reading choices" in got["error"]
    # A readings leaf with content other than the chosen reading is not admitted.
    wrong = copy.deepcopy(document)
    wrong["graph"]["nodes"][0]["label"] = "readings:rs@1:0"
    python, got, _ = three_ways(raw, wrong)
    assert "not admitted" in str(python) and "not admitted" in got["error"]


# --- The news article --------------------------------------------------------

def news_document():
    path = NEWS / "news-w6a.ve.md"
    doc = load_document(path)
    active = active_reading_sets(doc["meta"].get("reading_sets", []))
    return path, doc, quantity_admission_input(doc, active)


def test_news_document_is_regenerated_deterministically():
    process = subprocess.run([str(ROOT / ".venv" / "bin" / "python"),
                              str(NEWS / "build_w6a_document.py"), "--check"], timeout=HANG_TIMEOUT)
    assert process.returncode == 0, "rerun usecases/news-article/build_w6a_document.py"


def test_news_document_is_admitted_by_lean_with_the_python_report():
    path, doc, admission = news_document()
    result = check_document(path)
    [got] = lean([{"id": "news", "kind": "document", "environment": doc["meta"]["environment"],
                   "document": admission}])
    assert got["status"] == "ok", got
    assert got["report_id"] == result["admission"]["core_report_id"]
    assert got["report"] == result["admission"]["report"]
    [other] = rust([{"id": "news", "kind": "quantity", "mode": "document",
                     "environment": doc["meta"]["environment"], "document": admission}])
    assert other["status"] == "ok"
    labels = {a.get("label", "asserted") for a in got["report"]["assumptions"]}
    assert "readings:first_target_year@1:all" in labels
    assert {"bridge:accepts(fomc,s6_range)", "bridge:accepts(warsh,s14_goal)"} <= labels


def test_news_document_partitions_the_pinned_source():
    import hashlib
    _, doc, _ = news_document()
    assert hashlib.sha256(doc["source"]).hexdigest() == \
        "b905818ecbc38c479a273d1503430745d1f2c9697215752572922ccedd73545b"
    result = check_document(NEWS / "news-w6a.ve.md")
    coverage = result["coverage"]
    assert coverage["source_bytes"] == coverage["accounted_bytes"] == 5448
    assert sum(coverage["bytes_by_status"].values()) == 5448
    checked = {u["id"] for u in doc["units"] if u["status"] == "CHECKED"}
    assert checked == {"s1_date", "s2_range", "s6_range", "s7_goal", "s11_pce", "s12_target",
                       "s13_growth", "s13_unemployment", "s14_goal"}
    # Residuals stay visible: missing operands, the count, vague degrees, the
    # projection horizon and the unresolved reading of "not ... until".
    reasons = coverage["unformalised_reasons"]
    for reason in ("missing_old_range", "count_exceeds_bound", "missing_previous_expectation",
                   "vague_degree", "vague_timelier", "vague_pledge_manner"):
        assert reasons.get(reason) == 1
    assert coverage["residual"]["open_terms"] == 1
    assert coverage["residual"]["unresolved_reading_sets"] == 1
    statuses = {u["id"]: u["status"] for u in doc["units"]}
    assert statuses["s6_years"] == "OPEN" and statuses["s12_year"] == "OPEN"


def test_news_report_is_not_vacuous_in_the_fixture_model():
    """The fixture model satisfies every report assumption and the root, by
    Lean's budgeted evaluation of the regenerated cores."""
    _, doc, _ = news_document()
    raw = doc["meta"]["environment"]
    env = Environment(raw)
    model = json.loads((NEWS / "w6a-quantity-fixtures.json").read_text())["model"]
    result = check_document(NEWS / "news-w6a.ve.md")
    claims = [result["admission"]["report"]["root"], *result["admission"]["report"]["assumptions"]]
    got = lean([{"id": c["name"], "environment": raw, "quantity": c["quantity"], "model": model}
                for c in claims])
    assert all(g["status"] == "ok" and g["value"] is True for g in got), got
    target = erased_environment(env)
    finite = FiniteModel.from_dict(target, model)
    assert all(evaluate(target, core_formula(env, c["quantity"])[1], finite, trace=False).value
               for c in claims)


# --- Whole-grammar English and strict fences ------------------------------------

def grammar_env():
    return Environment(raw_environment(None, sorts={"item": {"description": "an item"}}, predicates={
        "p": {"arguments": ["item"], "description": "p", "verbalisation": "{0} is sealed"}},
        constants={"box": {"sort": "item", "description": "box"},
                   "n": {"sort": "$int", "description": "n", "verbalisation": "n"},
                   "rate": named("bp", "the rate")}))


@pytest.mark.parametrize("sentence,formula", [
    ("box is sealed.", ["unary", "p", ["const", "box"]]),
    ("Every item is sealed.", ["forall", "item", ["unary", "p", ["var", 0]]]),
    # Both grammars read it; the admitted readings are one statement.
    ("n is less than 3.", ["lt", ["const", "dimensionless", "n"], ["num", "dimensionless", "3"]]),
    ("The rate is less than 3.00%.", ["lt", ["const", "bp", "rate"], ["num", "bp", "300"]]),
])
def test_whole_grammar_reads_each_sentence_once(sentence, formula):
    assert parse_w6_sentence(grammar_env(), sentence)["formula"] == formula


def test_frozen_grammar_readings_pass_annotated_admission():
    # The frozen grammar reads a bare numeral; against a bp constant that is a
    # dimensionless literal, which annotated admission rejects.
    with pytest.raises(VEError, match="UnitMismatch"):
        parse_w6_sentence(grammar_env(), "The rate is less than 3.")


def test_readings_from_two_grammars_are_ambiguous():
    # "b" names constant a in the quantity wordings and constant b in the frozen
    # grammar: two admitted statements, so the sentence rejects.
    env = Environment(raw_environment({}, constants={
        "a": {"sort": "$int", "description": "a", "verbalisation": "b"},
        "b": {"sort": "$int", "description": "b"}}))
    with pytest.raises(AmbiguousDerivation, match="across the English grammar"):
        parse_w6_sentence(env, "b is less than 3.")


def write_document(tmp_path, units, fences=""):
    raw = doc_env()
    meta = {"format": "ve-document@1", "environment": raw, "units": units}
    path = tmp_path / "doc.ve.md"
    source = "The low rate is 3.75%. More."
    path.write_text("---\n" + json.dumps(meta) + "\n---\n" + source + "\n" + fences)
    return path


def test_fences_and_ast_content_go_through_annotated_admission(tmp_path):
    fence = "```ve u\nThe low rate equals 3.75%.\n```\n"
    unit = {"id": "u", "span": [0, 22], "kind": "asserted", "meaning": "specified", "support": "testimony",
            "content": {"fence": "u"}, "surface": "english"}
    rest = {"id": "r", "span": [22, 29], "kind": "exposition", "meaning": {"unformalised": "filler"},
            "support": "none"}
    doc = load_document(write_document(tmp_path, [unit, rest], fence))
    assert doc["units"][0]["content"] == {"format": "ve-quantity@1", "traces": [],
                                          "formula": ["eq", ["const", "bp", "low"], ["num", "bp", "375"]]}
    assert doc["units"][0]["status"] == "CHECKED"
    # Legacy-shaped ast content is dimensionless source input: against a bp
    # constant it rejects instead of bypassing the tag.
    ast_unit = {**unit, "content": {"ast": ["lt", ["const", "low"], ["num", "400"]]}}
    del ast_unit["surface"]
    with pytest.raises(VEError, match="UnitMismatch"):
        load_document(write_document(tmp_path, [ast_unit, rest]))
    quantity_unit = {**ast_unit, "content": {"quantity": q(["lt", ["const", "bp", "low"],
                                                           ["decimal", "bp", "4.00"]])}}
    assert load_document(write_document(tmp_path, [quantity_unit, rest]))["units"][0]["meaning_id"] == \
        quantity_meaning_id(Environment(doc_env()), quantity_unit["content"]["quantity"])
    # A claimed meaning id must be the annotated one.
    forged = {**quantity_unit, "meaning_id": "0" * 64}
    with pytest.raises(VEError, match="meaning id"):
        load_document(write_document(tmp_path, [forged, rest]))


def test_news_coverage_table_matches_its_rows_and_the_run():
    text = (NEWS / "coverage-w6a.md").read_text()
    labels = re.findall(r"^\| (\d+b?) \| .*? \| (DIRECT|REIFIED|OPAQUE|NO) \|", text, re.M)
    counts = {label: sum(1 for _, x in labels if x == label)
              for label in ("DIRECT", "REIFIED", "OPAQUE", "NO")}
    assert len(labels) == 27
    assert (f"27 rows" in text and f"{counts['DIRECT']} DIRECT,\n{counts['REIFIED']} REIFIED, "
            f"{counts['OPAQUE']} OPAQUE, {counts['NO']} NO." in text), counts
    assert {row for row, x in labels if x == "DIRECT"} == {"1", "7", "13", "21", "22", "23"}
    result = check_document(NEWS / "news-w6a.ve.md")
    statuses = result["coverage"]["bytes_by_status"]
    for status in ("CHECKED", "OPEN", "UNFORMALISED"):
        assert f"| {status} | {statuses[status]:,} |" in text
    leaves = {(a["name"], a.get("label", "asserted")) for a in result["admission"]["report"]["assumptions"]}
    kinds = Counter(label.split(":")[0] for _, label in leaves)
    assert kinds == {"asserted": 2, "bridge": 6, "readings": 1}


# --- W8 input: witnesses in document terms --------------------------------------

def test_witnesses_render_with_units_restored_and_read_back():
    """Every rendered value, put in the approved `equals` wording, parses back to
    exactly the model's coordinate with its tag."""
    from ve.surface.time import parse_quantity_sentence, render_quantity_witness
    fixture = json.loads((NEWS / "w6a-quantity-fixtures.json").read_text())
    env = Environment(fixture["environment"])
    model = copy.deepcopy(fixture["model"])
    model["constants"]["first_projected_target_year"] = "2030"  # the S12 distinguishing model
    lines = render_quantity_witness(env, model)
    assert "The first projected target year is calendar year 2030." in lines
    assert "The new target lower bound is 3.75%." in lines
    assert "The decision date is 2026-09-16." in lines
    names = {d.verbalisation: n for n, d in env.constants.items()}
    for line in lines:
        words, value = line[:-1].split(" is ", 1)
        name = names[words] if words in names else names[words[:1].lower() + words[1:]]
        parsed = parse_quantity_sentence(env, f"{words} equals {value}.")
        tag = env.constants[name].unit
        assert parsed["formula"] == ["eq", ["const", tag, name],
                                     ["num", tag, model["constants"][name]]], line
    outside = copy.deepcopy(fixture["model"])
    outside["constants"]["decision_date"] = "-1"
    assert "The decision date is day number -1 (outside 1970-01-01 to 9999-12-31)." in \
        render_quantity_witness(env, outside)
