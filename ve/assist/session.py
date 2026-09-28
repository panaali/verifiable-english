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
import dataclasses
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import inspect
import json
import secrets
import warnings

from .. import ast, stream_audit
from ..argument import ArgumentGraph, Claim, Deduction, check_argument, deduction_identity
from ..entailment import check_entailment_certificate, prove_entailment
from ..environment import RESERVED, Environment, valid_identifier
from ..errors import CheckerUnavailable, VEError
from ..parser import parse
from ..printer import print_formula
from ..search import check_countermodel, find_countermodel
from .ground import ground_countermodel
from .sources import load_source

SESSION_FORMAT = "ve.assist-session@1"
TOOL_VERSION = "ve-assist@1"
ORIGINS = ("hand-written", "proposer-verbatim", "proposer-edited", "suggestion-verbatim", "suggestion-edited")
DEFAULT_OPTIONS = {"premise_suggestions": False, "max_proof_steps": 10_000, "max_domain_size": 2,
                   "max_models": 2_000, "max_evaluations": 100_000, "proposer_k": 3,
                   "propose_repair_rounds": 1}


class AssistError(VEError):
    code = "AssistError"


class LedgerReplayError(VEError):
    code = "LedgerReplayError"


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def config_digest(config):
    """Digest of a session configuration (everything except the creation time and the digest itself)."""
    return _sha({k: v for k, v in config.items() if k not in ("created", "config_digest")})


def _ident(name, label="name"):
    if not valid_identifier(name) or name in RESERVED:
        raise AssistError(f"Invalid {label} {name!r}: use [a-z][a-z0-9_]*, not a reserved word")
    return name


def _names(value, label):
    if value is None:
        return ()
    if isinstance(value, str):
        value = [value]
    if type(value) not in (list, tuple) or any(type(v) is not str for v in value):
        raise AssistError(f"{label} must be a list of strings")
    if len(set(value)) != len(value):
        raise AssistError(f"Duplicate entry in {label}")
    return tuple(value)


def _predicates_of(formula, found=None):
    found = set() if found is None else found
    pending = [formula]
    while pending:
        node = pending.pop()
        if type(node) in (ast.Unary, ast.Binary):
            found.add(node.predicate)
        if type(node) is ast.Reach:
            if type(node.edge) is ast.Named:
                found.add(node.edge.relation)
            else:
                pending.append(node.edge.formula)
        for key in ("body", "left", "right"):
            child = getattr(node, key, None)
            if child is not None and not isinstance(child, (ast.Var, ast.Const)):
                pending.append(child)
    return found


def _symbols_of(formula):
    """Every vocabulary symbol a formula uses: predicates, relations, constants and quantified sorts."""
    found, pending = set(), [formula]
    while pending:
        node = pending.pop()
        if type(node) is ast.Const:
            found.add(node.name)
            continue
        for item in dataclasses.fields(node):
            value = getattr(node, item.name)
            if item.name in ("predicate", "relation", "sort") and type(value) is str:
                found.add(value)
            elif dataclasses.is_dataclass(value):
                pending.append(value)
    return found


def _conjuncts(formula):
    if type(formula) is ast.And:
        return _conjuncts(formula.left) + _conjuncts(formula.right)
    return [formula]


def _constants_of(formula, found=None):
    found = set() if found is None else found
    pending = [formula]
    while pending:
        node = pending.pop()
        for key in ("term", "left", "right", "body", "edge", "formula"):
            child = getattr(node, key, None)
            if type(child) is ast.Const:
                found.add(child.name)
            elif child is not None and not isinstance(child, (ast.Var, str)):
                pending.append(child)
    return found


@dataclass
class Node:
    name: str
    formula: ast.Formula
    text: str
    anchors: tuple[str, ...]
    parents: tuple[str, ...]
    origin: str
    source_ref: str | None = None  # candidate or suggestion id
    history: list = field(default_factory=list)

    @property
    def kind(self):
        return "step" if self.parents else "assumption"


