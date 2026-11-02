"""me-2d-f2's saved delta (docs/math-evidence/me-2d-f2/evidence/delta.json, DELTA row D1, standing ruling R1): the
calc mode's refusal of the words "the" alone, read from the saved records; the head record is Lean's answer today."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from tests.lean_build import lean_build
from tests.subprocesses import HANG_TIMEOUT
from ve.backends.lean_service import LeanService

DELTA = json.loads((Path(__file__).resolve().parents[1] /
                    "docs/math-evidence/me-2d-f2/evidence/delta.json").read_text())


def kept(text: str) -> tuple[str, set[str]]:
    """R1's (a) to (c) for a calc refusal: its code, and the value's name and every quoted word it names."""
    return text.split(":", 1)[0], set(re.findall(r'"([^"]*)"', text)) | set(re.findall(r"words of (\w+)", text))


def test_the_head_keeps_the_base_s_code_names_and_quoted_words():
    base, head = DELTA["base"], DELTA["head"]
    assert base != head and base.keys() == head.keys() == {"status", "error"}  # no path, before or after
    code, names = kept(base["error"])
    assert code == "ValueWordsForm" and names == {"x", "the"}
    assert kept(head["error"]) == (code, names)


@pytest.fixture(scope="module")
def service():
    with LeanService(lean_build("ve_service") / "ve_service", timeout=HANG_TIMEOUT) as running:
        yield running


def test_the_saved_head_is_lean_s_answer(service):
    _, response = service.exchange("calc", json.dumps([DELTA["request"]]), 1, timeout=HANG_TIMEOUT)
    result = response["results"][0]["result"]
    assert {k: result[k] for k in DELTA["head"]} == DELTA["head"]
