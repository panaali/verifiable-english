"""Admission of content-bearing reading sets by the S1 Lean route, relayed (docs/LEAN-FIRST-PLAN.md rule 2).

`validate` sends the document to `ve_readings_route` (`readings-validate`, docs/spec/composition-s1.md 8.4) and
returns Lean's row, or raises Lean's diagnostic with its text verbatim. Lean is the one owner of the answer: no
Python regeneration and no Rust replay is compared with it any more (lean-first batch 3). A route that cannot
answer, or answers a row that is not bound to the request (its shape, its sets, candidates, readings and
situations), is `CheckerUnavailable`, never a rejection and never an admission.

What Lean checks is the readings head of 4.1 on the decoded units and active sets. Couplings, narrowings and
W2's structural validation of the sets are not decoded by Lean (S1 limitation, DRI ruling 3): `ve/readings.py`
checks them in Python, and the report says so. The English of the report (`Wording`) is built from Lean's row
and Python's construction of the admitted document (`ve/readings_s1.py`).
"""
from __future__ import annotations

import re
from contextlib import contextmanager
from pathlib import Path

from .ast import decimal_value
from .backends.lean import run_readings_cases
from .errors import CheckerUnavailable, VEError
from .readings_s1 import KEY_FIELDS, KEY_OPTIONAL, Decoded, Document, content_bearing, decode_key, wire

LEAN_ROUTE = Path(__file__).resolve().parents[1] / "lean/.lake/build/bin/ve_readings_route"


def document_wire(units, reading_sets):
    """The document as `ve_readings_route` reads it: every unit with its kind (1.2), content when it has one."""
    return {"units": [{"id": unit["id"], "kind": unit["kind"],
                       **({"content": unit["content"]} if unit.get("content") is not None else {})}
                      for unit in units],
            "reading_sets": reading_sets}


def run_lean(cases, *, executable=LEAN_ROUTE):
    return run_readings_cases(executable, wire(cases))


@contextmanager
def _built():
    """Python builds the English of a document Lean admitted (rule 2: Lean validates, Python constructs); a
    construction that fails there is a bug, reported as `CheckerUnavailable`, never as a rejection."""
    try:
        yield
    except CheckerUnavailable:
        raise
    except (VEError, KeyError, TypeError, ValueError, AttributeError, IndexError, StopIteration) as exc:
        raise CheckerUnavailable("ReadingsConstruction: Python could not build the English of the document "
                                 f"Lean admitted: {type(exc).__name__}") from exc


# ---------------------------------------------------------------------------------------------------------------
# The answer's schema and its binding to the request (build checklist 4)
#
# The schema is that of Run.lean's encoders (`validateResult`, `candidateJson`, `keyEntry` with `keyJson`,
# `pairJson`, `setFindings`), checked over the whole row before anything is compared or hashed. The binding then
# checks what the request fixes: the content-bearing sets in source order, every candidate in order with its
# pending state, every ordered pair of candidates neither pending in index order with the situation its
# distinguishing model names and that situation's witness, and the producer's invariants (Lean only answers a
# pair it found separated by an admissible witness showing the recorded value; `other_value` is present exactly
# when the other side owns no key; decisions are the witness's own keys, fixed tables nobody's; findings in
# `setFindings`' text and order). What is left is Lean's alone: which keys a candidate generates, its hash and
# chain findings, the other side's completion and which pairs are findings.

class _Invalid(Exception):
    """A row that is not Lean's answer to this request."""


def _need(condition):
    if not condition:
        raise _Invalid


def _lit(expected):
    return lambda v: type(v) is type(expected) and v == expected


def _obj(required, optional=None):
    optional = optional or {}
    fields = {**required, **optional}
    return lambda v: (type(v) is dict and set(required) <= set(v) <= set(fields)
                      and all(fields[k](item) for k, item in v.items()))


def _arr(item, *, nonempty=False):
    return lambda v: type(v) is list and (bool(v) or not nonempty) and all(item(x) for x in v)


def _either(*schemas):
    return lambda v: any(schema(v) for schema in schemas)


def _str(v):
    return type(v) is str


def _name(v):
    return type(v) is str and v != ""


def _nat(v):
    return type(v) is int and v >= 0


def _bool(v):
    return type(v) is bool


def _digest(v):
    """A sha256 digest as Lean writes one (`CertificateWire.digest`, a situation id): 64 lowercase hex digits."""
    return type(v) is str and len(v) == 64 and all(ch in "0123456789abcdef" for ch in v)


_KEY = _either(*(_obj({f: _name for f in fields if f not in KEY_OPTIONAL},
                      {f: _name for f in fields if f in KEY_OPTIONAL}) for fields in KEY_FIELDS.values()))
