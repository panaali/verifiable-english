"""The binding of a `readings-verdicts` answer to its request: its schema and the relations to the request only,
never a verdict (DRI ruling of rd-3 round 3; build checklist 4 and 5)."""
from __future__ import annotations

import json
from contextlib import contextmanager

from ..errors import CheckerUnavailable, ResourceLimit


def dead_finding(set_id, index):
    """The finding of a dead reading (1.9), Lean's `deadReadingsJson` text; both routes report it."""
    return f"DeadReading: {set_id}:{index}"


# The piece each row word rests on (Lean's `lowerInfo`; under the completion `ndConflictRow`, `ndQueryRow`,
# `ndPremiseRow`), per row field. A word other than UNKNOWN names that piece: the request must have sent it for the
# row's choice and the row must note it accepted (the evidence a row names exists in the request). Which word the
# pieces give, and every verdict, condition and line folded from the rows, is Lean's (`readings_wire_verdicts_*`,
# `verdicts_conditions_*`, DRI ruling of rd-3 round 3); the client never re-derives them.
ROW_PIECES = {"conflict": {"CONFLICT-FREE": "conflict", "CONFLICT": "witness"},
              "query": {"proved": "certificate", "refuted": "countermodel"},
              "premises": {"INCONSISTENT": "unsat", "model": "model"}}
PAIR_LABEL = "unsaid:pair:"


class _Frame:
    """What a `readings-verdicts` answer is bound to: the request's document as Lean decodes it (its open sets at their
    active versions, in unit order; its couplings and narrowings), the request's environment, the compatible choices
    `choices` (Lean's elaborate row, bound to the request; None past 64), whether the unspecified completion applies,
    and the sets the route's finding names (E29)."""

    def __init__(self, case, choices, completion, finding_sets):
        from types import SimpleNamespace
        from ..readings_s1 import active_sets, wire
        document = wire(case["document"])
        active = active_sets(document.get("reading_sets") or [])
        self.sets = []
        for unit in document["units"]:
            R = next((r for r in active if r["unit"] == unit["id"]), None)
            if R is not None and R["status"] == "open":
                self.sets.append(SimpleNamespace(id=R["id"], unit=R["unit"], version=R["version"], candidates=[
                    SimpleNamespace(id=a["id"], labels=a.get("labels") or {}) for a in R["readings"]]))
        self.couplings = list(document.get("couplings") or [])
        self.narrowings = list(document.get("narrowings") or [])
        self.predicates = set((((case.get("environment") or {}).get("vocabulary") or {}).get("predicates") or {}))
        # The rules the request's document declares (a unit's or a reading's norm), with the exception conditions a
        # soft label names (`readings_route.soft_rules`).
        from ..readings_route import soft_rules
        contents = [unit.get("content") for unit in document["units"]] + [
            a.get("content") for R in active for a in R["readings"]]
        self.rules = soft_rules(c["norm"] for c in contents if type(c) is dict and type(c.get("norm")) is dict)
        self.choices, self.completion, self.finding_sets = choices, completion, list(finding_sets)
        self.candidates = [[R.id, i] for R in self.sets for i in range(len(R.candidates))]

    def label(self, label):
        """A condition label the request names: a coupling or narrowing of its document, a soft premise's label
        naming its rules (`readings_route.soft_label`, under the soft completion), or the pair label of two predicates
        of its environment (`unsaid:pair:<required>,<permission>`)."""
        from ..readings_route import SOFT_COHERENCE_LABEL, SOFT_EXCEPTION_LABEL, soft_label
        _need(type(label) is str)
        if label.startswith("coupling:"):
            _need(any(K["id"] == label[len("coupling:"):] for K in self.couplings))
        elif label.startswith("narrowing:"):
            _need(any(N["id"] == label[len("narrowing:"):] for N in self.narrowings))
        elif label.startswith((SOFT_EXCEPTION_LABEL, SOFT_COHERENCE_LABEL)):
            _need(soft_label(label, self.rules))
        else:
            required, comma, permission = label.removeprefix(PAIR_LABEL).partition(",")
            _need(label.startswith(PAIR_LABEL) and comma and {required, permission} <= self.predicates)

    def reading(self, reading):
        """A candidate the request's document has: `[set, index]`."""
        _need(type(reading) is list and len(reading) == 2 and reading in self.candidates)


