"""srccov-anthropic-rsp-1119: the RSP source text the coverage map found missing is carried word for word, and the
units it found out of scope with no record are recorded.

Carries. Each kept row of the map (reviews/source-coverage-1119/rows-anthropic-rsp.tsv in manage-agents) appends
source text to a legend the reader is shown: the description of a predicate or a threshold constant in
usecases/anthropic-rsp/environment.d1.json (written by rsp_vocabulary.py), or the description of a changelog date
constant in D3 (stage0.date_environment()). A run is a list of byte ranges of the pinned source text; the ranges skip
the PDF's footnote markers and bullet signs and are joined with one space. Each run, after the project's quote
normalisation (usecases/safetyfw_accounting.py `norm`), must occur in the legend byte for byte. With the pinned text
stored, the test reads it (tests/pinned_source.py); without it, it checks that the legend holds a run with the
recorded SHA-256 and length of that normalised text (the repository keeps hashes, not the text).

Records. Each recorded unit (S-ids of the map's units-anthropic-rsp.tsv) lies inside a spans.json unit whose kind
says it is not a rule: a heading (`meta`) or a hope with no commitment (`unformalised`, reason `hope`).
"""
import hashlib
import json

import test_rsp_fidelity_fix as fix
import test_safetyfw_usecases as base
from tests.pinned_source import pinned_source

RSP = base.RSP

