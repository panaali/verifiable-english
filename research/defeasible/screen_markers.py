"""DF-0 item 1: re-run research 2.3's marker screen and write the blind packet for the second reader.

    uv run python research/defeasible/screen_markers.py

The screen is research 2.3's, as stated there (markers over each unit's `source_excerpt`). The packet carries the
units' full source text and research 2.3's nine class definitions, never research 2.3's assignments; those (its 18
screened G units) go to a separate key file used only by `score_second_reader.py`.
"""
from __future__ import annotations

from common import (CONSTITUTION, CONSTITUTION_RUN, MARKER_RE, sha256, unit_bytes, unit_text, units, write_json)

# Research 2.3's class table: the "What the sentence does" column, without examples' owners.
CLASSES = {
    "D1": "deontic default: a default rule on an act (\"should generally\", \"by default ... should\", "
          "\"absent ... should\", \"unless ... should\")",
    "G": "generic about facts: a defeasible generalisation over a non-deontic predicate (\"Operators typically "
         "interact with Claude in the system prompt\")",
    "SW": "instructable defaults: switches and who may set them (\"Default behaviors that operators can turn off\", "
          "\"Absent operator instructions, Claude should fall back on ...\")",
    "R": "presumption: a default about what to believe (\"Claude should assume that the user could be a human ... "
         "unless the operator's system prompt specifies otherwise\")",
    "P": "priority between defaults (\"prioritize these properties in the order ...\", \"holistic rather than "
         "strict\", \"generally preferable to unilateral intervention\")",
    "W": "weighing factors (\"wide-scale societal harms are generally worse than local ones\" inside a list of "
         "harm factors)",
    "S": "default sense of a word (\"When we talk about helpfulness, we are typically referring to helpfulness "
         "towards principals\")",
    "M": "marker without a default (\"collapsed this section by default\", \"more generally\", \"would otherwise "
         "occur\")",
    "O": "other (for example a desire: \"In most cases, we want Claude to have such a thorough understanding ...\")",
}

# Research 2.3, "The G class in detail": the 18 screened units (u0039.s02 was missed by the screen).
RESEARCH_G = ("u0031.s04", "u0020.s02", "u0264.s02", "u0044.s04", "u0044.s03", "u0081.s05", "u0145.s01",
              "u0141.s03", "u0054.s02", "u0100.s03", "u0118.s04", "u0157.s03", "u0228.s02", "u0279.s02",
              "u0011.s01", "u0025.s02", "u0112.s02", "u0241.s03")

INSTRUCTIONS = (
    "For each unit, read its text and choose exactly one class from the nine below for the default pattern it "
    "carries (the unit's first default-bearing clause if there are several). Answer with the unit id and the class "
    "code only. Do not consult any other classification of these units.")


def main():
    source_path = CONSTITUTION / "source/claude-constitution.md"
    source = source_path.read_bytes()
    rows = []
    for unit in units(CONSTITUTION_RUN):
        found = sorted({m.group(0).lower() for m in MARKER_RE.finditer(unit["source_excerpt"])})
        if found:
            rows.append({"id": unit["id"], "bytes": unit_bytes(unit), "markers": found})
    total = sum(r["bytes"] for r in rows)
    ids = {r["id"] for r in rows}
    write_json("marker-screen.json", {
        "inputs": {"units": sha256(CONSTITUTION_RUN / "units.json"), "source": sha256(source_path)},
        "screen": "research 2.3: markers over source_excerpt, case-insensitive, whole words",
        "expected_from_research": {"units": 99, "bytes": 19857},
        "units": len(rows), "bytes": total,
        "research_g_units_in_screen": sum(1 for u in RESEARCH_G if u in ids),
        "rows": rows})
    by_id = {u["id"]: u for u in units(CONSTITUTION_RUN)}
    write_json("second-reader-packet.json", {
        "instructions": INSTRUCTIONS, "classes": CLASSES,
        "units": [{"id": r["id"], "text": unit_text(source, by_id[r["id"]])} for r in rows]})
    write_json("second-reader-key.json", {
        "note": "Research 2.3's G assignments for the screened units. Scoring only; never shown to the reader.",
        "g_units": list(RESEARCH_G)})
    print(f"marker screen: {len(rows)} units, {total} B; research G units in screen: "
          f"{sum(1 for u in RESEARCH_G if u in ids)}/{len(RESEARCH_G)}")


if __name__ == "__main__":
    main()
