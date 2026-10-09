"""Readings with their own vocabulary through `ve document` (docs/spec/readings-defaults.md 1.9, 1.10, 2.4, 3, 4.5;
plan RD-4b).

A document whose reading sets carry `companion` is split by Lean (`Readings.Wire.splitCase`): the main case and one
case per companion set, each checked by itself. Lean owns the split, every case's admission, the meaning ids over
each companion's environment, the product fold, the typing of a conclusion, the conditions and the English plan;
Python relays and binds Lean's answers, proposes evidence for each case with RD-3's untrusted generators
(`Enumerated`), and renders Lean's plan.

`load` asks Lean, at load, for the split's elaboration (each case's environment, document, checked part and route),
its validation and the product's conflict answer without evidence, so a document Lean does not check as a product is
refused with Lean's text. `Components` is the route of a loaded document: one `_Part` per case, `main` first, each
proposing evidence on its own choices' documents, and the product's `readings-verdicts` requests, whose answers
`check_product` binds to the request (schema and binding only; DRI ruling of rd-3 round 3).
"""
from __future__ import annotations

import json

from .errors import CheckerUnavailable, VEError
from .readings_verdicts import BUDGET, Enumerated, _check_answer, _check_english, _dead_certificates, _Frame, _need, _shown_of

PRODUCT = "components"
_NOT_SUPERPOSABLE = "ReadingsNotSuperposable: "


def has_companions(reading_sets):
    """Whether some reading of the document carries its own vocabulary (structural: the member is present)."""
    return type(reading_sets) is list and any(
        type(s) is dict and type(s.get("readings")) is list and
        any(type(r) is dict and "companion" in r for r in s["readings"]) for s in reading_sets)


def _companion_sets(document):
    """The set ids whose readings carry `companion`, in source order of their first version: the cases Lean's split
    must answer beside `main` (a binding check of Lean's answer, never a split)."""
    out = []
    for s in document.get("reading_sets") or []:
        if any("companion" in r for r in s.get("readings") or []) and s["id"] not in out:
            out.append(s["id"])
    return out


