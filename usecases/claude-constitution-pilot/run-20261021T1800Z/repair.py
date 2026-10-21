#!/usr/bin/env python3
"""Run 20261008T0600Z: the "readings come from the words only" repair of the previous run's translation.

    python3 -I usecases/claude-constitution-pilot/run-20261008T0600Z/repair.py

Starts from run 20261007T1800Z's files (prev/), writes translation.ve.md, readings/{all-strict,all-default,s1}.ve.md and the
ledger notes; asserts the starting point first. Changes (see AUDIT-REPAIR.md):

1. u0052.s01 "Claude should always use good judgment ...": the defeasible reading is removed. "always" excludes exceptions in the
   sentence itself and nothing the text says implies one (the lead's rule: no defeasible reading of "always"/"never" unless the text
   states or clearly implies exceptions). The unit keeps its one strict reading as content (READINGS -> OPEN).
2. The other four "should" force sets keep both readings, now with the text spans that admit them (the words, not outside knowledge).
3. Four open terms that no unit uses (broad_safety, appropriate_oversight, genuine_helpfulness, ethical_harm) are removed: their
   "factors" were the translator's, not questions the text raises at any covered unit. good_judgment's factors become the one question
   its own words raise.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
PREV = RUN / "prev"
DOCS = {"main": "translation.ve.md", "strict": "readings/all-strict.ve.md", "default": "readings/all-default.ve.md", "s1": "readings/s1.ve.md"}
UNUSED_TERMS = ("broad_safety", "appropriate_oversight", "genuine_helpfulness", "ethical_harm")
CTX_SHOULD = (" The words admit both: “should” is “directive language” in this document (u0253.s04: “While we often use directive language like "
              "“should” in this document, our hope is that …”) and the document says it generally favours judgment over strict rules "
              "(u0011.s01: “We generally favor cultivating good values and judgment over strict rules and decision procedures”). "
              "Added in run 20261008T0600Z: the reading comes from these spans, not from outside knowledge.")
CTX_HONESTY = (" The text itself implies exceptions to the honesty norm this sentence applies: “Claude should basically never directly lie or actively "
               "deceive anyone it’s interacting with” (u0109.s06) and honesty is not a hard constraint but is meant to function as “something quite "
               "similar to one” (u0109.s05). Added in run 20261008T0600Z: the defeasible reading comes from these spans, not from outside knowledge.")
SHOULD_SETS = {"force-u0036-s05": CTX_SHOULD, "force-u0263-s04-p2": CTX_SHOULD,
               "force-u0125-s04-p2": CTX_HONESTY, "force-u0156-s03": CTX_HONESTY}


def split(path: Path):
    t = path.read_text(encoding="utf-8")
    end = t.index("\n---\n", 4)
    return json.loads(t[4:end]), t[end + 5:]


def join(fm, body):
    return "---\n" + json.dumps(fm, separators=(",", ":"), ensure_ascii=False) + "\n---\n" + body


def patch_terms(fm):
    fm["open_terms"] = [o for o in fm["open_terms"] if o["name"] not in UNUSED_TERMS]
    for o in fm["open_terms"]:
        if o["name"] == "good_judgment":
            o["factors"] = ["what counts as good judgment"]


def strict_unit(strict_fm):
    return next(u for u in strict_fm["units"] if u["id"] == "u0052.s01")


def main():
    strict_fm, _ = split(PREV / "all-strict.ve.md") if (PREV / "all-strict.ve.md").exists() else split(RUN / DOCS["strict"])
    unit = strict_unit(strict_fm)
    assert unit["content"]["norm"]["predicate"] == "judgment_use_required" and "mode" not in unit["content"]["norm"]
    for key, rel in DOCS.items():
        fm, body = split(RUN / rel)
        if key == "main":
            old = [r["id"] for r in fm["reading_sets"]]
            assert "force-u0052-s01" in old, "repair already applied or wrong start"
        patch_terms(fm)
        for u in fm["units"]:
            if u["id"] == "u0052.s01":
                u["meaning"] = {"open": ["good_judgment"]}
                u["content"] = unit["content"] if key != "s1" else unit["content"]
        if "reading_sets" in fm:
            fm["reading_sets"] = [r for r in fm["reading_sets"] if r["id"] != "force-u0052-s01"]
            if key == "main":
                for r in fm["reading_sets"]:
                    if r["id"] in SHOULD_SETS:
                        for c in r["readings"]:
                            c["admission"]["why"] += SHOULD_SETS[r["id"]]
        (RUN / rel).write_text(join(fm, body), encoding="utf-8")
    # ledger
    ledger = json.load(open(RUN / "units.json"))
    for e in ledger:
        if e["id"] == "u0052.s01":
            e["status"] = "OPEN"
            e["note"] = ("One reading, a strict duty: “Claude should always use good judgment when evaluating conversational inputs”. “Always” excludes "
                         "exceptions in the sentence itself and nothing in the text states or implies one, so the defeasible reading earlier runs offered is "
                         "removed (run 20261008T0600Z, repair under the rule that readings come from the words only). “Good judgment” is the open term "
                         "good_judgment, with one question, what counts as good judgment. The duty is on instances of Claude only; where no rule decides, "
                         "the text does not say (completion `unspecified`), so VE reports UNDECIDED.")
            e["reading_set"] = None
            e["readings"] = [{"id": "strict", "in": "translation.ve.md and readings/all-strict.ve.md", "predicate": "judgment_use_required",
                              "completion": "unspecified",
                              "english": "Every instance of Claude must use good judgment when evaluating conversational inputs.", "english_round_trip": True,
                              "meaning": "a strict rule"}]
            e["document_status"] = "OPEN (one strict reading; its open term is good_judgment)"
            e["audit_repair"] = ("Run 20261008T0600Z: the defeasible reading (“should use good judgment”, a rule with an open exception) is removed: “always” "
                                 "excludes exceptions and the text states none. The unit changed, so any earlier acceptance of its READINGS form does not count; "
                                 "counted as claimed, not audit-verified.")
            e.pop("s1_demonstration_only", None)
        elif e["id"] in ("u0036.s05", "u0263.s04.p2"):
            e["note"] += CTX_SHOULD
        elif e["id"] in ("u0125.s04.p2", "u0156.s03"):
            e["note"] += CTX_HONESTY
    json.dump(ledger, open(RUN / "units.json", "w"), indent=2, ensure_ascii=False)
    open(RUN / "units.json", "a").write("\n")
    print("repaired")


if __name__ == "__main__":
    sys.exit(main())
