"""Soft-document handles (kb-10e): a `soft-selected` case names its document by handle and is answered
from the document the service prepared once.

The obligation (`VE.Service.softResult_cached`): the answer by handle is the answer of the same case with
the document's environment and norms written out, byte for byte. Two documents that differ in one rule's
guard and three models, alternating, are asked both ways; so are captured RSP and Preparedness cases. A
handle the process does not hold is a bound `CheckerUnavailable` request error, after which the client
registers the document again and retries once; every other case naming a soft document is refused.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from tests.lean_build import lean_build
from tests.test_soft_norms_lean import env, norm, should
from tests.test_soft_selected import EXCEPTION, EXTRA, MODEL, QUERIES, RULES
from ve import soft_route
from ve.backends.lean_service import HANDLE_KEY, SOFT_HANDLE_KEY, UNHANDLED_MODES, LeanService, case_digest
from ve.softnorms import SoftEnvironment, SoftNormDocument

# Handle reuse between requests is what the answer store's lines leave out (tests/answer_store.py).
pytestmark = pytest.mark.live_service

ROOT = Path(__file__).resolve().parents[1]
CAPTURED = ROOT / "docs/kernel/kb-10e/cases"

# Document B: document A (tests/test_soft_selected.py) with the strict rule's guard `w` in place of `v`.
RULES_B = [norm("h", "x_required", True, guard=("unary", "w", ["var", 0]))] + RULES[1:]
MODELS = [MODEL,
          {**MODEL, "relations": {**MODEL["relations"], "v": [["a"], ["c"]], "w": [["b"]]}},
          {**MODEL, "relations": {**MODEL["relations"], "v": [], "w": [["e"]], "s": [["a"]],
                                  "soft__excepted__d": [["a"]]}}]


@pytest.fixture(scope="module")
def executable():
    return lean_build("ve_service") / "ve_service"


def compact(value) -> str:
    """A result as the service writes it: compact, in its own key order."""
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def alternating() -> list[dict]:
    environment = env(extra=EXTRA)
    documents = [RULES, RULES_B]
    return [{"id": f"c{i}", "kind": "soft-selected", "environment": environment, "norms": documents[i % 2],
             "model": MODELS[i % 3], "queries": QUERIES} for i in range(20)]


def results(service: LeanService, cases: list, *, one_by_one: bool) -> list[str]:
    if one_by_one:
        return [compact(service.run("soft-norms", [case])[0]) for case in cases]
    return [compact(row) for row in service.run("soft-norms", cases)]


@pytest.mark.parametrize("one_by_one", [True, False], ids=["one-call-per-case", "one-request"])
def test_twenty_alternating_cases_answer_the_same_bytes_by_handle_and_written_out(executable, one_by_one):
    cases = alternating()
    sent: list[bytes] = []
    with LeanService(executable, handles=True) as handled, LeanService(executable, handles=False) as inline:
        handled.start()
        original = handled._write_all
        handled._write_all = lambda data, deadline: (sent.append(data), original(data, deadline))[1]
        by_handle = results(handled, cases, one_by_one=one_by_one)
        written = results(inline, cases, one_by_one=one_by_one)
        stats = dict(handled.stats)
    assert by_handle == written
    assert all('"status":"ok"' in row for row in written)
    # The two documents answer differently: an answer from the wrong entry would show.
    assert written[0] != written[3] and written[1] != written[4]
    # Each document was registered once, and every case named its document, never its environment.
    assert stats["registered"] == 2 and stats["handle_resends"] == 0 and stats["handle_reregistered"] == 0
    assert all(SOFT_HANDLE_KEY.encode() in line and HANDLE_KEY.encode() not in line for line in sent)
    norms_text = compact(RULES).encode()
    assert sum(norms_text in line for line in sent) == 1


@pytest.mark.parametrize("name", ["pf-case-1", "pf-case-3", "rsp-case-1"])
def test_captured_safety_framework_cases_answer_the_same_bytes(executable, name):
    case = json.loads((CAPTURED / f"{name}.json").read_text())
    with LeanService(executable, handles=True) as handled, LeanService(executable, handles=False) as inline:
        first, again = (compact(handled.run("soft-norms", [case])[0]) for _ in range(2))
        written = compact(inline.run("soft-norms", [case])[0])
        assert handled.stats["registered"] == 1
    assert first == again == written and '"status":"ok"' in written


def test_the_relay_answers_a_document_by_handle(executable, monkeypatch):
    """`selected_at` through the default pool: its case goes by handle, and its answer is the written-out one."""
    document = SoftNormDocument(SoftEnvironment(env(extra=EXTRA)), RULES_B)
    by_handle = soft_route.selected_at(document, MODELS[1], QUERIES)
    case = {"id": "soft-selected", "kind": "soft-selected", "environment": document.env.to_dict(),
            "norms": [rule.to_dict() for rule in document.rules], "model": MODELS[1], "queries": QUERIES}
    with LeanService(executable, handles=False) as inline:
        [row] = inline.run("soft-norms", [case])
    assert by_handle == soft_route.bind_selected(row, case)


def test_a_model_for_another_document_is_not_answered_from_this_one(executable):
    """Document C adds a default rule with an exception, so its models carry a decision predicate document A
    lacks. C's case sent by handle is C's answer; A's document with C's model is refused by Lean's model
    decoder, so a client that named A's document for C's case (seeded bug (c)) could not pass."""
    environment = env(extra=EXTRA)
    rules_c = RULES + [should("q", "x_required", True, exception=EXCEPTION)]
    model_c = copy.deepcopy(MODEL)
    model_c["relations"]["soft__excepted__q"] = [["a"], ["e"]]
    case_a = {"id": "a", "kind": "soft-selected", "environment": environment, "norms": RULES, "model": MODEL,
              "queries": QUERIES[:2]}
    case_c = dict(case_a, id="c", norms=rules_c, model=model_c)
    with LeanService(executable, handles=True) as handled, LeanService(executable, handles=False) as inline:
        by_handle = [compact(row) for row in handled.run("soft-norms", [case_a, case_c])]
        written = [compact(row) for row in inline.run("soft-norms", [case_a, case_c])]
        [crossed] = inline.run("soft-norms", [dict(case_a, id="c", model=model_c)])
    assert by_handle == written and all('"status":"ok"' in row for row in written)
    assert crossed["status"] == "error"


def _document(case: dict) -> tuple[str, str]:
    text = compact({"environment": case["environment"], "norms": case["norms"]})
    return case_digest(text), text


def test_a_lost_document_is_registered_again_and_retried_once(executable):
    """The client believes the process holds a document it does not: the request is a bound
    `CheckerUnavailable` request error, the client registers the document again and retries once."""
    case = alternating()[0]
    digest, _ = _document(case)
    with LeanService(executable, handles=False) as inline:
        expected = compact(inline.run("soft-norms", [case])[0])
    with LeanService(executable) as service:
        service.start()
        service._registered[digest] = 1
        assert compact(service.run("soft-norms", [case])[0]) == expected
        assert service.stats["handle_reregistered"] == 1 and service.stats["handle_resends"] == 0
        assert digest in service._registered
        assert compact(service.run("soft-norms", [case])[0]) == expected
        assert service.stats["handle_reregistered"] == 1 and service.stats["registered"] == 1


def _raw(service: LeanService, mode: str, cases: list, environments: dict | None = None) -> dict:
    text = "[" + ",".join(compact(c) for c in cases) + "]"
    return service.exchange(mode, text, len(cases), environments=environments)[1]


def test_a_handle_the_process_does_not_hold_is_a_bound_request_error(executable):
    named = {"id": "t", "kind": "soft-selected", SOFT_HANDLE_KEY: "a" * 64, "model": MODEL, "queries": QUERIES}
    with LeanService(executable) as service:
        response = _raw(service, "soft-norms", [named])
    assert response["status"] == "error" and response["code"] == "CheckerUnavailable"
    assert response["error"] == f"CheckerUnavailable: soft document handle {'a' * 64} is not registered"


@pytest.mark.parametrize("mode, edit", [
    ("soft-norms", {"kind": "soft-elaborate"}),
    ("soft-norms", {"environment": {"profiles": []}}),
    ("soft-norms", {"norms": []}),
    ("soft-norms", {HANDLE_KEY: "b" * 64}),
    ("soft-norms", {SOFT_HANDLE_KEY: 7}),
    ("norms", {}),
], ids=["another-kind", "with-environment", "with-norms", "with-environment-handle", "not-a-string",
        "another-mode"])
def test_any_other_case_naming_a_soft_document_is_refused(executable, mode, edit):
    case = alternating()[0]
    digest, text = _document(case)
    named = {"id": "t", "kind": "soft-selected", SOFT_HANDLE_KEY: digest, "model": MODEL, "queries": QUERIES}
    named.update(edit)
    with LeanService(executable) as service:
        response = _raw(service, mode, [named], {digest: text})
    assert response["status"] == "ok"
    [entry] = response["results"]
    assert entry["result"]["status"] == "error" and entry["code"] == "InvalidInput"
    assert entry["result"]["error"].startswith(f"InvalidInput: {SOFT_HANDLE_KEY} names a soft document only")


def _route_corpus() -> dict[str, list[dict]]:
    """The recorded corpus of every route answer kind (`tests/data/route-cases.jsonl`), by mode."""
    corpus: dict[str, list[dict]] = {}
    for line in (ROOT / "tests/data/route-cases.jsonl").read_text().splitlines():
        mode, case = json.loads(line)
        corpus.setdefault(mode, []).append(json.loads(case) if isinstance(case, str) else case)
    return corpus


STRAY = [("soft-norms", "rsp-case-1", json.loads((CAPTURED / "rsp-case-1.json").read_text())),
         ("soft-norms", "soft-selected-written-out", alternating()[0]),
         *((mode, f"route-corpus-{mode}", cases) for mode, cases in sorted(_route_corpus().items()))]


@pytest.mark.parametrize("mode, cases", [(m, c) for m, _, c in STRAY], ids=[name for _, name, _ in STRAY])
def test_a_stray_soft_document_handle_refuses_a_case_main_answered(executable, mode, cases):
    """Review F1 (DELTA row 4, SIGNED by the DRI 2026-11-14): main ignored `soft_document_handle` and answered the
    case in full; in every mode `expandCases` reaches, a case naming it outside the handle form of `soft-selected`
    is now the case error InvalidInput. English and risk-eval (`UNHANDLED_MODES`) are not reached: their answer
    stays the answer without the member. The first case of the mode the service answers is the one asked."""
    cases = cases if isinstance(cases, list) else [cases]
    stray = "0" * 64
    with LeanService(executable) as service:
        plain = _raw(service, mode, cases[:8])
        assert plain["status"] == "ok", plain
        answered = [i for i, row in enumerate(plain["results"]) if row["result"].get("status") != "error"]
        assert answered, plain["results"]
        case = cases[answered[0]]
        response = _raw(service, mode, [{**case, SOFT_HANDLE_KEY: stray}])
    assert response["status"] == "ok", response
    [entry] = response["results"]
    if mode in UNHANDLED_MODES:
        assert entry["result"] == plain["results"][answered[0]]["result"]
        return
    assert entry["code"] == "InvalidInput" and entry["result"]["status"] == "error"
    assert entry["result"]["error"].startswith(f"InvalidInput: {SOFT_HANDLE_KEY} names a soft document only")


def test_the_handshake_states_the_soft_member(executable):
    with LeanService(executable) as service:
        service.start()
        assert service.handshake["handles"]["soft_member"] == SOFT_HANDLE_KEY == "soft_document_handle"
