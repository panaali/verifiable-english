#!/usr/bin/env python3
"""Run 20261021T0600Z: the document changes of this run, applied to the input of `nd.py` (`translation-without-content.ve.md`) and to the strict companions.

The audit of run 20261020T1800Z (AUDIT-20261020T1800Z-received.md: 22 of 26 sampled verdicts faithful, four unfaithful) marked four units. This script repairs them:

  * u0168.s01 (“Claude should remain firm” under seemingly compelling arguments): the guard `seemingly_compelling_argument_to_cross_line(s)` took only the situation, so one instance
    facing an argument made every instance firm. The open term is now binary on (claude_instance, situation) and the guard binds the acting instance (de Bruijn: c is var 1, s is var 0).
  * u0156.s03 (“Claude shouldn’t actively deceive the user about the existence of a system prompt or its content”): the in-frame candidates took a unary frame term on the instance, so a
    request in one context governed every user for that instance. The frame term is now binary on (claude_instance, user), like the exception term and the regulated act
    (c is var 1, u is var 0); a third argument for the situation is impossible (the relational profile allows at most two arguments per predicate, lean/VE/Route/Wire.lean), so the pair
    (instance, user) stands for the conversation. The regulated act is unchanged. frame_u0156.py owns the wording.
  * u0036.s05 (“Claude should ask for clarification in cases of genuine ambiguity”): the rendering of the reading set says “c is not required to” for the default candidate in the
    separating situation (`ve/readings_english.py` `outcome_sentence`, a product wording the translator cannot change); the audit holds that this turns silence into an exemption.
    Not repairable in the translation, so the unit goes back to UNFORMALISED (`other.silence-display`) and its set, predicates, open terms and stored situations go with it
    (REMOVE EVERY TRACE). u0263.s04.p2 has the same candidate shape and the same rendering sentence (`rendered-raw.md`), so it goes the same way (as the 12 October repair took
    the three hard constraints the audit had not sampled together with the four it had).
  * u0013.presupposition (“Claude’s core values”): the prompt's PS-0p step 3 says not to claim u0013; the audit rejected the claim for that reason. The unit is UNFORMALISED again
    (`other.discourse`), the predicate `core_value_of` and its fence are removed with every trace.

    uv run python .../repair_20261021T0600Z.py          # edits translation-without-content.ve.md and readings/all-strict*.ve.md in place; refuses a second run
"""
from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(RUN))

_spec = importlib.util.spec_from_file_location("readings_s1_pilot", ROOT / "tools/readings_s1_pilot.py")
pilot = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pilot)
import frame_u0156 as fr  # noqa: E402
import spec_nd as nd  # noqa: E402

RUN_ID = "20261021T0600Z"
FIRM_TERM = "seemingly_compelling_argument_to_cross_line"
FIRM_ENGLISH = "{0} faces seemingly compelling arguments to cross the lines drawn by the hard constraints in {1}"
FIRM_DESCRIPTION = ("The instance of Claude faces seemingly compelling arguments to cross the hard-constraint lines in the situation; open term. "
                    "It binds the acting instance: another instance in the same situation does not face them unless the term holds for it too.")
SILENCE = "other.silence-display"
# (unit, set id, predicates and open terms that go with it)
DEMOTED = {
    "u0036.s05": ("force-u0036-s05", ["clarification_required", "genuine_ambiguity"]),
    "u0263.s04.p2": ("force-u0263-s04-p2", ["exploit_instruction_compliance_required", "explicit_instruction_against_exploits"]),
}
GONE_PREDICATES = [p for _, (_, ps) in DEMOTED.items() for p in ps] + ["core_value_of"]
U0013 = "u0013.presupposition"


def drop_relation(x, name):
    if isinstance(x, dict):
        if isinstance(x.get("relations"), dict):
            x["relations"].pop(name, None)
        for v in x.values():
            drop_relation(v, name)
    elif isinstance(x, list):
        for v in x:
            drop_relation(v, name)


def unformalised(unit, feature):
    span = unit["span"]
    unit.clear()
    unit.update({"id": None, "span": span, "support": "none", "kind": ["unformalised", feature], "meaning": {"unformalised": feature}})


