"""Admission of content-bearing reading sets by the S1 Lean route, relayed (docs/LEAN-FIRST-PLAN.md rule 2).

`validate` sends the document to the Lean readings route (service mode `readings-route`, `readings-validate`,
docs/spec/composition-s1.md 8.4) and
returns Lean's row, or raises Lean's diagnostic with its text verbatim. Lean is the one owner of the answer: no
Python regeneration and no Rust replay is compared with it any more (lean-first batch 3). A route that cannot
answer, or answers a row that is not bound to the request (its shape, its sets, candidates, readings and
situations), is `CheckerUnavailable`, never a rejection and never an admission.

What Lean checks is the readings head of 4.1 on the decoded units and active sets. Couplings, narrowings and
W2's structural validation of the sets are not decoded by Lean (S1 limitation, DRI ruling 3): `ve/readings.py`
checks them in Python, and the report says so. The English of the report (`Wording`) is built from Lean's row
and Python's construction of the admitted document (`ve/readings_s1.py`).

`elaborate` (S2) runs after those checks and compares S2's decoded restrictions, choice search and generated slot
with Python's independent regeneration. Verdict search is still separate from this admission path.
"""
from __future__ import annotations

import re
from contextlib import contextmanager

from .ast import decimal_value
from .backends.relay import rows
from .errors import CheckerUnavailable, VEError
from .readings_s1 import KEY_FIELDS, KEY_OPTIONAL, Decoded, Document, content_bearing, decode_filled, decode_key, \
    wire
from .readings_s2_english import s1_gated as _s1_gated

# readings-defaults.md 1.1 (Lean's `routeOf` and `completionFinding`): under `norm-defaults@0` the norms chain takes the
# enumerated route with this cause; the soft and rights chains keep the abstention.
COMPLETION_CAUSE = "the unspecified completion"
NORM_DEFAULTS = "norm-defaults@0"

def document_wire(units, reading_sets, *, couplings=(), narrowings=()):
    """The document as the readings route reads it: every unit with its kind (1.2), content when it has one."""
    document = {"units": [{"id": unit["id"],
                           **({"kind": unit["kind"]} if unit.get("kind") is not None else {}),
                           **({"content": unit["content"]} if unit.get("content") is not None else {})}
                          for unit in units], "reading_sets": reading_sets}
    if couplings:
        document["couplings"] = list(couplings)
    if narrowings:
        document["narrowings"] = list(narrowings)
    return document


def elaborate(environment, units, reading_sets, *, couplings=(), narrowings=(), executable=None):
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
    case = {"id": "readings-s2", "kind": "readings-elaborate", "environment": environment, "document": document}
    [row] = run_lean([case], executable=executable)
    if NORM_DEFAULTS in environment.get("profiles", ()):
        return _completion_elaborate(row, case)
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


def _completion_elaborate(row, case):
    """`readings-elaborate` under `norm-defaults@0` (readings-defaults 1.1, 3; plan RD-2b), relayed: Lean's text
    verbatim, else its row bound to the request. Lean owns the route, the choices and their count; nothing of them is
    regenerated here. On the norms chain a content-bearing document takes the pending route when a candidate has no
    content, else the superposed one when Lean finds the filled document superposable (plan RD-6b) and the enumerated
    one with Lean's cause otherwise, and the row carries the filled document."""
    if row["status"] == "error":
        raise VEError(row["error"])
    try:
        from .backends.service_schema import Invalid, check_row
        check_row("readings-route", row, case, 0)
        _need(row["id"] == case["id"])
        sets = Document(None, case["document"]).sets
        bearing = any(content_bearing(R) for R in sets)
        pending = any(a.content is None for R in sets for a in R.candidates)
        if not bearing:
            _need(row["route"] == "w2" and not {"fill_premises", "filled"} & set(row))
        else:
            _need(row["route"] in (("pending",) if pending else ("enumerated", "superposed")))
            _bind_completion(row, case)
            if row["route"] == "superposed":
                _bind_completion_superposed(row, case, sets)
            elif not pending:
                _bind_completion_choices(row, sets)
    except (_Invalid, Invalid, VEError, TypeError, KeyError, ValueError, AttributeError, IndexError,
            RecursionError) as exc:
        raise CheckerUnavailable("the Lean readings route returned an invalid answer") from exc
    return {key: value for key, value in row.items() if key not in ("id", "status")}


