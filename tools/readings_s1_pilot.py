"""Rerun S1's pilots and report section 11's figures (docs/spec/composition-s1.md 9.3, 11).

    uv run --frozen python tools/readings_s1_pilot.py --constitution <run dir> --udhr <run dir> --out <dir>

The constitution: the run's all-default document (the soft chain) with `readings@1`, every force set of the main
translation re-expressed with content-bearing candidates (the default one from the all-default document, the strict
one its strict twin, 1.7), and each set's stored situation re-expressed as one situation with the
default reading as witness (`readings/separating-situations.json`: one element of each sort, every guard atom true,
the default's exception supposed at the tuple), found by Python's search from that base and checked by Lean.

The UDHR: the run's translation with `readings@1`, the four norm-candidate sets (`u017`, `u052`, `u112`, `u114`)
given the contents of their companion documents, and every right set's situations found by the search (their
probe-free `models` are not read under S1, 13.9). The assertion set keeps today's validation.

Each document is loaded and checked through the ordinary entry point, so Lean admits it (the route relays its
answer). The report gives, per pilot: whether the single-attachment check
of 4.2 refuses the document; per named unit its status and bytes; the sets admitted, by probe form; the findings;
the pairs without a situation and the rejection text; ResourceLimit hits; and the load time. Nothing here is a
prediction: every number is the rerun's.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ve.document import _environment, check_document, load_document  # noqa: E402
from ve.errors import VEError  # noqa: E402
from ve.readings import s1_content_meaning_id  # noqa: E402
from ve.readings_route import document_wire  # noqa: E402
from ve.readings_s1 import Decoded, guard_base, record_situations, search  # noqa: E402


def read(path):
    raw = Path(path).read_bytes()
    _, front, source = raw.split(b"---\n", 2)
    return json.loads(front), source


def write(path, meta, source):
    Path(path).write_bytes(b"---\n" + json.dumps(meta, ensure_ascii=False).encode() + b"\n---\n" + source)


def with_readings(environment):
    return {**environment, "profiles": sorted({*environment["profiles"], "readings@1"})}


def candidate(env, set_id, cid, content, why):
    reading = {"id": cid, "kind": "norm", "content": content}
    return {**reading, "meaning_id": s1_content_meaning_id(env, set_id, reading),
            "admission": {"who": "pilot-rerun", "why": why, "distinguishing_models": {}}}


def constitution(run):
    """The constitution's S1 document and the units the plan names (its force sets)."""
    run = Path(run)
    main, _ = read(run / "translation.ve.md")
    default, source = read(run / "readings/all-default.ve.md")
    strict, _ = read(run / "readings/all-strict.ve.md")
    meta = json.loads(json.dumps(default))
    meta["environment"] = with_readings(default["environment"])
    env = _environment(meta["environment"])
    units = {u["id"]: u for u in meta["units"]}
    strict_units = {u["id"]: u for u in strict["units"]}
    sets, named, skipped = [], [], []
    for item in main["reading_sets"]:
        if not item["id"].startswith("force-") or [r["id"] for r in item["readings"]] != ["strict", "default"]:
            continue
        uid = item["unit"]
        unit, strict_unit = units.get(uid), strict_units.get(uid)
        if unit is None or strict_unit is None or unit.get("content") is None or strict_unit.get("content") is None:
            continue
        # The strict candidate is the default rule's strict twin (1.7, F1: the strict and the default reading of
        # one rule). The all-strict document states some rules over another environment's predicates (its
        # norm-defaults form), which this document does not declare; its rule is used where it is the twin.
        twin = {"norm": {k: v for k, v in unit["content"]["norm"].items() if k not in ("mode", "exception")}}
        twin.update({k: v for k, v in unit["content"].items() if k != "norm"})
        stated = strict_unit["content"]
        if stated.get("norm", {}).get("predicate") != twin["norm"]["predicate"]:
            skipped.append((uid, "the all-strict document states this rule over "
                                 f"{stated.get('norm', {}).get('predicate')}; its strict twin is used"))
        try:
            readings = [candidate(env, item["id"], "strict", twin, "the strict reading of the rule"),
                        candidate(env, item["id"], "default", unit["content"], "the default reading of the rule")]
        except VEError as exc:
            skipped.append((uid, exc.message if hasattr(exc, "message") else str(exc)))
            continue
        for r in readings:
            r["admission"]["distinguishing_models"] = {o["id"]: "pending" for o in readings if o["id"] != r["id"]}
        sets.append({"id": item["id"], "unit": uid, "version": 1, "status": "open", "readings": readings})
        unit["content"] = None
        # The main translation's meaning of the open unit: its open terms are declared ones, not the decision
        # predicate the default reading would generate.
        unit["meaning"] = next(u for u in _flat(main["units"]) if u["id"] == uid)["meaning"]
        unit.pop("meaning_id", None)
        unit.pop("status", None)
        named.append(uid)
    meta["reading_sets"] = sets
    return meta, source, named, skipped


