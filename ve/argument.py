"""Committed claim DAGs and experimental, assumption-preserving certification.

Input artifacts contain data only. The tableau checker and finite evaluator,
never a search status or an evidence judgment, authorize logical findings.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
import sys
import subprocess
from typing import Any

from .ast import (Reach, Named, Body, Formula, Not, Unary, Binary, formula_from_data, formula_to_data)
from .environment import Environment, validate_identifier
from .errors import InvalidModel, ResourceLimit, VEError
from .identity import meaning_id, source_id
from .model import FiniteModel
from .parser import parse
from .printer import print_formula
from .search import check_countermodel, find_countermodel
from .wire import canonical_json, digest, loads_json, require_fields

ARGUMENT_VERSION = "ve-argument-tableau@1"
MAX_CLAIMS = 256
MAX_REFERENCES = 512


def _checker_build():
    from .surface.registry import records
    root = Path(__file__).parent
    modules = sorted(path.relative_to(root).as_posix() for path in root.rglob("*.py"))
    payload = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in modules}
    def symbol(value):
        return "" if value is None else f"{value.__module__}.{value.__qualname__}"
    payload["surface_records"] = [{
        "tag": record.wire_tag, "strict": record.strict_form,
        "english": list(record.english_keywords), "fluent": record.fluent_form,
        "grammar": record.grammar_production, "arity": record.wire_arity,
        "node_type": symbol(record.node_type),
        "hooks": {name: symbol(getattr(record, name)) for name in (
            "evaluator_hook", "witness_renderer", "parser_hook", "strict_parser_hook",
            "printer_hook", "fluent_hook", "english_renderer", "grammar_hook",
            "strict_grammar_hook", "wire_encoder", "wire_decoder", "fol_import_hook",
            "fol_export_hook", "typecheck_hook")},
        "traversal_hooks": ({name: symbol(fn) for name, fn in record.traversal_hooks.items()}
                            if record.traversal_hooks else {})}
        for record in sorted(records(), key=lambda item: item.wire_tag)]
    payload["python"] = sys.version
    return digest("ve-python-checker-build-v1\n", payload)


def _sequence(value, label):
    if type(value) not in (tuple, list):
        raise VEError(f"{label} must be an ordered tuple or list")
    return tuple(value)


def _text(value, label):
    if type(value) is not str or not value:
        raise VEError(f"{label} must be a nonempty string")
    return value


@dataclass(frozen=True, slots=True)
class Claim:
    name: str
    source: str
    ast: Formula
    environment_id: str
    source_id: str
    meaning_id: str
    evidence_ids: tuple[str, ...] = ()
    label: str = "asserted"

    def __post_init__(self):
        object.__setattr__(self, "evidence_ids", _sequence(self.evidence_ids, "Evidence ids"))

    @classmethod
    def create(cls, env, name, source, *, candidate_ast=None, evidence_ids=(), label="asserted"):
        validate_identifier(name)
        document = parse(env, source)
        if len(document.formulas) != 1:
            raise VEError("A claim must contain exactly one closed statement")
        ast = document.formulas[0]
        if candidate_ast is not None:
            candidate = (formula_from_data(env, candidate_ast)
                         if type(candidate_ast) is list else candidate_ast)
            if candidate != ast:
                raise VEError("Claim AST does not match its exact source")
        source = source.decode("ascii") if type(source) is bytes else source
        return cls(name, source, ast, env.environment_id, source_id(source, env),
                   meaning_id(env, ast), evidence_ids, _text(label, "Claim label"))

    @property
    def claim_id(self):
        # Aliases and factual support do not change the committed statement.
        payload = {"environment_id": self.environment_id,
                   "source_id": self.source_id, "meaning_id": self.meaning_id}
        if self.label != "asserted":
            payload["label"] = self.label
        return digest("ve-claim-v1\n", payload)

    def to_dict(self, env):
        result = {"name": self.name, "source": self.source, "ast": formula_to_data(env, self.ast),
                "environment_id": self.environment_id, "source_id": self.source_id,
                "meaning_id": self.meaning_id, "claim_id": self.claim_id,
                "evidence_ids": list(self.evidence_ids)}
        if self.label != "asserted":
            result["label"] = self.label
        return result

    @classmethod
    def from_dict(cls, env, data):
        require_fields(data, {"name", "source", "ast", "environment_id", "source_id",
                              "meaning_id", "claim_id", "evidence_ids"} |
                       ({"label"} if type(data) is dict and "label" in data else set()))
        claim = cls.create(env, data["name"], data["source"], candidate_ast=data["ast"],
                           evidence_ids=data["evidence_ids"], label=data.get("label", "asserted"))
        if claim.to_dict(env) != data:
            raise VEError("Claim commitment is stale or substituted")
        return claim


@dataclass(frozen=True, slots=True)
class Evidence:
    """A reported review, not an authenticated attestation or logical premise.

    snapshot_id identifies immutable inspected content, not a mutable URL alone.
    assessment_binding prevents accidental reuse after metadata substitution.
    Authentication and factual adequacy remain outside this prototype.
    """
    evidence_id: str
    claim_id: str
    snapshot_id: str
    passage: str
    reviewer: str
    target_scope: str
    judgment: str = "unassessed"
    kind: str = "empirical"
    assessment_binding: str = ""

    def __post_init__(self):
        if not self.assessment_binding:
            object.__setattr__(self, "assessment_binding", self.expected_binding())

    def expected_binding(self):
        return digest("ve-evidence-assessment-v1\n", {
            key: getattr(self, key) for key in self.__dataclass_fields__ if key != "assessment_binding"})

    def to_dict(self):
        return {key: getattr(self, key) for key in self.__dataclass_fields__}

    @classmethod
    def from_dict(cls, data):
        require_fields(data, set(cls.__dataclass_fields__))
        if not data["assessment_binding"]:
            raise VEError("Evidence assessment requires its original binding")
        return cls(**data)


@dataclass(frozen=True, slots=True)
class Deduction:
    name: str
    premises: tuple[str, ...]
    conclusion: str
    certificates: tuple[dict, ...] = ()
    countermodels: tuple[FiniteModel, ...] = ()

    def __post_init__(self):
        for key in ("premises", "certificates", "countermodels"):
            object.__setattr__(self, key, _sequence(getattr(self, key), key))

    def to_dict(self):
        return {"name": self.name, "premises": list(self.premises), "conclusion": self.conclusion,
                "certificates": list(self.certificates),
                "countermodels": [m.to_dict() for m in self.countermodels]}


@dataclass(frozen=True, slots=True)
class ArgumentGraph:
    env: Environment
    claims: tuple[Claim, ...]
    deductions: tuple[Deduction, ...]
    root: str
    evidence: tuple[Evidence, ...] = ()
    target_scope: str = "unspecified"

    def __post_init__(self):
        for key in ("claims", "deductions", "evidence"):
            object.__setattr__(self, key, _sequence(getattr(self, key), key))

    def to_dict(self):
        return {"version": ARGUMENT_VERSION, "environment": self.env.to_dict(),
                "claims": [c.to_dict(self.env) for c in self.claims],
                "deductions": [d.to_dict() for d in self.deductions], "root": self.root,
                "evidence": [e.to_dict() for e in self.evidence], "target_scope": self.target_scope}

    def to_json(self):
        return canonical_json(self.to_dict()).decode("utf-8")

    @property
    def graph_id(self):
        return digest("ve-argument-package-v1\n", self.to_dict())

    @classmethod
    def from_dict(cls, data):
        canonical_json(data)
        require_fields(data, {"version", "environment", "claims", "deductions", "root",
                              "evidence", "target_scope"})
        if data["version"] != ARGUMENT_VERSION:
            raise VEError("Unsupported argument version")
        env = Environment.from_dict(data["environment"])
        claims = tuple(Claim.from_dict(env, c) for c in _sequence(data["claims"], "Claims"))
        deductions = []
        for d in _sequence(data["deductions"], "Deductions"):
            require_fields(d, {"name", "premises", "conclusion", "certificates", "countermodels"})
            deductions.append(Deduction(d["name"], d["premises"], d["conclusion"], d["certificates"],
                tuple(FiniteModel.from_dict(env, m) for m in _sequence(d["countermodels"], "Countermodels"))))
        graph = cls(env, claims, tuple(deductions), data["root"],
                    tuple(Evidence.from_dict(e) for e in _sequence(data["evidence"], "Evidence")),
                    data["target_scope"])
        _validate_graph(graph)
        return graph

    @classmethod
    def from_json(cls, data):
        return cls.from_dict(loads_json(data))


def deduction_identity(graph, deduction):
    claims = {c.name: c for c in graph.claims}
    return digest("ve-deduction-v1\n", {"version": ARGUMENT_VERSION,
        "environment_id": graph.env.environment_id, "name": deduction.name,
        "premises": [{"name": n, "claim_id": claims[n].claim_id} for n in deduction.premises],
        "conclusion": {"name": deduction.conclusion, "claim_id": claims[deduction.conclusion].claim_id}})


def _validate_graph(graph):
    if type(graph) is not ArgumentGraph or type(graph.env) is not Environment:
        raise VEError("Expected an ArgumentGraph under one validated environment")
    if not graph.claims or len(graph.claims) > MAX_CLAIMS:
        raise ResourceLimit("An argument requires 1 to 256 claims")
    if len(graph.deductions) > MAX_CLAIMS:
        raise ResourceLimit("An argument permits at most one deduction per claim")
    _text(graph.target_scope, "Target scope")
    claims = {}
    for c in graph.claims:
        if type(c) is not Claim:
            raise VEError("Expected a committed Claim")
        validate_identifier(c.name)
        if c.name in claims:
            raise VEError(f"Duplicate claim alias: {c.name}")
        expected = Claim.create(graph.env, c.name, c.source, candidate_ast=c.ast,
                                evidence_ids=c.evidence_ids, label=c.label)
        if c != expected:
            raise VEError(f"Stale or substituted claim: {c.name}")
        for eid in c.evidence_ids:
            _text(eid, "Cited evidence id")
        if len(set(c.evidence_ids)) != len(c.evidence_ids):
            raise VEError("Duplicate evidence citation")
        claims[c.name] = c
    if type(graph.root) is not str or graph.root not in claims:
        raise VEError("Root must resolve to a committed claim")
    by_conclusion, names, references = {}, set(), 0
    for edge in graph.deductions:
        if type(edge) is not Deduction:
            raise VEError("Expected a Deduction")
        validate_identifier(edge.name)
        if edge.name in names:
            raise VEError(f"Duplicate deduction alias: {edge.name}")
        names.add(edge.name)
        for n in (*edge.premises, edge.conclusion):
            if type(n) is not str or n not in claims:
                raise VEError(f"Unresolved claim reference: {n!r}")
        if any(type(m) is not FiniteModel for m in edge.countermodels):
            raise VEError("Countermodel artifacts must be FiniteModel objects")
        for model in edge.countermodels:
            try:
                checked_model = FiniteModel.from_dict(graph.env, model.to_dict())
            except (TypeError, KeyError, AttributeError) as exc:
                raise InvalidModel("Malformed in-memory countermodel fields") from exc
            if (model.environment_id != graph.env.environment_id or
                    model.model_id != checked_model.model_id):
                raise InvalidModel("Countermodel commitment is stale or belongs to another environment")
        if edge.conclusion in by_conclusion:
            raise VEError("Each conclusion must have exactly one submitted deduction")
        by_conclusion[edge.conclusion] = edge
        references += len(edge.premises)
    if references > MAX_REFERENCES:
        raise ResourceLimit("Argument exceeds 512 premise references")
    # All submitted components are checked, including components outside the root.
    visiting, visited = set(), set()
    def visit(name):
        if name in visiting:
            raise VEError(f"Dependency cycle at claim {name}")
        if name in visited:
            return
        visiting.add(name)
        edge = by_conclusion.get(name)
        if edge:
            for premise in edge.premises:
                visit(premise)
        visiting.remove(name)
        visited.add(name)
    for name in claims:
        visit(name)
    evidence = {}
    claim_ids = {c.claim_id for c in claims.values()}
    for item in graph.evidence:
        if type(item) is not Evidence:
            raise VEError("Expected Evidence metadata")
        for key in item.__dataclass_fields__:
            _text(getattr(item, key), f"Evidence {key}")
        if item.evidence_id in evidence:
            raise VEError("Duplicate evidence id")
        if item.claim_id not in claim_ids:
            raise VEError("Evidence is bound to an absent or substituted claim")
        if item.judgment not in ("accepted", "disputed", "unassessed"):
            raise VEError("Unknown evidence judgment")
        if item.kind not in ("empirical", "interpretive", "definitional", "normative"):
            raise VEError("Unknown evidence kind")
        if item.snapshot_id.startswith(("http://", "https://")):
            raise VEError("A mutable URL alone is not an evidence snapshot identity")
        if item.assessment_binding != item.expected_binding():
            raise VEError("Stale evidence assessment binding")
        evidence[item.evidence_id] = item
    for c in claims.values():
        for eid in c.evidence_ids:
            if eid not in evidence or evidence[eid].claim_id != c.claim_id:
                raise VEError(f"Unresolved or substituted evidence citation: {eid}")
    canonical_json(graph.to_dict())  # Aggregate 16 MiB including models/certificates.
    return claims, by_conclusion, evidence


@dataclass(frozen=True, slots=True)
class ArgumentResult:
    status: str
    graph_id: str = ""
    environment_id: str = ""
    root: str = ""
    findings: dict[str, tuple[str, ...]] = field(default_factory=dict)
    remaining_assumptions: tuple[str, ...] = ()
    unresolved_obligations: tuple[str, ...] = ()
    composed: bool = False
    edges: tuple[dict, ...] = ()
    errors: tuple[dict, ...] = ()
    composition: dict = field(default_factory=dict)
    checker_build: str = ""
    contradictory_premises: tuple[str, ...] = ()
    warnings: tuple[dict, ...] = ()
    profiles: tuple[str, ...] = ()
    lean_checked: bool = False
    lean_detail: str = "Lean replay not requested"
    premises: dict = field(default_factory=dict)

    def to_dict(self):
        data = {"version": ARGUMENT_VERSION, "assurance": "experimental", "status": self.status,
                "graph_id": self.graph_id, "environment_id": self.environment_id, "root": self.root,
                "findings": {k: list(v) for k, v in self.findings.items()},
                "remaining_assumptions": list(self.remaining_assumptions),
                "unresolved_obligations": list(self.unresolved_obligations), "composed": self.composed,
                "proof": "Python replay checked" if self.composed else "not_checked", "intent": "unconfirmed",
                "profiles": list(self.profiles), "lean_checked": self.lean_checked,
                "lean_status": "Lean-checked: " + ("yes" if self.lean_checked else "no"),
                "lean_detail": self.lean_detail,
                "approval": "unassessed", "edges": list(self.edges), "errors": list(self.errors),
                "composition": self.composition, "checker_build": self.checker_build,
                "contradictory_premises": list(self.contradictory_premises),
                "warnings": list(self.warnings)}
        if self.premises:
            data["premises"] = self.premises
        data["record_id"] = hashlib.sha256(b"ve-argument-diagnostic-record-v1\n" + json.dumps(
            data, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode("ascii")).hexdigest()
        return data

    def to_json(self):
        # Diagnostic records may include null; semantic input packages may not.
        return json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=False)


def _check_edge(graph, edge, claims, *, search, max_proof_steps, max_domain_size,
                max_models, max_evaluations):
    from .entailment import prove_entailment, check_entailment_certificate
    env = graph.env
    premises = tuple(claims[n].ast for n in edge.premises)
    conclusion = claims[edge.conclusion].ast
    edge_id = deduction_identity(graph, edge)
    findings, artifacts, errors, attempts = set(), [], [], []
    satisfying_models = []

    def replay(envelope, *, submitted):
        try:
            require_fields(envelope, {"edge_id", "direction", "proof"})
            if envelope["edge_id"] != edge_id or envelope["direction"] not in ("follows", "refuted"):
                raise VEError("Certificate names a stale edge or unsupported direction")
            direction = envelope["direction"]
            target = conclusion if direction == "follows" else Not(conclusion)
            checked = check_entailment_certificate(env, premises, target, envelope["proof"],
                                                   max_steps=max_proof_steps)
            artifacts.append({"kind": direction, "submitted": submitted,
                              "certificate": envelope, "check": checked.to_dict()})
            if checked.valid:
                findings.add(direction)
            else:
                errors.append({"code": checked.status, "message": "Certificate replay failed"})
        except VEError as exc:
            artifacts.append({"kind": "invalid_certificate", "submitted": submitted,
                              "certificate": envelope})
            errors.append(exc.to_dict())

    def witness(model, *, submitted):
        try:
            checked = check_countermodel(env, premises, conclusion, model, max_evaluations=max_evaluations)
            artifacts.append({"kind": "gap", "submitted": submitted, "model": model.to_dict(),
                              "model_id": model.model_id, "check": {"valid": checked.valid,
                              "status": checked.status, "premise_values": list(checked.premise_values),
                              "conclusion_value": checked.conclusion_value}})
            if (len(checked.premise_values) == len(premises) and all(checked.premise_values)
                    and checked.conclusion_value is not None):
                satisfying_models.append(model.model_id)
            if checked.valid:
                findings.add("gap")
            else:
                errors.append({"code": checked.status, "message": "Submitted witness is not a checked gap"})
        except VEError as exc:
            errors.append(exc.to_dict())

    for cert in edge.certificates:
        replay(cert, submitted=True)
    for model in edge.countermodels:
        witness(model, submitted=True)
    if search:
        for direction, target in (("follows", conclusion), ("refuted", Not(conclusion))):
            if direction in findings:
                continue
            try:
                proof = prove_entailment(env, premises, target, max_steps=max_proof_steps)
            except ResourceLimit as exc:
                attempts.append({"kind": direction, "status": "ResourceLimit", "detail": exc.message})
                continue
            attempts.append({"kind": direction, "status": proof.status})
            if proof.status == "Found":
                replay({"edge_id": edge_id, "direction": direction, "proof": proof.certificate}, submitted=False)
        if "gap" not in findings:
            try:
                candidate = find_countermodel(env, premises, conclusion, max_domain_size=max_domain_size,
                                             max_models=max_models, max_evaluations=max_evaluations)
                attempts.append({"kind": "gap", "status": candidate.status,
                                 "models_checked": candidate.models_checked, "detail": candidate.detail})
                if candidate.status == "Found":
                    witness(candidate.model, submitted=False)
            except ResourceLimit as exc:
                attempts.append({"kind": "gap", "status": "ResourceLimit", "detail": exc.message})
    ordered = tuple(f for f in ("follows", "refuted", "gap") if f in findings)
    from .vacuity import premise_status
    premise_report = premise_status(env, premises, max_proof_steps=max_proof_steps,
        max_domain_size=max_domain_size, max_models=max_models,
        max_evaluations=max_evaluations)
    if premise_report["status"] == "INCONSISTENT":
        for artifact in artifacts:
            if artifact["kind"] in ("follows", "refuted") and artifact.get("check", {}).get("valid"):
                artifact["vacuous"] = True
    return {"name": edge.name, "edge_id": edge_id, "premises": list(edge.premises),
            "conclusion": edge.conclusion, "findings": list(ordered),
            "premise_status": premise_report,
            "status": "established" if ordered else "unresolved",
            "contradictory_premises": "follows" in findings and "refuted" in findings,
            "checker_conflict": ("follows" in findings and "gap" in findings) or
                ("follows" in findings and "refuted" in findings and bool(satisfying_models)),
            "satisfying_premise_model_ids": satisfying_models,
            "artifacts": artifacts, "errors": errors, "search_attempts": attempts}


def _lean_deductions(graph, claims, records, reachable, executable):
    """Optional independent replay; never infer a Lean result from Python success."""
    if executable is None:
        return False, "Lean replay not requested"
    cases = []
    for record in records:
        if record['conclusion'] not in reachable:
            continue
        candidates = [a for a in record['artifacts'] if a['kind'] == 'follows'
                      and a.get('check', {}).get('valid') and 'certificate' in a]
        if not candidates:
            return False, "A supporting deduction has no certificate"
        cases.append({'id': record['edge_id'], 'environment': graph.env.to_dict(),
                      'premises': [formula_to_data(graph.env, claims[n].ast) for n in record['premises']],
                      'conclusion': formula_to_data(graph.env, claims[record['conclusion']].ast),
                      'certificate': candidates[0]['certificate']['proof']})
    if not cases:
        return False, "No deduction certificates to replay"
    try:
        proc = subprocess.run([str(executable), 'check-certificate'], input=canonical_json(cases),
                              capture_output=True, timeout=60)
        rows = loads_json(proc.stdout)
        expected = [{'id': c['id'], 'status': 'ok', 'valid': True} for c in cases]
        if proc.returncode == 0 and rows == expected:
            return True, f"{len(cases)} supporting deduction certificates accepted by Lean"
        return False, "Lean did not accept every supporting deduction certificate"
    except (OSError, subprocess.TimeoutExpired, VEError, ValueError):
        return False, "Lean replay unavailable or failed"


def check_argument(graph, *, search=True, max_proof_steps=10_000, max_domain_size=1,
                   max_models=1_000, max_evaluations=100_000, lean_executable=None):
    """Validate and check a submitted DAG; never discharge factual assumptions.

    ``search=False`` performs certificate/witness replay only. Search bounds are
    per edge/direction. Search failure is operational information, never a gap.
    Invalid submissions return diagnostics; invalid constructor inputs may raise.
    ``lean_executable`` optionally replays the supporting deduction certificates;
    the result labels actual Lean acceptance separately from Python replay.
    Host cancellation propagates and is never converted into a logical finding.
    """
    try:
        if type(search) is not bool:
            raise VEError("search must be Boolean")
        for value in (max_proof_steps, max_domain_size, max_models, max_evaluations):
            if type(value) is not int or value < 0:
                raise VEError("Checking budgets must be nonnegative integers")
        claims, by_conclusion, _ = _validate_graph(graph)
        records = tuple(_check_edge(graph, edge, claims, search=search,
                        max_proof_steps=max_proof_steps, max_domain_size=max_domain_size,
                        max_models=max_models, max_evaluations=max_evaluations) for edge in graph.deductions)
        findings = {r["name"]: tuple(r["findings"]) for r in records}
        reachable, pending = set(), [graph.root]
        while pending:
            name = pending.pop()
            if name in reachable:
                continue
            reachable.add(name)
            edge = by_conclusion.get(name)
            if edge:
                pending.extend(edge.premises)
        leaves = tuple(c.name for c in graph.claims if c.name in reachable and c.name not in by_conclusion)
        unresolved = tuple(c.name for c in graph.claims if c.name in reachable and c.name in by_conclusion
                           and "follows" not in findings[by_conclusion[c.name].name])
        # A rejected extra artifact or failed search cannot erase checked evidence.
        errors = tuple({"edge": r["name"], **e} for r in records if not r["findings"]
                       for e in r["errors"])
        warnings = tuple({"edge": r["name"], **e} for r in records if r["findings"]
                         for e in r["errors"])
        warnings += tuple({"edge": r["name"], "code": "ResourceLimit",
                           "message": f"{a['kind']} search exhausted its budget"}
                          for r in records for a in r["search_attempts"]
                          if a["status"] == "ResourceLimit")
        contradictory = tuple(r["name"] for r in records if r["contradictory_premises"])
        conflict = any(r["checker_conflict"] for r in records)
        search_exhausted = any(r["conclusion"] in unresolved and not r["findings"] and
                              any(a["status"] == "ResourceLimit" for a in r["search_attempts"])
                              for r in records)
        status = ("CheckerConflict" if conflict else
                  "ContradictoryPremises" if contradictory else
                  "ResourceLimit" if errors and all(e["code"] == "ResourceLimit" for e in errors) else
                  "InvalidInput" if errors else
                  "ResourceLimit" if unresolved and search_exhausted else
                  "Incomplete" if unresolved else "Checked")
        composed = status == "Checked"
        composition = {}
        checker_build = _checker_build()
        if composed:
            # This is a checked composition record, not a new tableau proof.
            composition = {"rule": "acyclic-implication-composition", "environment_id": graph.env.environment_id,
                "checker_build": checker_build,
                "root_claim_id": claims[graph.root].claim_id,
                "assumption_claim_ids": [claims[n].claim_id for n in leaves],
                "supporting_edge_ids": [r["edge_id"] for r in records if r["conclusion"] in reachable],
                "assumptions": [claims[n].to_dict(graph.env) for n in leaves]}
            if graph.env.language == "ve.core@0.2":
                from .background import background
                composition["assumptions"].extend({
                    "label": "background:" + item.generator,
                    "ast": formula_to_data(graph.env, item.formula),
                    "meaning_id": meaning_id(graph.env, item.formula)}
                    for item in background(graph.env))
            composition["record_id"] = digest("ve-composition-v1\n", composition)
        lean_checked, lean_detail = (_lean_deductions(graph, claims, records, reachable, lean_executable)
                                     if composed else (False, "Root deductions are not established"))
        from .vacuity import premise_status
        root_premises = tuple(claims[name].ast for name in leaves)
        premise_report = premise_status(graph.env, root_premises,
            max_proof_steps=max_proof_steps, max_domain_size=max_domain_size,
            max_models=max_models, max_evaluations=max_evaluations)
        if premise_report["status"] == "INCONSISTENT":
            for record in records:
                for artifact in record["artifacts"]:
                    if artifact["kind"] == "follows" and artifact.get("check", {}).get("valid"):
                        artifact["vacuous"] = True
        return ArgumentResult(status, graph.graph_id, graph.env.environment_id, graph.root,
                              findings, leaves, unresolved, composed, records, errors, composition, checker_build,
                              contradictory, warnings, tuple(graph.env.profiles), lean_checked, lean_detail,
                              premise_report)
    except (VEError, RecursionError) as exc:
        if isinstance(exc, RecursionError):
            exc = ResourceLimit("Argument exceeds runtime recursion budget")
        return ArgumentResult("ResourceLimit" if isinstance(exc, ResourceLimit) else "InvalidInput",
                              errors=(exc.to_dict(),))


def _display_context(graph, result=None):
    context = _validate_graph(graph)
    if result is not None and result.graph_id != graph.graph_id:
        raise VEError("Checking record is stale for this argument package")
    return context


def outstanding_obligations(graph, result):
    """E5 display: logical status and review obligations remain separate."""
    claims, _, evidence = _display_context(graph, result)
    assumptions = []
    for name in result.remaining_assumptions:
        claim = claims[name]
        items = [evidence[eid] for eid in claim.evidence_ids]
        judgments = [e.judgment for e in items]
        assessment = ("disputed" if "disputed" in judgments else "accepted" if judgments and
                      all(j == "accepted" for j in judgments) else "unassessed")
        scopes_match = bool(items) and all(e.target_scope == graph.target_scope for e in items)
        assumptions.append({"claim": name, "claim_id": claim.claim_id, "source": claim.source,
            "canonical_text": print_formula(graph.env, claim.ast) + ".\n",
            "evidence_ids": list(claim.evidence_ids), "evidence": [e.to_dict() for e in items],
            "reported_assessment": assessment, "scope_matches_target": scopes_match,
            "outstanding": assessment != "accepted" or not scopes_match,
            "logical_assumption": True})
    return {"graph_id": result.graph_id, "assurance": "experimental", "status": result.status,
        "proof": "Python replay checked under listed assumptions" if result.composed else "not checked for the root",
        "profiles": list(result.profiles), "lean_checked": result.lean_checked,
        "lean_status": "Lean-checked: " + ("yes" if result.lean_checked else "no"),
        "lean_detail": result.lean_detail,
        "root": claims[graph.root].to_dict(graph.env), "target_scope": graph.target_scope,
        "interpretation": {"status": "unconfirmed", "outstanding": True,
                           "environment_id": graph.env.environment_id},
        "assumptions": assumptions, "unresolved_deductions": list(result.unresolved_obligations),
        "contradictory_premises": list(result.contradictory_premises),
        **({"premises": result.premises} if result.premises else {}),
        "warnings": list(result.warnings),
        "approval": "unassessed", "evidence_assurance": "reported metadata; not authenticated or verified"}


def _predicates(formula):
    from .surface.registry import by_node
    found, pending = set(), [formula]
    while pending:
        node = pending.pop()
        record = by_node(node)
        if record is not None and record.traversal_hooks is not None:
            hook = record.traversal_hooks.get("predicates")
            if hook is not None:
                names, children = hook(node)
                found.update(names)
                pending.extend(children)
                continue
        if type(node) in (Unary, Binary):
            found.add(node.predicate)
        if type(node) is Reach:
            if type(node.edge) is Named:
                found.add(node.edge.relation)
            else:
                pending.append(node.edge.formula)
        for key in ("body", "left", "right"):
            child = getattr(node, key, None)
            if child is not None:
                pending.append(child)
    return found


def predicate_use_panel(graph, result=None):
    """Every premise use (including intermediate premises) and cited evidence.

    Uses outside the root component remain visible and explicitly marked.
    Evidence scope incompatibility is exposed for review, not proved false.
    """
    claims, by_conclusion, evidence = _display_context(graph, result)
    uses = {name: [] for name in claims}
    for edge in graph.deductions:
        for name in edge.premises:
            if edge.name not in uses[name]:
                uses[name].append(edge.name)
    reachable, pending = set(), [graph.root]
    while pending:
        name = pending.pop()
        if name in reachable:
            continue
        reachable.add(name)
        if name in by_conclusion:
            pending.extend(by_conclusion[name].premises)
    panel = []
    for predicate, decl in graph.env.predicates.items():
        rows = []
        for claim in graph.claims:
            if (uses[claim.name] or claim.name not in by_conclusion) and predicate in _predicates(claim.ast):
                rows.append({"claim": claim.name, "claim_id": claim.claim_id, "source": claim.source,
                    "is_leaf": claim.name not in by_conclusion, "used_by": uses[claim.name],
                    "supports_root": claim.name in reachable, "evidence_ids": list(claim.evidence_ids),
                    "evidence": [evidence[eid].to_dict() for eid in claim.evidence_ids]})
        panel.append({"predicate": predicate, "description": decl.description,
                      "arguments": list(decl.arguments), "premises": rows})
    return {"graph_id": graph.graph_id, "environment_id": graph.env.environment_id, "predicates": panel}
