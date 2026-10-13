"""Revisioned recovery and meaning-approval service for W8 consumers.

This layer does not certify proofs or source fidelity. Adapters supply the W2
document schema and W3 alias admission when those interfaces are available.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
import inspect
import json
import time

from ..ast import formula_from_data, formula_to_data
from ..evaluate import evaluate
from ..english import sentence_parse_cache
from .ambiguity_patterns import (CATALOGUE_VERSION, OPERATION_SECONDS, SEARCH_LIMITS,
                                 MAX_CANDIDATES, MAX_COMPARISONS, MAX_CARDS, Budget, _Deadline,
                                 checked_wording)
# The service is assembled from three modules (AR-9); every name they define is re-exported here.
from .recovery_commands import (  # noqa: F401 -- STATES, nearest_wordings re-exported
    COMMANDS, MAX_PROPOSALS, MAX_REPLIES, PROPOSAL_SECONDS, STATES, TASK_SECONDS, DocumentAdapter,
    GlossaryAdapter, ProposerAdapter, _Commands, nearest_wordings)
from .recovery_journal import (  # noqa: F401 -- DIVERGED re-exported
    DIVERGED, LEDGER_KEYS, RECOVERY_VERSION, Unit, _canonical, _digest, _InvalidLedger, _Journal,
    _Observations)
from .recovery_replay import _Replay


class RecoveryService(_Journal, _Replay, _Commands):
    """Single writer API over an event-sourced recovery ledger.

    Every top-level call is a command recorded with its JSON inputs and the
    nondeterministic observations it made. Units, readings, catalogue
    results, pending items, narrowings, approvals and events are all derived
    by running commands through the transitions of ``recovery_commands``; nothing is
    imported. ``from_ledger`` replays every command from genesis and accepts
    the ledger only if it is byte-equal to that replay.

    The public attributes are a read cache. Each transition or replay seals
    the canonical state it derived; a command runs only when the live state
    equals that seal and then continues from the sealed data, so edits to the
    cache cannot reach a transition. ``approval_valid`` replays the ledger.
    """
    def __init__(self, env, *, grammar_version: str, glossary_version: str,
                 reading_set_version: str, document_adapter: DocumentAdapter | None = None,
                 glossary_adapter: GlossaryAdapter | None = None, clock=time.time):
        self.env = env
        self.versions = {"grammar": grammar_version, "environment": env.environment_id,
                         "glossary": glossary_version, "catalogue": CATALOGUE_VERSION,
                         "reading_set": reading_set_version, "recovery": RECOVERY_VERSION}
        self.genesis_versions = deepcopy(self.versions)
        self.limits = {**SEARCH_LIMITS, "operation_seconds": OPERATION_SECONDS,
                       "max_candidates": MAX_CANDIDATES, "max_comparisons": MAX_COMPARISONS,
                       "max_cards": MAX_CARDS, "max_replies": MAX_REPLIES,
                       "task_seconds": TASK_SECONDS, "max_proposals": MAX_PROPOSALS,
                       "proposal_seconds": PROPOSAL_SECONDS}
        self.document_adapter = document_adapter
        self.glossary_adapter = glossary_adapter
        self.clock = clock
        self.units: dict[str, Unit] = {}
        self.events: list[dict] = []
        self.commands: list[dict] = []
        self.revision = 0
        self._observed: _Observations | None = None
        self._operation_budget: Budget | None = None
        self._replaying: dict | None = None
        self._document = None
        self._seal()

    # -- seams -------------------------------------------------------------
    # The split modules reach these names of this module through the service,
    # so the deadline and checkers every command uses are the ones set here.

    @staticmethod
    def _operation_seconds():
        return OPERATION_SECONDS

    @staticmethod
    def _checked_wording(*args, **kwargs):
        return checked_wording(*args, **kwargs)

    @staticmethod
    def _evaluate(*args, **kwargs):
        return evaluate(*args, **kwargs)

    @staticmethod
    def _formula_to_data(*args, **kwargs):
        return formula_to_data(*args, **kwargs)

    @staticmethod
    def _formula_from_data(*args, **kwargs):
        return formula_from_data(*args, **kwargs)

    # -- command log -------------------------------------------------------

    def _command(self, _name, /, _started_at=None, **args):
        with sentence_parse_cache():
            return self._command_uncached(_name, _started_at=_started_at, **args)

    def _command_uncached(self, _name, /, _started_at=None, **args):
        """Run one top-level command as a transaction and append its record.

        Live and replayed commands both run on the JSON-decoded arguments, so
        replay sees exactly the inputs the live transition saw. A command that
        fails before emitting an event leaves no trace; one that fails after
        emitting events is recorded with its error, and replay must reproduce
        both.
        """
        if self._observed is not None:
            raise RuntimeError("recovery commands cannot run inside another command")
        stop = (time.monotonic() if _started_at is None else _started_at) + OPERATION_SECONDS
        recorded = self._replaying
        self._observed = (_Observations(self.clock) if recorded is None else
                          _Observations(self.clock, replay=True, recorded=recorded.get("observed")))
        self._operation_budget = self._observed.budget(OPERATION_SECONDS, stop=stop)
        budget = self._operation_budget
        deadline_label = {"approve": "approval", "set_readings": "reading",
                          "resolve_pending": "resolution"}.get(_name, _name)
        deadline_error = ValueError(f"{deadline_label} operation deadline")
        saved = None
        previous_seal = self._sealed
        error = None
        try:
            # The replay takes the same checkpoint even though its state was
            # reconstructed by the caller. The live command starts its clock
            # before reconstructing the sealed cache.
            with budget.guard():
                if recorded is None:
                    self._resume()
                try:
                    args = json.loads(_canonical(args))
                except (TypeError, ValueError) as exc:
                    raise ValueError("recovery command arguments must be JSON data") from exc
                operation = getattr(self, "_" + _name)
                if set(args) != set(inspect.signature(operation).parameters) - {"budget"}:
                    raise ValueError("recovery command arguments do not match the command")
                saved = ({k: deepcopy(asdict(u)) for k, u in self.units.items()}, len(self.events),
                         self.revision, deepcopy(self.versions))
            # Catalogue and undo have their own pending/stale deadline outcomes.
            # Other commands are interrupted throughout their transition.
            if _name in {"classify", "continue_catalogue", "undo"}:
                result = operation(**args)
            else:
                with budget.guard():
                    result = operation(**args)
            if _name not in {"classify", "continue_catalogue", "undo"}:
                if budget.expired():
                    raise _Deadline(budget)
        except _Deadline as exc:
            if exc.budget is not budget:
                self._observed, self._operation_budget = None, None
                if saved is not None:
                    self._restore(saved)
                raise
            error = deadline_error
        except Exception as exc:
            error = exc
        except BaseException:
            self._observed, self._operation_budget = None, None
            if saved is not None:
                self._restore(saved)
            raise
        observed, self._observed, self._operation_budget = self._observed, None, None
        if saved is None:
            if budget.fired is None:
                raise error
            # A timeout can interrupt cache reconstruction. Rebuild only from
            # the prior seal, then record the deadline at that checkpoint.
            self._load_sealed()
            args = json.loads(_canonical(args))
            operation = getattr(self, "_" + _name)
            if set(args) != set(inspect.signature(operation).parameters) - {"budget"}:
                raise ValueError("recovery command arguments do not match the command")
            saved = ({k: deepcopy(asdict(u)) for k, u in self.units.items()}, len(self.events),
                     self.revision, deepcopy(self.versions))
        if error is not None and (len(self.events) == saved[1] or budget.fired is not None):
            self._restore(saved)
            # A deadline is an observable command outcome even when no event
            # was emitted. Its checkpoint is required to reproduce the failure.
            if budget.fired is None:
                raise error
        record = {"sequence": len(self.commands) + 1, "command": _name, "args": args,
                  "observed": observed.record(), "revision": self.revision,
                  "error": None if error is None else {"type": type(error).__name__,
                                                       "message": str(error)},
                  "previous_digest": self.commands[-1]["command_digest"] if self.commands else None}
        record["command_digest"] = _digest(record)
        self.commands.append(record)
        if error is None and budget.fired is None:
            try:
                with budget.guard():
                    self._seal()
            except _Deadline as exc:
                if exc.budget is not budget:
                    self.commands.pop()
                    self._restore(saved)
                    self._sealed = previous_seal
                    raise
                self.commands.pop()
                self._restore(saved)
                self._sealed = previous_seal
                error = deadline_error
                record["observed"] = observed.record()
                record["revision"] = self.revision
                record["error"] = {"type": "ValueError", "message": str(error)}
                record["command_digest"] = _digest({k: v for k, v in record.items()
                                                    if k != "command_digest"})
                self.commands.append(record)
        if error is not None or budget.fired is not None:
            self._seal()
        if error is not None:
            raise error
        return result

    def _legacy_command(self, _name, /, **args):
        """Replay commands recorded before the command-entry budget existed.

        Their observations contain only budgets opened by individual transition
        steps. This path is never used for a live command.
        """
        if self._replaying is None or self._observed is not None:
            raise RuntimeError("legacy recovery replay requires one recorded command")
        args = json.loads(_canonical(args))
        operation = getattr(self, "_" + _name)
        if set(args) != set(inspect.signature(operation).parameters) - {"budget"}:
            raise ValueError("recovery command arguments do not match the command")
        saved = ({k: deepcopy(asdict(u)) for k, u in self.units.items()}, len(self.events),
                 self.revision, deepcopy(self.versions))
        error = None
        try:
            self._observed = _Observations(self.clock, replay=True,
                                           recorded=self._replaying.get("observed"))
            result = operation(**args)
        except Exception as exc:
            error = exc
        except BaseException:
            self._observed = None
            self._restore(saved)
            raise
        observed, self._observed = self._observed, None
        if error is not None and (observed is None or len(self.events) == saved[1]):
            self._restore(saved)
            raise error
        record = {"sequence": len(self.commands) + 1, "command": _name, "args": args,
                  "observed": observed.record(), "revision": self.revision,
                  "error": None if error is None else {"type": type(error).__name__,
                                                       "message": str(error)},
                  "previous_digest": self.commands[-1]["command_digest"] if self.commands else None}
        record["command_digest"] = _digest(record)
        self.commands.append(record)
        self._seal()
        if error is not None:
            raise error
        return result

    def _budget(self) -> Budget:
        return (self._operation_budget if self._operation_budget is not None
                else self._observed.budget(OPERATION_SECONDS))

    @classmethod
    def _replay(cls, env, ledger, clock=time.time, budget=None):
        with sentence_parse_cache():
            return cls._replay_uncached(env, ledger, clock, budget)

    @classmethod
    def _replay_uncached(cls, env, ledger, clock=time.time, budget=None):
        """Derive a service from genesis by replaying every recorded command."""
        budget = Budget(OPERATION_SECONDS) if budget is None else budget
        with budget.guard():
            service = cls._replay_inner(env, ledger, clock)
            if budget.expired():
                raise _Deadline(budget)
            return service

    @classmethod
    def _replay_inner(cls, env, ledger, clock):
        if type(ledger) is not dict or set(ledger) != LEDGER_KEYS or ledger["format"] != RECOVERY_VERSION:
            raise _InvalidLedger("invalid recovery ledger")
        genesis = ledger["genesis_versions"]
        if type(genesis) is not dict or not all(type(genesis.get(k)) is str
                                                 for k in ("grammar", "glossary", "reading_set")):
            raise _InvalidLedger("invalid recovery ledger")
        service = cls(env, grammar_version=genesis["grammar"], glossary_version=genesis["glossary"],
                      reading_set_version=genesis["reading_set"], clock=clock)
        if _canonical(genesis) != _canonical(service.versions) or _canonical(ledger["limits"]) != _canonical(service.limits):
            raise ValueError("recovery ledger versions or limits changed")
        if type(ledger["commands"]) is not list or type(ledger["events"]) is not list:
            raise _InvalidLedger("invalid recovery ledger")
        legacy_seen = False
        for record in ledger["commands"]:
            first = len(service.events)
            if (type(record) is not dict or type(record.get("command")) is not str
                    or record["command"] not in COMMANDS or type(record.get("args")) is not dict):
                raise _InvalidLedger("invalid recovery ledger")
            old_slot = record.get("observed", {}).get("deadlines") == []
            modes = ("legacy",) if old_slot else (("current", "legacy") if legacy_seen else ("current",))
            previous_seal = service._sealed
            for mode in modes:
                service._replaying = record
                try:
                    command = service._legacy_command if mode == "legacy" else service._command
                    command(record["command"], **record["args"])
                except Exception:
                    pass  # a recorded failure must recur; the comparison below decides
                finally:
                    service._replaying = None
                if (service.commands and _canonical(service.commands[-1]) == _canonical(record)
                        and _canonical(service.events[first:])
                        == _canonical(ledger["events"][first:len(service.events)])):
                    legacy_seen = legacy_seen or mode == "legacy"
                    break
                service._sealed = previous_seal
                service._load_sealed()
            else:
                raise _InvalidLedger("invalid recovery ledger")
        if _canonical(service.to_ledger()) != _canonical(ledger):
            raise _InvalidLedger("invalid recovery ledger")
        if not all(service._approval_valid(k, Budget()) for k, u in service.units.items()
                   if u.state == "approved"):
            raise _InvalidLedger("invalid recovery ledger")
        service._seal()
        return service

    def request_proposer(self, unit_id, proposer: ProposerAdapter, *, expected_revision=None):
        """Reserve before calling. Failure stays visible; an explicit retry is a new event.

        The reservation and the proposer outcome are separate commands, so
        edits made while the request is outstanding are ordered in the ledger.
        """
        capped = self._command("request_proposer", unit_id=unit_id, expected_revision=expected_revision)
        if capped is not None:
            return capped
        unit = self.units[unit_id]
        reserved_revision, reserved_source = self.revision, unit.source
        started = time.monotonic()
        try:
            suggestion = proposer.request(reserved_source, timeout_seconds=PROPOSAL_SECONDS)
            outcome = ({"kind": "suggestion", "text": suggestion} if isinstance(suggestion, str)
                       else {"kind": "failed", "error": "TypeError"})
        except Exception as exc:
            outcome = {"kind": "failed", "error": type(exc).__name__}
        if self.revision != reserved_revision or self.units.get(unit_id) is not unit or unit.source != reserved_source:
            return {"status": "stale", "reason": "proposer request superseded"}
        if outcome["kind"] == "suggestion" and time.monotonic() - started > PROPOSAL_SECONDS:
            outcome = {"kind": "timed_out"}
        return self._command("proposer_result", unit_id=unit_id, reserved_revision=reserved_revision,
                             outcome=outcome)
