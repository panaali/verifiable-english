"""Reports document view over Lean's checked elaboration.

The reports service owns decoding, identities, elaboration, status and residual
lines. This object only holds the accepted input and constructs Python
containers from the returned rows for callers that need them.
"""
from __future__ import annotations

from copy import deepcopy

from .environment import Environment
from .errors import CheckerUnavailable
from .reports_preflight import prepare
from .reports_route import run_case

class ReportsDocument:
    def __init__(self, environment: Environment, contexts, assessments, units, *,
                 bridges=(), scoped=(), choices=(), open_terms=()):
        self.environment = environment
        self.contexts, self.assessments, bridges, scoped = prepare(
            environment, contexts, assessments, bridges, scoped)
        self.units = deepcopy(units)
        self._document = {"units": self.units, "contexts": deepcopy(contexts), "assessments": deepcopy(assessments),
                          "bridges": deepcopy(bridges), "scoped": deepcopy(scoped),
                          "open_terms": deepcopy(open_terms), "choices": deepcopy(choices)}
        self._environment = environment.to_dict()
        answer = run_case("reports-elaborate", self._environment, self._document)
        self.choices = deepcopy(choices)
        self._answer = answer
        self.envelope = answer["envelope"]
        self.document_id = self.envelope["document_id"]
        self.open_terms = answer["open_terms"]
        self.premises = [row["ast"] for row in answer["premises"]]
        self._meaning_ids = {row["unit"]: row["meaning_id"] for row in answer["meaning_ids"]}
        report_ids = [unit["id"] for unit in self.units if type(unit.get("content")) is dict and
                      set(unit["content"]) & {"report", "assessment", "negated"}]
        if [row["unit"] for row in answer["meaning_ids"]] != report_ids:
            raise CheckerUnavailable("Lean returned report meanings for different units")
        try:
            self.extended_environment = Environment(answer["environment_reports"], _generated_reports=True)
        except Exception as exc:
            raise CheckerUnavailable("Lean accepted a reports environment Python cannot construct") from exc
        if self.extended_environment.environment_id != answer["environment_reports_id"]:
            raise CheckerUnavailable("Lean returned an unbound reports environment")
        self._load_statuses(replay=False)

    def _load_statuses(self, **extra):
        answer = run_case("reports-status", self._environment, self._document, **extra)
        for field, expected in (("units", self.units), ("scoped", self._document["scoped"])):
            if [row["id"] for row in answer[field]] != [row["id"] for row in expected]:
                raise CheckerUnavailable(f"Lean returned report statuses for different {field}")
        self._statuses = answer

    def replay(self):
        self._load_statuses()

    def elaborated(self):
        return {key: value for key, value in self._answer.items()
                if key not in ("id", "status", "environment_reports", "meaning_ids")}

    def route_answer(self):
        return {key: value for key, value in self._answer.items()
                if key not in ("environment_reports", "meaning_ids")}

    def search_payload(self, conclusion=None):
        return {"family": "elaborated-document", "profile": "reports@0", "untrusted": True,
                "environment": self.extended_environment.to_dict(),
                "premises": self.premises, "envelope": self.envelope,
                "open_terms": self.open_terms,
                **({"conclusion": conclusion} if conclusion is not None else {})}

    def statuses(self):
        return {key: self._statuses[key] for key in ("units", "scoped", "document_status")}

    def residual_lines(self):
        return self._statuses["residual_lines"]

    def unit_status(self, unit):
        return next(row["status"] for row in self._statuses["units"] if row["id"] == unit["id"])

    def meaning_id(self, node):
        for unit in self.units:
            if unit.get("content") == node and unit["id"] in self._meaning_ids:
                return self._meaning_ids[unit["id"]]
        return run_case("reports-content", self._environment, self._document, content=node)["meaning_id"]

    def _node(self, node, _label, *, top=False):
        self.meaning_id(node)
        return node
