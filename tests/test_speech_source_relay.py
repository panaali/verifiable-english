"""The bound Python transport for VE.SpeechActs.Source.report."""
from __future__ import annotations

import copy
import json
import subprocess

import pytest

from test_speech_source_lean import base_env, done_document, judged, nominated, templates
from ve.backends import lean as lean_backend
from ve.backends.speech_source import decide_source
from ve.errors import CheckerUnavailable, VEError


def sample():
    _, metadata, source = templates()[0]
    return metadata, source


def test_source_report_comes_from_lean():
    metadata, source = sample()
    result = decide_source(metadata, source)
    assert result["status"] == "ok"
    assert result["document_id"] and sum(result["coverage"]["bytes_by_class"].values()) == len(source.encode())


def test_source_rejection_keeps_leans_code_and_text():
    metadata, source = sample()
    with pytest.raises(VEError) as caught:
        decide_source({**metadata, "format": "wrong"}, source)
    assert caught.value.message == "unsupported document format"


@pytest.mark.parametrize("mutation", ["id", "document_id", "coverage"])
def test_source_transport_fails_closed_on_tampered_report(monkeypatch, mutation):
    metadata, source = sample()
    result = copy.deepcopy(decide_source(metadata, source))
    if mutation == "id":
        result["id"] = "other"
    elif mutation == "document_id":
        result["document_id"] = False
    else:
        result["coverage"]["bytes_by_class"]["C"] = False
    monkeypatch.setattr("ve.backends.lean.run_limited", lambda *a, **k:
                        subprocess.CompletedProcess([], 0, json.dumps([result]).encode(), b""))
    with pytest.raises(CheckerUnavailable):
        decide_source(metadata, source)


def test_every_producer_field_is_required_and_typed(monkeypatch):
    metadata, source = sample()
    result = decide_source(metadata, source)
    original = lean_backend.run_limited
    try:
        for field in result.keys() - {"id", "status"}:
            for kind in ("drop", "retype"):
                tampered = copy.deepcopy(result)
                if kind == "drop":
                    del tampered[field]
                else:
                    value = tampered[field]
                    tampered[field] = [] if type(value) is dict else {} if type(value) is list else False
                monkeypatch.setattr("ve.backends.lean.run_limited", lambda *a, row=tampered, **k:
                                    subprocess.CompletedProcess([], 0, json.dumps([row]).encode(), b""))
                with pytest.raises(CheckerUnavailable):
                    decide_source(metadata, source)
    finally:
        monkeypatch.setattr("ve.backends.lean.run_limited", original)


@pytest.mark.parametrize("case,mutation", [
    ("polar", "document_id_same_shape"),
    ("polar", "source_id_same_shape"),
    ("polar", "environment_id_same_shape"),
    ("polar", "scope_with_rehashed_environment"),
    ("polar", "overclaimed_checked_coverage"),
    ("polar", "underclaimed_checked_coverage"),
    ("answered", "unknown_question"),
    ("answered", "boolean_answer"),
    ("answered", "missing_answer"),
    ("certified", "wrong_query"),
    ("certified", "duplicate_answer"),
    ("certified", "wrong_unit_id"),
    ("certified", "shifted_unit_bytes"),
    ("external", "wrong_command"),
    ("nomination", "wrong_nomination_question"),
    ("gap", "boolean_gap_status"),
])
def test_report_records_are_typed_and_bound_to_the_request(monkeypatch, case, mutation):
    examples = {name: (meta, source) for name, meta, source in templates()}
    if case == "external":
        metadata, source = done_document(base_env())
    elif case == "nomination":
        metadata, source = nominated([{"question": "r", "by": "alice", "support": "testimony",
                                      "nominate": 1}])
    elif case == "gap":
        metadata, source = judged(base_env())
    else:
        metadata, source = examples[case]
    result = copy.deepcopy(decide_source(metadata, source))
    if mutation == "document_id_same_shape":
        result["document_id"] = "0" * 64
    elif mutation == "source_id_same_shape":
        result["source_id"] = "0" * 64
    elif mutation == "environment_id_same_shape":
        result["environment_id"] = "0" * 64
    elif mutation == "scope_with_rehashed_environment":
        from ve.environment import Environment
        result["scope"]["task"] = "other"
        result["environment_id"] = Environment({**metadata["environment"],
                                                 "speech_acts": result["scope"]}).environment_id
    elif mutation in {"overclaimed_checked_coverage", "underclaimed_checked_coverage"}:
        unit_row = result["units"][0]
        old_status, old_class = unit_row["status"], unit_row["class"]
        new_status, new_class = (("CHECKED", "C") if mutation == "overclaimed_checked_coverage"
                                 else ("OPEN", "R"))
        # The totals remain internally consistent; only the source can refute this claim.
        if (old_status, old_class) == (new_status, new_class):
            new_status, new_class = ("OPEN", "R") if new_status == "CHECKED" else ("CHECKED", "C")
        unit_row["status"], unit_row["class"] = new_status, new_class
        result["coverage"]["bytes_by_status"] = {}
        result["coverage"]["bytes_by_class"] = {}
        for unit_row in result["units"]:
            for field, key in (("bytes_by_status", "status"), ("bytes_by_class", "class")):
                counts = result["coverage"][field]
                counts[unit_row[key]] = counts.get(unit_row[key], 0) + unit_row["bytes"]
    elif mutation == "unknown_question":
        result["answers"][0]["question"] = "absent"
    elif mutation == "boolean_answer":
        result["answers"][0]["answer"] = True
    elif mutation == "missing_answer":
        del result["answers"][0]["answer"]
    elif mutation == "wrong_query":
        result["answers"][1]["query"] = "absent"
    elif mutation == "duplicate_answer":
        result["answers"].append(copy.deepcopy(result["answers"][0]))
    elif mutation == "wrong_unit_id":
        result["units"][0]["id"] = "absent"
    elif mutation == "shifted_unit_bytes":
        result["units"][0]["bytes"] += 1
        result["units"][1]["bytes"] -= 1
        result["coverage"]["bytes_by_class"]["C"] = sum(
            unit["bytes"] for unit in result["units"] if unit["class"] == "C")
        result["coverage"]["bytes_by_status"]["CHECKED"] = sum(
            unit["bytes"] for unit in result["units"] if unit["status"] == "CHECKED")
    elif mutation == "wrong_command":
        result["compliance"][0]["command"] = "absent"
    elif mutation == "wrong_nomination_question":
        result["nominations"][0]["question"] = "absent"
    elif mutation == "boolean_gap_status":
        result["answers"][0]["status"] = True
    monkeypatch.setattr("ve.backends.lean.run_limited", lambda *a, **k:
                        subprocess.CompletedProcess([], 0, json.dumps([result]).encode(), b""))
    with pytest.raises(CheckerUnavailable):
        decide_source(metadata, source)


