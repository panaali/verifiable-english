"""Admission of content-bearing reading sets by the S1 Lean route, with Python's and Rust's agreement.

`validate` sends the document to `ve_readings_route` (`readings-validate`, docs/spec/composition-s1.md 8.4) and
regenerates the answer in Python (`ve/readings_s1.py`); the two must be byte for byte the same (4.1 rule 3), and
each recorded situation's evaluations are replayed by Rust, untrusted, whose values must agree (10). Lean's
answer is the authority: its diagnostic rejects the document, and a disagreement of Python or Rust with it is
`CheckerUnavailable`, never a rejection and never an admission.

`validate` retains S1's scope: couplings, narrowings and W2's structural checks are handled by Python there.
`elaborate` runs after those checks and compares S2's decoded restrictions, choice search and generated slot with
Python's independent regeneration. Verdict search is still separate from this admission path.
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

    The choice search and the generated vocabulary, units, names and slot are
    independently repeated in Python. A disagreement is an operational failure,
    never a reading verdict. S1 has already admitted the content and the W2
    validators have checked the restrictions.
    """
    from .readings_s1 import Document, S1Environment
    from .readings_sup import (choices, choice_vocabulary, choices_checked, first_nonuniform, name_map,
                               route_refusal, sup_ready, superposed_elaboration, superposed_units)

    environment = wire(environment)
    document = wire(document_wire(units, reading_sets, couplings=couplings, narrowings=narrowings))
    [row] = run_lean([{"id": "readings-s2", "kind": "readings-elaborate",
                       "environment": environment, "document": document}], executable=executable,
                     timeout=300)
    try:
        senv = S1Environment(environment)
        source = Document(senv, document)
    except VEError:
        if row["status"] == "error":
            raise VEError(row["error"]) from None
        raise
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
    regenerated = None
    cause = None
    expected_text = None
    if expected_route is None:
        if not sup_ready(sets, couplings, narrowings, doc=source):
            expected_route, cause = "enumerated", "the shape of the reading sets"
        elif (first := first_nonuniform(source)) is not None:
            expected_route, cause = "enumerated", f"precedence under {first[1]}"
            expected_text = f"ReadingsNotSuperposable: {first[0]}"
        else:
            try:
                regenerated = superposed_elaboration(source, couplings, narrowings)
            except (VEError, SyntaxError) as exc:
                expected_route, cause = "enumerated", _message(exc)
            else:
                expected_route = "superposed"
    # 4.1 steps 3 and 5: before any verdict, no compatible choice is `ReadingsUnsatisfiable` and a compatible choice
    # whose document the chain refuses is that diagnostic under the choice (DRI ruling 5). Lean must refuse exactly
    # these documents, with these texts.
    refusal = route_refusal(source, expected_route, couplings, narrowings)
    if row["status"] == "error":
        routed = row["error"].startswith("ReadingsUnsatisfiable: ") or " under " in row["error"]
        if refusal is not None or routed:
            if row["error"] != refusal:
                raise CheckerUnavailable("ReadingsConformance: Python and Lean differ on the S2 refusal: "
                                         f"Lean {row['error']}, Python {refusal or 'none'}")
        raise VEError(row["error"])
    if refusal is not None:
        raise CheckerUnavailable(f"ReadingsConformance: Python and Lean differ on the S2 refusal: Lean none, "
                                 f"Python {refusal}")
    if row.get("route") != expected_route:
        raise CheckerUnavailable("ReadingsConformance: Python and Lean differ on the S2 route")
    if cause is not None and (row.get("finding") or {}).get("cause") != cause:
        raise CheckerUnavailable("ReadingsConformance: Python and Lean differ on the S2 finding")
    if expected_text is not None and (row.get("finding") or {}).get("text") != expected_text:
        raise CheckerUnavailable("ReadingsConformance: Python and Lean differ on S2 precedence")
    if row.get("route") in ("superposed", "enumerated"):
        found, over = choices(sets, couplings, narrowings)
        expected = {"choice_count": "over 64" if over else len(found),
                    "choices": "over" if over else [[[s.id, c[s.id]] for s in sets] for c in found],
                    "choices_checked": choices_checked(sets, row["route"], couplings, narrowings),
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
            python_slot, python_sizes = regenerated
            if row.get("slot") != [{"label": label, "ast": formula} for label, formula in python_slot]:
                raise CheckerUnavailable("ReadingsConformance: Python and Lean differ on the S2 slot")
            if row.get("sizes") != python_sizes:
                raise CheckerUnavailable("ReadingsConformance: Python and Lean differ on S2 sizes")
    return {key: value for key, value in row.items() if key not in ("id", "status")}


def run_lean(cases, *, executable=LEAN_ROUTE, timeout=120):
    return run_readings_cases(executable, wire(cases), timeout=timeout)


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
    rows = run_lean([case], executable=executable, timeout=300)
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
              "S2 choices, units, names, slot and sizes compared with Lean",
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
            "route": s2["route"]}
    from .readings_verdicts import context
    route = context(doc)
    if s2["route"] in ("superposed", "enumerated"):
        result.update(choice_count=s2["choice_count"], choices_checked=s2["choices_checked"],
                      narrowings_stale=s2["narrowings_stale"],
                      reading_premises=[entry["label"] for entry in s2.get("slot", [])],
                      not_superposable=s2["finding"])
        if "sizes" in s2:
            result["sizes"] = s2["sizes"]
    if route is not None:
        # `status`, `conflict` and `dead_readings` (6): each from checked evidence; `dead_readings` is null when
        # the compatible choices were too many to enumerate, never an unchecked empty list.
        result.update(route.report_fields())
        result["english"] = report_english(doc, route)
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
                return "E14", _s1_gated("E14", " ".join(lines))
            text = E.outcome_pair_sentence(self.situation_text(set_id, i, situation), names[i], names[j], role,
                                           row[0], value, other_admissible=facts["other_admissible"],
                                           other_value=facts.get("other_value"))
            return "E19", _s1_gated("E19", text)
        if probe == "holds" and all(R.candidates[k].content.kind == "assertion" for k in (i, j)):
            true, false = (names[i], names[j]) if value else (names[j], names[i])
            return "E21", _s1_gated("E19", E.assertion_pair_sentence(self.situation_text(set_id, i, situation),
                                                                     true, false))
        return "E24", _s1_gated("E24", E.E24)

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
                    lines.append(_s1_gated("E16", E.act_only_sentence(*acts)))
        return lines

    def act_phrase(self, set_id, k):
        from .readings_s1 import content_acts
        side = self.admission.side(set_id, k)
        content = self.admission.doc.set_by_id(set_id).candidates[k].content
        [act] = content_acts(side, content)
        phrase = side.soft.env.predicates[act].regulated.act or act
        return " ".join(word for word in phrase.split() if not (word.startswith("{") and word.endswith("}")))


