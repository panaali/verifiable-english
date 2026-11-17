"""Execution adapters: one per document, the deterministic projection of a use case's answers (plan section 6).

An adapter calls the document's run() (never main(), which reruns the mutants and narrowing passes) and returns,
per item of the answer key's comparison, the answer tuple of the plan's table, the rule ids VE selected and the
case-model atoms (Opus round 2 point 6: B4's add-guard-true reads them). Timings, costs and prover counters are left
out. The answer fields:

- anthropic-rsp: `ve` of run()["comparison"];
- openai-preparedness: `ve` and, on the rows that carry it, `soft.ve` (a PF row has no release field);
- safety-framework: `ve`, `ve_rel` (DM and CCA release sets) and `premises` of the comparison main() writes,
  built by run.py's with_comparison(), D2/D3 rows included. FSF's run() also runs variants() and the
  default-sensitivity pass; the adapter keeps run() whole and leaves their output out of the projection.

`project` reads the same fields from a results dict, so a committed results.json projects to the same values.
"""
from __future__ import annotations

import json
from dataclasses import dataclass

ANSWER_FIELDS = {
    "anthropic-rsp": ("ve",),
    "openai-preparedness": ("ve", "soft.ve"),
    "safety-framework": ("ve", "ve_rel", "premises"),
}
DOCUMENTS = tuple(ANSWER_FIELDS)


@dataclass(frozen=True)
class Projection:
    """{item id: value} per kind; every value is built of tuples, strings, numbers, booleans and None. `agree` is
    the comparison row's own agreement with the key (the record's toward/away movement reads it)."""
    answers: dict
    rules: dict
    atoms: dict
    agree: dict


def freeze(value):
    """A JSON value as nested tuples: a list as a tuple, an object as its sorted (key, value) pairs."""
    value = json.loads(json.dumps(value, sort_keys=True))

    def walk(v):
        if isinstance(v, dict):
            return tuple((k, walk(v[k])) for k in sorted(v))
        if isinstance(v, list):
            return tuple(walk(x) for x in v)
        return v
    return walk(value)


def _field(row, dotted):
    node = row
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return None, False
        node = node[part]
    return node, True


def answers_of(document, rows):
    """{item id: ((field, value), ...)} over the comparison rows; a field a row does not carry is left out."""
    out = {}
    for row in rows:
        if row["id"] in out:
            raise ValueError(f"{document}: item {row['id']} twice in the comparison")
        out[row["id"]] = tuple((f, freeze(v)) for f in ANSWER_FIELDS[document]
                               for v, present in [_field(row, f)] if present)
    return out


def _collect(node, holder, found):
    """Every rule id in a `rules` list of a row under `holder` (a list of rows or a dict of rows), at any depth."""
    if isinstance(node, dict):
        for key, value in node.items():
            if key == holder:
                for row in value.values() if isinstance(value, dict) else value:
                    if isinstance(row, dict):
                        found.update(_ids(row.get("rules") or ()))
            _collect(value, holder, found)
    elif isinstance(node, list):
        for value in node:
            _collect(value, holder, found)
    return found


def _ids(rules):
    """The rule ids of a `rules` value: a list of ids, or of id groups (RSP C-doc's conflicting rule sets)."""
    for rule in rules:
        if isinstance(rule, str):
            yield rule
        elif isinstance(rule, list):
            yield from _ids(rule)
        else:
            raise ValueError(f"a rules entry is no rule id: {rule!r}")


def rules_of(document, items, ids):
    """{item id: sorted rule ids} from run()["items"]: RSP choices[*].rules, FSF details[*]["rules"], PF
    selected_rules. An item with no result (FSF's D2/D3 rows) has none."""
    out = {}
    for id_ in ids:
        result = items.get(id_)
        if result is None:
            out[id_] = ()
        elif document == "openai-preparedness":
            out[id_] = tuple(sorted(set(result["selected_rules"])))
        else:
            out[id_] = tuple(sorted(_collect(result, "choices" if document == "anthropic-rsp" else "details",
                                             set())))
    return out


def _common(sets):
    sets = [frozenset(s) for s in sets]
    return tuple(sorted(frozenset.intersection(*sets))) if sets else ()


def atoms_of(document, module, items, ids):
    """{item id: sorted atoms} of the item's case model, case plus facts, read through the module's own atom
    function. An atom is listed only when it holds in every model the item read: PF's atoms depend on the choice
    (RS2 nest), so they are intersected over the item's choices; FSF's over the alternatives of a case. An item
    with no case has none."""
    key = {entry["id"]: entry for entry in json.loads((module.HERE / "answer-key.json").read_text())["items"]}
    out = {}
    for id_ in ids:
        case_id = key.get(id_, {}).get("case")
        case = module.CASES.get(case_id) if case_id is not None else None
        if case is None:
            out[id_] = ()
        elif document == "anthropic-rsp":
            out[id_] = tuple(sorted(module.atoms(case)))
        elif document == "openai-preparedness":
            rows = (items.get(id_) or {}).get("choices") or [{"choice": {}}]
            out[id_] = _common(module.atoms(case, {**module.BASE, **row["choice"]}) for row in rows)
        else:
            case = module.item_case(id_, case)
            out[id_] = _common(module.fact_atoms() | module.case_atoms(s) for s in module.situations(case))
    return out


def project(document, results, module=None):
    """The projection of a results dict (live run() output or a committed results.json). Atoms need the module;
    without it they are left empty."""
    if document not in ANSWER_FIELDS:
        raise ValueError(f"no adapter for document {document!r}")
    answers = answers_of(document, results["comparison"])
    rules = rules_of(document, results["items"], answers)
    atoms = atoms_of(document, module, results["items"], answers) if module is not None else {}
    agree = {row["id"]: bool(row["agree"]) for row in results["comparison"]}
    return Projection(answers, rules, atoms, agree)


def run_document(document, module):
    """The document's results as main() builds them, without main(): run(), and for FSF with_comparison()."""
    results = module.run()
    if document == "safety-framework":
        results = module.with_comparison(results)
    return results


def adapt(document, module):
    """The deterministic projection of one run of `module` (the document's run.py, already imported)."""
    return project(document, run_document(document, module), module)
