"""The bound Python transport for VE.SpeechActs.Source.report."""
from __future__ import annotations

import copy
import json
import subprocess

import pytest

from test_speech_source_lean import templates
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
    monkeypatch.setattr("ve.backends.speech_source.subprocess.run", lambda *a, **k:
                        subprocess.CompletedProcess([], 0, json.dumps([result]).encode(), b""))
    with pytest.raises(CheckerUnavailable):
        decide_source(metadata, source)
