"""Relay containers for the Lean norm-defaults route.

Lean owns the fill, diagnostics, report and identities. Python constructs only the
objects needed by existing document display and proof-search adapters from its
accepted elaboration row.
"""
from __future__ import annotations

import copy
from itertools import product

from .ast import Not, _Decoder, formula_from_data
from .environment import Environment
from .errors import CheckerUnavailable, VEError
from .norms import NormDocument, _bind

PROFILE = "norm-defaults@0"


def unsaid_name(predicate):
    return f"unsaid__{predicate}"


def fill_name(predicate):
    return f"unsaid--{predicate}"


def fill_description(predicate):
    return f"the text does not say whether {predicate}"


def _placeholder(data):
    """Build the accepted container vocabulary; Lean checks the resulting id."""
    data = copy.deepcopy(data)
    data["profiles"] = [p for p in data["profiles"] if p != PROFILE]
    for decl in data["vocabulary"]["predicates"].values():
        regulated = decl.get("regulated")
        if regulated is not None and regulated.get("default") == "unspecified":
            regulated["default"] = "deny"
    return data


class _Filled:
    def __init__(self, env, row, fill_premises):
        self.env = env
        self.order = tuple(row["order"])
        self.fill_premises = fill_premises
        self._premises = tuple((item["label"], formula_from_data(env, item["ast"], _generated=True))
                               for item in row["premises"])

    def premises(self):
        return self._premises

    def base_environment(self):
        raw = self.env.to_dict()
        raw["profiles"] = [p for p in raw["profiles"] if p not in ("norms@0", "readings@1")]
        raw["vocabulary"]["predicates"] = {
            p: decl for p, decl in raw["vocabulary"]["predicates"].items() if "regulated" not in decl}
        return Environment(raw)


class UnspecifiedDocument:
    """Container constructed from a Lean-accepted `norm-defaults-elaborate` row."""

    def __init__(self, env, units):
        from .norm_defaults_route import run_case
        self.env = env if type(env) is Environment else Environment(env)
        self.norms = [unit.to_dict() if hasattr(unit, "to_dict") else unit for unit in units]
        row = run_case({"id": "norm-defaults-elaborate", "kind": "norm-defaults-elaborate",
                        "environment": self.env.to_dict(), "norms": self.norms})
        raw = _placeholder(self.env.to_dict())
        for item in row["unsaid"]:
            predicate = item["name"].removeprefix("unsaid__")
            raw["vocabulary"]["predicates"][item["name"]] = {
                "arguments": item["sorts"], "description": fill_description(predicate)}
        try:
            filled_env = Environment(raw)
            self.author = NormDocument(self.env, units)
            self.fill_premises = tuple((label, formula_from_data(filled_env, item["ast"], _generated=True))
                                       for label, item in zip(row["fill_labels"], row["fill"], strict=True))
            self.filled = _Filled(filled_env, row, self.fill_premises)
        except Exception as exc:
            raise CheckerUnavailable("CheckerUnavailable: Lean accepted norm defaults that Python could not construct") from exc
        if filled_env.environment_id != row["filled_environment_id"] or self.env.environment_id != row["environment_id"]:
            raise CheckerUnavailable("CheckerUnavailable: norm-defaults environment identity mismatch")
        self.unspec = tuple(row["unspecified"])
        self.fill_hash = row["fill_hash"]
        self.document_hash = row["document_hash"]
        self.elaboration = row


def _propose_report_evidence(document, predicates, *, search_domain_size=2, prove=True,
                             tableau_steps=10_000):
    """Propose models or certificates; the Lean report replays every proposal."""
    from .entailment import prove_entailment
    from .norm_defaults_route import run_case, source_case
    from .search import find_countermodel

    base = document.filled.base_environment()
    fill = [formula for _, formula in document.fill_premises]
    witnesses, packages = {}, {}
    for item in document.elaboration["reached"]:
        predicate, sorts = item["predicate"], item["sorts"]
        if predicates is not None and predicate not in predicates:
            continue
        # `reached` is open over the predicate's argument tuple; Lean checked it.
        reached = _Decoder().decode(item["ast"])
        conclusion = _bind(Not(reached), sorts)
        found = find_countermodel(base, fill, conclusion, max_domain_size=search_domain_size)
        if found.status == "Found":
            model = found.model.to_dict()
            for values in product(*(model["domains"][sort] for sort in sorts)):
                candidate = source_case(document, "norm-defaults-gaps", model=model,
                                        predicate=predicate, tuple=list(values))
                if run_case(candidate)["gaps"] == "reachable":
                    witnesses[predicate] = {"model": model, "tuple": list(values)}
                    break
        if predicate not in witnesses and prove:
            proof = prove_entailment(base, fill, conclusion, max_steps=tableau_steps)
            if proof.status == "Found":
                packages[f"reached:{predicate}"] = {
                    "environment_id": document.elaboration["environment_id"],
                    "document_hash": document.document_hash,
                    "fill_hash": document.fill_hash,
                    "target": f"reached:{predicate}", "certificate": proof.certificate}
    return witnesses, packages


def report(document, *, model=None, translation=False, completions=None, unit_ids=None,
           witnesses=None, packages=None, predicates=None, **_options):
    """Return Lean's report row, including its residual and findings."""
    from .norm_defaults_route import run_case, source_case
    fields = {"translation": translation}
    if model is not None:
        fields["model"] = model.to_dict() if hasattr(model, "to_dict") else model
    elif witnesses is None and packages is None and (_options.get("prove") or _options.get("search_domain_size")):
        witnesses, packages = _propose_report_evidence(
            document, predicates, search_domain_size=_options.get("search_domain_size") or 2,
            prove=_options.get("prove", False), tableau_steps=_options.get("tableau_steps", 10_000))
    if completions is not None:
        fields["completions"] = completions
        fields["unit_ids"] = list(unit_ids or ())
    if witnesses is not None:
        fields["witnesses"] = witnesses
    if packages is not None:
        fields["packages"] = packages
    if predicates is not None:
        fields["predicates"] = list(predicates)
    return run_case(source_case(document, "norm-defaults-report", **fields))


