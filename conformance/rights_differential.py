"""Deterministic Python/Lean `correlate` differential on 1,000 generated rights documents
(docs/spec/rights.md 10): each accepted source is correlated by Python and regenerated,
independently, by the Lean rights route and the Lean soft route, and every output of
`check_rights_regenerated` must agree (generated keys, E″′ byte for byte, line instances
and nodes, Lim_D, bar nodes, order, layer premises, background, targets, warnings). A
generated source Python rejects must be rejected by Lean too, and conversely. Every accepted
source is also wrapped as a ve-document and loaded by `load_document`, which must accept it and
correlate it to the same rules: the loader admits exactly the unit contents the profile does.

The generator covers every incident shape (strict and default claims of both signs,
fan-out claims, liberties, immunities, powers), holder guards, right_lines units later in
the document, switches and ranks, limitations with scopes, kinds and conditions, both bar
readings, outside rules with precedence and `narrows:` citations, and faults (an unknown
cited unit, seven carve-outs, an unknown scope, a second bar, a reserved name, a missing
fan-out sort)."""
from __future__ import annotations

import json
import os
import random
import subprocess
import sys
import tempfile
from copy import deepcopy
from pathlib import Path

from tests.test_norms import environment, obligation, permission
from ve.document import load_document
from ve.errors import VEError
from ve.rights import correlate
from ve.rights_route import LEAN_ROUTE, _wire, check_rights_regenerated
from ve.soft_route import LEAN_ROUTE as SOFT_ROUTE

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "conformance/rights-differential-report.json"
EXCEPTION = {"decided_by": "unstated", "sufficient": [], "necessary": [], "factors": []}
ATOMS = {("state", "person"): [["binary", "arbitrary", ["var", 1], ["var", 0]], ["unary", "adult", ["var", 0]]],
         ("person", "person"): [["binary", "q", ["var", 1], ["var", 0]], ["unary", "adult", ["var", 1]]],
         ("person",): [["unary", "adult", ["var", 0]]]}
SORTS = {"protect_required": ("state", "person"), "protect_permitted": ("state", "person"),
         "person_protect_permitted": ("person", "person"), "publish_required": ("person", "person"),
         "publish_permitted": ("person", "person"), "speak_permitted": ("person",),
         "marry_permitted": ("person",), "recognise_required": ("state", "person"),
         "deprive_permitted": ("state", "person")}


def base(*sorts):
    return {"arguments": list(sorts), "description": "base"}


def environment_json(rng):
    raw = environment({
        "protect_required": obligation("deny", "protect_permitted", act="{0} protect {1}", args=("state", "person")),
        "protect_permitted": permission("allow", act="{0} protect {1}", args=("state", "person")),
        "person_protect_permitted": permission("allow", act="{0} protect {1}", args=("person", "person")),
        "publish_required": obligation("deny", "publish_permitted", act="{0} publish about {1}",
                                       args=("person", "person")),
        "publish_permitted": permission("allow", act="{0} publish about {1}", args=("person", "person")),
        "speak_permitted": permission(rng.choice(["allow", "deny"]), act="{0} speak", args=("person",)),
        "marry_permitted": permission("allow", act="{0} marry", args=("person",)),
        "recognise_required": obligation("deny", None, act="{0} recognise {1}", args=("state", "person")),
        "deprive_permitted": permission("allow", act="{0} deprive {1} of nationality", args=("state", "person")),
        "married": base("person"), "has_nationality": base("person"), "adult": base("person"),
        "arbitrary": base("state", "person"), "q": base("person", "person"),
    }, sorts=("state", "person")).to_dict()
    raw["profiles"] = sorted({"relational-fol@0", "norms@0", "soft-norms@0", "rights@0"})
    raw["vocabulary"]["rights"] = {
        "holders": ["person"], "bearers": ["state", "person"],
        "protected": ["adult"] if rng.randrange(2) else [],
        "alters": {"marry_permitted": {"holder_slot": 0, "status": "married", "recognition": "recognise_required"},
                   "deprive_permitted": {"holder_slot": 1, "status": "has_nationality"}}}
    parties = ["user"] if rng.randrange(2) else []
    ranks = ["high", "low"] if rng.randrange(2) else []
    if parties or ranks:
        raw["vocabulary"]["soft"] = {"parties": parties, "ranks": ranks,
                                     "outranks": [["high", "low"]] if ranks else [],
                                     "outranking": {"mode": "strict"}}
    return raw, parties, ranks


