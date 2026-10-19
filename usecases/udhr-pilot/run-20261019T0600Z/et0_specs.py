"""Companion documents with Lean status witnesses for ET-0's u042 and u043 (the pre-registered content, the same rule the part holds).

Each companion holds one candidate's rule over only the vocabulary it uses, under norm-defaults@0 with the completion 'unspecified'; its Lean
`norm-defaults-status` rows say, for a small model, whether the rule SETTLES the case (the permission is false) or leaves it UNDECIDED.
They are checks of meaning, not part of the translation: the translation is in translation-part01.ve.md.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2]))

import et0_apply as E  # noqa: E402

PART = HERE / "translation-part01.ve.md"


def _front():
    return json.loads(PART.read_bytes().split(b"---\n", 2)[1])


def _spec(unit_id, cid, rule, sorts, predicates, open_terms, witnesses):
    front = _front()
    voc = front["environment"]["vocabulary"]
    unit = next(u for u in front["units"] if u["id"] == unit_id)
    return {"sorts": {s: voc["sorts"][s] for s in sorts}, "predicates": {p: voc["predicates"][p] for p in predicates},
            "rule": rule, "open": [t for t in open_terms],
            "open_terms": [t for t in front["open_terms"] if t["name"] in open_terms], "witnesses": witnesses, "unit": unit_id, "span": unit["span"]}


def specs():
    front = _front()
    u042 = next(u for u in front["units"] if u["id"] == "u042")["content"]
    item = next(s for s in front["reading_sets"] if s["unit"] == "u043")
    rules = {r["id"]: r["content"] for r in item["readings"]}
    out = {}
    sorts42 = ["finding", "act", "day"]
    preds42 = ["finding_of_guilt_permitted", "on_account_of", "committed_on", "constitutes_penal_offence_on"]
    d42 = {"finding": ["f1", "f2"], "act": ["a1"], "day": ["d1"]}
    out["u042.prohibited"] = _spec("u042", "prohibited", u042, sorts42, preds42, [], [
        # f1 is on account of a1, committed on d1, and a1 did not constitute a penal offence on d1: the finding is not permitted (SETTLED no)
        (d42, {"on_account_of": [["f1", "a1"]], "committed_on": [["a1", "d1"]]},
         [("finding_of_guilt_permitted", ("f1",), ("SETTLED", False)),
          ("finding_of_guilt_permitted", ("f2",), ("UNDECIDED", None))]),     # f2 is on account of no act: the rule says nothing about it
        # a1 did constitute a penal offence on d1: the rule does not apply, the finding is not forbidden by it (UNDECIDED, never permitted)
        (d42, {"on_account_of": [["f1", "a1"]], "committed_on": [["a1", "d1"]], "constitutes_penal_offence_on": [["a1", "d1"]]},
         [("finding_of_guilt_permitted", ("f1",), ("UNDECIDED", None))])])
    sorts43 = ["imposition", "penalty", "applicability", "act", "day"]
    preds43 = ["imposition_permitted", "imposes", "imposed_for", "committed_on", "applicability_of", "applicability_to", "applicable_on", "heavier_than"]
    d43 = {"imposition": ["i1"], "penalty": ["pn_mid", "pn_light", "pn_heavy"], "applicability": ["ap_light", "ap_heavy"], "act": ["ac1"], "day": ["dy1"]}
    common = {"imposes": [["i1", "pn_mid"]], "imposed_for": [["i1", "ac1"]], "committed_on": [["ac1", "dy1"]]}
    both = {"applicability_to": [["ap_light", "ac1"], ["ap_heavy", "ac1"]], "applicable_on": [["ap_light", "dy1"], ["ap_heavy", "dy1"]],
            "applicability_of": [["ap_light", "pn_light"], ["ap_heavy", "pn_heavy"]]}
    one = {"applicability_to": [["ap_light", "ac1"]], "applicable_on": [["ap_light", "dy1"]], "applicability_of": [["ap_light", "pn_light"]]}
    for cid, on_both in (("universal", ("UNDECIDED", None)), ("existential", ("SETTLED", False))):
        out[f"u043.{cid}"] = _spec("u043", cid, rules[cid], sorts43, preds43, ["heavier"], [
            # two penalties were applicable on that day; the imposed one is heavier than the lighter but not than the heavier: the readings part here
            (d43, {**common, **both, "heavier_than": [["pn_mid", "pn_light"]]}, [("imposition_permitted", ("i1",), on_both)]),
            # one penalty was applicable and the imposed one is heavier: both readings forbid it
            (d43, {**common, **one, "heavier_than": [["pn_mid", "pn_light"]]}, [("imposition_permitted", ("i1",), ("SETTLED", False))]),
            # heavier than both applicable penalties: both readings forbid it
            (d43, {**common, **both, "heavier_than": [["pn_mid", "pn_light"], ["pn_mid", "pn_heavy"]]}, [("imposition_permitted", ("i1",), ("SETTLED", False))]),
            # not heavier than any applicable penalty: neither reading applies (UNDECIDED, never permitted)
            (d43, {**common, **both, "heavier_than": []}, [("imposition_permitted", ("i1",), ("UNDECIDED", None))]),
            # no penalty was applicable on that day: neither reading applies
            (d43, {**common, "heavier_than": [["pn_mid", "pn_light"]]}, [("imposition_permitted", ("i1",), ("UNDECIDED", None))])])
    return out


def write_companion(directory: Path, key: str, spec: dict, source: bytes) -> Path:
    import udhr_specs as U
    uid, cid = key.split(".")
    a, b = spec["span"]
    meta = {"format": "ve-document@1", "environment": U.environment(U.PROFILES, spec["sorts"], spec["predicates"]),
            "open_terms": copy.deepcopy(spec["open_terms"]),
            "units": [{"content": spec["rule"], "id": f"{uid}_{cid}", "kind": "norm",
                       "meaning": ({"open": list(spec["open"])} if spec["open"] else "specified"), "span": [0, b - a], "support": "none"}]}
    path = directory / f"{uid}.{cid}.ve.md"
    path.write_bytes(b"---\n" + json.dumps(meta, ensure_ascii=False, sort_keys=True, indent=2).encode() + b"\n---\n" + source[a:b])
    return path


if __name__ == "__main__":
    raw = (HERE.parent / "source" / "udhr.md").read_bytes()
    import witnesses_nd as WND
    from ve.document import check_document
    for key, spec in specs().items():
        path = write_companion(HERE / "readings", key, spec, raw)
        verdict = check_document(path)
        outs = WND.run(path, spec)
        print(key, verdict["premises"]["status"], [(o["lean_point_status"], o["as_expected"]) for o in outs], flush=True)
