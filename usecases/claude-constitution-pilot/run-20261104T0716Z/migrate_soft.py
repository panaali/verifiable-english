#!/usr/bin/env python3
"""SC-9: the probe translation of run 20261010T1800Z under the soft form (docs/spec/rd-9-soft-chain-PLAN.md SC-9, 5.2).

    uv run python usecases/claude-constitution-pilot/run-20261104T0716Z/migrate_soft.py

Reads `translation.ve.md` of run 20261010T1800Z at pilot commit `76922d6c` (the pinned copy in `tests/data/ce4/`,
checked against the commit's blob id) and writes
`probe-translation.probe.md` beside this script. The rewriting rules, each one function:

1. `soft-norms@0` is added to the profiles (`with_soft`).
2. Each `default` candidate is rewritten as in 5.2 (`tests/ce4.soft_default`, the one owner of that rule): the
   strict rule with `mode: default`, an unstated exception and no `unless`.
3. u0073.s05 (C9) becomes one default rule with three sufficient exception conditions, its first three `unless`
   formulas; its fourth, the `general_exception_to_complying` open term, is dropped (`conditioned`).
4. The five open terms the rewrites leave unused (the four `exception_to_*` and `general_exception_to_complying`)
   are removed from the vocabulary, the open-term list and every unit's `meaning.open` (`drop_open_terms`).
5. The recorded situations name the dropped terms, so every set's situations are dropped and re-proposed by SC-8's
   search over the filled frame Lean's `readings-elaborate` answers (`tools/readings_s1_pilot`, `ve.readings_s1`);
   Lean then checks them when the document is loaded.
6. A unit's `meaning_id` is Lean's (`document` mode, on load). No Lean answer carries a reading candidate's
   `meaning_id`: Lean's `document` mode gives a unit with a candidate's content its soft content identity, which is
   not the candidate's (`lean_unit_ids` records both, `answers/meaning-ids.json`). So each candidate gets the
   identity the loader binds it to (`ve.readings.s1_content_meaning_id`), as the pilot's run 20261016T1800Z did; a
   Lean-owned candidate id is a product change this item does not make (REPORT, deviation D1).

Units, spans, `source_word` and the body bytes are unchanged (`unchanged`). The changed units are written to
`changed_units.json`, the search's record to `answers/search.json`.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import sys
import tempfile
import time
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT))

from tests.ce4 import PILOT_COMMIT, PILOT_PATH, SETS, pinned_bytes, soft_default  # noqa: E402

_spec = importlib.util.spec_from_file_location("readings_s1_pilot", ROOT / "tools/readings_s1_pilot.py")
pilot = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pilot)

SOFT = "soft-norms@0"
CONDITIONED = "u0073.s05"
GENERAL = "general_exception_to_complying"
EXCEPTIONS = ("exception_to_asking_for_clarification", "exception_to_never_denying_being_claude",
              "exception_to_not_deceiving_about_system_prompt", "exception_to_complying_with_exploit_instruction")
PROBE = RUN / "probe-translation.probe.md"


def pinned():
    """The translation's bytes at the pilot commit: `tests/ce4`'s pinned copy, checked against the commit's blob id
    (`tests/test_readings_sd_ce4.py` reads the blob back from the commit where the repository holds it)."""
    return pinned_bytes()


def with_soft(environment):
    """Rule 1: the environment with `soft-norms@0` among its profiles."""
    return {**environment, "profiles": sorted({*environment["profiles"], SOFT})}


def conditioned(content, general=GENERAL):
    """Rule 3 (C9): a strict rule whose `unless` lists conditions and, last, the `general` open term becomes one
    default rule whose exception has those conditions as sufficient ones, decided by nobody the source names."""
    rule = copy.deepcopy(content["norm"])
    *conditions, last = rule["unless"]
    if rule.get("mode", "strict") != "strict" or not conditions or last != ["unary", general, ["var", 0]]:
        raise ValueError(f"not a rule with conditions and the open term {general}: {rule}")
    exception = {"decided_by": "unstated", "sufficient": conditions, "necessary": [], "factors": []}
    return {"norm": {**rule, "unless": [], "mode": "default", "exception": exception}}


def drop_open_terms(meta, names):
    """Rule 4: the open terms `names` removed from the vocabulary, the open-term list and every unit's
    `meaning.open`; a name some kept content still mentions is refused."""
    meta = copy.deepcopy(meta)
    predicates = meta["environment"]["vocabulary"]["predicates"]
    for name in names:
        predicates.pop(name)
    meta["open_terms"] = [t for t in meta["open_terms"] if t["name"] not in names]
    for unit in pilot._flat(meta["units"]):
        meaning = unit.get("meaning")
        if type(meaning) is dict and "open" in meaning:
            meaning["open"] = [n for n in meaning["open"] if n not in names]
    kept = json.dumps({k: v for k, v in meta.items() if k != "environment"} | {"vocabulary": predicates})
    left = [n for n in names if f'"{n}"' in kept]
    if left:
        raise ValueError(f"open terms still mentioned: {left}")
    return meta


def rewrite(meta):
    """Rules 1 to 4, and the situations dropped for the search (rule 5): the migrated front matter and the ids of
    the units whose content changed."""
    meta = copy.deepcopy(meta)
    meta["environment"] = with_soft(meta["environment"])
    changed = []
    for item in meta["reading_sets"]:
        if item["id"] not in SETS:
            continue
        for reading in item["readings"]:
            if reading["id"] == "default":
                reading["content"] = soft_default(reading["content"])
            reading["admission"]["distinguishing_models"] = {
                o["id"]: "pending" for o in item["readings"] if o["id"] != reading["id"]}
        item.pop("situations", None)
        changed.append(item["unit"])
    [unit] = [u for u in pilot._flat(meta["units"]) if u["id"] == CONDITIONED]
    unit["content"] = conditioned(unit["content"])
    changed.append(CONDITIONED)
    return drop_open_terms(meta, (*EXCEPTIONS, GENERAL)), sorted(changed)


def unchanged(before, after, source_before, source_after):
    """Units, spans, kinds, supports and `source_word` as they were; the body byte for byte."""
    assert source_before == source_after
    keys = ("id", "span", "kind", "support")
    flat = [[{k: u.get(k) for k in keys} for u in pilot._flat(m["units"])] for m in (before, after)]
    assert flat[0] == flat[1]
    assert [(R["id"], R["unit"], R["source_word"]) for R in before["reading_sets"]] == \
        [(R["id"], R["unit"], R["source_word"]) for R in after["reading_sets"]]


def lean_unit_ids(meta, source):
    """The `meaning_id` Lean's `document` mode answers for a unit with each candidate's content: for each reading position (the strict and
    the default candidates share their rule's name), one small document in the same environment whose units are the
    sets' sentences, each with that position's content, loaded through the ordinary entry point (Lean's answer, bound
    by the relay)."""
    from ve.document import load_document
    spans = {u["id"]: u["span"] for u in pilot._flat(meta["units"])}
    ids = {}
    for position in range(max(len(item["readings"]) for item in meta["reading_sets"])):
        units, text, owners = [], b"", []
        for item in meta["reading_sets"]:
            if position >= len(item["readings"]) or item["readings"][position].get("content") is None:
                continue
            reading = item["readings"][position]
            start, stop = spans[item["unit"]]
            sentence = source[start:stop].rstrip(b"\n ") + b"\n"
            units.append({"id": f"c{len(units)}", "span": [len(text), len(text) + len(sentence)], "kind": "norm",
                          "meaning": "specified", "support": "assumption", "content": reading["content"]})
            owners.append((item["id"], reading["id"]))
            text += sentence
        small = {"format": meta["format"], "environment": meta["environment"], "units": units,
                 "open_terms": meta["open_terms"]}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidates.ve.md"
            pilot.write(path, small, text)
            loaded = {u["id"]: u["meaning_id"] for u in load_document(path)["units"]}
        ids.update({owner: loaded[f"c{i}"] for i, owner in enumerate(owners)})
    return ids


def main():
    raw = pinned()
    _, front, source = raw.split(b"---\n", 2)
    before = json.loads(front)
    after, changed = rewrite(before)
    unchanged(before, after, source, source)
    from ve.document import _environment
    from ve.readings import s1_content_meaning_id
    env = _environment(after["environment"])
    ids = {}
    for item in after["reading_sets"]:
        for reading in item["readings"]:
            reading["meaning_id"] = ids[item["id"], reading["id"]] = s1_content_meaning_id(env, item["id"], reading)
    lean = lean_unit_ids(after, source)
    started = time.monotonic()
    after, missing, limits = find_situations(after)
    searched = round(time.monotonic() - started, 1)
    unchanged(before, after, source, source)
    pilot.write(PROBE, after, source)
    (RUN / "answers").mkdir(exist_ok=True)
    (RUN / "answers/search.json").write_text(json.dumps(
        {"seconds": searched, "pairs_without_situation": missing, "search_limits": limits,
         "situations": {R["id"]: sorted(R.get("situations", {})) for R in after["reading_sets"]}}, indent=2) + "\n")
    (RUN / "answers/meaning-ids.json").write_text(json.dumps(
        {f"{s}:{r}": {"candidate": m, "lean_unit": lean[s, r]} for (s, r), m in ids.items()}, indent=2) + "\n")
    (RUN / "changed_units.json").write_text(json.dumps(
        {"translation": f"{PILOT_COMMIT}:{PILOT_PATH}", "probe": PROBE.name, "changed_units": changed},
        indent=2) + "\n")
    print(json.dumps({"changed_units": changed, "search_seconds": searched, "missing": missing,
                      "limits": limits}))


def find_situations(meta):
    """SC-8's search under the completion for every set (the pilot's `nd.find_situations` of run 20261016T1800Z):
    the frame is the filled document Lean's `readings-elaborate` answers before any situation is recorded; each
    found situation is recorded for its pair, a pair without one is listed, never invented."""
    from ve.errors import VEError
    from ve.readings_route import document_wire, run_lean
    from ve.readings_s1 import Decoded, guard_base, record_situations, search
    units = [{"id": u["id"], "kind": u["kind"], "content": u.get("content")} for u in pilot._flat(meta["units"])]
    document = document_wire(units, meta["reading_sets"])
    [row] = run_lean([{"id": "e", "kind": "readings-elaborate", "environment": meta["environment"],
                       "document": document}])
    if row.get("status") != "ok" or "filled" not in row:
        raise VEError("elaborate refused: " + json.dumps(row)[:600])
    decoded = Decoded(meta["environment"], document, row["filled"], row.get("fill_premises"), row.get("soft_premises"))
    missing, limits, sets = [], [], []
    for item in meta["reading_sets"]:
        R = decoded.doc.set_by_id(item["id"])
        hints = [guard_base(decoded, item["id"], i) for i, a in enumerate(R.candidates) if a.content is not None]
        try:
            found = search(meta["environment"], document, item["id"], max_size=1, hints=hints, decoded=decoded,
                           filled=row)
        except VEError as exc:
            limits.append([item["id"], str(exc)])
            sets.append(item)
            continue
        missing += [[item["id"], x, y] for (x, y), hit in found.items() if hit is None]
        sets.append(record_situations(item, {k: v for k, v in found.items() if v is not None}))
    return {**meta, "reading_sets": sets}, missing, limits


if __name__ == "__main__":
    main()
