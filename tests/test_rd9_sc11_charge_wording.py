"""sc-11 review F1: every text about `routeSD`'s limits says `sdSuperposable` is read before the work limit, uncharged.

DRI ruling sc-11-3 item 2 (manage-agents/reviews/dri-decisions-20261109-sc-11-3.md) found that the "a wide guard
costs more per unit, row sc-11w makes the charge cost-proportional" reading was a misreading: the slow wide-guard
documents spend their CPU in `sdSuperposable`, which `routeSD` reads before `sdChecked`'s work limit and charges to
nothing, and sc-11w no longer has to build a cost-proportional charge. The ruling orders SoftSupWire.lean's module
docstring, the REPORT's OPEN-SC11-7 paragraph and 14.11's closing paragraph to say so. The class is a text that
promises a charge nobody builds, or hides the uncharged read: one table (`PLACES`) names every text that states
the route's limits, and each must carry the ruling's facts and none of the stale phrases. Since sc-11w (DRI
2026-11-10 sc-11w item 1) `sdSuperposable` reads a size charge first, so the code comment and 14.11 (`CURRENT`) state
that charge instead, and sc-11's REPORT keeps the wording sc-11 merged with.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# The facts the ruling orders each text to state (substrings, after collapsing whitespace).
REQUIRED = (
    "`sdSuperposable` (`superposable`, `WellFormedU (supU N)`) is read before the work limit and not charged",
    "10.98 s and 94-100 s measured on the 767- and 3,071-node guard documents",
    "row sc-11w bounds it before sc-11b (DRI 2026-11-09 sc-11-3 item 2)",
)
# Phrases of the misreading the ruling withdrew.
STALE = ("cost-proportional", "costs more per unit")


def _module_docstring(text: str) -> str:
    return text.split("/-!", 1)[1].split("-/", 1)[0]


def _section(heading: str, following: str):
    return lambda text: text.split(heading, 1)[1].split(following, 1)[0]


def _report_bullet(text: str) -> str:
    return text.split("- **OPEN-SC11-7**", 1)[1].split("\n- **", 1)[0]


# Every text that states routeSD's limits: (path, the part that must carry the ruling's wording). sc-11's REPORT
# records sc-11 as merged; the code comment and 14.11 state the limits as they are now (CURRENT, sc-11w).
PLACES = (
    ("docs/rd-9/sc-11/REPORT.md", _report_bullet),
)
CURRENT = (
    ("lean/VE/Readings/SoftSupWire.lean", _module_docstring),
    ("docs/spec/rd-9-soft-chain.md", _section("### 14.11", "### 14.12")),
)
# DRI 2026-11-10 sc-11w item 1: `sdSuperposable` reads the size charge first, and the measured seconds were
# `sdCheckWork`'s premise build; a current text that still says the read is uncharged is stale.
CURRENT_REQUIRED = (
    "sdSizeCharge N ≤ maxSdSizeCharge",
    "`sdCheckWork_eq_fast`",
    "10.98 s and 94-100 s",
    "premise build",
)
CURRENT_STALE = ("not charged",)
# Every file of the item that could repeat the withdrawn promise anywhere.
SCANNED = (
    "docs/spec/rd-9-soft-chain.md",
    "docs/rd-9/sc-11/REPORT.md",
    "docs/rd-9/sc-11/w13-cpu.md",
    "lean/VE/Readings/SoftSupLabels.lean",
    "lean/VE/Readings/SoftSupWire.lean",
    "lean/VE/Readings/SoftSupWireExamples.lean",
)


def _flat(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def wording_faults(part: str) -> list[str]:
    flat = _flat(part)
    return [f"missing: {r}" for r in REQUIRED if r not in flat] + [f"stale: {s}" for s in STALE if s in flat]


@pytest.mark.parametrize(("path", "cut"), PLACES, ids=[p for p, _ in PLACES])
def test_probe_f1_each_limits_text_says_sd_superposable_is_read_before_the_work_limit(path, cut):
    """PROBE F1 of sc-11-review: the ruling's wording, in each place the ruling names."""
    assert wording_faults(cut((ROOT / path).read_text(encoding="utf-8"))) == []


def current_faults(part: str) -> list[str]:
    flat = _flat(part)
    return [f"missing: {r}" for r in CURRENT_REQUIRED if r not in flat] + [
        f"stale: {s}" for s in STALE + CURRENT_STALE if s in flat]


