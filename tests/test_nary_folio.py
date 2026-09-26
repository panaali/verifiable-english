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
    assert {kind: sum(message.startswith(kind) for message in result["failures"].values())
            for kind in ("Unexpected token", "free variable", "predicate signature collision",
                         "shadowed variable")} == {
        "Unexpected token": 10, "free variable": 11,
        "predicate signature collision": 5, "shadowed variable": 1}
    assert set(result["failures"]) == {
        "e1010:c", "e1025:c", "e1045:c", "e1094:c", "e821:c", "e963:c", "e969:c",
        "e975:c", "e980:c", "e981:c", "s119:p2", "s143:p2", "s148:p0",
        "s162:p4", "s241:p1", "s330:p4", "s330:p5", "s362:p2", "s362:p4",
        "s364:p1", "s367:p3", "s367:p4", "s368:p4", "s368:p6", "s372:p6",
        "s422:p5", "s447:p4"}
    assert result["frozen_sample"] == {
        "baseline_direct_fit": 26, "new_nary_ids": ["e532:c", "s367:p0"],
        "new_direct_fit": 28, "sample_size": 30,
    }