def load(environment, units, reading_sets, *, couplings=(), narrowings=(), executable=None):
    """Lean's split of a document with companion sets, bound to the request: each case's environment, document,
    checked part, elaboration and validation, and the product's conflict answer without evidence. A Lean refusal of
    any of the three is the document's diagnostic, Lean's text."""
    from .readings_route import _check, _completion_elaborate, document_wire, run_lean
    from .readings_s1 import Document, content_bearing, wire
    from .backends.service_schema import same_json
    environment = wire(environment)
    document = wire(document_wire(units, reading_sets, couplings=couplings, narrowings=narrowings))
    base = {"environment": environment, "document": document}
    cases = [{"id": "readings-s2", "kind": "readings-elaborate", **base},
             {"id": "readings-s1", "kind": "readings-validate", **base},
             {"id": "readings-verdicts", "kind": "readings-verdicts", **base, "question": "conflict", "evidence": []}]
    elaborate, validate, product = run_lean(cases, executable=executable)
    for row in (elaborate, validate, product):
        if row.get("status") == "error":
            raise VEError(row["error"])
    try:
        from .backends.service_schema import check_row
        for case, row in zip(cases, (elaborate, validate)):
            check_row("readings-route", row, {"id": row.get("id"), "kind": case["kind"]}, 0)
            _need(row["id"] == case["id"] and set(row) == {"id", "status", "components"})
        names = [c["component"] for c in elaborate["components"]]
        _need(names == ["main", *_companion_sets(document)])
        _need([c["component"] for c in validate["components"]] == names)
    except (CheckerUnavailable, VEError):
        raise
    except Exception as exc:  # noqa: BLE001 - any failure of the check is an invalid answer, never a verdict
        raise CheckerUnavailable("the Lean readings route returned an invalid answer") from exc
    parts = []
    # Bind the split's names and copied rows to the input. Lean decides where each row belongs; the relay only
    # refuses an invented, omitted or duplicated source row. A cited unit may be carried without its content.
    source_units = {u["id"]: u for u in document["units"]}
    source_sets = list(document.get("reading_sets") or [])
    source_narrowings = list(document.get("narrowings") or [])
    source_couplings = list(document.get("couplings") or [])
    copied_sets, copied_narrowings, copied_couplings = [], [], []
    for row, checked_row in zip(elaborate["components"], validate["components"]):
        part_doc = row["document"]
        for unit in part_doc["units"]:
            _need(unit["id"] in source_units)
            _need(same_json(unit, source_units[unit["id"]]) or same_json(unit, {"id": unit["id"]}) or
                  same_json(unit, {k: v for k, v in source_units[unit["id"]].items() if k != "content"}))
        _need(len({u["id"] for u in part_doc["units"]}) == len(part_doc["units"]))
        copied_sets.extend(part_doc.get("reading_sets") or [])
        copied_narrowings.extend(part_doc.get("narrowings") or [])
        copied_couplings.extend(part_doc.get("couplings") or [])
        _need(all(u["id"] in source_units for u in row["checked"]["units"]))
        if row["component"] == "main":
            _need(same_json(row["environment"], environment))
        case = {"environment": row["environment"], "document": row["document"]}
        _check(checked_row["answer"], {"id": "readings-s1", "kind": "readings-validate", **case})
        checked = {"id": "readings-s2", "kind": "readings-elaborate", "environment": row["environment"],
                   "document": row["checked"]}
        # In a split the main case without a content-bearing set is read under the completion as its checked part
        # (its fixed units): Lean's row then carries its filled document (`Readings.Run.admitChecked`).
        main_fixed = row["component"] == "main" and not any(content_bearing(R) for R in Document(None, row["checked"]).sets)
        answer = _completion_elaborate(row["answer"], checked, checked_part=main_fixed)
        parts.append({"name": row["component"], "environment": row["environment"], "document": row["document"],
                      "checked": row["checked"], "elaborate": answer, "validate": checked_row["answer"]})
    def rows_equal(left, right):
        return sorted(json.dumps(x, sort_keys=True) for x in left) == sorted(json.dumps(x, sort_keys=True) for x in right)
    _need(rows_equal(copied_sets, source_sets))
    _need(rows_equal(copied_narrowings, source_narrowings))
    _need(rows_equal(copied_couplings, source_couplings))
    loaded = {"environment": environment, "document": document, "parts": parts}
    route = Components(None, loaded)
    route.check_product(product, cases[2])
    loaded["route"] = route.routes_of(product)
    return loaded


# ---------------------------------------------------------------------------------------------------------------
# One case: RD-3's evidence generators on the case's own choices

class _Part(Enumerated):
    """One case of the split as the enumerated route Lean checks it under the completion: its environment, its checked
    document and Lean's elaboration of it (the filled frame and the compatible choices; a checked part without an
    open set has the one empty choice). Python's generators propose evidence on each choice's document; every Lean
    request names the case (`component`) on the whole document, which Lean splits again."""

    def __init__(self, product, part):
        from .readings_s1 import Document, S1Environment
        self.product = product
        self.name = part["name"]
        self.row = dict(part["elaborate"])
        self.route = "enumerated"
        self.environment = part["environment"]
        self.document = part["checked"]
        self.couplings = list(self.document.get("couplings") or [])
        self.narrowings = list(self.document.get("narrowings") or [])
        filled = self.row.get("filled")
        self.completion = filled is not None
        self.source = Document(S1Environment(self.environment, filled), self.document, filled)
        self.sets = self.source.sets
        choices = self.row.get("choices")
        self.choices = (None if choices == "over" else [{}] if not self.sets else
                        [{s: i for s, i in choice} for choice in choices])
        self.numbers = product.numbers
        self.doc = product.doc
        self._docs, self._conflict, self._premise, self._answers = {}, {}, {}, {}
        self._dead, self._notes = None, None
        self.requests = {}

    def lean(self, kind, **fields):
        from .readings_route import run_lean
        [row] = run_lean([{"id": kind, "kind": kind, "environment": self.product.environment,
                           "document": self.product.document, "component": self.name, **fields}])
        if row.get("status") != "ok":
            raise CheckerUnavailable(f"ReadingsConformance: Lean refused the {kind} case Python built: "
                                     f"{row.get('error')}")
        return row

    def frame(self, case):
        finding = (self.row.get("finding") or {}).get("text")
        if finding is not None and not finding.startswith(_NOT_SUPERPOSABLE):
            raise CheckerUnavailable("ReadingsConformance: a component's finding names no sets")
        return _Frame(case, None if self.choices is None else [self.choice_json(c) for c in self.choices],
                      self.completion, [] if finding is None else finding.removeprefix(_NOT_SUPERPOSABLE).split(", "))

    def _verdicts(self, question, query=None, **fields):  # noqa: D401 - the product asks every case at once
        raise CheckerUnavailable("ReadingsConformance: a component's verdicts are the product's")

    def entries(self, query=None):
        """This case's evidence entries, tagged with its name."""
        out = []
        for choice in self.choices or []:
            key = self._key(choice)
            pieces = {**self._conflict.get(key, {}), **self._premise.get(key, {}), **(query or {}).get(key, {})}
            if pieces:
                out.append({"component": self.name, "choice": self.choice_json(choice), **pieces})
        return out


