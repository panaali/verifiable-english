"""The Lean `document` mode (lean-first batch 16a) against Python's `load_document` and `check_document` wrapper.

Each finding of the 16a review is a class here, with its regression cases: the checks the mode lacked (B2), the
profile and JSON gates that must run first and fail closed (B3), Python against Lean on every seed document with
nonzero residual counts (B4; the mutants are `tools/difffuzz.py`'s `document` surface), the fault order (C1), and
the Python crashes the comparison found (C5 and its class). The Python switch is batch 16b.
"""
from __future__ import annotations

from copy import deepcopy
import json

import pytest

from conformance import document_wrapper as dw
from conformance.p0 import VOCAB, envelope, environment
from ve.backends.lean_service import CheckerUnavailable, LeanService


def document(source, units, **extra):
    front = {"format": "ve-document@1", "environment": extra.pop("environment_json", environment()),
             "units": units, **extra}
    return "---\n" + json.dumps(front) + "\n---\n" + source


def unit(uid, span, *, kind="exposition", meaning="specified", support="none", **extra):
    return {"id": uid, "span": span, "kind": kind, "meaning": meaning,
            "support": support, **extra}


@pytest.fixture(scope="module")
def service():
    with LeanService() as instance:
        yield instance


def lean(service, text):
    return dw.lean_answers(service, [text])[0]


def both(service, text):
    """(Python's answer, Lean's answer) on one document text."""
    return dw.python_answer(text), lean(service, text)


def assert_same(service, text):
    python, answer = both(service, text)
    assert dw.verdict(python, answer) == "agree", (python, answer)
    return answer


def row(service, source, units, **extra):
    return service.run("document", [{"id": "d", "document": document(source, units, **extra)}])[0]


# ---------------------------------------------------------------- the structural wrapper

def test_utf8_partition_status_and_counts(service):
    source = "Café. Next.\n"
    cut = len("Café. ".encode())
    result = row(service, source, [
        unit("a", [0, cut], kind="asserted", support="assumption", content={"ast": ["top"]}),
        unit("b", [cut, len(source.encode())], kind=["unformalised", "future_profile"],
             meaning={"unformalised": "future_profile"}, status="UNFORMALISED")])
    assert result["status"] == "ok"
    assert result["coverage"] == {
        "source_bytes": len(source.encode()), "accounted_bytes": len(source.encode()),
        "coverage_percent": 100, "bytes_by_kind": {"asserted": cut,
                                                       "unformalised": len(source.encode()) - cut},
        "bytes_by_status": {"CHECKED": cut, "UNFORMALISED": len(source.encode()) - cut},
        "unformalised_reasons": {"future_profile": 1},
        "residual": {"open_terms": 0, "assumptions": 1, "bridge_leaves": 0,
                     "unresolved_reading_sets": 0}, "residual_total": 1}


def test_mixed_parent_counts_parts_once(service):
    parts = [unit("a", [0, 1], kind="asserted", content={"ast": ["top"]}, status="CHECKED"),
             unit("b", [1, 3], kind=["unformalised", "opaque"],
                  meaning={"unformalised": "opaque"}, status="UNFORMALISED")]
    result = row(service, "A B", [{"id": "parent", "span": [0, 3],
                                     "status": "MIXED", "parts": parts}])
    assert result["status"] == "ok"
    assert [u["parent_id"] for u in result["units"]] == ["parent", "parent"]
    assert result["coverage"]["accounted_bytes"] == 3
    assert sum(result["coverage"]["bytes_by_status"].values()) == 3


def test_gap_and_wrong_status_are_rejected(service):
    gap = row(service, "AB", [unit("a", [0, 1])])
    assert gap["status"] == "error"
    assert gap["error"] == "unit spans do not partition all source bytes"
    wrong = row(service, "AB", [unit("a", [0, 2], status="CHECKED")])
    assert wrong["status"] == "error"
    assert wrong["error"] == "unit status contradicts content, meaning, or active reading set"


# ---------------------------------------------------------------- B4: Python against Lean on every seed

# The seeds Lean must decide (no fail-closed answer): its owned profiles, every branch of the wrapper.
DECIDED = {"usecases/bluedot-grant/document.ve.md", "usecases/bluedot-grant/causal.ve.md", "plain", "mixed",
           "open-terms", "reading-sets", "graph-bridge", "graph-readings", "definitions", "p0-envelope",
           "alternatives-cells", "alternatives-graph", "risk"}