_KEY_ENTRY = _obj({"key": _KEY, "name": _name})
_CANDIDATE = _either(
    _obj({"id": _str, "index": _nat, "pending": _lit(True)}),
    _obj({"id": _str, "index": _nat, "pending": _lit(False), "document_hash": _digest,
          "owned": _arr(_KEY_ENTRY), "shared": _arr(_KEY_ENTRY), "findings": _arr(_name)}))
# Lean answers a pair only after `unless f.witnessValid` and `unless f.separated` (setPairs), so both are true and
# the witness's value is the recorded one, never null.
_PAIR_FACTS = _obj({"situation": _digest, "witness": _str, "separated": _lit(True),
                    "witness_admissible": _lit(True), "witness_value": _bool, "other_admissible": _bool},
                   {"other_value": lambda v: v is None or type(v) is bool})
_SET = _obj({"set": _str, "version": _nat, "candidates": _arr(_CANDIDATE, nonempty=True),
             "pairs": _arr(_obj({"reading": _str, "other": _str, "pair": _PAIR_FACTS})), "findings": _arr(_name)})
ROW = _either(_obj({"id": _str, "status": _lit("ok"), "content_bearing": _lit(False)}),
              _obj({"id": _str, "status": _lit("ok"), "content_bearing": _lit(True),
                    "sets": _arr(_SET, nonempty=True)}))

# `setFindings`: `<code>: <set>: <i>, <j>`, with ` (not certified)` on SeparatedByDecisionOnly; per unordered pair
# (i < j) in order, the decision-only finding (either twin first) before the act-only one (i first).
FINDING_RANK = {"SeparatedByDecisionOnly": 0, "SeparatedByActOnly": 1}
_FINDING = re.compile(r"(SeparatedByDecisionOnly|SeparatedByActOnly): (.*): (0|[1-9][0-9]*), (0|[1-9][0-9]*)"
                      r"( \(not certified\))?", re.DOTALL)


def parse_finding(text):
    """(code, set, i, j) of one of Lean's set findings, or None when it is not in `setFindings`' text."""
    m = _FINDING.fullmatch(text)
    if m is None or (m[5] is not None) != (m[1] == "SeparatedByDecisionOnly"):
        return None
    return m[1], m[2], decimal_value(m[3]), decimal_value(m[4])


def _bind(row, document):
    sets = [R for R in Document(None, document).sets if content_bearing(R)]
    _need(row["content_bearing"] is bool(sets))
    if sets:
        _need([(e["set"], e["version"]) for e in row["sets"]] == [(R.id, R.version) for R in sets])
        for entry, R in zip(row["sets"], sets):
            _bind_set(entry, R)


def _bind_set(entry, R):
    candidates = entry["candidates"]
    _need([(c["id"], c["index"], c["pending"]) for c in candidates]
          == [(a.id, n, a.content is None) for n, a in enumerate(R.candidates)])
    _need(len({a.id for a in R.candidates}) == len(R.candidates))
    owned, keys = {}, {}
    for c in candidates:
        if c["pending"]:
            continue
        generated = [decode_key(e["key"]) for e in c["owned"] + c["shared"]]
        _need(len(set(generated)) == len(generated))
        suffix = f" under {R.id}@{R.version}:{c['index']}"
        _need(all(len(f) > len(suffix) and f.endswith(suffix) for f in c["findings"]))
        owned[c["index"]] = {decode_key(e["key"]) for e in c["owned"]}
        keys[c["index"]] = set(generated)
    index = {a.id: n for n, a in enumerate(R.candidates)}
    readings = R.raw["readings"]
    expected = []
    for x, a in enumerate(R.candidates):
        for y, b in enumerate(R.candidates):
            if x != y and a.content is not None and b.content is not None:
                sid = readings[x]["admission"]["distinguishing_models"][b.id]
                expected.append((a.id, b.id, sid, R.situations[sid]["witness"]))
    _need([(p["reading"], p["other"], p["pair"]["situation"], p["pair"]["witness"]) for p in entry["pairs"]]
          == expected)
    for p in entry["pairs"]:
        facts, situation = p["pair"], R.situations[p["pair"]["situation"]]
        _need(facts["witness"] in (p["reading"], p["other"]))
        witness = index[facts["witness"]]
        other = index[p["other"] if facts["witness"] == p["reading"] else p["reading"]]
        _need(type(situation["value"]) is bool and facts["witness_value"] is situation["value"])
        _need(("other_value" in facts) is (not owned[other]))
        # With no key of its own the other side has one completion; separated, it does not show the value.
        _need(not (facts["other_admissible"] and facts.get("other_value") is facts["witness_value"]))
        decisions = [decode_key(t["key"]) for t in situation.get("decisions", [])]
        fixed = [decode_key(t["key"]) for t in situation.get("fixed", [])]
        _need(all(k in owned[witness] for k in decisions))
        _need(all(k not in owned[witness] | owned[other] and k in keys[witness] | keys[other] for k in fixed))
    order = []
    for text in entry["findings"]:
        parsed = parse_finding(text)
        _need(parsed is not None and parsed[1] == R.id)
        code, _, i, j = parsed
        _need(i != j and i in owned and j in owned and (code == "SeparatedByDecisionOnly" or i < j))
        order.append((min(i, j), max(i, j), FINDING_RANK[code]))
    _need(order == sorted(set(order)))