def _bind_completion_choices(row, sets):
    """The enumerated row's finding and choices, bound to the request: every open set named in source order with
    Lean's cause (the completion's, or after RD-6b what keeps the filled document from superposing), each choice a
    reading with content of every open set, no choice twice, the count Lean's list's own."""
    finding = row["finding"]
    _need(type(finding) is dict and set(finding) == {"text", "cause"}
          and finding["text"] == "ReadingsNotSuperposable: " + ", ".join(R.id for R in sets)
          and _name(finding["cause"]))
    _need(_arr(_name)(row["narrowings_stale"]))
    if row["choices"] == "over":
        _need(row["choice_count"] == row["choices_checked"] == "over 64")
        return
    _need(row["choice_count"] == row["choices_checked"])
    _bind_choice_list(row["choices"], row["choice_count"], sets)


def _bind_choice_list(choices, count, sets):
    """A list of compatible choices bound to the request: each a reading with content of every open set in source
    order, none twice, `count` the list's own length."""
    _need(type(choices) is list and _nat(count) and count == len(choices) and count > 0)
    seen = set()
    for choice in choices:
        _need(type(choice) is list and all(type(e) is list and len(e) == 2 for e in choice)
              and [entry[0] for entry in choice] == [R.id for R in sets])
        for (_, index), R in zip(choice, sets):
            _need(_nat(index) and index < len(R.candidates) and R.candidates[index].content is not None)
        key = tuple(index for _, index in choice)
        _need(key not in seen)
        seen.add(key)


def _bind_completion_superposed(row, case, sets):
    """The superposed row under the completion (plan RD-6b; Lean's `elaborateFieldsND`), typed by the generated schema and
    bound to what the request fixes: the open sets in order with their versions and candidates, the unit ids, the
    restriction ids, the declared pairs a `Fill_T` label names, and the choices. What is left is Lean's alone: the
    formulas, the positions, the qualified names and the sizes."""
    from .environment import Environment
    from .readings_sup import FILL, slot_label
    _need(row["finding"] is None)
    document = Document(None, case["document"])
    by_id = {R.id: R for R in sets}
    raw = case["document"]
    narrowing_ids = [n["id"] for n in raw.get("narrowings", [])]
    coupling_ids = [k["id"] for k in raw.get("couplings", [])]
    stale = row["narrowings_stale"]
    _need(len(set(stale)) == len(stale) and set(stale) <= set(narrowing_ids))
    bits = [p["name"] for p in row["vocabulary"]["predicates"]]
    _need(len(set(bits)) == len(bits) and [g["name"] for g in row["generated_predicates"]] == bits)
    expected_units = [{k: value for k, value in unit.items() if k != "content"}
                      for unit in row["filled"]["units"]]
    positions = {(R.id, i): sum(len(previous.candidates) for previous in sets[:m]) + i + 1
                 for m, R in enumerate(sets) for i in range(len(R.candidates))}
    for unit in expected_units:
        if "set" in unit:
            unit["position"] = positions[(unit["set"], unit["index"])]
    _need([{k: value for k, value in unit.items() if k != "content"} for unit in row["units"]]
          == expected_units)
    readings = set()
    for unit in row["units"]:
        _typed_filled_content(unit["content"])
        if "set" not in unit:
            continue
        R = by_id.get(unit["set"])
        _need(R is not None and (unit["unit"], unit["version"]) == (R.unit, R.version)
              and unit["index"] < len(R.candidates) and R.candidates[unit["index"]].content is not None)
        key = (unit["set"], unit["index"])
        _need(key not in readings)
        readings.add(key)
    _need(readings == set(positions))
    request = Environment(case["environment"])
    pairs = {(name, decl.regulated.permission) for name, decl in request.predicates.items()
             if decl.regulated is not None and decl.regulated.role == "obligation"}
    labels = [entry["label"] for entry in row["slot"] + row["fill"]]
    _need(len(set(labels)) == len(labels))
    for entry in row["fill"]:
        decoded = slot_label(entry["label"])
        _need(decoded.kind == FILL and tuple(decoded.key.split(",")) in pairs)
    for entry in row["slot"]:
        decoded = slot_label(entry["label"])
        if decoded.kind in ("coupling", "narrowing"):
            _need(decoded.key in (coupling_ids if decoded.kind == "coupling" else narrowing_ids))
        elif decoded.kind in ("one", "own"):
            R = by_id.get(decoded.set)
            _need(R is not None and R.version == decoded.version
                  and (decoded.kind == "one" or decoded.index < len(R.candidates)))
        else:
            _need(False)
    _need([(e["set"], e["version"]) for e in row["names"]] == [(R.id, R.version) for R in sets])
    for entry, R in zip(row["names"], sets):
        _need([(c["index"], c["id"]) for c in entry["candidates"]] == [(i, a.id) for i, a in enumerate(R.candidates)])
        _need([c["position"] for c in entry["candidates"]] == [positions[(R.id, i)] for i in range(len(R.candidates))])
        for candidate, authored in zip(entry["candidates"], R.candidates):
            authored_names = {rule["name"] for rule in authored.content.rules()} if authored.content is not None else set()
            _need(all(pair[0] in authored_names for pair in candidate["names"]))
    if row["choices"] == "over":
        upper = 1
        for reading_set in sets:
            upper *= len(reading_set.candidates)
        _need(upper > 64 and row["choice_count"] == "over 64"
              and (row["choices_checked"] == "over 1024" and upper > 1024
                   or _nat(row["choices_checked"]) and 64 < row["choices_checked"] <= upper))
    else:
        _need(row["choice_count"] == row["choices_checked"])
        _bind_choice_list(row["choices"], row["choice_count"], sets)


