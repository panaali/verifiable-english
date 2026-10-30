"""Process-local readings admission memo through the real Lean service and Python relay."""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import pytest

from ve.backends.lean_service import LeanService

CASE = json.loads((Path(__file__).parent / "data/readings_memo/choice.json").read_text())


def choice(document=None, environment=None, *, component="rs_a", index=0):
    case = copy.deepcopy(CASE)
    case["choice"] = [[component, index]]
    case["component"] = component
    if document is not None:
        case["document"] = document
    if environment is not None:
        case["environment"] = environment
    return case


def stats(service):
    _, stderr = service.stderr()
    lines = [line for line in stderr.splitlines() if line.startswith("readings_memo ")]
    assert lines, stderr
    return {name: int(value) for name, value in re.findall(r"(admissions|hits|entries|bytes)=(\d+)", lines[-1])}


def test_memo_hit_answer_equals_fresh_service(monkeypatch):
    monkeypatch.setenv("VE_READINGS_MEMO_STATS", "1")
    first, second = choice(index=0), choice(index=1)
    with LeanService(allow_unlisted_build=True) as kept:
        assert kept.run("readings-route", [first])[0]["status"] == "ok"
        hit = kept.run("readings-route", [second])[0]
        assert stats(kept)["hits"] == 1
    with LeanService(allow_unlisted_build=True) as fresh:
        cold = fresh.run("readings-route", [second])[0]
        assert stats(fresh)["admissions"] == 1
    assert hit == cold


def test_memo_key_contains_document_environment_and_kind(monkeypatch):
    monkeypatch.setenv("VE_READINGS_MEMO_STATS", "1")
    original = choice()
    changed_document = copy.deepcopy(original)
    changed_document["document"]["units"][0]["id"] = "u0_other"
    changed_environment = copy.deepcopy(original)
    changed_environment["environment"]["vocabulary"]["sorts"]["memo"] = {"description": "memo"}
    changed_kind = {**original, "kind": "readings-elaborate", "id": "readings-elaborate"}
    with LeanService(allow_unlisted_build=True) as service:
        for case in (original, changed_document, changed_environment, changed_kind):
            assert service.run("readings-route", [case])[0]["status"] == "ok"
        assert stats(service)["admissions"] == 4
        assert stats(service)["hits"] == 0
        service.run("readings-route", [original])
        assert stats(service)["hits"] == 1


def test_memo_evicts_oldest_entry_at_count_bound(monkeypatch):
    monkeypatch.setenv("VE_READINGS_MEMO_STATS", "1")
    original = choice()
    with LeanService(allow_unlisted_build=True) as service:
        for i in range(5):
            case = copy.deepcopy(original)
            case["document"]["units"][0]["id"] = f"u0_{i}"
            assert service.run("readings-route", [case])[0]["status"] == "ok"
            assert stats(service)["entries"] <= 4
            assert stats(service)["bytes"] <= 2097152
        assert stats(service)["admissions"] == 5
        oldest = copy.deepcopy(original)
        oldest["document"]["units"][0]["id"] = "u0_0"
        service.run("readings-route", [oldest])
        assert stats(service)["admissions"] == 6
        assert stats(service)["hits"] == 0


def test_second_choice_does_not_readmit(monkeypatch):
    monkeypatch.setenv("VE_READINGS_MEMO_STATS", "1")
    with LeanService(allow_unlisted_build=True) as service:
        assert service.run("readings-route", [choice(index=0)])[0]["status"] == "ok"
        assert stats(service)["admissions"] == 1
        assert service.run("readings-route", [choice(index=1)])[0]["status"] == "ok"
        assert stats(service)["admissions"] == 1
        assert stats(service)["hits"] == 1


SITUATION = "803302a4a75368f270db9cbaf56d7a7b39d4f0c5d28ec455645d8227de0df7d3"
CLOSE = {"checker_version": "ve-tableau-checker@2", "environment_id": "-", "premise_meaning_ids": [],
         "conclusion_meaning_id": "-", "trace": {"rule": "close"}}
FIELDS = {"readings-separate": {"set": "rs_a", "situation": SITUATION, "other": "asks"},
          "readings-certificate": {"certificate": CLOSE},
          "readings-dead": {"set": "rs_a", "index": 0, "certificate": CLOSE},
          "readings-model": {"model": {"complete": True, "domains": {"agent": ["a"]}, "constants": {}, "relations": {}}},
          "readings-verdicts": {"question": "conflict", "evidence": []}}
KINDS = ("readings-validate", "readings-elaborate", "readings-conflict", "readings-certificate", "readings-model",
         "readings-dead", "readings-verdicts")


def named(kind, component):
    case = {**choice(component="rs_a"), "kind": kind, "id": kind}
    if component is None:
        del case["component"]
    else:
        case["component"] = component
    case.update(FIELDS.get(kind, {}))
    return case


