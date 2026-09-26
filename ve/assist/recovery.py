"""Revisioned recovery and meaning-approval service for W8 consumers.

This layer does not certify proofs or source fidelity. Adapters supply the W2
document schema and W3 alias admission when those interfaces are available.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
import hashlib
import json
import time
from typing import Protocol

from ..ast import check_formula
from ..evaluate import evaluate
from ..model import FiniteModel
from ..identity import meaning_id
from .ambiguity_patterns import CATALOGUE_VERSION, OPERATION_SECONDS

RECOVERY_VERSION = "ve.assist-recovery@1"
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
    pending: list[dict] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    approval: dict | None = None
    reason: str | None = None
    replies: int = 0
    proposals: int = 0
    started: float = field(default_factory=time.monotonic)


class RecoveryService:
    """Single writer API. All changes append a revisioned event to the ledger."""
    def __init__(self, env, *, grammar_version: str, glossary_version: str,
                 reading_set_version: str, document_adapter: DocumentAdapter | None = None,
                 glossary_adapter: GlossaryAdapter | None = None):
        self.env = env
        self.versions = {"grammar": grammar_version, "environment": env.environment_id,
                         "glossary": glossary_version, "catalogue": CATALOGUE_VERSION,
                         "reading_set": reading_set_version, "recovery": RECOVERY_VERSION}
        self.document_adapter = document_adapter
        self.glossary_adapter = glossary_adapter
        self.units: dict[str, Unit] = {}
        self.events: list[dict] = []
        self.revision = 0

    def _event(self, action, unit: Unit, **detail):
        self.revision += 1
        unit.revision = self.revision
        event = {"revision": self.revision, "action": action, "unit": unit.id,
                 "state": unit.state, "source_digest": _digest(unit.source),
                 "versions": deepcopy(self.versions), **detail}
        self.events.append(event)
        return event

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

    def add(self, unit_id: str, source: str, anchor: dict, *, mode="authoring", dependencies=()):
        if unit_id in self.units or not source or mode not in {"authoring", "translation"}:
            raise ValueError("invalid or duplicate unit")
        if any(parent not in self.units for parent in dependencies):
            raise ValueError("unknown dependency")
        unit = Unit(unit_id, source, deepcopy(anchor), mode=mode, dependencies=list(dependencies))
        self.units[unit_id] = unit
        self._event("add", unit)
        return unit

    def edit(self, unit_id, *, source=None, anchor=None, presentation=None):
        unit = self.units[unit_id]
        self._invalidate(unit_id)
        if source is not None:
            unit.source = source
        if anchor is not None:
            unit.anchor = deepcopy(anchor)
        if presentation is not None:
            unit.presentation = presentation
        unit.state = "draft"
        unit.meaning_id = None
        unit.readings.clear()
        unit.pending.clear()
        unit.started = time.monotonic()
        self._event("edit", unit)
        return unit

    def update_versions(self, **versions):
        if set(versions) - set(self.versions):
            raise ValueError("unknown version field")
        changed = any(self.versions[k] != v for k, v in versions.items())
        self.versions.update(versions)
        if changed:
            for unit_id in list(self.units):
                self._invalidate(unit_id)

    def start(self, unit_id):
        unit = self.units[unit_id]
        if unit.state not in {"draft", "stale", "unresolved", "exhausted"}:
            raise ValueError("unit cannot start analysis from this state")
        unit.state = "analysing"
        unit.started = time.monotonic()
        self._event("start", unit)

    def classify(self, unit_id, *, parse_outcome, vocabulary="known", discourse="complete",
                 force="supported", check="checked", pending=(), limit=None):
        unit = self.units[unit_id]
        if unit.state != "analysing":
            raise ValueError("analyse first")
        if parse_outcome not in {"zero", "one", "multiple", "exhausted"}:
            raise ValueError("invalid parse outcome")
        unit.pending = list(pending)
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
                    discourse=discourse, force=force, check=check, limit=unit.reason)
        return unit.state

    def reply(self, unit_id, text: str, *, proposer=False):
        unit = self.units[unit_id]
        if unit.state not in {"needs_word", "needs_repair", "reading_review", "exhausted"}:
            raise ValueError("no clarification requested")
        if not text.strip():
            raise ValueError("empty reply")
        unit.replies += 1
        unit.proposals += int(proposer)
        elapsed = time.monotonic() - unit.started
        if unit.replies > MAX_REPLIES or unit.proposals > MAX_PROPOSALS or elapsed > TASK_SECONDS:
            unit.state, unit.reason = "unresolved", "clarification task cap"
        else:
            unit.state = "analysing"
        self._event("reply", unit, proposer=proposer)
        return unit.state

    def cancel(self, unit_id):
        unit = self.units[unit_id]
        if unit.state == "approved":
            raise ValueError("approved unit requires an edit")
        unit.state = "draft"
        self._event("cancel", unit)

    def unresolved(self, unit_id, reason):
        if not reason:
            raise ValueError("reason required")
        unit = self.units[unit_id]
        self._invalidate(unit_id)
        unit.state, unit.reason = "unresolved", reason
        self._event("unresolved", unit)

    def set_readings(self, unit_id, readings, pending=()):
        unit = self.units[unit_id]
        if unit.state not in {"reading_review", "ready"}:
            raise ValueError("unit is not in reading review")
        self._invalidate(unit_id)
        unit.readings = deepcopy(list(readings))
        unit.pending = deepcopy(list(pending))
        unit.state = "reading_review" if unit.pending else "ready"
        self._event("readings", unit)

    def approve(self, unit_id, formula, *, actor, paraphrase, presentation, situation,
                rejected=(), narrowing=None):
        unit = self.units[unit_id]
        if unit.state != "ready" or unit.pending:
            raise ValueError("reading review is incomplete")
        if unit.mode == "translation" and len(unit.readings) > 1 and narrowing is None:
            raise ValueError("translation choice requires a cited narrowing")
        if any(self.units[d].state in {"stale", "unresolved"} for d in unit.dependencies):
            raise ValueError("dependent unit is stale or unresolved")
        if not all((actor, paraphrase, presentation)) or not isinstance(situation, dict):
            raise ValueError("actor, paraphrase, presentation and checked situation required")
        check_formula(self.env, formula)
        from ..english import parse_english_with_metadata
        parsed = parse_english_with_metadata(self.env, presentation.rstrip(".\n") + ".\n")
        if len(parsed.document.formulas) != 1 or parsed.document.formulas[0] != formula:
            raise ValueError("presentation fails full English derivation/AST correspondence")
        model = FiniteModel.from_dict(self.env, situation)
        checked = evaluate(self.env, formula, model, trace=False)
        if checked.status != "Satisfied" or checked.value is not True:
            raise ValueError("example situation does not satisfy selected meaning")
        mid = meaning_id(self.env, formula)
        unit.meaning_id = mid
        unit.paraphrase, unit.presentation, unit.situation = paraphrase, presentation, deepcopy(situation)
        unit.rejected = deepcopy(list(rejected))
        snapshot = {"unit": unit.id, "source": unit.source, "anchor": unit.anchor,
                    "presentation": presentation, "meaning_id": mid, "paraphrase": paraphrase,
                    "situation": situation, "considered": unit.readings, "rejected": unit.rejected,
                    "narrowing": narrowing, "actor": actor, "versions": self.versions,
                    "dependencies": [(d, self.units[d].revision) for d in unit.dependencies]}
        unit.approval = {"digest": _digest(snapshot), "snapshot": deepcopy(snapshot)}
        unit.state = "approved"
        self._event("approve", unit, approval_digest=unit.approval["digest"])
        return deepcopy(unit.approval)

    def approval_valid(self, unit_id) -> bool:
        unit = self.units[unit_id]
        if unit.state != "approved" or unit.approval is None:
            return False
        snap = unit.approval["snapshot"]
        return (snap["source"] == unit.source and snap["anchor"] == unit.anchor
                and snap["presentation"] == unit.presentation and snap["meaning_id"] == unit.meaning_id
                and snap["versions"] == self.versions
                and snap["dependencies"] == [(d, self.units[d].revision) for d in unit.dependencies]
                and _digest(snap) == unit.approval["digest"])

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
