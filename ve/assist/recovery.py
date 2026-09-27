"""Revisioned recovery and meaning-approval service for W8 consumers.

This layer does not certify proofs or source fidelity. Adapters supply the W2
document schema and W3 alias admission when those interfaces are available.
"""
from __future__ import annotations

from contextlib import nullcontext
from copy import deepcopy
from dataclasses import asdict, dataclass, field
import hashlib
import inspect
import json
import math
import time
from typing import Protocol

from ..ast import check_formula, formula_from_data, formula_to_data
from ..errors import VEError
from ..evaluate import evaluate
from ..model import FiniteModel
from ..identity import meaning_id
from .ambiguity_patterns import (CATALOGUE_VERSION, OPERATION_SECONDS, SEARCH_LIMITS,
                                 MAX_CANDIDATES, MAX_COMPARISONS, MAX_CARDS, Budget, _Deadline,
                                 checked_wording)

# @2: the ledger records commands and observations; state is derived by replay.
RECOVERY_VERSION = "ve.assist-recovery@2"
MAX_REPLIES = 8
TASK_SECONDS = 300
MAX_PROPOSALS = 2
PROPOSAL_SECONDS = 50
STATES = frozenset({"draft", "analysing", "needs_word", "needs_repair",
                    "reading_review", "ready", "approved", "exhausted", "stale", "unresolved"})


def _digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode()).hexdigest()


class DocumentAdapter(Protocol):
    """W2 owns schema validation, unit insertion, reading insertion, narrowing."""
    version: str
    def add_unit(self, document, *, anchor, kind, meaning_status, support): ...
    def add_reading(self, document, *, unit_id, meaning_id, kind): ...
    def narrow(self, document, *, set_id, set_version, keeps, actor, reason, cited_spans): ...


class GlossaryAdapter(Protocol):
    """W3 must validate conservative aliases, direction, collisions and cycles."""
    version: str
    def propose_alias(self, *, source, target, argument_types, direction, context): ...


class ProposerAdapter(Protocol):
    """Untrusted suggestions; the caller enforces the 50-second request timeout."""
    def request(self, source: str, *, timeout_seconds: int): ...


def nearest_wordings(query: str, registered: list[str] | tuple[str, ...]) -> list[str]:
    """Stable Levenshtein token edits, then lexical tie break; advisory only."""
    def distance(a, b):
        a, b = a.lower().split(), b.lower().split()
        row = list(range(len(b) + 1))
        for i, x in enumerate(a, 1):
            nxt = [i]
            for j, y in enumerate(b, 1):
                nxt.append(min(nxt[-1] + 1, row[j] + 1, row[j - 1] + (x != y)))
            row = nxt
        return row[-1]
    return sorted(set(registered), key=lambda s: (distance(query, s), s))[:3]


@dataclass
class Unit:
    id: str
    source: str
    anchor: dict
    mode: str = "authoring"
    revision: int = 0
    state: str = "draft"
    meaning_id: str | None = None
    paraphrase: str | None = None
    presentation: str | None = None
    situation: dict | None = None
    readings: list[dict] = field(default_factory=list)
    rejected: list[dict] = field(default_factory=list)
    narrowings: list[dict] = field(default_factory=list)
    pending: list[dict] = field(default_factory=list)
    catalogue_reviewed: list[str] = field(default_factory=list)
    catalogue_results: dict = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)
    approval: dict | None = None
    reason: str | None = None
    replies: int = 0
    proposals: int = 0
    started: float = field(default_factory=time.time)


class _Observations:
    """Nondeterministic inputs of one command: wall clock, deadline expiry, W2.

    A live command reads them; a replayed command takes them from the ledger.
    A recorded expiry can only make an operation stop earlier, so a forged
    observation can add pending work or reject an approval, never grant one.
    """
    KEYS = frozenset({"now", "deadlines", "external"})

    def __init__(self, clock, *, replay=False, recorded=None):
        self.replay = replay
        self.budgets: list[Budget] = []
        self.external: list[str] = []
        if not self.replay:
            self.now, self._fire_at, self._external = clock(), None, None
            return
        if (type(recorded) is not dict or set(recorded) != self.KEYS
                or type(recorded["now"]) not in (int, float) or not math.isfinite(recorded["now"])
                or type(recorded["deadlines"]) is not list
                or any(row is not None and (type(row) is not int or row < 1) for row in recorded["deadlines"])
                or type(recorded["external"]) is not list
                or any(type(row) is not str for row in recorded["external"])):
            raise ValueError("invalid recorded observations")
        self.now = recorded["now"]
        self._fire_at = list(recorded["deadlines"])
        self._external = list(recorded["external"])

    def budget(self, seconds, *, stop=None) -> Budget:
        if not self.replay:
            budget = Budget(seconds, stop=stop)
        elif not self._fire_at:
            raise ValueError("replayed command used an unrecorded deadline")
        else:
            budget = Budget(replay=True, fire_at=self._fire_at.pop(0))
        self.budgets.append(budget)
        return budget

    def record(self):
        return {"now": self.now, "deadlines": [budget.fired for budget in self.budgets],
                "external": list(self.external)}


class _InvalidLedger(ValueError):
    pass


def _canonical(value) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
                      allow_nan=False)


LEDGER_KEYS = frozenset({"format", "genesis_versions", "versions", "limits", "revision",
                         "commands", "events"})
DIVERGED = "recovery state differs from its ledger replay"