def _shown_of(piece, name):
    """`Readings.Run.shownOf`: the model Lean shows of a piece Python sent, its `shown` member else its checked
    model."""
    if type(piece) is not dict:
        raise ValueError
    if "shown" in piece:
        return piece["shown"]
    holder = piece.get("witness") if name == "witness" else piece
    return holder.get("model") if type(holder) is dict else None


def _need(condition):
    if not condition:
        raise ValueError


INVALID_ANSWER = "the Lean readings route returned an invalid answer"


@contextmanager
def relayed():
    """Checking an answer Lean sent (build checklist 4 and 5): every failure inside is `CheckerUnavailable`, never a
    crash and never a verdict, whatever the answer holds (a type its schema did not fix, a missing or duplicated
    row, a decoder's refusal of a value Lean sent). A resource limit stays a resource limit (checklist 6). The one
    guard of every check of a `readings-verdicts` answer and of the split's answers at load."""
    try:
        yield
    except (CheckerUnavailable, ResourceLimit):
        raise
    except Exception as exc:  # noqa: BLE001 - any failure of the check is an invalid answer
        raise CheckerUnavailable(INVALID_ANSWER) from exc


def _labels(value):
    _need(type(value) is list and all(type(x) is str for x in value))
    return value


def _check_rows(row, case, frame):
    """The rows, bound to the request: the compatible choices exactly the ones taking `assumed`, in order, at least
    one; past 64 only choices the request's evidence names, in its order. Each row notes only pieces the request sent
    for its choice (every conflict package sent is noted); its refusals, shown models and gaps are of noted pieces;
    a shown model is the one the request's piece shows; its word fields are the question's; and a word other than
    UNKNOWN names a piece the row notes accepted (`ROW_PIECES`). Returns the rows by choice."""
    question, assumed = case["question"], case.get("assumed")
    sent = {json.dumps(e["choice"]): e for e in case.get("evidence", [])}
    rows = row["per_choice"]
    seen = [entry["choice"] for entry in rows]
    _need(len({json.dumps(c) for c in seen}) == len(seen))

    def takes(choice):
        return all(x in choice for x in assumed or [])
    if frame.choices is None:
        order = [json.loads(k) for k in sent]
        _need(all(takes(c) for c in seen))
        _need([order.index(c) for c in seen] == sorted(order.index(c) for c in seen))  # ValueError if not sent
    else:
        expected = [c for c in frame.choices if takes(c)]
        _need(expected and seen == expected)
    for entry in rows:
        piece_of = sent.get(json.dumps(entry["choice"]), {})
        pieces = {name for name in piece_of if name != "choice"}
        noted = entry["evidence"]
        _need(set(noted) <= pieces and ("conflict" not in pieces or "conflict" in noted))
        _need(set(entry["errors"]) <= set(noted) and all(noted[name] is False for name in entry["errors"]))
        _need(set(entry["shown"]) <= set(noted) and set(entry["gaps"]) <= set(noted))
        # A witness's status text is the lower route's own, relayed with the witness.
        _need(entry["status_text"] is None or "witness" in noted)
        for name, shown in entry["shown"].items():
            _need(shown == _shown_of(piece_of.get(name), name))
        _need(set(entry) & {"query", "premises"} == {question} - {"conflict"})
        for field in {"conflict", question}:
            word = entry[field]
            _need(word == "UNKNOWN" or (word in ROW_PIECES[field] and noted.get(ROW_PIECES[field][word]) is True))
    return {json.dumps(entry["choice"]): entry for entry in rows}


def _walk(value):
    """Every object inside a JSON value, the value's own first."""
    if type(value) is dict:
        yield value
        for item in value.values():
            yield from _walk(item)
    elif type(value) is list:
        for item in value:
            yield from _walk(item)


# The piece whose shown model a result member shows, by the member that holds it.
SHOWN_IN = {"witnesses": "witness", "countermodels": "countermodel", "countermodel": "countermodel"}