class Names:
    def __init__(self):
        self.count = 0

    def __call__(self, prefix):
        self.count += 1
        return f"{prefix}-{self.count}"


def rule(rng, name, predicate, sign, parties, ranks, *, default=None):
    sorts = SORTS[predicate]
    body = {"name": name, "predicate": predicate, "sign": sign,
            "guard": rng.choice([["top"], *ATOMS[sorts]]),
            "unless": [rng.choice(ATOMS[sorts]) for _ in range(rng.choice([0, 0, 1, 2]))], "over": []}
    if default if default is not None else rng.randrange(3) == 0:
        body["mode"] = "default"
        body["exception"] = dict(EXCEPTION)
        if ranks and rng.randrange(2):
            body["rank"] = rng.choice(ranks)
    if parties and rng.randrange(4) == 0:
        body["alterable"] = list(parties)
    return body


def cites(rng):
    return rng.choice([{}, {}, {"exception": ["u1"]}, {"guard": ["u2"]}, {"rank": ["u1"]}])


def source_line(rng, names, parties, ranks):
    shape = rng.choice(["claim+", "claim-", "claim-publish", "fan", "liberty", "liberty-publish",
                        "immunity", "power"])
    if shape == "claim+":
        return {"kind": "claim", "cites": cites(rng),
                "norm": rule(rng, names("claim"), "protect_required", True, parties, ranks)}
    if shape == "claim-":
        return {"kind": "claim", "cites": cites(rng),
                "norm": rule(rng, names("claim"), "protect_permitted", False, parties, ranks)}
    if shape == "claim-publish":
        return {"kind": "claim", "cites": cites(rng), "holder_slot": 1,
                "norm": rule(rng, names("claim"), rng.choice(["publish_required", "publish_permitted"]),
                             None, parties, ranks) | {}}
    if shape == "fan":
        norm = rule(rng, names("fan"), "protect_permitted", False, parties, ranks)
        norm["predicate"] = None
        norm["guard"], norm["unless"] = ["top"], []
        return {"kind": "claim", "cites": cites(rng), "norm": norm,
                "fan_out": {"state": "protect_permitted", "person": "person_protect_permitted"}}
    if shape in ("liberty", "liberty-publish"):
        predicate = "speak_permitted" if shape == "liberty" else "publish_permitted"
        return {"kind": "liberty", "cites": cites(rng),
                "norm": rule(rng, names("liberty"), predicate, True, parties, ranks)}
    if shape == "immunity":
        return {"kind": "immunity", "cites": cites(rng),
                "norm": rule(rng, names("immunity"), "deprive_permitted", False, parties, ranks)}
    return {"kind": "power", "cites": cites(rng),
            "liberty": rule(rng, names("may"), "marry_permitted", True, parties, ranks, default=False),
            "recognition": rule(rng, names("recognise"), "recognise_required", True, parties, ranks,
                                default=False)}


def fix_signs(line):
    norm = line.get("norm")
    if norm is not None and norm["sign"] is None:
        # a claim is an obligation + or a permission −
        norm["sign"] = norm["predicate"] == "publish_required"
    return line


