#!/usr/bin/env python3
"""Run 20261019T1800Z: the document changes of this run, applied to `translation-without-content.ve.md` (the input of `nd.py`).

  * FEATURE UPGRADE (ps-6r merged: the four relational-noun idioms “{0} is a core value / guideline / mission / nature of {1}” are admitted by the English lint, evidence/ps6r/wording-lint.json):
    the heading presuppositions of u0013 (“Claude’s core values”), u0095 (“Following Anthropic’s guidelines”), u0002 (“Claude and the mission of Anthropic”) and u0235 (“Claude’s nature”) are
    stated as existence claims with the new wordings, as u0286 and u0245 are. Each is the existence of a thing with that relation to its owner, nothing more (the PS-0p audit rule).
  * AUDIT REPAIR (audit of 20261019T0600Z, u0032.presupposition UNFAITHFUL: its English “Some thing is helpful.” drops “genuine” and “constitutes”): the unit goes back to UNFORMALISED
    (other.discourse), the predicate `genuine_helpfulness`, its open term and its fence are removed with every trace. The merged wordings do not help (no idiom for “constitutes genuine helpfulness”).

    uv run python .../repair_20261019T1800Z.py          # edits translation-without-content.ve.md in place; refuses a second run
"""
from __future__ import annotations
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
TARGET = RUN / "translation-without-content.ve.md"
SPLIT = b"---\n"

# unit -> (predicate, argument sorts, wording, owner constant, fence, description)
UNITS = {
    "u0013.presupposition": ("core_value_of", ["entity", "entity"], "{0} is a core value of {1}", "claude", "Some thing is a core value of claude.",
                             "The first thing is a core value of the second, in the source's sense (u0013, “Claude’s core values”). Declared for the heading's presupposition (PS-0p, wording PS-6r): "
                             "the heading takes for granted that Claude has core values, and nothing more."),
    "u0095.presupposition": ("guideline_of", ["entity", "principal_type"], "{0} is a guideline of {1}", "anthropic", "Some thing is a guideline of anthropic.",
                             "The first thing is a guideline of the second, in the source's sense (u0095, “Following Anthropic’s guidelines”). The second argument has the sort that holds the constant "
                             "`anthropic` (u0043.s02), so Anthropic is one constant in the document. Declared for the heading's presupposition (PS-0p, wording PS-6r): the heading takes for granted that "
                             "Anthropic has guidelines, and nothing more."),
    "u0002.presupposition": ("mission_of", ["entity", "principal_type"], "{0} is a mission of {1}", "anthropic", "Some thing is a mission of anthropic.",
                             "The first thing is a mission of the second, in the source's sense (u0002, “Claude and the mission of Anthropic”). The second argument has the sort that holds the constant "
                             "`anthropic` (u0043.s02), so Anthropic is one constant in the document. Declared for the heading's presupposition (PS-0p, wording PS-6r): the heading takes for granted that "
                             "Anthropic has a mission, and nothing more (not that it has exactly one)."),
    "u0235.presupposition": ("nature_of", ["entity", "entity"], "{0} is a nature of {1}", "claude", "Some thing is a nature of claude.",
                             "The first thing is a nature of the second, in the source's sense (u0235, “Claude’s nature”). Declared for the heading's presupposition (PS-0p, wording PS-6r): the heading "
                             "takes for granted that Claude has a nature, and nothing more."),
}
OLD = "u0032.presupposition"


def main(argv=()):
    global TARGET
    only = None
    rename = {}
    unique = False
    for a in argv:
        if a.startswith("--rename="):   # a measurement option (premise-check variants): predicate identifiers, never wordings
            rename = dict(x.split(":") for x in a[len("--rename="):].split(",") if x)
        elif a == "--unique-u0002":    # a measurement option: u0002 as "exactly one mission" (the definite's uniqueness)
            unique = True
        if a.startswith("--only="):
            only = [x + ".presupposition" for x in a[len("--only="):].split(",") if x]
        elif a.startswith("--target="):
            TARGET = Path(a[len("--target="):])
    raw = TARGET.read_bytes()
    _, front, body = raw.split(SPLIT, 2)
    meta = json.loads(front)
    voc = meta["environment"]["vocabulary"]
    assert "genuine_helpfulness" in voc["predicates"], "repair already applied"
    by = {u["id"]: u for u in meta["units"]}
    # 1. audit repair: u0032 back to UNFORMALISED, with every trace removed
    u = by[OLD]
    assert u["kind"] == "asserted" and u["meaning"] == {"open": ["genuine_helpfulness"]}
    by[OLD].clear()
    by[OLD].update({"id": OLD, "span": [17290, 17328], "support": "none", "kind": ["unformalised", "other.discourse"], "meaning": {"unformalised": "other.discourse"}})
    del voc["predicates"]["genuine_helpfulness"]
    meta["open_terms"] = [t for t in meta["open_terms"] if t["name"] != "genuine_helpfulness"]
    fence = f"```ve {OLD}\nSome thing is helpful.\n```\n".encode()
    assert body.count(fence) == 1
    body = body.replace(fence, b"")
    # 2. the four upgrades
    fences = b""
    for uid, (pred, args, wording, owner, text, desc) in UNITS.items():
        if only is not None and uid not in only:
            continue
        u = by[uid]
        assert u["kind"] == ["unformalised", "other.discourse"] and pred not in voc["predicates"], uid
        pred = rename.get(pred, pred)
        if unique and uid == "u0002.presupposition":
            text = ("There is a first thing such that both of the following hold:\n  (a) the first thing is a mission of anthropic;\n"
                    "  (b) for every second thing that is a mission of anthropic, the second thing is the same as the first thing.")
        voc["predicates"][pred] = {"arguments": args, "description": desc, "verbalisation": wording}
        u.clear()
        u.update({"id": uid, "span": SPAN[uid], "support": "assumption", "kind": "asserted", "meaning": "specified", "content": {"fence": uid}, "surface": "english"})
        fences += f"```ve {uid}\n{text}\n```\n".encode()
    assert body.endswith(b"```\n")
    body += fences
    TARGET.write_bytes(SPLIT + json.dumps(meta, ensure_ascii=False).encode() + b"\n" + SPLIT + body)
    assert b"genuine_helpfulness" not in json.dumps(meta).encode()
    print("repaired", OLD, "upgraded", [u for u in UNITS if only is None or u in only])


SPAN = {"u0002.presupposition": [17, 54], "u0013.presupposition": [6120, 6144], "u0095.presupposition": [58219, 58255], "u0235.presupposition": [149641, 149660]}

if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