def _s1_gated(lead, text):
    """S1's report sentences read against every registered wording, S2a's included (2.2 and composition.md 2): the
    sentence has exactly one derivation, by its own lead (E19 to E21 share one lead), so no sentence of S1 can be
    read as one of S2a's. Their own slots are S1's (composition-s1.md 2.1) and are read as any text here."""
    from .readings_s2_english import Slots, derivations
    found = derivations(text, Slots())
    if len(found) != 1 or found[0][0] != lead:
        raise VEError(f"InvalidInput: S1 wording {lead} has {len(found)} derivations: {text}")
    return text


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



# ---------------------------------------------------------------------------------------------------------------
# The English of S2a (composition-s2.md 2.3), from checked verdicts only, every sentence through W7's gate


def report_english(doc, route):
    """The sentences of 2.3 for the report's verdicts across readings: the conflict status, the premise status, the
    dead readings and the finding of 1.8."""
    from .readings_verdicts import Enumerated, Superposed
    if not isinstance(route, (Superposed, Enumerated)):
        return []
    return S2Wording(doc, route).report()


def query_english(doc, conclusion, data):
    """The sentences of 2.3 for one ALL, SOME or NONE query across readings."""
    from .readings_verdicts import Enumerated, Superposed, context
    route = context(doc)
    if not isinstance(route, (Superposed, Enumerated)):
        return []
    return S2Wording(doc, route).query(conclusion, data)


