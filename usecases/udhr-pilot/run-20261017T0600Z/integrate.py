"""Fold the norm candidates of the UDHR companions into the translation itself (readings-defaults RD-2a/RD-2b, merged since rd-6a).

Until now a norm candidate of a reading set could not carry content beside `norm-defaults@0`; each one lived in a one-unit companion
document. RD-2b lets `ve document` load, check, render and answer a `readings@1` document whose candidates carry norm content under
the completion 'unspecified'. This script builds the translation as PARTS (exact byte slices of the pinned source), because one
environment may hold at most 64 regulated predicates and the 94 candidates need more:

  * a unit whose set has ONE candidate becomes an ordinary norm unit with that content (no reading set at all);
  * a unit whose set has several candidates keeps a reading set whose candidates carry their content, with the separating
    situations found by the search over Lean's filled document (`readings-elaborate`) and admitted by Lean;
  * sets with formula candidates (u052, u110, u112, u114) keep their formulas and, where they are mixed, their norm content too.

    uv run --frozen python usecases/udhr-pilot/run-20261009T1800Z/integrate.py
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import readings_s1_pilot as P  # noqa: E402
import repair11_specs as R11  # noqa: E402
from ve.document import _environment, check_document, load_document  # noqa: E402
from ve.errors import VEError  # noqa: E402
from ve.readings_route import document_wire, run_lean  # noqa: E402
from ve.readings_s1 import Decoded, guard_base, record_situations, search, wire  # noqa: E402

PIN = "d6495201e9f6229603d2b13427ac68bd8febf5ad80f1cec329bbc3d04d9c7d3a"
READINGS = HERE / "readings"
PROFILES = {"documents@1", "norm-defaults@0", "norms@0", "relational-fol@0", "readings@1"}


# The merged vocabulary must give every regulated predicate its own act phrase (the English layer's distinctness check, V4, compares
# the wording of every symbol): nine companions shared "{0} take place" and two "{0} be carried out". Only the wording changes.
ACT_REWRITE = {
    "attack_upon_honour_or_reputation_permitted": "{0} be launched",
    "deprivation_of_property_permitted": "{0} be effected",
    "entry_into_marriage_permitted": "{0} be concluded",
    "interference_with_private_domains_permitted": "{0} be committed",
    "loss_of_nationality_permitted": "{0} be applied",
    "subjection_to_ill_treatment_permitted": "{0} be inflicted",
    "exercise_permitted": "{0} be exercised"}


def rename(value, old, new):
    """Rename a name in a vocabulary or a content: dictionary keys and string values alike."""
    if type(value) is str:
        return new if value == old else value
    if type(value) is list:
        return [rename(v, old, new) for v in value]
    if type(value) is dict:
        return {(new if k == old else k): rename(v, old, new) for k, v in value.items()}
    return value


def companion(uid, cid):
    raw = (READINGS / f"{uid}.{cid}.ve.md").read_bytes()
    _, front, _ = raw.split(b"---\n", 2)
    meta = json.loads(front)
    [unit] = meta["units"]
    return meta["environment"]["vocabulary"], unit["content"], unit["meaning"]


def merge(vocab, uid, cid, comp_vocab, content):
    """Add the companion's declarations to `vocab`; a name already declared otherwise is renamed for this candidate.

    The act rewrite comes FIRST (2026-10-09 audit of u055): applied after the name test, the second candidate of one reading set still
    carried the old act phrase, no longer matched the first, and was renamed, so the set's readings regulated two different acts."""
    comp_vocab = deepcopy(comp_vocab)
    for name, decl in comp_vocab["predicates"].items():
        if name in ACT_REWRITE:
            decl["regulated"]["act"] = ACT_REWRITE[name]
    for field in ("sorts", "predicates"):
        for name in list(comp_vocab[field]):
            if name in vocab[field] and vocab[field][name] != comp_vocab[field][name]:
                new = f"{name}_{uid}"[:64]
                comp_vocab = rename(comp_vocab, name, new)
                content = rename(content, name, new)
    for field in ("sorts", "predicates"):
        for name, decl in comp_vocab[field].items():
            assert vocab[field].setdefault(name, decl) == decl, (uid, cid, name)
    return content


