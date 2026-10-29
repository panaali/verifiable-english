"""Make readings-route admission inputs from the saved UDHR prefix documents.

Copies rename unit, set, reading, rule, constant, and predicate identifiers. The
first copy is the original; subsequent copies are independent article replicas.
Usage: python3 docs/perf/admission_cases.py SOURCE OUT [--copies 2|4]
"""
from __future__ import annotations

import argparse
import copy
import json
import os
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ve.readings_route import document_wire
from ve.readings_s1 import wire
from ve.readings_s1 import S1Environment
from ve.environment import Environment
from ve.norms import NormDocument
from ve.wire import digest


def metadata(path: Path) -> dict:
    return json.loads(path.read_text().split("---\n", 2)[1])


def names_in(value):
    names = set()
    if isinstance(value, dict):
        vocab = value.get("vocabulary")
        if isinstance(vocab, dict):
            for key in ("predicates", "constants"):
                names.update(vocab.get(key, {}))
        for key in ("id", "unit", "witness", "other", "set"):
            if isinstance(value.get(key), str):
                names.add(value[key])
        if isinstance(value.get("norm"), dict) and isinstance(value["norm"].get("name"), str):
            names.add(value["norm"]["name"])
        for child in value.values():
            names.update(names_in(child))
    elif isinstance(value, list):
        for child in value:
            names.update(names_in(child))
    return names


def rule_names_in(value):
    names = set()
    if isinstance(value, dict):
        if isinstance(value.get("norm"), dict) and isinstance(value["norm"].get("name"), str):
            names.add(value["norm"]["name"])
        for child in value.values():
            names.update(rule_names_in(child))
    elif isinstance(value, list):
        for child in value:
            names.update(rule_names_in(child))
    return names


def vocabulary_names_in(value):
    found = {"predicates": set(), "constants": set()}
    if isinstance(value, dict):
        vocab = value.get("vocabulary")
        if isinstance(vocab, dict):
            for key in found:
                found[key].update(vocab.get(key, {}))
        children = value.values()
    elif isinstance(value, list):
        children = value
    else:
        return found
    for child in children:
        more = vocabulary_names_in(child)
        for key in found:
            found[key].update(more[key])
    return found


def renamed(value, mapping):
    def name(s):
        if s in mapping:
            return mapping[s]
        if s.startswith("unsaid__") and s[8:] in mapping:
            return "unsaid__" + mapping[s[8:]]
        return s
    if isinstance(value, dict):
        return {name(k): renamed(v, mapping) for k, v in value.items()}
    if isinstance(value, list):
        return [renamed(v, mapping) for v in value]
    if isinstance(value, str):
        return name(value)
    return value


