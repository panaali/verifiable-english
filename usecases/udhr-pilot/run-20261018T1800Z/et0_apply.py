"""ET-0 rerun (events-time-causation plan, section 5): UDHR u042 and u043 with an event sort and a day sort.

    uv run --frozen python usecases/udhr-pilot/run-20261018T1800Z/et0_apply.py u042     # stage 1: u042 into part01 and the whole declaration
    uv run --frozen python usecases/udhr-pilot/run-20261018T1800Z/et0_apply.py u043     # stage 2: u043 as a reading set of both readings

The pre-registered content is read from research/events-time-causation-p1 (`git show`, never checked out) and used unchanged:
docs/research/evidence/events-time-causation/et0/part01.u042u043.ve.md (vocabulary entries, the two units' content, the term `heavier`).
Nothing here calls a model.  Reading-set ids are recomputed by vocab_patch.py after each vocabulary change.

u043's second reading (the existential one) is derived from the pre-registered universal guard by replacing `forall applicability. applicable -> ...`
with `exists applicability. applicable and ...`; both guards are written out in this file so that a reader can compare them with the evidence.
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import integrate as I  # noqa: E402
import readings_s1_pilot as P  # noqa: E402
import vocab_patch as V  # noqa: E402
from ve.errors import VEError  # noqa: E402
from ve.readings_route import document_wire, run_lean  # noqa: E402
from ve.readings_s1 import Decoded, guard_base, record_situations, search, wire  # noqa: E402

BRANCH = "research/events-time-causation-p1"
EVIDENCE = "docs/research/evidence/events-time-causation/et0/part01.u042u043.ve.md"
DOCS = {"part01": HERE / "translation-part01.ve.md", "whole": HERE / "experiment-whole" / "translation-whole.ve.md"}

STAGE1 = {"sorts": ["finding", "act", "day"],
          "predicates": ["finding_of_guilt_permitted", "on_account_of", "committed_on", "constitutes_penal_offence_on"]}
STAGE2 = {"sorts": ["imposition", "penalty", "applicability"],
          "predicates": ["imposition_permitted", "imposes", "imposed_for", "applicability_of", "applicability_to", "applicable_on", "heavier_than"]}

UNIVERSAL_WHY = ("Article 11(2): 'Nor shall a heavier penalty be imposed than the one that was applicable at the time the penal offence was committed': "
                 "'the one that was applicable' is read as every penalty that was applicable to the act or omission on the day it was committed, "
                 "given that one was: an imposition is not permitted if its penalty is heavier than every such penalty (the pre-registered "
                 "phase-1 text). The words 'the one' speak of a single applicable penalty and do not say which to compare with when several "
                 "were applicable. Which penalty is heavier stays the open term heavier. The words name no one who must act, so no bearer is "
                 "named. Completion 'unspecified' (norm-defaults@0): where the guard fails the case is UNDECIDED, never permitted and never "
                 "'not required'; strict force, because the source states no exception.")
EXISTENTIAL_WHY = ("Article 11(2): 'Nor shall a heavier penalty be imposed than the one that was applicable at the time the penal offence was committed': "
                   "'the one that was applicable' is read as any one of the penalties that was applicable to the act or omission on the day it was "
                   "committed: an imposition is not permitted if its penalty is heavier than some such penalty. The two readings differ only when "
                   "several penalties were applicable on that day; the source's definite 'the one' admits both. Which penalty is heavier stays the "
                   "open term heavier. The words name no one who must act, so no bearer is named. Completion 'unspecified' (norm-defaults@0): "
                   "where the guard fails the case is UNDECIDED, never permitted and never 'not required'; strict force, because the source states no exception.")


def evidence():
    raw = subprocess.run(["git", "show", f"{BRANCH}:{EVIDENCE}"], cwd=ROOT, capture_output=True, check=True).stdout
    return json.loads(raw.split(b"---\n", 2)[1])


def add_vocabulary(meta, ev, stage):
    vocab, evv = meta["environment"]["vocabulary"], ev["environment"]["vocabulary"]
    for kind in ("sorts", "predicates"):
        for name in stage[kind]:
            assert name not in vocab[kind] or vocab[kind][name] == evv[kind][name], (kind, name)   # reuse only if identical
            vocab[kind][name] = copy.deepcopy(evv[kind][name])


def new_relations(ev, stage):
    """The relation names a situation base needs for the new predicates: the non-regulated ones, and `unsaid__` of the regulated ones."""
    preds = ev["environment"]["vocabulary"]["predicates"]
    return [(f"unsaid__{p}" if "regulated" in preds[p] else p) for p in stage["predicates"]]


def reidentify(meta, ev, stage):
    domains = {s: [s] for s in stage["sorts"]}
    meta["reading_sets"] = V.reidentified(meta["environment"], meta["reading_sets"], domains, {}, stage["predicates"], new_relations(ev, stage))


def replace_unit(meta, ev, uid, **extra):
    unit = next(u for u in meta["units"] if u["id"] == uid)
    evu = next(u for u in ev["units"] if u["id"] == uid)
    assert unit["kind"] == ["unformalised", "time"] and unit["span"] == evu["span"], unit
    span = unit["span"]
    for key in ("kind", "meaning", "support", "content"):
        unit.pop(key, None)
    unit.update({k: copy.deepcopy(v) for k, v in evu.items() if k in ("kind", "meaning", "support", "content")})
    unit.update(extra)
    assert unit["span"] == span
    return unit


def existential_content(universal):
    """The pre-registered universal guard `E and F` (E: some applicability; F: every applicability has a lighter penalty) with F's `forall` read as
    `exists`: the imposition's penalty is heavier than SOME penalty applicable to the act on the day it was committed."""
    content = copy.deepcopy(universal)
    rule = content["norm"]
    exists_act = rule["guard"]
    # guard: exists penalty (imposes and exists act (imposed_for and exists day (committed_on and (E and F))))
    day = exists_act[2][2][2][2]                   # the `exists day` node
    assert day[0] == "exists" and day[1] == "day", day[:2]
    body = day[2]                                         # ["and", committed_on, ["and", E, F]]
    assert body[0] == "and" and body[2][0] == "and" and body[2][2][0] == "forall", body[2][2][:2]
    e_node, f_node = body[2][1], body[2][2]
    assert f_node[1] == "applicability" and f_node[2][0] == "implies"
    ante, cons = f_node[2][1], f_node[2][2]               # applicability_to and applicable_on  /  exists penalty (applicability_of and heavier_than)
    day[2] = ["and", body[1], ["exists", "applicability", ["and", ante, cons]]]
    rule["name"] = "u043-existential"
    return content