@pytest.mark.parametrize(("path", "cut"), CURRENT, ids=[p for p, _ in CURRENT])
def test_each_current_limits_text_says_sd_superposable_reads_the_charge_first(path, cut):
    """sc-11w: the code comment and 14.11 state the size charge, and the uncharged read is gone."""
    assert current_faults(cut((ROOT / path).read_text(encoding="utf-8"))) == []


def test_the_sc11_wording_is_stale_in_a_current_text():
    assert "stale: not charged" in current_faults(" ".join(REQUIRED + CURRENT_REQUIRED))


@pytest.mark.parametrize("path", SCANNED)
def test_no_sc11_text_promises_the_withdrawn_cost_proportional_charge(path):
    flat = _flat((ROOT / path).read_text(encoding="utf-8"))
    assert [s for s in STALE if s in flat] == []


# The committed text the review found (1264c26df), one per place: the check must refuse each.
_REVIEWED = (
    "shape; a wide guard costs more per unit, and row sc-11w makes the charge cost-proportional before sc-11b.",
    "limit is the enumerated row, not an error. A wide guard costs more per unit than W-13's shape; row sc-11w makes "
    "the\ncharge cost-proportional before sc-11b switches the dispatch (item 2 of that decision).",
    "Correction sent to the DRI: the two wide-guard rows' cost is `sdSuperposable`'s, not the per-choice texts' "
    "(w13-cpu.md); it bears on sc-11w and sc-admit-cpu, not on the constant.",
)


@pytest.mark.parametrize("text", _REVIEWED, ids=["lean", "spec", "report"])
def test_the_reviewed_wording_fails_the_check(text):
    assert any(f.startswith("missing: ") for f in wording_faults(text))


def test_a_text_with_the_ruling_and_a_stale_phrase_fails():
    text = " ".join(REQUIRED) + " A wide guard costs more per unit; the charge becomes cost-proportional."
    assert wording_faults(text) == ["stale: cost-proportional", "stale: costs more per unit"]


def test_each_place_cut_is_a_proper_part_of_its_file():
    """A cut that fell back to the whole file would let a far-away sentence satisfy the check."""
    for path, cut in PLACES + CURRENT:
        text = (ROOT / path).read_text(encoding="utf-8")
        assert 0 < len(cut(text)) < len(text) // 2, path


# sc-11w review F1 and F2 (manage-agents/sc-11w-review.final.md): two overclaims about what sc-11w's limits ensure.
# F1: `sdCheckWorkFast` builds no *coherence* premise, but it still builds the exception premises (`min` reads
# `excPremises X`'s length). F2: the size charge bounds `sdSuperposable`'s reads, not the whole route; `heavyIn` is
# within both limits and took up to 1.16 s (the accepted gap of row sc-11wc), and cpu.md's table has 0.74 s above
# the 0.60 s its summary called the maximum. The class is a text of the item that claims more than its code or its
# own table: every sc-11w text is scanned (`SC11W_TEXTS`), and the summary figures are recomputed from the table.
SC11W_TEXTS = (
    "lean/VE/Readings/SoftSupWire.lean",
    "docs/spec/rd-9-soft-chain.md",
    *sorted(str(p.relative_to(ROOT)) for p in (ROOT / "docs/rd-9/sc-11w").glob("*.md")),
)
# "no premise", "builds no premise", "without building the premises": a premise claim not narrowed to coherence.
_UNNARROWED_PREMISE = re.compile(r"\b(?:no|without building the) premises?\b")
# A claim that the charge (or being within it) makes the route end within R4.
_CHARGE_ENSURES_R4 = re.compile(r"within `maxSdSizeCharge`, `routeSD` ends within R4")


def overclaim_faults(text: str) -> list[str]:
    flat = _flat(text)
    return ([f"premise: {m.group(0)}" for m in _UNNARROWED_PREMISE.finditer(flat)]
            + [f"R4: {m.group(0)}" for m in _CHARGE_ENSURES_R4.finditer(flat)])


@pytest.mark.parametrize("path", SC11W_TEXTS)
def test_probe_sc11w_f1_f2_no_text_overclaims_the_fast_counter_or_the_charge(path):
    """PROBE F1 and F2 of sc-11w-review: no unnarrowed premise claim, no claim that the charge ensures R4."""
    assert overclaim_faults((ROOT / path).read_text(encoding="utf-8")) == []


