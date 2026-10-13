"""RD-5 step 3: the companions' status witnesses, replayed by Lean in each component and in each companion alone.

The run of 20261006T1800Z recorded, for each of its 156 companions, status witnesses: a case inside the rule's guard
SETTLED, a case outside it UNDECIDED (`witnesses.json`, from the situations of its spec modules). Here each witness is
asked again of Lean, twice:

- **in the component** (`readings-choice` with inner `norm-defaults-status`, `component` the set): on the migrated
  document, under the choice that takes the companion's reading, over the component's merged frame. Only the
  companions of migrated sets have a component;
- **alone** (the norm-defaults route's `norm-defaults-status`): on the companion as a standalone document, so that
  "nothing changed for a reading checked alone" is checked, not assumed. Each companion is also checked whole
  (`check_document`: its premises status).

The evidence is proposed as the norm-defaults route's own callers propose it: `table3`, then `enumerate`, then
`undecided` with the fillings "every unsaid table full" and "every unsaid table empty" (`ve/norm_defaults.py`
`_point_statuses`). Lean's first answer that is not UNKNOWN is compared with the recorded status. The unsaid tables
are the ones Lean's `norm-defaults-elaborate` names. Nothing here decides a status.
"""
from __future__ import annotations

import importlib
import json
import sys
import tempfile
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from migrate import COMMIT, RUN, git_ls, git_show  # noqa: E402

SPEC_MODULES = ("companions", "companions_nd", "udhr_specs", "repair_specs", "repair2_specs", "repair3_specs",
                "repair4_specs")
METHODS = ("table3", "enumerate", "undecided")
BATCH = 40


def label(status, value):
    """A recorded witness's status as Lean words it (`point_status`)."""
    return f"SETTLED {'yes' if value else 'no'}" if status == "SETTLED" else status


def specs(folder, commit=COMMIT):
    """Each companion's spec (`<unit>.<candidate>`), gathered as the run's `finish5.py` gathers them, from the run's
    own spec modules (read at `commit` into `folder`)."""
    for name in SPEC_MODULES:
        (folder / f"{name}.py").write_bytes(git_show(commit, f"{RUN}/{name}.py"))
    sys.path.insert(0, str(folder))
    try:
        nd, u, rs, r2, r3, r4 = [importlib.import_module(n) for n in SPEC_MODULES[1:]]
    finally:
        sys.path.remove(str(folder))
    out = {}
    for uid, per in nd.SPECS.items():
        for cid, spec in per.items():
            out[f"{uid}.{cid}"] = spec
    repaired = {*r2.REPAIRED, *rs.REPAIRED, *r3.REPAIRED, *r4.REPAIRED}
    for uid, cands in u.CANDIDATES.items():
        if uid not in repaired:
            for cid, spec, _why in cands:
                out[f"{uid}.{cid}"] = spec
    for uid, cands in [*rs.CANDIDATES.items(), *r2.CANDIDATES.items(), *r3.NEW_CANDIDATES.items(),
                       *r4.NEW_CANDIDATES.items()]:
        for cid, spec, _why in cands:
            out[f"{uid}.{cid}"] = spec
    return out


def recorded(commit=COMMIT):
    return json.loads(git_show(commit, f"{RUN}/witnesses.json"))["norm_defaults_status"]


def situation(vocabulary, domains, relations):
    """A base model over `vocabulary` (an environment's): every sort a domain (the spec's, else empty), every
    predicate without a completion a table (the spec's, else empty), as `witnesses_nd.py` builds it."""
    return {"complete": True, "constants": {},
            "domains": {s: list(domains.get(s, [])) for s in sorted(vocabulary["sorts"])},
            "relations": {p: [list(r) for r in relations.get(p, [])]
                          for p, decl in sorted(vocabulary["predicates"].items()) if "regulated" not in decl}}


def fillings(unsaid, model):
    """The two fillings the `undecided` method is offered: every unsaid table full, every one empty."""
    yes = {item["name"]: [list(v) for v in product(*(model["domains"][s] for s in item["sorts"]))] for item in unsaid}
    return yes, {item["name"]: [] for item in unsaid}


def inner_cases(unsaid, model, predicate, row):
    yes, no = fillings(unsaid, model)
    base = {"kind": "norm-defaults-status", "model": model, "predicate": predicate, "tuple": list(row)}
    return [{**base, "method": "table3"}, {**base, "method": "enumerate"},
            {**base, "method": "undecided", "yes": yes, "no": no}]


