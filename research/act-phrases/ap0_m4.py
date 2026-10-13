"""AP-0 item 3: tag the constitution's norm units with `act_workaround` (rule: docs/research/act-phrases-phase1.md 1.4).

    uv run python research/act-phrases/ap0_m4.py [RUN_DIR]

Reads the pilot run read-only and writes docs/research/evidence/act-phrases/m4-act-workaround.json. No model call.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = Path(sys.argv[1] if len(sys.argv) > 1 else
           "/home/seyran/code/manage-agents/pilots/claude-constitution/run-20261012T1800Z")
OUT = ROOT / "docs/research/evidence/act-phrases/m4-act-workaround.json"
MARKERS = {"in", "about", "to", "by", "of", "for", "with"}
# The research note's hand groups (docs/research/act-phrases.md 2.2), for comparison only.
NOTE = {**{f"u0165.s0{i}": "pointer" for i in range(1, 8)},
        **{u: "folded" for u in ("u0062.s01", "u0123.s01.p1", "u0123.s02.p1", "u0123.s03")},
        **{u: "shortened" for u in ("u0125.s04.p2", "u0156.s03", "u0052.s01", "u0073.s05", "u0036.s05",
                                    "u0263.s04.p2", "u0168.s01")}}


def words(text):
    text = text.lower().replace("’", "'").replace("*", "")
    return [w for w in re.split(r"[^a-z0-9'\-]+", text) if w]


def act_runs(act):
    tokens = act.split()
    assert tokens[0] == "{0}", act
    runs, cur = [], []
    for tok in tokens[1:]:
        if re.fullmatch(r"\{\d+\}", tok):
            if cur:
                runs.append((cur, True))
            cur = []
        else:
            cur.append(tok)
    if cur:
        runs.append((cur, False))
    out = []
    for run, before_slot in runs:
        ws = words(" ".join(run))
        if before_slot and len(ws) == 1 and ws[0] in MARKERS:
            continue
        if ws:
            out.append(ws)
    return out


def contiguous(run, src):
    n = len(run)
    return any(src[i:i + n] == run for i in range(len(src) - n + 1))


def has_or(node, depth=0):
    """A disjunction of two or more atoms anywhere in the guard."""
    if not isinstance(node, list) or not node:
        return False
    if node[0] == "or":
        return True
    return any(has_or(child) for child in node[1:] if isinstance(child, list))


def tag(act, guard, src_words):
    first = act.split()[1].lower()
    if first == "do" and "do" not in src_words:
        return "pointer", "the act begins with 'do', which the source does not say"
    if has_or(guard):
        return "folded", "the guard is a disjunction of case atoms"
    missing = [" ".join(r) for r in act_runs(act) if not contiguous(r, src_words)]
    if missing:
        return "shortened", "act words not in the source as written: " + "; ".join(repr(m) for m in missing)
    return "none", "every act run occurs in the source as written"


def main():
    text = (RUN / "translation.ve.md").read_text()
    end = text.index("\n---\n", 4)
    doc = json.loads(text[4:end])
    body = text[end + 5:].encode()
    preds = doc["environment"]["vocabulary"]["predicates"]
    rows = []
    for unit in doc["units"]:
        if unit.get("kind") != "norm":
            continue
        norm = (unit.get("content") or {}).get("norm")
        origin = "unit"
        if norm is None:
            rs = next(r for r in doc["reading_sets"] if r["unit"] == unit["id"])
            norm, origin = rs["readings"][0]["content"]["norm"], f"reading set {rs['id']}, first reading"
        start, stop = unit["span"]
        source = body[start:stop].decode()
        act = preds[norm["predicate"]]["regulated"]["act"]
        workaround, why = tag(act, norm["guard"], words(source))
        rows.append({"unit": unit["id"], "bytes": stop - start, "predicate": norm["predicate"], "rule_from": origin,
                     "act": act, "source": source.strip(), "act_workaround": workaround, "reason": why,
                     "research_note_group": NOTE.get(unit["id"]),
                     "agrees_with_note": workaround == NOTE.get(unit["id"])})
    tally = {}
    for r in rows:
        t = tally.setdefault(r["act_workaround"], {"units": 0, "bytes": 0})
        t["units"] += 1
        t["bytes"] += r["bytes"]
    m4 = [r for r in rows if r["act_workaround"] != "none"]
    result = {"run": str(RUN), "rule": "docs/research/act-phrases-phase1.md 1.4", "norm_units": len(rows),
              "norm_bytes": sum(r["bytes"] for r in rows), "tally": tally,
              "m4_after": {"units": len(m4), "bytes": sum(r["bytes"] for r in m4)},
              "m4_before": {"units": 18, "bytes": 2580},
              "disagreements_with_note": [r["unit"] for r in rows if not r["agrees_with_note"]], "units": rows}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({k: result[k] for k in ("norm_units", "norm_bytes", "tally", "m4_after", "disagreements_with_note")}))
    for r in rows:
        print(f"{r['unit']:14} {r['bytes']:4} {r['act_workaround']:10} note={r['research_note_group']}  {r['reason']}")


if __name__ == "__main__":
    main()