# (map row, vocabulary section, symbol, runs); a run is ([(map unit, start byte, end byte), ...], the SHA-256 and
# the byte length of its normalised text). Row 5 has two runs: T2's description (footnote markers 4 to 7 left out)
# and footnote 4.
CARRIES = [
    ("row4", "constants", "non_novel_chem_bio_weapons", [
        ([("S0059", 9821, 10070)], "c95d784cea19ddbd5b1eaf84a829bf20cd4e899917a5071aa0f4ba7940173ce7", 248),
    ]),
    ("row5", "constants", "novel_chem_bio_weapons", [
        ([("S0073", 11774, 11980), ("S0074", 11983, 12013), ("S0074", 12016, 12215), ("S0074", 12218, 12258),
          ("S0074", 12261, 12290)],
         "8f2913bdff24fb41545ee59e84655dd1691381abfbd6e7229bd1b49265013c52", 507),
        ([("S0088", 14820, 14942)], "aed06ac8b302c0ecf6458c23b924ee30ddce933a353a4b752e8124a968045fee", 122),
    ]),
    ("row6", "constants", "misaligned_high_stakes", [
        ([("S0081", 13595, 13843), ("S0088", 15105, 15246)],
         "8aeb14965dd4d5f08999b0613a877d8102a0604d8a052c27065fde1a6186da5c", 388),
    ]),
    ("row7", "constants", "automated_rd", [
        ([("S0096", 16221, 16551)], "0ce19b040d333491559803eba54ecebbc29f6c8ef283459f559b4d0b4268cad1", 328),
    ]),
    ("row8", "predicates", "double_rate", [
        ([("S0121", 21585, 21702), ("S0120", 21544, 21582)],
         "da006658a64d9a73cf169b1b2086a0afa34a82e9fa93cf249a59fb51fcdefd0e", 148),
    ]),
    ("row10", "predicates", "more_capable_than_analyzed", [
        ([("S0151", 26348, 26659)], "7276cd5814d8f2710b2df5dd7c980304be1b8e31054c09155df37c1b03dd216a", 310),
    ]),
    ("row11", "predicates", "exceeds_all_analyzed", [
        ([("S0153", 26891, 27210)], "5ef94a916e1ac889de4256a1986b9c55ecb2b744562a861662eaf71505d4d11b", 318),
    ]),
    ("row13", "predicates", "factual_documented", [
        ([("S0161", 28301, 28377), ("S0162", 28378, 28420), ("S0163", 28421, 28540), ("S0164", 28541, 28659),
          ("S0165", 28660, 28966), ("S0166", 28967, 29181), ("S0167", 29182, 29269)],
         "b994f865d81d2faffefd58f5a3e9feb661213d6f70d1a900cf9add2f8ca061b3", 966),
    ]),
    ("row14", "predicates", "risk_analysed", [
        ([("S0170", 29395, 29421), ("S0171", 29422, 29585), ("S0172", 29586, 29833), ("S0173", 29834, 29905),
          ("S0174", 29906, 30053), ("S0175", 30095, 30209)],
         "d47e8331ac7038d66bca59d1f1e54dffa3038eefdf1d8c06341c146cc3c1a11e", 762),
    ]),
    ("row15", "predicates", "past_reviewed", [
        ([("S0177", 30253, 30269), ("S0178", 30270, 30543), ("S0179", 30544, 30696), ("S0180", 30697, 30855)],
         "4de6e95e9a3095f2e89244b9bb47e2da0146575ffaa1c84668ff4f909a09dc9e", 600),
    ]),
    ("row16", "predicates", "marginal_analysed", [
        ([("S0183", 30985, 31186), ("S0183", 31190, 31233), ("S0184", 31234, 31396), ("S0185", 31397, 31481),
          ("S0186", 31482, 31736), ("S0187", 31737, 31939)],
         "57608e3561f744f705e8a86dfd21c1b677708ea820af343101ee3ad4ea93d2ca", 949),
    ]),
    ("row16", "predicates", "marginal_justification", [
        ([("S0183", 30985, 31186)], "b2d96084b610ecf3eebb8e3fc84c06e530ad121392a983a45714d874e239a5ea", 201),
    ]),
    ("row17", "predicates", "executive_submitted", [
        ([("S0195", 32903, 33053)], "e96842230eb0633363b5fd4078bd1272a2ea6ac42c16e89ac752f635dda92fcc", 150),
    ]),
    ("row18", "predicates", "redaction_reason_listed", [
        ([("S0202", 34041, 34103), ("S0203", 34104, 34299), ("S0204", 34300, 34502), ("S0205", 34503, 34629),
          ("S0206", 34630, 34689)],
         "2d0bb8cf72397efa3d4e31ef0b1b5163c09a8af489943347873c1950b79eee14", 647),
    ]),
    ("row19", "predicates", "significantly_redacted", [
        ([("S0215", 36095, 36390), ("S0216", 36391, 36519)],
         "7eb85ee89efb9873cdad3aef07147799a7256c15284e5be08a03cc31328ac1be", 418),
    ]),
    ("row20", "predicates", "commentary_asked", [
        ([("S0234", 39171, 39204), ("S0235", 39205, 39322), ("S0236", 39323, 39403), ("S0237", 39404, 39564),
          ("S0238", 39565, 39659), ("S0239", 39660, 39782), ("S0240", 39783, 39820), ("S0241", 39821, 39884),
          ("S0245", 40189, 40382), ("S0246", 40383, 40537), ("S0247", 40538, 40711)],
         "2862e1401e31d097b072ee681a55174a4e344210a7e9df502b822577c7407a4a", 1220),
    ]),
    ("row21", "predicates", "rso_maintained", [
        ([("S0253", 41523, 41629), ("S0254", 41630, 41725), ("S0255", 41726, 41821), ("S0256", 41822, 41922),
          ("S0257", 41923, 42000), ("S0258", 42001, 42072)],
         "72792a5562723abcfcff0297aa759fe6c9de4b45da742cbe4c38b96221b349c8", 546),
    ]),
    ("row22", "predicates", "marginal_justification", [
        ([("S0197", 33262, 33455)], "33c6f249af15ceb7ad7d728564352ee31c3b56b0370728bf355ea265b6e92f70", 189),
    ]),
    ("row22", "predicates", "marginal_major_role", [
        ([("S0197", 33262, 33455)], "33c6f249af15ceb7ad7d728564352ee31c3b56b0370728bf355ea265b6e92f70", 189),
    ]),
    ("row23", "predicates", "redactions_justified", [
        ([("S0207", 34780, 34902)], "c647fcc6fc0284ba737a062b585055a24726ca4c2c156b01b9759d4c769bc12c", 121),
    ]),
    ("row24", "predicates", "public_review_sought", [
        ([("S0209", 35025, 35247)], "b144be003818615659a08c5e995c96651509c4a0fb3837e0869b525fe286bddc", 222),
    ]),
    ("row25", "predicates", "compliance_review", [
        ([("S0272", 44139, 44213)], "7bf45c7c2fff67d54440d76d05fad4f3fceaf4d6b16b31f705e9e1a8598a3aec", 74),
    ]),
]