# The seeds it must refuse, each with the reason it names.
FAIL_CLOSED = {"usecases/news-article/news-w6a.ve.md": "order@0",
               "tests/data/readings_s2/constitution-nd-readings.ve.md": "norm-defaults@0",
               "fence": "surface parser"}


@pytest.fixture(scope="module")
def seed_answers(service):
    seeds = dw.seeds()
    answers = dw.lean_answers(service, [dw.text_of(doc) for _, doc in seeds])
    return {name: (doc, dw.python_answer(dw.text_of(doc)), answer) for (name, doc), answer in zip(seeds, answers)}


def test_every_seed_document_agrees_with_python_or_fails_closed(seed_answers):
    assert set(seed_answers) == DECIDED | set(FAIL_CLOSED)
    for name, (_, python, answer) in seed_answers.items():
        if name in DECIDED:
            assert dw.verdict(python, answer) == "agree", (name, python, answer)
            assert python["outcome"] == "ok", (name, python)
        else:
            assert python["outcome"] == "ok" or name == "fence", (name, python)
            assert answer["code"] == "CheckerUnavailable" and FAIL_CLOSED[name] in answer["text"], (name, answer)


def test_residual_counts_are_nonzero_and_python_s(seed_answers):
    """Each residual line the wrapper counts is nonzero on some seed, in Lean's answer and Python's alike, so a
    Lean that dropped a line (or counted it as 0) fails here."""
    residual = {name: seed_answers[name][2]["value"]["coverage"]["residual"] for name in DECIDED}
    assert residual["graph-bridge"]["bridge_leaves"] == 1
    assert residual["open-terms"]["open_terms"] == 2
    assert residual["reading-sets"]["unresolved_reading_sets"] == 2
    assert residual["usecases/bluedot-grant/document.ve.md"]["assumptions"] == 19
    for line in ("bridge_leaves", "open_terms", "unresolved_reading_sets", "assumptions"):
        assert any(r[line] for r in residual.values()), line


def test_composed_block_coverage_is_its_route_s_line(seed_answers):
    """B1's profile-specific coverage: an `alternatives@0` or `risk@0` document's coverage carries its block
    route's cells and residual counts (`Alternatives.Wire.coverage`, the call Python relays), each cell kind
    nonzero on some seed, and the risk route's on the risk seed."""
    cells = seed_answers["alternatives-cells"][2]["value"]["coverage"]
    assert [x["unit"] for x in cells["alternatives"]["alternatives_declared"]] == ["u0"]
    assert [x["unit"] for x in cells["alternatives"]["counterfactual_leaves"]] == ["u1"]
    assert [x["unit"] for x in cells["alternatives"]["proximate_judgments"]] == ["u2"]
    assert cells["residual"]["assumed_harm_free"] == 1 and cells["residual"]["table_complete"] == 1
    risk = seed_answers["risk"][2]["value"]["coverage"]
    assert risk["residual"]["alternatives_declared"] == 1 and risk["residual"]["counterfactual_leaves"] == 1
    assert "alternatives" not in seed_answers["plain"][2]["value"]["coverage"]


def test_reading_set_status_fold_follows_the_active_version(seed_answers):
    """An open latest version leaves its unit OPEN; an authored single assertion makes it CHECKED (Lean's
    `foldStatus`, Python's active-set loop)."""
    units = {u[0]: u[2] for u in seed_answers["reading-sets"][2]["value"]["units"]}
    assert units == {"a": "OPEN", "b": "CHECKED", "c": "LABELLED"}


def test_owned_profiles_are_the_lean_modes(service):
    """`document_wrapper.OWNED` is the set of profiles the Lean mode reads (`ownedProfiles`): every other
    profile of Python's registry is refused, by name, before its environment is decoded."""
    from ve.profiles import BY_NAME
    unowned = set()
    for profile in BY_NAME:
        env = envelope(VOCAB, sorted({profile, "relational-fol@0"}))
        answer = lean(service, document("A", [unit("a", [0, 1])], environment_json=env))
        if answer["outcome"] == "error" and f"document checks under {profile} need" in answer["text"]:
            unowned.add(profile)
    assert set(BY_NAME) - unowned == dw.OWNED


