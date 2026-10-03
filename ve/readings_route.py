"""Admission of content-bearing reading sets by the S1 Lean route, with Python's and Rust's agreement.

`validate` sends the document to `ve_readings_route` (`readings-validate`, docs/spec/composition-s1.md 8.4) and
regenerates the answer in Python (`ve/readings_s1.py`); the two must be byte for byte the same (4.1 rule 3), and
each recorded situation's evaluations are replayed by Rust, untrusted, whose values must agree (10). Lean's
answer is the authority: its diagnostic rejects the document, and a disagreement of Python or Rust with it is
`CheckerUnavailable`, never a rejection and never an admission.

What this checks is the readings head of 4.1 on the decoded units and active sets. Couplings, narrowings and
W2's structural validation of the sets are not decoded by Lean (S1 limitation, DRI ruling 3): `ve/readings.py`
checks them in Python, and the report says so.
"""
from __future__ import annotations

from pathlib import Path

from .backends.lean import run_readings_cases
from .errors import CheckerUnavailable, VEError
from .readings_s1 import Admission, answer, wire

LEAN_ROUTE = Path(__file__).resolve().parents[1] / "lean/.lake/build/bin/ve_readings_route"


def document_wire(units, reading_sets, *, couplings=(), narrowings=()):
    """The document as `ve_readings_route` reads it: every unit with its kind (1.2), content when it has one."""
    document = {"units": [{"id": unit["id"],
                           **({"kind": unit["kind"]} if unit.get("kind") is not None else {}),
                           **({"content": unit["content"]} if unit.get("content") is not None else {})}
                          for unit in units], "reading_sets": reading_sets}
    if couplings:
        document["couplings"] = list(couplings)
    if narrowings:
        document["narrowings"] = list(narrowings)
    return document


def elaborate(environment, units, reading_sets, *, couplings=(), narrowings=(), executable=LEAN_ROUTE):
    """Ask the S2 Lean route to regenerate the admitted document's reading route.

    The choice search is independently repeated in Python. A disagreement is an
    operational failure, never a reading verdict. The S1 admission has already
    checked the content and the W2 validators have checked the restrictions.
    """
    from .readings_s1 import Document, S1Environment
    from .readings_sup import (choice_slot, choices, choice_vocabulary, name_map,
                               superposed_units, uniform_precedence)

    environment = wire(environment)
    document = wire(document_wire(units, reading_sets, couplings=couplings, narrowings=narrowings))
    [row] = run_lean([{"id": "readings-s2", "kind": "readings-elaborate",
                       "environment": environment, "document": document}], executable=executable)
    if row["status"] == "error":
        raise VEError(row["error"])
    senv = S1Environment(environment)
    source = Document(senv, document)
    sets = source.sets
    content_bearing = any(a.content is not None and a.content.kind != "assertion"
                          for reading_set in sets for a in reading_set.candidates)
    if not content_bearing:
        expected_route = "w2"
    elif any(a.content is None for reading_set in sets for a in reading_set.candidates):
        expected_route = "pending"
    elif "norm-defaults@0" in senv.profiles:
        expected_route = "abstention"
    elif senv.chain == "rights":
        expected_route = "enumerated"
    else:
        expected_route = None
    if expected_route is not None and row.get("route") != expected_route:
        raise CheckerUnavailable("ReadingsConformance: Python and Lean differ on the S2 route")
    if (expected_route is None and not uniform_precedence(source) and
            (row.get("route") != "enumerated" or
             not (row.get("finding") or {}).get("cause", "").startswith("precedence under "))):
        raise CheckerUnavailable("ReadingsConformance: Python and Lean differ on S2 precedence")
    if row.get("route") in ("superposed", "enumerated"):
        found, over = choices(sets, couplings, narrowings)
        expected = {"choice_count": "over 64" if over else len(found),
                    "choices": "over" if over else [[[s.id, c[s.id]] for s in sets] for c in found],
                    "narrowings_stale": [n["id"] for n in narrowings if
                                          not any((s.id, s.version) == (n["set"], n["version"])
                                                  for s in sets)]}
        if any(row.get(key) != value for key, value in expected.items()):
            raise CheckerUnavailable("ReadingsConformance: Python and Lean differ on S2 choices")
        if row["route"] == "superposed":
            vocabulary = choice_vocabulary(sets)
            expected_vocabulary = {"sorts": vocabulary["sorts"], "constants": vocabulary["constants"],
                                   "predicates": [{"name": name, "arguments": arguments}
                                                  for name, arguments in vocabulary["predicates"].items()]}
            if row.get("vocabulary") != expected_vocabulary:
                raise CheckerUnavailable("ReadingsConformance: Python and Lean differ on the S2 vocabulary")
            if row.get("units") != superposed_units(source):
                raise CheckerUnavailable("ReadingsConformance: Python and Lean differ on S2 units")
            if row.get("names") != name_map(source):
                raise CheckerUnavailable("ReadingsConformance: Python and Lean differ on S2 names")
            try:
                python_slot = choice_slot(source, couplings, narrowings)
            except VEError as exc:
                raise CheckerUnavailable(f"ReadingsConformance: Python could not regenerate the S2 slot: "
                                         f"{_message(exc)}") from None
            if row.get("slot") != [{"label": label, "ast": formula} for label, formula in python_slot]:
                raise CheckerUnavailable("ReadingsConformance: Python and Lean differ on the S2 slot")
    return {key: value for key, value in row.items() if key not in ("id", "status")}


