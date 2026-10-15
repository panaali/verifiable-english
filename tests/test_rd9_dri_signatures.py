"""The DRI's rd-9 signatures, recorded (review F27 of rd-9; manage-agents/reviews/rd-9-dri-signatures-20261015.md).

Each signature is read from the saved records (the trust baseline's signed entry, `DELTA.md`, the fix report) and from
the code it cites, never from a live diff, so the tests still pass after a sync with main.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DELTA = ROOT / "docs/readings-defaults/rd9-lean/DELTA.md"
REPORT = ROOT / "docs/rd-9/integration/FIX-REPORT.md"
SIGNED = "SIGNED WITH CONDITION by DRI 2026-10-15 (rd-9 B8/B9"
NARROWINGS = "ve/rights_route.py:23-89"


def _entry():
    """The signed entry. Since AR-4 the budget file keeps it as allowances, one per class that grew, the entry's text
    as their reason and the commit that recorded it; the entry itself (its `rebaselined_from`) is read there."""
    allowances = [a for a in json.loads((ROOT / "docs/trust-baseline.json").read_text())["allowances"]
                  if a["signature"].startswith(SIGNED)]
    [reason] = {a["reason"] for a in allowances}
    [commit] = {a["commit"] for a in allowances}
    recorded = json.loads(subprocess.check_output(["git", "show", f"{commit}:docs/trust-baseline.json"], cwd=ROOT))
    [entry] = [e for e in recorded["history"] if e.get("signed", "").startswith(SIGNED)]
    assert entry["change"] == reason
    assert {a["class"]: a["lines"] for a in allowances} == {c: n for c, n in entry["allow"].items() if n}
    return entry


def _items(text):
    found = re.findall(r"`?((?:VE|ResponseShape)/[\w/]+\.lean)`? ([+-]\d+)", text)
    return [(path, int(delta)) for path, delta in found]


def test_the_trust_entry_is_signed_and_itemised():
    """(a) The signed entry allows exactly the re-measured growth, and its per-file items add up to it, per class."""
    entry = _entry()
    assert entry["allow"] == {"K": 0, "S": 171, "V": 372}
    change = entry["change"]
    s_part, v_part = change.split("S by file", 1)[1].split("V (untied D[V] and G[V]) by file", 1)
    assert sum(d for _, d in _items(s_part)) == 171
    assert sum(d for _, d in _items(v_part.split("FOLLOW-UP", 1)[0])) == 372
    assert "FOLLOW-UP: a ties pass" in change
    assert entry["rebaselined_from"] == {"K": 997, "S": 9788, "V": 37154}


def test_the_reports_record_the_same_itemised_numbers():
    """DELTA.md's row lists the same files and numbers as the baseline's signed entry."""
    entry_items = sorted(_items(_entry()["change"]))
    delta = DELTA.read_text()
    row = next(line for line in delta.splitlines() if line.startswith("| Trust growth"))
    assert sorted(_items(row)) == entry_items
    assert "SIGNED WITH CONDITION" in row and "S +171, V +372" in row
    assert "K 997, S 9,959, V 37,526" in REPORT.read_text()


def test_the_d1_exception_cites_narrowings_lines():
    """(b) Both records cite `_narrowings`' lines, its time box and the item that ends it; the lines cited are the
    whole function, and its docstring carries the same exception."""
    for text in (DELTA.read_text(), REPORT.read_text()):
        assert NARROWINGS in text and "time-boxed to 2026-10-22" in text and "rights-licence-relay" in text
    lines = (ROOT / "ve/rights_route.py").read_text().splitlines()
    first, last = (int(n) for n in NARROWINGS.split(":")[1].split("-"))
    assert lines[first - 1].startswith("def _narrowings(")
    assert lines[last - 1] == "    ]" and lines[last].strip() == "" and lines[last + 2].startswith("def ")
    body = "\n".join(lines[first - 1:last])
    assert "D1 exception the DRI GRANTED on 2026-10-15, time-boxed to 2026-10-22" in body
    assert "rights-licence-relay" in body
    assert any("!= _narrowings(" in line for line in lines[312:317])


def test_b1_b4_and_b8_are_recorded():
    """(c) and (d): B4 and B8 signed; B1 signed once the full gate passes, its conditions (F25, F26) met."""
    for text in (DELTA.read_text(), REPORT.read_text()):
        assert re.search(r"\| B4[^\n]*\*\*SIGNED\*\*", text)
        assert re.search(r"\| B8[^\n]*\*\*SIGNED\*\*", text)
        assert re.search(r"\| B1[^\n]*\*\*SIGNED once the full gate passes on the final HEAD\*\*", text)


def test_f30_no_row_of_a_signed_item_still_says_pending():
    """Review F30 of rd-9: every row of the reports about B1, B4 or B8 gives the DRI's signature; none still says
    the item is pending or not to be signed (code spans, which name tools and tests, are not prose)."""
    for text in (DELTA.read_text(), REPORT.read_text()):
        rows = [line for line in text.splitlines() if re.match(r"\| B[148]\b", line)]
        assert len(rows) >= 3
        for row in rows:
            prose = re.sub(r"`[^`]*`", "", row)
            assert not re.search(r"pending|do not (sign|mark)", prose, re.IGNORECASE), row