def test_every_report_record_field_rejects_type_confusion(monkeypatch):
    cases = [next((meta, source) for name, meta, source in templates() if name == "certified"),
             judged(base_env()), done_document(base_env()),
             nominated([{"question": "r", "by": "alice", "support": "testimony", "nominate": 1}])]
    original = lean_backend.run_limited
    try:
        for metadata, source in cases:
            report = decide_source(metadata, source)
            for field in ("answers", "nominations", "compliance"):
                for index, record in enumerate(report[field]):
                    for key in record:
                        tampered = copy.deepcopy(report)
                        tampered[field][index][key] = False
                        monkeypatch.setattr("ve.backends.lean.run_limited", lambda *a, row=tampered, **k:
                                            subprocess.CompletedProcess([], 0, json.dumps([row]).encode(), b""))
                        with pytest.raises(CheckerUnavailable):
                            decide_source(metadata, source)
                        monkeypatch.setattr("ve.backends.lean.run_limited", original)
    finally:
        monkeypatch.setattr("ve.backends.lean.run_limited", original)


@pytest.mark.parametrize("name,metadata,source", templates(), ids=lambda case: case if isinstance(case, str) else None)
def test_every_coverage_class_is_bound_to_the_source(monkeypatch, name, metadata, source):
    report = decide_source(metadata, source)
    for index in range(len(report["units"])):
        tampered = copy.deepcopy(report)
        unit = tampered["units"][index]
        unit["status"], unit["class"] = (("OPEN", "R") if unit["status"] == "CHECKED"
                                           else ("CHECKED", "C"))
        for field, key in (("bytes_by_status", "status"), ("bytes_by_class", "class")):
            counts = {}
            for item in tampered["units"]:
                counts[item[key]] = counts.get(item[key], 0) + item["bytes"]
            tampered["coverage"][field] = counts
        monkeypatch.setattr("ve.backends.lean.run_limited", lambda *a, row=tampered, **k:
                            subprocess.CompletedProcess([], 0, json.dumps([row]).encode(), b""))
        with pytest.raises(CheckerUnavailable):
            decide_source(metadata, source)
        monkeypatch.undo()


def test_residual_coverage_is_bound_to_open_terms_and_active_sets(monkeypatch):
    metadata, source = sample()
    report = copy.deepcopy(decide_source(metadata, source))
    report["coverage"]["residual"]["open_terms"] += 1
    monkeypatch.setattr("ve.backends.lean.run_limited", lambda *a, **k:
                        subprocess.CompletedProcess([], 0, json.dumps([report]).encode(), b""))
    with pytest.raises(CheckerUnavailable):
        decide_source(metadata, source)