def first_answer(rows):
    """Lean's first status that is not UNKNOWN among the methods' rows, else UNKNOWN (or Lean's refusal)."""
    for row in rows:
        if row.get("status") != "ok":
            return f"refused: {row.get('error')}"
        if row["point_status"] != "UNKNOWN":
            return row["point_status"]
    return "UNKNOWN"


def _batched(run, cases):
    rows = []
    for k in range(0, len(cases), BATCH):
        rows += run(cases[k:k + BATCH])
    return rows


def checks(spec, record):
    """(situation domains, relations, predicate, row, expected label) of a companion's witnesses, in the recorded
    order; the recorded entries and the spec's checks must agree one for one."""
    out = []
    for domains, relations, items in spec["witnesses"]:
        for predicate, row, (status, value) in items:
            out.append((domains, relations, predicate, tuple(row), label(status, value)))
    if [(c[2], list(c[3]), c[4]) for c in out] != [(r["predicate"], r["row"], label(r["status"], r["value"]))
                                                    for r in record]:
        raise SystemExit("witnesses: the spec and witnesses.json differ")
    return out


def alone(commit=COMMIT, folder=None, only=None):
    """Each companion checked as a standalone document: its premises status and every witness's Lean status (the
    companions `only` names, `<unit>.<candidate>`, when given)."""
    from ve.document import check_document, load_document
    from ve.norm_defaults_route import run_cases, source_case
    folder = Path(folder or tempfile.mkdtemp(prefix="rd5-companions-"))
    spec, record = specs(folder, commit), recorded(commit)
    out = {}
    for name in git_ls(commit, f"{RUN}/readings"):
        if not name.endswith(".ve.md"):
            continue
        key = ".".join(name.split(".")[:2])
        if only is not None and key not in only:
            continue
        path = folder / name
        path.write_bytes(git_show(commit, f"{RUN}/readings/{name}"))
        premises = check_document(path)["premises"]["status"]
        ud = load_document(path)["norm_defaults"]
        vocabulary = ud.env.to_dict()["vocabulary"]
        unsaid = run_cases([source_case(ud, "norm-defaults-elaborate")])[0]["unsaid"]
        items = checks(spec[key], record[key])
        cases = [source_case(ud, c["kind"], **{k: v for k, v in c.items() if k != "kind"})
                 for d, r, p, row, _ in items for c in inner_cases(unsaid, situation(vocabulary, d, r), p, row)]
        rows = _batched(run_cases, cases)
        got = [first_answer(rows[k:k + len(METHODS)]) for k in range(0, len(rows), len(METHODS))]
        out[key] = {"premises": premises, "witnesses": [
            {"predicate": p, "row": list(row), "recorded": want, "lean": g, "same": g == want}
            for (_, _, p, row, want), g in zip(items, got)]}
    return out


def in_components(environment, document, components, commit=COMMIT, folder=None, only=None):
    """Each witness of a migrated set's companion, replayed in its component under the choice of its reading.
    `components` maps a set id to Lean's case for it (`readings-elaborate`'s component row: its environment); `only`
    restricts the sets replayed."""
    from ve.readings_route import run_lean
    folder = Path(folder or tempfile.mkdtemp(prefix="rd5-specs-"))
    spec, record = specs(folder, commit), recorded(commit)
    out = {}
    for item in document["reading_sets"]:
        if item["id"] not in components or (only is not None and item["id"] not in only):
            continue
        vocabulary = components[item["id"]]["environment"]["vocabulary"]
        for index, reading in enumerate(item["readings"]):
            key = f"{item['unit']}.{reading['id']}"
            if key not in spec:
                out[key] = {"witnesses": [], "note": "no recorded witnesses (a reading without a companion)"}
                continue
            choice = [[item["id"], index]]
            case = {"kind": "readings-choice", "environment": environment, "document": document,
                    "component": item["id"], "choice": choice}
            [elaborated] = run_lean([{**case, "id": "e", "inner": {"kind": "norm-defaults-elaborate"}}])
            unsaid = elaborated["inner"]["unsaid"]
            items = checks(spec[key], record[key])
            cases = [{**case, "id": f"{key}:{n}", "inner": c}
                     for n, (d, r, p, row, _) in enumerate(items)
                     for c in inner_cases(unsaid, situation(vocabulary, d, r), p, row)]
            rows = [r["inner"] if r.get("status") == "ok" else r for r in _batched(run_lean, cases)]
            got = [first_answer(rows[k:k + len(METHODS)]) for k in range(0, len(rows), len(METHODS))]
            out[key] = {"set": item["id"], "choice": choice, "witnesses": [
                {"predicate": p, "row": list(row), "recorded": want, "lean": g, "same": g == want}
                for (_, _, p, row, want), g in zip(items, got)]}
    return out