# ---------------------------------------------------------------------------------------------------------------
# The product (4.5)

class Components:
    """The route of a document with companion sets: one `_Part` per case of Lean's split, `main` first, and the
    product's answers, Lean's (`readings-verdicts` without `component`)."""

    route = PRODUCT

    def __init__(self, doc, loaded=None):
        loaded = loaded if loaded is not None else doc["readings_components"]
        self.doc = doc
        self.environment, self.document = loaded["environment"], loaded["document"]
        units = doc["units"] if doc is not None else [{"id": u["id"]} for u in self.document["units"]]
        self.numbers = {unit["id"]: n for n, unit in enumerate(units, 1)}
        self.parts = [_Part(self, part) for part in loaded["parts"]]
        self.by_name = {part.name: part for part in self.parts}
        self.loaded = loaded
        self._answers = {}
        self.requests = {}

    # -- requests

    def _case(self, question, query=None, query_part=None, **fields):
        evidence = [e for part in self.parts for e in part.entries(query if part is query_part else None)]
        case = {"id": "readings-verdicts", "kind": "readings-verdicts", "environment": self.environment,
                "document": self.document, "question": question, "evidence": evidence, **fields}
        dead = [{"component": part.name, **d} for part in self.parts for d in part._dead or []]
        if dead:
            case["dead"] = dead
        return case

    def _ask(self, question, query=None, query_part=None, user=False, **fields):
        """Lean's product answer to the request with the evidence generated so far, checked (`check_product`). A
        refusal of the first request of a query is the user's (the conclusion, `--sentence`, `--under`), Lean's text;
        any other refusal is of a case Python built."""
        from .readings_route import run_lean
        case = self._case(question, query, query_part, **fields)
        [row] = run_lean([case])
        if row.get("status") != "ok":
            error = row.get("error")
            if user and isinstance(error, str):
                raise VEError(error)
            raise CheckerUnavailable(f"ReadingsConformance: Lean refused the readings-verdicts case Python built: "
                                     f"{error}")
        self.check_product(row, case)
        self.requests[id(row)] = case
        return row

    @staticmethod
    def sub(row, name):
        """The answer of case `name` inside a product answer."""
        return next(entry["answer"] for entry in row["components"] if entry["component"] == name)

    # -- the questions

    def conflict_answer(self):
        """The conflict question: every case's packages, then a witness for every choice Lean leaves without
        CONFLICT-FREE (`readings-choice`'s order of 4.3), every case in one request."""
        if "conflict" not in self._answers:
            for part in self.parts:
                for choice in part.choices or []:
                    case = part._choice(choice).conflict_case()
                    if case is not None:
                        part._conflict.setdefault(part._key(choice), {})["conflict"] = case
            row = self._ask("conflict")
            found = False
            for part in self.parts:
                for entry in self.sub(row, part.name)["per_choice"]:
                    if entry["conflict"] != "CONFLICT-FREE":
                        choice = part._of(entry["choice"])
                        witness = part._choice(choice).witness_case()
                        if witness is not None:
                            part._conflict.setdefault(part._key(choice), {})["witness"] = witness
                            found = True
            self._answers["conflict"] = self._ask("conflict") if found else row
        return self._answers["conflict"]

    def premises_answer(self):
        """The premises question: per case and choice a certificate of ⊥ (only under a CONFLICT-FREE reading; the
        quick proof first), else a model; then the dead readings' certificates of each case's untaken candidates."""
        if "premises" not in self._answers:
            conflict = self.conflict_answer()
            for part in self.parts:
                free = {part._key(part._of(e["choice"])): e["conflict"] == "CONFLICT-FREE"
                        for e in self.sub(conflict, part.name)["per_choice"]}
                for choice in part.choices or []:
                    document, key = part._choice(choice), part._key(choice)
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
                        part._premise[key] = piece
            row = self._ask("premises")
            again = False
            for part in self.parts:
                untaken = self.sub(row, part.name)["untaken"]
                if untaken and part._dead is None:
                    dead = _dead_certificates(part, [tuple(x) for x in untaken])
                    if dead is not None:
                        part._dead = dead
                        again = True
            self._answers["premises"] = self._ask("premises") if again else row
        return self._answers["premises"]

    def query_answer(self, conclusion_ast, assumed=None, sentence=None, premises=()):
        """The query (4.5): every case's conflict and premise evidence first; Lean types the conclusion in one case
        (`sentence` names it when the terms fit several) and names it; then a certificate or a countermodel for each
        of that case's choices past its gate, and Lean's product answer."""
        key = json.dumps([conclusion_ast, list(premises), None if assumed is None else [list(x) for x in assumed],
                          sentence], sort_keys=True)
        if key not in self._answers:
            self.premises_answer()
            fields = {"premises": list(premises), "conclusion": conclusion_ast}
            if assumed is not None:
                fields["assumed"] = [list(x) for x in assumed]
            if sentence is not None:
                fields["sentence"] = sentence
            row = self._ask("query", user=True, **fields)
            part = self.by_name[row["component"]]
            answer = self.sub(row, part.name)
            if "conflict_status" not in answer["result"] and "budget" not in answer["result"]:
                query = {}
                for entry in answer["per_choice"]:
                    choice = part._of(entry["choice"])
                    document = part._choice(choice)
                    found = document.certificate_case(conclusion_ast, premises)
                    if found is not None:
                        query[part._key(choice)] = {"certificate": found}
                        continue
                    found = document.model_case(conclusion_ast, premises)
                    if found is not None:
                        query[part._key(choice)] = {"countermodel": found}
                if query:
                    row = self._ask("query", query=query, query_part=part, **fields)
            self._answers[key] = row
        return self._answers[key]

    # -- the route's interface for `ve document check`

    def conflict(self, A=()):
        return self.conflict_answer()["result"]

    def premises(self):
        return self.premises_answer()["result"]

    def entailment(self, conclusion_ast, premises=(), assumed=None, sentence=None):
        return self.query_answer(conclusion_ast, assumed, sentence, premises)["result"]

    def routes_of(self, row):
        return {entry["component"]: entry["route"] for entry in row["components"]}

    # -- the answer's binding to the request (build checklist 4)

    def _sub_case(self, case, part, question):
        """The request one case's answer answers: its evidence and dead certificates without their tag, its
        question, and for the query's case the conclusion, premises and readings named."""
        def untagged(items):
            return [{k: v for k, v in e.items() if k != "component"} for e in items if e.get("component") == part.name]
        sub = {"id": case["id"], "kind": case["kind"], "environment": part.environment, "document": part.document,
               "question": question, "evidence": untagged(case.get("evidence", []))}
        dead = untagged(case.get("dead", []))
        if question == "premises" and dead:
            sub["dead"] = dead
        if question == "query":
            for name in ("premises", "conclusion", "assumed"):
                if name in case:
                    sub[name] = case[name]
        return sub

    def check_product(self, row, case):
        """Lean's product answer to `case`, as untrusted output: its schema (`verdicts_components`, generated and
        proved to fit) and its binding to the request, nothing else. Its cases are exactly the split's, `main` first;
        each case's answer is checked as RD-3 checks an answer (`_check_answer`) against that case's request; the
        query's case is one of them and the readings `--under` names are its; each status a result restates is its
        case's own; every choice, unit and line names only what its case has. What the product concludes (its
        verdict, the decided units, which lines are said) is Lean's, by theorem (`readings_wire_product_*`)."""
        try:
            from .backends.service_schema import Invalid, check_row
            check_row("readings-route", row, {"id": row.get("id"), "kind": "readings-verdicts"}, 0)
            question = case["question"]
            _need(row["id"] == case["id"] and row["question"] == question and row["route"] == PRODUCT)
            names = [part.name for part in self.parts]
            _need([entry["component"] for entry in row["components"]] == names)
            k = row["component"]
            if question == "query":
                _need(k in names and row["sentence"] == case.get("sentence"))
            else:
                _need(k is None and row["sentence"] is None)
            units = {}
            for part, entry in zip(self.parts, row["components"]):
                own = [u["id"] for u in part.document["units"]]
                set_units = {s["unit"] for s in part.document.get("reading_sets") or []
                             if any(r.get("content") is not None for r in s.get("readings") or [])}
                checked_units = [u["id"] for u in part.document["units"]
                                 if u.get("content") is not None or u["id"] in set_units]
                _need(entry["units"] == checked_units)
                for u in entry["units"]:
                    _need(u not in units)
                    units[u] = part.name
                written = {(s["id"], s["unit"]) for s in self.loaded_document(part)["reading_sets"]}
                _need(all((x["set"], x["unit"]) in written for x in entry["unchecked"]))
                _need(not entry["unchecked"] or part.name == "main")
                sub_question = (("query" if part.name == k else "premises") if question == "query" else question)
                sub = self._sub_case(case, part, sub_question)
                _check_answer(entry["answer"], sub, part.frame(sub))
                self._check_sub_fields(entry["answer"], sub)
            result = row["result"]
            subs = {entry["component"]: entry["answer"] for entry in row["components"]}
            if question == "query":
                _need(result["component"] == k)
                if result["verdict"] == "UNKNOWN" and subs[k]["result"].get("verdict") != "UNKNOWN":
                    _need("reason" in result or "conflict_status" in result)
                if "choice_component" in result:
                    j = result["choice_component"]
                    _need(j in names and j != k)
                    _need(any(e["choice"] == result["choice"] for e in subs[j]["per_choice"]))
            else:
                _need([c["component"] for c in result["components"]] == names)
                for c in result["components"]:
                    _need(c["status"] == subs[c["component"]]["result"]["status"])
            decided = row["decided_units"]
            _need(len(set(decided)) == len(decided) and all(u in units for u in decided))
            _need(decided == sorted(decided, key=lambda u: self.numbers[u]))
            for entry in row["english"]:
                name = entry["component"]
                if name is None:
                    _need(entry["line"]["frame"] == "E32")
                    self._check_line_fields(entry["line"])
                    continue
                part = self.by_name[name]
                sub = subs[name]
                sub_question = sub["question"]
                frame = part.frame(self._sub_case(case, part, sub_question))
                rows = {json.dumps(e["choice"]): e for e in sub["per_choice"]}
                _check_english({**sub, "english": [entry["line"]]}, frame, rows)
                self._check_line_fields(entry["line"])
        except CheckerUnavailable:
            raise
        except (Invalid, AttributeError, KeyError, TypeError, ValueError, IndexError, StopIteration) as exc:
            raise CheckerUnavailable("the Lean readings route returned an invalid answer") from exc

    @staticmethod
    def _check_line_fields(line):
        """Type a plan line's optional fields by its frame (the producer's `PlanItem.line` forms)."""
        frame = line["frame"]
        result = line["result"]
        _need(frame in {"E3", "E5", "E7", "E10", "E12", "E13", "E17", "E26", "E27", "E28", "E29",
                        "E30", "E31", "E32", "P1", "status", "unworded"})
        has_result = frame in {"E10", "E12", "E26", "E30"}
        _need(result in {"R1", "R2", "R3", "R4", "R5", "R6", "R7"} if has_result else result is None)
        _need((line["model"] is not None) == (result in {"R3", "R4", "R5"}))
        _need((line["label"] is not None) == (frame in {"E5", "E7", "P1", "status", "unworded"}))

    @classmethod
    def _check_sub_fields(cls, row, case):
        """Bind optional line and shown-model members of a case's answer to their producer forms and request."""
        _need((row["dead_readings"] is not None) == (case["question"] == "premises"))
        for line in row["english"]:
            cls._check_line_fields(line)
        sent = {json.dumps(e["choice"]): e for e in case.get("evidence", [])}
        for entry in row["per_choice"]:
            piece = sent.get(json.dumps(entry["choice"]), {})
            for shown in entry["shown"].values():
                _need(type(shown) is dict)
            for name, accepted in entry["evidence"].items():
                if accepted is True:
                    expected = _shown_of(piece.get(name), name)
                    if type(expected) is dict:
                        _need(entry["shown"].get(name) == expected)
            if entry["status_text"] is not None:
                witness = piece.get("witness")
                _need(type(witness) is dict and entry["status_text"] == witness.get("status_text"))

    def loaded_document(self, part):
        """The case's document as Lean split it (its sets, those it leaves on W2 included)."""
        return next(p["document"] for p in self.loaded["parts"] if p["name"] == part.name)