def case_from(path: Path, copies: int, main_sets: int | None = None) -> dict:
    base = metadata(path)
    made = copy.deepcopy(base)
    identifiers = names_in(base)
    symbols = vocabulary_names_in(base)
    for number in range(2, copies + 1):
        mapping = {name: f"{name}_copy{number}" for name in identifiers}
        for kind, prefix in (("predicates", "p"), ("constants", "c")):
            mapping.update({name: f"{prefix}{number}_{index}" for index, name in enumerate(sorted(symbols[kind]))})
        mapping.update({name: f"{name}-copy{number}" for name in rule_names_in(base)})
        replica = renamed(base, mapping)
        # The combined main frame needs distinct act-role keys. Each companion
        # keeps the article's original act phrase, preserving its recorded model.
        index = 0
        for decl in replica["environment"]["vocabulary"]["predicates"].values():
            regulated = decl.get("regulated", {})
            if isinstance(regulated, dict) and regulated.get("act"):
                arity = len(decl["arguments"])
                letter = chr(ord("a") + index)
                index += 1
                regulated["act"] = " ".join(["{0}", "perform", "replica",
                                              ("two", "three", "four")[number - 2], "item", letter] +
                                             [f"{{{i}}}" for i in range(1, arity)])
        made["units"].extend(replica["units"])
        made["reading_sets"].extend(replica["reading_sets"])
        for key in ("couplings", "narrowings"):
            made.setdefault(key, []).extend(replica.get(key, []))
        for key in ("predicates", "constants"):
            made["environment"]["vocabulary"][key].update(replica["environment"]["vocabulary"][key])
    for reading_set in made["reading_sets"]:
        for reading in reading_set["readings"]:
            content = reading.get("content")
            if not isinstance(content, dict):
                continue
            env_data = reading.get("companion", {}).get("environment", made["environment"])
            env = Environment(env_data, _validated_projection=True)
            ast = NormDocument._decode(content).to_dict() if "norm" in content else content.get("ast")
            if ast is not None:
                reading["meaning_id"] = digest(
                    f"ve-meaning-{env.identity_version}\n", {"environment_id": env.environment_id, "ast": ast})
    if copies > 1 or main_sets is not None:
        # Main-set situations were authored over the original whole vocabulary.
        # A replica widens that vocabulary, so keep its first article reading as
        # a fixed unit while retaining all independently scoped companion sets.
        retained = []
        units = {unit["id"]: unit for unit in made["units"]}
        remaining_main = 0 if main_sets is None else main_sets
        for reading_set in made["reading_sets"]:
            companion = any("companion" in reading for reading in reading_set["readings"])
            if companion or remaining_main > 0:
                retained.append(reading_set)
                if not companion:
                    remaining_main -= 1
            else:
                first = reading_set["readings"][0]
                unit = units[reading_set["unit"]]
                unit["kind"] = first["kind"]
                unit["content"] = first.get("content")
        made["reading_sets"] = retained
        kept = {reading_set["id"] for reading_set in retained}
        made["couplings"] = [c for c in made.get("couplings", [])
                             if all(ref["set"] in kept for ref in c.get("sets", []))]
        made["narrowings"] = [n for n in made.get("narrowings", []) if n.get("set") in kept]
    doc = document_wire(made["units"], made["reading_sets"],
                        couplings=made.get("couplings", ()), narrowings=made.get("narrowings", ()))
    suffix = f"-main{main_sets}" if main_sets is not None else ""
    return {"id": f"{path.stem}-{copies}x{suffix}", "kind": "readings-elaborate",
            "environment": wire(made["environment"]), "document": wire(doc)}


def repair_situations(case: dict, service: Path) -> None:
    """Use Lean's split output to bind each replica's recorded model IDs to its merged environment."""
    request = {"id": "parts", "mode": "readings-route", "cases": [case]}
    env = {**os.environ, "VE_READINGS_STAGE_TIMES": "0"}
    proc = subprocess.run([str(service)], input=json.dumps(request, separators=(",", ":")) + "\n",
                          text=True, capture_output=True, check=True, env=env)
    result = json.loads(proc.stdout.splitlines()[-1])["results"][0]["result"]
    if result["status"] != "ok":
        raise ValueError(f"Lean refused synthetic split: {result['error']}")
    parts = {row["component"]: row["environment"] for row in result["components"]}
    for reading_set in case["document"]["reading_sets"]:
        old = reading_set.get("situations", {})
        if not old:
            continue
        env = Environment(parts.get(reading_set["id"], parts["main"]), _validated_projection=True)
        replacements = {sid: S1Environment.situation_id_for(env, entry) for sid, entry in old.items()}
        reading_set["situations"] = {replacements[sid]: entry for sid, entry in old.items()}
        for reading in reading_set["readings"]:
            models = reading.get("admission", {}).get("distinguishing_models", {})
            if isinstance(models, dict):
                reading["admission"]["distinguishing_models"] = {
                    other: replacements.get(sid, sid) for other, sid in models.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("source", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--copies", type=int, choices=(1, 2, 4), default=1)
    parser.add_argument("--main-sets", type=int)
    parser.add_argument("--service", type=Path, default=Path("lean/.lake/build/bin/ve_service"))
    args = parser.parse_args()
    case = case_from(args.source, args.copies, args.main_sets)
    refused = None
    if args.copies > 1:
        try:
            repair_situations(case, args.service.resolve())
        except ValueError as exc:
            if args.copies != 4 or "ResourceLimit: vocabulary size" not in str(exc):
                raise
            refused = "ResourceLimit: vocabulary size"
    request = {"id": "admission-profile", "mode": "readings-route", "cases": [case]}
    args.out.write_text(json.dumps(request, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(json.dumps({"bytes": args.out.stat().st_size, "units": len(case["document"]["units"]),
                      "sets": len(case["document"]["reading_sets"]), "refused": refused}))


if __name__ == "__main__":
    main()