def _check(row, case):
    """Raise `CheckerUnavailable` unless `row` is a well-formed `ok` answer bound to the request. Every failure of
    the check itself (a type the schema missed, a missing request field) is contained here: the answer is then
    not shown to be Lean's, which is operational, never a rejection."""
    try:
        _need(ROW(row) and row["id"] == case["id"])
        _bind(row, case["document"])
    except (_Invalid, TypeError, KeyError, ValueError, AttributeError, IndexError, RecursionError) as exc:
        raise CheckerUnavailable("ve_readings_route returned an invalid answer") from exc


def validate(environment, units, reading_sets, *, executable=LEAN_ROUTE):
    """Return Lean's checked reading data, or raise its diagnostic.

    Transport failure and a row that is malformed or not bound to the request are operational failures
    (`CheckerUnavailable`); a well-formed Lean error row rejects the document with Lean's text."""
    # One normalised input (`wire`: an explicit null is an absent field), as Lean reads it.
    environment, document = wire(environment), wire(document_wire(units, reading_sets))
    case = {"id": "readings-s1", "kind": "readings-validate", "environment": environment, "document": document}
    row = run_lean([case], executable=executable)[0]
    if row["status"] == "error":
        raise VEError(row["error"])
    _check(row, case)
    return row


# ---------------------------------------------------------------------------------------------------------------
# The report (6) and the English (2), from the checked answer

CHECKED_BY = {
    "lean": "readings@1 admission (4.1 to 4.4), every recorded separation (4.5) and the findings (4.6): "
            "ve_readings_route readings-validate",
    "python": "W2 structure of the reading sets, couplings and narrowings (S1 limitation, DRI ruling 3: "
              "Lean does not decode them)",
    "not_certified": "SeparatedByDecisionOnly: decision_only_sound is not proved (DRI ruling 2)"}


def _probe_form(entry):
    probe = entry["probe"]
    return "holds" if probe == "holds" else "outcome" if "outcome" in probe else "selects"


def report(doc):
    """Section 6 for the content-bearing sets of a loaded document, or None."""
    row = doc.get("readings_s1")
    if row is None or not row.get("content_bearing"):
        return None
    with _built():
        return _report(doc, row)


def _report(doc, row):
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
    return {"checked_by": CHECKED_BY, "sets": sets, "separations": separations, "findings": findings,
            "pending_candidates": pending,
            "couplings": len({item["axis"] for item in doc["meta"].get("couplings", [])}),
            "status": "UNKNOWN: superposition pending"}


class Wording:
    """The wordings of 2.3 for the pairs of a checked answer, filled from checked data only."""

    def __init__(self, doc):
        from .english import EnglishVocabulary
        self.doc = doc
        with _built():
            self.environment = doc["environment"].to_dict()
            self.document = document_wire(doc["units"], doc["meta"].get("reading_sets", []))
            self.admission = Decoded(self.environment, self.document)
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
        key = decode_key(key_json_value)
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
                if (strict, default) in _finding_pairs(entry, "SeparatedByDecisionOnly"):
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
        with _built():
            return self._set_lines(unit_id)

    def _set_lines(self, unit_id):
        from . import readings_english as E
        row = self.doc.get("readings_s1")
        lines = []
        for entry in row["sets"]:
            R = self.admission.doc.set_by_id(entry["set"])
            if R.unit != unit_id:
                continue
            for pair in self.unordered_pairs(entry):
                lines.append(self.pair(entry, pair)[1])
            for i, j in _finding_pairs(entry, "SeparatedByActOnly"):
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


def _finding_pairs(entry, code):
    """The candidate indices of each of Lean's findings with this code, in Lean's order (`parse_finding`, the
    reader `validate` checked them with)."""
    return [(i, j) for found, _, i, j in map(parse_finding, entry["findings"]) if found == code]


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


__all__ = ["CHECKED_BY", "ROW", "Wording", "document_wire", "parse_finding", "report", "run_lean", "validate"]
