"""`english.statement`'s relay binding (docs/spec/en-e3-norm.md 2.4, Relay and Fuzz tests; section 8's P2 and P3).

Genuine answers of the built `ve_service` to the W1 path's requests (`statement_request`) are mutated one and two
faults at a time: every member dropped, emptied, retyped or duplicated, rows reordered, a number pushed out of range,
a name changed, and each rule row's `span` rebound by each condition of the span binding. Every mutant is
`CheckerUnavailable` at `statement_answer`, or changes nothing the relay shows (the shadow record), or is a value
Lean chooses (`LEAN`, each with the reason).
"""
from __future__ import annotations

import copy
import hashlib
import json

import pytest

from tests.test_norms import environment, permission
from ve.errors import CheckerUnavailable
from ve.norm_english import STATEMENT_MODE, parse_english, statement_answer, statement_record, statement_request

ENV = environment({"permitted": permission()})
NBSP = " "
TEXTS = {
    "two": "Rule 1. Every act may be done.\nRule 2 (exception to rule 1). Every act must not be done.\n"
           "Rule 2 takes precedence over rule 1.",
    "nbsp": f"Rule 1. Every act must not be done.{NBSP}\nRule 2 (exception to rule 1). Every act may be done.",
    "lines": "Rule 1.\nEvery act may be done.",
    "none": "Rule 1. X.",
    "expected": "Rule 2. Every act may be done.",
    "unknown": "Rule 1. Every act may be done.\nRule 2 takes precedence over rule 3.",
    "empty": "",
}
DEEP: list = []
for _ in range(10_000):
    DEEP = [DEEP]
RETYPES = (7, True, None, [], {}, 1.5, "\ud800", DEEP)
# Values Lean chooses, which an answer of the same shape may change (their encoder theorem covers them): which
# rule rows a text has (its last rule row dropped), a rule's sign, guard and carve-outs, and a refusal's text.
LEAN = {"result.statements[]": "how many statements the text has is Lean's reading (`oneSpans`); a last rule row no "
                               "precedence row names can go without a trace in the answer (EN-3's manifest binds the "
                               "block count)",
        "result.statements[].node.norm.sign": "the rule's force", "result.statements[].node.norm.guard": "a formula",
        "result.statements[].node.norm.unless": "the carve-outs", "result.text": "Lean's wording of the refusal"}


def sources() -> dict:
    """The fixtures' environments and texts, and the pinned rsp block with a guard (`rows-cond`)."""
    from tests.test_english_statement_blocks import blocks, use_case
    from ve.environment import Environment
    out = {name: (ENV, text) for name, text in TEXTS.items()}
    [row] = [r for r in blocks("rsp") if r["id"] == "rows-cond"]
    return {**out, "guarded": (Environment(use_case("rsp")["environment"]), row["text"])}


@pytest.fixture(scope="module")
def answers() -> dict:
    """Each source's request, environment and genuine row, from the built service."""
    from tests.test_soft_norms_lean import SERVICE
    from ve.backends import relay
    if not SERVICE.exists():
        pytest.skip("the Lean service has not been built")
    out = {}
    for name, (env, text) in sources().items():
        case = statement_request(env, text)
        out[name] = (env, case, relay.decide(STATEMENT_MODE, [case])[0])
    return out


def shown(env, case, row) -> dict:
    """What the relay shows of `row`: the shadow record beside Python's own outcome."""
    try:
        python = [rule.to_dict()["norm"] for rule in parse_english(env, case["source"]).rules]
    except Exception as exc:  # noqa: BLE001 - Python's refusal is its outcome
        python = exc
    return statement_record(case["source"], python, statement_answer(row, case, env))


def unavailable(env, case, row) -> bool:
    try:
        statement_answer(row, case, env)
    except CheckerUnavailable:
        return True
    return False


def _walk(value, path=(), name=""):
    """Every position of `value`: its path of keys and indices, and its schema-like name (`a[].b`)."""
    yield path, name
    if type(value) is dict:
        for key, item in value.items():
            yield from _walk(item, (*path, key), f"{name}.{key}" if name else key)
    elif type(value) is list:
        for index, item in enumerate(value):
            yield from _walk(item, (*path, index), f"{name}[]")


def _at(row, path):
    for key in path:
        row = row[key]
    return row