def _check_result(row, case, frame, rows):
    """The result, bound to the request and the rows: it is the over-budget form exactly when the request has more
    than 64 compatible choices, it assumes exactly the readings the request named, every choice it names is a row's,
    a list restating the rows (`choices`, `proofs`, `countermodels`) restates every row once, in order, each status
    the row's word, and `witnesses` the rows in conflict; a SOME names its proof and its countermodel; every model it shows is that row's shown model (the request's piece's), a witness's status text
    is its row's, its candidates are the document's, every narrowing, unit and label it names is the request's, and
    its restrictions are the answer's."""
    result, question = row["result"], case["question"]
    _need(("budget" in result) == (frame.choices is None))
    _need(result.get("assumed") == (case.get("assumed") if question == "query" else None))
    for obj in _walk(result):
        if "choice" in obj:
            _need(json.dumps(obj["choice"]) in rows)
    for member in ("choices", "proofs", "countermodels"):
        if member in result:
            _need([json.dumps(item["choice"]) for item in result[member]] == list(rows))
    for item in result.get("choices", []):
        _need(item["status"] == rows[json.dumps(item["choice"])]["conflict" if question == "conflict" else question])
    if "witnesses" in result:
        _need([json.dumps(w["choice"]) for w in result["witnesses"]] ==
              [key for key, entry in rows.items() if entry["conflict"] == "CONFLICT"])
    if result.get("verdict") == "SOME":
        _need(type(result["proof"]) is dict and type(result["countermodel"]) is dict)
    for member, piece in SHOWN_IN.items():
        items = result.get(member)
        for item in items if type(items) is list else [items] if type(items) is dict else []:
            entry = rows[json.dumps(item["choice"])]
            if "model" in item:
                _need(item["model"] == entry["shown"].get(piece))
            if member == "witnesses":
                _need(item["status_text"] == entry["status_text"])
    if question == "premises" and "model" in result:
        _need(result["model"] == rows[json.dumps(result["choice"])]["shown"].get("model"))
    if "candidates" in result:
        _need([[c["set"], c["index"]] for c in result["candidates"]] == frame.candidates)
    for candidate in result.get("candidates", []):
        if "narrowing" in candidate:
            _need(any(N["id"] == candidate["narrowing"] for N in frame.narrowings))
    for unit in result.get("units", []):
        _need(any(R.unit == unit for R in frame.sets))
    for name in ("restrictions", "reading_premises_used"):
        if name in result:
            _need(result[name] == row["restrictions"])
    for obj in _walk(result):
        for label in obj.get("conditional_on", []):
            # Under the completion every condition is a pair label or a restriction of the request; on the lower route
            # a choice's own answer may add its route's labels (coherence, alternatives, risk), which only it reads.
            if frame.completion:
                frame.label(label)
            else:
                _need(type(label) is str and label)


def _check_dead(row, case, frame):
    """The premises question's dead evidence, bound to the request: one note per dead certificate sent, naming its
    candidate; each untaken candidate a candidate of the document no row takes; a dead reading untaken, with a
    certificate the request sent and Lean noted accepted, and the finding that names it (`dead_finding`). Every
    other question has none."""
    sent = case.get("dead", [])
    if case["question"] != "premises" or frame.choices is None:
        _need(row["dead"] == [] and row["untaken"] == [] and row["dead_readings"] is None)
        return
    _need(len(row["dead"]) == len(sent))
    for d, note in zip(sent, row["dead"]):
        s, i = d.get("set"), d.get("index")
        if type(s) is not str or type(i) is not int or i < 0:
            _need(note == {"accepted": False})
        else:
            _need((note.get("set"), note.get("index")) == (s, i))
    for reading in row["untaken"]:
        frame.reading(reading)
        # An untaken candidate is one no row takes.
        _need(not any(reading in entry["choice"] for entry in row["per_choice"]))
    accepted = {(n["set"], n["index"]) for n in row["dead"] if n.get("accepted") is True}
    for d in row["dead_readings"] or []:
        frame.reading([d["set"], d["index"]])
        _need([d["set"], d["index"]] in row["untaken"] and (d["set"], d["index"]) in accepted)
        _need(d["finding"] == dead_finding(d["set"], d["index"]))


