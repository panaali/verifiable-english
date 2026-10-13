"""Checking a ``RecoveryService`` against the replay of its ledger, and revalidating approvals.

Split out of ``ve.assist.recovery`` (AR-9). The replay loop itself (``_replay_inner``)
stays in ``recovery`` with the other reviewed exception boundaries. This module calls
``recovery``'s operation deadline and checkers through the service's seams
(``_operation_seconds``, ``_checked_wording``, ``_evaluate``).
"""
from __future__ import annotations

from copy import deepcopy
import json
import time

from ..ast import check_formula
from ..errors import VEError
from ..identity import meaning_id
from ..model import FiniteModel
from .ambiguity_patterns import Budget, _Deadline
from .recovery_journal import DIVERGED, _InvalidLedger, _canonical, _digest


class _Replay:
    """Derivation from the ledger and the approval obligations of a ``RecoveryService``."""

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

    def verify_ledger(self, ledger=None):
        """Replay ``ledger`` (default: this service's) and require it to be this state."""
        budget = Budget(self._operation_seconds())
        try:
            with budget.guard():
                derived = self._derived(budget)
                matches = ledger is None or self._replay(self.env, ledger, budget=budget)._sealed == derived._sealed
                return matches and not budget.expired()
        except (KeyError, TypeError, ValueError, IndexError, AttributeError, RecursionError, _Deadline):
            return False

    def _approval_still_valid(self, unit_id, budget) -> bool:
        try:
            return self._approval_valid(unit_id, budget)
        except _Deadline as exc:
            if exc.budget is not budget:
                raise
            return False

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
        self._checked_wording(self.env, presentation, formula)
        self._checked_wording(self.env, paraphrase, formula)
        model = FiniteModel.from_dict(self.env, situation)
        validate_background(self.env, model)
        if any(self._evaluate(self.env, premise.formula, model, trace=False).value is not True
               for premise in background(self.env)):
            raise ValueError("example situation violates Background")
        checked = self._evaluate(self.env, formula, model, trace=False)
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
                if any(self._evaluate(self.env, premise.formula, card_model, trace=False).value is not True
                       for premise in background(self.env)):
                    raise ValueError("card situation violates Background")
                values = []
                for wording, candidate_id in zip(card["paraphrases"], card["meaning_ids"]):
                    if not wording.endswith((".", ".\n")):
                        raise ValueError("card wording is not writable")
                    parsed = parse_english_with_metadata(self.env, wording.rstrip("\n") + "\n")
                    if len(parsed.document.formulas) != 1 or meaning_id(self.env, parsed.document.formulas[0]) != candidate_id:
                        raise ValueError("card wording changed meaning")
                    values.append(self._evaluate(self.env, parsed.document.formulas[0], card_model,
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
        budget = Budget(self._operation_seconds())
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