def run_lean(cases, *, executable=LEAN_ROUTE):
    return run_readings_cases(executable, wire(cases))


def _message(exc):
    return exc.message if hasattr(exc, "message") else str(exc)


def rights_findings(side, label):
    """The rights chain's findings of one candidate's document (4.4): `limitationScope` without certificates
    and `noDistinction`, as the rights route reports them. Python has no implementation of either."""
    from .rights_route import LEAN_ROUTE as RIGHTS_ROUTE
    from .backends.lean import run_soft_case
    units = [{"source_units": list(side.unit_ids)}]
    for c in side.contents:
        if isinstance(c, tuple):
            units.append({"bar": c[1]})
        elif c.kind != "assertion":
            units.append(c.raw)
    environment = wire(side.senv.frame_data)
    scope = run_soft_case(RIGHTS_ROUTE, {"id": "scope", "kind": "rights-scope", "environment": environment,
                                         "document": wire(units), "certificates": {}})
    elaborated = run_soft_case(RIGHTS_ROUTE, {"id": "elaborate", "kind": "rights-elaborate",
                                              "environment": environment, "document": wire(units)})
    return list(scope["findings"]) + list(elaborated["findings"])


def rust_check(admission, s, i, j, situation, Ti, Tj, facts):
    """Replay one pair's evaluations in Rust, untrusted (10): the witness's completion under the shown
    decision, and the other side with its own tables empty. Each value must be Python's, which the comparison
    with Lean's answer then checks."""
    from .backends.rust_jsonl import run
    model, _, _, probe, _ = situation
    witness, other = admission.side(s, i), admission.side(s, j)
    sides = [witness.evaluation_case(model, Ti, probe), other.evaluation_case(model, Tj, probe)]
    try:
        record = run({"id": "readings-evaluate", "kind": "readings-evaluate", "untrusted": True, "sides": sides},
                     timeout=60.0)
    except VEError as exc:
        # Rust is an untrusted shadow: its failure is never a rejection of the document.
        raise CheckerUnavailable(f"ReadingsConformance: Rust did not evaluate the situation: {_message(exc)}") \
            from None
    if record.get("status") != "ok" or record.get("untrusted") is not True:
        raise CheckerUnavailable(f"ReadingsConformance: Rust did not evaluate the situation: {record}")
    for side, tables, values in ((witness, Ti, record["sides"][0]), (other, Tj, record["sides"][1])):
        python_model = side.model(model, tables)
        expected = {"premises": side.valid(python_model), "value": side.observe(python_model, probe)}
        if probe == "holds":
            value = all(values["assertions"])
        elif probe[0] == "outcome":
            value = values["outcomes"][1] if values["outcomes"][0] else None
        else:
            value = any(values["selections"])
        if {"premises": all(values["premises"]), "value": value} != expected:
            raise CheckerUnavailable(f"ReadingsConformance: Rust's untrusted evaluation differs from Python's "
                                     f"on situation {facts['situation']}")