# Each place that says the fast counter skips the coherence premises also says the exception premises are built,
# and each place that states the charge's measurement names the open per-choice gap.
_FAST_COUNTER_PLACES = (
    ("lean/VE/Readings/SoftSupWire.lean", _module_docstring),
    ("lean/VE/Readings/SoftSupWire.lean", lambda t: t.split("def sdCheckWork (N", 1)[1].split("def sdCheckWorkFast", 1)[0]),
    ("docs/spec/rd-9-soft-chain.md", _section("### 14.11", "### 14.12")),
    ("docs/rd-9/sc-11w/cpu.md", _section("## `sdCheckWork` before and after", "| Case")),
    ("docs/rd-9/sc-11w/REPORT.md", _section("2. **A cheaper `sdCheckWork`", "3. **")),
)
_CHARGE_PLACES = (
    ("lean/VE/Readings/SoftSupWire.lean", _module_docstring),
    ("lean/VE/Readings/SoftWire.lean", lambda t: t.split("/-- 14.11 (sc-11w)", 1)[1].split("def sdSizeCharge", 1)[0]),
    ("docs/spec/rd-9-soft-chain.md", _section("### 14.11", "### 14.12")),
    ("docs/rd-9/sc-11w/cpu.md", _section("Results:", "## ")),
    ("docs/rd-9/sc-11w/REPORT.md", _section("12. CPU:", "13. ")),
)


@pytest.mark.parametrize(("path", "cut"), _FAST_COUNTER_PLACES, ids=[f"{p}#{i}" for i, (p, _) in
                                                                      enumerate(_FAST_COUNTER_PLACES)])
def test_each_fast_counter_text_says_the_exception_premises_are_built(path, cut):
    part = _flat(cut((ROOT / path).read_text(encoding="utf-8")))
    assert "coherence premise" in part and "excPremises" in part


@pytest.mark.parametrize(("path", "cut"), _CHARGE_PLACES, ids=[f"{p}#{i}" for i, (p, _) in enumerate(_CHARGE_PLACES)])
def test_each_charge_measurement_names_the_open_per_choice_gap(path, cut):
    part = _flat(cut((ROOT / path).read_text(encoding="utf-8")))
    assert "sc-11wc" in part and "1.16 s" in part


def _cpu_rows() -> list[tuple[str, int, float, float]]:
    """cpu.md's `routeSD` table: (case, charge, the slowest `routeSD` run, the slowest `reads` run)."""
    text = (ROOT / "docs/rd-9/sc-11w/cpu.md").read_text(encoding="utf-8")
    table = text.split("## `routeSD` on the committed code", 1)[1].split("Results:", 1)[0]
    rows = []
    for line in table.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 6 or not cells[1].replace(",", "").isdigit():
            continue
        secs = [[float(x) for x in re.findall(r"\d+\.\d+", c)] for c in (cells[3], cells[4])]
        rows.append((cells[0], int(cells[1].replace(",", "")), max(secs[0]), max(secs[1])))
    return rows


def test_cpu_summary_figures_are_the_table_maxima():
    """F2's second half: the Results name the table's slowest `routeSD` row and the slowest reads within the charge,
    and no summary in cpu.md or the REPORT bounds every case below the table's maximum."""
    rows = _cpu_rows()
    assert len(rows) >= 13
    case, _, slowest, _ = max(rows, key=lambda r: r[2])
    reads = max(r[3] for r in rows if r[1] <= 16384)
    results = _flat(_section("Results:", "## ")((ROOT / "docs/rd-9/sc-11w/cpu.md").read_text(encoding="utf-8")))
    assert f"The slowest is {case.split(' (')[0]} at {slowest:.2f} s" in results
    assert f"at most {reads:.2f} s on any case within the charge" in results
    for path in ("docs/rd-9/sc-11w/cpu.md", "docs/rd-9/sc-11w/REPORT.md"):
        flat = _flat((ROOT / path).read_text(encoding="utf-8"))
        assert [float(x) for x in re.findall(r"every case at most (\d+\.\d+) s", flat) if float(x) < slowest] == []


# The committed text the sc-11w review found (89f139589f): the check must refuse each.
_REVIEWED_SC11W = (
    "`sdCheckWork` is evaluated without building the premises it counts (`sdCheckWork_eq_fast`).",
    "`softXL`'s length is its exception labels' and colliding pairs', so no\npremise is built",
    "counts the exception labels and the colliding pairs and builds no premise.",
    "Measured: within `maxSdSizeCharge`,\n`routeSD` ends within R4 (docs/rd-9/sc-11w/cpu.md).",
)


@pytest.mark.parametrize("text", _REVIEWED_SC11W, ids=["spec", "lean-fast", "cpu", "lean-charge"])
def test_the_reviewed_sc11w_overclaims_fail_the_check(text):
    assert overclaim_faults(text) != []
