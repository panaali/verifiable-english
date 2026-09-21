"""E5 construction-grounded items. Pure local generation; never invokes a model.

JSONL rows match ve_experiments.runner.Item(**row). render_cell accepts such a
row, a harness Item, or the visible payload passed to Condition.build_prompt.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from dataclasses import replace
from functools import lru_cache
import hashlib
import json
from pathlib import Path

from ve.argument import (ArgumentGraph, Claim, Deduction, Evidence, check_argument,
                         deduction_identity, outstanding_obligations, predicate_use_panel)
from ve.entailment import prove_entailment
from ve.environment import Environment, LANGUAGE, PROFILE, SPEC_REVISION
from ve.model import FiniteModel

HERE = Path(__file__).resolve().parent
CELLS = ("a", "b", "c", "d", "e")
FAMILIES = ("merged_vocabulary", "scope_mismatch", "unsupported_leaf", "stale_evidence")
# Each topology is a distinct semantic template, with nodes numbered in DAG order.
# Every rule is necessary for reaching the final node from node 0.
TEMPLATES = {
    "chain2": [[0], [1]],
    "chain3": [[0], [1], [2]],
    "fork2": [[0], [0], [1, 2]],
    "fork_tail": [[0], [0], [1, 2], [3]],
    "chain4": [[0], [1], [2], [3]],
    "chain5": [[0], [1], [2], [3], [4]],
    "fork3": [[0], [0], [0], [1, 2, 3]],
    "nested_join": [[0], [0], [1, 2], [1], [3, 4]],
    "parallel_chains": [[0], [1], [0], [3], [2, 4]],
    "shared_prefix": [[0], [1], [1], [2, 3]],
    "staggered_join": [[0], [1], [0], [2, 3]],
    "double_join": [[0], [0], [1, 2], [0], [3, 4]],
}
VOCABS = {
    "dev_cinder": ("deployment", "service"),
    "dev_loam": ("warehouse", "parcel"),
    "score_mica": ("laboratory", "sample"),
    "score_reef": ("satellite", "module"),
    "score_twill": ("archive", "volume"),
    "score_umber": ("irrigation", "valve"),
}
DEV_TEMPLATES = tuple(TEMPLATES)[:4]


def packed(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def fingerprint(value):
    return hashlib.sha256(packed(value).encode()).hexdigest()


def make_split_manifest():
    templates = {t: "dev" if t in DEV_TEMPLATES else "scored" for t in TEMPLATES}
    vocabularies = {v: "dev" if v.startswith("dev_") else "scored" for v in VOCABS}
    # Two vocabulary families per template, all four scored domains represented.
    groups = {}
    for i, (t, split) in enumerate(templates.items()):
        vs = [v for v, s in vocabularies.items() if s == split]
        for v in (vs[i % len(vs)], vs[(i + 1) % len(vs)]):
            groups[f"{t}/{v}"] = split
    return {"version": 1, "seed": 5301, "dev_fraction": 1 / 3,
            "templates": templates, "vocabulary_families": vocabularies, "groups": groups}


def split_manifest():
    return json.loads((HERE / "split.json").read_text())


def _word(seed):
    # Fresh fixed-width pronounceable symbols; no condition or label information.
    raw = hashlib.sha256(seed.encode()).digest()
    return "".join("bcdfghjklmnprstvz"[raw[2*i] % 16] + "aeiou"[raw[2*i+1] % 5]
                   for i in range(4))


def _formula(sort, antecedents, consequent):
    parts = [f"x is {p}" for p in antecedents]
    left = parts[0]
    for part in parts[1:]:
        left = f"({left}) and ({part})"
    return f"for every {sort} x, (if ({left}), then (x is {consequent})).\n"


@lru_cache(maxsize=None)
def logical_bundle(template, vocabulary_family, invalid):
    """Reusable data-only proofs. All badges ultimately come from replay below."""
    domain, sort = VOCABS[vocabulary_family]
    topology = TEMPLATES[template]
    symbols = [_word(f"{vocabulary_family}:{i}") for i in range(len(topology) + 2)]
    assert len(set(symbols)) == len(symbols)
    env = Environment.from_dict({
        "language": LANGUAGE, "profile": PROFILE, "spec_revision": SPEC_REVISION,
        "vocabulary": {"sorts": {sort: {"description": f"An entity in the synthetic {domain} register."}},
            "predicates": {p: {"arguments": [sort], "description": f"Recorded as status {p}."}
                           for p in symbols}, "constants": {}},
    })
    leaves, derived, rules, edges = [], [], [], []
    for index, parents in enumerate(topology, 1):
        antecedents, consequent = [symbols[p] for p in parents], symbols[index]
        # Reverse the final rule, but retain the proposed forward deduction.
        if invalid and index == len(topology):
            antecedents, consequent = [symbols[index]], symbols[parents[0]]
        source = _formula(sort, antecedents, consequent)
        leaves.append(Claim.create(env, f"l{index}", source))
        rules.append({"claim": f"l{index}", "antecedent": antecedents, "consequent": consequent})
        derived.append(Claim.create(env, f"n{index}", _formula(sort, [symbols[0]], symbols[index])))
        premises = tuple([f"n{p}" for p in parents if p != 0] + [f"l{index}"])
        edges.append(Deduction(f"s{index}", premises, f"n{index}"))
    graph = ArgumentGraph(env, tuple(leaves + derived), tuple(edges), derived[-1].name)
    by_name = {c.name: c for c in graph.claims}
    certified = []
    for index, edge in enumerate(edges, 1):
        if invalid and index == len(edges):
            # All earlier statuses true, final status false; the reversed rule holds vacuously.
            model = FiniteModel.from_dict(env, {
                "complete": True, "domains": {sort: ["entity"]}, "constants": {},
                "relations": {p: [["entity"]] if i < len(topology) else []
                              for i, p in enumerate(symbols)},
            })
            certified.append(replace(edge, countermodels=(model,)))
        else:
            proof = prove_entailment(env, tuple(by_name[n].ast for n in edge.premises),
                                     by_name[edge.conclusion].ast)
            if proof.status != "Found":
                raise AssertionError((template, edge.name, proof.status))
            certificate = {"edge_id": deduction_identity(graph, edge), "direction": "follows",
                           "proof": proof.certificate}
            certified.append(replace(edge, certificates=(certificate,)))
    graph = replace(graph, deductions=tuple(certified))
    result = check_argument(graph, search=False)
    assert result.status == ("Incomplete" if invalid else "Checked"), result.to_dict()
    assert result.composed is (not invalid)
    return graph, rules, symbols


def _sense(symbol, variant=0):
    return f"urn:ve:e5:{symbol}:sense:{variant}"


def _sense_description(symbol, variant=0):
    return f"{symbol} / {'security assurance review' if variant else 'operational readiness review'}"


def _text(record):
    statement = record["what"]
    before = " and ".join(record["interpretations"][p] for p in statement["antecedent"])
    after = record["interpretations"][statement["consequent"]]
    return f"Every entity recorded under {before} is recorded under {after}."


def _record(rule, scope, record_id):
    ps = list(dict.fromkeys(rule["antecedent"] + [rule["consequent"]]))
    record = {"record_id": record_id, "who": "Registrar Talven",
              "what": {"kind": "universal_rule", "antecedent": rule["antecedent"],
                       "consequent": rule["consequent"]},
              "when": {"recorded_at": "2031-04-16", "valid_from": "2031-04-01", "valid_until": "2031-04-30"},
              "scope": deepcopy(scope), "senses": {p: _sense(p) for p in ps},
              "interpretations": {p: _sense_description(p) for p in ps}}
    record["text"] = _text(record)
    return record


def grounding_audit(payload):
    """Deterministic support rule for this synthetic, authoritative record world.

    Only a cited record can discharge its leaf. No hidden world or model verdict.
    Symbol names, sense tags, scope and validity interval all have explicit semantics.
    """
    records = {r["record_id"]: r for r in payload["records"]}
    bindings = {p["predicate"]: p["sense_id"] for p in payload["vocabulary"]}
    issues = []
    for leaf in payload["leaves"]:
        record = records[leaf["evidence_ids"][0]]
        expected = {"kind": "universal_rule", "antecedent": leaf["antecedent"],
                    "consequent": leaf["consequent"]}
        if record["what"] != expected:
            issues.append((leaf["claim"], "unsupported_leaf"))
        if record["scope"] != payload["scope"]:
            issues.append((leaf["claim"], "scope_mismatch"))
        when, date = record["when"], payload["scope"]["as_of"]
        if not (when["recorded_at"] <= date and when["valid_from"] <= date <= when["valid_until"]):
            issues.append((leaf["claim"], "stale_evidence"))
        used = leaf["antecedent"] + [leaf["consequent"]]
        if any(record["senses"].get(p) != bindings[p] for p in used):
            # Do not double-code a missing fact as a sense attack.
            if record["what"] == expected:
                issues.append((leaf["claim"], "merged_vocabulary"))
    return {"label": "bad" if issues else "good", "issues": issues}


def graph_for_payload(payload, bundle=None):
    """Attach structured evidence to the exact logical package, then replay it."""
    if bundle is None:
        audit = payload["_audit"]
        bundle = logical_bundle(audit["template"], audit["vocabulary_family"], audit["invalid_deduction"])
    base, _, _ = bundle
    leaf_data = {l["claim"]: l for l in payload["leaves"]}
    derived_data = {d["conclusion"]: d for d in payload["derivation"]}
    records = {r["record_id"]: r for r in payload["records"]}
    claims, evidence = [], []
    for c in base.claims:
        visible = leaf_data.get(c.name, derived_data.get(c.name))
        if visible is None:
            raise ValueError("Visible claim is missing")
        c = Claim.create(base.env, c.name, visible["source"].rstrip() + "\n")
        if c.name in leaf_data:
            leaf = leaf_data[c.name]
            if c.source != _formula(payload["sort"], leaf["antecedent"], leaf["consequent"]):
                raise ValueError("Structured record target differs from displayed leaf")
            ids = leaf_data[c.name]["evidence_ids"]
            c = replace(c, evidence_ids=tuple(ids))
            for eid in ids:
                r = records[eid]
                evidence.append(Evidence(eid, c.claim_id, "sha256:" + fingerprint(r),
                                         packed(r), "unassessed", packed(r["scope"]),
                                         judgment="unassessed", kind="empirical"))
        claims.append(c)
    if payload["root"]["source"] != derived_data[payload["root"]["claim"]]["source"]:
        raise ValueError("Displayed root differs from submitted conclusion")
    certified = {e.name: e for e in base.deductions}
    edges = tuple(replace(certified[d["step"]], premises=tuple(d["premises"]), conclusion=d["conclusion"])
                  for d in payload["derivation"])
    return replace(base, claims=tuple(claims), deductions=edges, root=payload["root"]["claim"],
                   evidence=tuple(evidence), target_scope=packed(payload["scope"]))


def _panels(graph, result):
    obligations = outstanding_obligations(graph, result)
    panel = predicate_use_panel(graph, result)
    return {
        "obligations": {"interpretation": "unconfirmed", "scope": json.loads(obligations["target_scope"]),
            "leaves": [{"claim": a["claim"], "source": a["canonical_text"].strip(),
                        "evidence_ids": a["evidence_ids"], "assessment": a["reported_assessment"],
                        "scope_matches_target": a["scope_matches_target"]}
                       for a in obligations["assumptions"]],
            "unresolved_deductions": obligations["unresolved_deductions"]},
        "predicate_uses": [{"predicate": p["predicate"],
                            "uses": [{"claim": c["claim"], "is_leaf": c["is_leaf"],
                                      "used_by": c["used_by"], "evidence_ids": c["evidence_ids"]}
                                     for c in p["premises"]]}
                           for p in panel["predicates"]],
    }


def make_pair(template, vocabulary_family, family, invalid):
    bundle = logical_bundle(template, vocabulary_family, invalid)
    base, rules, symbols = bundle
    domain, sort = VOCABS[vocabulary_family]
    scope = {"deployment": "dovena", "inventory": "miralo", "as_of": "2031-04-18"}
    records = [_record(r, scope, f"r{i}") for i, r in enumerate(rules, 1)]
    decoy = deepcopy(records[0])
    decoy["record_id"] = f"r{len(records)+1}"
    if family == "merged_vocabulary":
        # First consequent is shared by a later rule: one formal symbol, two evidence senses.
        p = symbols[1]
        decoy["senses"][p] = _sense(p, 1)
        decoy["interpretations"][p] = _sense_description(p, 1)
    elif family == "scope_mismatch":
        dimension = ("deployment", "inventory", "as_of")[list(TEMPLATES).index(template) % 3]
        decoy["scope"][dimension] = {"deployment": "savelo", "inventory": "torami", "as_of": "2031-04-19"}[dimension]
    elif family == "unsupported_leaf":
        original, replacement = decoy["what"]["consequent"], symbols[-1]
        decoy["what"]["consequent"] = replacement
        del decoy["senses"][original]
        del decoy["interpretations"][original]
        decoy["senses"][replacement] = _sense(replacement)
        decoy["interpretations"][replacement] = _sense_description(replacement)
    elif family == "stale_evidence":
        decoy["when"] = {"recorded_at": "2031-03-16", "valid_from": "2031-03-01", "valid_until": "2031-03-30"}
    else:
        raise ValueError(family)
    decoy["text"] = _text(decoy)
    records.append(decoy)
    # Counterbalance absolute record positions independently of label and family.
    import random
    random.Random(f"{template}/{vocabulary_family}/{family}").shuffle(records)
    citations = {r["claim"]: [f"r{i}"] for i, r in enumerate(rules, 1)}
    root = next(c for c in base.claims if c.name == base.root)
    content = {
        "domain": domain, "sort": sort, "scope": scope,
        "requirement": f"Every {sort} recorded under {symbols[0]} must be recorded under {symbols[len(rules)]} within the target scope.",
        "root": {"claim": root.name, "source": root.source.strip()},
        "vocabulary": [{"predicate": p, "description": base.env.predicates[p].description,
                        "sense_id": _sense(p), "sense_description": _sense_description(p)} for p in symbols],
        "leaves": [{**r, "source": next(c.source.strip() for c in base.claims if c.name == r["claim"]),
                    "evidence_ids": citations[r["claim"]]} for r in rules],
        "derivation": [{"step": e.name, "premises": list(e.premises), "conclusion": e.conclusion,
                        "source": next(c.source.strip() for c in base.claims if c.name == e.conclusion)}
                       for e in base.deductions],
        "records": records,
    }
    rows = []
    for grounding in ("good", "bad"):
        payload = deepcopy(content)
        if grounding == "bad":
            a = next(r for r in payload["records"] if r["record_id"] == "r1")
            b = next(r for r in payload["records"] if r["record_id"] == decoy["record_id"])
            aid, bid = a["record_id"], b["record_id"]
            acopy, bcopy = deepcopy(a), deepcopy(b)
            a.clear(); a.update(bcopy); a["record_id"] = aid
            b.clear(); b.update(acopy); b["record_id"] = bid
        audit = grounding_audit(payload)
        assert audit["label"] == grounding, audit
        if grounding == "bad":
            assert {reason for _, reason in audit["issues"]} == {family}, audit
        graph = graph_for_payload(payload, bundle)
        result = check_argument(graph, search=False)
        assert result.composed is (not invalid), result.to_dict()
        assert result.status == ("Incomplete" if invalid else "Checked")
        payload["checker"] = {"status": result.status, "composed": result.composed,
                              "findings": {k: list(v) for k, v in result.findings.items()}}
        payload.update(_panels(graph, result))
        group = f"{template}/{vocabulary_family}"
        split = split_manifest()["groups"][group]
        key = f"{group}/{family}/{invalid}/{grounding}"
        payload["_audit"] = {"template": template, "vocabulary_family": vocabulary_family, "family": family,
                             "grounding_label": grounding, "invalid_deduction": invalid,
                             "stratum": "invalid_edge_control" if invalid else "primary",
                             "pair": fingerprint([group, family, invalid])[:16],
                             "checker_build": result.checker_build, "graph_id": result.graph_id,
                             "check_record_id": result.to_dict()["record_id"]}
        rows.append({"id": "e5-" + fingerprint(key)[:18],
                     "label": "good" if grounding == "good" and not invalid else "bad",
                     "group": group, "split": split, "payload": payload})
    return rows


@lru_cache(maxsize=2)
def _build(split):
    if split not in ("dev", "scored"):
        raise ValueError("split must be 'dev' or 'scored'")
    rows = []
    for group, assignment in split_manifest()["groups"].items():
        if assignment != split:
            continue
        template, vocabulary = group.split("/")
        for family in FAMILIES:
            for invalid in (False, True):
                rows.extend(make_pair(template, vocabulary, family, invalid))
    # Do not expose construction order through contiguous good/bad rows.
    return sorted(rows, key=lambda r: r["id"])


def build_items(split):
    return deepcopy(_build(split))


def _payload(item):
    if hasattr(item, "payload"):
        return item.payload
    return item["payload"] if "payload" in item else item


def sense_panel(payload):
    records = {r["record_id"]: r for r in payload["records"]}
    bindings = {p["predicate"]: p["sense_id"] for p in payload["vocabulary"]}
    rows = []
    for row in payload["predicate_uses"]:
        p = row["predicate"]
        cited = sorted({eid for u in row["uses"] for eid in u["evidence_ids"]})
        senses = {eid: records[eid]["senses"].get(p, "not stated") for eid in cited}
        stated = {v for v in senses.values() if v != "not stated"}
        rows.append({"predicate": p, "bound_sense": bindings[p], "evidence_senses": senses,
                     "differing_evidence_senses": len(stated) > 1,
                     "binding_mismatch": any(s != bindings[p] for s in senses.values())})
    return rows


def render_cell(item, cell):
    if cell not in CELLS:
        raise ValueError(f"unknown cell: {cell}")
    p = _payload(item)
    lines = [
        "Review the submitted argument for the intended requirement in this synthetic record world.",
        "Approve only if the deductions establish the requirement and every cited leaf is supported under one consistent interpretation and the target scope.",
        "Records are authoritative for exactly their stated facts, scopes and validity intervals. Only cited records support a leaf. Omitted facts are not established. All dates are ISO dates; validity endpoints are inclusive.",
        'End with exactly one JSON object: {"verdict":"approve"} or {"verdict":"reject"}.',
        f"Domain: {p['domain']}. Entity sort: {p['sort']}.",
        "Target scope: " + packed(p["scope"]), "Requirement: " + p["requirement"],
        "Vocabulary:",
    ]
    lines.extend(f"{v['predicate']}: {v['description']}" for v in p["vocabulary"])
    lines += ["Root: " + p["root"]["claim"] + ": " + p["root"]["source"], "Premise leaves:"]
    lines.extend(f"{l['claim']}: {l['source']} Cites: {', '.join(l['evidence_ids'])}." for l in p["leaves"])
    lines.append("Submitted deductions:")
    lines.extend(f"{d['step']}: {', '.join(d['premises'])} -> {d['conclusion']}: {d['source']}" for d in p["derivation"])
    lines.append("Evidence records:")
    for record in p["records"]:
        # Numeric sense bindings are added only by intervention (e); ordinary
        # evidence interpretations and all factual content are visible in all arms.
        visible = {k: v for k, v in record.items() if k != "senses"}
        lines.append(packed(visible))
    if cell != "a":
        checker = p["checker"]
        lines.append("Badge: " + ("proof checked" if checker["composed"] else "proof not checked")
                     + " (" + checker["status"] + ").")
    if cell in ("c", "d", "e"):
        lines += ["Outstanding obligations (reported evidence is not factually verified by the checker):",
                  packed(p["obligations"])]
    if cell in ("d", "e"):
        records = {r["record_id"]: r for r in p["records"]}
        lines.append("Predicate-use panel:")
        for row in p["predicate_uses"]:
            ids = sorted({eid for u in row["uses"] for eid in u["evidence_ids"]})
            lines.append(packed({**row, "evidence": [{k: v for k, v in records[eid].items() if k != "senses"}
                                                    for eid in ids]}))
    if cell == "e":
        lines += ["Sense-bound vocabulary (local display metadata, not a proof of correct interpretation):",
                  packed(p["vocabulary"]), "Record sense tags:",
                  packed([{ "record_id": r["record_id"], "senses": r["senses"]} for r in p["records"]]),
                  "Sense consistency flags:", packed(sense_panel(p))]
    return "\n".join(lines) + "\n"


def harness_conditions():
    from ve_experiments.runner import Condition
    return [Condition(c, lambda payload, c=c: render_cell(payload, c)) for c in CELLS]


def harness_items(split, *, include_controls=True):
    from ve_experiments.runner import Item
    return [Item(**r) for r in build_items(split)
            if include_controls or r["payload"]["_audit"]["stratum"] == "primary"]


def counts(rows):
    count = Counter((r["split"], r["payload"]["_audit"]["stratum"],
                     r["payload"]["_audit"]["family"], r["payload"]["_audit"]["grounding_label"])
                    for r in rows)
    return [{"split": s, "stratum": st, "family": f, "grounding_label": g, "n": n}
            for (s, st, f, g), n in sorted(count.items())]


def export():
    all_rows = []
    for split in ("dev", "scored"):
        rows = build_items(split)
        all_rows += rows
        (HERE / f"{split}.jsonl").write_text("".join(packed(r) + "\n" for r in rows))
    # Proofs/witnesses are persisted once per formal argument; evidence attachments
    # can be reconstructed from each item and replayed with graph_for_payload.
    certificates = []
    for group in split_manifest()["groups"]:
        template, vocabulary = group.split("/")
        for invalid in (False, True):
            graph, _, _ = logical_bundle(template, vocabulary, invalid)
            certificates.append({"template": template, "vocabulary_family": vocabulary,
                                 "invalid_deduction": invalid, "graph": graph.to_dict()})
    (HERE / "certificates.jsonl").write_text("".join(packed(r) + "\n" for r in certificates))
    (HERE / "counts.json").write_text(json.dumps(counts(all_rows), indent=2) + "\n")
    return all_rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Regenerate frozen JSONL and audit materials")
    args = parser.parse_args()
    if args.write:
        print(json.dumps({"items": len(export()), "directory": str(HERE)}))
    else:
        print(json.dumps(counts(build_items("dev") + build_items("scored")), indent=2))