def run_lean(cases, *, executable=None, timeout=None):
    """Lean's readings route rows for `cases`, in order, rejections included (service mode `readings-route`;
    `executable` names another service build, `timeout` replaces the mode's deadline)."""
    return rows("readings-route", wire(cases), timeout=timeout, executable=executable)


def _message(exc):
    return exc.message if hasattr(exc, "message") else str(exc)


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
# Under the unspecified completion (readings-defaults.md 3) Lean adds, per reading, its `Fill_T` and, once, the filled
# frame and units. Their shape is checked here and their binding to the request by `_bind_completion`; the search and
# the English read them (`readings_s1.Decoded`).
FILL_PREMISES = _arr(_obj({"set": _str, "index": _nat,
                           "premises": _arr(_obj({"label": _str, "ast": lambda v: v is not None}))}))
FILLED = _obj({"environment": lambda v: type(v) is dict,
               "units": _arr(_obj({"unit": _name, "content": lambda v: type(v) is dict},
                                  {"set": _str, "version": _nat, "index": _nat}))})
_COMPLETION = {"fill_premises": FILL_PREMISES, "filled": FILLED}
# A `Fill_T` premise's label (norm-defaults 2.4): `unsaid:pair:<obligation>,<permission>`.
FILL_LABEL = "unsaid:pair:"
ROW = _either(_obj({"id": _str, "status": _lit("ok"), "content_bearing": _lit(False)}, _COMPLETION),
              _obj({"id": _str, "status": _lit("ok"), "content_bearing": _lit(True),
                    "sets": _arr(_SET, nonempty=True)}, _COMPLETION))

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


