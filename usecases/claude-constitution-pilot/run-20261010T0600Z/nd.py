#!/usr/bin/env python3
"""Reading sets with checked content on the main chain (`norm-defaults@0`, completion unspecified), RD-2b.

    uv run python usecases/claude-constitution-pilot/run-20261010T0600Z/nd.py [force|all]

Run 20261010T0600Z (from 20261009T1800Z). The four operator units (u0062.s01, u0123.s01.p1, u0123.s02.p1, u0123.s03) are no longer reading sets:
the audit of 20261009T1800Z rejected the "wide" scope of "while role-playing as a custom AI persona", and what is left is one reading each,
written as content on the unit (repair_20261010T0600Z.py). Only the four "should" sets remain: 16 choices; `force` and `all` are the same group.

* the strict candidate of each "should" set is the strict rule of `readings/all-strict.ve.md` (norm-defaults
  predicates, completion unspecified); the defeasible candidate is the strict rule with one exception the text does not name
  (a base predicate that is an open term).

Not part of the translation proper (`translation-without-content.ve.md` keeps its sets without content); these are measurement documents.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import re
import sys
import time
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(RUN))

_spec = importlib.util.spec_from_file_location("readings_s1_pilot", ROOT / "tools/readings_s1_pilot.py")
pilot = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pilot)

import spec_nd as nd  # noqa: E402
from ve.document import _environment, check_document, load_document  # noqa: E402
from ve.errors import VEError  # noqa: E402
from ve.readings import s1_content_meaning_id  # noqa: E402

OUT = RUN / "readings"
FORCE = ["force-u0036-s05", "force-u0125-s04-p2", "force-u0156-s03", "force-u0263-s04-p2"]
GROUPS = {"force": FORCE, "all": FORCE}


# The defeasible candidate of a "should" set, on the main chain: the strict rule with ONE exception the text does not
# name (the soft chain's `exception: unstated`, here a base predicate that is an open term, so `norm-defaults@0` need
# not be left). set id -> (exception predicate, its sorts, its English, the exception's variable indexes in the guard)
EXCEPTIONS = {
    "force-u0036-s05": ("exception_to_asking_for_clarification", [nd.SITUATION],
                        "{0} is an exception to asking for clarification in cases of genuine ambiguity", [0]),
    "force-u0125-s04-p2": ("exception_to_never_denying_being_claude", [nd.CLAUDE],
                           "{0} has an exception to never directly denying being Claude", [0]),
    "force-u0156-s03": ("exception_to_not_deceiving_about_system_prompt", [nd.CLAUDE, nd.USER],
                        "{0} has an exception to not deceiving {1} about a system prompt", [1, 0]),
    "force-u0263-s04-p2": ("exception_to_complying_with_exploit_instruction", [nd.CLAUDE, nd.SITUATION],
                           "{0} has an exception to complying with an instruction against unintended exploits in {1}",
                           [1, 0]),
}


def with_exception(content, set_id):
    name, sorts, _, vars_ = EXCEPTIONS[set_id]
    atom = ["unary", name, ["var", vars_[0]]] if len(vars_) == 1 else ["binary", name, ["var", vars_[0]], ["var", vars_[1]]]
    out = copy.deepcopy(content)
    out["norm"]["unless"] = [atom]
    return out


def source_word(source, span):
    a, b = span
    text = source[a:b].decode("utf-8")
    m = re.search("shouldn’t|should not|should|must not|must|shall not|shall|always|never", text)
    start = a + len(text[:m.start()].encode("utf-8"))
    return [start, start + len(m.group(0).encode("utf-8"))]


def build(group, main_meta, source, strict_meta):
    sets_wanted = GROUPS[group]
    meta = copy.deepcopy(main_meta)
    env_data = meta["environment"]
    env_data["profiles"] = sorted({*env_data["profiles"], "readings@1"})
    vocab = env_data["vocabulary"]
    for set_id, (name, sorts, english, _) in EXCEPTIONS.items():
        if set_id in sets_wanted:
            vocab["predicates"][name] = nd.base(
                sorts, english, "An exception the source does not name, which the defeasible reading of its sentence "
                                "allows; open term, decided by nobody the source names.")
            meta["open_terms"].append({"name": name, "arguments": sorts, "decided_by": "unresolved_decider",
                                       "necessary": [], "sufficient": [],
                                       "factors": ["the source names no exception"], "precedents": [],
                                       "jurisdiction": "claude_constitution", "version": 1})
    env = _environment(env_data)
    strict_units = {u["id"]: u for u in pilot._flat(strict_meta["units"])}
    spans = {u["id"]: u["span"] for u in pilot._flat(meta["units"])}
    new_sets = []
    for item in main_meta["reading_sets"]:
        if item["id"] not in sets_wanted:
            continue
        item = copy.deepcopy(item)
        item.pop("models", None)
        readings = []
        for r in item["readings"]:
            if item["id"] in FORCE and r["id"] == "strict":
                content = strict_units[item["unit"]]["content"]
                r = {**r, "content": content}
                r["meaning_id"] = s1_content_meaning_id(env, item["id"], r)
            elif item["id"] in FORCE and r["id"] == "default":
                r = {**r, "content": with_exception(strict_units[item["unit"]]["content"], item["id"])}
                r["meaning_id"] = s1_content_meaning_id(env, item["id"], r)
            else:  # a candidate without content (the defeasible reading: it needs the soft chain)
                r = {**r, "content": None}
                r["meaning_id"] = _pending_id(env, item["id"], r)
            readings.append(r)
        for r in readings:
            r["admission"] = {**r["admission"], "distinguishing_models": {o["id"]: "pending" for o in readings
                                                                         if o["id"] != r["id"]}}
        if item["id"] in FORCE:
            item["source_word"] = source_word(source, spans[item["unit"]])
        item["readings"] = readings
        new_sets.append(item)
    meta["reading_sets"] = new_sets
    kept = [c for c in meta.get("couplings", []) if sum(r["set"] in sets_wanted for r in c["sets"]) >= 2]
    meta["couplings"] = [{**c, "sets": [r for r in c["sets"] if r["set"] in sets_wanted]} for c in kept]
    if not meta["couplings"]:
        meta.pop("couplings")
    # units of the sets left out keep their place without a set (their content is null already)
    return meta


def _pending_id(env, set_id, reading):
    old = reading.get("meaning_id", "")
    return old


def find_situations(meta):
    """`tools/readings_s1_pilot.find_situations` under the completion: the frame is the filled document Lean's
    `readings-elaborate` answers before any situation is recorded (RD-2b)."""
    from ve.readings_route import document_wire, run_lean
    from ve.readings_s1 import Decoded, guard_base, record_situations, search
    units = [{"id": u["id"], "kind": u["kind"], "content": u.get("content")} for u in pilot._flat(meta["units"])]
    document = document_wire(units, meta["reading_sets"])
    [row] = run_lean([{"id": "e", "kind": "readings-elaborate", "environment": meta["environment"],
                       "document": document}])
    if row.get("status") != "ok" or "filled" not in row:
        raise VEError("elaborate refused: " + json.dumps(row)[:600])
    decoded = Decoded(meta["environment"], document, row["filled"], row.get("fill_premises"))
    missing, limits, sets = [], [], []
    for item in meta["reading_sets"]:
        R = decoded.doc.set_by_id(item["id"])
        if R is None or not Decoded.content_bearing(R):
            sets.append(item)
            continue
        with_content = [i for i, a in enumerate(R.candidates) if a.content is not None]
        if len(with_content) < 2:  # nothing to separate: a pending candidate needs no situation
            sets.append(item)
            continue
        hints = [guard_base(decoded, item["id"], i) for i in with_content]
        try:
            found = search(meta["environment"], document, item["id"], max_size=1, hints=hints, decoded=decoded,
                           filled=row)
        except VEError as exc:
            limits.append((item["id"], str(exc)))
            sets.append(item)
            continue
        missing += [(item["id"], x, y) for (x, y), hit in found.items() if hit is None and x < y]
        sets.append(record_situations(item, {k: v for k, v in found.items() if v is not None}))
    return {**meta, "reading_sets": sets}, missing, limits


def main(argv):
    group = argv[1] if len(argv) > 1 else "force"
    main_meta, source = pilot.read(RUN / "translation-without-content.ve.md")
    strict_meta, _ = pilot.read(RUN / "readings/all-strict.ve.md")
    meta = build(group, main_meta, source, strict_meta)
    started = time.monotonic()
    meta, missing, limits = find_situations(meta)
    searched = round(time.monotonic() - started, 1)
    path = OUT / f"nd-{group}.ve.md"
    pilot.write(path, meta, source)
    result = {"document": str(path.relative_to(ROOT)), "group": group, "search_seconds": searched,
              "sets": [{"set": i["id"], "unit": i["unit"], "candidates": [
                  {"id": r["id"], "content": "none" if r["content"] is None else ("norm" if r["kind"] == "norm" else "assertion")}
                  for r in i["readings"]]} for i in meta["reading_sets"]],
              "pairs_without_situation": missing, "search_limits": limits}
    started = time.monotonic()
    try:
        load_document(path)
    except VEError as exc:
        result.update({"admitted": False, "rejection": getattr(exc, "message", str(exc))})
        (OUT / f"nd-{group}-result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
        print(json.dumps(result, indent=1, ensure_ascii=False))
        return 1
    result["load_seconds"] = round(time.monotonic() - started, 1)
    result["admitted"] = True
    started = time.monotonic()
    report = check_document(path)
    result["check_seconds"] = round(time.monotonic() - started, 1)
    (OUT / f"nd-{group}-check.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    result["readings"] = report.get("readings")
    result["premises"] = report.get("premises")
    result["bytes_by_status"] = report["coverage"]["bytes_by_status"]
    (OUT / f"nd-{group}-result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("readings",)}, indent=1, ensure_ascii=False)[:6000])
    r = report.get("readings") or {}
    print(json.dumps({k: v for k, v in r.items() if k != "sets"}, indent=1, ensure_ascii=False)[:3000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
