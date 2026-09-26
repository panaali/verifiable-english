"""Revisioned recovery and meaning-approval service for W8 consumers.

This layer does not certify proofs or source fidelity. Adapters supply the W2
document schema and W3 alias admission when those interfaces are available.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass, field
import hashlib
import json
import time
from typing import Protocol

from ..ast import check_formula
from ..errors import VEError
from ..evaluate import evaluate
from ..model import FiniteModel
from ..identity import meaning_id
from .ambiguity_patterns import (CATALOGUE_VERSION, OPERATION_SECONDS, SEARCH_LIMITS,
                                 MAX_CANDIDATES, MAX_COMPARISONS, MAX_CARDS, checked_wording)

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


class RecoveryService:
    """Single writer API. All changes append a revisioned event to the ledger."""
    def __init__(self, env, *, grammar_version: str, glossary_version: str,
                 reading_set_version: str, document_adapter: DocumentAdapter | None = None,
                 glossary_adapter: GlossaryAdapter | None = None):
        self.env = env
        self.versions = {"grammar": grammar_version, "environment": env.environment_id,
                         "glossary": glossary_version, "catalogue": CATALOGUE_VERSION,
                         "reading_set": reading_set_version, "recovery": RECOVERY_VERSION}
        self.limits = {**SEARCH_LIMITS, "operation_seconds": OPERATION_SECONDS,
                       "max_candidates": MAX_CANDIDATES, "max_comparisons": MAX_COMPARISONS,
                       "max_cards": MAX_CARDS, "max_replies": MAX_REPLIES,
                       "task_seconds": TASK_SECONDS, "max_proposals": MAX_PROPOSALS,
                       "proposal_seconds": PROPOSAL_SECONDS}
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
                 "versions": deepcopy(self.versions), "limits": deepcopy(self.limits),
                 "unit_snapshot": self._snapshot(unit),
                 "previous_digest": self.events[-1]["event_digest"] if self.events else None,
                 **detail}
        event["event_digest"] = _digest(event)
        self.events.append(event)
        return event

    @staticmethod
    def _snapshot(unit):
        return asdict(unit)

    def _expect(self, expected_revision):
        if expected_revision is not None and expected_revision != self.revision:
            raise ValueError("stale recovery revision")

    @classmethod
    def from_ledger(cls, env, ledger, *, document_adapter=None, glossary_adapter=None):
        versions = ledger["versions"]
        service = cls(env, grammar_version=versions["grammar"],
                      glossary_version=versions["glossary"],
                      reading_set_version=versions["reading_set"],
                      document_adapter=document_adapter, glossary_adapter=glossary_adapter)
        if ledger.get("versions") != service.versions or ledger.get("limits") != service.limits:
            raise ValueError("recovery ledger versions or limits changed")
        service.events = deepcopy(ledger["events"])
        service.revision = ledger["revision"]
        for event in service.events:
            service.units[event["unit"]] = Unit(**deepcopy(event["unit_snapshot"]))
        if not service.verify_ledger():
            raise ValueError("invalid recovery ledger")
        return service

    def to_ledger(self):
        return {"format": RECOVERY_VERSION, "versions": deepcopy(self.versions),
                "limits": deepcopy(self.limits),
                "revision": self.revision, "events": deepcopy(self.events)}

    def verify_ledger(self, ledger=None):
        try:
            return self._verify_ledger(ledger)
        except (KeyError, TypeError, ValueError, IndexError, VEError):
            return False

    def _verify_ledger(self, ledger=None):
        ledger = self.to_ledger() if ledger is None else ledger
        if (ledger.get("format") != RECOVERY_VERSION or ledger.get("versions") != self.versions
                or ledger.get("limits") != self.limits):
            return False
        events = ledger.get("events")
        if type(events) is not list or ledger.get("revision") != len(events):
            return False
        previous = None
        history = RecoveryService(self.env, grammar_version=self.versions["grammar"],
            glossary_version=self.versions["glossary"],
            reading_set_version=self.versions["reading_set"])
        for number, event in enumerate(events, 1):
            raw = {k: v for k, v in event.items() if k != "event_digest"}
            if (event.get("revision") != number or event.get("previous_digest") != previous
                    or event.get("event_digest") != _digest(raw)
                    or event.get("source_digest") != _digest(event["unit_snapshot"]["source"])):
                return False
            history.versions = deepcopy(event["versions"])
            history.units[event["unit"]] = Unit(**deepcopy(event["unit_snapshot"]))
            if history.units[event["unit"]].state == "approved" and not history.approval_valid(event["unit"]):
                return False
            previous = event["event_digest"]
        latest = {e["unit"]: e["unit_snapshot"] for e in events}
        if latest != {k: self._snapshot(v) for k, v in self.units.items()}:
            return False
        return all(self.approval_valid(k) for k, u in self.units.items() if u.state == "approved")

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
        self._expect(expected_revision)
        if unit_id in self.units or not source or mode not in {"authoring", "translation"}:
            raise ValueError("invalid or duplicate unit")
        if any(parent not in self.units for parent in dependencies):
            raise ValueError("unknown dependency")
        unit = Unit(unit_id, source, deepcopy(anchor), mode=mode, dependencies=list(dependencies))
        self.units[unit_id] = unit
        self._event("add", unit)
        return unit

    def word_prompt(self, *, term, accepted_prefix, expected, registered):
        return {"term": term, "accepted_prefix": accepted_prefix,
                "expected_construction": expected,
                "nearest_registered_wordings": nearest_wordings(term, registered),
                "prefix_is_admitted": False}

    def undo(self, unit_id: str, target_revision: int, *, expected_revision=None):
        self._expect(expected_revision)
        """Restore an earlier snapshot as a new revision; revalidate its approval."""
        prior = next((e["unit_snapshot"] for e in self.events
                      if e["unit"] == unit_id and e["revision"] == target_revision), None)
        if prior is None:
            raise ValueError("unknown unit revision")
        old_approval = deepcopy(prior["approval"])
        current = self.units[unit_id]
        if (old_approval is not None and current.approval == old_approval
                and current.source == prior["source"] and current.anchor == prior["anchor"]
                and current.presentation == prior["presentation"] and self.approval_valid(unit_id)):
            self._event("undo", current, target_revision=target_revision)
            return current
        unit = self.edit(unit_id, source=prior["source"], anchor=prior["anchor"],
                         presentation=prior["presentation"])
        self._event("undo", unit, target_revision=target_revision)
        if old_approval is None:
            return unit
        snap = old_approval["snapshot"]
        try:
            from ..english import parse_english_with_metadata
            parsed = parse_english_with_metadata(self.env, snap["presentation"].rstrip(".\n") + ".\n")
            formula = parsed.document.formulas[0]
            if len(parsed.document.formulas) != 1 or meaning_id(self.env, formula) != snap["meaning_id"]:
                raise ValueError("restored meaning changed")
            unit.readings = deepcopy(snap["considered"])
            self.start(unit_id)
            self.classify(unit_id, parse_outcome="one")
            self.approve(unit_id, formula, actor=snap["actor"], paraphrase=snap["paraphrase"],
                         presentation=snap["presentation"], situation=snap["situation"],
                         rejected=snap["rejected"], narrowing=snap["narrowing"])
        except (ValueError, KeyError, IndexError):
            unit.state = "stale"
            self._event("undo_requires_review", unit)
        return unit

    def edit(self, unit_id, *, source=None, anchor=None, presentation=None, expected_revision=None):
        self._expect(expected_revision)
        unit = self.units[unit_id]
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
        self._expect(expected_revision)
        if set(versions) - set(self.versions):
            raise ValueError("unknown version field")
        changed = any(self.versions[k] != v for k, v in versions.items())
        self.versions.update(versions)
        if changed:
            for unit_id in list(self.units):
                self._invalidate(unit_id)

    def start(self, unit_id, *, expected_revision=None):
        self._expect(expected_revision)
        unit = self.units[unit_id]
        if unit.state not in {"draft", "stale", "unresolved", "exhausted"}:
            raise ValueError("unit cannot start analysis from this state")
        unit.state = "analysing"
        if time.time() - unit.started >= TASK_SECONDS or unit.replies > MAX_REPLIES:
            unit.state, unit.reason = "unresolved", "clarification task cap"
            self._event("task_cap", unit)
            return unit.state
        self._event("start", unit)

    def classify(self, unit_id, *, parse_outcome, vocabulary="known", discourse="complete",
                 force="supported", check="checked", pending=(), limit=None,
                 catalogue_bindings=None, catalogue_dispositions=None, expected_revision=None):
        self._expect(expected_revision)
        unit = self.units[unit_id]
        if unit.state != "analysing":
            raise ValueError("analyse first")
        if parse_outcome not in {"zero", "one", "multiple", "exhausted"}:
            raise ValueError("invalid parse outcome")
        from .ambiguity_patterns import PATTERNS, review as review_pattern
        # A restart may refresh catalogue work, but cannot erase an unresolved
        # discourse or author clarification recorded by an earlier attempt.
        unit.pending = ([deepcopy(row) for row in unit.pending if not row.get("pattern_id")]
                        + deepcopy(list(pending)))
        matched = [pattern.id for pattern in PATTERNS if pattern.matches(unit.source)]
        bindings = catalogue_bindings or {}
        dispositions = catalogue_dispositions or {}
        stop = time.monotonic() + OPERATION_SECONDS
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
                                     pattern_id=pattern_id, deadline=stop)
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
                    matched_patterns=matched)
        return unit.state

    def continue_catalogue(self, unit_id, pattern_id, bindings, *, expected_revision=None):
        self._expect(expected_revision)
        unit = self.units[unit_id]
        previous = unit.catalogue_results.get(pattern_id)
        if unit.state != "reading_review" or not previous or previous.get("next_cursor") is None:
            raise ValueError("no catalogue page to continue")
        from .ambiguity_patterns import review
        page = review(self.env, unit.source, bindings, pattern_id=pattern_id,
                      cursor=previous["next_cursor"])
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
        unit.state = "reading_review" if unit.pending else "ready"
        self._event("catalogue_page", unit, pattern_id=pattern_id,
                    cursor=page["cursor"], next_cursor=page["next_cursor"])
        return deepcopy(previous)

    def reply(self, unit_id, text: str, *, rejected=(), expected_revision=None):
        self._expect(expected_revision)
        unit = self.units[unit_id]
        if unit.state not in {"needs_word", "needs_repair", "reading_review", "ready", "exhausted"}:
            raise ValueError("no clarification requested")
        if not text.strip():
            raise ValueError("empty reply")
        unit.replies += 1
        for row in rejected:
            if not isinstance(row, dict) or not row.get("meaning_id") or not row.get("reason"):
                raise ValueError("rejection needs meaning_id and reason")
            if unit.readings and row["meaning_id"] not in {item["meaning_id"] for item in unit.readings}:
                raise ValueError("rejected meaning is outside the considered reading set")
            unit.rejected.append(deepcopy(row))
        elapsed = time.time() - unit.started
        if unit.replies > MAX_REPLIES or unit.proposals > MAX_PROPOSALS or elapsed > TASK_SECONDS:
            unit.state, unit.reason = "unresolved", "clarification task cap"
        else:
            unit.state = "analysing"
        self._event("reply", unit, text=text, rejected=deepcopy(list(rejected)))
        return unit.state

    def request_proposer(self, unit_id, proposer: ProposerAdapter, *, expected_revision=None):
        self._expect(expected_revision)
        """Reserve before calling. Failure stays visible; an explicit retry is a new event."""
        unit = self.units[unit_id]
        if unit.state not in {"needs_word", "needs_repair", "reading_review", "exhausted"}:
            raise ValueError("proposer request is unavailable in this state")
        if unit.proposals >= MAX_PROPOSALS or time.time() - unit.started >= TASK_SECONDS:
            unit.state, unit.reason = "unresolved", "proposer/task cap"
            self._event("proposer_cap", unit)
            return {"status": "unresolved", "reason": unit.reason}
        unit.proposals += 1
        self._event("proposer_reserved", unit, request=unit.proposals,
                    timeout_seconds=PROPOSAL_SECONDS)
        reserved_revision, reserved_source = self.revision, unit.source
        started = time.monotonic()
        try:
            suggestion = proposer.request(reserved_source, timeout_seconds=PROPOSAL_SECONDS)
        except Exception as exc:
            if self.revision != reserved_revision or unit.source != reserved_source:
                return {"status": "stale", "reason": "proposer request superseded"}
            unit.state, unit.reason = "exhausted", f"proposer unavailable: {type(exc).__name__}"
            self._event("proposer_failed", unit, reason=unit.reason)
            return {"status": "exhausted", "reason": unit.reason}
        if self.revision != reserved_revision or unit.source != reserved_source:
            return {"status": "stale", "reason": "proposer request superseded"}
        if time.monotonic() - started > PROPOSAL_SECONDS:
            unit.state, unit.reason = "exhausted", "proposer request deadline (50 seconds)"
            self._event("proposer_timed_out", unit)
            return {"status": "exhausted", "reason": unit.reason}
        # Suggestions are never automatically admitted or selected.
        self._event("proposer_suggested", unit, text=suggestion, provenance="untrusted_proposer")
        return {"status": "suggestion", "text": suggestion}

    def cancel(self, unit_id, *, expected_revision=None):
        self._expect(expected_revision)
        unit = self.units[unit_id]
        if unit.state == "approved":
            raise ValueError("approved unit requires an edit")
        unit.state = "draft"
        self._event("cancel", unit)

    def unresolved(self, unit_id, reason, *, expected_revision=None):
        self._expect(expected_revision)
        if not reason:
            raise ValueError("reason required")
        unit = self.units[unit_id]
        self._invalidate(unit_id)
        unit.state, unit.reason = "unresolved", reason
        self._event("unresolved", unit)

    def set_readings(self, unit_id, readings, pending=(), *, expected_revision=None):
        self._expect(expected_revision)
        unit = self.units[unit_id]
        if unit.state not in {"reading_review", "ready"}:
            raise ValueError("unit is not in reading review")
        self._invalidate(unit_id)
        supplied = deepcopy(list(readings))
        from ..english import parse_english_with_metadata
        for row in supplied:
            if not isinstance(row, dict) or not row.get("meaning_id") or not row.get("wording"):
                raise ValueError("reading needs checked meaning_id and wording")
            if not row["wording"].endswith((".", ".\n")):
                raise ValueError("reading wording is not a writable sentence")
            parsed = parse_english_with_metadata(self.env, row["wording"].rstrip("\n") + "\n")
            if len(parsed.document.formulas) != 1 or meaning_id(self.env, parsed.document.formulas[0]) != row["meaning_id"]:
                raise ValueError("reading wording fails AST correspondence")
        existing = {row.get("meaning_id") for row in unit.readings}
        if existing - {row.get("meaning_id") for row in supplied}:
            raise ValueError("considered readings cannot be erased")
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
        self._expect(expected_revision)
        unit = self.units[unit_id]
        if unit.state != "reading_review" or not actor or not reason:
            raise ValueError("checked pending resolution requires actor and reason")
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
            if not wording.endswith((".", ".\n")):
                raise ValueError("resolution rewrite is not writable")
            parsed = parse_english_with_metadata(self.env, wording.rstrip("\n") + "\n")
            if len(parsed.document.formulas) != 1:
                raise ValueError("resolution needs one meaning")
            formula = parsed.document.formulas[0]
            checked_wording(self.env, wording, formula)
            mid = meaning_id(self.env, formula)
            if not any(item.get("meaning_id") == mid for item in unit.readings):
                unit.readings.append({"meaning_id": mid, "wording": wording, "name": "resolution"})
        unit.pending.pop(index)
        unit.state = "reading_review" if unit.pending else "ready"
        self._event("resolve_pending", unit, item=row, actor=actor,
                    reason=reason, disposition=disposition, wording=wording,
                    cited_spans=deepcopy(list(cited_spans)))

    def record_narrowing(self, unit_id, *, keeps, actor, reason, cited_spans,
                         document=None, expected_revision=None):
        self._expect(expected_revision)
        unit = self.units[unit_id]
        ids = {row["meaning_id"] for row in unit.readings}
        kept = list(keeps)
        if (unit.mode != "translation" or unit.state not in {"ready", "reading_review"}
                or not ids or not kept or not set(kept) <= ids or not actor or not reason
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
        if self.document_adapter is not None:
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
        unit.narrowings.append(record)
        self._event("narrowing", unit, narrowing=deepcopy(record))
        return deepcopy(record)

    def approve(self, unit_id, formula, *, actor, paraphrase, presentation, situation,
                rejected=(), narrowing=None, expected_revision=None):
        self._expect(expected_revision)
        unit = self.units[unit_id]
        if unit.state != "ready" or unit.pending:
            raise ValueError("reading review is incomplete")
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
        if time.time() - unit.started >= TASK_SECONDS or unit.replies > MAX_REPLIES:
            unit.state, unit.reason = "unresolved", "clarification task cap"
            self._event("task_cap", unit)
            raise ValueError("clarification task cap")
        if any(self.units[d].state != "approved" or not self.approval_valid(d)
               for d in unit.dependencies):
            raise ValueError("dependent unit is not approved")
        if not all((actor, paraphrase, presentation)) or not isinstance(situation, dict):
            raise ValueError("actor, paraphrase, presentation and checked situation required")
        check_formula(self.env, formula)
        stop = time.monotonic() + OPERATION_SECONDS
        checked_wording(self.env, presentation, formula)
        checked_wording(self.env, paraphrase, formula)
        if time.monotonic() >= stop:
            raise ValueError("approval operation deadline")
        model = FiniteModel.from_dict(self.env, situation)
        from ..background import background, validate_background
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
                from ..english import parse_english_with_metadata
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
        if time.monotonic() >= stop:
            raise ValueError("approval operation deadline")
        from ..english import parse_english_with_metadata
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
        all_rejected = unit.rejected + deepcopy(list(rejected))
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
        if time.monotonic() >= stop or time.time() - unit.started >= TASK_SECONDS:
            raise ValueError("approval deadline")
        unit.readings = proposed_readings
        unit.meaning_id = mid
        unit.paraphrase, unit.presentation, unit.situation = paraphrase, presentation, deepcopy(situation)
        unit.rejected = all_rejected
        snapshot = {"unit": unit.id, "source": unit.source, "anchor": unit.anchor,
                    "presentation": presentation, "meaning_id": mid, "paraphrase": paraphrase,
                    "situation": situation, "considered": unit.readings, "rejected": unit.rejected,
                    "catalogue_results": unit.catalogue_results,
                    "narrowing": narrowing, "narrowings": unit.narrowings,
                    "actor": actor, "versions": self.versions,
                    "dependencies": [[d, self.units[d].revision] for d in unit.dependencies]}
        unit.approval = {"digest": _digest(snapshot), "snapshot": deepcopy(snapshot)}
        unit.state = "approved"
        self._event("approve", unit, approval_digest=unit.approval["digest"])
        return deepcopy(unit.approval)

    def approval_valid(self, unit_id) -> bool:
        unit = self.units[unit_id]
        if unit.state != "approved" or unit.approval is None:
            return False
        try:
            snap = unit.approval["snapshot"]
            bound = (snap["source"] == unit.source and snap["anchor"] == unit.anchor
                    and snap["presentation"] == unit.presentation and snap["meaning_id"] == unit.meaning_id
                    and snap["paraphrase"] == unit.paraphrase and snap["situation"] == unit.situation
                    and snap["considered"] == unit.readings and snap["rejected"] == unit.rejected
                    and snap["narrowings"] == unit.narrowings
                    and snap["catalogue_results"] == unit.catalogue_results
                    and snap["versions"] == self.versions
                    and snap["dependencies"] == [[d, self.units[d].revision] for d in unit.dependencies]
                    and _digest(snap) == unit.approval["digest"])
        except (KeyError, TypeError, ValueError, IndexError):
            return False
        if not bound:
            return False
        try:
            from ..english import parse_english_with_metadata
            parsed = parse_english_with_metadata(self.env, snap["presentation"].rstrip("\n") + "\n")
            if len(parsed.document.formulas) != 1:
                return False
            replay = RecoveryService(self.env, grammar_version=self.versions["grammar"],
                glossary_version=self.versions["glossary"],
                reading_set_version=self.versions["reading_set"])
            replay.units = deepcopy(self.units)
            selected = replay.units[unit_id]
            selected.state, selected.approval = "ready", None
            selected.started = time.time()
            result = replay.approve(unit_id, parsed.document.formulas[0], actor=snap["actor"],
                paraphrase=snap["paraphrase"], presentation=snap["presentation"],
                situation=snap["situation"], narrowing=snap["narrowing"])
            return result["digest"] == unit.approval["digest"]
        except (KeyError, TypeError, ValueError, IndexError, VEError):
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
