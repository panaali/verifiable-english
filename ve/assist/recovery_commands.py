"""The recovery commands: each public method records one command; its ``_name`` transition derives state.

Split out of ``ve.assist.recovery`` (AR-9), which re-exports every name here. The
proposer request (``request_proposer``) stays in ``recovery`` with the other reviewed
exception boundaries. This module calls ``recovery``'s formula conversions and wording
check through the service's seams (``_formula_to_data``, ``_formula_from_data``,
``_checked_wording``).
"""
from __future__ import annotations

from contextlib import nullcontext
from copy import deepcopy
import time
from typing import Protocol

from ..identity import meaning_id
from .ambiguity_patterns import _Deadline
from .recovery_journal import Unit, _digest

MAX_REPLIES = 8
TASK_SECONDS = 300
MAX_PROPOSALS = 2
PROPOSAL_SECONDS = 50
STATES = frozenset({"draft", "analysing", "needs_word", "needs_repair",
                    "reading_review", "ready", "approved", "exhausted", "stale", "unresolved"})


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


COMMANDS = frozenset({"add", "undo", "edit", "update_versions", "start", "classify",
                      "continue_catalogue", "reply", "request_proposer", "proposer_result",
                      "cancel", "unresolved", "set_readings", "resolve_pending",
                      "record_narrowing", "approve"})


class _Commands:
    """The commands and transitions of a ``RecoveryService``."""

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
            self._approve(unit_id, self._formula_to_data(self.env, formula), snap["actor"], snap["paraphrase"],
                          snap["presentation"], snap["situation"], snap["rejected"], snap["narrowing"], None,
                          budget=budget)
        except _Deadline as exc:
            if exc.budget is not budget:
                raise
            unit.state = "stale"
            self._event("undo_requires_review", unit)
        except (ValueError, KeyError, IndexError):
            unit.state = "stale"
            self._event("undo_requires_review", unit)
        return unit

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
            if exc.budget is not budget:
                raise
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
            budget = self._budget()
            try:
                with budget.guard():
                    parsed = parse_english_with_metadata(self.env, wording.rstrip("\n") + "\n")
                    if len(parsed.document.formulas) != 1:
                        raise ValueError("resolution needs one meaning")
                    formula = parsed.document.formulas[0]
                    self._checked_wording(self.env, wording, formula)
                    mid = meaning_id(self.env, formula)
            except _Deadline as exc:
                if exc.budget is not budget:
                    raise
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

    def approve(self, unit_id, formula, *, actor, paraphrase, presentation, situation,
                rejected=(), narrowing=None, expected_revision=None):
        started = time.monotonic()
        return self._command("approve", _started_at=started, unit_id=unit_id,
                             formula=self._formula_to_data(self.env, formula),
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
                outcome = self._approval(unit_id, self._formula_from_data(self.env, formula), actor=actor,
                                         paraphrase=paraphrase, presentation=presentation,
                                         situation=situation, rejected=rejected,
                                         narrowing=narrowing, budget=budget)
            if budget.expired():
                raise ValueError("approval operation deadline")
        except _Deadline as exc:
            if exc.budget is not budget:
                raise
            raise ValueError("approval operation deadline") from exc
        for key, value in outcome.items():
            setattr(unit, key, value)
        unit.state = "approved"
        self._event("approve", unit, approval_digest=unit.approval["digest"])
        return deepcopy(unit.approval)

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