class S2Wording:
    """2.1's slots on one document: sentence numbers, reading names, conclusions and pulled situations."""

    def __init__(self, doc, route):
        from . import readings_s2_english as E
        self.E = E
        self.doc, self.route = doc, route
        self.s1 = Wording(doc)
        self.numbers = {unit["id"]: n for n, unit in enumerate(doc["units"], 1)}
        self.sets = route.sets
        self.set_number = {R.id: self.numbers[R.unit] for R in self.sets}
        self.names = {R.id: self.s1.reading_names(R.id) for R in self.sets}
        self.slots = E.Slots(numbers={str(n) for n in self.numbers.values()},
                             readings={name for names in self.names.values() for name in names})
        senv = self.s1.admission.senv
        self.frame = senv.frame
        self.author = set(senv.author_environment().predicates)
        self.decisions = self._decision_names()

    # -- slots

    def readings(self, choice):
        """[(sentence number, reading name)] for a choice or assumed list, in source order."""
        chosen = {s: i for s, i in choice}
        return [(self.set_number[R.id], self.names[R.id][chosen[R.id]]) for R in self.sets if R.id in chosen]

    def conclusion(self, ast):
        """`<conclusion>`: the conclusion's canonical sentence on the existing English surface, in italics; it is
        read back by that surface's all-derivations parser to the conclusion itself before it is shown."""
        from .ast import Document as Formulas, formula_from_data
        from .english import parse_english
        from .printer import render
        formula = formula_from_data(self.frame, ast)
        text = render(Formulas((formula,)), self.frame, "ve_english").strip()
        if parse_english(self.frame, text).formulas != (formula,):
            raise VEError("InvalidInput: the conclusion's sentence does not read back to the conclusion")
        slot = f"*{text}*"
        self.slots.conclusions.add(slot)
        return slot

    def _decision_names(self):
        """Every decision predicate a rule of the document or of a candidate generates, with what it decides:
        (kind, rule name, party or ranks, owner (set, index) or None)."""
        from .readings_sup import position, qualify
        out = {}

        def add(rule, owner, name):
            root = name.replace("-", "_")
            if rule.get("mode", "strict") == "default":
                out[f"soft__excepted__{root}"] = ("excepted", rule, None, owner)
            for party in rule.get("alterable", []):
                out[f"soft__off__{root}__{party}"] = ("off", rule, party, owner)

        source = self.route.source
        for _, content in source.fixed_units():
            for rule in content.rules():
                add(rule, None, rule["name"])
        for R in self.sets:
            for i, a in enumerate(R.candidates):
                for rule in (a.content.rules() if a.content is not None else []):
                    add(rule, (R.id, i), rule["name"])
                    add(rule, (R.id, i), qualify(position(self.sets, R.id, i), rule["name"]))
        return out

    def situation(self, data, choice):
        """`<situation>` (2.1): the pulled situation of a model of the reading `choice` names: the elements by
        sort, the author's base facts, and each decision as a supposition attributed to who decides; no choice
        vocabulary and no generated name."""
        words = self.s1.words
        facts = []
        for sort in sorted(data["domains"]):
            if sort == "ve__reading":
                continue
            noun = words.sorts[sort]
            for name in sorted(data["domains"][sort]):
                facts.append(f"{name} is {_article(noun)} {noun}")
        relations = data.get("relations", {})
        for predicate in sorted(relations):
            if predicate in self.author:
                for row in sorted(relations[predicate]):
                    facts.append(words.predicates[predicate].format(*row))
        chosen = {(s, i) for s, i in choice}
        own = self._choice_decisions(choice)
        for predicate in sorted(relations):
            for row in sorted(relations[predicate]):
                phrase = (self._decision(predicate, row, chosen) if own is None else
                          self._choice_decision(own, predicate, row, chosen))
                if phrase is not None:
                    facts.append("suppose " + phrase)
                elif predicate not in self.author and predicate.startswith(_DECISION_PREFIXES):
                    # Review A of compose-s2 looprecheck2: a decision the situation needs is never left out.
                    raise VEError(f"InvalidInput: a situation's decision table {predicate} has no wording")
        text = "; ".join(facts) if facts else "nothing exists"
        self.slots.situations.add(text)
        return text

    def _choice_decisions(self, choice):
        """On the enumerated route a model is one of the choice's own document, so its decision tables are the ones
        that document generates (`gen_keys`: exceptions, switches, outweighing, limitations, their conditions and
        the bar, on every chain): (the choice's side, generated name → key). None on the superposed route."""
        from .readings_verdicts import Enumerated
        if not isinstance(self.route, Enumerated):
            return None
        own = self.route._choice({s: i for s, i in choice})
        if own.chain == "norms":
            return own.side, {}
        return own.side, {generated: key for key, generated, _ in own.side.gen_keys()}

    def _rule_owner(self, name, chosen):
        """(True, None) when the rule named `name` is a candidate's of the choice, (False, n) when sentence n's. Every
        rule a content states is found (`Content.rules`: a norm, and every rule-bearing field of every line kind, a
        power line's liberty and recognition included; compose-s2 fix4 A2)."""
        def names(content):
            return [] if content is None else [rule["name"] for rule in content.rules()]
        for R in self.sets:
            for i, a in enumerate(R.candidates):
                if (R.id, i) in chosen and name in names(a.content):
                    return True, None
        for uid, content in self.route.source.fixed_units():
            if name in names(content):
                return False, self.numbers[uid]
        raise VEError(f"InvalidInput: no sentence of the reading states rule {name}")

    def _choice_decision(self, own, predicate, row, chosen):
        """`<decision>` (2.1) for a decision table of a choice's own document, as S1 words it for a reading."""
        side, keys = own
        key = keys.get(predicate)
        if key is None:
            return None
        subject = _series(list(row))
        soft = side.soft.env.soft or {}
        if key[0] in ("excepted", "off"):
            mine, number = self._rule_owner(key[1], chosen)
            sentence = "this sentence" if mine else f"sentence {number}"
            if key[0] == "off":
                return f"{key[3]} has turned {sentence} off for {subject}"
            rule = next((r for r, name, bearer in side.keyed_rules() if name == key[1] and bearer == key[2]), None)
            decided = ((rule.exception or {}).get("decided_by") if rule is not None else None) or \
                soft.get("exception_decider")
            target = "the exception" if mine else f"the exception to {sentence}"
            return f"{self.s1.decider(decided)} decides {target} applies to {subject}"
        if key[0] == "outweighs":
            who = self.s1.decider(soft.get("outranking", {}).get("decided_by"))
            return f"{who} decides that {key[2]} outweighs {key[3]} for {subject}"
        rd = side.rights
        if key[0] == "lim":
            limit = next(item for item in rd.limitations if item["name"] == key[1])
            who = limit["decided_by"]
        elif key[0] == "cond":
            limit = next(item for item in rd.limitations if item["name"] == key[1])
            condition = next(item for item in limit["conditions"] if item["name"] == key[3])
            who = condition.get("decided_by") or limit["decided_by"]
        else:
            who = rd.bar["decided_by"]
        return f"{self.s1.decider(who)} decides that " + rd.wordings[predicate].format(*row)

    def _decision(self, predicate, row, chosen):
        subject = _series(list(row))
        soft = getattr(self.frame, "soft", None) or {}
        if predicate.startswith("soft__outweighs__"):
            _, _, low, high, _ = predicate.split("__", 4)
            outranking = soft.get("outranking", {})
            return f"{self.s1.decider(outranking.get('decided_by'))} decides that {low} outweighs {high} for {subject}"
        entry = self.decisions.get(predicate)
        if entry is None:
            return None
        kind, rule, party, owner = entry
        own = owner is not None
        if own and owner not in chosen:
            return None  # an unchosen reading's table is empty (quiescence); never shown
        sentence = "this sentence" if own else f"sentence {self.s1.rule_unit(rule['name'])}"
        if kind == "off":
            return f"{party} has turned {sentence} off for {subject}"
        decided = (rule.get("exception") or {}).get("decided_by") or soft.get("exception_decider")
        target = "the exception" if own else f"the exception to {sentence}"
        return f"{self.s1.decider(decided)} decides {target} applies to {subject}"

    def classification(self, conflict):
        """The lower route's classification line of a witness (R4 follows it), each rule of a candidate named as
        the author named it with ` under <set>@<v>:<i>` (6)."""
        sorts, values = conflict.get("sorts", []), conflict["tuple"]
        setting = ", ".join(f"{sort} {value}" for sort, value in zip(sorts, values))
        target = conflict["target"]
        kind = f"pair conflict on {target}" if "->" in target else f"strict collision on {target}"
        rules = conflict.get("selected")
        if not rules:
            return f"CONFLICT: {kind} at {setting}"
        return (f"CONFLICT: {kind} at {setting}: " +
                "; ".join(f"rule {self._rule_name(name)} {verb}" for name, verb in rules))

    def _rule_name(self, name):
        versions = {R.id: R.version for R in self.sets}
        for entry in self.route.row.get("names", []):
            for candidate in entry["candidates"]:
                for original, qualified in candidate["names"]:
                    if qualified == name:
                        return f"{original} under {entry['set']}@{versions[entry['set']]}:{candidate['index']}"
        return name

    # -- E3's lines (2.3 item 1)

    def provided(self, used):
        E, lines = self.E, []
        quiet = False
        for label in used:
            if label.endswith(":one"):
                set_id = label.split(":", 1)[1].rsplit("@", 1)[0]
                R = next(R for R in self.sets if R.id == set_id)
                lines.append(E.one_reading(self.set_number[set_id], len(R.candidates), self.slots))
            elif label.endswith(":quiet") or label.startswith("readings:quiet:"):
                quiet = True
            elif label.startswith("coupling:"):
                from .readings_english import coupling_sentence
                coupling = next(c for c in self.route.couplings if c["id"] == label.split(":", 1)[1])
                sets = {R.id: {"unit": R.unit} for R in self.sets}
                lines.append(E.gated("E5", coupling_sentence(coupling, sets, self.doc["units"]), self.slots))
            elif label.startswith("narrowing:"):
                narrowing = next(n for n in self.route.narrowings if n["id"] == label.split(":", 1)[1])
                R = next(R for R in self.sets if (R.id, R.version) == (narrowing["set"], narrowing["version"]))
                cited = [self.numbers[u] for u in narrowing["reason_spans"]]
                for i, a in enumerate(R.candidates):
                    if a.id not in narrowing["keeps"]:
                        lines.append(E.narrowed(self.set_number[R.id], self.names[R.id][i], cited, self.slots))
        if quiet:
            lines.append(E.quiet(self.slots))
        return ([E.provided(self.slots)] + lines) if lines else []

    def independent(self, mentions):
        return [self.E.independent(self.set_number[R.id], self.slots) for R in self.sets if R.id not in mentions]

    def _mentions(self, used):
        """The open sets the used labels mention: a slot leaf by its bit predicates, and on the enumerated route a
        coupling or narrowing label by the sets it restricts."""
        from .readings_sup import bit_name, bits_of, in_force
        asts = {entry["label"]: entry["ast"] for entry in self.route.row.get("slot", [])}
        restricted = set()
        for label in used:
            kind, _, ident = label.partition(":")
            if kind == "coupling":
                coupling = next(c for c in self.route.couplings if c["id"] == ident)
                restricted.update(ref["set"] for ref in coupling["sets"])
            elif kind == "narrowing":
                narrowing = next(n for n in self.route.narrowings if n["id"] == ident)
                restricted.update(R.id for R in self.sets if in_force(R, narrowing))
        out = []
        for position, R in enumerate(self.sets, 1):
            bits = {bit_name(position, j) for j in range(bits_of(len(R.candidates)))}
            if R.id in restricted or any(bits & _predicates(asts.get(label, [])) for label in used):
                out.append(R.id)
        return out

    # -- the report (2.3 items 1, 3 and 6)

    def report(self):
        E, route, lines = self.E, self.route, []
        k = len(self.sets)
        finding = route.row.get("finding")
        if finding is not None:
            sets = finding["text"].split(": ", 1)[1].split(", ")
            lines.append(E.not_superposed([self.set_number[s] for s in sets], self.slots))
        conflict = route.conflict(())
        if conflict["status"] == "CONFLICT-FREE":
            lines.append(E.every_result(k, "conflict_free", self.slots))
            used = self._dependencies(conflict)
            lines += self.provided(used)
            lines += self.independent(self._mentions(used))
        elif conflict["status"] == "CONFLICT" and "model" in conflict:
            lines.append(E.named_result(self.readings(conflict["choice"]), "conflict", self.slots,
                                        situation=self.situation(conflict["model"], conflict["choice"])))
            lines.append(self.classification(conflict))
        elif conflict["status"] == "CONFLICT":
            for witness in conflict.get("witnesses", []):
                lines.append(E.named_result(self.readings(witness["choice"]), "conflict", self.slots,
                                            situation=self.situation(witness["model"], witness["choice"])))
                if witness.get("status_text"):
                    lines.append(witness["status_text"])
        premises = route.premises()
        if premises["status"] == "model" and "model" in premises:
            lines.append(E.named_result(self.readings(premises["choice"]), "premise_model", self.slots,
                                        situation=self.situation(premises["model"], premises["choice"])))
        elif premises["status"] == "INCONSISTENT" and premises.get("evidence") == "certificate":
            # A certificate with A = [] (2.3 item 1): E3 and E13 from what it and its conflict certificates rely on.
            lines.append(E.every_result(k, "inconsistent", self.slots))
            used = self._dependencies(premises)
            lines += self.provided(used)
            lines += self.independent(self._mentions(used))
        for dead in route.dead_readings() or []:
            lines.append(E.dead_reading(self.set_number[dead["set"]], self.names[dead["set"]][dead["index"]],
                                        self.slots))
        return lines

    # -- a query (2.3 items 1, 2, 4, 5 and 7)

    def query(self, conclusion_ast, data):
        E, lines = self.E, []
        k = len(self.sets)
        verdict = data["verdict"]
        # Review A of compose-s2 looprecheck1: a result under named readings is worded under exactly those readings
        # (2.3 item 2, on either route); E10, E26, E27 and E28 speak of every reading and never word one.
        assumed = data.get("assumed") or []
        slot = self.conclusion(conclusion_ast)
        if verdict == "ALL":
            if assumed:
                lines.append(E.named_result(self.readings(assumed), "follows", self.slots, conclusion=slot))
            else:
                lines.append(E.every_result(k, "follows", self.slots, conclusion=slot))
            # Review A1 of compose-s2 fix4: the conditions and the independence statement are both worded from the
            # answer's one dependency set, its conflict certificates' included. Combined over the compatible choices
            # (review A of compose-s2 looprecheck2) the set holds the couplings and narrowings that excluded the
            # others (E3 with E5 and E7), and no independence is claimed.
            used = self._dependencies(data)
            lines += self.provided(used)
            if data.get("evidence") == "certificate":
                lines += self.independent(set(self._mentions(used)) | {s for s, _ in assumed})
        elif verdict == "SOME":
            lines.append(E.named_result(self.readings(data["proof"]["choice"]), "follows", self.slots,
                                        conclusion=slot))
            lines.append(self._countermodel(data["countermodel"]))
        elif verdict == "NOT ALL":
            lines.append(self._countermodel(data["countermodel"]))
        elif verdict == "NONE":
            if k >= 2 and not assumed:
                lines.append(E.none_result(k, self.slots))
            lines += [self._countermodel(c) for c in data["countermodels"]]
            lines += self.provided(self._restrictions(data))
        elif verdict == "UNKNOWN" and "countermodel" in data and data.get("budget") == {"max_choices": 64} \
                and not assumed:
            lines.append(E.over_budget(self.slots))
            lines.append(self._countermodel(data["countermodel"]))
        return lines

    @staticmethod
    def _dependencies(data):
        """The slot labels a Lean-checked answer depends on (`reading_premises_used`, `Superposed._dependencies` on
        the superposed route, the restrictions on the enumerated route); an answer without them is refused, never
        worded as depending on no reading."""
        if "reading_premises_used" not in data:
            raise VEError("InvalidInput: a checked answer's wording needs the reading premises it depends on")
        return data["reading_premises_used"]

    @staticmethod
    def _restrictions(data):
        """The restrictions a combined verdict keeps; a combined verdict without the field is refused, never worded
        as if no coupling or narrowing had selected its choices."""
        if "restrictions" not in data:
            raise VEError("InvalidInput: a verdict combined over the compatible choices needs its restrictions")
        return data["restrictions"]

    def _countermodel(self, counter):
        model = counter.get("model")
        if model is None:
            raise VEError("InvalidInput: a countermodel's wording needs its checked model")
        return self.E.named_result(self.readings(counter["choice"]), "countermodel", self.slots,
                                   situation=self.situation(model, counter["choice"]))


_DECISION_PREFIXES = ("soft__excepted__", "soft__off__", "soft__outweighs__", "rights__")


def _series(values):
    values = list(values)
    if len(values) == 1:
        return values[0]
    if len(values) == 2:
        return f"{values[0]} and {values[1]}"
    return ", ".join(values[:-1]) + " and " + values[-1]


def _predicates(ast):
    out, stack = set(), [ast]
    while stack:
        node = stack.pop()
        if type(node) is list and node:
            if node[0] in ("unary", "binary") and type(node[1]) is str:
                out.add(node[1])
            stack.extend(item for item in node[1:] if type(item) is list)
    return out