def context(doc):
    """The product route of a loaded document with companion sets."""
    if "_readings_components" not in doc:
        doc["_readings_components"] = Components(doc)
    return doc["_readings_components"]


# ---------------------------------------------------------------------------------------------------------------
# Display: each case as a document of its own (Lean's split), numbered as the whole document

CHECKED_BY = {
    "lean": "readings-defaults RD-4b: Readings.Wire.splitCase splits the document; each case's readings@1 admission, "
            "separations and findings (readings-validate), its route and choices (readings-elaborate), every "
            "verdict, the product fold, the Lean-decided units and the English plan (readings-verdicts)",
    "python": "W2 structure of the reading sets (companion passed through unread); evidence proposed by Python's "
              "generators, every piece checked by Lean"}


def subdoc(doc, part, checked=False):
    """Case `part` of Lean's split as a loaded document of its own, for display: its environment, its units (the
    document's own, by id), its reading sets, couplings and narrowings, and Lean's answers on it. `checked`: the
    document its verdicts read (the main case's checked part when it has no content-bearing set), with the filled
    document Lean's elaboration gives it."""
    from .document import _environment
    by_id = {u["id"]: u for u in doc["units"]}
    document = part["checked"] if checked else part["document"]
    validated = part["validate"]
    if checked and "filled" in part["elaborate"] and "filled" not in validated:
        validated = {**validated, "filled": part["elaborate"]["filled"],
                     "fill_premises": part["elaborate"]["fill_premises"]}
    # A narrowing may carry a cited unit into its component without that unit's content. Keep Lean's split
    # content boundary when attaching the original source and span for display.
    units = []
    for unit in document["units"]:
        shown = {**by_id[unit["id"]]}
        if "content" not in unit:
            shown["content"] = None
        else:
            shown["content"] = unit["content"]
        units.append(shown)
    return {"environment": _environment(part["environment"]),
            "units": units,
            "meta": {"reading_sets": list(document.get("reading_sets") or []),
                     "couplings": list(document.get("couplings") or []),
                     "narrowings": list(document.get("narrowings") or [])},
            "readings_s1": validated, "readings_s2": part["elaborate"]}


