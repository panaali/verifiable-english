"""The readings routes' shared parts (docs/spec/composition-s2.md 1.1): the search budget, the route base
every route past the first three rows shares, the pending route and the request key of a query."""
from __future__ import annotations

import json
from collections.abc import MutableMapping

from ..errors import CheckerUnavailable


class _LeanBudget(MutableMapping):
    """The readings routes' search budget: Lean's premise-check budget (`ve.search.lean_budget`,
    premise-scale), read on first use. A key set here (a test's zero budget) stands in for Lean's
    until it is deleted; no other key exists."""
    _FIELDS = {"max_steps": "max_proof_steps", "max_domain_size": "max_domain_size",
               "max_models": "max_models", "max_evaluations": "max_evaluations"}

    def __init__(self):
        self._set = {}

    def __getitem__(self, key):
        if key in self._set:
            return self._set[key]
        from ..search import lean_budget
        return getattr(lean_budget(), self._FIELDS[key])

    def __setitem__(self, key, value):
        if key not in self._FIELDS:
            raise KeyError(key)
        self._set[key] = value

    def __delitem__(self, key):
        del self._set[key]

    def __iter__(self):
        return iter(self._FIELDS)

    def __len__(self):
        return len(self._FIELDS)


BUDGET = _LeanBudget()
PENDING = {"status": "UNKNOWN", "reason": "non-assertion reading elaboration pending"}


def _dropped(sets, narrowings, set_id, index):
    """The first narrowing in force (document order) that drops candidate `index` of `set_id`, if any (Lean's
    `droppedBy`; E7, not `DeadReading`)."""
    R = next(R for R in sets if R.id == set_id)
    for narrowing in narrowings:
        if (narrowing["set"], narrowing["version"]) == (R.id, R.version) and \
                R.candidates[index].id not in narrowing["keeps"]:
            return narrowing["id"]
    return None


class _Route:
    """What every route past the first three rows of 1.1 shares: the decoded document, its open sets and the
    compatible choices (at most 64, else None)."""

    def __init__(self, doc):
        from ..readings_route import document_wire
        from ..readings_s1 import Document, S1Environment, wire
        meta = doc["meta"]
        self.doc = doc
        self.row = doc["readings_s2"]
        self.route = self.row["route"]
        self.couplings = list(meta.get("couplings", []))
        self.narrowings = list(meta.get("narrowings", []))
        self.environment = wire(doc["environment"].to_dict())
        units = [{"id": u["id"], "kind": u["kind"], "content": u["content"]} for u in doc["units"]]
        self.document = wire(document_wire(units, meta.get("reading_sets", []), couplings=self.couplings,
                                           narrowings=self.narrowings))
        # Under the unspecified completion (readings-defaults 3) the route's row carries Lean's filled document, and
        # each choice is checked on Lean's `choiceU N c` (`_FilledChoiceDocument`).
        filled = self.row.get("filled")
        self.completion = filled is not None
        self.source = Document(S1Environment(self.environment, filled), self.document, filled)
        self.sets = self.source.sets
        self.choices = None if self.row["choices"] == "over" else [
            {s: i for s, i in choice} for choice in self.row["choices"]]
        self.numbers = {unit["id"]: n for n, unit in enumerate(doc["units"], 1)}

    def lean(self, kind, **fields):
        from ..readings_route import run_lean
        [row] = run_lean([{"id": kind, "kind": kind, "environment": self.environment, "document": self.document,
                           **fields}])
        if row.get("status") != "ok":
            raise CheckerUnavailable(f"ReadingsConformance: Lean refused the {kind} case Python built: "
                                     f"{row.get('error')}")
        return row

    def choice_json(self, choice):
        return [[R.id, choice[R.id]] for R in self.sets]

    def choice_text(self, choice_json):
        versions = {R.id: R.version for R in self.sets}
        return ", ".join(f"{s}@{versions[s]}:{i}" for s, i in choice_json)

    def dropped(self, set_id, index):
        """The narrowing in force that drops candidate `index` of `set_id`, if any (E7, not `DeadReading`)."""
        return _dropped(self.sets, self.narrowings, set_id, index)

    def candidates(self):
        return [(R.id, i) for R in self.sets for i in range(len(R.candidates))]

    def restrictions(self, A=()):
        return (self._ask("conflict", A) if self.route == "superposed" else
                self._verdicts("conflict", assumed=[list(x) for x in A]))["restrictions"]

    def report_fields(self):
        return {}

    def untaken_text(self, A):
        """Lean's `untakenText`: the named readings, as given, that no compatible choice takes."""
        versions = {R.id: R.version for R in self.sets}
        return "ReadingsUnsatisfiable: no compatible reading takes " + ", ".join(
            f"{s}@{versions[s]}:{i}" if s in versions else f"{s}:{i}" for s, i in A)


class Pending(_Route):
    """1.1 row 2: a pending candidate; every verdict across readings is UNKNOWN with today's reason."""

    def __init__(self, doc):  # noqa: D401 - nothing of 1.2 to 1.9 is computed
        self.doc = doc
        self.route = doc["readings_s2"]["route"]

    def premises(self):
        return dict(PENDING)

    def conflict(self, A=()):
        return dict(PENDING)

    def entailment(self, conclusion_ast, premises=(), assumed=None):
        return {"verdict": "UNKNOWN", "route": self.route, "reason": PENDING["reason"]}

    def report_fields(self):
        return {"status": "UNKNOWN: " + PENDING["reason"]}


def _request_key(conclusion_ast, premises, assumed):
    return json.dumps([conclusion_ast, list(premises), None if assumed is None else [list(x) for x in assumed]],
                      sort_keys=True)
