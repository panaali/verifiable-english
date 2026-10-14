"""The recovery ledger: its records, one command's observations, and the sealed derived state.

Split out of ``ve.assist.recovery`` (AR-9), which re-exports every name here.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass, field
import hashlib
import json
import math
import time

from .ambiguity_patterns import Budget

# @2: the ledger records commands and observations; state is derived by replay.
RECOVERY_VERSION = "ve.assist-recovery@2"


def _digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode()).hexdigest()


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


class _Journal:
    """The derived state of a ``RecoveryService``, its seal, and the events and ledger it writes."""

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

    def to_ledger(self):
        return {"format": RECOVERY_VERSION, "genesis_versions": deepcopy(self.genesis_versions),
                "versions": deepcopy(self.versions), "limits": deepcopy(self.limits),
                "revision": self.revision, "commands": deepcopy(self.commands),
                "events": deepcopy(self.events)}
