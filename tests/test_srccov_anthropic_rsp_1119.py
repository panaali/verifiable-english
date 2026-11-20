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
import re
import sys
from collections import Counter

import pytest

import test_fsf_repair_f6_sl2plus_1119 as f6
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
           ("S0141", 24916, 24939, "s31-heading", "meta", None),
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


def test_no_carried_run_sits_inside_a_citation_parenthesis():
    """A carry counts only if the counter reads it: a run quoted inside "(3.5: ...)" is cut whole as a citation
    (tests/test_fsf_repair_f6_sl2plus_1119.py, tools/defs_carried_counter.py). Each carried run must survive that
    cut of its legend; the five carries once written as "(3.3: \"...\")" did not. Predicate legends only: the counter
    shows no constant legend at all (REPORT, Note 1)."""
    source = _source()
    for row, section, name, runs in (c for c in CARRIES if c[1] == "predicates"):
        legend = _legend(section, name)
        cut = _norm(f6._cut_inside(legend))
        assert [m.group(0)[:60] for m in f6.CITATION_PARENTHESIS.finditer(legend) if '"' in m.group(0)] == [], row
        assert ".. " not in legend, (row, name)  # a quoted sentence's full stop is not doubled before "Open term"
        for pieces, _, _ in runs if source is not None else ():
            # The run is cut the same way: the source's own "(1)" or "(e.g., ...)" goes on both sides.
            assert _norm(f6._cut_inside(_run_text(source, pieces))) in cut, (row, name)

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


# --- The derived records the span changes move (review F1, F2) -------------------------------------------------------
# results.json copies the byte measurement (coverage.json, spans.json) into its metrics, and the README copies the
# measurement, stage 0, the gaps and the results into its tables and prose. Each copy is checked against the committed
# files it comes from, so a span change that leaves one stale fails here instead of in a review.

@pytest.mark.skipif(not base.LEAN_SERVICE.exists(), reason="the Lean service is not built")
@pytest.mark.parametrize("case", ("anthropic-rsp", "openai-preparedness"))
def test_saved_metrics_equal_their_recomputation_from_the_committed_files(case, monkeypatch):
    """Every metric results.json saves (M3's bytes and M10's units included) equals run.metrics() over the saved run
    and the committed coverage.json and spans.json; no metric is saved that metrics() does not compute."""
    modules = base.RSP_MODULES if case == "anthropic-rsp" else base.PF_MODULES
    for name, module in modules.items():
        monkeypatch.setitem(sys.modules, name, module)
    saved = json.loads((base.USECASES / case / "results.json").read_text())
    fresh = modules["run"].metrics(saved)
    stale = sorted(k for k in fresh.keys() | saved["metrics"].keys() if fresh.get(k) != saved["metrics"].get(k))
    assert stale == [], f"{case}/results.json is out of date in {stale}: rerun its run.py"


def _flat(text):
    return " ".join(text.split())


def _section(readme, heading):
    start = readme.index(f"\n## {heading}")
    end = readme.find("\n## ", start + 1)
    return readme[start:None if end == -1 else end]


def _body_rows(section):
    """The cells of each body row of the section's tables (header and rule rows left out)."""
    rows, header = [], True
    for line in section.splitlines():
        if not line.startswith("|"):
            header = True
            continue
        if not header and not line.startswith("|---"):
            rows.append([cell.strip() for cell in line.strip().strip("|").split("|")])
        header = header and not line.startswith("|---")
    return rows


def _and(ids):
    return ids[0] if len(ids) == 1 else ", ".join(ids[:-1]) + " and " + ids[-1]