def as_assertion(vocab, content):
    """A rule over a `plain` regulated predicate says that a property holds of every case its guard picks out: an assertion, and the
    predicate is then an ordinary one (the English layer words a probe only for obligations and permissions, and the assertion
    leaves the regulated budget alone)."""
    rule = content["norm"]
    decl = vocab["predicates"][rule["predicate"]]
    if decl.get("regulated", {}).get("role") != "plain":
        return content, "norm"
    if len(decl["arguments"]) != 1:      # 2026-10-14T1800Z: u106's right has two arguments (person, production): it stays a plain norm unit
        return content, "norm"
    assert rule["sign"] is True and not rule["over"] and not rule["unless"], rule
    (sort,) = decl["arguments"]
    body = ["unary", rule["predicate"], ["var", 0]]
    guard = rule["guard"]
    formula = ["forall", sort, body if guard == ["top"] else ["implies", guard, body]]
    del decl["regulated"]
    return formula, "asserted"


def build_part(meta, raw, first, last, label):
    """The part from unit `first` to unit `last` (ids, inclusive): meta, source slice, offset."""
    ids = [u["id"] for u in meta["units"]]
    chunk = meta["units"][ids.index(first):ids.index(last) + 1]
    a, b = chunk[0]["span"][0], chunk[-1]["span"][1]
    sets = {s["unit"]: s for s in meta["reading_sets"]}
    part = deepcopy(meta)
    env = part["environment"]
    env["profiles"] = sorted(PROFILES)
    vocab = env["vocabulary"]
    # u074's permission: the source states no default, so the completion is 'unspecified'
    for name, decl in vocab["predicates"].items():
        if "regulated" in decl:
            decl["regulated"]["default"] = "unspecified"
    units, reading_sets = [], []
    for unit in chunk:
        unit = deepcopy(unit)
        unit.pop("status", None)                  # the loader computes every status
        unit["span"] = [unit["span"][0] - a, unit["span"][1] - a]
        s = sets.get(unit["id"])
        if s is not None:
            readings, norm_cands = [], 0
            for r in s["readings"]:
                if r["content"] is None:
                    cv, content, _meaning = companion(unit["id"], r["id"])
                    content = merge(vocab, unit["id"], r["id"], cv, content)
                    content, kind = as_assertion(vocab, content)
                    readings.append((dict(r, kind=kind), content))
                else:
                    readings.append((r, None))
            if len(readings) == 1 and readings[0][1] is not None:
                unit["content"] = {"ast": readings[0][1]} if readings[0][0]["kind"] == "asserted" else readings[0][1]
                unit["kind"] = readings[0][0]["kind"]
                units.append(unit)
                continue
            s = deepcopy(s)
            s["readings"] = [r for r, _c in readings]
            s["_content"] = {r["id"]: c for r, c in readings if c is not None}
            reading_sets.append(s)
        units.append(unit)
    part["units"] = units
    part["_sets"] = reading_sets
    # 2026-10-12T0600Z: the scope of 'freely' is one choice over the list (u105a-c): the two sets of Article 27(1) are coupled on one
    # axis. Labels and couplings need readings@1, which the legacy whole-source form lacks, so they are added to the parts here.
    in_part = {s["unit"]: s for s in reading_sets}
    if all(u in in_part for u in R11.COUPLED):
        refs = []
        for u, set_id in R11.COUPLED.items():
            for r in in_part[u]["readings"]:
                r["labels"] = {R11.AXIS: R11.LABEL[r["id"]]}
            refs.append({"set": set_id, "version": in_part[u]["version"]})
        part["couplings"] = [{"id": "freely-scope", "axis": R11.AXIS, "sets": refs, "by": "translator",
                              "reason_spans": ["u105a", "u105b", "u105c"]}]
    return part, raw[a:b], a, b