# Row 33: each changelog date (map unit, start byte, end byte, the date's words) in its D3 date constant's legend.
DATES = [("S0299", 47905, 47934, "v1_0_date", "September 19, 2023 (RSP v1.0)"),
         ("S0300", 47977, 48004, "v2_0_date", "October 15, 2024 (RSP v2.0)"),
         ("S0336", 53583, 53608, "v2_1_date", "March 31, 2025 (RSP v2.1)"),
         ("S0343", 54916, 54939, "v2_2_date", "May 14, 2025 (RSP v2.2)"),
         ("S0347", 55755, 55783, "v3_0_date", "February 24, 2026 (RSP v3.0)"),
         ("S0349", 55901, 55925, "v3_1_date", "April 2, 2026 (RSP v3.1)"),
         ("S0356", 56573, 56598, "v3_2_date", "April 29, 2026 (RSP v3.2)"),
         ("S0357", 56827, 56850, "v3_3_date", "May 26, 2026 (RSP v3.3)")]

# Recorded units: (map unit, start byte, end byte, spans.json unit, kind, reason or None).
RECORDS = [("S0065", 10576, 10740, "t1-expect", "unformalised", "hope"),
           ("S0182", 30947, 30984, "s33-marginal-heading", "meta", None),
           ("S0211", 35479, 35609, "s36-intent", "unformalised", "hope"),
           ("S0280", 45300, 45510, "appa-priority", "unformalised", "hope"),
           ("S0281", 45511, 45553, "appa-lead-heading", "meta", None),
           ("S0286", 46000, 46040, "appa-strong-heading", "meta", None),
           ("S0290", 46601, 46620, "appa-uplevel-heading", "meta", None)]


def _norm(text):
    return fix._accounting().norm(text).strip()


def _legend(section, name):
    """The legend the reader is shown: the description in the committed D1 environment."""
    vocabulary = json.loads((RSP / "environment.d1.json").read_text(encoding="utf-8"))["vocabulary"]
    return vocabulary[section][name]["description"]


def _run_text(source, pieces):
    return " ".join(_norm(source[start:end].decode("utf-8")) for _, start, end in pieces)


def _holds_hashed_run(text, digest, length):
    data = text.encode("utf-8")
    return any(hashlib.sha256(data[i:i + length]).hexdigest() == digest for i in range(len(data) - length + 1))


def _source():
    path = pinned_source("anthropic-rsp", skip=False)
    return None if path is None else path.read_bytes()


def test_every_kept_row_carries_its_source_text_in_its_legend():
    source = _source()
    for row, section, name, runs in CARRIES:
        legend = _norm(_legend(section, name))
        for pieces, digest, length in runs:
            if source is not None:
                text = _run_text(source, pieces)
                assert hashlib.sha256(text.encode()).hexdigest() == digest and len(text.encode()) == length, row
                assert text in legend, (row, name, text)
            assert _holds_hashed_run(legend, digest, length), (row, name)


def test_every_changelog_date_is_in_its_d3_legend():
    source = _source()
    env = base.rsp_stage0.date_environment()
    for unit, start, end, constant, words in DATES:
        if source is not None:
            assert _norm(source[start:end].decode("utf-8")) == words, unit
        assert words in env.constants[constant].description, unit


def test_every_recorded_unit_lies_in_a_record_that_says_it_is_not_a_rule():
    spans = {u["id"]: u for u in json.loads((RSP / "spans.json").read_text(encoding="utf-8"))["units"]}
    for unit, start, end, record, kind, reason in RECORDS:
        found = spans.get(record)
        assert found is not None, unit
        assert found["span"][0] <= start and end <= found["span"][1], unit
        assert found["kind"] == kind and found.get("reason") == reason, unit
        assert found["status"] == ("UNFORMALISED" if reason else "LABELLED"), unit
        assert "rule" not in found and "open_terms" not in found and not found.get("waits"), unit