def _bind_completion(row, case):
    """`fill_premises` and `filled` (readings-defaults 3), bound to the request: present exactly under
    `norm-defaults@0` beside a content-bearing set; one `Fill_T` per reading with content, in admission order, each
    label naming a declared obligation and its permission; the filled environment decodes, keeps the request's sorts,
    constants and predicates (each with its arguments) and adds only base predicates; the filled units are the
    request's fixed units, then its readings with content, in source order, each content of the author's kind, then
    Lean's generated units, each a rule on a regulated predicate of the request, named by its unit, whose guard reads
    one added table. What is left is Lean's alone: the filled contents and the formulas."""
    from .environment import Environment
    document = Document(None, case["document"])
    sets = document.sets
    completion = (NORM_DEFAULTS in case["environment"].get("profiles", ())
                  and any(content_bearing(R) for R in sets))
    _need(("fill_premises" in row) is completion and ("filled" in row) is completion)
    if not completion:
        return
    _need(FILL_PREMISES(row["fill_premises"]) and FILLED(row["filled"]))
    request = Environment(case["environment"])
    pairs = {(name, decl.regulated.permission) for name, decl in request.predicates.items()
             if decl.regulated is not None and decl.regulated.role == "obligation"}
    readings = [(R.id, i) for R in sets for i, a in enumerate(R.candidates) if a.content is not None]
    _need([(e["set"], e["index"]) for e in row["fill_premises"]] == readings)
    for e in row["fill_premises"]:
        for premise in e["premises"]:
            label = premise["label"]
            _need(label.startswith(FILL_LABEL) and tuple(label[len(FILL_LABEL):].split(",")) in pairs)
    filled = Environment(row["filled"]["environment"])
    _need(set(filled.sorts) == set(request.sorts) and set(filled.constants) == set(request.constants))
    # The profiles are the request's, in its order, without the completion's own (review B4 of rd-6b).
    profiles = row["filled"]["environment"]["profiles"]
    _need(NORM_DEFAULTS not in profiles and profiles == [p for p in case["environment"]["profiles"] if p in profiles])
    added = set(filled.predicates) - set(request.predicates)
    from .norm_defaults import unsaid_name
    expected_added = {unsaid_name(p) for p, decl in request.predicates.items()
                      if decl.regulated is not None and decl.regulated.default == "unspecified"}
    _need(added == expected_added)
    _need(all(filled.predicates[p].arguments == decl.arguments for p, decl in request.predicates.items())
          and all(filled.predicates[p].regulated is None for p in added))
    expected = []
    for item in document.items:
        if item[0] == "fixed":
            expected.append(({"unit": item[1]}, item[2].kind))
        elif item[0] == "set":
            R = item[2]
            expected += [({"unit": R.unit, "set": R.id, "version": R.version, "index": i}, a.content.kind)
                         for i, a in enumerate(R.candidates) if a.content is not None]
    units = row["filled"]["units"]
    _need(len(units) >= len(expected))
    for unit, (where, kind) in zip(units, expected):
        content = _typed_filled_content(unit["content"])
        _need({k: v for k, v in unit.items() if k != "content"} == where and getattr(content, "kind", None) == kind)
    generated = units[len(expected):]
    names = [unit["unit"] for unit in generated]
    _need(len(set(names)) == len(names) and not set(names) & set(document.unit_ids))
    for unit in generated:
        content = _typed_filled_content(unit["content"])
        _need(set(unit) == {"unit", "content"} and getattr(content, "kind", None) == "norm")
        rule = content.body
        guard = rule["guard"]
        _need(rule["name"] == unit["unit"] and request.predicates[rule["predicate"]].regulated is not None
              and guard[0] in ("unary", "binary") and guard[1] in added)


