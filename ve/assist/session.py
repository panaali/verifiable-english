"""Interactive, sentence-level assisted formalisation (``ve assist``).

A session holds frozen targets, source sentences, an environment, and a graph
of nodes. Every node is one closed VE formula, anchored to the source
sentences it formalises. An *assumption* has no parents; a *step* has parents
and must be checked by ``check_step``. Nothing enters the graph without an
explicit author action, and every action (including rejected ones) is logged
in an append-only ledger that deterministically replays.

Trust boundary: the tableau certificate checker and ``check_countermodel`` are
the only authorities for "follows" and "countermodel". Everything else here
(anchoring, coverage, load-bearing analysis, lexical gates, the proposer) is
bookkeeping that reports, never certifies. Fidelity to the prose is the
author's responsibility and is audited outside the tool.
"""
from __future__ import annotations

from copy import deepcopy
import inspect
import json
import secrets
import warnings

from .. import ast, stream_audit
from ..entailment import check_entailment_certificate, prove_entailment
from ..environment import Environment
from ..errors import CheckerUnavailable, VEError
from ..parser import parse
from ..printer import print_formula
from ..search import check_countermodel, find_countermodel
from .ground import ground_countermodel
from .sources import load_source
# The session is assembled from three modules (AR-9); every name they define is re-exported here.
from .session_proposals import _Proposals
from .session_state import (  # noqa: F401 -- ORIGINS and the formula helpers re-exported
    DEFAULT_OPTIONS, ORIGINS, SESSION_FORMAT, TOOL_VERSION, AssistError, LedgerReplayError, Node, _Ledger,
    _conjuncts, _constants_of, _ident, _names, _now, _predicates_of, _sha, _symbols_of, config_digest)
from .session_views import _Views