def validate(environment, units, reading_sets, *, executable=LEAN_ROUTE, rust=True):
    """Return Lean's checked reading data, or raise its first diagnostic.

    Transport failure, a malformed response and any disagreement of Python's or Rust's regeneration with Lean's
    answer remain operational failures (`CheckerUnavailable`); only a well-formed Lean error row, which Python
    reproduces, can reject the document.
    """
    # One normalised input (`wire`: an explicit null is an absent field) for Lean and Python alike.
    environment, document = wire(environment), wire(document_wire(units, reading_sets))
    case = {"id": "readings-s1", "kind": "readings-validate", "environment": environment, "document": document}
    rows = run_lean([case], executable=executable)
    row = rows[0]
    if row["status"] == "ok" and (type(row.get("content_bearing")) is not bool or
                                  row["content_bearing"] and type(row.get("sets")) is not list):
        raise CheckerUnavailable("ve_readings_route returned an invalid answer")
    try:
        python = {"status": "ok", **answer(environment, document, chain_findings=rights_findings,
                                           rust=rust_check if rust else None)}
    except CheckerUnavailable:
        raise
    except VEError as exc:
        python = {"status": "error", "error": _message(exc)}
    lean = {key: value for key, value in row.items() if key != "id"}
    if python != lean:
        raise CheckerUnavailable("ReadingsConformance: Python and Lean differ on readings-validate: "
                                 f"Lean {lean.get('error', 'ok')}, Python {python.get('error', 'ok')}")
    if row["status"] == "error":
        raise VEError(row["error"])
    return row


def separate_many(environment, units, reading_sets, queries, *, executable=LEAN_ROUTE):
    """`readings-separate` for each (set, situation id, other reading): Lean's answer per query, or its
    diagnostic (the search's check, 8.5). The document carries the candidate situations."""
    environment, document = wire(environment), wire(document_wire(units, reading_sets))
    cases = [{"id": f"q{n}", "kind": "readings-separate", "environment": environment, "document": document,
              "set": s, "situation": sid, "other": other} for n, (s, sid, other) in enumerate(queries)]
    return run_lean(cases, executable=executable) if cases else []


# ---------------------------------------------------------------------------------------------------------------
# The report (6) and the English (2), from the checked answer

CHECKED_BY = {
    "lean": "readings@1 admission (4.1 to 4.4), every recorded separation (4.5) and the findings (4.6): "
            "ve_readings_route readings-validate; S2 route and restrictions: readings-elaborate",
    "python": "W2 structure of the reading sets and regeneration of S1 admission; "
              "S2 choices and choice vocabulary compared with Lean",
    "rust": "untrusted evaluation of every recorded situation (10)",
    "not_certified": "SeparatedByDecisionOnly: decision_only_sound is not proved (DRI ruling 2)"}


def _probe_form(entry):
    probe = entry["probe"]
    return "holds" if probe == "holds" else "outcome" if "outcome" in probe else "selects"


def report(doc):
    """Section 6 for the content-bearing sets of a loaded document, or None."""
    row = doc.get("readings_s1")
    if row is None or not row.get("content_bearing"):
        return None
    english = Wording(doc)
    sets = []
    separations = {"outcome": 0, "selects": 0, "holds": 0}
    findings = {"SeparatedByDecisionOnly": 0, "SeparatedByActOnly": 0}
    pending = 0
    for entry in row["sets"]:
        reading_set = english.set_raw(entry["set"])
        pairs = []
        for pair in english.unordered_pairs(entry):
            situation = reading_set["situations"][pair["pair"]["situation"]]
            separations[_probe_form(situation)] += 1
            wording, text = english.pair(entry, pair)
            pairs.append({"readings": [pair["reading"], pair["other"]], "situation": pair["pair"]["situation"],
                          "probe": _probe_form(situation), "wording": wording, "text": text})
        for finding in entry["findings"]:
            findings[finding.split(":", 1)[0]] += 1
        pending += sum(c["pending"] for c in entry["candidates"])
        sets.append({"set": entry["set"], "version": entry["version"], "unit": reading_set["unit"],
                     "candidates": [{"id": c["id"], "index": c["index"], "pending": c["pending"],
                                     **({"chain_findings": c["findings"]} if not c["pending"] else {})}
                                    for c in entry["candidates"]],
                     "pairs": pairs, "findings": entry["findings"],
                     "not_certified": [f for f in entry["findings"] if f.endswith("(not certified)")]})
    s2 = doc.get("readings_s2") or {"route": "pending"}
    result = {"checked_by": CHECKED_BY, "sets": sets, "separations": separations, "findings": findings,
            "pending_candidates": pending,
            "couplings": len({item["axis"] for item in doc["meta"].get("couplings", [])}),
            "route": s2["route"], "status": "UNKNOWN: superposition pending"}
    if s2["route"] in ("superposed", "enumerated"):
        result.update(choice_count=s2["choice_count"], narrowings_stale=s2["narrowings_stale"],
                      reading_premises=[entry["label"] for entry in s2.get("slot", [])],
                      dead_readings=[], not_superposable=s2["finding"])
        if "sizes" in s2:
            result["sizes"] = s2["sizes"]
    return result