class RecoveryService:
    """Single writer API over an event-sourced recovery ledger.

    Every top-level call is a command recorded with its JSON inputs and the
    nondeterministic observations it made. Units, readings, catalogue
    results, pending items, narrowings, approvals and events are all derived
    by running commands through the transition code below; nothing is
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

    # -- derived state -----------------------------------------------------

    def _state(self) -> str:
        return _canonical({"ledger": self.to_ledger(),
                           "units": {k: asdict(u) for k, u in self.units.items()}})

    def _seal(self):
        self._sealed = self._state()

    def _resume(self):
        """Require the live state to be the sealed derived state, then continue from the seal.

        Rebuilding from the seal keeps unit identities but drops any object
        substituted into the cache, even one that serialises identically.
        """
        try:
            live = self._state()
        except (KeyError, TypeError, ValueError, IndexError, AttributeError, RecursionError):
            live = None
        if live != self._sealed:
            raise ValueError(DIVERGED)
        self._load_sealed()

    def _load_sealed(self):
        """Restore the last committed state after an interrupted preparation."""
        sealed = json.loads(self._sealed)
        units = {}
        for unit_id, data in sealed["units"].items():
            derived, current = Unit(**data), self.units.get(unit_id)
            if type(current) is Unit:
                current.__dict__.clear()
                current.__dict__.update(derived.__dict__)
                derived = current
            units[unit_id] = derived
        if type(self.units) is not dict:
            self.units = {}
        self.units.clear()
        self.units.update(units)
        ledger = sealed["ledger"]
        self.genesis_versions, self.versions = ledger["genesis_versions"], ledger["versions"]
        self.limits, self.revision = ledger["limits"], ledger["revision"]
        self.commands, self.events = ledger["commands"], ledger["events"]

    def _derived(self, budget):
        """Replay the recorded commands from genesis; the live state must equal that replay."""
        try:
            with budget.guard():
                live = self._state()
                if live != self._sealed:
                    raise ValueError(DIVERGED)
                replayed = self._replay(self.env, json.loads(live)["ledger"], budget=budget)
        except (KeyError, TypeError, ValueError, IndexError, AttributeError, RecursionError) as exc:
            raise ValueError(DIVERGED) from exc
        if live != replayed._sealed:
            raise ValueError(DIVERGED)
        return replayed

    # -- command log -------------------------------------------------------

    def _command(self, _name, /, _started_at=None, **args):
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
                    raise _Deadline
        except _Deadline:
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
            except _Deadline:
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

    def _restore(self, saved):
        units, events, revision, versions = saved
        for unit_id in list(self.units):
            if unit_id not in units:
                del self.units[unit_id]
            else:
                self.units[unit_id].__dict__.update(deepcopy(units[unit_id]))
        del self.events[events:]
        self.revision = revision
        self.versions.clear()
        self.versions.update(versions)

    def _now(self):
        return self._observed.now

    def _budget(self) -> Budget:
        return (self._operation_budget if self._operation_budget is not None
                else self._observed.budget(OPERATION_SECONDS))

    def _event(self, action, unit: Unit, **detail):
        self.revision += 1
        unit.revision = self.revision
        event = {"revision": self.revision, "command": len(self.commands) + 1,
                 "action": action, "unit": unit.id,
                 "state": unit.state, "source_digest": _digest(unit.source),
                 "versions": deepcopy(self.versions), "limits": deepcopy(self.limits),
                 "unit_snapshot": self._snapshot(unit),
                 "previous_digest": self.events[-1]["event_digest"] if self.events else None,
                 **detail}
        event["event_digest"] = _digest(event)
        self.events.append(event)
        return event

    @staticmethod
    def _snapshot(unit):
        return deepcopy(asdict(unit))

    def _expect(self, expected_revision):
        if expected_revision is not None and expected_revision != self.revision:
            raise ValueError("stale recovery revision")

    @classmethod
    def _replay(cls, env, ledger, clock=time.time, budget=None):
        """Derive a service from genesis by replaying every recorded command."""
        budget = Budget(OPERATION_SECONDS) if budget is None else budget
        with budget.guard():
            return cls._replay_inner(env, ledger, clock)

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

    @classmethod
    def from_ledger(cls, env, ledger, *, document_adapter=None, glossary_adapter=None, clock=time.time):
        try:
            service = cls._replay(env, ledger, clock)
        except _InvalidLedger:
            raise
        except _Deadline as exc:
            raise ValueError("recovery import operation deadline") from exc
        except ValueError as exc:
            if str(exc) == "recovery ledger versions or limits changed":
                raise
            raise ValueError("invalid recovery ledger") from exc
        except (KeyError, TypeError, IndexError, AttributeError, RecursionError) as exc:
            raise ValueError("invalid recovery ledger") from exc
        service.document_adapter = document_adapter
        service.glossary_adapter = glossary_adapter
        return service

    def to_ledger(self):
        return {"format": RECOVERY_VERSION, "genesis_versions": deepcopy(self.genesis_versions),
                "versions": deepcopy(self.versions), "limits": deepcopy(self.limits),
                "revision": self.revision, "commands": deepcopy(self.commands),
                "events": deepcopy(self.events)}

    def verify_ledger(self, ledger=None):
        """Replay ``ledger`` (default: this service's) and require it to be this state."""
        budget = Budget(OPERATION_SECONDS)
        try:
            with budget.guard():
                derived = self._derived(budget)
                return ledger is None or self._replay(self.env, ledger, budget=budget)._sealed == derived._sealed
        except (KeyError, TypeError, ValueError, IndexError, AttributeError, RecursionError, _Deadline):
            return False

    # -- transitions -------------------------------------------------------

    def _invalidate(self, unit_id, seen=None):
        seen = set() if seen is None else seen
        if unit_id in seen:
            return
        seen.add(unit_id)
        unit = self.units[unit_id]
        if unit.approval:
            unit.approval = None
            unit.state = "stale"
            self._event("invalidate", unit)
        for child in self.units.values():
            if unit_id in child.dependencies:
                self._invalidate(child.id, seen)

    def add(self, unit_id: str, source: str, anchor: dict, *, mode="authoring", dependencies=(), expected_revision=None):
        started = time.monotonic()
        return self._command("add", _started_at=started, unit_id=unit_id, source=source, anchor=anchor, mode=mode,
                             dependencies=list(dependencies), expected_revision=expected_revision)

    def _add(self, unit_id, source, anchor, mode, dependencies, expected_revision):
        self._expect(expected_revision)
        if (not isinstance(unit_id, str) or not unit_id or unit_id in self.units
                or not isinstance(source, str) or not source or mode not in {"authoring", "translation"}
                or not isinstance(dependencies, list)):
            raise ValueError("invalid or duplicate unit")
        if any(not isinstance(parent, str) or parent not in self.units for parent in dependencies):
            raise ValueError("unknown dependency")
        unit = Unit(unit_id, source, deepcopy(anchor), mode=mode, dependencies=list(dependencies),
                    started=self._now())
        self.units[unit_id] = unit
        self._event("add", unit)
        return unit

    def word_prompt(self, *, term, accepted_prefix, expected, registered):
        return {"term": term, "accepted_prefix": accepted_prefix,
                "expected_construction": expected,
                "nearest_registered_wordings": nearest_wordings(term, registered),
                "prefix_is_admitted": False}

    def undo(self, unit_id: str, target_revision: int, *, expected_revision=None):
        """Restore an earlier snapshot as a new revision; revalidate its approval."""
        return self._command("undo", unit_id=unit_id, target_revision=target_revision,
                             expected_revision=expected_revision)

    def _undo(self, unit_id, target_revision, expected_revision):
        self._expect(expected_revision)
        # Events are derived by this service's own transitions, never imported.
        prior = next((e["unit_snapshot"] for e in self.events
                      if e["unit"] == unit_id and e["revision"] == target_revision), None)
        if prior is None:
            raise ValueError("unknown unit revision")
        old_approval = deepcopy(prior["approval"])
        current = self.units[unit_id]
        # One budget covers the whole undo: revalidating the current approval
        # and every restoration step (parse, catalogue review, readings,
        # approval). Expiry can only leave the unit for review.
        budget = self._budget()
        # The undo event always advances this unit's revision, including when
        # edit sees identical fields or the requested snapshot was preapproval.
        for child in list(self.units.values()):
            if unit_id in child.dependencies:
                self._invalidate(child.id)
        if (old_approval is not None and current.approval == old_approval
                and current.source == prior["source"] and current.anchor == prior["anchor"]
                and current.presentation == prior["presentation"]
                and self._approval_still_valid(unit_id, budget)):
            self._event("undo", current, target_revision=target_revision)
            return current
        unit = self._edit(unit_id, prior["source"], prior["anchor"], prior["presentation"], None)
        self._event("undo", unit, target_revision=target_revision)
        if old_approval is None:
            return unit
        snap = old_approval["snapshot"]
        try:
            from ..english import parse_english_with_metadata
            with budget.guard():
                parsed = parse_english_with_metadata(self.env, snap["presentation"].rstrip(".\n") + ".\n")
                formula = parsed.document.formulas[0]
                if len(parsed.document.formulas) != 1 or meaning_id(self.env, formula) != snap["meaning_id"]:
                    raise ValueError("restored meaning changed")
            self._invalidate(unit_id)
            self._start(unit_id, None)
            self._classify(unit_id, "one", budget=budget)
            if unit.state != "ready":
                raise ValueError("restored reading review is incomplete")
            self._set_readings(unit_id, deepcopy(snap["considered"]), [], None, budget=budget)
            self._approve(unit_id, formula_to_data(self.env, formula), snap["actor"], snap["paraphrase"],
                          snap["presentation"], snap["situation"], snap["rejected"], snap["narrowing"], None,
                          budget=budget)
        except (ValueError, KeyError, IndexError, _Deadline):
            unit.state = "stale"
            self._event("undo_requires_review", unit)
        return unit

    def _approval_still_valid(self, unit_id, budget) -> bool:
        try:
            return self._approval_valid(unit_id, budget)
        except _Deadline:
            return False

    def edit(self, unit_id, *, source=None, anchor=None, presentation=None, expected_revision=None):
        return self._command("edit", unit_id=unit_id, source=source, anchor=anchor,
                             presentation=presentation, expected_revision=expected_revision)

    def _edit(self, unit_id, source, anchor, presentation, expected_revision):
        self._expect(expected_revision)
        unit = self.units[unit_id]
        if source is not None and (not isinstance(source, str) or not source):
            raise ValueError("invalid source")
        new_source = unit.source if source is None else source
        new_anchor = unit.anchor if anchor is None else anchor
        new_presentation = unit.presentation if presentation is None else presentation
        if (new_source, new_anchor, new_presentation) == (unit.source, unit.anchor, unit.presentation):
            return unit
        source_changed = new_source != unit.source
        source_ref = next((event["revision"] for event in reversed(self.events)
                           if event["unit"] == unit_id and event["action"] == "proposer_suggested"
                           and source is not None and event.get("text") == source), None)
        self._invalidate(unit_id)
        if source is not None:
            unit.source = source
        if anchor is not None:
            unit.anchor = deepcopy(anchor)
        if presentation is not None:
            unit.presentation = presentation
        if source_changed:
            unit.state = "draft"
            unit.meaning_id = None
            unit.readings.clear()
            unit.rejected.clear()
            unit.narrowings.clear()
            unit.pending.clear()
            unit.catalogue_reviewed.clear()
            unit.catalogue_results.clear()
        elif unit.state == "stale":
            unit.state = "reading_review" if unit.pending else "ready"
        self._event("edit", unit, source_ref=source_ref)
        return unit

    def update_versions(self, *, expected_revision=None, **versions):
        return self._command("update_versions", versions=versions, expected_revision=expected_revision)

    def _update_versions(self, versions, expected_revision):
        self._expect(expected_revision)
        if (not isinstance(versions, dict) or set(versions) - set(self.versions)
                or any(not isinstance(v, str) for v in versions.values())):
            raise ValueError("unknown version field")
        changed = any(self.versions[k] != v for k, v in versions.items())
        self.versions.update(versions)
        if changed:
            for unit_id in list(self.units):
                self._invalidate(unit_id)

    def start(self, unit_id, *, expected_revision=None):
        return self._command("start", unit_id=unit_id, expected_revision=expected_revision)

    def _start(self, unit_id, expected_revision):
        self._expect(expected_revision)
        unit = self.units[unit_id]
        if unit.state not in {"draft", "stale", "unresolved", "exhausted"}:
            raise ValueError("unit cannot start analysis from this state")
        unit.state = "analysing"
        if self._now() - unit.started >= TASK_SECONDS or unit.replies > MAX_REPLIES:
            unit.state, unit.reason = "unresolved", "clarification task cap"
            self._event("task_cap", unit)
            return unit.state
        self._event("start", unit)

    def classify(self, unit_id, *, parse_outcome, vocabulary="known", discourse="complete",
                 force="supported", check="checked", pending=(), limit=None,
                 catalogue_bindings=None, catalogue_dispositions=None, expected_revision=None):
        started = time.monotonic()
        return self._command("classify", _started_at=started, unit_id=unit_id, parse_outcome=parse_outcome,
                             vocabulary=vocabulary, discourse=discourse, force=force, check=check,
                             pending=list(pending), limit=limit, catalogue_bindings=catalogue_bindings,
                             catalogue_dispositions=catalogue_dispositions,
                             expected_revision=expected_revision)

    def _classify(self, unit_id, parse_outcome, vocabulary="known", discourse="complete",
                  force="supported", check="checked", pending=(), limit=None,
                  catalogue_bindings=None, catalogue_dispositions=None, expected_revision=None,
                  budget=None):
        budget = self._budget() if budget is None else budget
        with (budget.guard() if self._operation_budget is not None else nullcontext()):
            self._expect(expected_revision)
            unit = self.units[unit_id]
            if unit.state != "analysing":
                raise ValueError("analyse first")
            if parse_outcome not in {"zero", "one", "multiple", "exhausted"}:
                raise ValueError("invalid parse outcome")
            if any(not isinstance(row, dict) for row in pending):
                raise ValueError("pending items must be records")
            from .ambiguity_patterns import PATTERNS, review as review_pattern
            # A restart may refresh catalogue work, but cannot erase an unresolved
            # discourse or author clarification recorded by an earlier attempt.
            requested_pending = deepcopy(list(pending))
            unit.pending = ([deepcopy(row) for row in unit.pending if not row.get("pattern_id")]
                            + requested_pending)
            matched = [pattern.id for pattern in PATTERNS if pattern.matches(unit.source)]
            bindings = catalogue_bindings or {}
            dispositions = catalogue_dispositions or {}
        unit.catalogue_reviewed = []
        unit.catalogue_results = {}
        for pattern_id in matched:
            if pattern_id in dispositions:
                row = dispositions[pattern_id]
                if (not isinstance(row, dict) or row.get("disposition") != "not_applicable"
                        or not row.get("actor") or not row.get("reason")):
                    raise ValueError("catalogue disposition needs actor and reason")
                unit.catalogue_reviewed.append(pattern_id)
                unit.catalogue_results[pattern_id] = {"disposition": deepcopy(row),
                                                       "candidates": [], "cards": []}
                continue
            result = (review_pattern(self.env, unit.source, bindings[pattern_id],
                                     pattern_id=pattern_id, deadline=budget)
                      if pattern_id in bindings else None)
            if result is not None:
                unit.catalogue_results[pattern_id] = result
                for candidate in result["candidates"]:
                    if not any(r.get("meaning_id") == candidate["meaning_id"] for r in unit.readings):
                        unit.readings.append(deepcopy(candidate))
            if (result is None or result.get("pending") or result.get("residual")
                    or result.get("next_cursor") is not None):
                unit.pending.append({"pattern_id": pattern_id, "reason": "catalogue review incomplete"})
            else:
                unit.catalogue_reviewed.append(pattern_id)
        if discourse != "complete":
            unit.pending.append({"reason": "discourse reference unresolved"})
        if parse_outcome == "multiple":
            unit.pending.append({"reason": "multiple source readings unresolved"})
        if (self._operation_budget is not None and budget.expired()
                and not any("deadline" in row.get("reason", "") for row in unit.pending)):
            unit.pending.append({"reason": "operation deadline (8 seconds)"})
        if limit or parse_outcome == "exhausted":
            unit.state, unit.reason = "exhausted", limit or "parser/search exhausted"
        elif vocabulary != "known" or parse_outcome == "zero":
            unit.state = "needs_word" if vocabulary != "known" else "needs_repair"
        elif force != "supported" or check != "checked":
            unit.state = "needs_repair"
        elif discourse != "complete" or parse_outcome == "multiple" or unit.pending:
            unit.state = "reading_review"
        else:
            unit.state = "ready"
        self._event("classify", unit, parse_outcome=parse_outcome, vocabulary=vocabulary,
                    discourse=discourse, force=force, check=check, limit=unit.reason,
                    matched_patterns=matched, requested_pending=deepcopy(requested_pending))
        return unit.state

    def continue_catalogue(self, unit_id, pattern_id, bindings, *, expected_revision=None):
        return self._command("continue_catalogue", unit_id=unit_id, pattern_id=pattern_id,
                             bindings=bindings, expected_revision=expected_revision)

    def _continue_catalogue(self, unit_id, pattern_id, bindings, expected_revision):
        self._expect(expected_revision)
        unit = self.units[unit_id]
        previous = unit.catalogue_results.get(pattern_id)
        if unit.state != "reading_review" or not previous or previous.get("next_cursor") is None:
            raise ValueError("no catalogue page to continue")
        from .ambiguity_patterns import review
        budget = self._budget()
        page = review(self.env, unit.source, bindings, pattern_id=pattern_id,
                      cursor=previous["next_cursor"], deadline=budget)
        if page["candidates"] != previous["candidates"] or page["candidate_count"] != previous["candidate_count"]:
            raise ValueError("catalogue bindings changed between pages")
        previous["cards"].extend(page["cards"])
        previous["comparison_count"] += page["comparison_count"]
        previous["pending"] = [p for p in previous["pending"]
                               if p.get("reason") not in {"page card limit (3)", "operation deadline (8 seconds)"}]
        previous["pending"].extend(page["pending"])
        previous["next_cursor"] = page["next_cursor"]
        previous["residual"] = page["residual"]
        if not previous["pending"] and not previous["residual"] and previous["next_cursor"] is None:
            unit.catalogue_reviewed.append(pattern_id)
            unit.pending = [p for p in unit.pending if p.get("pattern_id") != pattern_id]
        if self._operation_budget is not None and budget.expired() and not previous["pending"]:
            previous["pending"].append({"reason": "operation deadline (8 seconds)"})
            if not any(row.get("pattern_id") == pattern_id for row in unit.pending):
                unit.pending.append({"pattern_id": pattern_id, "reason": "catalogue review incomplete"})
            if pattern_id in unit.catalogue_reviewed:
                unit.catalogue_reviewed.remove(pattern_id)
        unit.state = "reading_review" if unit.pending else "ready"
        self._event("catalogue_page", unit, pattern_id=pattern_id,
                    cursor=page["cursor"], next_cursor=page["next_cursor"])
        return deepcopy(previous)

    def reply(self, unit_id, text: str, *, rejected=(), expected_revision=None):
        started = time.monotonic()
        return self._command("reply", _started_at=started, unit_id=unit_id, text=text, rejected=list(rejected),
                             expected_revision=expected_revision)

    def _reply(self, unit_id, text, rejected, expected_revision):
        self._expect(expected_revision)
        unit = self.units[unit_id]
        if unit.state not in {"needs_word", "needs_repair", "reading_review", "ready", "exhausted"}:
            raise ValueError("no clarification requested")
        if not isinstance(text, str) or not text.strip():
            raise ValueError("empty reply")
        unit.replies += 1
        for row in rejected:
            if not isinstance(row, dict) or not row.get("meaning_id") or not row.get("reason"):
                raise ValueError("rejection needs meaning_id and reason")
            if unit.readings and row["meaning_id"] not in {item["meaning_id"] for item in unit.readings}:
                raise ValueError("rejected meaning is outside the considered reading set")
            unit.rejected.append(deepcopy(row))
        elapsed = self._now() - unit.started
        if unit.replies > MAX_REPLIES or unit.proposals > MAX_PROPOSALS or elapsed > TASK_SECONDS:
            unit.state, unit.reason = "unresolved", "clarification task cap"
        else:
            unit.state = "analysing"
        self._event("reply", unit, text=text, rejected=deepcopy(list(rejected)))
        return unit.state

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

    def _request_proposer(self, unit_id, expected_revision):
        self._expect(expected_revision)
        unit = self.units[unit_id]
        if unit.state not in {"needs_word", "needs_repair", "reading_review", "exhausted"}:
            raise ValueError("proposer request is unavailable in this state")
        if unit.proposals >= MAX_PROPOSALS or self._now() - unit.started >= TASK_SECONDS:
            unit.state, unit.reason = "unresolved", "proposer/task cap"
            self._event("proposer_cap", unit)
            return {"status": "unresolved", "reason": unit.reason}
        unit.proposals += 1
        self._event("proposer_reserved", unit, request=unit.proposals,
                    timeout_seconds=PROPOSAL_SECONDS)
        return None

    def _proposer_result(self, unit_id, reserved_revision, outcome):
        unit = self.units[unit_id]
        reserved = (self.events[reserved_revision - 1]
                    if type(reserved_revision) is int and 1 <= reserved_revision <= len(self.events) else None)
        # Only the latest reservation of this unit, with nothing in between, may be answered.
        if (reserved_revision != self.revision or reserved is None
                or reserved["action"] != "proposer_reserved" or reserved["unit"] != unit_id):
            raise ValueError("proposer result does not answer the latest reservation")
        kind = outcome.get("kind") if isinstance(outcome, dict) else None
        if kind == "failed" and set(outcome) == {"kind", "error"} and isinstance(outcome["error"], str):
            unit.state, unit.reason = "exhausted", f"proposer unavailable: {outcome['error']}"
            self._event("proposer_failed", unit, reason=unit.reason)
            return {"status": "exhausted", "reason": unit.reason}
        if kind == "timed_out" and set(outcome) == {"kind"}:
            unit.state, unit.reason = "exhausted", "proposer request deadline (50 seconds)"
            self._event("proposer_timed_out", unit)
            return {"status": "exhausted", "reason": unit.reason}
        if kind == "suggestion" and set(outcome) == {"kind", "text"} and isinstance(outcome["text"], str):
            # Suggestions are never automatically admitted or selected.
            self._event("proposer_suggested", unit, text=outcome["text"], provenance="untrusted_proposer")
            return {"status": "suggestion", "text": outcome["text"]}
        raise ValueError("invalid proposer outcome")

    def cancel(self, unit_id, *, expected_revision=None):
        return self._command("cancel", unit_id=unit_id, expected_revision=expected_revision)

    def _cancel(self, unit_id, expected_revision):
        self._expect(expected_revision)
        unit = self.units[unit_id]
        if unit.state == "approved":
            raise ValueError("approved unit requires an edit")
        unit.state = "draft"
        self._event("cancel", unit)

    def unresolved(self, unit_id, reason, *, expected_revision=None):
        return self._command("unresolved", unit_id=unit_id, reason=reason,
                             expected_revision=expected_revision)

    def _unresolved(self, unit_id, reason, expected_revision):
        self._expect(expected_revision)
        if not reason:
            raise ValueError("reason required")
        unit = self.units[unit_id]
        self._invalidate(unit_id)
        unit.state, unit.reason = "unresolved", reason
        self._event("unresolved", unit)

    def set_readings(self, unit_id, readings, pending=(), *, expected_revision=None):
        started = time.monotonic()
        return self._command("set_readings", _started_at=started, unit_id=unit_id, readings=list(readings),
                             pending=list(pending), expected_revision=expected_revision)

    def _set_readings(self, unit_id, readings, pending, expected_revision, budget=None):
        self._expect(expected_revision)
        unit = self.units[unit_id]
        if unit.state not in {"reading_review", "ready"}:
            raise ValueError("unit is not in reading review")
        if any(not isinstance(row, dict) for row in pending):
            raise ValueError("pending items must be records")
        supplied = deepcopy(list(readings))
        from ..english import parse_english_with_metadata
        # Every wording is checked inside the operation budget before any change.
        budget = self._budget() if budget is None else budget
        try:
            with budget.guard():
                for row in supplied:
                    if (not isinstance(row, dict) or not row.get("meaning_id")
                            or not isinstance(row.get("wording"), str)):
                        raise ValueError("reading needs checked meaning_id and wording")
                    if not row["wording"].endswith((".", ".\n")):
                        raise ValueError("reading wording is not a writable sentence")
                    parsed = parse_english_with_metadata(self.env, row["wording"].rstrip("\n") + "\n")
                    if (len(parsed.document.formulas) != 1
                            or meaning_id(self.env, parsed.document.formulas[0]) != row["meaning_id"]):
                        raise ValueError("reading wording fails AST correspondence")
        except _Deadline as exc:
            raise ValueError("reading operation deadline") from exc
        existing = {row.get("meaning_id") for row in unit.readings}
        if existing - {row.get("meaning_id") for row in supplied}:
            raise ValueError("considered readings cannot be erased")
        self._invalidate(unit_id)
        unit.readings = supplied
        from .ambiguity_patterns import PATTERNS
        unit.pending.extend(deepcopy(list(pending)))
        unit.pending.extend({"pattern_id": p.id, "reason": "catalogue review incomplete"}
                            for p in PATTERNS if p.matches(unit.source)
                            and p.id not in unit.catalogue_reviewed
                            and not any(row.get("pattern_id") == p.id for row in unit.pending))
        unit.state = "reading_review" if unit.pending else "ready"
        self._event("readings", unit)

    def resolve_pending(self, unit_id, index, *, actor, reason, disposition,
                        wording=None, cited_spans=(),
                        expected_revision=None):
        started = time.monotonic()
        return self._command("resolve_pending", _started_at=started, unit_id=unit_id, index=index, actor=actor,
                             reason=reason, disposition=disposition, wording=wording,
                             cited_spans=list(cited_spans), expected_revision=expected_revision)

    def _resolve_pending(self, unit_id, index, actor, reason, disposition, wording,
                         cited_spans, expected_revision):
        self._expect(expected_revision)
        unit = self.units[unit_id]
        if unit.state != "reading_review" or not actor or not reason:
            raise ValueError("checked pending resolution requires actor and reason")
        if type(index) is not int or not 0 <= index < len(unit.pending):
            raise ValueError("unknown pending item")
        row = unit.pending[index]
        if row.get("pattern_id") and disposition == "not_applicable":
            result = unit.catalogue_results.get(row["pattern_id"])
            if result and (result.get("cards") or result.get("candidates")):
                raise ValueError("checked catalogue readings cannot be dismissed as not applicable")
            unit.catalogue_results[row["pattern_id"]] = {"disposition": {"actor": actor,
                "reason": reason, "disposition": disposition}, "cards": [], "candidates": []}
            unit.catalogue_reviewed.append(row["pattern_id"])
        elif disposition != "resolved" or row.get("pattern_id"):
            raise ValueError("catalogue comparison requires completion, not dismissal")
        else:
            if not wording or not cited_spans:
                raise ValueError("resolution needs a checked rewrite and cited spans")
            from ..english import parse_english_with_metadata
            if not isinstance(wording, str) or not wording.endswith((".", ".\n")):
                raise ValueError("resolution rewrite is not writable")
            try:
                with self._budget().guard():
                    parsed = parse_english_with_metadata(self.env, wording.rstrip("\n") + "\n")
                    if len(parsed.document.formulas) != 1:
                        raise ValueError("resolution needs one meaning")
                    formula = parsed.document.formulas[0]
                    checked_wording(self.env, wording, formula)
                    mid = meaning_id(self.env, formula)
            except _Deadline as exc:
                raise ValueError("resolution operation deadline") from exc
            if not any(item.get("meaning_id") == mid for item in unit.readings):
                unit.readings.append({"meaning_id": mid, "wording": wording, "name": "resolution"})
        unit.pending.pop(index)
        unit.state = "reading_review" if unit.pending else "ready"
        self._event("resolve_pending", unit, item=row, actor=actor,
                    reason=reason, disposition=disposition, wording=wording,
                    cited_spans=deepcopy(list(cited_spans)))

    def record_narrowing(self, unit_id, *, keeps, actor, reason, cited_spans,
                         document=None, expected_revision=None):
        """The W2 document is external; the ledger records that W2 accepted it."""
        started = time.monotonic()
        self._document = document
        try:
            return self._command("record_narrowing", _started_at=started, unit_id=unit_id, keeps=list(keeps), actor=actor,
                                 reason=reason, cited_spans=cited_spans,
                                 expected_revision=expected_revision)
        finally:
            self._document = None

    def _record_narrowing(self, unit_id, keeps, actor, reason, cited_spans, expected_revision):
        self._expect(expected_revision)
        unit = self.units[unit_id]
        ids = {row["meaning_id"] for row in unit.readings}
        kept = list(keeps)
        if (unit.mode != "translation" or unit.state not in {"ready", "reading_review"}
                or not ids or not kept or any(not isinstance(k, str) for k in kept)
                or not set(kept) <= ids or not actor or not reason
                or not isinstance(cited_spans, list) or not cited_spans
                or any(not isinstance(span, dict) or type(span.get("start")) is not int
                       or type(span.get("end")) is not int or not 0 <= span["start"] < span["end"] <= len(unit.source)
                       for span in cited_spans)
                or len(set(kept)) != len(kept)):
            raise ValueError("invalid attributed narrowing")
        record = {"id": f"{unit.id}:narrowing:{len(unit.narrowings)+1}",
                  "set_id": unit.id, "set_version": self.versions["reading_set"],
                  "source_digest": _digest(unit.source),
                  "reading_set_digest": _digest(sorted(ids)),
                  "keeps": kept, "actor": actor, "reason": reason,
                  "cited_spans": deepcopy(cited_spans)}
        record["document_unit"] = {"id": record["id"], "source": unit.source,
                                   "anchor": deepcopy(cited_spans), "kind": "meta",
                                   "meaning_status": "reviewed", "support": [unit.id]}
        observed = self._observed
        if observed.replay:
            if observed._external[:1] == ["w2:accepted"]:
                observed.external.append(observed._external.pop(0))
        elif self.document_adapter is not None:
            document = self._document
            if document is None:
                raise ValueError("W2 document required for attributed narrowing")
            checked = self.document_adapter.add_unit(document, anchor=deepcopy(cited_spans),
                kind="meta", meaning_status="reviewed", support=[unit.id])
            if checked is False or (isinstance(checked, dict) and checked.get("valid") is False):
                raise ValueError("W2 rejected narrowing document unit")
            result = self.document_adapter.narrow(document if checked is None else checked, set_id=unit.id,
                set_version=self.versions["reading_set"], keeps=kept, actor=actor,
                reason=reason, cited_spans=deepcopy(cited_spans))
            if result is False or (isinstance(result, dict) and
                                   (result.get("valid") is False or result.get("status") == "rejected")):
                raise ValueError("W2 rejected narrowing")
            observed.external.append("w2:accepted")
        unit.narrowings.append(record)
        self._event("narrowing", unit, narrowing=deepcopy(record))
        return deepcopy(record)

    def _catalogue_complete(self, unit):
        from .ambiguity_patterns import PATTERNS
        matched = {pattern.id for pattern in PATTERNS if pattern.matches(unit.source)}
        if matched - set(unit.catalogue_reviewed):
            raise ValueError("catalogue review is incomplete")
        for pattern_id in matched:
            result = unit.catalogue_results.get(pattern_id)
            if result is None or result.get("pending") or result.get("residual") or result.get("next_cursor") is not None:
                raise ValueError("catalogue review is incomplete")
            disposition = result.get("disposition")
            if disposition is not None and (disposition.get("disposition") != "not_applicable"
                                            or not disposition.get("actor") or not disposition.get("reason")):
                raise ValueError("catalogue disposition is invalid")

    def approve(self, unit_id, formula, *, actor, paraphrase, presentation, situation,
                rejected=(), narrowing=None, expected_revision=None):
        started = time.monotonic()
        return self._command("approve", _started_at=started, unit_id=unit_id,
                             formula=formula_to_data(self.env, formula),
                             actor=actor, paraphrase=paraphrase, presentation=presentation,
                             situation=situation, rejected=list(rejected), narrowing=narrowing,
                             expected_revision=expected_revision)

    def _approve(self, unit_id, formula, actor, paraphrase, presentation, situation,
                 rejected, narrowing, expected_revision, budget=None):
        self._expect(expected_revision)
        unit = self.units[unit_id]
        if unit.state != "ready" or unit.pending:
            raise ValueError("reading review is incomplete")
        self._catalogue_complete(unit)
        if self._now() - unit.started >= TASK_SECONDS or unit.replies > MAX_REPLIES:
            unit.state, unit.reason = "unresolved", "clarification task cap"
            self._event("task_cap", unit)
            raise ValueError("clarification task cap")
        # One budget covers every step, including dependency revalidation.
        budget = self._budget() if budget is None else budget
        try:
            with budget.guard():
                outcome = self._approval(unit_id, formula_from_data(self.env, formula), actor=actor,
                                         paraphrase=paraphrase, presentation=presentation,
                                         situation=situation, rejected=rejected,
                                         narrowing=narrowing, budget=budget)
            if budget.expired():
                raise ValueError("approval operation deadline")
        except _Deadline as exc:
            raise ValueError("approval operation deadline") from exc
        for key, value in outcome.items():
            setattr(unit, key, value)
        unit.state = "approved"
        self._event("approve", unit, approval_digest=unit.approval["digest"])
        return deepcopy(unit.approval)

    def _approval(self, unit_id, formula, *, actor, paraphrase, presentation, situation,
                  rejected, narrowing, budget):
        """Every approval obligation, computed from derived state without mutating it.

        Returns the unit fields an approval sets. Runs inside ``budget``.
        """
        from ..english import parse_english_with_metadata
        from ..background import background, validate_background
        unit = self.units[unit_id]
        if unit.pending:
            raise ValueError("reading review is incomplete")
        self._catalogue_complete(unit)
        for dependency in unit.dependencies:
            with budget.guard():
                valid = (self.units[dependency].state == "approved"
                         and self._approval_valid(dependency, budget))
            if not valid:
                raise ValueError("dependent unit is not approved")
        if not all((actor, paraphrase, presentation)) or not isinstance(situation, dict):
            raise ValueError("actor, paraphrase, presentation and checked situation required")
        check_formula(self.env, formula)
        checked_wording(self.env, presentation, formula)
        checked_wording(self.env, paraphrase, formula)
        model = FiniteModel.from_dict(self.env, situation)
        validate_background(self.env, model)
        if any(evaluate(self.env, premise.formula, model, trace=False).value is not True
               for premise in background(self.env)):
            raise ValueError("example situation violates Background")
        checked = evaluate(self.env, formula, model, trace=False)
        if checked.status != "Satisfied" or checked.value is not True:
            raise ValueError("example situation does not satisfy selected meaning")
        mid = meaning_id(self.env, formula)
        alternatives = set()
        for result in unit.catalogue_results.values():
            for candidate in result.get("candidates", []):
                wording = candidate["wording"]
                if not wording.endswith((".", ".\n")):
                    raise ValueError("catalogue wording is not writable")
                parsed = parse_english_with_metadata(self.env, wording.rstrip("\n") + "\n")
                if (len(parsed.document.formulas) != 1 or
                        meaning_id(self.env, parsed.document.formulas[0]) != candidate["meaning_id"]):
                    raise ValueError("catalogue wording changed meaning")
                alternatives.add(candidate["meaning_id"])
            for card in result.get("cards", []):
                if (len(card["paraphrases"]) != 2 or len(card["meaning_ids"]) != 2
                        or len(card["values"]) != 2
                        or set(card["meaning_ids"]) - alternatives):
                    raise ValueError("card reading set is invalid")
                card_model = FiniteModel.from_dict(self.env, card["model"])
                validate_background(self.env, card_model)
                if any(evaluate(self.env, premise.formula, card_model, trace=False).value is not True
                       for premise in background(self.env)):
                    raise ValueError("card situation violates Background")
                values = []
                for wording, candidate_id in zip(card["paraphrases"], card["meaning_ids"]):
                    if not wording.endswith((".", ".\n")):
                        raise ValueError("card wording is not writable")
                    parsed = parse_english_with_metadata(self.env, wording.rstrip("\n") + "\n")
                    if len(parsed.document.formulas) != 1 or meaning_id(self.env, parsed.document.formulas[0]) != candidate_id:
                        raise ValueError("card wording changed meaning")
                    values.append(evaluate(self.env, parsed.document.formulas[0], card_model,
                                           trace=False).value)
                if values != card["values"] or len(values) != 2 or values[0] == values[1]:
                    raise ValueError("card situation does not distinguish its readings")
        for row in unit.readings:
            wording = row.get("wording")
            if not isinstance(wording, str) or not wording.endswith((".", ".\n")):
                raise ValueError("considered reading wording is not writable")
            parsed = parse_english_with_metadata(self.env, wording.rstrip("\n") + "\n")
            if len(parsed.document.formulas) != 1 or meaning_id(self.env, parsed.document.formulas[0]) != row.get("meaning_id"):
                raise ValueError("considered reading wording changed meaning")
        proposed_readings = deepcopy(unit.readings)
        considered = {row.get("meaning_id") for row in proposed_readings}
        if alternatives - considered:
            raise ValueError("catalogue readings are missing from the considered set")
        if considered and mid not in considered:
            raise ValueError("selected meaning is outside the considered reading set")
        if not considered:
            proposed_readings.append({"meaning_id": mid, "wording": presentation, "name": "selected"})
            considered = {mid}
        for row in rejected:
            if not isinstance(row, dict) or not row.get("meaning_id") or not row.get("reason"):
                raise ValueError("explicit rejection needs meaning_id and reason")
            if row["meaning_id"] not in considered:
                raise ValueError("rejected meaning is outside the considered reading set")
        all_rejected = deepcopy(unit.rejected) + deepcopy(list(rejected))
        rejected_ids = {row["meaning_id"] for row in all_rejected}
        if unit.mode == "authoring" and (alternatives | considered) - {mid} - rejected_ids:
            raise ValueError("every distinct alternative needs an explicit rejection")
        if unit.mode == "translation" and len(alternatives | considered) > 1:
            record = next((row for row in unit.narrowings if row["id"] == narrowing), None)
            if (record is None or record["keeps"] != [mid]
                    or record["set_version"] != self.versions["reading_set"]
                    or record["source_digest"] != _digest(unit.source)
                    or record["reading_set_digest"] != _digest(sorted(considered))
                    or record.get("document_unit", {}).get("id") != record["id"]
                    or record["document_unit"].get("source") != unit.source
                    or record["document_unit"].get("support") != [unit.id]
                    or record["document_unit"].get("anchor") != record["cited_spans"]
                    or record["document_unit"].get("kind") != "meta"
                    or record["document_unit"].get("meaning_status") != "reviewed"
                    or not isinstance(record["cited_spans"], list) or not record["cited_spans"]
                    or any(not isinstance(span, dict) or type(span.get("start")) is not int
                           or type(span.get("end")) is not int
                           or not 0 <= span["start"] < span["end"] <= len(unit.source)
                           for span in record["cited_spans"])
                    or not record.get("actor") or not record.get("reason")):
                raise ValueError("translation choice requires a separately recorded cited narrowing")
        elif narrowing is not None and not any(row["id"] == narrowing for row in unit.narrowings):
            raise ValueError("unknown narrowing")
        snapshot = {"unit": unit.id, "source": unit.source, "anchor": unit.anchor,
                    "presentation": presentation, "meaning_id": mid, "paraphrase": paraphrase,
                    "situation": situation, "considered": proposed_readings, "rejected": all_rejected,
                    "catalogue_results": unit.catalogue_results,
                    "narrowing": narrowing, "narrowings": unit.narrowings,
                    "actor": actor, "versions": self.versions,
                    "dependencies": [[d, self.units[d].revision] for d in unit.dependencies]}
        return {"readings": proposed_readings, "meaning_id": mid, "paraphrase": paraphrase,
                "presentation": presentation, "situation": deepcopy(situation),
                "rejected": all_rejected,
                "approval": {"digest": _digest(snapshot), "snapshot": deepcopy(snapshot)}}

    def approval_valid(self, unit_id) -> bool:
        """Replay the ledger and recompute the approval from the replayed state.

        The live state must also equal that replay, so an edited cache never
        reports a valid approval.
        """
        if self._observed is not None:
            raise RuntimeError("approval_valid cannot run inside a command")
        budget = Budget(OPERATION_SECONDS)
        try:
            with budget.guard():
                derived = self._derived(budget)
                return derived._approval_valid(unit_id, budget) and not budget.expired()
        except (ValueError, _Deadline):
            return False

    def _approval_valid(self, unit_id, budget) -> bool:
        unit = self.units.get(unit_id)
        if unit is None or unit.state != "approved" or not isinstance(unit.approval, dict):
            return False
        try:
            with budget.guard():
                from ..english import parse_english_with_metadata
                snap = unit.approval["snapshot"]
                parsed = parse_english_with_metadata(self.env, snap["presentation"].rstrip("\n") + "\n")
                if len(parsed.document.formulas) != 1:
                    return False
                expected = self._approval(unit_id, parsed.document.formulas[0], actor=snap["actor"],
                                          paraphrase=snap["paraphrase"], presentation=snap["presentation"],
                                          situation=snap["situation"], rejected=(),
                                          narrowing=snap["narrowing"], budget=budget)
            return _canonical(expected) == _canonical({key: getattr(unit, key) for key in expected})
        except (KeyError, TypeError, ValueError, IndexError, AttributeError, VEError):
            return False

    def add_unit(self, document, **kwargs):
        if self.document_adapter is None:
            raise RuntimeError("W2 document adapter unavailable")
        return self.document_adapter.add_unit(document, **kwargs)

    def add_reading(self, document, **kwargs):
        if self.document_adapter is None:
            raise RuntimeError("W2 document adapter unavailable")
        return self.document_adapter.add_reading(document, **kwargs)

    def narrow(self, document, **kwargs):
        if self.document_adapter is None:
            raise RuntimeError("W2 document adapter unavailable")
        return self.document_adapter.narrow(document, **kwargs)

    def alias_prompt(self, *, source, target, argument_types, direction, context):
        if self.glossary_adapter is None:
            return {"status": "pending", "reason": "W3 alias admission unavailable",
                    "source": source, "target": target}
        return self.glossary_adapter.propose_alias(source=source, target=target,
            argument_types=argument_types, direction=direction, context=context)


COMMANDS = frozenset({"add", "undo", "edit", "update_versions", "start", "classify",
                      "continue_catalogue", "reply", "request_proposer", "proposer_result",
                      "cancel", "unresolved", "set_readings", "resolve_pending",
                      "record_narrowing", "approve"})
