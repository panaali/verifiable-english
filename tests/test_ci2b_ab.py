"""ci-2b's saved A/B over the pinned command corpus (docs/commands-imperatives/ci-2b/evidence/ab.json): the evidence R1
and DRI 2026-10-28 item 2(a) ask for, read from the saved file only. Every sentence the base refused is still refused
(its code and quoted names kept) or read as `many`; no wording the base read reads differently."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/commands-imperatives/ci-2b/evidence"


def _ab():
    spec = importlib.util.spec_from_file_location("ci2b_ab", EVIDENCE / "ab.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_saved_ab_has_no_forbidden_row():
    ab, saved = _ab(), json.loads((EVIDENCE / "ab.json").read_text())
    assert ab.problems(saved) == []
    assert saved["corpus_sha256"] == hashlib.sha256((EVIDENCE / "corpus.json.gz").read_bytes()).hexdigest()
    assert saved["rows"] > 20_000 and not saved["tree_dirty"]
    assert ab.problems({"rows": 0, "counts": {}, "changed": []})  # an empty corpus fails
    assert {row["class"] for row in saved["changed"]} == {"R1", "b2", "many"}


def test_a_lost_code_or_quoted_name_or_new_reading_fails_the_check():
    ab, saved = _ab(), json.loads((EVIDENCE / "ab.json").read_text())
    r1 = next(row for row in saved["changed"] if row["class"] == "R1" and "'" in row["base"]["text"])
    for edit in ({"text": "InvalidInput: no single speech-act reading"},
                 {"text": r1["head"]["text"].replace("'", '"')}):
        forged = copy.deepcopy(saved)
        row = next(r for r in forged["changed"] if r == r1)
        row["head"] = {**row["head"], **edit}
        row["class"] = ab.classify(row["base"], row["head"])
        assert ab.problems(forged) and row["class"] == "code"
    forged = copy.deepcopy(saved)
    many = next(row for row in forged["changed"] if row["class"] == "many")
    many["head"] = {"outcome": "one", "command": {"act": "x"}}
    assert ab.problems(forged)