def _check_english(row, frame, rows):
    """The plan's lines name only what the request and the answer have: each reading a candidate, each shown model a
    row's shown piece (`<piece>@<k>`, the `k`th row), each label a condition label of the request (a `status` line: a
    row's status text), an E17 line one of the answer's dead readings. Which lines the plan has, and the conditions it
    states, are Lean's (`verdictsPlan_cites`, `plan_conditions_only`)."""
    from ..ast import decimal_value
    ordered = list(rows.values())
    dead = [[d["set"], d["index"]] for d in row["dead_readings"] or []]
    for line in row["english"]:
        for reading in line["readings"]:
            frame.reading(reading)
        if line["frame"] == "E17":
            _need(line["readings"] and all(reading in dead for reading in line["readings"]))
        if line["model"] is not None:
            piece, at, k = line["model"].partition("@")
            _need(at and k.isdigit() and decimal_value(k) < len(ordered) and piece in ordered[decimal_value(k)]["shown"])
        if line["label"] is not None:
            if line["frame"] == "status":
                _need(any(entry["status_text"] == line["label"] for entry in ordered))
            else:
                frame.label(line["label"])


def _check_answer(row, case, frame):
    """Lean's answer to the `readings-verdicts` request `case`, as untrusted output: its schema and its binding to the
    request, nothing else (DRI ruling of rd-3 round 3; build checklist 4).

    Its shape is `Readings.Run.verdictsAnswer`'s (the generated, proved response schema: every field, its type, the
    result's form for the question, the status words). It answers this request (its id and question), for the route's
    finding, and names only what the request has: its rows are exactly the request's compatible choices (no empty,
    missing or extra row), each piece a row notes or shows was sent for that row's choice, a row's word names a piece
    it notes accepted, and every choice, reading, sentence, model, label and dead reading in the result, the
    conditions and the plan is the request's (`_check_rows`, `_check_result`, `_check_dead`, `_check_english`). What
    the answer concludes from the rows (the verdict, its conditions, which lines the plan says) is Lean's, by theorem
    (`readings_wire_verdicts_*`, `verdicts_conditions_*`, `verdictsPlan_cites`); the client never re-derives it, and
    relays Lean's English unchanged. Every piece of evidence sent is accepted: a refused or unanswered piece (a
    witness, certificate or model Python's own check accepted, or a dead reading's certificate) is
    `CheckerUnavailable`. A conflict package that does not certify CONFLICT-FREE is not refused: the witness search
    follows (4.3)."""
    sent = {json.dumps(e["choice"]): e for e in case.get("evidence", [])}
    with relayed():
        from ..backends.service_schema import check_row
        # The producer's generated, proved response shape owns every field,
        # status spelling and JSON type.
        check_row("readings-route", row, {"id": row.get("id"), "kind": "readings-verdicts"}, 0)
        _need(row["id"] == case["id"] and row["question"] == case["question"])
        _need(("decided_units" in row) is frame.completion)
        if frame.completion:
            units = {unit["id"] for unit in case["document"]["units"]}
            _need(len(row["decided_units"]) == len(set(row["decided_units"])))
            _need(set(row["decided_units"]) <= units)
        _need(row["finding_sets"] == frame.finding_sets)
        rows = _check_rows(row, case, frame)
        for label in row["restrictions"] + row["labels"]:
            frame.label(label)
        _check_result(row, case, frame, rows)
        _check_dead(row, case, frame)
        _check_english(row, frame, rows)
    for entry in row["per_choice"]:
        pieces = {k for k in sent.get(json.dumps(entry["choice"]), {}) if k != "choice"}
        for piece, error in entry["errors"].items():
            raise CheckerUnavailable(f"ReadingsConformance: Lean refused the {piece} Python built on a reading's "
                                     f"document: {error}")
        for piece in sorted(pieces - {"conflict"}):
            # The lower route checks no witness of a choice its packages certify CONFLICT-FREE.
            if piece == "witness" and entry["conflict"] == "CONFLICT-FREE" and piece not in entry["evidence"]:
                continue
            if entry["evidence"].get(piece) is not True:
                raise CheckerUnavailable(f"ReadingsConformance: Lean does not confirm the {piece} Python's "
                                         "generators found on a reading's document")
    for note in row["dead"]:
        if note.get("accepted") is not True:
            raise CheckerUnavailable("ReadingsConformance: Lean does not confirm the dead reading Python's prover "
                                     "certified")