# ---------------------------------------------------------------- B2: the checks the mode lacked

def _sets_env():
    return envelope(VOCAB)


B2_CASES = {
    "asserted unit without content": (
        document("AB", [unit("a", [0, 2], kind="asserted")]),
        "asserted unit needs content or a reading set"),
    "unbound ve fence": (
        document("AB\n```ve x\ntrue.\n```\n", [unit("a", [0, 3])]), "unbound VE fence"),
    "couplings without rights": (
        document("AB", [unit("a", [0, 2])], couplings=[]),
        "UnsupportedProfile: rights@0 is required for couplings"),
    "completions without norm-defaults": (
        document("AB", [unit("a", [0, 2])], completions={}),
        "UnsupportedProfile: norm-defaults@0 is required for completions"),
    "bridges without reports": (document("AB", [unit("a", [0, 2])], bridges=[]), "unknown document metadata"),
    "contexts without reports": (document("AB", [unit("a", [0, 2])], contexts=[]), "unknown document metadata"),
    "invalid weights": (document("AB", [unit("a", [0, 2])], weights=[{"set": "s"}]),
                        "invalid removable reading weights"),
    "lemmas not a list": (document("AB", [unit("a", [0, 2])], lemmas={}), "lemmas must be a list"),
    "dangling narrowing": (
        document("AB", [unit("a", [0, 2])], narrowings=[
            {"id": "n", "set": "s", "version": 1, "keeps": ["r"], "by": "alice", "reason_spans": ["a"]}]),
        "narrowing cites unknown reading set version"),
}


@pytest.mark.parametrize("name", B2_CASES)
def test_review_b2_documents_python_rejects_are_rejected_with_its_text(service, name):
    text, message = B2_CASES[name]
    python, answer = both(service, text)
    assert python["outcome"] == "error" and python["text"] == message, python
    assert answer == {"outcome": "error", "code": python["code"], "text": message}


@pytest.mark.parametrize("graph", [7, [], {"root": "c"}, {"root": "c", "nodes": 7},
                                   {"root": "c", "nodes": [{"name": "c", "ast": ["top"],
                                                             "label": "bridge:accepts(alice,a)"}]}])
def test_a_graph_is_admitted_before_its_labels_are_counted(service, graph):
    """B2's graph: a malformed or unadmitted claim graph is a rejection, never `ok` with `bridge_leaves`
    counted from it (Python's `_report` admits it; C5: a non-object graph or node list is admission's
    diagnostic, not an AttributeError)."""
    text = document("AB", [unit("a", [0, 2], kind="asserted", content={"ast": ["top"]})], graph=graph)
    python, answer = both(service, text)
    assert python["outcome"] == "error" and answer["outcome"] == "error", (python, answer)
    assert dw.verdict(python, answer) in ("agree", "admission"), (python, answer)


# ---------------------------------------------------------------- B3: what the mode cannot decide fails closed

def test_profile_gate_runs_before_the_environment_decoder(service):
    """A profile the mode does not compose is refused as unavailable before any decoder reads the environment
    (B3: the plain envelope decoder rejected the alternatives and quantity documents with `fields do not
    match`), as is a unit-schema block, a legacy envelope and a `@2` document; an alternatives block is its
    own route's to decode, with that route's text."""
    env = envelope(VOCAB, ["norms@0", "relational-fol@0", "soft-norms@0"])
    env["soft_norms"] = {"anything": True}
    answer = lean(service, document("AB", [unit("a", [0, 2])], environment_json=env))
    assert answer["code"] == "CheckerUnavailable" and "soft-norms@0" in answer["text"], answer
    alternatives = envelope(VOCAB, ["alternatives@0", "norms@0", "relational-fol@0"])
    alternatives["alternatives"] = {"anything": True}
    python, answer = both(service, document("AB", [unit("a", [0, 2])], environment_json=alternatives))
    assert python["outcome"] == answer["outcome"] == "error" and dw.verdict(python, answer) != "differ", answer
    block = envelope(VOCAB, ["relational-fol@0", "time@0"])
    block["unit_schema"] = {}
    answer = lean(service, document("AB", [unit("a", [0, 2])], environment_json=block))
    assert answer["code"] == "CheckerUnavailable" and "unit_schema" in answer["text"], answer
    legacy = {"language": "ve.core@0", "profile": "relational-fol@0", "spec_revision": "x", "vocabulary": {}}
    assert lean(service, document("AB", [unit("a", [0, 2])], environment_json=legacy))["code"] == \
        "CheckerUnavailable"
    second = "---\n" + json.dumps({"format": "ve-document@2"}) + "\n---\nA"
    assert lean(service, second)["code"] == "CheckerUnavailable"