def document(seed):
    rng = random.Random(seed)
    raw, parties, ranks = environment_json(rng)
    names = Names()
    rights = []
    for index in range(rng.randrange(1, 4)):
        rights.append({"right": {"name": f"r{index + 1}", "holder": "person",
                                 "guard": rng.choice([["top"], ["top"], ["unary", "adult", ["var", 0]]]),
                                 "lines": [fix_signs(source_line(rng, names, parties, ranks))
                                           for _ in range(rng.randrange(1, 4))]}})
    units = [{"source_units": ["u1", "u2"]}, *rights]
    if rng.randrange(3) == 0:
        target = rng.choice(rights)["right"]["name"]
        units.append({"right_lines": {"right": target, "lines": [
            fix_signs(source_line(rng, names, parties, ranks)) for _ in range(rng.randrange(1, 3))]}})
    right_names = [r["right"]["name"] for r in rights]
    for index in range(rng.choice([0, 1, 1, 2])):
        conditions = [{"name": f"c{j}", "role": rng.choice(["necessary", "sufficient"]),
                       "decided_by": rng.choice([None, "a tribunal"]),
                       "verbalisation": f"condition {j} holds"} for j in range(rng.randrange(3))]
        units.append({"limitation": {
            "name": f"l{index + 1}",
            "scope": "all" if rng.randrange(2) else sorted(rng.sample(right_names, rng.randrange(1, len(right_names) + 1))),
            "kinds": "all" if rng.randrange(2) else sorted(rng.sample(["claim", "liberty", "immunity", "power"],
                                                                      rng.randrange(1, 5))),
            "decided_by": rng.choice(["unstated", "the courts"]), "conditions": conditions,
            "factors": rng.choice([[], ["public order"]])}})
    if rng.randrange(2):
        units.append({"bar": {"name": "b30", "reading": rng.choice(["rule", "query"]),
                              "decided_by": "unstated"}})
    lines = [line for r in rights for line in r["right"]["lines"] if "norm" in line
             and line["norm"]["predicate"] is not None]
    for _ in range(rng.choice([0, 0, 1, 2])):
        if lines and rng.randrange(2):
            parent = rng.choice(lines)["norm"]
            outside = {"norm": {"name": names("rule"), "predicate": parent["predicate"],
                                "sign": not parent["sign"], "guard": rng.choice(ATOMS[SORTS[parent["predicate"]]]),
                                "unless": [], "over": [parent["name"]] if rng.randrange(2) else []}}
            if rng.randrange(2):
                outside["cites"] = {f"narrows:{parent['name']}": ["u1"]}
        else:
            outside = {"norm": rule(rng, names("rule"), rng.choice(["protect_permitted", "speak_permitted"]),
                                    rng.randrange(2) == 0, parties, ranks)}
        units.append(outside)
    fault = rng.randrange(20)  # one source in four carries a fault
    if fault == 0:
        units[1]["right"]["lines"][0]["cites"] = {"exception": ["u9"]}
    elif fault == 1:
        first = units[1]["right"]["lines"][0]
        norm = first.get("norm") or first["liberty"]
        norm["unless"] = [["top"]] * 7
    elif fault == 2:
        units.append({"limitation": {"name": "lx", "scope": ["nope"], "kinds": "all", "decided_by": "unstated",
                                     "conditions": [], "factors": []}})
    elif fault == 3:
        units.append({"bar": {"name": "b31", "reading": "rule", "decided_by": "unstated"}})
        units.append({"bar": {"name": "b32", "reading": "query", "decided_by": "unstated"}})
    elif fault == 4:
        first = units[1]["right"]["lines"][0]
        (first.get("norm") or first["liberty"])["name"] = "rights-x"
    return raw, units


def loaded(raw, units, directory):
    """The rights source as a ve-document, one source unit per content; `u2` is a plain
    exposition unit when the source has a single content, so every citation resolves."""
    contents = [unit for unit in units if "source_units" not in unit]
    source, spans, start = "", [], 0
    for index in range(max(len(contents), 2)):
        text = f"Unit {index + 1}.\n"
        source += text
        spans.append([start, start + len(text)])
        start += len(text)
    document = [{"id": f"u{index + 1}", "span": spans[index],
                 "kind": next(iter(contents[index])) if index < len(contents) else "exposition",
                 "meaning": "specified", "support": "none",
                 **({"content": deepcopy(contents[index])} if index < len(contents) else {})}
                for index in range(len(spans))]
    path = Path(directory) / "rights.ve.md"
    path.write_text("---\n" + json.dumps({"format": "ve-document@1", "environment": deepcopy(raw),
                                          "units": document}) + "\n---\n" + source)
    return load_document(path)