def udhr(run):
    """The UDHR's S1 document and the units the plan names (its sets)."""
    run = Path(run)
    meta, source = read(run / "translation.ve.md")
    meta = json.loads(json.dumps(meta))
    meta["environment"] = with_readings(meta["environment"])
    companions, merged = {}, []
    vocabulary = meta["environment"]["vocabulary"]
    for path in sorted((run / "readings").glob("*.ve.md")):
        uid, reading_id = path.name.split(".")[:2]
        companion, _ = read(path)
        contents = [u["content"] for u in companion["units"] if u.get("kind") == "norm" and u.get("content")]
        if len(contents) == 1:
            companions[(uid, reading_id)] = contents[0]
            # The companion's own vocabulary joins the document's: under S1 its candidate is a content of this
            # document (F4), so what it regulates is declared here.
            for field in ("sorts", "predicates"):
                for name, decl in companion["environment"]["vocabulary"].get(field, {}).items():
                    if name not in vocabulary[field]:
                        vocabulary[field][name] = decl
                        merged.append(f"{field[:-1]} {name}")
    env = _environment(meta["environment"])
    sets, named = [], []
    for item in meta.get("reading_sets", []):
        filled = any((item["unit"], r["id"]) in companions for r in item["readings"])
        bearing = filled or any(type(r.get("content")) is dict and set(r["content"]) & {"right", "right_lines",
                                                                                          "limitation"}
                                for r in item["readings"])
        named.append(item["unit"])
        if not bearing:
            # A formula-only set keeps today's validation with its models (4.9); the new environment gives its
            # formulas and models new identities.
            sets.append(_reidentified(env, item))
            continue
        item = {key: value for key, value in item.items() if key != "models"}
        readings = []
        for r in item["readings"]:
            if (item["unit"], r["id"]) in companions:
                r = candidate(env, item["id"], r["id"], companions[(item["unit"], r["id"])], r["admission"]["why"])
            else:
                # The environment now holds readings@1, so every content's identity is recomputed (3).
                r = {**r, "meaning_id": _identity(env, item["id"], r)}
            readings.append(r)
        for r in readings:
            r["admission"]["distinguishing_models"] = {o["id"]: "pending" for o in readings if o["id"] != r["id"]}
        sets.append({**item, "readings": readings})
    meta["reading_sets"] = sets
    return meta, source, named, [("declarations merged from the companion documents", merged)]


def _identity(env, set_id, reading):
    from ve.ast import formula_from_data
    from ve.identity import meaning_id
    if type(reading.get("content")) is list:
        return meaning_id(env, formula_from_data(env, reading["content"]))
    return s1_content_meaning_id(env, set_id, reading) or reading["meaning_id"]


def _reidentified(env, item):
    """A formula-only set with its meaning and model ids recomputed over `env`."""
    from ve.ast import formula_from_data
    from ve.identity import meaning_id
    from ve.model import FiniteModel
    from ve.readings import _reading_evaluation
    model_env, _ = _reading_evaluation(env)
    models = {}
    for old, data in item.get("models", {}).items():
        # Sorts and predicates merged from the companions are empty in today's models.
        data = {**data, "domains": {**{sort: [] for sort in model_env.model_sorts}, **data["domains"]},
                "relations": {**{p: [] for p in model_env.predicates if p not in model_env.definition_entries},
                              **data["relations"]}}
        models[old] = data
    renamed = {old: FiniteModel.from_dict(model_env, data).model_id for old, data in models.items()}
    readings = []
    for r in item["readings"]:
        mid = meaning_id(env, formula_from_data(env, r["content"])) if r["content"] is not None else r["meaning_id"]
        named = {o: renamed.get(m, m) for o, m in r["admission"]["distinguishing_models"].items()}
        readings.append({**r, "meaning_id": mid, "admission": {**r["admission"], "distinguishing_models": named}})
    return {**item, "readings": readings, "models": {renamed[old]: data for old, data in models.items()}}


