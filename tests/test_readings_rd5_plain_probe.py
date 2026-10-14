"""A pair separated on a plain regulated predicate gets E24 (readings-defaults RD-5).

The UDHR's entitlement readings make a plain regulated predicate true of every person ("Everyone has the right to
…"), and the situation that separates such a reading from a State's duty probes that predicate. E19 words a duty or
a permission only, so before RD-5 Python's English raised on such a pair and the whole report was
`CheckerUnavailable`. The pair now gets E24, the existing sentence for a checked separation VE cannot yet show in
words; a pair probed on a duty keeps E19.
"""
from __future__ import annotations

import pytest

from tests import lean_routes
from tests.test_document import unit, write_doc
from tests.test_readings_nd_lean import environment, regulated
from tests.test_readings_s1_lean import entry, norm, reading, reading_set, situation_id
from ve.document import _environment, check_document
from ve.readings import s1_content_meaning_id
from ve.readings_english import E24

TEXT = b"Everyone has the right to recognition.\n"


@pytest.fixture(scope="module", autouse=True)
def lean():
    if not lean_routes.SERVICE.exists():
        pytest.skip("the Lean service has not been built")


def env():
    return environment({
        "entitled": {"arguments": ["person"], "description": "plain", "verbalisation": "{0} is entitled",
                     "regulated": {"role": "plain", "default": "unspecified"}},
        "recognise_required": {"arguments": ["state", "person"], "description": "obligation",
                               "regulated": regulated("obligation", "unspecified", "{0} recognise {1}")}},
        ("person", "state"))


def document(tmp_path, probe, witness):
    raw = env()
    base = {"domains": {"person": ["p"], "state": ["s"]}, "constants": {},
            "relations": {"unsaid__entitled": [], "unsaid__recognise_required": []}}
    sigma = entry(base, witness, {"outcome": probe}, True)
    sid = situation_id(raw, sigma)
    readings = [reading("entitlement", norm("u-entitlement", "entitled", True), {"claim": sid}),
                reading("claim", norm("u-claim", "recognise_required", True), {"entitlement": sid})]
    rs = reading_set("rs_u", "u", readings, {sid: sigma})
    environment_ = _environment(raw)
    for r in rs["readings"]:
        r["meaning_id"] = s1_content_meaning_id(environment_, "rs_u", r)
    return write_doc(tmp_path, TEXT, [unit("u", 0, len(TEXT), "norm")], environment_json=raw, reading_sets=[rs])


def pairs(path):
    report = check_document(path)["readings"]
    return [(p["wording"], p["text"]) for s in report["sets"] for p in s["pairs"]]


def test_a_pair_probed_on_a_plain_predicate_gets_e24(tmp_path):
    path = document(tmp_path, {"predicate": "entitled", "tuple": ["p"]}, "entitlement")
    assert pairs(path) == [("E24", E24)]


def test_a_pair_probed_on_a_duty_keeps_e19(tmp_path):
    path = document(tmp_path, {"predicate": "recognise_required", "tuple": ["s", "p"]}, "claim")
    got = pairs(path)
    assert [w for w, _ in got] == ["E19"]
    assert all("still must" in text for _, text in got)