def readme_figures():
    """The README's measured sentences, each built from the committed file it reports."""
    spans = json.loads((RSP / "spans.json").read_text())["units"]
    coverage = json.loads((RSP / "coverage.json").read_text())
    stage0 = json.loads((base.RSP_EVIDENCE / "stage0.json").read_text())
    results = json.loads((RSP / "results.json").read_text())
    total, units = stage0["P5"]["total"], stage0["P5"]["units"]
    routed = stage0["P6"]["routed"]
    d1 = coverage["bytes_by_status"]["CHECKED"]
    # The README adds D1's and the routed documents' CHECKED bytes; they must make the master map's CHECKED.
    assert d1 + routed["D2"] + routed["D3"] == coverage["master_bytes_by_status"]["CHECKED"]
    checked = [u for u in spans if u["status"] == "CHECKED"]
    parts = {"premise": [u for u in checked if u["kind"] == "asserted" and "routed" not in u],
             "routed": [u for u in checked if "routed" in u],
             "commitment": [u for u in checked if u["kind"] == "norm" and "routed" not in u]}
    assert sum(map(len, parts.values())) == len(checked)
    size = {u["id"]: u["span"][1] - u["span"][0] for u in spans}
    rows = results["comparison"]
    undecided = results["metrics"]["M8"]["unknown_items"]
    findings = [r["id"] for r in rows if r["status"] == "disagree" and r["cause"]["kind"] == "key finding"]
    correct = sum(r["agree"] for r in rows)
    narrowed = {k: sorted(v["changed"]) for k, v in results["without_narrowings"].items()}
    return [
        f"({total:,} bytes, from",
        f"the byte-by-byte accounting of the source text: {units} units",
        f"| {results['metrics']['M10']['rules']} VE rules:",
        f"the {len(rows)} answers of PLAN sections 5 and 6",
        f"All {total:,} bytes of the source are in exactly one of the document's {units} units.",
        f"Within D1 alone, {d1:,} bytes are CHECKED. D3 checks {routed['D3']:,} bytes",
        f"D2 checks {routed['D2']:,} bytes",
        f"The {len(checked)} CHECKED units are {len(parts['premise'])} premise units, the {len(parts['routed'])} "
        f"routed units and the {len(parts['commitment'])} commitments",
        f"Only its {size['s361-financial-interest']}-byte organization clause is CHECKED; the "
        f"{size['s361-individual-financial-interest']}-byte individual/review-chain financial-interest clause and "
        f"{size['s361-personal-relationships']}-byte close-personal-relationship clause are UNFORMALISED",
        f"| P5 D1 over the text | {units} units; `bytes_by_status` totals {total:,} |",
        f"| P6 the routed units | {routed['D2']:,} B to D2, {routed['D3']:,} B to D3;",
        f"All {len(undecided)} undecided rows name",
        f"The {len(findings)} other rows that differ from the frozen key ({', '.join(findings)}) are key findings",
        f"so {correct + len(findings)} of {len(rows)} match the key",
        f"The {len(undecided)} faithful undecided rows in `results.json`",
        f"Removing N1 changes {len(narrowed['N1'])} answer cells",
        f"removing N2 changes {_and(narrowed['N2'])}; removing N3 changes {_and(narrowed['N3'])}.",
    ]


def readme_tables():
    """For each measured table: the section, and the expected cells of each family keyed by the row's first cell."""
    gaps = json.loads((base.RSP_EVIDENCE / "gaps.json").read_text())
    spans = json.loads((RSP / "spans.json").read_text())["units"]
    results = json.loads((RSP / "results.json").read_text())
    counts = Counter(u["status"] for u in spans)
    statuses = {s: [str(counts[s]), f"{b:,}", f"{b / gaps['source_bytes']:.1%}"]
                for s, b in gaps["master_bytes_by_status"].items()}
    features = {k: [str(f["units"]), f"{f['bytes']:,}", f"{f['sole_units']}, {f['sole_bytes']:,}"]
                for k, f in gaps["features"].items()}
    m1 = results["metrics"]["M1"]
    answers = {k: [f"{v['correct']} / {v['key']}", str(v["faithful_undecided"])] for k, v in m1.items()}
    answers["**Total**"] = [f"**{sum(v['correct'] for v in m1.values())} / {sum(v['key'] for v in m1.values())}**",
                            f"**{sum(v['faithful_undecided'] for v in m1.values())}**"]
    return [("Span accounting", statuses, False), ("What each byte that is not CHECKED waits for", features, True),
            ("Answers to the frozen key", answers, True)]


def _family(label, families):
    keys = [k for k in families if label == k or label.startswith(k + " ")]
    assert len(keys) <= 1, label
    return keys[0] if keys else None


def test_readme_figures_are_the_committed_measurements():
    """Each measured sentence of the README is the one built from today's files, every row of its measured tables
    shows its family's committed cells (a family the files lack shows zeros), every family has its row, and no byte
    or unit count is left in the README outside a checked sentence or table row."""
    readme = (RSP / "README.md").read_text()
    flat = _flat(readme)
    bound = []
    for figure in readme_figures():
        found = [i for i in range(len(flat)) if flat.startswith(figure, i)]
        assert found, f"README.md does not say: {figure!r}"
        bound += [(i, i + len(figure)) for i in found]
    for heading, families, absent_zero in readme_tables():
        seen = []
        for cells in _body_rows(_section(readme, heading)):
            family = _family(cells[0], families)
            if family is None:
                width = len(next(iter(families.values())))
                assert absent_zero and set("".join(cells[1:width + 1])) <= set("0, "), (heading, cells)
                continue
            seen.append(family)
            assert cells[1:len(families[family]) + 1] == families[family], (heading, cells[0])
        assert sorted(seen) == sorted(families), heading
    # Table cells are bare numbers, checked above; a count of bytes or units in prose must sit in a checked sentence.
    for match in re.finditer(r"\d[\d,]*(?:-byte| bytes?\b| B to| units?\b)", flat):
        assert any(a <= match.start() < b for a, b in bound), \
            f"README.md states {match.group()!r} with no check against the committed files"
