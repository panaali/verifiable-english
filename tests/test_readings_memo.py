"""Process-local readings admission memo through the real Lean service and Python relay."""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path

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