def _typed_filled_content(raw):
    """Decode the complete producer content before Python displays or uses it. The rule and formula grammars are
    the existing decoders; a malformed decoded value remains an unavailable answer, never a verdict."""
    from .readings_s1 import node_value
    from .ast import _Decoder
    _need(type(raw) is dict and len(raw) == 1)
    if "norm" in raw:
        norm = raw["norm"]
        _need(type(norm) is dict and set(norm) == {"name", "predicate", "sign", "mode", "guard", "unless",
                                                "over", "rank", "alterable", "exception", "hard"})
        _need(_name(norm["name"]) and _name(norm["predicate"]) and _bool(norm["sign"])
              and norm["mode"] in ("strict", "default") and (norm["rank"] is None or _name(norm["rank"]))
              and _arr(_name)(norm["over"]) and _arr(_name)(norm["alterable"]) and _bool(norm["hard"]))
        exception = norm["exception"]
        if exception is not None:
            _need(type(exception) is dict and set(exception) == {"decided_by", "sufficient", "necessary", "factors"}
                  and (exception["decided_by"] is None or _name(exception["decided_by"]))
                  and _arr(lambda v: type(v) is list)(exception["sufficient"])
                  and _arr(lambda v: type(v) is list)(exception["necessary"])
                  and _arr(_name)(exception["factors"]))
            for formula in exception["sufficient"] + exception["necessary"]:
                _Decoder().decode(formula)
        _Decoder().decode(norm["guard"])
        _need(_arr(lambda v: type(v) is list)(norm["unless"]))
        for formula in norm["unless"]:
            _Decoder().decode(formula)
        node_value(norm)
    elif "assertion" in raw:
        _Decoder().decode(raw["assertion"])
    else:
        _need(False)
    content = decode_filled(wire(raw))
    _need(content is not None)
    return content


def _check(row, case):
    """Raise `CheckerUnavailable` unless `row` is a well-formed `ok` answer bound to the request. Every failure of
    the check itself (a type the schema missed, a missing request field) is contained here: the answer is then
    not shown to be Lean's, which is operational, never a rejection."""
    try:
        _need(ROW(row) and row["id"] == case["id"])
        _bind(row, case["document"])
        _bind_completion(row, case)
    except (_Invalid, TypeError, KeyError, ValueError, AttributeError, IndexError, RecursionError) as exc:
        raise CheckerUnavailable("the Lean readings route returned an invalid answer") from exc


def validate(environment, units, reading_sets, *, executable=None):
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
            "ve_readings_route readings-validate; S2 route and restrictions: readings-elaborate",
    "python": "W2 structure of the reading sets, couplings and narrowings (S1 limitation, DRI ruling 3: "
              "Lean does not decode them); S2 choices, units, names, slot and sizes compared with Lean",
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
                      reading_premises=[entry["label"] for entry in s2.get("slot", []) + s2.get("fill", [])],
                      not_superposable=s2["finding"])
        if "sizes" in s2:
            result["sizes"] = s2["sizes"]
    if route is not None:
        # `status`, `conflict` and `dead_readings` (6): each from checked evidence; `dead_readings` is null when
        # the compatible choices were too many to enumerate, never an unchecked empty list.
        result.update(route.report_fields())
        from .readings_s2_wording import report_english
        result["english"] = report_english(doc, route)
    return result