def validate_completions(document, block, unit_ids):
    """Ask Lean to validate the block and return the accepted input for display."""
    report(document, completions=block, unit_ids=unit_ids)
    return block


def search_reached(document, predicate, *, max_domain_size=2):
    """Propose a reached witness and have Lean replay it before returning it."""
    if not isinstance(document, UnspecifiedDocument):
        # The frozen oracle's tests use the old document type. It is not a
        # production container and never supplies a public verdict.
        from conformance.frozen_norm_defaults import search_reached as frozen_search
        return frozen_search(document, predicate, max_domain_size=max_domain_size)
    from .model import FiniteModel
    from .norm_defaults_route import run_case, source_case
    witnesses, _ = _propose_report_evidence(document, (predicate,),
                                             search_domain_size=max_domain_size, prove=False)
    candidate = witnesses.get(predicate)
    if candidate is None:
        return None
    row = run_case(source_case(document, "norm-defaults-report", witnesses={predicate: candidate},
                               predicates=[predicate]))
    if row["report"][0]["reached"] != "reachable":
        return None
    raw = candidate["model"]
    filling = {name: frozenset(tuple(value) for value in values)
               for name, values in raw["relations"].items() if name.startswith("unsaid__")}
    base = copy.deepcopy(raw)
    base["relations"] = {name: values for name, values in base["relations"].items()
                         if not name.startswith("unsaid__")}
    return FiniteModel.from_dict(document.env, base), tuple(candidate["tuple"]), filling


def _profiled(raw, switched=()):
    data = copy.deepcopy(raw)
    data["profiles"] = sorted(set(data["profiles"]) | {PROFILE})
    for predicate in switched:
        data["vocabulary"]["predicates"][predicate]["regulated"]["default"] = "unspecified"
    return Environment(data)


def _point_statuses(document, model):
    from .norm_defaults_route import run_case, source_case
    states = {}
    yes = {item["name"]: [list(values) for values in product(*(model["domains"][s] for s in item["sorts"]))]
           for item in document.elaboration["unsaid"]}
    no = {item["name"]: [] for item in document.elaboration["unsaid"]}
    for item in document.elaboration["reached"]:
        for values in product(*(model["domains"][sort] for sort in item["sorts"])):
            case = source_case(document, "norm-defaults-status", model=model,
                               predicate=item["predicate"], tuple=list(values), method="enumerate")
            state = run_case(case)["point_status"]
            if state == "UNKNOWN" and yes:
                state = run_case({**case, "method": "undecided", "yes": yes, "no": no})["point_status"]
            states[(item["predicate"], values)] = state
    return states


def audit_completions(env, units, *, model=None, prove=True, **options):
    """Compose Lean's reports and statuses for each completion switch."""
    raw = env.to_dict()
    document = UnspecifiedDocument(_profiled(raw), units)
    base_report = report(document, model=model, prove=prove, search_domain_size=2, **options)
    lines = {item["predicate"]: item for item in base_report["report"]}
    before = _point_statuses(document, model) if model is not None else None
    entries = []
    for predicate in document.elaboration["order"]:
        line = lines[predicate]
        if line["completion"] == "unspecified":
            continue
        entry = {"predicate": predicate, "completion": line["completion"],
                 "default_reached": line["reached"]}
        if line["reached"] == "reachable":
            entry["witness"] = line["witness"]
        switched = UnspecifiedDocument(_profiled(raw, (predicate,)), units)
        if line["reached"] != "reachable":
            switched_row = report(switched, model=model, prove=prove, search_domain_size=2,
                                  predicates=(predicate,), **options)
            gap = switched_row["report"][0]
            entry["switched_gaps"] = gap["reached"]
            if gap["reached"] == "reachable":
                entry["switched_witness"] = gap["witness"]
            elif gap["reached"] == "none":
                _, packages = _propose_report_evidence(switched, (predicate,), prove=True)
                entry["certificate"] = packages[f"reached:{predicate}"]
        if before is not None:
            after = _point_statuses(switched, model)
            entry["changes_if_switched"] = [
                {"predicate": p, "tuple": list(values), "before": old, "after": after[(p, values)]}
                for (p, values), old in before.items() if old != after[(p, values)]]
        entries.append(entry)
    return {"environment_id": document.elaboration["environment_id"], "completions": entries}


def load_audit_source(raw: bytes):
    """Read a document or JSON audit source; file format handling stays in Python."""
    from .wire import loads_json
    if raw.startswith(b"---\n"):
        from .document import _parts, _split
        from .readings import active_reading_sets
        meta, _, _ = _split(raw)
        units = [unit for unit, _ in _parts(meta.get("units", []))]
        under = {r["unit"] for r in active_reading_sets(meta.get("reading_sets", []))}
        norms = [u["content"] for u in units if u.get("kind") == "norm" and u.get("id") not in under
                 and type(u.get("content")) is dict and set(u["content"]) == {"norm"}]
        return Environment(meta["environment"]), norms
    data = loads_json(raw)
    if type(data) is not dict or set(data) != {"environment", "norms"} or type(data["norms"]) is not list:
        raise VEError("InvalidInput: expected a ve-document@1 or {environment, norms}")  # relay-lint: file I/O
    return Environment(data["environment"]), data["norms"]