def edit_common(meta):
    """The vocabulary and rules every document carries: u0168.s01's binary term, the demoted units' predicates."""
    voc = meta["environment"]["vocabulary"]["predicates"]
    pred = voc[FIRM_TERM]
    assert pred["arguments"] == ["situation"], pred["arguments"]
    pred["arguments"] = ["claude_instance", "situation"]
    pred["verbalisation"] = FIRM_ENGLISH
    pred["description"] = FIRM_DESCRIPTION
    term = next(t for t in meta["open_terms"] if t["name"] == FIRM_TERM)
    assert term["arguments"] == ["situation"]
    term["arguments"] = ["claude_instance", "situation"]
    for unit in pilot._flat(meta["units"]):
        if unit["id"] == "u0168.s01":
            guard = unit["content"]["norm"]["guard"]
            assert guard == ["unary", FIRM_TERM, ["var", 0]], guard
            unit["content"]["norm"]["guard"] = ["binary", FIRM_TERM, ["var", 1], ["var", 0]]
    for unit_id, (_, preds) in DEMOTED.items():
        for u in pilot._flat(meta["units"]):
            if u["id"] == unit_id:
                assert u["kind"] == "norm", u
                unformalised(u, SILENCE)
                u["id"] = unit_id
        for p in preds:
            assert p in voc, p
            del voc[p]
            meta["open_terms"] = [t for t in meta["open_terms"] if t["name"] != p]
            drop_relation(meta.get("reading_sets", []), p)
    return meta


def edit_main(meta, body):
    meta = edit_common(meta)
    voc = meta["environment"]["vocabulary"]["predicates"]
    # the two sets of the demoted units go; the other two keep their place
    before = [s["id"] for s in meta["reading_sets"]]
    assert before == ["force-u0036-s05", "force-u0156-s03", "force-u0263-s04-p2", "scope-u0165-s03"], before
    gone = [s for s, _ in DEMOTED.values()]
    meta["reading_sets"] = [s for s in meta["reading_sets"] if s["id"] not in gone]
    # u0013.presupposition: UNFORMALISED again, with its predicate and fence
    assert "core_value_of" in voc
    by = {u["id"]: u for u in meta["units"]}
    u = by[U0013]
    assert u["kind"] == "asserted" and u["content"] == {"fence": U0013}
    unformalised(u, "other.discourse")
    u["id"] = U0013
    del voc["core_value_of"]
    meta["open_terms"] = [t for t in meta["open_terms"] if t["name"] != "core_value_of"]
    fence = f"```ve {U0013}\nSome thing is a core value of claude.\n```\n".encode()
    assert body.count(fence) == 1
    body = body.replace(fence, b"")
    # the stored placeholder models and identities of this input are not read (nd.py drops `models` and rebuilds every meaning id over the finished environment)
    assert [s["id"] for s in meta["reading_sets"]] == ["force-u0156-s03", "scope-u0165-s03"]
    return meta, body


def frame_companion(strict_meta):
    """The strict companion with u0156.s03 as the strict-in-frame rule (as repair_20261017T1800Z.frame_companion did, with the binary frame term)."""
    meta = copy.deepcopy(strict_meta)
    meta["environment"]["vocabulary"]["predicates"][fr.FRAME_TERM] = nd.base(fr.FRAME_SORTS, fr.ENGLISH, fr.DESCRIPTION)
    meta["open_terms"].append({"name": fr.FRAME_TERM, "arguments": list(fr.FRAME_SORTS), "decided_by": "unresolved_decider", "necessary": [], "sufficient": [],
                               "factors": list(fr.FACTORS), "precedents": [], "jurisdiction": "claude_constitution", "version": 1})
    for u in pilot._flat(meta["units"]):
        if u["id"] == fr.UNIT:
            u["content"] = fr.with_frame(u["content"])
            now = u["meaning"]
            u["meaning"] = {"open": [fr.FRAME_TERM]} if now == "specified" else {"open": [*now["open"], fr.FRAME_TERM]}
    return meta


def no_traces(meta, where):
    text = json.dumps(meta, ensure_ascii=False)
    for name in GONE_PREDICATES + ["exception_to_asking_for_clarification", "exception_to_complying_with_exploit_instruction", "force-u0036-s05", "force-u0263-s04-p2"]:
        assert name not in text, (where, name)


def main():
    main_path = RUN / "translation-without-content.ve.md"
    raw = main_path.read_bytes()
    assert b"core_value_of" in raw, "already repaired"
    _, front, body = raw.split(b"---\n", 2)
    meta, body = edit_main(json.loads(front), body)
    no_traces(meta, "main")
    main_path.write_bytes(b"---\n" + json.dumps(meta, ensure_ascii=False).encode() + b"\n---\n" + body)
    strict, strict_source = pilot.read(RUN / "readings/all-strict.ve.md")
    strict = edit_common(strict)
    no_traces(strict, "strict")
    pilot.write(RUN / "readings/all-strict.ve.md", strict, strict_source)
    narrow, narrow_source = pilot.read(RUN / "readings/all-strict-narrow.ve.md")
    narrow = edit_common(narrow)
    no_traces(narrow, "narrow")
    pilot.write(RUN / "readings/all-strict-narrow.ve.md", narrow, narrow_source)
    companion = frame_companion(strict)
    no_traces(companion, "frame")
    pilot.write(RUN / "readings/all-strict-in-frame.ve.md", companion, strict_source)
    print("ok:", [s["id"] for s in meta["reading_sets"]], len(meta["open_terms"]), "open terms in the main document")


if __name__ == "__main__":
    main()