def asserted_only_set(env, item):
    """A set whose readings are all `forall x. P_i(x)` assertions (2026-10-09: u077 once its claim readings were gone): no norm content,
    so Python's search has nothing to enumerate; the separating situation is a one-element model where P_i holds and P_j does not,
    recorded with the models route that formula-only sets use."""
    sort, preds = None, {}
    for r in item["readings"]:
        kind, srt, body = r["content"]
        assert kind == "forall" and body[0] == "unary" and body[2] == ["var", 0], r["content"]
        sort = sort or srt
        assert sort == srt
        preds[r["id"]] = body[1]
    models, readings = {}, []
    ids = [r["id"] for r in item["readings"]]
    for n, a in enumerate(ids):
        for b in ids[n + 1:]:
            models[f"m_{a}_{b}"] = {"complete": True, "constants": {}, "domains": {sort: ["p0"]},
                                    "relations": {preds[a]: [["p0"]]}}
    for r in item["readings"]:
        named = {}
        for o in ids:
            if o != r["id"]:
                named[o] = f"m_{r['id']}_{o}" if f"m_{r['id']}_{o}" in models else f"m_{o}_{r['id']}"
        readings.append({**r, "admission": {**r["admission"], "distinguishing_models": named}})
    return P._reidentified(env, {**item, "readings": readings, "models": models})


def finish_sets(part, source, label):
    """Make the sets content-bearing, find the situations, return the document meta."""
    env = _environment(part["environment"])
    sets, models_needed = [], []
    for item in part.pop("_sets"):
        content_of = item.pop("_content")
        if not content_of:                       # formula-only set: keep today's validation with its models
            sets.append(P._reidentified(env, item))
            continue
        item = {k: v for k, v in item.items() if k != "models"}
        readings = []
        for r in item["readings"]:
            if r["id"] in content_of and r["kind"] == "norm":
                readings.append(P.candidate(env, item["id"], r["id"], content_of[r["id"]], r["admission"]["why"]))
            elif r["id"] in content_of:
                readings.append({**r, "content": content_of[r["id"]], "meaning_id": P._identity(env, item["id"], {**r, "content": content_of[r["id"]]})})
            else:
                readings.append({**r, "meaning_id": P._identity(env, item["id"], r)})
        for r in readings:
            r["admission"]["distinguishing_models"] = {o["id"]: "pending" for o in readings if o["id"] != r["id"]}
        if all(r["kind"] == "asserted" for r in readings):
            sets.append(asserted_only_set(env, {**item, "readings": readings}))
            continue
        sets.append({**item, "readings": readings})
    part["reading_sets"] = sets
    return part


def find(part, label):
    """Lean's filled document, then Python's search per content-bearing set; Lean admits at load time."""
    units = [{"id": u["id"], "kind": u["kind"], "content": u.get("content")} for u in part["units"]]
    document = document_wire(units, part["reading_sets"])
    env_wire = wire(part["environment"])
    started = time.monotonic()
    [row] = run_lean([{"id": "e", "kind": "readings-elaborate", "environment": env_wire, "document": wire(document)}])
    print(label, "elaborate:", row["status"], row.get("route"), row.get("error"), round(time.monotonic() - started, 1), "s", flush=True)
    if row["status"] != "ok":
        return part, row, [], []
    if "filled" not in row:                      # no content-bearing set in this part (route w2): nothing for the search to enumerate
        return part, row, [], []
    decoded = Decoded(part["environment"], document, row["filled"], row["fill_premises"])
    out, missing, limits = [], [], []
    for item in part["reading_sets"]:
        R = decoded.doc.set_by_id(item["id"])
        if R is None or not Decoded.content_bearing(R):
            out.append(item)
            continue
        hints = [guard_base(decoded, item["id"], i) for i, a in enumerate(R.candidates) if a.content is not None]
        try:
            found = search(part["environment"], document, item["id"], max_size=1, hints=hints, decoded=decoded)
        except VEError as exc:
            limits.append((item["id"], str(exc)))
            out.append(item)
            continue
        missing += [(item["id"], x, y) for (x, y), hit in found.items() if hit is None and x < y]
        out.append(record_situations(item, {k: v for k, v in found.items() if v is not None}))
    return {**part, "reading_sets": out}, row, missing, limits