def find_situations(meta):
    """Python's search for every content-bearing set, from the pilots' guard bases first; Lean checks each."""
    units = [{"id": u["id"], "kind": u["kind"], "content": u.get("content")}
             for u in _flat(meta["units"])]
    document = document_wire(units, meta["reading_sets"])
    decoded = Decoded(meta["environment"], document)
    missing, limits = [], []
    sets = []
    for item in meta["reading_sets"]:
        R = decoded.doc.set_by_id(item["id"])
        if R is None or not Decoded.content_bearing(R):
            sets.append(item)
            continue
        hints = [guard_base(decoded, item["id"], i) for i, a in enumerate(R.candidates) if a.content is not None]
        try:
            found = search(meta["environment"], document, item["id"], max_size=1, hints=hints, decoded=decoded)
        except VEError as exc:
            limits.append((item["id"], str(exc)))
            sets.append(item)
            continue
        missing += [(item["id"], x, y) for (x, y), hit in found.items() if hit is None and x < y]
        sets.append(record_situations(item, {k: v for k, v in found.items() if v is not None}))
    return {**meta, "reading_sets": sets}, missing, limits


def _flat(units):
    for unit in units:
        if unit.get("status") == "MIXED":
            yield from unit["parts"]
        else:
            yield unit


def measure(name, meta, source, named, skipped, out):
    path = Path(out) / f"{name}.s1.ve.md"
    started = time.monotonic()
    meta, missing, limits = find_situations(meta)
    searched = time.monotonic() - started
    write(path, meta, source)
    result = {"pilot": name, "document": str(path), "search_seconds": round(searched, 1),
              "units_not_reexpressed": skipped,
              "sets": len(meta["reading_sets"]), "pairs_without_situation": missing, "search_limits": limits}
    started = time.monotonic()
    try:
        doc = load_document(path)
    except VEError as exc:
        result.update({"admitted": False, "rejection": exc.message if hasattr(exc, "message") else str(exc),
                       "load_seconds": round(time.monotonic() - started, 1),
                       "single_attachment_refusal": "depends on reading sets" in str(exc)})
        return result
    result["load_seconds"] = round(time.monotonic() - started, 1)
    report = check_document(path)
    readings = report.get("readings") or {}
    statuses = {u["id"]: u["status"] for u in doc["units"]}
    spans = {u["id"]: u["span"][1] - u["span"][0] for u in doc["units"]}
    result.update({
        "admitted": True, "single_attachment_refusal": False,
        "content_bearing_sets": len(readings.get("sets", [])),
        "separations": readings.get("separations"), "findings": readings.get("findings"),
        "not_certified": [f for s in readings.get("sets", []) for f in s["not_certified"]],
        "wordings": {w: sum(p["wording"] == w for s in readings.get("sets", []) for p in s["pairs"])
                     for w in ("E14", "E19", "E21", "E24")},
        "premises": report["premises"],
        "named_units": {uid: {"status": statuses.get(uid), "bytes": spans.get(uid)} for uid in named},
        "bytes_by_status": report["coverage"]["bytes_by_status"]})
    return result


def baseline(path):
    """The pilot's own translation, checked today: its bytes by status and its premise status."""
    started = time.monotonic()
    try:
        report = check_document(path)
    except VEError as exc:
        return {"document": str(path), "error": exc.message if hasattr(exc, "message") else str(exc)}
    return {"document": str(path), "bytes_by_status": report["coverage"]["bytes_by_status"],
            "premises": report.get("premises"), "check_seconds": round(time.monotonic() - started, 1)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--constitution")
    parser.add_argument("--udhr")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    Path(args.out).mkdir(parents=True, exist_ok=True)
    results = []
    if args.constitution:
        result = measure("constitution", *constitution(args.constitution), args.out)
        result["baseline"] = baseline(Path(args.constitution) / "readings/all-default.ve.md")
        results.append(result)
    if args.udhr:
        result = measure("udhr", *udhr(args.udhr), args.out)
        result["baseline"] = baseline(Path(args.udhr) / "translation.ve.md")
        results.append(result)
    print(json.dumps(results, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