@pytest.mark.parametrize("extra", ['"x": null', '"x": -1', '"x": 1.5', '"x": 1e3', '"x": NaN', '"x": Infinity',
                                   '"x": "\\ud800"', '"x": 99999999999999999999', '"weights": [], "weights": []'])
def test_json_python_reads_and_the_document_reader_agrees(service, extra):
    """The document reader accepts standard JSON values; Python-only constants remain undecided."""
    front = ('{"format": "ve-document@1", "environment": ' + json.dumps(environment()) +
             ', "units": [{"id": "a", "span": [0, 2], "kind": "exposition", "meaning": "specified", '
             '"support": "none"}], ' + extra + '}')
    text = "---\n" + front + "\n---\nAB"
    json.loads(front)
    answer = lean(service, text)
    python = dw.python_answer(text)
    if extra in ('"x": NaN', '"x": Infinity'):
        assert answer["code"] == "CheckerUnavailable", answer
    else:
        assert dw.verdict(python, answer) == "agree", (extra, python, answer)


@pytest.mark.parametrize("front", ["{", '{"a": 01}', "{} x", "[1,]"])
def test_json_neither_reader_reads_is_invalid_in_both(service, front):
    text = "---\n" + front + "\n---\nAB"
    python, answer = both(service, text)
    assert python["text"] == answer["text"] == "invalid JSON front matter", (python, answer)


def test_json_nested_front_matter_matches_python(service):
    deep = "[" * 300 + "]" * 300
    text = document("AB", [unit("a", [0, 2])]).replace('"units":', '"weights": [{"set": 1, "by": 2, "values": '
                                                         + deep + '}], "units":', 1)
    python, answer = both(service, text)
    assert answer["text"] == "ResourceLimit: JSON depth exceeds 256", answer


# ---------------------------------------------------------------- C1: Python's fault order

def test_open_terms_are_checked_before_the_unit_list(service):
    text = document("AB", [], open_terms=7)
    assert assert_same(service, text)["text"] == "open_terms must be a list"


def test_a_status_contradiction_is_reported_after_every_unit_check(service):
    """C1: the explicit status is compared after the loop and the reading-set fold, so a later unit's schema
    fault is reported first, as Python does."""
    text = document("ABC", [unit("a", [0, 1], status="CHECKED"), {"id": "b"}])
    assert assert_same(service, text)["text"] == "invalid unit schema"


def test_the_unformalised_reason_is_checked_before_unformalised_content(service):
    text = document("AB", [unit("a", [0, 2], kind=["unformalised", "x"], meaning={"unformalised": "y"},
                                content={"ast": ["top"]})])
    assert assert_same(service, text)["text"] == "InvalidInput: unformalised kind reason does not match meaning of a"


def test_mixed_parts_are_compiled_one_by_one(service):
    """Python's `_parts` is a generator: a part is compiled before the next part's partition is read, so the
    first part's own fault comes before the second part's partition fault; a Boolean span start that Python
    compares equal to the cursor (`True == 1`) reaches the part's own span check."""
    parts = [unit("a", [1, 2], support="nobody", status="LABELLED"), {**unit("b", [5, 3]), "status": "LABELLED"}]
    text = document("XAB", [unit("x", [0, 1]), {"id": "p", "span": [1, 3], "status": "MIXED", "parts": parts}])
    assert assert_same(service, text)["text"] == "invalid support"
    boolean = [{**unit("a", [True, 2]), "status": "LABELLED"}, {**unit("b", [2, 3]), "status": "LABELLED"}]
    text = document("XAB", [unit("x", [0, 1]), {"id": "p", "span": [1, 3], "status": "MIXED", "parts": boolean}])
    assert assert_same(service, text)["text"] == "unit spans must partition every source byte in order"


@pytest.mark.parametrize("body, message", [
    ("AB\n```ve bad name\nx\n```\n```ve u\nunclosed\n", "invalid or duplicate VE fence"),
    ("AB\n```ve ü\nx\n```\n", "invalid VE fence name"),
    ("AB\n```ve u\nx\n```\n```ve u\ny\n```\n", "invalid or duplicate VE fence"),
    ("AB\n```ve u\nunclosed\n", "unclosed VE fence")])