def _rows(executable, cases):
    run = subprocess.run([str(executable), "-"], input=json.dumps(cases), text=True,
                         capture_output=True, check=False,
                         timeout=int(os.environ.get("VE_CONFORMANCE_HANG_TIMEOUT", "600")))
    rows = json.loads(run.stdout)
    if len(rows) != len(cases):
        raise AssertionError("Lean returned the wrong row count")
    return rows


def run(count=1000, batch=50):
    """Compare until `count` generated sources are accepted by both routes."""
    accepted = rejected = seeds = 0
    same_text = loader = 0
    shapes = set()
    directory = tempfile.TemporaryDirectory()
    while accepted < count:
        sources = []
        while len(sources) < min(batch, count - accepted):
            raw, units = document(seeds)
            try:
                rights = correlate(deepcopy(raw), deepcopy(units))
                error = None
            except VEError as exc:
                rights, error = None, str(exc)
            sources.append((seeds, raw, units, rights, error))
            seeds += 1
        rows = _rows(LEAN_ROUTE, [{"id": str(seed), "kind": "rights-elaborate", "environment": _wire(raw),
                                   "document": _wire(units)} for seed, raw, units, _, _ in sources])
        soft_cases = [(i, {"id": str(seed), "kind": "soft-elaborate",
                           "environment": rights.soft_document.env.to_dict(),
                           "norms": [r.to_dict() for r in rights.soft_document.rules]})
                      for i, (seed, _, _, rights, _) in enumerate(sources) if rights is not None]
        soft_rows = dict(zip((i for i, _ in soft_cases), _rows(SOFT_ROUTE, [case for _, case in soft_cases])))
        for i, ((seed, raw, units, rights, error), row) in enumerate(zip(sources, rows)):
            if rights is None:
                if row.get("status") != "error":
                    raise AssertionError(f"seed {seed}: Python rejected ({error}), Lean accepted")
                rejected += 1
                same_text += error.endswith(row["error"]) or row["error"].endswith(error)
                continue
            if row.get("status") != "ok":
                raise AssertionError(f"seed {seed}: Python accepted, Lean rejected: {row.get('error')}")
            if soft_rows[i].get("status") != "ok":
                raise AssertionError(f"seed {seed}: soft route rejected the correlation: {soft_rows[i]}")
            try:
                check_rights_regenerated(rights, row, soft_rows[i])
            except VEError as exc:
                raise AssertionError(f"seed {seed}: {exc}") from exc
            try:
                doc = loaded(raw, units, directory.name)
            except VEError as exc:
                raise AssertionError(f"seed {seed}: the document loader rejected an accepted source: {exc}") from exc
            if ([r.to_dict() for r in doc["rights_document"].soft_document.rules] !=
                    [r.to_dict() for r in rights.soft_document.rules]):
                raise AssertionError(f"seed {seed}: the document loader correlated different rules")
            loader += 1
            accepted += 1
            shapes.update(instance["kind"] for instance in rights.instances)
            shapes.update(("fan-out",) if any(instance["bearer"] for instance in rights.instances) else ())
            shapes.update(("right_lines",) if any("right_lines" in unit for unit in units) else ())
            shapes.update(("limitation",) if rights.limitations else ())
            shapes.update((f"bar:{rights.bar['reading']}",) if rights.bar else ())
    return {"format": "rights-differential@0", "documents": accepted + rejected, "accepted_by_both": accepted,
            "rejected_by_both": rejected, "rejections_with_the_same_text": same_text,
            "loaded_as_documents": loader,
            "seeds_examined": seeds, "shapes": sorted(shapes)}


if __name__ == "__main__":
    result = run()
    REPORT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result))
    sys.exit(0)
