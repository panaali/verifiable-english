#!/usr/bin/env python3
"""PS-0p census (presupposition-PLAN 6, PS-0p steps 1, 2, 4 and the audit additions): pinned runs, read only.

Writes, under docs/research/evidence/presupposition/:
  ledger-triggers-constitution.json, ledger-triggers-udhr.json  the word-level `presupposition_triggers` of every unit (D1)
  headings.json                                                 the 29 heading units: class, trigger words, withholding hits (D2, D3)
  census-checks.json                                            checks H1-H6, O1-O9, U1-U5 against the pre-registered values

Every definition is the one fixed in docs/research/presupposition-phase1.md 1.3 before this script existed.

    python3 research/presupposition/ps0p_census.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PILOTS = Path("/home/seyran/code/manage-agents/pilots")
CONST_RUN = PILOTS / "claude-constitution/run-20261012T1800Z"
UDHR_RUN = PILOTS / "udhr/run-20261012T1800Z"
CONST_SRC = PILOTS / "claude-constitution/source/claude-constitution.md"
UDHR_SRC = PILOTS / "udhr/source/udhr.md"
OUT = ROOT / "docs/research/evidence/presupposition"

AP = "(?:’s|'s)"
I = re.IGNORECASE

# In-sentence trigger groups (1.3).
G1 = re.compile(r"\bthe (?:user|operator)s?\b", I)
G2 = re.compile(r"\b(?:the (?:user|operator|principal)" + AP + r"|its|their)\s+(?:system prompt|instructions?|requests?|message"
                r"|claims?|content|goals?|context|wishes|interests?|failure|right)\b", I)
G3 = re.compile(r"\b(?:stop(?:s|ped|ping)?|ceas(?:e|es|ed|ing)|continu(?:e|es|ed|ing)|resum(?:e|es|ed|ing)|no longer"
                r"|remain(?:s|ed|ing)?|still|again|return(?:s|ed|ing)? to)\b", I)
G3_NARROW = re.compile(r"\b(?:stop(?:s|ped|ping)?|ceas(?:e|es|ed|ing)|continu(?:e|es|ed|ing)|resum(?:e|es|ed|ing)|no longer)\b", I)
G3_EXCLUDED = ("Still,", "Again,")
G4 = re.compile(r"\b(?:(?i:the user|the operator|the principal)|Claude|Anthropic)" + AP)
G5 = re.compile(r"\b(?:reali[sz]\w*|recogni[sz]\w*|aware (?:that|of)|know(?:s|n)? that|knew that|acknowledg\w*|notic\w*"
                r"|discover\w*|regret\w*|forg[eo]t\w*|learn(?:s|ed|t)? that)\b", I)
G6 = re.compile(r"\b(?:Claude" + AP + r"|(?i:its))\s+(?i:wellbeing|welfare|interests|moral status|experiences?|emotions?"
                r"|sense of (?:self|identity))\b")
O2_RE = re.compile(r"\bthe (?:user|operator|principal)" + AP + r" \w+", I)
O3_RE = re.compile(r"\b(?:Claude|Anthropic)" + AP)
O6_RE = re.compile(r"\bremain\w*", I)
O7_RE = re.compile(r"\bstill\b", I)
O8_RE = re.compile(r"\b(?:again|return(?:s|ed|ing)? to)\b", I)

GROUPS = {"G1": G1, "G2": G2, "G3": G3, "G4": G4, "G5": G5, "G6": G6}

# Title lexicon (1.3).
FACTIVE_STEMS = G5.pattern
TITLE_LEXICON = re.compile(
    r"\w+" + AP + r"|\b(?:our|its|their|his|her|my|your|we|us|the|existing|other|as|one|two|three|four|five|six|seven"
    r"|eight|nine|ten|\d+)\b|" + FACTIVE_STEMS, I)
TITLE_WH = re.compile(r"^\s*(?:what|why|how|who|which)\b", I)

CLASSES = {
    "A": ["u0013", "u0095", "u0286", "u0002", "u0235"],
    "B": ["u0069", "u0083", "u0245", "u0032"],
    "C": ["u0008", "u0238", "u0219", "u0027", "u0042", "u0130", "u0143"],
    "D": ["u0254", "u0268"],
    "E": ["u0040", "u0055", "u0075", "u0151", "u0162", "u0174", "u0195", "u0207", "u0212", "u0257", "u0260"],
}
TRIGGER_WORDS = {"u0013": "Claude’s", "u0095": "Anthropic’s", "u0286": "Acknowledging", "u0002": "the mission of",
                 "u0235": "Claude’s"}
NOUNS = {"u0013": "core value", "u0095": "guideline", "u0286": "open problem", "u0002": "mission", "u0235": "nature",
         "u0254": "wellbeing", "u0268": "wellbeing"}


def load(run: Path) -> list[dict]:
    data = json.loads((run / "units.json").read_text())
    return data if isinstance(data, list) else data["units"]


def text_of(src: bytes, unit: dict) -> str:
    a, b = unit["span"]
    return src[a:b].decode("utf-8")


def nbytes(unit: dict) -> int:
    return unit["span"][1] - unit["span"][0]


def byte_offset(text: str, char_index: int) -> int:
    return len(text[:char_index].encode("utf-8"))


def g3_kept(m: re.Match) -> bool:
    return m.group(0) + m.string[m.end():m.end() + 1] not in G3_EXCLUDED


def matches(group: str, text: str):
    for m in GROUPS[group].finditer(text):
        if group == "G3" and not g3_kept(m):
            continue
        yield m


def trigger_class(group: str, words: str) -> str:
    if group == "G1":
        return "definite"
    if group == "G3":
        return "iterative" if re.match(r"(?i)again|return", words) else "change-of-state"
    if group == "G5":
        return "factive"
    return "possessive"


def ledger(units: list[dict], src: bytes) -> list[dict]:
    rows = []
    for u in units:
        text = text_of(src, u)
        entries = []
        for g in GROUPS:
            for m in matches(g, text):
                a = u["span"][0] + byte_offset(text, m.start())
                entries.append({"words": m.group(0), "class": trigger_class(g, m.group(0)), "group": g,
                                "span": [a, a + len(m.group(0).encode("utf-8"))]})
        entries.sort(key=lambda e: (e["span"], e["group"]))
        rows.append({"id": u["id"], "span": u["span"], "status": u["status"], "presupposition_triggers": entries})
    return rows


def units_with(rows: list[dict], group: str) -> list[dict]:
    return [r for r in rows if any(e["group"] == group for e in r["presupposition_triggers"])]


def check(cid: str, what: str, expected, measured, ok: bool) -> dict:
    return {"id": cid, "check": what, "expected": expected, "measured": measured, "pass": bool(ok)}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    csrc, usrc = CONST_SRC.read_bytes(), UDHR_SRC.read_bytes()
    cunits, uunits = load(CONST_RUN), load(UDHR_RUN)
    ctext = csrc.decode("utf-8")
    checks = []

    # D1: the word-level ledger.
    crow, urow = ledger(cunits, csrc), ledger(uunits, usrc)
    for name, rows in (("constitution", crow), ("udhr", urow)):
        (OUT / f"ledger-triggers-{name}.json").write_text(json.dumps(
            {"run": "20261012T1800Z", "definitions": "docs/research/presupposition-phase1.md 1.3", "units": rows},
            ensure_ascii=False, indent=1) + "\n")

    # D2/D3: the heading units.
    heads = [u for u in cunits if u["id"].endswith(".presupposition")]
    hb = sum(nbytes(u) for u in heads)
    all_unf = all(u["status"] == "UNFORMALISED" and "presupposed_claim" in u for u in heads)
    checks.append(check("H1", "heading presupposition units, bytes; all UNFORMALISED with presupposed_claim",
                        {"units": 29, "bytes": 999, "all": True}, {"units": len(heads), "bytes": hb, "all": all_unf},
                        len(heads) == 29 and hb == 999 and all_unf))
    by_id = {u["id"]: u for u in cunits}
    expected_classes = {"A": [5, 145], "B": [4, 149], "C": [7, 284], "D": [2, 72], "E": [11, 349]}
    measured_classes, heading_rows = {}, []
    for cls, ids in CLASSES.items():
        members = [by_id[i + ".presupposition"] for i in ids]
        measured_classes[cls] = [len(members), sum(nbytes(u) for u in members)]
        for u in members:
            title = text_of(csrc, u)
            words = [m.group(0) for m in TITLE_LEXICON.finditer(title)]
            if TITLE_WH.match(title):
                words.insert(0, TITLE_WH.match(title).group(0).strip())
            uid = u["id"].split(".")[0]
            row = {"id": u["id"], "class": cls, "bytes": nbytes(u), "title": title,
                   "presupposed_claim": u.get("presupposed_claim"), "missing_feature": u.get("missing_feature"),
                   "lexicon_words": words}
            if uid in NOUNS:
                noun = re.compile(r"\b" + re.escape(NOUNS[uid]) + r"s?\b", I)
                hits = [{"id": v["id"], "text": text_of(csrc, v)} for v in cunits
                        if re.search(r"\b(?:whether|uncertain)\b", text_of(csrc, v), I) and noun.search(text_of(csrc, v))]
                row["withholding_hits"] = hits
            if uid in TRIGGER_WORDS:
                row["trigger_words"] = TRIGGER_WORDS[uid]
                row["trigger_in_title"] = TRIGGER_WORDS[uid] in title
            heading_rows.append(row)
    a89 = sum(nbytes(by_id[i + ".presupposition"]) for i in CLASSES["A"][:3])
    checks.append(check("H2", "classes A-E (units, bytes); A's first three bytes",
                        {**expected_classes, "A3": 89}, {**measured_classes, "A3": a89},
                        measured_classes == expected_classes and a89 == 89))
    e_with = [r["id"] for r in heading_rows if r["class"] == "E" and r["lexicon_words"]]
    ad_without = [r["id"] for r in heading_rows if r["class"] != "E" and not r["lexicon_words"]]
    checks.append(check("H3", "title lexicon: none in class E; at least one in each of A-D",
                        {"E_with_trigger": [], "A_to_D_without": []},
                        {"E_with_trigger": e_with, "A_to_D_without": ad_without}, not e_with and not ad_without))
    drows = [r for r in heading_rows if r["class"] == "D"]
    h4 = {r["id"]: [h["id"] for h in r["withholding_hits"]] for r in drows}
    checks.append(check("H4", "withholding hits for class D, u0269.s02 among them",
                        {"each_nonempty": True, "contains": "u0269.s02"}, h4,
                        all(v and "u0269.s02" in v for v in h4.values())))
    arows = [r for r in heading_rows if r["class"] == "A"]
    h5 = {r["id"]: [h["id"] for h in r["withholding_hits"]] for r in arows}
    checks.append(check("H5", "withholding hits for class A", {k: [] for k in h5}, h5, not any(h5.values())))
    h6 = {r["id"]: r["trigger_in_title"] for r in arows}
    checks.append(check("H6", "trigger words in the title, class A", {k: True for k in h6}, h6, all(h6.values())))
    (OUT / "headings.json").write_text(json.dumps({"run": "20261012T1800Z", "headings": heading_rows},
                                                  ensure_ascii=False, indent=1) + "\n")

    # O1-O9: occurrences over the whole pinned source.
    def count(rx, keep=None):
        return sum(1 for m in rx.finditer(ctext) if keep is None or keep(m))
    occ = [("O1", "G1", count(G1), 101, "eq"), ("O2", "the role's possessive", count(O2_RE), 23, "eq"),
           ("O3", "(Claude|Anthropic)'s", count(O3_RE), 205, "ge"), ("O4", "G6", count(G6), 17, "eq"),
           ("O5", "G3n", count(G3_NARROW), 18, "eq"), ("O6", "remain…", count(O6_RE), 15, "eq"),
           ("O7", "still (any case)", count(O7_RE), 17, "eq"), ("O8", "again / return to (any case)", count(O8_RE), 4, "eq"),
           ("O9", "G5", count(G5), 46, "eq")]
    for cid, what, got, exp, rel in occ:
        checks.append(check(cid, "source occurrences, " + what, exp if rel == "eq" else f">= {exp}", got,
                            got == exp if rel == "eq" else got >= exp))

    # U1-U4: units over whole spans; U5: UDHR headings.
    u1 = units_with(crow, "G1")
    u2 = units_with(crow, "G2")
    u3 = units_with(crow, "G3")
    u4 = units_with(crow, "G4")
    b = lambda rows: sum(r["span"][1] - r["span"][0] for r in rows)
    checks.append(check("U1", "units with G1", ">= 68", len(u1), len(u1) >= 68))
    checks.append(check("U2", "units with G2 (units, bytes)", ">= 22 / >= 4833", [len(u2), b(u2)],
                        len(u2) >= 22 and b(u2) >= 4833))
    checks.append(check("U3", "units with G3 (units, bytes)", ">= 36 / >= 6887", [len(u3), b(u3)],
                        len(u3) >= 36 and b(u3) >= 6887))
    checks.append(check("U4", "units with G4", ">= 172", len(u4), len(u4) >= 172))
    uheads = [u for u in uunits if u["id"].endswith(".presupposition") or "presupposed_claim" in u]
    checks.append(check("U5", "UDHR heading presupposition units", 0, len(uheads), not uheads))

    # Information (no expected value): status of trigger-bearing units, the co-blocker candidates.
    info = {}
    for name, rows in (("constitution", crow), ("udhr", urow)):
        with_any = [r for r in rows if r["presupposition_triggers"]]
        by_status = {}
        for r in with_any:
            s = by_status.setdefault(r["status"], [0, 0])
            s[0] += 1
            s[1] += r["span"][1] - r["span"][0]
        info[name] = {"units": len(rows), "units_with_a_trigger": len(with_any), "by_status": by_status,
                      "entries": sum(len(r["presupposition_triggers"]) for r in rows),
                      "entries_by_group": {g: sum(1 for r in rows for e in r["presupposition_triggers"] if e["group"] == g)
                                           for g in GROUPS},
                      "units_by_group": {g: [len(units_with(rows, g)), b(units_with(rows, g))] for g in GROUPS},
                      "G1_or_G2_units": len([r for r in rows if any(e["group"] in ("G1", "G2")
                                                                      for e in r["presupposition_triggers"])])}
    result = {"run": "20261012T1800Z", "definitions": "docs/research/presupposition-phase1.md 1.3-1.4",
              "checks": checks, "passed": sum(c["pass"] for c in checks), "total": len(checks), "information": info}
    (OUT / "census-checks.json").write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n")
    for c in checks:
        print(f"{c['id']:3} {'PASS' if c['pass'] else 'FAIL'}  expected {c['expected']}  measured {c['measured']}")
    print(json.dumps(info, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
