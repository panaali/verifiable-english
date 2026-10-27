"""The enumerated route (4.6; readings-defaults 3.5, RD-3): every verdict is Lean's; Python generates evidence on
each compatible choice's document and relays Lean's answer."""
from __future__ import annotations

import json

from ..errors import CheckerUnavailable, VEError
from .binding import _Frame, _check_answer
from .choice import _ChoiceDocument, _FilledChoiceDocument
from .route import BUDGET, _Route, _request_key
from .superposed import _dead_certificates


_NOT_SUPERPOSABLE = "ReadingsNotSuperposable: "


# ---------------------------------------------------------------------------------------------------------------
# The enumerated route (4.6; readings-defaults 3.5, RD-3)


class Enumerated(_Route):
    """The enumerated route: every verdict is Lean's (`readings-verdicts`, one request per question). Lean
    enumerates the compatible choices taking `assumed`, checks every piece of evidence on the choice's document it
    regenerates, folds the rows, computes the restrictions and the labels an answer uses, and plans its English.
    Python only generates evidence (each choice's document below: conflict packages, witnesses, certificates and
    models, its own untrusted prover and search) and relays Lean's answer; a piece Lean refuses that Python's own
    check accepted is `CheckerUnavailable`, never a verdict."""

    def __init__(self, doc):
        super().__init__(doc)
        self._docs = {}
        self._conflict = {}  # choice key → its conflict packages and witness (inner cases)
        self._premise = {}   # choice key → its certificate of ⊥ or model
        self._dead = None    # the dead readings' certificates, once Lean names the untaken candidates
        self._answers = {}
        self._notes = None   # choice → Lean's notes on its conflict package and witness, once the conflict is asked
        self.requests = {}   # id of an answer → the request it answers

    def _choice(self, choice):
        key = self._key(choice)
        if key not in self._docs:
            self._docs[key] = (_FilledChoiceDocument if self.completion else _ChoiceDocument)(self, choice)
        return self._docs[key]

    def _key(self, choice):
        return tuple(choice[R.id] for R in self.sets)

    @staticmethod
    def _of(choice_json):
        return {s: i for s, i in choice_json}

    def _verdicts(self, question, query=None, **fields):
        """Lean's `readings-verdicts` answer, the evidence generated so far sent with it, checked against the request
        (`_check_answer`); the request is kept beside it (`requests`, by the answer's identity)."""
        from ..readings_route import run_lean
        evidence = []
        for choice in self.choices or []:
            key = self._key(choice)
            pieces = {**self._conflict.get(key, {}), **self._premise.get(key, {}), **(query or {}).get(key, {})}
            if pieces:
                evidence.append({"choice": self.choice_json(choice), **pieces})
        case = {"id": "readings-verdicts", "kind": "readings-verdicts", "environment": self.environment,
                "document": self.document, "question": question, "evidence": evidence, **fields}
        if self._dead is not None:
            case["dead"] = self._dead
        [row] = run_lean([case])
        if row.get("status") != "ok":
            error = row.get("error")
            if isinstance(error, str) and error.startswith("ReadingsUnsatisfiable: "):
                raise VEError(error)
            raise CheckerUnavailable(f"ReadingsConformance: Lean refused the readings-verdicts case Python built: "
                                     f"{error}")
        self.check_answer(row, case)
        if self._notes is not None and any(self._notes[json.dumps(e["choice"])] != _conflict_notes(e)
                                           for e in row["per_choice"]):
            raise CheckerUnavailable("ReadingsConformance: Lean notes a reading's conflict evidence differently from "
                                     "one request to the next")
        self.requests[id(row)] = case
        return row

    def check_answer(self, row, case):
        """`_check_answer` with this route's frame."""
        _check_answer(row, case, self.frame(case))

    def frame(self, case):
        """The frame `case` is answered in: the request's document, Lean's compatible choices (the route's row, bound
        to its request), the completion and the sets its finding names (none on the rights chain)."""
        finding = (self.row.get("finding") or {}).get("text")
        if finding is not None and not finding.startswith(_NOT_SUPERPOSABLE):
            raise CheckerUnavailable("ReadingsConformance: the enumerated route's finding names no sets")
        return _Frame(case, None if self.choices is None else [self.choice_json(c) for c in self.choices],
                      self.completion, [] if finding is None else finding.removeprefix(_NOT_SUPERPOSABLE).split(", "))

    def _conflict_answer(self):
        """The conflict question: each choice's packages, then a witness for every choice Lean leaves without
        CONFLICT-FREE (`readings-choice`'s order of 4.3)."""
        if "conflict" not in self._answers:
            for choice in self.choices or []:
                case = self._choice(choice).conflict_case()
                if case is not None:
                    self._conflict.setdefault(self._key(choice), {})["conflict"] = case
            row = self._verdicts("conflict")
            found = False
            for entry in row["per_choice"]:
                if entry["conflict"] != "CONFLICT-FREE":
                    choice = self._of(entry["choice"])
                    witness = self._choice(choice).witness_case()
                    if witness is not None:
                        self._conflict.setdefault(self._key(choice), {})["witness"] = witness
                        found = True
            final = self._verdicts("conflict") if found else row
            # The witnesses change no package's note (the same packages are sent).
            if [e["evidence"].get("conflict") for e in final["per_choice"]] != \
                    [e["evidence"].get("conflict") for e in row["per_choice"]]:
                raise CheckerUnavailable("ReadingsConformance: Lean notes a reading's conflict packages differently "
                                         "from one request to the next")
            self._notes = {json.dumps(e["choice"]): _conflict_notes(e) for e in final["per_choice"]}
            self._answers["conflict"] = final
        return self._answers["conflict"]

    def conflict(self, A=()):
        if A:
            self._conflict_answer()
            return self._verdicts("conflict", assumed=[list(x) for x in A])["result"]
        return self._conflict_answer()["result"]

    def _free(self):
        return {self._key(self._of(e["choice"])): e["conflict"] == "CONFLICT-FREE"
                for e in self._conflict_answer()["per_choice"]}

    def _premises_answer(self):
        """The premises question: per choice a certificate of ⊥ (only under a CONFLICT-FREE reading, S2a 14.8; the
        quick proof first), else a model, as `premise_status` orders them; then, for the candidates Lean finds no
        compatible choice takes, the dead readings' certificates."""
        if "premises" not in self._answers:
            free = self._free()
            for choice in self.choices or []:
                document, key = self._choice(choice), self._key(choice)
                piece = None
                if free.get(key):
                    piece = document.certificate_case(None, max_steps=min(BUDGET["max_steps"], 128))
                    piece = piece and {"unsat": piece}
                if piece is None:
                    found = document.model_case(None)
                    piece = found and {"model": found}
                if piece is None and free.get(key) and BUDGET["max_steps"] > 128:
                    found = document.certificate_case(None)
                    piece = found and {"unsat": found}
                if piece is not None:
                    self._premise[key] = piece
            row = self._verdicts("premises")
            if row["untaken"] and self._dead is None:
                dead = _dead_certificates(self, [tuple(x) for x in row["untaken"]])
                if dead is not None:
                    self._dead = dead
                    row = self._verdicts("premises")
            self._answers["premises"] = row
        return self._answers["premises"]

    def premises(self):
        return self._premises_answer()["result"]

    def dead_readings(self):
        """Lean's dead readings (1.9): every candidate no compatible choice takes and no narrowing drops, each with
        its certificate; None when one has none or the choices are too many (an incomplete list is never reported)."""
        return self._premises_answer()["dead_readings"]

    def entailment(self, conclusion_ast, premises=(), assumed=None):
        """ALL, SOME, NONE or UNKNOWN across the compatible choices taking `assumed` (4.6), Lean's. A first request
        names the choices and their conflict rows; a certificate or a countermodel is generated for each choice past
        the gate (14.8), and the second request folds them."""
        self._conflict_answer()
        fields = {"premises": list(premises), "conclusion": conclusion_ast}
        if assumed is not None:
            fields["assumed"] = [list(x) for x in assumed]
        row = self._verdicts("query", **fields)
        result = row["result"]
        if "conflict_status" not in result and "budget" not in result:
            query = {}
            for entry in row["per_choice"]:
                choice = self._of(entry["choice"])
                document = self._choice(choice)
                found = document.certificate_case(conclusion_ast, premises)
                if found is not None:
                    query[self._key(choice)] = {"certificate": found}
                    continue
                found = document.model_case(conclusion_ast, premises)
                if found is not None:
                    query[self._key(choice)] = {"countermodel": found}
            if query:
                row = self._verdicts("query", query=query, **fields)
        self._answers[("query", _request_key(conclusion_ast, premises, assumed))] = row
        return row["result"]

    def query_answer(self, conclusion_ast, assumed=None, premises=()):
        """Lean's whole answer to the `entailment` request for this conclusion (its English plan included), asked
        when this route has not asked it yet."""
        key = ("query", _request_key(conclusion_ast, premises, assumed))
        if key not in self._answers:
            self.entailment(conclusion_ast, premises, assumed)
        return self._answers[key]

    def conflict_answer(self):
        return self._conflict_answer()

    def premises_answer(self):
        return self._premises_answer()

    @property
    def base(self):
        """`_core_environment` reads the frame's identity fields from a base environment."""
        return self.source.senv.author_environment()

    def report_fields(self):
        conflict = self.conflict(())
        dead = self.dead_readings()
        return {"status": conflict["status_text"],
                "conflict": {key: value for key, value in conflict.items() if key not in ("status_text", "witnesses")},
                "dead_readings": None if dead is None else [d["finding"] for d in dead]}


def _conflict_notes(entry):
    """A row's notes on its conflict evidence: the same packages and witness get the same notes in every answer."""
    return {name: entry["evidence"].get(name) for name in ("conflict", "witness")}