def test_fences_are_read_left_to_right_with_python_s_texts(service, body, message):
    text = document(body, [unit("a", [0, 3])])
    assert assert_same(service, text)["text"] == message


# ---------------------------------------------------------------- the Python crashes the comparison found

@pytest.mark.parametrize("name, units", [
    ("MIXED without an id", [{"span": [0, 2], "status": "MIXED", "parts": []}]),
    ("unhashable part status", [{"id": "p", "span": [0, 2], "status": "MIXED", "parts": [
        {**unit("a", [0, 1]), "status": []}, {**unit("b", [1, 2]), "status": "LABELLED"}]}]),
    ("unhashable unit status", [unit("a", [0, 2], status={})])])
def test_malformed_units_are_diagnostics_in_both(service, name, units):
    python, answer = both(service, document("AB", units))
    assert python["outcome"] == "error", (name, python)
    assert dw.verdict(python, answer) == "agree", (name, python, answer)


def test_a_malformed_later_reading_is_a_diagnostic_not_a_key_error(service):
    from ve.environment import Environment
    from ve.identity import meaning_id
    from ve.ast import Top
    env = _sets_env()
    mid = meaning_id(Environment(deepcopy(env)), Top())
    first = {"id": "r", "kind": "asserted", "meaning_id": mid, "content": ["top"],
             "admission": {"who": "alice", "why": "w", "distinguishing_models": {"q": "m"}}}
    sets = [{"id": "s", "unit": "a", "version": 1, "status": "open", "readings": [first, {}]}]
    python, answer = both(service, document("AB", [unit("a", [0, 2])], environment_json=env, reading_sets=sets))
    assert python == answer == {"outcome": "error", "code": "InvalidInput",
                                "text": "each other reading needs a distinguishing model id"}


# ---------------------------------------------------------------- budgets and deadlines

def test_a_zero_request_budget_is_a_resource_limit_never_an_answer(service):
    text = json.dumps([{"id": "d", "document": document("AB", [unit("a", [0, 2])])}])
    _, response = service.exchange("document", text, 1, budget={"cases": 0})
    assert response["status"] == "error" and "ResourceLimit" in json.dumps(response), response
    assert "results" not in response


@pytest.mark.skipif(not __import__("pathlib").Path("/proc/self/stat").exists(), reason="CPU time from /proc")
def test_a_document_past_its_cpu_deadline_is_unavailable_never_ok(monkeypatch):
    """The mode's deadline covers the whole case (front matter, units, reading sets, graph admission): a
    deadline below what the bluedot document needs is `CheckerUnavailable`, never an answer."""
    from ve.backends import lean_service
    text = (dw.ROOT / "usecases/bluedot-grant/document.ve.md").read_text()
    monkeypatch.setitem(lean_service.DEADLINES, "document", (1e-4, 1e-4))
    with LeanService() as slow:
        with pytest.raises(CheckerUnavailable, match="mode document"):
            slow.run("document", [{"id": str(i), "document": text} for i in range(8)])


def test_python_document_diagnostics_carry_the_code_their_text_names():
    """A Python rejection on the document path whose text starts with a diagnostic code (`UnsupportedProfile:
    ...`) is raised with that code, as Lean's relayed text carries it: a plain `VEError` there reports
    `InvalidInput` beside an `UnsupportedProfile` text (the couplings and completions gates did). Read with
    Python's own parser."""
    import ast
    from ve.backends.relay import CLASSES
    for path in ("ve/document.py", "ve/readings.py"):
        tree = ast.parse((dw.ROOT / path).read_text())
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Raise) and isinstance(node.exc, ast.Call)
                    and isinstance(node.exc.func, ast.Name) and node.exc.func.id == "VEError" and node.exc.args):
                continue
            first = node.exc.args[0]
            text = (first.value if isinstance(first, ast.Constant) else
                    first.values[0].value if isinstance(first, ast.JoinedStr) and first.values
                    and isinstance(first.values[0], ast.Constant) else "")
            code = str(text).partition(":")[0]
            assert code == "InvalidInput" or code not in CLASSES, (path, node.lineno, text)