def generic(row):
    """One-fault mutants at every position: dropped, emptied, retyped to each JSON type, duplicated, reordered."""
    for path, name in _walk(row):
        if not path:
            continue
        parent, key, value = _at(row, path[:-1]), path[-1], _at(row, path)
        edits = [("retyped", r) for r in RETYPES]
        if type(value) in (list, dict, str) and value:
            edits.append(("emptied", type(value)()))
        if type(value) is list and value:
            edits += [("duplicated", [value[0], *value]), ("reordered", value[::-1])]
        for edit, replacement in [("dropped", None), *edits]:
            mutant = copy.deepcopy(row)
            target = _at(mutant, path[:-1])
            if edit == "dropped":
                del target[key]
            else:
                target[key] = replacement
            if json.dumps(mutant, sort_keys=True) != json.dumps(row, sort_keys=True):
                yield name, edit, mutant


def _rules(row) -> list[dict]:
    return [r for r in row["result"]["statements"] if r["kind"] == "rule"]


def named(row, source: str):
    """The spec's named faults of a `one` row, as changes of (rule rows, all rows): numbers, names and rows out of
    the request, and each condition of the span binding (dropped or doubled, start = stop, an end past the source
    or off a UTF-8 boundary, two spans overlapping or out of order)."""
    rules, raw = _rules(row), source.encode()
    k, first, last = len(rules), rules[0]["span"], rules[-1]["span"]
    yield "number past k", lambda r, s: r[-1].update(number=k + 1)
    yield "number 0", lambda r, s: r[0].update(number=0)
    yield "name changed", lambda r, s: r[0]["node"]["norm"].update(name="rule-9")
    yield "over names a rule past k", lambda r, s: r[-1]["node"]["norm"]["over"].append(f"rule-{k + 1}")
    yield "exception_to past k", lambda r, s: r[-1]["exception_to"].append(k + 1)
    yield "predicate undeclared", lambda r, s: r[0]["node"]["norm"].update(predicate="absent")
    yield "extra precedence row", lambda r, s: s.append({"kind": "precedence", "rule": k, "over": 1})
    yield "precedence row past k", lambda r, s: s.append({"kind": "precedence", "rule": k + 1, "over": 1})
    yield "span dropped", lambda r, s: r[0].pop("span")
    yield "span doubled", lambda r, s: r[0].update(span=first * 2)
    yield "start = stop", lambda r, s: r[0].update(span=[first[0], first[0]])
    yield "end past the source", lambda r, s: r[-1].update(span=[last[0], len(raw) + 1])
    yield "start past the header", lambda r, s: r[0].update(span=[first[0] + 1, first[1]])
    yield "the row duplicated", lambda r, s: s.insert(1, copy.deepcopy(r[0]))
    if k > 1:
        yield "rows reordered", lambda r, s: s.reverse()
        yield "spans out of order", lambda r, s: (r[0].update(span=r[1]["span"]), r[1].update(span=first))
        yield "spans overlap", lambda r, s: r[0].update(span=[first[0], r[1]["span"][0] + 1])
    off = [e for e in range(first[1] + 1, len(raw)) if raw[e] & 0xC0 == 0x80]  # inside a multi-byte character
    if off:
        yield "end off a UTF-8 boundary", lambda r, s: r[0].update(span=[first[0], off[0]])


def applied(row, *changes):
    mutant = copy.deepcopy(row)
    for change in changes:
        change(_rules(mutant), mutant["result"]["statements"])
    return mutant


def test_every_genuine_answer_is_accepted(answers):
    """The binding's other direction: each genuine answer is bound (one, none, and rejections with and without
    a sentence), and a `one` row's rule numbers and spans are as the text has them (P3: a block over two lines)."""
    results = {name: statement_answer(row, case, env) for name, (env, case, row) in answers.items()}
    assert {name: r["status"] for name, r in results.items()} == {
        "two": "one", "nbsp": "one", "lines": "one", "none": "none", "expected": "rejected", "unknown": "rejected",
        "empty": "rejected", "guarded": "one"}
    assert [r["span"] for r in _rules({"result": results["lines"]})] == [[0, len(TEXTS["lines"])]]
    assert [r["span"] for r in _rules({"result": results["nbsp"]})] == [[0, 35], [38, len(TEXTS["nbsp"].encode())]]


def test_every_retyped_dropped_or_duplicated_member_is_unavailable(answers):
    survivors = []
    for name, (env, case, row) in answers.items():
        genuine = shown(env, case, row)
        for path, edit, mutant in generic(row):
            if not unavailable(env, case, mutant) and path not in LEAN and shown(env, case, mutant) != genuine:
                survivors.append(f"{name} {path}: {edit}")
    assert survivors == []