class PartsWording:
    """`ve document render`'s S1 lines under each open set, read in the case the set is in."""

    def __init__(self, doc):
        from .readings_route import Wording
        self.numbers = {u["id"]: n for n, u in enumerate(doc["units"], 1)}
        self.cases = []
        for part in doc["readings_components"]["parts"]:
            units = {s["unit"] for s in part["document"].get("reading_sets") or []}
            if part["validate"].get("content_bearing"):
                self.cases.append((units, Wording(subdoc(doc, part), numbers=self.numbers)))

    def set_lines(self, unit_id):
        for units, wording in self.cases:
            if unit_id in units:
                return wording.set_lines(unit_id)
        return []


def _wordings(doc, route):
    """Each case's S2 wording, numbered as the whole document."""
    from .readings_s2_wording import S2Wording
    out = {}
    for loaded, part in zip(doc["readings_components"]["parts"], route.parts):
        out[part.name] = S2Wording(subdoc(doc, loaded, checked=True), part, numbers=route.numbers)
    return out


def english(doc, route, row, slot=None):
    """The sentences of Lean's product plan (2.4): E32, then each line read in its case (`S2Wording.plan`'s
    rendering, E30 and E31 included). A line Python cannot render as planned is `CheckerUnavailable`."""
    wordings = _wordings(doc, route)
    if slot is not None:
        wordings[row["component"]].slots.conclusions.add(slot)
    out = []
    for entry in row["english"]:
        name = entry["component"]
        wording = wordings[name] if name is not None else next(iter(wordings.values()))
        answer = route.sub(row, name) if name is not None else row
        try:
            out.append(wording._plan_line(entry["line"], answer, slot))
        except (KeyError, TypeError, ValueError, IndexError) as exc:
            raise CheckerUnavailable(f"ReadingsConformance: Lean's English plan has a line Python cannot render: "
                                     f"{entry}") from exc
    return out