class Wording:
    """The wordings of 2.3 for the pairs of a checked answer, filled from checked data only."""

    def __init__(self, doc):
        from .english import EnglishVocabulary
        self.doc = doc
        self.environment = doc["environment"].to_dict()
        self.document = document_wire(doc["units"], doc["meta"].get("reading_sets", []))
        self.admission = Admission(self.environment, self.document)
        self.words = EnglishVocabulary(self.admission.senv.frame)
        self.numbers = {unit["id"]: n for n, unit in enumerate(doc["units"], 1)}

    def set_raw(self, set_id):
        return self.admission.doc.set_by_id(set_id).raw

    @staticmethod
    def unordered_pairs(entry):
        seen, out = set(), []
        for pair in entry["pairs"]:
            key = frozenset((pair["reading"], pair["other"]))
            if key not in seen:
                seen.add(key)
                out.append(pair)
        return out

    # -- slots (2.1)

    def reading_names(self, set_id):
        """`<reading>`: the deontic verb in italics when the candidates differ only in it, else `reading <i>`."""
        from .norm_english import render_rule_sentence
        from .softnorms import decode_rule
        R = self.admission.doc.set_by_id(set_id)
        names = [f"reading {i + 1}" for i in range(len(R.candidates))]
        if not all(a.content is not None and a.content.kind == "norm" for a in R.candidates):
            return names
        env = self.admission.side(set_id, 0).soft.env
        verbs, frames = [], []
        for a in R.candidates:
            rule = decode_rule(env, {"norm": a.content.body})
            sentence = render_rule_sentence(rule, env)
            verb = _modal(env, rule)
            if f" {verb} " not in sentence:
                return names
            verbs.append(verb)
            frames.append(sentence.replace(f" {verb} ", " _ ", 1))
        if len(set(frames)) == 1 and len(set(verbs)) == len(verbs):
            return [f"*{verb}*" for verb in verbs]
        return names

    def decider(self, value):
        who = value or "unstated"
        return "the decider" if who == "unstated" else who

    def subject(self, row):
        from .readings_english import subject
        return subject(row)

    def situation_text(self, set_id, witness, entry):
        """`<situation>`: elements by sort then name, true base tuples, then each decision supposed."""
        from .ast import formula_from_data  # noqa: F401  (vocabulary is the frame's)
        base = entry["base"]
        facts = []
        for sort in sorted(base["domains"]):
            noun = self.words.sorts[sort]
            for name in sorted(base["domains"][sort]):
                facts.append(f"{name} is {_article(noun)} {noun}")
        for predicate in sorted(base["relations"]):
            for row in sorted(base["relations"][predicate]):
                facts.append(self.words.predicates[predicate].format(*row))
        for table, own in [(t, False) for t in entry["fixed"]] + [(t, True) for t in entry["decisions"]]:
            for row in table["tuples"]:
                facts.append("suppose " + self.decision(set_id, witness, table["key"], row, own))
        return "; ".join(facts) if facts else "nothing exists"

    def decision(self, set_id, witness, key_json_value, row, own):
        """`<decision>` of 2.1."""
        from .readings_s1 import decode_key
        key = decode_key(key_json_value, "invalid key")
        tuple_text = self.subject(row)
        side = self.admission.side(set_id, witness)
        sd = side.soft
        if key[0] in ("excepted", "off"):
            rule = next((r for r, name, bearer in side.keyed_rules() if name == key[1] and bearer == key[2]), None)
            sentence = "this sentence" if own else f"sentence {self.rule_unit(key[1])}"
            if key[0] == "off":
                return f"{key[3]} has turned {sentence} off for {tuple_text}"
            decided = (rule.exception or {}).get("decided_by") if rule is not None else None
            who = self.decider(decided or sd.env.soft.get("exception_decider"))
            target = "the exception" if own else f"the exception to {sentence}"
            return f"{who} decides {target} applies to {tuple_text}"
        if key[0] == "outweighs":
            who = self.decider(sd.env.soft["outranking"].get("decided_by"))
            return f"{who} decides that {key[2]} outweighs {key[3]} for {tuple_text}"
        rd = side.rights
        if key[0] == "lim":
            name = rd.limitation_names[(key[1], key[2])]
            limit = next(item for item in rd.limitations if item["name"] == key[1])
            who = limit["decided_by"]
        elif key[0] == "cond":
            name = rd.condition_names[(key[1], key[2], key[3])]
            limit = next(item for item in rd.limitations if item["name"] == key[1])
            condition = next(item for item in limit["conditions"] if item["name"] == key[3])
            who = condition.get("decided_by") or limit["decided_by"]
        else:
            name = rd.bar_names[key[1]]
            who = rd.bar["decided_by"]
        return f"{self.decider(who)} decides that " + rd.wordings[name].format(*row)

    def rule_unit(self, rule_name):
        for unit in self.doc["units"]:
            content = unit.get("content")
            if type(content) is dict and type(content.get("norm")) is dict and content["norm"].get("name") == rule_name:
                return self.numbers[unit["id"]]
        return "?"

    # -- which wording a pair gets (2.3)

    def pair(self, entry, pair):
        """(wording number, text) for one unordered pair."""
        from . import readings_english as E
        set_id = entry["set"]
        R = self.admission.doc.set_by_id(set_id)
        situation = R.situations[pair["pair"]["situation"]]
        facts = pair["pair"]
        ids = [a.id for a in R.candidates]
        i, j = ids.index(facts["witness"]), ids.index(pair["other"] if pair["reading"] == facts["witness"]
                                                       else pair["reading"])
        names = self.reading_names(set_id)
        lines = []
        twins = self.twins(set_id, i, j)
        source_word = self.source_word(R.raw)
        probe = situation["probe"]
        value = situation["value"]
        if probe != "holds" and "outcome" in probe:
            predicate = probe["outcome"]["predicate"]
            row = probe["outcome"]["tuple"]
            role = self.admission.senv.regulated[predicate].regulated.role
            if (twins is not None and source_word is not None and facts["witness_admissible"]
                    and facts["other_admissible"] and facts.get("other_value") is not None
                    and facts["witness_value"] is not None and facts["other_value"] != facts["witness_value"]
                    and twins[1] == i):
                strict, default = twins
                strict_value, default_value = facts["other_value"], facts["witness_value"]
                paraphrases = [self.paraphrase(set_id, k) for k in (strict, default)]
                rule = R.candidates[default].content.body
                who = ((rule.get("exception") or {}).get("decided_by")
                       or self.admission.side(set_id, default).soft.env.soft.get("exception_decider") or "unstated")
                lines.append(E.force_twin_sentence(source_word, *paraphrases, who, tuple(row), role,
                                                   strict_value, default_value))
                lines += self.e22_e23(set_id, strict, default)
                if self.admission.decision_only(set_id, strict, default) is not None:
                    lines.append(E.decision_only_sentence(who))
                return "E14", " ".join(lines)
            text = E.outcome_pair_sentence(self.situation_text(set_id, i, situation), names[i], names[j], role,
                                           row[0], value, other_admissible=facts["other_admissible"],
                                           other_value=facts.get("other_value"))
            return "E19", text
        if probe == "holds" and all(R.candidates[k].content.kind == "assertion" for k in (i, j)):
            true, false = (names[i], names[j]) if value else (names[j], names[i])
            return "E21", E.assertion_pair_sentence(self.situation_text(set_id, i, situation), true, false)
        return "E24", E.E24

    def twins(self, set_id, i, j):
        """(strict index, default index) when the pair is force twins (1.7), else None."""
        from .readings_s1 import force_twins
        R = self.admission.doc.set_by_id(set_id)
        ci, cj = R.candidates[i].content, R.candidates[j].content
        if force_twins(ci, cj) is not None:
            return (i, j)
        if force_twins(cj, ci) is not None:
            return (j, i)
        return None

    def paraphrase(self, set_id, k):
        """The canonical VE sentence of the twin rule under one reading, without its header (2.1)."""
        from .norm_english import render_rule_sentence
        from .softnorms import decode_rule
        side = self.admission.side(set_id, k)
        content = self.admission.doc.set_by_id(set_id).candidates[k].content
        body = content.body if content.kind == "norm" else next(
            line["norm"] for line in content.lines() if type(line.get("norm")) is dict)
        return render_rule_sentence(decode_rule(side.soft.env, {"norm": body}), side.soft.env)

    def source_word(self, raw):
        from .readings import source_word_text
        span = raw.get("source_word")
        if span is None:
            return None
        unit = next(u for u in self.doc["units"] if u["id"] == raw["unit"])
        return source_word_text(self.doc["source"], span, unit["span"])

    def e22_e23(self, set_id, strict, default):
        """E22 and E23 under exactly their conditions (2.2), on the default reading's document."""
        from . import readings_english as E
        side = self.admission.side(set_id, default)
        sd = side.soft
        rules = list(sd.rules)
        twin_name = self.admission.doc.set_by_id(set_id).candidates[default].content.body["name"]
        twin = next((r for r in rules if r.core.name == twin_name), None)
        if twin is None or any(twin_name in r.core.over for r in rules):
            return []
        related = _precedence_related(rules, twin_name)
        act = _act(sd, twin)
        out = []
        if any(r.mode == "strict" and r.core.name != twin_name and _act(sd, r) == act
               and sd._incompatible(r, twin) and r.core.name not in related for r in rules):
            out.append(E.E22)
        if sd.env.soft["outranking"]["mode"] == "strict" and any(
                r.mode == "default" and r.core.name != twin_name and _act(sd, r) == act
                and (r.core.predicate == twin.core.predicate or sd._incompatible(r, twin))
                and r.core.name not in related for r in rules):
            out.append(E.E23)
        return out

    def set_lines(self, unit_id):
        """The English shown under a content-bearing set (2.3): each pair's wording, then E16 for the
        `SeparatedByActOnly` finding."""
        from . import readings_english as E
        row = self.doc.get("readings_s1")
        lines = []
        for entry in row["sets"]:
            R = self.admission.doc.set_by_id(entry["set"])
            if R.unit != unit_id:
                continue
            for pair in self.unordered_pairs(entry):
                lines.append(self.pair(entry, pair)[1])
            for finding in entry["findings"]:
                if finding.startswith("SeparatedByActOnly:"):
                    i, j = (int(x) for x in finding.split(":", 2)[2].split(","))
                    acts = [self.act_phrase(entry["set"], k) for k in (i, j)]
                    lines.append(E.act_only_sentence(*acts))
        return lines

    def act_phrase(self, set_id, k):
        from .readings_s1 import content_acts
        side = self.admission.side(set_id, k)
        content = self.admission.doc.set_by_id(set_id).candidates[k].content
        [act] = content_acts(side, content)
        phrase = side.soft.env.predicates[act].regulated.act or act
        return " ".join(word for word in phrase.split() if not (word.startswith("{") and word.endswith("}")))


