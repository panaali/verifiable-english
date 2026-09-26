"""Pinned FOLIO witness accounting, with the large corpus optional in CI."""
import json

import pytest

from conformance.nary_folio import ROOT, direct_parse, report


def test_frozen_sample_new_nary_witnesses():
    sample = json.loads((ROOT / "experiments/E0/survey_samples/_drawn/folio.json").read_text())
    rows = {row["id"]: row for row in sample["sample"]}
    for id_ in ("e532:c", "s367:p0"):
        assert direct_parse(rows[id_]["fol"]).endswith(".\n")


def test_full_nary_folio_accounting_when_corpus_is_available():
    if not (ROOT / "data/folio/tasksource_folio_v2_train.jsonl").exists():
        pytest.skip("optional pinned FOLIO v2 corpus is not downloaded")
    result = report()
    assert result["nary_pairs"] == 216
    assert result["direct_parses"] == 189
    assert len(result["failures"]) == 27
    assert result["frozen_sample"] == {
        "baseline_direct_fit": 26, "new_nary_ids": ["e532:c", "s367:p0"],
        "new_direct_fit": 28, "sample_size": 30,
    }
