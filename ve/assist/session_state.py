"""The assist session's records: formats, errors, the node record, formula helpers and the ledger.

Split out of ``ve.assist.session`` (AR-9), which re-exports every name here.
"""
from __future__ import annotations

from copy import deepcopy
import dataclasses
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json

from .. import ast, stream_audit
from ..environment import RESERVED, valid_identifier
from ..errors import VEError

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


class _Ledger:
    """The append-only ledger of an ``AssistSession`` and its deterministic replay."""

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