def _article(noun):
    """`a` or `an` by the sound of the noun's first letters (`a user`, `an agent`, `an hour`)."""
    word = noun.lower()
    if word.startswith(("uni", "use", "usu", "uti", "eu", "one", "once")):
        return "a"
    if word.startswith(("hour", "honest", "honour", "heir")):
        return "an"
    return "an" if word[:1] in "aeiou" else "a"


def _modal(env, rule):
    reg = env.predicates[rule.core.predicate].regulated
    if rule.mode == "default":
        return ("should" if rule.core.sign else "generally need not") if reg.role == "obligation" else (
            "generally may" if rule.core.sign else "should not")
    return ("must" if rule.core.sign else "need not") if reg.role == "obligation" else (
        "may" if rule.core.sign else "must not")


def _act(sd, rule):
    from .readings_s1 import _act_key
    return _act_key(sd.env, rule.core.predicate)


def _precedence_related(rules, name):
    """The rules related to `name` by precedence, in either direction, through any chain."""
    over = {r.core.name: set(r.core.over) for r in rules}
    below = {r.core.name: {o for o, parents in over.items() if r.core.name in parents} for r in rules}
    related = set()
    for edges in (over, below):
        frontier = [name]
        while frontier:
            current = frontier.pop()
            for nxt in edges.get(current, ()):
                if nxt not in related:
                    related.add(nxt)
                    frontier.append(nxt)
    related.discard(name)
    return related


__all__ = ["Admission", "CHECKED_BY", "Wording", "document_wire", "report", "rights_findings", "run_lean",
           "rust_check", "separate_many", "validate"]