def plan_parts(meta, units_json, limit=64):
    """Consecutive articles grouped so that the product of the sets' candidate counts (the enumerated choices) stays within `limit`."""
    count = {s["unit"]: len(s["readings"]) for s in meta["reading_sets"]}
    arts = []
    for u in units_json["units"]:
        if not arts or arts[-1][0] != u["article"]:
            arts.append([u["article"], []])
        arts[-1][1].append(u["id"])
    parts, cur, prod = [], [], 1
    groups = []
    for _name, ids in arts:
        p = 1
        for i in ids:
            p *= count.get(i, 1)
        if p <= limit:
            groups.append([(ids, p)])
        else:                                   # one article beyond the limit: split it unit by unit
            groups.append([([i], count.get(i, 1)) for i in ids])
    for group in groups:
        whole = len(group) == 1
        for ids, p in group:
            if cur and prod * p > limit:
                parts.append((cur[0], cur[-1], prod))
                cur, prod = [], 1
            cur += ids
            prod *= p
    parts.append((cur[0], cur[-1], prod))
    return parts


def main(first="u001", last="u114", label="all", out=None):
    raw = (HERE.parent / "source" / "udhr.md").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PIN
    meta, source = P.read(HERE / "translation.ve.md")
    assert source == raw
    part, src, a, b = build_part(meta, raw, first, last, label)
    print(label, "bytes", a, b, "regulated:", sum(1 for d in part["environment"]["vocabulary"]["predicates"].values() if "regulated" in d),
          "sorts:", len(part["environment"]["vocabulary"]["sorts"]), flush=True)
    part = finish_sets(part, src, label)
    part, row, missing, limits = find(part, label)
    path = Path(out or HERE / f"integrated-{label}.ve.md")
    P.write(path, part, src)
    print("missing:", missing, "limits:", limits, flush=True)
    return path, {"label": label, "first": first, "last": last, "span": [a, b], "missing": missing, "limits": limits}


def all_parts():
    meta, _ = P.read(HERE / "translation.ve.md")
    units_json = json.loads((HERE / "units.json").read_text())
    plan = plan_parts(meta, units_json)
    # 2026-10-09T1800Z: the planner's first part (u001-u111, 64 choices) is too large for the Rust checker's 5 s limit and for Python's
    # one-element search to separate u111's readings; the parts keep the article boundaries of the previous runs, merged where fewer
    # reading sets (rights are one reading now) leave room: u001-u046, u047-u071b, u072-u103, u104-u114.
    count = {s["unit"]: len(s["readings"]) for s in meta["reading_sets"]}
    ids = [u["id"] for u in units_json["units"]]

    def product(a, b):
        out = 1
        span_ids = ids[ids.index(a):ids.index(b) + 1]
        for i in span_ids:
            out *= count.get(i, 1)
        if all(u in span_ids for u in R11.COUPLED):        # the coupled sets take one choice together (2026-10-12T0600Z)
            out //= count["u105c"]
        return out
    plan = [(a, b, product(a, b)) for a, b in (("u001", "u046"), ("u047", "u071b"), ("u072", "u103"), ("u104", "u114"))]
    out = []
    for n, (first, last, prod) in enumerate(plan, 1):
        label = f"part{n:02d}"
        path, info = main(first, last, label, HERE / f"translation-{label}.ve.md")
        info["choices"] = prod
        out.append(info)
    (HERE / "parts.json").write_text(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    if sys.argv[1:] == ["all"]:
        all_parts()
    else:
        main(*sys.argv[1:])