class AssistSession:
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

    def _sentence_view(self, sid):
        s = self.sentences[sid]
        return {"id": sid, "role": s["role"], "text": s["text"]}

    def node_view(self, name):
        node = self.nodes[name]
        check = self.checks.get(name)
        view = {"name": name, "kind": node.kind, "text": node.text,
                "paraphrase": self.paraphrase_formula(node.formula),
                "anchors": [self._sentence_view(a) for a in node.anchors],
                "parents": list(node.parents), "origin": node.origin}
        if node.source_ref:
            view["source_ref"] = node.source_ref
        if node.kind == "step":
            view["check"] = check["status"] if check else "unchecked"
        matches = [t for t, row in self.targets.items() if row["formula"] == node.formula]
        if matches:
            view["matches_targets"] = matches
        return view

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
        if type(conclusion) is ast.Top:
            return "yes"
        try:
            status = prove_entailment(self.env, premises, conclusion,
                                      max_steps=self.options["max_proof_steps"]).status
        except (ValueError, VEError):
            status = "ResourceLimit"
        if status == "Found":
            return "yes"
        if status == "NotFound" and not self.env.closure:
            return "no"
        budget = self._budget()
        try:
            found, model = ground_countermodel(self.env, premises, conclusion)
            if found == "Unsupported":
                model = find_countermodel(self.env, premises, conclusion,
                                          max_domain_size=budget["max_domain_size"],
                                          max_models=budget["max_models"],
                                          max_evaluations=budget["max_evaluations"]).model
            if model is not None and check_countermodel(self.env, premises, conclusion, model,
                                                        max_evaluations=budget["max_evaluations"]).valid:
                return "no"
        except (ValueError, VEError):
            pass
        return "unknown"

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

    # ------------------------------------------------------------------ actions
    def _do_freeze_target(self, target, text=None, surface="auto", candidate=None):
        """Commit the formal target for a target sentence. Irreversible."""
        if candidate is not None:
            if candidate not in self.candidates:
                raise AssistError(f"Unknown candidate {candidate!r}")
            if text is None:
                text = self._canonical(self.candidates[candidate]["formula"])
        if text is None:
            raise AssistError("freeze_target needs text or a candidate")
        if target not in self.targets:
            raise AssistError(f"Unknown target {target!r}")
        row = self.targets[target]
        if row["formula"] is not None:
            raise AssistError(f"Target {target} is already frozen and cannot change")
        if self.nodes:
            raise AssistError("Targets must be frozen before any node is added")
        formula, used = self._parse(text, surface)
        vacuity = self._reject_vacuous(target, formula)
        origin = "hand-written"
        if candidate is not None:
            origin = "proposer-verbatim" if formula == self.candidates[candidate]["formula"] else "proposer-edited"
        elif self._offered(formula):
            origin = self._offered(formula)[0] + "-verbatim"
        row.update(formula=formula, text=self._canonical(formula), frozen_by="author", origin=origin,
                   vacuity=vacuity)
        result = {"target": target, "sentence": self._sentence_view(row["sentence"]), "text": row["text"],
                  "paraphrase": self.paraphrase_formula(formula), "surface": used, "origin": origin}
        if vacuity == "unknown":
            result["warning"] = ("Could not decide within budget whether this target is provable from no "
                                 "premises; the item cannot succeed (fail closed).")
        return result

    def _do_add_node(self, name, text=None, anchors=(), parents=(), candidate=None, suggestion=None,
                     surface="auto"):
        self._require_frozen()
        _ident(name, "node name")
        if name in self.nodes:
            raise AssistError(f"Node {name} already exists; use rewrite")
        anchors, parents = self._anchors(anchors), _names(parents, "parents")
        for p in parents:
            if p not in self.nodes:
                raise AssistError(f"Unknown parent node {p!r}")
        if candidate and suggestion:
            raise AssistError("Give at most one of candidate and suggestion")
        ref = candidate or suggestion
        if ref:
            pool = self.candidates if candidate else self.suggestions
            if ref not in pool:
                raise AssistError(f"Unknown {'candidate' if candidate else 'suggestion'} {ref!r}")
            offered = pool[ref]["formula"]
            formula = offered if text is None else self._parse(text, surface)[0]
            kind = "proposer" if candidate else "suggestion"
            origin = f"{kind}-verbatim" if formula == offered else f"{kind}-edited"
        else:
            if text is None:
                raise AssistError("add_node needs text, a candidate, or a suggestion")
            formula, _ = self._parse(text, surface)
            origin = "hand-written"
            offered = self._offered(formula)
            if offered:
                origin, ref = offered[0] + "-verbatim", offered[1]
        self.nodes[name] = Node(name, formula, self._canonical(formula), anchors, parents, origin, ref)
        return {"node": self.node_view(name)}

    def _do_accept(self, candidate, name, anchors=(), parents=()):
        """Accept a proposer candidate verbatim (alias of add_node with candidate)."""
        return self._do_add_node(name, anchors=anchors, parents=parents, candidate=candidate)

    def _do_rewrite(self, name, text=None, anchors=None, parents=None, surface="auto"):
        if name not in self.nodes:
            raise AssistError(f"Unknown node {name!r}")
        node = self.nodes[name]
        formula = node.formula if text is None else self._parse(text, surface)[0]
        new_anchors = node.anchors if anchors is None else self._anchors(anchors)
        new_parents = node.parents if parents is None else _names(parents, "parents")
        if parents is not None:
            below = self._descendants(name) | {name}
            for p in new_parents:
                if p not in self.nodes:
                    raise AssistError(f"Unknown parent node {p!r}")
                if p in below:
                    raise AssistError(f"Parent {p} would create a cycle")
        if (formula, new_anchors, new_parents) == (node.formula, node.anchors, node.parents):
            raise AssistError("Rewrite changes nothing")
        node.history.append({"text": node.text, "anchors": list(node.anchors), "parents": list(node.parents),
                             "origin": node.origin})
        if formula != node.formula:
            offered = self._offered(formula)
            if offered:
                node.origin, node.source_ref = offered[0] + "-verbatim", offered[1]
            elif node.origin.endswith("-verbatim"):
                node.origin = node.origin.replace("-verbatim", "-edited")
        node.formula, node.text, node.anchors, node.parents = formula, self._canonical(formula), new_anchors, new_parents
        self._invalidate(name)
        return {"node": self.node_view(name), "invalidated_checks": sorted(
            {name, *(n.name for n in self.nodes.values() if name in n.parents)})}

    def _do_remove_node(self, name):
        if name not in self.nodes:
            raise AssistError(f"Unknown node {name!r}")
        children = sorted(n.name for n in self.nodes.values() if name in n.parents)
        if children:
            raise AssistError(f"Node {name} is a parent of {', '.join(children)}; rewrite those first")
        del self.nodes[name]
        self.checks.pop(name, None)
        return {"removed": name}

    def _do_declare(self, name, gloss, kind="predicate", arguments=(), sort=None, verbalisation=None,
                    acknowledge=()):
        """Add vocabulary through the ``ve propose``-style gates. Gloss required."""
        from ..english import EnglishVocabulary
        from ..english_phrases import BLOCKED, content_tokens, nearest
        # Targets are frozen in the original vocabulary, never in newly invented words.
        self._require_frozen()
        _ident(name, "symbol")
        if kind not in ("predicate", "constant", "sort"):
            raise AssistError("kind must be predicate, constant or sort")
        taken = {*self.env.sorts, *self.env.predicates, *self.env.constants}
        if name in taken:
            raise AssistError(f"Symbol {name} is already declared")
        if type(gloss) is not str or len(gloss.strip()) < 3 or gloss.strip().lower() == name.replace("_", " "):
            raise AssistError("A gloss is required: say in words what the symbol means (not just its name)")
        acknowledge = set(_names(acknowledge, "acknowledge"))
        data = self.env.to_dict()
        if kind == "predicate":
            arguments = _names(arguments, "arguments")
            if len(arguments) not in (1, 2) or any(a not in self.env.sorts for a in arguments):
                raise AssistError("A predicate needs one or two declared argument sorts")
            data["vocabulary"]["predicates"][name] = {"arguments": list(arguments), "description": gloss.strip()}
        elif kind == "constant":
            if sort not in self.env.sorts:
                raise AssistError("A constant needs a declared sort")
            data["vocabulary"]["constants"][name] = {"sort": sort, "description": gloss.strip()}
        else:
            data["vocabulary"]["sorts"][name] = {"description": gloss.strip()}
        flags = []
        # Gate 1 (as in ve propose): near-duplicates of existing wording need acknowledgement.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            words = EnglishVocabulary(self.env, vocabulary=self.overlay, accept_suggested_vocabulary=True)
        phrase = (verbalisation or "").replace("{0}", "").replace("{1}", "").strip() or name.replace("_", " ")
        for row in nearest(phrase, words):
            if row["near_duplicate"]:
                flags.append({"flag": row["symbol"], "reason": "near-duplicate of existing " + row["kind"],
                              "detail": {k: row[k] for k in ("wording", "edit_distance", "shared_stem",
                                                             "content_overlap")}})
        if kind == "predicate" and set(content_tokens(phrase)) & BLOCKED:
            raise AssistError("Wording contains blocked relational or negative content; declare a neutral name")
        # Gate 2: the new symbol must not be a target conclusion under another name.
        for tid, row in self.targets.items():
            target_words = content_tokens(self.sentences[row["sentence"]]["text"])
            target_words -= {c.lower() for c in self.env.constants}
            symbol_words = content_tokens(gloss + " " + name.replace("_", " ") + " " + phrase)
            symbol_words -= {c.lower() for c in self.env.constants}
            if target_words and symbol_words and (target_words <= symbol_words or symbol_words <= target_words):
                flags.append({"flag": "conclusion:" + tid, "reason": "gloss/name restates target sentence " + tid,
                              "detail": {"target_sentence": self.sentences[row["sentence"]]["text"]}})
        missing = sorted({f["flag"] for f in flags} - acknowledge)
        if missing:
            raise AssistError("Declaration blocked; acknowledge each flag if intended: " + ", ".join(missing)
                              + ". Flags: " + json.dumps(flags, ensure_ascii=False))
        stray = acknowledge - {f["flag"] for f in flags}
        if stray:
            raise AssistError("Acknowledgement names no raised flag: " + ", ".join(sorted(stray)))
        new_env = Environment(data)
        overlay = deepcopy(self.overlay)
        if overlay is not None or verbalisation:
            overlay = overlay or {"format": "ve.english-vocabulary@1", "sorts": {}, "predicates": {}}
            overlay["environment_id"] = new_env.environment_id
            if verbalisation and kind == "predicate":
                overlay["predicates"][name] = {"verbalisation": verbalisation, "suggested": True}
            if verbalisation and kind == "sort":
                raise AssistError("Sort wording is not supported here; use the sort name")
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                try:
                    EnglishVocabulary(new_env, vocabulary=overlay, accept_suggested_vocabulary=True)
                except VEError as exc:
                    raise AssistError("Verbalisation fails the English template linter: " + exc.message) from exc
        self.env, self.overlay = new_env, overlay
        self.declared[name] = {"kind": kind, "gloss": gloss.strip(), "acknowledged": sorted(acknowledge)}
        # Certificates and models bind the environment identity: recheck silently.
        rechecked = sorted(self.checks)
        for step in rechecked:
            self.checks[step] = self._check(self.nodes[step], self.checks[step].get("invariants") or ())
        return {"declared": name, "kind": kind, "gloss": gloss.strip(), "acknowledged": sorted(acknowledge),
                "environment_id": self.env.environment_id, "rechecked": rechecked}

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

    def describe_model(self, model, formulas):
        """Readable model: named entities, true atoms, and the false atoms the formulas mention."""
        from .ground import _atoms
        used, mentioned = set(), {}
        for f in formulas:
            _predicates_of(f, used)
            _atoms(f, mentioned)  # ground atoms (constants only); stops at binders
        names = {}
        for const, entity in model.constants.items():
            names.setdefault(entity, []).append(const)
        label = lambda e: " = ".join(sorted(names[e])) if e in names else e
        spell = lambda p, args: (f"{label(args[0])} is {p}" if len(args) == 1
                                 else f"{label(args[0])} {p} {label(args[1])}")
        true_atoms = [spell(p, row) for p in sorted(used) if p in self.env.predicates
                      for row in sorted(model.relations[p])]
        false_atoms = []
        for (p, consts) in mentioned:
            row = tuple(model.constants[c] for c in consts)
            text = spell(p, row)
            if row not in model.relations[p] and text not in false_atoms:
                false_atoms.append(text)
        return {"entities": {sort: [label(e) for e in model.domains[sort]] for sort in sorted(model.domains)},
                "true": true_atoms, "false": sorted(false_atoms)}

    def _do_check_step(self, name, invariants=(), suggest_premises=False):
        """Does node ``name`` follow from its parents? follows / countermodel / unknown."""
        if name not in self.nodes:
            raise AssistError(f"Unknown node {name!r}")
        node = self.nodes[name]
        if node.kind != "step":
            raise AssistError(f"{name} is an assumption (no parents); only steps are checked")
        if suggest_premises and not self.options["premise_suggestions"]:
            raise AssistError("Premise suggestions are disabled in this session (option premise_suggestions)")
        record = self._check(node, tuple(_names(invariants, "invariants")))
        self.checks[name] = record
        result = {"node": name, "status": record["status"], "parents": list(node.parents),
                  "conclusion": node.text, "conclusion_paraphrase": self.paraphrase_formula(node.formula)}
        if record["status"] == "follows":
            result["certificate_digest"] = record["certificate_digest"]
            if record.get("contradictory_parents"):
                result["warning"] = "The parents are jointly contradictory; the step follows vacuously."
        elif record["status"] == "countermodel":
            result["countermodel"] = record["explanation"]
            result["model_id"] = record["model_id"]
        else:
            result["detail"] = "No certificate and no countermodel within budget (not a refutation)."
        if suggest_premises and record["status"] != "follows":
            result["premise_suggestions"] = self._suggest_premises(node)
        return result

    def _suggest_premises(self, node):
        """Off by default. Suggestions can assume the gap away: each is labelled."""
        from .premises import suggest_premises
        rows = suggest_premises(self, node)
        out = []
        for row in rows:
            sid = f"s{len(self.suggestions) + 1}"
            self.suggestions[sid] = {"formula": row["formula"], "for": node.name, "kind": row["kind"]}
            view = {k: v for k, v in row.items() if k != "formula"}
            out.append({"id": sid, **view, "text": self._canonical(row["formula"]),
                        "paraphrase": self.paraphrase_formula(row["formula"])})
        return out

    def _do_waive(self, sentence, reason):
        if sentence not in self.sentences:
            raise AssistError(f"Unknown sentence id {sentence!r}")
        if type(reason) is not str or len(reason.strip()) < 3:
            raise AssistError("A waiver needs a reason")
        if any(row["sentence"] == sentence for row in self.targets.values()):
            raise AssistError("A target sentence cannot be waived")
        self.waivers[sentence] = reason.strip()
        return {"waived": sentence, "reason": reason.strip()}

    def _do_show(self, name=None):
        if name is not None:
            if name not in self.nodes:
                raise AssistError(f"Unknown node {name!r}")
            view = self.node_view(name)
            view["history"] = self.nodes[name].history
            check = self.checks.get(name)
            if check and check["status"] == "countermodel":
                view["countermodel"] = check["explanation"]
            return {"node": view}
        return {"targets": [self._target_view(t) for t in self.targets],
                "nodes": [self.node_view(n) for n in self.nodes]}

    def _target_view(self, tid):
        row = self.targets[tid]
        view = {"id": tid, "sentence": self._sentence_view(row["sentence"]), "frozen": row["formula"] is not None}
        if row["formula"] is not None:
            view.update(text=row["text"], paraphrase=self.paraphrase_formula(row["formula"]),
                        vacuity=row.get("vacuity", "invalid"))
        return view

    def _do_paraphrase(self, text, surface="auto"):
        formula, used = self._parse(text, surface)
        return {"text": self._canonical(formula), "paraphrase": self.paraphrase_formula(formula), "surface": used}

    def _do_sentences(self):
        return {"sentences": [self._sentence_view(s) | {"asserting": self.sentences[s]["asserting"]}
                              for s in self.sentence_order],
                "targets": [self._target_view(t) for t in self.targets],
                "vocabulary": self.vocabulary()}

    def vocabulary(self):
        return {"sorts": {k: v.description for k, v in self.env.sorts.items()},
                "predicates": {k: {"arguments": list(v.arguments), "gloss": v.description}
                               for k, v in self.env.predicates.items()},
                "constants": {k: v.sort for k, v in self.env.constants.items()}}

    def _resolve(self, ref):
        if ref in self.nodes:
            return self.nodes[ref].formula
        if ref in self.candidates:
            return self.candidates[ref]["formula"]
        if ref in self.targets and self.targets[ref]["formula"] is not None:
            return self.targets[ref]["formula"]
        return self._parse(ref, "auto")[0]

    def _do_compare(self, a, b):
        """Compare two formulas (node names, candidate ids, target ids or VE text)."""
        from .proposer import compare_formulas
        return compare_formulas(self, self._resolve(a), self._resolve(b))

    def _do_propose(self, sentence, k=None, note=None):
        from .proposer import run_propose
        return run_propose(self, sentence, k=k, note=note)

    def _do_record_usage(self, role, input_tokens=0, output_tokens=0, note=None):
        if role not in ("author", "proposer", "auditor"):
            raise AssistError("role must be author, proposer or auditor")
        if any(type(v) is not int or v < 0 for v in (input_tokens, output_tokens)):
            raise AssistError("Token counts must be nonnegative integers")
        return {"recorded": role}

    # ------------------------------------------------------------------ status
    def _support(self, root):
        found, pending = [], [root]
        while pending:
            name = pending.pop()
            if name in found:
                continue
            found.append(name)
            pending.extend(self.nodes[name].parents)
        return found

    def _anchor_state(self, node):
        """``anchored`` only when every anchor is given: an anchor to any claimed sentence means the
        assumption states (part of) a conclusion, which must be derived, not assumed."""
        roles = {self.sentences[a]["role"] for a in node.anchors}
        if "claimed" in roles:
            return "anchored_to_claim_only"
        if "given" in roles:
            return "anchored"
        return "unanchored"

    def _is_anchored_parent(self, name):
        node = self.nodes[name]
        return node.kind == "step" or self._anchor_state(node) == "anchored"

    def target_graph(self, tid):
        """Build the checked ArgumentGraph for one target, or (None, reason)."""
        row = self.targets[tid]
        if row["formula"] is None:
            return None, "target not frozen", None
        matches = [n for n in self.nodes.values() if n.formula == row["formula"] and n.kind == "step"]
        if not matches:
            return None, "no step node states the frozen target", None
        certified = [n for n in matches if self.checks.get(n.name, {}).get("status") == "follows"]
        # Deterministic in the graph (by name), never by insertion order; every other matching step is
        # still evaluated by status as a witness.
        root = min(certified or matches, key=lambda n: n.name)
        support = self._support(root.name)
        claims = tuple(Claim.create(self.env, n, print_formula(self.env, self.nodes[n].formula) + ".\n")
                       for n in support)
        steps = [n for n in support if self.nodes[n].kind == "step"]
        # Deduction premises in the canonical parent order _check proved them in.
        parents = {n: self._ordered_parents(self.nodes[n]) for n in steps}
        bare = ArgumentGraph(self.env, claims, tuple(Deduction("d_" + n, parents[n], n) for n in steps),
                             root.name, target_scope="assist:" + tid)
        deductions = []
        for n in steps:
            plain = Deduction("d_" + n, parents[n], n)
            check = self.checks.get(n)
            certs = ()
            if check and check["status"] == "follows":
                certs = ({"edge_id": deduction_identity(bare, plain), "direction": "follows",
                          "proof": check["certificate"]},)
            deductions.append(Deduction("d_" + n, parents[n], n, certs))
        graph = ArgumentGraph(self.env, claims, tuple(deductions), root.name, target_scope="assist:" + tid)
        return graph, None, root.name

    def _entails(self, premises, conclusion):
        """Positive-only proof search (True only on a Found proof). Used for suggestions and
        comparisons; never interpret False as "not entailed" in a check success depends on: use
        ``_decide``, which reports an exhausted search as ``unknown``."""
        try:
            return prove_entailment(self.env, self._canonical_premises(premises), conclusion,
                                    max_steps=self.options["max_proof_steps"]).status == "Found"
        except (ValueError, VEError):
            return False

    def _do_status(self):
        failures = []
        targets, support_all = [], set()
        for tid in self.targets:
            view = self._target_view(tid)
            graph, reason, root = self.target_graph(tid) if view["frozen"] else (None, "target not frozen", None)
            if graph is None:
                view.update(certified=False, reason=reason)
                failures.append(f"target {tid}: {reason}")
            else:
                result = check_argument(graph, search=False)
                support = self._support(root)
                support_all.update(support)
                view.update(node=root, replay=result.status, certified=result.status == "Checked",
                            support=support, assumptions=list(result.remaining_assumptions))
                if result.status != "Checked":
                    failures.append(f"target {tid}: graph replay status {result.status}")
                failures += self._consistency_failures(f"target {tid}", result.remaining_assumptions, view)
                # Vacuity through the graph: tautological assumptions add nothing, so a target they
                # entail on their own is vacuous even when the direct empty-premise check ran out of budget.
                # An assumption whose validity is undecided counts as possibly tautological (fail closed).
                verdicts = {n: self._validity(self.nodes[n].formula) for n in sorted(result.remaining_assumptions)}
                trivial = [n for n, v in verdicts.items() if v != "invalid"]
                if trivial:
                    verdict = self._decide([self.nodes[n].formula for n in trivial], self.targets[tid]["formula"])
                    undecided = [n for n in trivial if verdicts[n] == "unknown"]
                    if verdict == "yes" and not undecided:
                        view["vacuous"] = True
                        failures.append(f"target {tid}: provable from tautological assumptions only "
                                        f"({', '.join(trivial)})")
                    elif verdict != "no":
                        view["vacuous"] = "unknown"
                        failures.append(f"target {tid}: vacuity through assumptions undecided within budget "
                                        f"({', '.join(trivial)} may be tautologies that entail it; fail closed)")
            if view["frozen"] and view.get("vacuity") == "unknown":
                failures.append(f"target {tid}: vacuity unknown (the empty-premise check exhausted its budget; "
                                "fail closed)")
            targets.append(view)
        steps = [n for n in self.nodes.values() if n.kind == "step"]
        # Outcome is a FUNCTION OF THE GRAPH: every certified step that states a frozen target or is anchored
        # to a claimed sentence is a WITNESS, and ALL witnesses are evaluated (never "the first found"), in
        # name order. Each witness joins the load-bearing analysis, has its assumptions checked for
        # consistency, and must be entailed by its ANCHORED assumptions alone (decided by ``_decide``): a
        # witness that needs an unanchored assumption blocks success whatever other witnesses exist.
        witnesses = self._witnesses()
        dependence = {}
        for w in witnesses:
            support = self._support(w)
            support_all.update(support)
            leaves = [n for n in support if self.nodes[n].kind == "assumption"]
            failures += self._consistency_failures(f"step {w}", leaves)
            verdict, loose = self._anchored_entailment(w)
            dependence[w] = {"verdict": verdict, "unanchored_assumptions": loose}
            if verdict == "no":
                failures.append(f"step {w}: its anchored assumptions alone do not entail it (it needs "
                                f"unanchored {', '.join(loose)})")
            elif verdict == "unknown":
                failures.append(f"step {w}: undecided within budget whether its anchored assumptions alone "
                                f"entail it (unanchored {', '.join(loose) or 'none'}; fail closed)")
        # A claimed sentence is DERIVED when some witness anchored to it is independent of unanchored
        # assumptions (decided) and no single assumption in its support already states it (decided "no").
        # Covering it with an idle node, restating it, or waiving it never counts.
        derived, derivation_unknown = {}, {}
        for sid in self.sentence_order:
            if self.sentences[sid]["role"] == "claimed" and self.sentences[sid]["asserting"]:
                by, undecided = self._derivation(sid, dependence)
                if by:
                    derived[sid] = by
                elif undecided:
                    derivation_unknown[sid] = undecided
        unproved = [{"node": n.name, "check": self.checks.get(n.name, {}).get("status", "unchecked"),
                     "parents": list(n.parents)} for n in steps
                    if self.checks.get(n.name, {}).get("status") != "follows"]
        if unproved:
            failures.append(f"{len(unproved)} unproved step(s)")
        # Load-bearing: a certified step whose anchored parents ALONE (every unanchored parent removed at
        # once, so duplicates cannot hide each other) no longer entail it needs its unanchored parents.
        needs, undecided_needs = {}, {}
        for s in steps:
            if s.name not in support_all or self.checks.get(s.name, {}).get("status") != "follows":
                continue
            loose = [p for p in s.parents if not self._is_anchored_parent(p)]
            if not loose:
                continue
            anchored = [self.nodes[p].formula for p in s.parents if self._is_anchored_parent(p)]
            verdict = self._decide(anchored, s.formula)
            if verdict != "yes":  # "unknown" counts as needed (fail closed)
                for p in loose:
                    needs.setdefault(p, []).append(s.name)
                    undecided_needs.setdefault(p, []).extend([s.name] if verdict == "unknown" else [])
        unanchored = []
        for n in self.nodes.values():
            if n.kind != "assumption" or self._anchor_state(n) == "anchored":
                continue
            needed_by = needs.get(n.name, [])
            row = {"node": n.name, "anchor_state": self._anchor_state(n), "text": n.text,
                   "paraphrase": self.paraphrase_formula(n.formula),
                   "supports_target": n.name in support_all, "load_bearing": bool(needed_by),
                   "needed_by": needed_by}
            if undecided_needs.get(n.name):
                row["load_bearing_undecided_for"] = undecided_needs[n.name]
            unanchored.append(row)
            if needed_by:
                failures.append(f"load-bearing unanchored assumption {n.name}"
                                + (" (undecided within budget; fail closed)"
                                   if set(needed_by) <= set(undecided_needs.get(n.name, ())) else ""))
        coverage, uncovered, underived, waived = [], [], [], []
        for sid in self.sentence_order:
            s = self.sentences[sid]
            if not s["asserting"]:
                continue
            by = [n.name for n in self.nodes.values() if sid in n.anchors]
            if s["role"] == "claimed":
                state = "derived" if sid in derived else "underived"
            else:
                state = "covered" if by else "uncovered"
            # Waiving ANY asserting sentence blocks success, even one that is already covered or derived.
            state = "waived" if sid in self.waivers else state
            coverage.append({"sentence": sid, "role": s["role"], "state": state, "nodes": by,
                             **({"derived_by": derived[sid]} if sid in derived else {}),
                             **({"derivation_undecided": derivation_unknown[sid]}
                                if sid in derivation_unknown else {}),
                             **({"waiver": self.waivers[sid]} if state == "waived" else {})})
            {"uncovered": uncovered, "underived": underived, "waived": waived}.get(state, []).append(sid)
        if uncovered:
            failures.append(f"{len(uncovered)} given sentence(s) not covered by any node: {', '.join(uncovered)}")
        if underived:
            failures.append(f"{len(underived)} claimed sentence(s) not derived by a certified step: "
                            f"{', '.join(underived)}")
        for sid, rows in derivation_unknown.items():
            if sid in underived:
                failures.append(f"claimed sentence {sid}: undecided within budget whether it is derived "
                                f"({'; '.join(rows)}; fail closed)")
        if waived:
            failures.append(f"{len(waived)} asserting sentence(s) waived (a waiver is reported, never success): "
                            f"{', '.join(waived)}")
        waivers = [{"sentence": sid, "role": self.sentences[sid]["role"],
                    "asserting": self.sentences[sid]["asserting"], "reason": reason,
                    "counts_against_success": sid in waived}
                   for sid, reason in self.waivers.items()]
        for tid, row in self.targets.items():
            if row["formula"] is None:
                continue
            for n in self.nodes.values():
                if n.kind != "assumption":
                    continue
                verdict = self._decide([n.formula], row["formula"])
                if verdict == "yes":
                    failures.append(f"assumption {n.name} alone entails target {tid}")
                elif verdict == "unknown":
                    failures.append(f"assumption {n.name}: undecided within budget whether it alone entails "
                                    f"target {tid} (fail closed)")
        renamed = self._renamed_conclusions()
        failures += [f"declared vocabulary carries target {r['target']} ({', '.join(r['assumptions'])})"
                     if not r.get("undecided") else
                     f"declared vocabulary may carry target {r['target']} ({', '.join(r['assumptions'])}): "
                     "undecided within budget (fail closed)"
                     for r in renamed]
        origins = {o: sum(1 for n in self.nodes.values() if n.origin == o) for o in ORIGINS}
        return {"success": not failures, "failures": failures, "targets": targets,
                "unproved_steps": unproved, "unanchored_assumptions": unanchored,
                "coverage": {"covered": sum(r["state"] == "covered" for r in coverage),
                             "derived": sum(r["state"] == "derived" for r in coverage),
                             "waived": sum(r["state"] == "waived" for r in coverage),
                             "uncovered": uncovered, "underived": underived, "sentences": coverage},
                "waivers": waivers,
                "renamed_conclusions": renamed, "provenance": origins,
                "declared": self.declared, "usage": self.usage()}

    def _witnesses(self):
        """Every certified step that states a frozen target or is anchored to a claimed sentence, by name."""
        targets = [row["formula"] for row in self.targets.values() if row["formula"] is not None]
        return sorted(n.name for n in self.nodes.values()
                      if n.kind == "step" and self.checks.get(n.name, {}).get("status") == "follows"
                      and (n.formula in targets or any(self.sentences[a]["role"] == "claimed" for a in n.anchors)))

    def _anchored_entailment(self, name):
        """``(verdict, unanchored)``: do the ANCHORED assumptions under step ``name`` alone entail it?

        ``yes`` without search when its support is fully certified and every assumption is anchored (the
        certified chain is the proof); otherwise decided by ``_decide`` on the anchored assumptions only.
        An uncertified step in the support makes the chain no proof: ``unknown`` (fail closed)."""
        support = [self.nodes[n] for n in self._support(name)]
        loose = sorted(m.name for m in support if m.kind == "assumption" and self._anchor_state(m) != "anchored")
        if not all(self.checks.get(m.name, {}).get("status") == "follows" for m in support if m.kind == "step"):
            return "unknown", loose
        if not loose:
            return "yes", loose
        anchored = [m.formula for m in support if m.kind == "assumption" and m.name not in loose]
        return self._decide(anchored, self.nodes[name].formula), loose

    def _derivation(self, sid, dependence):
        """``(steps, undecided)``: EVERY witness that derives claimed sentence ``sid`` (sorted), and, when
        none does, the witnesses rejected only because a decision is still undecided within budget."""
        derived, undecided = [], []
        for name in sorted(n.name for n in self.nodes.values() if sid in n.anchors):
            if name not in dependence:  # not a certified step
                continue
            node = self.nodes[name]
            verdicts = {m: self._decide([self.nodes[m].formula], node.formula)
                        for m in self._support(name) if self.nodes[m].kind == "assumption"}
            if dependence[name]["verdict"] == "no" or any(v == "yes" for v in verdicts.values()):
                continue
            unknown = sorted(m for m, v in verdicts.items() if v == "unknown")
            if dependence[name]["verdict"] == "unknown":
                unknown.append("independence of unanchored assumptions")
            if unknown:
                undecided.append(f"{name}: {', '.join(unknown)}")
                continue
            derived.append(name)
        return derived, [] if derived else undecided

    def _consistency_failures(self, label, names, view=None):
        """Assumptions ``names`` must be decided consistent; contradictory or undecided fails."""
        leaves = [self.nodes[n].formula for n in sorted(names)]
        if not leaves:
            return []
        verdict = self._decide(leaves, ast.Bottom())
        if view is not None and verdict != "no":
            view["inconsistent_assumptions"] = True if verdict == "yes" else "unknown"
        if verdict == "yes":
            return [f"{label}: its assumptions are jointly contradictory"]
        if verdict == "unknown":
            return [f"{label}: consistency of its assumptions undecided within budget (fail closed)"]
        return []

    def _renamed_conclusions(self):
        """Declared vocabulary that carries a target.

        The suspect assumptions are every assumption that mentions a declared symbol (predicate,
        constant or sort) plus every
        assumption not anchored to given prose. If they jointly entail a target WITHOUT the anchored,
        undeclared premises, the target was carried in, not derived; the reported set is a minimal
        entailing subset (so chains through ordinary assumptions are caught, not only pairs).
        """
        if not self.declared:
            return []
        declared = set(self.declared)
        carriers = [n for n in self.nodes.values() if n.kind == "assumption" and _symbols_of(n.formula) & declared]
        if not carriers:
            return []
        names = {n.name for n in carriers}
        suspects = [n for n in self.nodes.values() if n.kind == "assumption"
                    and (n.name in names or self._anchor_state(n) != "anchored")]
        found = []
        for tid, row in self.targets.items():
            if row["formula"] is None:
                continue
            verdict = self._decide([g.formula for g in suspects], row["formula"])
            if verdict == "no":
                continue
            if verdict == "unknown":
                found.append({"target": tid, "assumptions": [g.name for g in suspects], "undecided": True})
                continue
            group = list(suspects)
            # Drop ordinary assumptions before declared carriers, so a carrier stays in the witness set.
            # A member is dropped only when the rest is PROVED to still entail the target.
            for member in sorted(group, key=lambda g: (g.name in names, g.name)):  # graph order, not insertion
                rest = [g for g in group if g is not member]
                if self._decide([g.formula for g in rest], row["formula"]) == "yes":
                    group = rest
            if any(g.name in names for g in group):
                found.append({"target": tid, "assumptions": [g.name for g in group]})
        return found

    def usage(self):
        totals = {}
        for event in self.events:
            for role, row in event.get("tokens", {}).items():
                acc = totals.setdefault(role, {"input_tokens": 0, "output_tokens": 0, "calls": 0})
                for key in acc:
                    acc[key] += row.get(key, 0) or 0
        actions = {}
        for event in self.events:
            actions[event["action"]] = actions.get(event["action"], 0) + 1
        return {"tokens": totals, "actions": actions, "events": len(self.events),
                "rejected_actions": sum(1 for e in self.events if not e["result"]["ok"]),
                "tool_result_chars": sum(e.get("result_chars", 0) for e in self.events)}

    def _do_export(self):
        graphs = {}
        for tid in self.targets:
            graph, reason, _ = self.target_graph(tid)
            graphs[tid] = graph.to_dict() if graph is not None else {"missing": reason}
        return {"graphs": graphs,
                "nodes": [{**self.node_view(n), "anchors": list(self.nodes[n].anchors)} for n in self.nodes],
                "environment": self.env.to_dict(), "english_vocabulary": self.overlay}

    def log_rejection(self, action, args, error):
        """Record a call rejected before dispatch (unknown tool or argument)."""
        result = stream_audit.sanitize({"ok": False, "error": error}, self.SECRET_NEEDLES)
        args = stream_audit.sanitize(deepcopy(args), self.SECRET_NEEDLES)
        self.events.append({"seq": len(self.events), "action": action, "args": args, "time": _now(),
                            "rejected_by_api": True, "result": result,
                            "result_chars": len(json.dumps(result, ensure_ascii=False))})
        return result

    # ------------------------------------------------------------------ ledger
    def to_ledger(self):
        return {"format": SESSION_FORMAT, "config": self.config, "events": self.events}

    @classmethod
    def from_ledger(cls, data, *, verify=True):
        """Rebuild by replaying every event; recorded model outputs are reused, never re-requested.

        Integrity checks run whether or not ``verify`` is set: the configuration must match its
        ``config_digest``; token totals are recomputed from the recorded calls (never copied from the
        file); every recorded model call must be consumed; ``rejected_by_api`` events must have the
        exact shape ``log_rejection`` writes. ``verify`` additionally requires every result to reproduce.
        This proves internal consistency only: an evaluator must also rebuild the configuration from
        its own materials and compare the calls ledger (``ve.assist.verify.verify_session``).
        """
        if type(data) is not dict or data.get("format") != SESSION_FORMAT:
            raise LedgerReplayError("Not a ve assist ledger")
        config = data.get("config")
        if type(config) is not dict or not isinstance(config.get("config_digest"), str):
            raise LedgerReplayError("Ledger configuration has no config_digest")
        if config_digest(config) != config["config_digest"]:
            raise LedgerReplayError("Ledger configuration does not match its config_digest")
        events = data.get("events")
        if type(events) is not list:
            raise LedgerReplayError("Ledger events must be a list")
        session = cls(config)
        for index, event in enumerate(events):
            if type(event) is not dict or event.get("seq") != index:
                raise LedgerReplayError(f"Ledger event {index} is malformed or out of sequence")
            if "rejected_by_api" in event:
                session._replay_rejection(event)
                continue
            if type(event.get("args")) is not dict:
                raise LedgerReplayError(f"Ledger event {index} has no argument object")
            result = session.apply(event.get("action"), event["args"], _recorded=event)
            replayed = session.events[-1]
            replayed["time"] = event.get("time", replayed["time"])
            if session._leftover_calls:
                raise LedgerReplayError(f"Ledger event {index} records model calls the replay never used")
            for key in ("model_calls", "tokens"):
                if event.get(key) != replayed.get(key):
                    raise LedgerReplayError(f"Ledger event {index} ({event.get('action')}): recorded {key} "
                                            "do not match the replay")
            if verify and json.loads(json.dumps(result)) != event.get("result"):
                raise LedgerReplayError(f"Ledger event {index} ({event.get('action')}) does not replay")
        return session

    REJECTION_KEYS = {"seq", "action", "args", "time", "rejected_by_api", "result", "result_chars"}

    def _replay_rejection(self, event):
        """Accept a pre-dispatch rejection only in the exact shape ``log_rejection`` writes."""
        result = event.get("result")
        error = result.get("error") if type(result) is dict else None
        if (set(event) != self.REJECTION_KEYS or event["rejected_by_api"] is not True
                or type(event["action"]) is not str or type(event["args"]) is not dict
                or result != {"ok": False, "error": error} or type(error) is not dict
                or set(error) != {"code", "message"} or not all(type(v) is str for v in error.values())
                or event["result_chars"] != len(json.dumps(result, ensure_ascii=False))):
            raise LedgerReplayError(f"Ledger event {event['seq']} is not a valid API rejection")
        self.events.append(deepcopy(event))

    def recorded_model_call(self):
        """During replay, the next recorded model call; None when live or when none remain.

        A replayed session has no backend, so running out of recorded calls reproduces exactly the
        live "no backend" failure; the result comparison then detects a truncated ledger.
        """
        if not self._replaying:
            return None
        call = self._replaying.pop(0)
        if type(call) is not dict or not isinstance(call.get("prompt_digest"), str):
            raise LedgerReplayError("Recorded model call is malformed")
        attempts = call.get("attempts", [])
        if type(attempts) is not list or not all(type(a) is dict and set(a) == {"input_tokens", "output_tokens"}
                                                 for a in attempts):
            raise LedgerReplayError("Recorded model call has malformed retry attempts")
        for row in (call, *attempts):
            for key in ("input_tokens", "output_tokens"):
                value = row.get(key)
                if value is not None and (type(value) is not int or value < 0):
                    raise LedgerReplayError("Recorded model call has invalid token counts")
        return call

    @property
    def replaying(self):
        return self._replaying is not None