def _check_sup_answer(row, case, route):
    """The generated shape and request relations only; Lean owns every derived result and English line."""
    from ..backends.service_schema import check_row
    from ..readings_s2_wording import PLAN_FRAMES, PLAN_RESULTS
    A = case.get("assumed") or []
    sent = {json.dumps(e["choice"]): e for e in case["evidence"]}
    candidates = [[R.id, i] for R in route.sets for i in range(len(R.candidates))]
    labels = {name for name, _ in route.labelled} | {name for name, _ in getattr(route.base, "soft_premises", ())}
    sets = {R.id for R in route.sets}
    versions = {R.id: R.version for R in route.sets}
    rules = {u["content"]["norm"]["name"] for u in route.document["units"]
             if isinstance(u.get("content"), dict) and "norm" in u["content"]}
    rules.update(obj["name"] for envelope in (route.environment, route.row.get("filled", {}))
                 for obj in _walk(envelope) if isinstance(obj.get("name"), str))
    for entry in route.row.get("names", []):
        for candidate in entry["candidates"]:
            for original, qualified in candidate["names"]:
                rules.update((original, qualified,
                              f"{original} under {entry['set']}@{versions[entry['set']]}:{candidate['index']}"))

    def choice(c, complete=False):
        _need(type(c) is list and all(x in candidates for x in c))
        _need(len({x[0] for x in c}) == len(c))
        if complete:
            _need([x[0] for x in c] == [R.id for R in route.sets])
            if route.choices is not None:
                _need(c in [route.choice_json(x) for x in route.choices])

    def label(value):
        _need(value in labels)

    with relayed():
        check_row("readings-route", row, case, 0)
        _need(row["id"] == case["id"] and row["question"] == case["question"] and row["route"] == "superposed")
        scopes = row["scopes"]
        proposals = row["model_proposals"]
        _need(proposals or not route.checked)
        _need(len({json.dumps(c) for c in proposals}) == len(proposals))
        for c in proposals:
            choice(c, complete=True)
            _need(all(x in c for x in A))
        scope_choices = [x["row"]["choice"] for x in scopes]
        _need(scopes and scope_choices[0] == A)
        _need(len({json.dumps(x) for x in scope_choices}) == len(scope_choices))
        if route.choices is not None:
            full = [route.choice_json(c) for c in route.choices]
            taking = [c for c in full if all(x in c for x in A)]
            live = [[c] for c in candidates if any(c in x for x in full)] if case["question"] == "premises" else []

            def listed(required):
                out = [A]
                for c in required:
                    if c not in out:
                        out.append(c)
                return out
            # Lean lists the asked scope and the live candidates, and the complete choices taking it only while its
            # answer is open (`supOpen`; never for premises): one of these two lists, in this order.
            _need(scope_choices == listed(live) or case["question"] != "premises" and scope_choices == listed(taking))
        else:
            _need(all(c == A or case["question"] == "premises" and len(c) == 1 for c in scope_choices))
        for scope in scopes:
            entry = scope["row"]
            choice(entry["choice"])
            scope_proposals = scope["model_proposals"]
            _need(scope_proposals or not route.checked)
            _need(len({json.dumps(c) for c in scope_proposals}) == len(scope_proposals))
            for c in scope_proposals:
                choice(c, complete=True)
                _need(all(x in c for x in entry["choice"]))
            pieces = sent.get(json.dumps(entry["choice"]), {})
            noted = entry["evidence"]
            _need(set(noted) == set(pieces) - {"choice"})
            _need(set(entry["errors"]) <= set(noted))
            _need(set(entry["shown"]) == set(scope["encoded"]))
            _need(set(entry["shown"]) <= set(noted) and set(entry["gaps"]) <= set(entry["shown"]))
            _need(set(scope["used"]) <= set(noted) and set(scope["mentions"]) == set(scope["used"]))
            for key, model in entry["shown"].items():
                _need(model == _shown_of(pieces[key], key))
                choice(scope["encoded"][key], complete=True)
                _need(all(c in scope["encoded"][key] for c in entry["choice"]))
                _bound_gaps(entry["gaps"].get(key, []), model, route)
            for ls in scope["used"].values():
                for l in ls:
                    label(l)
            for mentioned in scope["mentions"].values():
                _need(set(mentioned) <= sets)
        result = row["result"]
        if "budget" in result and "max_choices" not in result["budget"]:
            _need(result["budget"] == case["budget"])
        if "target" in result:
            _need(any(p.get("witness", {}).get("target") == result["target"] and
                      p.get("witness", {}).get("tuple") == result.get("tuple")
                      for e in case["evidence"] for p in [e.get("witness", {})]))
        _need(result["route"] == "superposed")
        _need("verdict" in result if case["question"] == "query" else "status" in result)
        if case["question"] == "query":
            _need(result.get("assumed", []) == A)
        else:
            # A conflict answer names the readings it was asked under (review F4 of rd-7); premises name none.
            _need(result.get("assumed", A) == A and (case["question"] == "conflict" or "assumed" not in result))
        references = [result]
        references += [result[name] for name in ("proof", "countermodel") if name in result]
        references += [obj for name in ("proofs", "countermodels", "choices", "candidates")
                       for obj in result.get(name, [])]
        for obj in references:
            _need(set(obj.get("mentions", [])) <= sets)
            _need(all(s in route.base.sorts for s in obj.get("sorts", [])))
            _need(all(name in rules for name, _ in obj.get("selected") or []))
            if "choice" in obj:
                choice(obj["choice"], complete=True)
                # Every choice an answer names takes the readings it was asked under (a candidate's its own).
                _need(any(obj is c for c in result.get("candidates", [])) or all(x in obj["choice"] for x in A))
            for key in ("conditional_on", "reading_premises_used", "restrictions"):
                for l in obj.get(key, []):
                    label(l)
            if "model" in obj:
                _need(any(obj["model"] == s["row"]["shown"].get(k) and obj.get("choice") == s["encoded"].get(k)
                          for s in scopes for k in ("witness", "model", "countermodel")))
                _bound_gaps(obj.get("gaps", []), obj["model"], route)
        for member in ("proofs", "countermodels", "choices"):
            if member in result:
                _need(route.choices is not None)
                _need([obj["choice"] for obj in result[member]] ==
                      [route.choice_json(c) for c in route.choices if all(x in route.choice_json(c) for x in A)])
        for proof in ([result["proof"]] if "proof" in result else []) + result.get("proofs", []):
            _need(any(s["row"]["choice"] == proof["choice"] and "certificate" in s["row"]["evidence"]
                      for s in scopes))
        for l in row["restrictions"]:
            label(l)
        sent_dead = case.get("dead", []) if case["question"] == "premises" else []
        _need(len(row["dead"]) == len(sent_dead))
        for note, sent_note in zip(row["dead"], sent_dead):
            _need((note.get("set"), note.get("index")) == (sent_note.get("set"), sent_note.get("index")))
        _need(len({(d["set"], d["index"]) for d in row["dead_readings"] or []}) == len(row["dead_readings"] or []))
        _need(len({tuple(c) for c in row["untaken"]}) == len(row["untaken"]))
        if case["question"] == "premises":
            _need("candidates" not in result or [[c["set"], c["index"]] for c in result["candidates"]] == candidates)
            for c in result.get("candidates", []):
                if "choice" in c:
                    _need([c["set"], c["index"]] in c["choice"])
                if "narrowing" in c:
                    _need(any(n["id"] == c["narrowing"] and n["set"] == c["set"] for n in route.narrowings))
        for d in row["dead_readings"] or []:
            _need([d["set"], d["index"]] in candidates)
            _need(any(e.get("set") == d["set"] and e.get("index") == d["index"] for e in case.get("dead", [])))
        _need(all(c in candidates for c in row["untaken"]))
        for note in row["dead"]:
            _need(any(e.get("set") == note.get("set") and e.get("index") == note.get("index")
                      for e in case.get("dead", [])))
        for line in row["english"]:
            _need(line["frame"] in PLAN_FRAMES and (line["result"] is None or line["result"] in PLAN_RESULTS))
            choice(line["readings"])
            if line["label"] is not None:
                if line["frame"] == "status":
                    _need(any(s["row"]["status_text"] == line["label"] for s in scopes))
                else:
                    label(line["label"])
            if line["model"] is not None:
                from ..ast import decimal_value
                piece, sep, index = line["model"].partition("@")
                _need(sep and index.isascii() and index.isdecimal())
                scope = scopes[decimal_value(index)]
                _need(piece in scope["encoded"] and line["readings"] == scope["encoded"][piece])
                _bound_gaps(line["gaps"], scope["row"]["shown"][piece], route)


def _bound_gaps(gaps, model, route):
    predicates = route.doc["environment"].predicates
    for name, values, answer in gaps:
        _need(name in predicates and predicates[name].regulated is not None and
              predicates[name].regulated.default == "unspecified" and len(values) == len(predicates[name].arguments) and
              all(e in model["domains"].get(sort, []) for sort, e in zip(predicates[name].arguments, values)) and
              type(answer) is bool)