# Every kind on the shared hit path, on `main` (S1 for validate and separate, S2 otherwise) and on the companion sets
# (admitted under the completion), and the per-case answers of validate and elaborate (review F1's sweep).
SWEEP = [named(k, c) for k in KINDS for c in ("main", "rs_a", "rs_b")] + [
    named("readings-validate", None), named("readings-elaborate", None), named("readings-separate", "rs_a"),
    named("readings-separate", "main"), choice(component="rs_b"), choice(component="main")]
# The cases Lean refuses after their admission, which a hit reaches the same way.
REFUSED = {"readings-model-main", "readings-model-rs_a", "readings-model-rs_b", "readings-verdicts-main",
           "readings-separate-main", "readings-choice-main"}


@pytest.mark.parametrize("case", SWEEP, ids=[f"{c['kind']}-{c.get('component', 'unnamed')}" for c in SWEEP])
def test_a_hit_admits_nothing_on_every_kind_consecutive_and_batched(monkeypatch, request, case):
    """`admissions` counts runs of the admission itself (`admitComponentsMemo`'s `admit`), not misses."""
    monkeypatch.setenv("VE_READINGS_MEMO_STATS", "1")
    with LeanService(allow_unlisted_build=True) as service:
        [cold] = service.run("readings-route", [case])
        assert cold["status"] == ("error" if request.node.callspec.id in REFUSED else "ok"), cold
        assert (stats(service)["admissions"], stats(service)["hits"]) == (1, 0)
        [warm] = service.run("readings-route", [case])
        assert (stats(service)["admissions"], stats(service)["hits"]) == (1, 1)
        assert service.run("readings-route", [case, case]) == [cold, cold]
        assert (stats(service)["admissions"], stats(service)["hits"]) == (1, 3)
    assert warm == cold


def test_a_case_refused_after_its_admission_keeps_it(monkeypatch):
    monkeypatch.setenv("VE_READINGS_MEMO_STATS", "1")
    refused = choice(component="absent")
    with LeanService(allow_unlisted_build=True) as service:
        assert service.run("readings-route", [refused])[0]["status"] == "error"
        assert (stats(service)["admissions"], stats(service)["entries"]) == (1, 1)
        assert service.run("readings-route", [choice()])[0]["status"] == "ok"
        assert (stats(service)["admissions"], stats(service)["hits"]) == (1, 1)


def charged(case):
    """The bytes the memo charges for a case: its kind, environment and document as compact JSON."""
    triple = [case["kind"], case["environment"], case["document"]]
    return len(json.dumps(triple, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())


def padded(size, tag="memo"):
    """A case whose charged bytes are exactly `size`: an unused sort's description pads the environment."""
    case = choice()
    case["environment"]["vocabulary"]["sorts"][tag] = {"description": ""}
    case["environment"]["vocabulary"]["sorts"][tag]["description"] = "x" * (size - charged(case))
    assert charged(case) == size
    return case


def test_memo_charges_each_entry_its_serialized_bytes(monkeypatch):
    monkeypatch.setenv("VE_READINGS_MEMO_STATS", "1")
    first, second = choice(), named("readings-validate", None)
    with LeanService(allow_unlisted_build=True) as service:
        service.run("readings-route", [first])
        assert stats(service)["bytes"] == charged(first)
        service.run("readings-route", [second])
        assert stats(service)["bytes"] == charged(first) + charged(second)


@pytest.mark.parametrize("size, kept", [(2097152, True), (2097153, False)])
def test_an_entry_over_the_byte_bound_is_answered_but_not_kept(monkeypatch, size, kept):
    monkeypatch.setenv("VE_READINGS_MEMO_STATS", "1")
    case = padded(size)
    with LeanService(allow_unlisted_build=True) as service:
        [cold] = service.run("readings-route", [case])
        assert cold["status"] == "ok"
        assert (stats(service)["entries"], stats(service)["bytes"]) == ((1, size) if kept else (0, 0))
        assert service.run("readings-route", [case]) == [cold]
        assert (stats(service)["admissions"], stats(service)["hits"]) == ((1, 1) if kept else (2, 0))


@pytest.mark.parametrize("count, evicted", [(2, False), (3, True)])
def test_entries_over_the_aggregate_byte_bound_evict_the_oldest(monkeypatch, count, evicted):
    """Three entries of 0.8 MiB exceed 2 MiB together, two do not; the entry count bound is four."""
    monkeypatch.setenv("VE_READINGS_MEMO_STATS", "1")
    cases = [padded(838861, tag=f"memo{i}") for i in range(count)]
    with LeanService(allow_unlisted_build=True) as service:
        for case in cases:
            assert service.run("readings-route", [case])[0]["status"] == "ok"
        assert stats(service)["entries"] == count - evicted
        assert stats(service)["bytes"] == 838861 * (count - evicted)
        service.run("readings-route", [cases[0]])
        assert (stats(service)["admissions"], stats(service)["hits"]) == (count + evicted, 1 - evicted)