class Wording:
    """The wordings of 2.3 for the pairs of a checked answer, filled from checked data only."""

    def __init__(self, doc):
        from .english import EnglishVocabulary
        self.doc = doc
        with _built():
            self.environment = doc["environment"].to_dict()
            self.document = document_wire(doc["units"], doc["meta"].get("reading_sets", []))
            # Under the completion the documents are Lean's filled ones (readings-defaults 3, `validate`'s row).
            row = doc.get("readings_s1") or {}
            self.admission = Decoded(self.environment, self.document, row.get("filled"), row.get("fill_premises"))
            self.words = EnglishVocabulary(self.admission.senv.frame)
            self.numbers = {unit["id"]: n for n, unit in enumerate(doc["units"], 1)}
        self._names = {}

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
        """`<reading>` (2.1, as readings-defaults 2.3 amends it, review A4): the deontic verb in italics when the
        candidates are rules whose full sentences, notes included, differ only in it; otherwise each candidate's
        own rendered sentence, in italics, without its final period (`sentence_slots`, the one rule for both).
        "reading <i>" is never shown. A candidate the slot cannot show (no content, a sentence that does not read
        back, or one sentence for two different contents) is `Unnamed`: only an answer that names it is refused.
        Computed once per set."""
        if set_id not in self._names:
            from .readings_s2_english import sentence_slots
            from .wire import canonical_json
            R = self.admission.doc.set_by_id(set_id)
            # All candidates share the lower soft frame. Check their quoted rules in one Lean
            # request, then use the checked containers for both the sentence and its identity.
            rules = None
            if R.candidates and all(a.authored is not None and a.authored.kind == "norm"
                                    for a in R.candidates):
                from .softnorms import batch_rule, check_rule_batch
                env = self.admission.side(set_id, 0).soft.env
                contents = [{"norm": a.authored.body} for a in R.candidates]
                outcomes = check_rule_batch(env, contents)
                rules = [batch_rule(env, content, outcome)
                         for content, outcome in zip(contents, outcomes, strict=True)]
            self._batched_rules = rules
            try:
                shown = [self.candidate_sentence(set_id, i) for i in range(len(R.candidates))]
            finally:
                del self._batched_rules
            keys = [i if a.authored is None else
                    rule_key(self.admission.side(set_id, i).soft.env, a.authored.body,
                             rule=None if rules is None else rules[i]) if a.authored.kind == "norm" else
                    canonical_json(a.authored.raw) for i, a in enumerate(R.candidates)]
            self._names[set_id] = sentence_slots(set_id, [text for text, _ in shown], [verb for _, verb in shown],
                                                 keys)
        return self._names[set_id]

    def candidate_sentence(self, set_id, i):
        """(sentence, verb): the candidate's own sentence, rendered as the document's renderer shows that kind of
        content, and a rule's deontic verb (else None). A rule by its canonical rule sentence followed by the
        notes for the fields that sentence leaves out (precedence, switches, rank, exception conditions;
        `rule_notes`, under which two rules differing in any field render differently), an assertion by its
        canonical VE English sentence, read back to the same formula, and a right, its incident lines or a
        limitation by the rights renderer. A candidate that cannot be shown gets an `Unnamed` with the reason."""
        from .readings_s2_english import Unnamed
        # The reading as the author wrote it: under the completion its document is Lean's filled one.
        content = self.admission.doc.set_by_id(set_id).candidates[i].authored
        if content is None:
            return Unnamed(f"an answer names a reading of {set_id} without content"), None
        side = self.admission.side(set_id, i)
        if content.kind == "norm":
            rules = getattr(self, "_batched_rules", None)
            rule = None if rules is None else rules[i]
            return rule_sentence(side.soft.env, content.body, rule=rule)
        if content.kind == "assertion":
            from .ast import formula_from_data
            from .readings_s2_english import canonical_sentence
            frame = self.admission.senv.frame
            failure = f"a reading of {set_id} does not read back to its content"
            try:
                return canonical_sentence(frame, formula_from_data(frame, content.body), failure), None
            except VEError as error:
                if error.message != f"InvalidInput: {failure}":
                    raise
                return Unnamed(failure), None
        from .surface.rights import render_unit
        return render_unit(side.rights, content.raw), None

    def decider(self, value):
        who = value or "unstated"
        return "the decider" if who == "unstated" else who

    def subject(self, row):
        from .readings_english import subject
        return subject(row)

    def situation_text(self, set_id, witness, entry):
        """`<situation>`: elements by sort then name, true base tuples, then each decision supposed. Under the
        completion a filled table is no fact of the situation: it is shown by `gap_text`."""
        from .ast import formula_from_data  # noqa: F401  (vocabulary is the frame's)
        base = entry["base"]
        facts = []
        for sort in sorted(base["domains"]):
            noun = self.words.sorts[sort]
            for name in sorted(base["domains"][sort]):
                facts.append(f"{name} is {_article(noun)} {noun}")
        for predicate in sorted(base["relations"]):
            if predicate in self.admission.doc.filled_tables:
                continue
            for row in sorted(base["relations"][predicate]):
                facts.append(self.words.predicates[predicate].format(*row))
        for table, own in [(t, False) for t in entry["fixed"]] + [(t, True) for t in entry["decisions"]]:
            for row in table["tuples"]:
                facts.append("suppose " + self.decision(set_id, witness, table["key"], row, own))
        return "; ".join(facts) if facts else "nothing exists"

    def gap_text(self, base):
        """norm-defaults 3.2's filled-gap sentences after a shown situation (readings-defaults 2.2), each led by a
        space: under the completion, every point of every filled table over the situation's elements, with the
        situation's answer (Lean's plan selects the ones a result depends on from RD-3 on)."""
        from .readings_s2_english import gap_sentences
        from .readings_s2_wording import filled_gaps
        return gap_sentences(filled_gaps(self.admission.senv.frame, self.admission.doc.filled_tables, base))

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
        from .readings_s2_english import named_pair
        names = named_pair(set_id, self.reading_names(set_id), i, j)
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
                return "E14", _s1_gated("E14", " ".join(lines))
            text = E.outcome_pair_sentence(self.situation_text(set_id, i, situation), names[i], names[j], role,
                                           row[0], value, other_admissible=facts["other_admissible"],
                                           other_value=facts.get("other_value"),
                                           gaps=self.gap_text(situation["base"]))
            return "E19", _s1_gated("E19", text)
        if probe == "holds" and all(R.candidates[k].content.kind == "assertion" for k in (i, j)):
            true, false = (names[i], names[j]) if value else (names[j], names[i])
            return "E21", _s1_gated("E19", E.assertion_pair_sentence(self.situation_text(set_id, i, situation),
                                                                     true, false,
                                                                     gaps=self.gap_text(situation["base"])))
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
        content = self.admission.doc.set_by_id(set_id).candidates[k].authored
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
        def incompatible(rule):
            return frozenset((rule.core.name, twin_name)) in sd.incompatible_pairs
        out = []
        if any(r.mode == "strict" and r.core.name != twin_name and _act(sd, r) == act
               and incompatible(r) and r.core.name not in related for r in rules):
            out.append(E.E22)
        if sd.env.soft["outranking"]["mode"] == "strict" and any(
                r.mode == "default" and r.core.name != twin_name and _act(sd, r) == act
                and (r.core.predicate == twin.core.predicate or incompatible(r))
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
                lines.append(_s1_gated("E16", E.act_only_sentence(*acts)))
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


def rule_sentence(env, body, *, rule=None):
    """(sentence, verb) of a rule candidate's `norm` object (the `<reading>` slot, 2.3): its canonical rule sentence,
    then `rule_notes` (precedence, switches, rank, exception conditions and factors), then, for a default rule
    whose exception is decided by someone other than the document's default decider, who decides it; and its
    deontic verb. Two rules that differ in what `rule_key` keeps render differently."""
    from .norm_english import render_rule_sentence
    from .softnorms import decode_rule
    from .surface.rights import rule_notes
    rule = decode_rule(env, {"norm": body}) if rule is None else rule
    notes = list(rule_notes(rule, env))
    decider, usual = _deciders(env, rule)
    if decider != usual:
        notes.append(f"Its exception is decided by {decider}." if decider != "unstated" else
                     "The source names no decider for its exception.")
    return " ".join((render_rule_sentence(rule, env), *notes)), _modal(env, rule)


def rule_key(env, body, *, rule=None):
    """What a rule candidate means to a reader, the `<reading>` slot's identity of it: the decoded rule without its
    own name (other units refer to it by name, so two readings of one set that differ in it alone mean the same)
    and without `hard` (a declaration check: strict and unswitchable, which the rule states anyway), with the
    decider that decides its exception."""
    from .softnorms import decode_rule
    from .wire import canonical_json
    rule = decode_rule(env, {"norm": body}) if rule is None else rule
    raw = rule.to_dict()["norm"]
    raw.pop("name"), raw.pop("hard", None)
    if "exception" in raw:
        raw["exception"]["decided_by"] = _deciders(env, rule)[0]
    return canonical_json(raw)


def _deciders(env, rule):
    """(who decides the rule's exception, who decides an exception the rule names no decider for); both "unstated"
    for a strict rule."""
    if rule.mode != "default":
        return "unstated", "unstated"
    usual = env.soft.get("exception_decider") or "unstated"
    return (rule.exception or {}).get("decided_by") or usual, usual


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


__all__ = ["CHECKED_BY", "ROW", "Wording", "document_wire", "elaborate", "parse_finding", "report", "run_lean",
           "validate"]