def conclusion_slot(doc, route, row, conclusion_ast):
    """`<conclusion>` in the case the query is typed in (Lean's choice), read back by that case's surface."""
    return _wordings(doc, route)[row["component"]].conclusion(conclusion_ast)


def report(doc):
    """Section 6 for a document with companion sets: per case its sets (S1), its route, units, the sets it leaves
    on W2 and its own conflict and premise answers (RD-3's on it); the product's conflict and premise results, the
    Lean-decided units (1.10) and the English of both plans."""
    from .readings_route import s1_sections
    route = context(doc)
    conflict, premises = route.conflict_answer(), route.premises_answer()
    numbers = route.numbers
    parts = []
    separations = {"outcome": 0, "selects": 0, "holds": 0}
    findings = {"SeparatedByDecisionOnly": 0, "SeparatedByActOnly": 0}
    pending = 0
    for loaded, part, entry in zip(doc["readings_components"]["parts"], route.parts, premises["components"]):
        sections = (s1_sections(subdoc(doc, loaded), loaded["validate"], numbers)
                    if loaded["validate"].get("content_bearing") else None)
        if sections is not None:
            for key, value in sections["separations"].items():
                separations[key] += value
            for key, value in sections["findings"].items():
                findings[key] += value
            pending += sections["pending_candidates"]
        parts.append({"component": part.name, "route": entry["route"], "units": entry["units"],
                      "unchecked": entry["unchecked"], "sets": [] if sections is None else sections["sets"],
                      "conflict": route.sub(conflict, part.name)["result"],
                      "premises": entry["answer"]["result"],
                      "dead_readings": entry["answer"]["dead_readings"]})
    return {"checked_by": CHECKED_BY, "route": PRODUCT, "components": parts,
            "sets": [s for p in parts for s in p["sets"]],
            "separations": separations, "findings": findings, "pending_candidates": pending,
            "couplings": len({item["axis"] for item in doc["meta"].get("couplings", [])}),
            "status": conflict["result"]["status"], "conflict": conflict["result"],
            "decided_units": premises["decided_units"],
            "english": english(doc, route, conflict) + english(doc, route, premises)}


def query(doc, conclusion_ast, assumed=None, sentence=None):
    """`ve document readings --conclusion … [--sentence <unit>] [--under SET:INDEX]` (4.5): Lean's product answer,
    each case's own result, restrictions and conditions under it (A3), the decided units and the English."""
    route = context(doc)
    row = route.query_answer(conclusion_ast, assumed, sentence)
    slot = conclusion_slot(doc, route, row, conclusion_ast)
    components = []
    for entry in row["components"]:
        answer = entry["answer"]
        components.append({"component": entry["component"], "route": entry["route"], "question": answer["question"],
                           "result": answer["result"], "restrictions": answer["restrictions"],
                           "conditional_on": answer["result"].get("conditional_on", []),
                           "unchecked": entry["unchecked"]})
    return {**row["result"], "sentence": row["sentence"], "components": components,
            "decided_units": row["decided_units"], "english": english(doc, route, row, slot)}


__all__ = ["Components", "PRODUCT", "PartsWording", "context", "english", "has_companions", "load", "query",
           "report"]