def test_every_named_mutant_is_unavailable(answers):
    """Each condition of the binding, one fault at a time on every `one` answer, then every two of them at once."""
    survivors, count = [], 0
    for name, (env, case, row) in answers.items():
        if row["result"]["status"] != "one":
            continue
        faults = list(named(row, case["source"]))
        pairs = [((a, b), (f, g)) for i, (a, f) in enumerate(faults) for b, g in faults[i + 1:]]
        for edits, changes in [((a,), (f,)) for a, f in faults] + pairs:
            count += 1
            if not unavailable(env, case, applied(row, *changes)):
                survivors.append(f"{name}: {' + '.join(edits)}")
    assert survivors == [] and count > 400


def test_an_extra_rule_row_over_a_precedence_line_is_unavailable(answers):
    """The rule numbers are the request's: a row k + 1, its node and `over` consistent and its span the trailing
    precedence line's bytes, is refused because the source there holds no header of rule k + 1."""
    env, case, row = answers["two"]
    mutant = copy.deepcopy(row)
    statements, source = mutant["result"]["statements"], case["source"]
    extra = copy.deepcopy(_rules(mutant)[0])
    start = source.encode().rindex(b"Rule 2 takes")
    extra.update(number=3, span=[start, len(source.encode())])
    extra["node"]["norm"].update(name="rule-3")
    statements.append(extra)
    assert unavailable(env, case, mutant)


@pytest.mark.parametrize("change", ["off a UTF-8 boundary", "overlap", "past the source"])
def test_p2_a_rule_span_out_of_the_source_is_unavailable(answers, change):
    """P2: a `one` answer whose rule span ends off a UTF-8 character boundary of the source (inside the
    no-break space after rule 1's period), overlaps the next, or ends past the source."""
    env, case, row = answers["nbsp"]
    mutant = copy.deepcopy(row)
    first, second = _rules(mutant)
    raw = case["source"].encode()
    assert raw[35:37] == NBSP.encode()
    first["span"] = {"off a UTF-8 boundary": [0, 36], "overlap": [0, 39], "past the source": first["span"]}[change]
    if change == "past the source":
        second["span"] = [second["span"][0], len(raw) + 1]
    assert unavailable(env, case, mutant)
    first["span"], second["span"] = [0, 37], [38, len(raw)]  # the other direction: on boundaries, apart
    assert not unavailable(env, case, mutant)


def test_p3_a_block_over_two_lines_is_bound(answers):
    """P3: E13's text "Rule 1.\\nX.", answered `one` with the span [0, 10] from header to period across the line
    break, is bound (the relay has no layout check); its genuine counterpart through the mode is `lines`."""
    env, case, row = answers["lines"]
    source = "Rule 1.\nX."
    e13 = {**case, "source": source}
    mutant = copy.deepcopy(row)
    mutant["result"]["identities"]["source_sha256"] = hashlib.sha256(source.encode()).hexdigest()
    _rules(mutant)[0]["span"] = [0, 10]
    assert statement_answer(mutant, e13, env)["statements"][0]["span"] == [0, 10]
    assert unavailable(env, case, mutant)  # the same answer is not the answer to another source


def test_an_overlay_digest_the_request_did_not_send_is_unavailable(answers):
    """The W1 path sends no overlay, so an answer naming an overlay digest is not this request's."""
    env, case, row = answers["two"]
    mutant = copy.deepcopy(row)
    mutant["result"]["identities"]["overlay_digest"] = "0" * 64
    assert unavailable(env, case, mutant)


def test_a_refusal_names_a_sentence_exactly_when_its_code_does(answers):
    env, case, row = answers["expected"]
    named_sentence = copy.deepcopy(row)
    named_sentence["result"].pop("sentence")
    past = copy.deepcopy(row)
    past["result"]["sentence"] = case["source"].count(".")
    env, unknown_case, unknown = answers["unknown"]
    unsentenced = copy.deepcopy(unknown)
    unsentenced["result"]["sentence"] = 0
    assert unavailable(env, case, named_sentence) and unavailable(env, case, past)
    assert unavailable(env, unknown_case, unsentenced)
    assert not unavailable(env, case, row) and not unavailable(env, unknown_case, unknown)


def test_a_refusal_code_and_class_are_lean_s_table(answers):
    env, case, row = answers["expected"]
    for change in ({"code": "NoDerivation"}, {"class": "VEError"}, {"code": "RenderMismatch", "class": "VEError"}):
        mutant = copy.deepcopy(row)
        mutant["result"].update(change)
        assert unavailable(env, case, mutant), change