class AssistSession(_Ledger, _Proposals, _Views):
    """One authoring session. Use ``apply`` (or the JSON tool API) to act."""

    # Deterministic needles of the canonical sanitizer (``ve.stream_audit``) for everything the session
    # logs or returns: the known credential prefixes. A backend's live token is applied where the backend's
    # output enters the session (``proposer._call``), so replay without the backend is identical.
    SECRET_NEEDLES = stream_audit.needles_for(None)

    def __init__(self, config):
        config = deepcopy(config)
        if config.get("format") != SESSION_FORMAT:
            raise AssistError("Not a ve assist session configuration")
        self.config = config
        self.options = {**DEFAULT_OPTIONS, **config.get("options", {})}
        unknown = set(self.options) - set(DEFAULT_OPTIONS)
        if unknown:
            raise AssistError("Unknown session options: " + ", ".join(sorted(unknown)))
        self.env = Environment(config["environment"])
        self.overlay = config.get("english_vocabulary")
        source = load_source(config["source"])
        self.sentences = {s["id"]: s for s in source["sentences"]}
        self.sentence_order = [s["id"] for s in source["sentences"]]
        self.targets = {}
        for row in config.get("targets", []):
            tid = _ident(row.get("id"), "target id")
            if row.get("sentence") not in self.sentences:
                raise AssistError(f"Target {tid} names an unknown sentence {row.get('sentence')!r}")
            if self.sentences[row["sentence"]]["role"] != "claimed":
                raise AssistError(f"Target {tid} must be a claimed sentence; {row['sentence']} is "
                                  f"{self.sentences[row['sentence']]['role']!r}")
            if tid in self.targets:
                raise AssistError(f"Duplicate target id {tid}")
            self.targets[tid] = {"id": tid, "sentence": row["sentence"], "formula": None, "text": None,
                                 "frozen_by": None}
            if row.get("formula"):
                formula, _ = self._parse(row["formula"], "auto")
                vacuity = self._reject_vacuous(tid, formula)
                self.targets[tid].update(formula=formula, text=self._canonical(formula), frozen_by="config",
                                         vacuity=vacuity)
        if not self.targets:
            raise AssistError("A session needs at least one target sentence")
        self.nodes: dict[str, Node] = {}
        self.checks: dict[str, dict] = {}
        self.waivers: dict[str, str] = {}
        self.declared: dict[str, dict] = {}
        self.proposals: dict[str, dict] = {}
        self.candidates: dict[str, dict] = {}
        self.suggestions: dict[str, dict] = {}
        self.events: list[dict] = []
        self.proposer = None  # injected callable, see ve.assist.proposer
        self._replaying = None
        self._leftover_calls = 0
        self._seq = None

    # ------------------------------------------------------------------ creation
    @classmethod
    def create(cls, environment, source, targets, *, english_vocabulary=None, options=None, metadata=None):
        env = environment if isinstance(environment, dict) else environment.to_dict()
        # session_id names this session's backend calls (item ids in the calls ledger). It is fixed at
        # creation and survives metadata edits, so calls cannot be orphaned by re-digesting the config.
        config = {"format": SESSION_FORMAT, "tool_version": TOOL_VERSION, "session_id": secrets.token_hex(8),
                  "environment": env,
                  "english_vocabulary": english_vocabulary, "source": source, "targets": targets,
                  "options": options or {}, "metadata": metadata or {}, "created": _now()}
        session = cls(config)
        session.config["options"] = dict(session.options)
        session.config["config_digest"] = config_digest(session.config)
        return session

    @property
    def session_id(self):
        return self.config.get("session_id") or str(self.config.get("config_digest", "session"))[:16]

    # ------------------------------------------------------------------ helpers
    def _canonical(self, formula):
        return print_formula(self.env, formula) + "."

    def _parse(self, text, surface="auto"):
        if type(text) is not str or not text.strip():
            raise AssistError("Formula text must be a nonempty string")
        body = text.strip()
        strict = body if body.endswith(".") else body + "."
        errors = []
        if surface in ("auto", "strict"):
            try:
                document = parse(self.env, strict + "\n")
                if len(document.formulas) != 1:
                    raise AssistError("A node is exactly one statement")
                return document.formulas[0], "strict"
            except AssistError:
                raise
            except VEError as exc:
                errors.append(exc)
                if surface == "strict":
                    raise
        if surface in ("auto", "english"):
            from ..english import parse_english_with_metadata
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    parsed = parse_english_with_metadata(self.env, strict + "\n", vocabulary=self.overlay,
                                                         accept_suggested_vocabulary=True)
                if len(parsed.document.formulas) != 1:
                    raise AssistError("A node is exactly one statement")
                return parsed.document.formulas[0], "english"
            except AssistError:
                raise
            except VEError as exc:
                if surface == "english" or not errors:
                    raise
                raise errors[0] from exc
        raise AssistError(f"Unknown surface {surface!r}: use auto, strict or english")

    def paraphrase_formula(self, formula):
        """Display English only when its full parse recovers the requested AST."""
        from ..english import parse_english_with_metadata, render_english
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                wording = render_english(formula, self.env, vocabulary=self.overlay,
                                         accept_suggested_vocabulary=True) + "."
                parsed = parse_english_with_metadata(self.env, wording + "\n", vocabulary=self.overlay,
                                                     accept_suggested_vocabulary=True)
                if len(parsed.document.formulas) == 1 and parsed.document.formulas[0] == formula:
                    return wording
        except Exception:  # display only; never part of a verdict
            pass
        return self._canonical(formula)

    def _reject_vacuous(self, tid, formula):
        """A target valid on its own certifies nothing. Returns ``invalid`` (a real claim) or ``unknown``
        (the check ran out of budget: the target may be frozen but the item can never succeed)."""
        vacuity = self._validity(formula)
        if vacuity == "valid":
            raise AssistError(f"Target {tid} is provable from no premises (vacuous); freeze the sentence's "
                              "actual claim")
        return vacuity

    def _premise_key(self, formula):
        return self._canonical(formula)

    def _canonical_premises(self, premises):
        """THE premise canonicalization (sorted by canonical text, deduplicated): every prover or model
        search the session runs sees premises as a SET, never in node or parent order."""
        return tuple({self._premise_key(p): p for p in sorted(premises, key=self._premise_key)}.values())

    def _ordered_parents(self, node):
        """``node``'s parents in canonical order (by canonical formula text, then name). ``_check`` proves a
        step against exactly these premises and ``target_graph`` lists the deduction's premises in the same
        order, so the certificate, its replay and the verdict are independent of the author's parent order."""
        return tuple(sorted(node.parents, key=lambda p: (self._premise_key(self.nodes[p].formula), p)))

    def _decide(self, premises, conclusion):
        """Does ``premises`` entail ``conclusion``? ``yes`` / ``no`` / ``unknown``.

        The single interpretation point for every fidelity search. ``yes`` needs a Found proof;
        ``no`` needs a saturated open tableau (no closure) or a checked countermodel. Anything
        else -- an exhausted proof budget (ResourceLimit), a prover error, no countermodel within
        budget -- is ``unknown``, and every caller treats ``unknown`` as blocking success. So
        raising or lowering the proof budget can only turn ``unknown`` into a decision, never flip a
        decided answer, and never turn a failing item into a success.
        """
        # Canonical premise order (sorted, deduplicated): a verdict is a function of the premise SET,
        # never of node insertion order or parent order.
        premises = self._canonical_premises(premises)
        try:
            proof = prove_entailment(self.env, premises, conclusion,
                                     max_steps=self.options["max_proof_steps"])
        except (ValueError, VEError):
            proof = None
        if proof is not None and self._lean_replays(proof, premises, conclusion):
            return "yes"
        budget = self._budget()
        try:
            found, model = ground_countermodel(self.env, premises, conclusion)
            if found == "Unsupported":
                # A saturated open non-closure tableau already established a
                # negative search result without spending the model-search
                # budget. Materialise a witness for Lean even when that budget
                # is zero; only Lean's countermodel answer may become "no".
                witness_budget = (1_000_000 if proof is not None and proof.status == "NotFound"
                                  and not self.env.closure else budget["max_evaluations"])
                model = find_countermodel(self.env, premises, conclusion,
                                          max_domain_size=budget["max_domain_size"],
                                          max_models=budget["max_models"],
                                          max_evaluations=witness_budget).model
            if model is not None:
                saturated = proof is not None and proof.status == "NotFound" and not self.env.closure
                if saturated:
                    if self._lean_refutes(premises, conclusion, model):
                        return "no"
                else:
                    from ..backends.dispatch import pinned
                    with pinned("lean"):
                        checked = check_countermodel(
                            self.env, premises, conclusion, model,
                            max_evaluations=budget["max_evaluations"])
                    if checked.valid:
                        return "no"
        except (ValueError, VEError):
            pass
        return "unknown"

    def _lean_refutes(self, premises, conclusion, model):
        """Lean checks a proposed witness; search budgets never decide its truth."""
        from ..ast import _to_data
        from ..backends.lean_runner import cached_route_environment, lean_mode
        from ..backends.relay import decide
        case = {"id": "assist-countermodel", "kind": "countermodel",
                "environment": cached_route_environment(self.env),
                "premises": [_to_data(p) for p in premises], "conclusion": _to_data(conclusion),
                "model": model.to_dict()}
        return decide(lean_mode(self.env), [case])[0]["refutes"]

    def _lean_replays(self, proof, premises, conclusion):
        """A search result is evidence only after the Lean certificate checker accepts it."""
        if proof.status != "Found" or proof.certificate is None:
            return False
        from ..entailment import _check_certificate_lean
        try:
            return _check_certificate_lean(self.env, premises, conclusion, proof.certificate,
                                           self.options["max_proof_steps"]).valid
        except (ValueError, VEError):
            return False

    def _validity(self, formula):
        """``valid`` / ``invalid`` / ``unknown`` from no premises, conjunct by conjunct (fails closed)."""
        parts = []
        for part in _conjuncts(formula):
            verdict = self._decide((), part)
            if verdict == "no":
                return "invalid"
            parts.append("valid" if verdict == "yes" else "unknown")
        return "valid" if all(p == "valid" for p in parts) else "unknown"

    def _offered(self, formula):
        """The candidate or suggestion (kind, id) whose formula this is, if any: provenance is bound to
        content, so retyping an offered formula by hand cannot erase that the proposer supplied it."""
        for kind, pool in (("proposer", self.candidates), ("suggestion", self.suggestions)):
            for ref, row in pool.items():
                if row["formula"] == formula:
                    return kind, ref
        return None

    def _require_frozen(self):
        missing = [t for t, row in self.targets.items() if row["formula"] is None]
        if missing:
            raise AssistError("Freeze every target first (freeze_target): " + ", ".join(missing))

    def _anchors(self, anchors):
        anchors = _names(anchors, "anchors")
        for a in anchors:
            if a not in self.sentences:
                raise AssistError(f"Unknown sentence id {a!r}")
        return anchors

    def _descendants(self, name):
        found, pending = set(), [name]
        while pending:
            current = pending.pop()
            for other in self.nodes.values():
                if current in other.parents and other.name not in found:
                    found.add(other.name)
                    pending.append(other.name)
        return found

    def _invalidate(self, name):
        for affected in {name, *(n.name for n in self.nodes.values() if name in n.parents)}:
            self.checks.pop(affected, None)

    def _budget(self):
        return {k: self.options[k] for k in ("max_proof_steps", "max_domain_size", "max_models", "max_evaluations")}

    # ------------------------------------------------------------------ dispatch
    ACTIONS = ("freeze_target", "add_node", "accept", "rewrite", "remove_node", "declare", "check_step",
               "status", "waive", "show", "paraphrase", "sentences", "compare", "propose", "export",
               "record_usage")

    def apply(self, action, args=None, *, _recorded=None):
        """Run one action, log it, and return its JSON result (never raises VEError)."""
        if action not in self.ACTIONS:
            raise AssistError(f"Unknown action {action!r}")
        args = deepcopy(args or {})
        if type(args) is not dict:
            raise AssistError("Arguments must be an object")
        # Arguments are sanitized BEFORE they are acted on, so live and replayed runs see the same input.
        args = stream_audit.sanitize(args, self.SECRET_NEEDLES)
        handler = getattr(self, "_do_" + action)
        event = {"seq": len(self.events), "action": action, "args": args, "time": _now()}
        self._seq = event["seq"]
        self._model_calls = []
        recorded_calls = _recorded.get("model_calls", []) if _recorded else []
        if type(recorded_calls) is not list:
            raise LedgerReplayError("Recorded model_calls must be a list")
        self._replaying = list(recorded_calls) if _recorded is not None else None
        self._leftover_calls = 0
        try:
            try:
                inspect.signature(handler).bind(**args)
            except TypeError as exc:
                raise AssistError(f"Invalid arguments for {action}: {exc}") from exc
            result = {"ok": True, **handler(**args)}
        except LedgerReplayError:
            raise
        except (VEError, CheckerUnavailable) as exc:
            result = {"ok": False, "error": exc.to_dict()}
        except RuntimeError as exc:  # a backend failure must still be logged, never lost
            from .proposer import redact_secrets
            result = {"ok": False, "error": {"code": "BackendError", "message": redact_secrets(str(exc))[:500]}}
        finally:
            self._leftover_calls = len(self._replaying) if self._replaying is not None else 0
            self._replaying = None
        if self._model_calls:
            event["model_calls"] = self._model_calls
            # Earlier failed attempts of the same backend call (retries) spent tokens too.
            spent = lambda c, k: (c.get(k) or 0) + sum(a.get(k) or 0 for a in c.get("attempts", ()))
            event["tokens"] = {"proposer": {
                "input_tokens": sum(spent(c, "input_tokens") for c in self._model_calls),
                "output_tokens": sum(spent(c, "output_tokens") for c in self._model_calls),
                "calls": len(self._model_calls)}}
        if action == "record_usage" and result["ok"]:
            event["tokens"] = {args["role"]: {"input_tokens": args.get("input_tokens", 0),
                                              "output_tokens": args.get("output_tokens", 0), "calls": 1}}
        # Every string of every logged event and returned result passes through the canonical sanitizer.
        result = stream_audit.sanitize(result, self.SECRET_NEEDLES)
        event = stream_audit.sanitize(event, self.SECRET_NEEDLES)
        event["result"] = result
        event["result_chars"] = len(json.dumps(result, ensure_ascii=False))
        self.events.append(event)
        return result

    def _invariant(self, text):
        """Closure-induction invariant written as 'for every SORT v, (F)'; F with v free is used."""
        formula, _ = self._parse(text, "strict")
        if type(formula) is not ast.Forall:
            raise AssistError("Write an invariant as 'for every SORT v, (F)', where F mentions v")
        return formula.body

    def _check(self, node, invariants=()):
        # Same canonicalization as _decide: parent ORDER never changes what the prover sees.
        premises = tuple(self.nodes[p].formula for p in self._ordered_parents(node))
        budget = self._budget()
        record = {"status": "unknown", "parents": list(node.parents)}
        if invariants:
            record["invariants"] = list(invariants)
        inv = tuple(self._invariant(i) for i in invariants)
        try:
            proof = prove_entailment(self.env, premises, node.formula, max_steps=budget["max_proof_steps"],
                                     invariants=inv)
        except (ValueError, VEError) as exc:
            record["prover"] = {"status": "error", "detail": str(exc)}
            proof = None
        if proof is not None:
            record["prover"] = {"status": proof.status, "steps": proof.steps}
        if proof is not None and proof.status == "Found":
            replay = check_entailment_certificate(self.env, premises, node.formula, proof.certificate,
                                                  max_steps=budget["max_proof_steps"])
            if replay.valid:
                record.update(status="follows", certificate=proof.certificate,
                              certificate_digest=_sha(proof.certificate), replay_steps=replay.steps)
                # Informational only: status decides consistency of every support fail-closed.
                if self._entails(premises, ast.Bottom()):
                    record["contradictory_parents"] = True
                return record
            record["prover"]["replay"] = replay.status
        status, model = ground_countermodel(self.env, premises, node.formula)
        search = "ground"
        if status == "Unsupported":
            search = "bounded"
            result = find_countermodel(self.env, premises, node.formula,
                                       max_domain_size=budget["max_domain_size"],
                                       max_models=budget["max_models"],
                                       max_evaluations=budget["max_evaluations"])
            status, model = result.status, result.model
        record["countermodel_search"] = {"method": search, "status": status}
        if model is not None:
            checked = check_countermodel(self.env, premises, node.formula, model,
                                         max_evaluations=budget["max_evaluations"])
            if checked.valid:
                record.update(status="countermodel", model=model.to_dict(), model_id=model.model_id,
                              explanation={**self.describe_model(model, (*premises, node.formula)),
                                           "reading": "Every parent is true in this model and the "
                                                      "step's conclusion is false."})
        return record

    def _entails(self, premises, conclusion):
        """Positive-only proof search (True only on a Found proof). Used for suggestions and
        comparisons; never interpret False as "not entailed" in a check success depends on: use
        ``_decide``, which reports an exhausted search as ``unknown``."""
        try:
            premises = self._canonical_premises(premises)
            proof = prove_entailment(self.env, premises, conclusion,
                                     max_steps=self.options["max_proof_steps"])
            return self._lean_replays(proof, premises, conclusion)
        except (ValueError, VEError):
            return False
