"""DF-0 item 1: re-run research 2.3's marker screen and write the blind packet for the second reader.

    uv run python research/defeasible/screen_markers.py

The screen is research 2.3's, as stated there (markers over each unit's `source_excerpt`). The packet carries the
units' full source text and research 2.3's nine class definitions, never research 2.3's assignments; those (its 18
screened G units) go to a separate key file used only by `score_second_reader.py`.
"""
from __future__ import annotations

from common import (CONSTITUTION, CONSTITUTION_RUN, MARKER_RE, sha256, unit_bytes, unit_text, units, write_json)

# Research 2.3's class table: the "What the sentence does" column. Pre-run edit (before any reader, recorded in
# docs/research/defeasible-phase1.md 2.1): research 2.3 illustrates each class with phrases and sentences from the
# constitution, and 29 of the 99 packet units contain one of them (28 verbatim, u0135.s04 near-verbatim), which labels
# those units for the reader. Every
# example below is invented and quotes nothing from the constitution; the class meanings are unchanged.
CLASSES = {
    "D1": "deontic default: a default rule on an act, which holds unless something defeats it (invented example: "
          "\"Visitors should generally sign in at the front desk\")",
    "G": "generic about facts: a defeasible generalisation over a non-deontic predicate (invented example: "
         "\"Trains on this line usually arrive on time\")",
    "SW": "instructable defaults: a default behaviour with who may switch it on or off, or what applies when nobody "
          "has (invented example: \"Notifications are on by default, and an administrator can turn them off\")",
    "R": "presumption: a default about what to believe or assume until told otherwise (invented example: \"Staff "
         "should assume that a caller is a customer unless the caller says otherwise\")",
    "P": "priority between defaults: an order or preference among defaults or considerations, strict or holistic "
         "(invented example: \"Put safety first, cost second and speed third\")",
    "W": "weighing factors: a consideration that counts for more or less when options are weighed, usually inside a "
         "list of factors (invented example: \"A delay that strands many passengers usually counts for more than "
         "one that strands a few\")",
    "S": "default sense of a word: what a word is normally taken to mean in the text (invented example: \"By the "
         "library we usually mean the main branch\")",
    "M": "marker without a default: a marker word such as \"generally\", \"by default\" or \"otherwise\" is present "
         "but no default is stated (invented example: \"More generally, the report has three parts\")",
    "O": "other: a default pattern that fits none of the classes above, for example a desire (invented example: "
         "\"In most cases we want visitors to feel welcome\")",
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
        "units": [{"id": r["id"], "bytes": r["bytes"], "text": unit_text(source, by_id[r["id"]])} for r in rows]})
    write_json("second-reader-key.json", {
        "note": "Research 2.3's G assignments for the screened units. Scoring only; never shown to the reader.",
        "g_units": list(RESEARCH_G)})
    print(f"marker screen: {len(rows)} units, {total} B; research G units in screen: "
          f"{sum(1 for u in RESEARCH_G if u in ids)}/{len(RESEARCH_G)}")


if __name__ == "__main__":
    main()