def hand_base(decoded, set_id, i):
    """The separating situation's base: one imposition i1 of the middle penalty for one act on one day, on which two penalties were applicable, a
    lighter one and a heavier one; the imposed penalty is heavier than the lighter and not than the heavier one."""
    base = guard_base(decoded, set_id, i)
    d, r = base["domains"], base["relations"]
    d.update({"imposition": ["i1"], "act": ["ac1"], "day": ["dy1"], "penalty": ["pn_mid", "pn_light", "pn_heavy"], "applicability": ["ap_light", "ap_heavy"]})
    rows = {"imposes": [["i1", "pn_mid"]], "imposed_for": [["i1", "ac1"]], "committed_on": [["ac1", "dy1"]],
            "applicability_to": [["ap_light", "ac1"], ["ap_heavy", "ac1"]], "applicable_on": [["ap_light", "dy1"], ["ap_heavy", "dy1"]],
            "applicability_of": [["ap_light", "pn_light"], ["ap_heavy", "pn_heavy"]], "heavier_than": [["pn_mid", "pn_light"]]}
    for p, v in rows.items():
        assert p in r, p
        r[p] = v
    return base


def add_reading_set(meta, ev):
    """u043 as a reading set of the universal and the existential reading; the separating situation is found by Python's search from the hand base
    and admitted by Lean at load time."""
    content = {"universal": copy.deepcopy(next(u for u in ev["units"] if u["id"] == "u043")["content"])}
    content["existential"] = existential_content(content["universal"])
    content["universal"]["norm"]["name"] = "u043-universal"
    skeleton = {"id": "rs_u043", "unit": "u043", "version": 1, "status": "open",
                "readings": [{"id": "universal", "kind": "norm", "admission": {"who": "pilot-rerun", "why": UNIVERSAL_WHY, "distinguishing_models": {}}},
                             {"id": "existential", "kind": "norm", "admission": {"who": "pilot-rerun", "why": EXISTENTIAL_WHY, "distinguishing_models": {}}}],
                "_content": content}
    mini = {**copy.deepcopy(meta), "reading_sets": [], "_sets": [skeleton]}
    mini = I.finish_sets(mini, b"x", "u043")
    [item] = mini["reading_sets"]
    units = [{"id": u["id"], "kind": u["kind"], "content": u.get("content")} for u in mini["units"]]
    document = document_wire(units, mini["reading_sets"])
    started = time.monotonic()
    [row] = run_lean([{"id": "e", "kind": "readings-elaborate", "environment": wire(mini["environment"]), "document": wire(document)}])
    print("u043 elaborate:", row["status"], row.get("route"), row.get("error"), round(time.monotonic() - started, 1), "s", flush=True)
    assert row["status"] == "ok" and "filled" in row, row
    decoded = Decoded(mini["environment"], document, row["filled"], row["fill_premises"])
    R = decoded.doc.set_by_id(item["id"])
    hints = [hand_base(decoded, item["id"], 0), hand_base(decoded, item["id"], 1)]
    found = search(mini["environment"], document, item["id"], max_size=0, hints=hints, decoded=decoded)
    missing = [pair for pair, hit in found.items() if hit is None]
    print("u043 pairs", {k: (v is not None) for k, v in found.items()}, "missing", missing, flush=True)
    if missing:
        return None
    item = record_situations(item, {k: v for k, v in found.items() if v is not None})
    sets = {s["unit"]: s for s in meta["reading_sets"]}
    sets["u043"] = item
    meta["reading_sets"] = [sets[u["id"]] for u in meta["units"] if u["id"] in sets]
    return item


def stage(name):
    ev = evidence()
    for label, path in DOCS.items():
        raw = Path(path).read_bytes()
        _, front, source = raw.split(b"---\n", 2)
        meta = json.loads(front)
        if name == "u042":
            add_vocabulary(meta, ev, STAGE1)
            replace_unit(meta, ev, "u042")
            reidentify(meta, ev, STAGE1)
        else:
            add_vocabulary(meta, ev, STAGE2)
            heavier = next(t for t in ev["open_terms"] if t["name"] == "heavier")
            assert "heavier" not in [t["name"] for t in meta["open_terms"]]
            meta["open_terms"].append(copy.deepcopy(heavier))
            replace_unit(meta, ev, "u043")
            next(u for u in meta["units"] if u["id"] == "u043")["meaning"] = {"open": ["heavier"]}
            reidentify(meta, ev, STAGE2)
            if add_reading_set(meta, ev) is None:
                print("COULD NOT BUILD the u043 reading set in", label)
                raise SystemExit(2)
        P.write(path, meta, source)
        print("stage", name, "applied to", label, flush=True)


if __name__ == "__main__":
    stage(sys.argv[1])
