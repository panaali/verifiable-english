"""The English reader of S2.4 end to end (docs/spec/english-lean-s2.md 2.10, 2.11, 4.3, 4.4, 8; base 2.12, 8.8).

`ve_english_route` is the real Lean executable here, reached through the adapter `ve/backends/english_lean.py`.
The spec fixtures of section 8 (every literal sentence of `lean/VE/EnglishGrammar/ReadExamples.lean`, under the
environments section 8 names) are read three ways: by Python's dispatched unit (hand parser, Lark audit,
`check_document`), by `english.read`, and, where the text is in its core skeleton, by the W7 reader
(`lean/VE/English/Run.lean`, `conformance/english_lean.py`). Python and `english.read` must agree under the
comparison of 2.11 (the adapter's shadow record has no difference class); the W7 reader, where it reads a
text, must give Python's formulas. Admission runs end to end under the shadow and Lean overrides; the
identities of base 8.8 are checked on the real answers; malformed requests are error rows only.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import warnings

import pytest

from ve import Environment
from ve import english as EN
from ve import english_grammar as EG
from ve.backends import english_lean as L
from ve.backends import lean as lean_backend
from ve.english import UnreviewedVocabularyWarning
from ve.errors import CheckerUnavailable, ResourceLimit, VEError

from conformance import english_lean as W7
from subprocesses import HANG_TIMEOUT

ROOT = Path(__file__).resolve().parents[1]
ROUTE = ROOT / "lean/.lake/build/bin/ve_english_route"
EXAMPLES = ROOT / "lean/VE/EnglishGrammar/ReadExamples.lean"

pytestmark = pytest.mark.filterwarnings("ignore::ve.english.UnreviewedVocabularyWarning")


@pytest.fixture(autouse=True)
def built(monkeypatch):
    assert ROUTE.is_file(), "lake build ve_english_route before the English route tests"
    monkeypatch.setattr(L, "TRANSPORT", None)
    monkeypatch.delenv("VE_ENGLISH_ROUTE", raising=False)


# ------------------------------------------------------------------ the environments of section 8

SORTS_F = [("person", None), ("service", None)]
PREDS_F = [("deployed", ["service"], "{0} is deployed", None),
           ("reviewed", ["service"], "{0} is reviewed", "{0} is not reviewed"),
           ("owns", ["person", "service"], "{0} owns {1}", "{0} does not own {1}")]
CONSTS_F = [("alice", "person"), ("legacy", "service")]


def env_json(closure, sorts, preds, consts) -> dict:
    """`envJson` of ReadExamples.lean."""
    vocabulary = {
        "sorts": {s: {"description": "A sort.",
                      **({"verbalisation": {"singular": n, "plural": n + "s"}} if n else {})} for s, n in sorts},
        "predicates": {p: {"arguments": args, "description": "A predicate.", "verbalisation": w,
                           **({"negative_verbalisation": neg} if neg else {})} for p, args, w, neg in preds},
        "constants": {c: {"sort": s, "description": "A constant."} for c, s in consts}}
    if closure:
        return {"language": "ve.core@0.1", "profiles": ["closure@0", "relational-fol@0"],
                "spec_revision": "ve-v0.1-closure-2026-09-21", "vocabulary": vocabulary}
    return {"language": "ve.core@0", "profile": "relational-fol@0", "spec_revision": "ve-v0-draft-2026-09-20",
            "vocabulary": vocabulary}


def case(data: dict, displays=()) -> tuple[Environment, dict]:
    """The environment and its `parse_english` options: an overlay of constant displays, as `env` builds it."""
    env = Environment(data)
    if not displays:
        return env, {}
    overlay = {"format": "ve.english-vocabulary@1", "environment_id": env.environment_id, "sorts": {},
               "predicates": {}, "constants": {c: {"verbalisation": d} for c, d in displays}}
    return env, {"vocabulary": overlay}


def with_pred(pred, consts=()):
    return env_json(False, SORTS_F, PREDS_F + [pred], CONSTS_F + list(consts))


ENVIRONMENTS = {
    "F": lambda: case(env_json(False, SORTS_F, PREDS_F, CONSTS_F)),
    "FC": lambda: case(env_json(True, SORTS_F, PREDS_F, CONSTS_F)),
    "F3": lambda: case(env_json(False, SORTS_F, PREDS_F, CONSTS_F + [("beta", "service"), ("gamma", "service")])),
    "FD": lambda: case(env_json(False, SORTS_F + [("dservice", "deployed service")], PREDS_F, CONSTS_F)),
    "F51": lambda: case(with_pred(("owner_of", ["service", "person"], "the owner of {0} is {1}", None))),
    "F52": lambda: case(with_pred(("follows", ["person", "person"], "{1} follows {0}", None))),
    "F53": lambda: case(with_pred(("related", ["person", "person"], "{1} {0} are related", None),
                                  [("bob", "person"), ("alicebob", "person")]), [("alicebob", "alice bob")]),
    "Fapi": lambda: case(env_json(False, SORTS_F, PREDS_F, CONSTS_F + [("api", "service")])),
}
ENVIRONMENTS["Fapi"] = lambda: case(env_json(False, SORTS_F, PREDS_F, CONSTS_F + [("api", "service")]),
                                    [("api", "the api")])
# The lexicon each environment's fixtures are stated under, in ReadExamples.lean.
LEXICON = {"F": "LF", "FC": "LF", "F3": "LF3", "FD": "LFD", "F51": "L51", "F52": "L52", "F53": "L53",
           "Fapi": "Lapi"}
# The fixture lexicons Python's producer selects as written (the others are V3/TEMPLATE_SHAPE corners).
LF = {"nouns": [["person", "person"], ["service", "service"]], "letters": [["person", "P"], ["service", "S"]],
      "wordings": [["deployed", "{0} is deployed"], ["owns", "{0} owns {1}"], ["reviewed", "{0} is reviewed"]],
      "negatives": [["owns", "{0} does not own {1}"], ["reviewed", "{0} is not reviewed"]], "aliases": [],
      "spellings": [["alice", "alice"], ["legacy", "legacy"]]}
SELECTED = {
    "F": LF, "FC": LF,
    "F3": {**LF, "spellings": [["alice", "alice"], ["beta", "beta"], ["gamma", "gamma"], ["legacy", "legacy"]]},
    "FD": {**LF, "nouns": [["dservice", "deployed service"], *LF["nouns"]],
           "letters": [["dservice", "D"], *LF["letters"]]},
    "Fapi": {**LF, "spellings": [["alice", "alice"], ["api", "the api"], ["legacy", "legacy"]]},
}


def _unescape(literal: str) -> str:
    return re.sub(r'\\(.)', lambda m: {"n": "\n", "t": "\t"}.get(m[1], m[1]), literal)


def fixture_texts() -> list[tuple[str, str]]:
    """(environment, text) of every `#guard verdicts`/`#guard rd` of ReadExamples.lean under the environment's
    own lexicon, in order, without repeats; the two built texts (`negations`) are spelled here."""
    out: list[tuple[str, str]] = []
    for line in EXAMPLES.read_text().splitlines():
        found = re.match(r'#guard (?:verdicts|rd) (\w+) (\w+) (.*)$', line)
        if not found:
            continue
        env, lexicon, rest = found.groups()
        literal = re.match(r'"((?:[^"\\]|\\.)*)"', rest)
        if literal:
            text = _unescape(literal[1])
        else:
            built = re.match(r'\(negations (\d+)\)', rest)
            assert built, f"an unrecognised fixture form: {line}"
            k = int(built[1])
            text = "It is not the case that " + "it is not the case that " * (k - 1) + "legacy is deployed."
        if LEXICON.get(env) == lexicon and (env, text) not in out:
            out.append((env, text))
    return out


FIXTURES = fixture_texts()


def test_the_fixtures_are_read_from_the_lean_examples():
    assert len(FIXTURES) > 80
    assert {env for env, _ in FIXTURES} == set(ENVIRONMENTS)
    assert ("F", 'Starting from legacy, legacy is reachable by one or more "owns" steps.') in FIXTURES


@pytest.mark.parametrize("name", sorted(SELECTED))
def test_python_selects_the_fixture_lexicon(name):
    """Where Python's producer selects the fixture's wordings, the route reads the lexicon the Lean `#guard`s
    state their outcomes under, so agreement with Python carries over to the spec's expected outcomes."""
    env, options = ENVIRONMENTS[name]()
    exported = EG.export(EN.EnglishVocabulary(env, **options))
    assert {k: v for k, v in exported.items() if k not in ("format", "environment_id")} == SELECTED[name]


# ------------------------------------------------------------------ three-way conformance on the fixtures

def python_reading(env, text, words, options):
    try:
        return EN._python_reading(env, text, words, options)
    except Exception as exc:  # the comparison classifies every outcome, internal errors included
        return exc


def lean_reading(env, text, words, options):
    try:
        return EN._lean_reading(env, text, words, options)
    except CheckerUnavailable:
        raise
    except VEError as exc:
        return exc


def formulas(reading) -> list | None:
    return None if isinstance(reading, BaseException) else [EN.ast._to_data(f) for f in reading.document.formulas]


def w7_readings(env, words, texts) -> list | None:
    """The W7 reader's formulas per text (None where it reads none or where its tokens do not spell the text:
    the harness splits at whitespace, so spacing is not its to judge), or None when the vocabulary is outside
    its core lexicon."""
    try:
        lex = W7.lexicon(env, words)
    except W7.Untokenizable:
        return None
    letters = tuple(words.letters.values())
    cases = [{"tokens": W7.tokenize(W7.lower_sentence_starts(t), letters), "formulas": [["top"]]} for t in texts]
    _, _, results = W7.run_lean({"environment": W7.environment(env), "lexicon": lex, "cases": cases})
    assert len(results) == len(texts)
    return [result["parsed"] if W7.detokenize(c["tokens"]) == t else None
            for t, c, result in zip(texts, cases, results)]


def test_three_way_conformance_on_the_spec_fixtures():
    """Python's dispatched unit and `english.read` agree on every fixture (2.11: verdict, formulas, canonical
    text, marks, witness count, or mapped classes); the W7 reader, on every fixture it reads, gives Python's
    formulas. The comparison would fail on a constant answer: both outcomes occur, and each leg is used."""
    seen = {"agree": 0, "accepted": 0, "rejected": 0, "w7 read": 0}
    differences = []
    by_env: dict[str, list[str]] = {}
    for name, text in FIXTURES:
        by_env.setdefault(name, []).append(text)
    for name, texts in by_env.items():
        env, options = ENVIRONMENTS[name]()
        words = EN.EnglishVocabulary(env, **options)
        w7 = w7_readings(env, words, texts)
        for k, text in enumerate(texts):
            python = python_reading(env, text, words, options)
            lean = lean_reading(env, text, words, options)
            record = L.shadow_record(env, text, words, python, lean)
            if record["classes"]:
                differences.append((name, text, record))
                continue
            seen["agree"] += 1
            seen["accepted" if formulas(python) is not None else "rejected"] += 1
            # The W7 skeleton has no nesting limit: a text Python refuses for its size is not W7's to judge.
            if w7 is not None and w7[k] is not None and not isinstance(python, ResourceLimit):
                seen["w7 read"] += 1
                if w7[k] != formulas(python):
                    differences.append((name, text, {"w7": w7[k], "python": formulas(python)}))
    assert differences == []
    assert seen["agree"] == len(FIXTURES)
    assert seen["accepted"] > 40 and seen["rejected"] > 20 and seen["w7 read"] > 10, seen


def test_the_comparison_sees_a_planted_difference(monkeypatch):
    """The three-way comparison is not vacuous: a Lean answer with one formula changed is a difference."""
    env, options = ENVIRONMENTS["F"]()
    words = EN.EnglishVocabulary(env, **options)
    def changed(case):
        response = answer(case)
        response["ast"][0] = ["top"]
        return response
    monkeypatch.setattr(L, "TRANSPORT", changed)
    text = "Alice owns legacy."
    record = L.shadow_record(env, text, words, python_reading(env, text, words, options),
                             lean_reading(env, text, words, options))
    assert record["classes"] and record["lean"]["formulas"] == [["top"]], record


# ------------------------------------------------------------------ admission end to end

ADMISSION = ["Every service is reviewed.", "Legacy is deployed. It is reviewed.",
             "Legacy is deployed. Therefore legacy is deployed.", "Alice owns legacy.",
             "Every deployed service has an owner.", "Every sevice is reviewed.", "Every service is reviewed",
             "Legacy, alice and legacy are deployed.", "For every person, some service is deployed.",
             "Legacy is deployed. Therefore legacy is reviewed."]


def outcome(env, text, options):
    try:
        result = EN.parse_english_with_metadata(env, text, **options)
        return ("ok", [EN.ast._to_data(f) for f in result.document.formulas], result.canonical_text,
                result.english_text, result.conclusions)
    except VEError as exc:
        return (type(exc).__name__, str(exc))


def test_admission_under_shadow_records_agreement_with_the_real_reader(monkeypatch, tmp_path):
    env, options = ENVIRONMENTS["F"]()
    monkeypatch.setenv("VE_AUTHORITY_OVERRIDES", "english.admission=python")
    expected = {text: outcome(env, text, options) for text in ADMISSION}
    log = tmp_path / "ve-shadow.jsonl"
    monkeypatch.setenv("VE_SHADOW_LOG", str(log))
    monkeypatch.setenv("VE_AUTHORITY_OVERRIDES", "english.admission=shadow")
    assert {text: outcome(env, text, options) for text in ADMISSION} == expected
    records = [json.loads(line) for line in log.read_text().splitlines()]
    assert len(records) >= len(ADMISSION)
    assert all(r["classes"] == [] and r["lean"]["status"] != "unavailable" for r in records), records
    assert {r["lean"]["status"] for r in records} == {"one", "none", "rejected"}
    assert any(r.get("conclusion_rejected") for r in records)


def test_admission_under_lean_authority_gives_pythons_outcome(monkeypatch):
    """The same input gets the same verdict on both paths (checklist 10), with Lean's reading."""
    env, options = ENVIRONMENTS["F"]()
    for text in ADMISSION:
        monkeypatch.setenv("VE_AUTHORITY_OVERRIDES", "english.admission=python")
        python = outcome(env, text, options)
        monkeypatch.setenv("VE_AUTHORITY_OVERRIDES", "english.admission=lean")
        lean = outcome(env, text, options)
        assert lean[0] == python[0], (text, python, lean)
        if python[0] == "ok":
            assert lean == python


# ------------------------------------------------------------------ identities (base 8.8)

def route(cases: list[dict], mode: str = "english.read") -> list[dict]:
    done = subprocess.run([str(ROUTE), mode], input=json.dumps(cases).encode(), capture_output=True,
                          timeout=HANG_TIMEOUT)
    assert done.returncode in (0, 1) and b"PANIC" not in done.stderr, done.stderr[-2000:]
    rows = json.loads(done.stdout)
    assert len(rows) == len(cases)
    assert (done.returncode == 1) == any(row["status"] == "error" for row in rows)
    return rows


def request(name: str, text: str, **changes) -> dict:
    env, options = ENVIRONMENTS[name]()
    return {**L.request(env, text, EN.EnglishVocabulary(env, **options), options), **changes}


def answer(case: dict) -> dict:
    [row] = route([case])
    assert row["status"] == "ok", row
    return row["result"]


def test_i1_i2_the_identities_of_one_text_twice_and_respaced():
    first, second = answer(request("F", "Alice owns legacy.")), answer(request("F", "Alice owns legacy."))
    assert first == second
    spaced = answer(request("F", "Alice owns  legacy."))
    assert spaced["identities"]["source_sha256"] != first["identities"]["source_sha256"]
    assert {k: v for k, v in spaced["identities"].items() if k != "source_sha256"} == \
        {k: v for k, v in first["identities"].items() if k != "source_sha256"}
    assert spaced["ast"] == first["ast"]


def test_i3_another_lexicon_changes_only_the_lexicon_id():
    base = request("F", "Every service is reviewed.")
    other = copy.deepcopy(base)
    other["lexicon"]["wordings"][1] = ["owns", '{0} has the recorded relation "owns" to {1}']
    other["lexicon"]["negatives"] = [["reviewed", "{0} is not reviewed"]]
    a, b = answer(base), answer(other)
    assert a["status"] == b["status"] == "one" and a["ast"] == b["ast"]
    assert [k for k in a["identities"] if a["identities"][k] != b["identities"][k]] == ["lexicon_id"]
    assert b["identities"]["lexicon_id"] == EG.lexicon_id(other["lexicon"])


def test_i4_a_stated_lexicon_id_is_not_read():
    """The request has no `lexicon_id`: the service computes it, so a stated one is an unknown field."""
    row = route([request("F", "Alice owns legacy.", lexicon_id="0" * 64)])[0]
    assert row["status"] == "error" and "fields do not match" in row["error"]


@pytest.mark.parametrize("name", ["F", "F53"])
def test_i6_the_overlay_digest_is_present_exactly_with_an_overlay(name):
    env, options = ENVIRONMENTS[name]()
    words = EN.EnglishVocabulary(env, **options)
    case = request(name, "Alice owns legacy.")
    found = answer(case)["identities"]
    assert found == L.identities(env, case["source"], words, case["lexicon"])
    assert ("overlay_digest" in found) is bool(options)


def test_every_identity_is_the_adapters():
    """The six identities of every fixture answer are those the adapter computes from the same request."""
    for name, text in FIXTURES[::7]:
        env, options = ENVIRONMENTS[name]()
        words = EN.EnglishVocabulary(env, **options)
        case = L.request(env, text, words, options)
        assert answer(case)["identities"] == L.identities(env, text, words, case["lexicon"]), (name, text)


# ------------------------------------------------------------------ the answer's fields

def test_a_derivation_names_the_rules_with_their_spans():
    result = answer(request("F", "Legacy is deployed. It is reviewed."))
    assert result["derivation"] == [
        [["sentence.plain", 0, 3], ["formula.atom", 0, 3], ["clause.deployed", 0, 3], ["term.constant", 0, 1],
         ["constant.legacy", 0, 1]],
        [["sentence.plain", 0, 3], ["formula.atom", 0, 3], ["clause.reviewed", 0, 3], ["term.it", 0, 1]]]
    assert "canonical" not in result  # Python's printer renders Lean's formulas (one owner)


def test_many_carries_two_witness_trees():
    result = answer(request("FD", "Every deployed service is reviewed."))
    assert result["status"] == "many" and result["code"] == "Ambiguous" and result["sentence"] == 0
    roots = [tree[1][0] for tree in result["witnesses"]]
    assert sorted(roots) == ["formula.natural", "formula.universal"]


@pytest.mark.parametrize("text, code, sentence", [
    ("Legacy is deployed. Alice owns it.", "PronounUnresolved", 1),
    ("For every person, some service is deployed.", "NaturalScoped", 0),
    ("Every service is reviewed", "Unterminated", None),
])
def test_rejections_carry_their_code_text_and_sentence(text, code, sentence):
    result = answer(request("F", text))
    assert result["status"] == "rejected" and result["code"] == code
    assert result.get("sentence") == sentence
    assert result["text"].startswith(f"Sentence {sentence + 1} ") if sentence is not None else result["text"]


def test_an_invalid_lexicon_is_invalid_grammar_with_its_first_failure():
    case = request("F", "Alice owns legacy.")
    case["lexicon"]["wordings"][1] = ["owns", '{0} has the recorded relation "owns" to {1}']
    result = answer(case)
    assert result["status"] == "invalidGrammar" and result["fault"] == "lexicon"
    assert result["failure"] == ["V5", "negative", "owns"]


# ------------------------------------------------------------------ translation mode (base 4.3, spec 8.4)

@pytest.mark.parametrize("name, cap, text, status, count, complete", [
    ("FD", 2, "Every deployed service is reviewed.", "many", 2, False),
    ("FD", 3, "Every deployed service is reviewed.", "many", 2, True),
    ("F", 2, "Every service is reviewed.", "one", 1, True),
    ("F", 2, "Every sevice is reviewed.", "none", 0, True),
    ("F", 0, "Every service is reviewed.", "budget", 0, False),
    ("F", 1, "Every service is reviewed.", "budget", 1, False),
])
def test_translation_mode(name, cap, text, status, count, complete):
    """tr1 to tr4: a set that is not complete is never a verdict: cap 0 gives no reading and `budget`."""
    result = answer(request(name, text, mode="translation", cap=cap))
    assert (result["status"], len(result["readings"]), result["complete"]) == (status, count, complete)


def test_translation_mode_reads_one_sentence():
    result = answer(request("F", "Legacy is deployed. Legacy is reviewed.", mode="translation"))
    assert (result["status"], result["code"]) == ("rejected", "NotOneSentence")


def test_authoring_reads_at_cap_two_only():
    row = route([request("F", "Alice owns legacy.", cap=3)])[0]
    assert row["status"] == "error" and "cap 2" in row["error"]


# ------------------------------------------------------------------ the export (spec 4.4)

def grammar_request(name: str) -> dict:
    env, options = ENVIRONMENTS[name]()
    case = L.request(env, "x.", EN.EnglishVocabulary(env, **options), options)
    return {k: v for k, v in case.items() if k not in ("source", "mode", "cap")}


def test_the_export_is_the_grammar_with_the_sources_rows():
    spec = __import__("importlib").util.spec_from_file_location("english_grammar_gen",
                                                                ROOT / "tools/english_grammar_gen.py")
    G = __import__("importlib").util.module_from_spec(spec)
    spec.loader.exec_module(G)
    [row] = route([grammar_request("F")], "english.grammar")
    result = row["result"]
    assert result["nonterminals"] == [n for n, _ in G.CATALOGUE] and result["ranks"] == [r for _, r in G.CATALOGUE]
    table = G.table_rows(G.parse_source((ROOT / "ve/english_grammar/relational-fol@0.json").read_bytes(), "x"))
    rules = result["rules"]
    assert [r["index"] for r in rules] == list(range(len(rules))) and len(rules) == 127
    for got, want in zip(rules, table):
        rhs = [s if type(s) is str or "p" not in s else {"before": False, "after": False, **s} for s in want["rhs"]]
        assert (got["tag"], got["lhs"], got["act"], got["rhs"]) == (want["tag"], want["lhs"], G.act_text(want), rhs)
    lexical = {r["tag"]: r for r in rules[len(table):]}
    assert lexical["clause.owns"]["act"] == 'pred "owns" [0,1] false'
    assert lexical["clause.owns"]["rhs"] == [{"n": "term"}, {"c": "owns"}, {"n": "term"}]
    env, options = ENVIRONMENTS["F"]()
    words = EN.EnglishVocabulary(env, **options)
    expected = L.identities(env, "", words, EG.export(words))
    del expected["source_sha256"]
    assert result["identities"] == expected


def test_the_export_carries_kwmid():
    [row] = route([grammar_request("Fapi")], "english.grammar")
    capital = next(r for r in row["result"]["rules"] if r["tag"] == "constant.api.capital")
    assert capital["rhs"] == [{"kwMid": "The"}, "api"]


# ------------------------------------------------------------------ malformed requests (checklist 5)

REPLACEMENTS = [7, True, None, [], {}, "deep"]


def _nodes(value, path=()):
    yield path
    if type(value) is dict:
        for key, item in value.items():
            yield from _nodes(item, (*path, key))
    elif type(value) is list:
        for k, item in enumerate(value):
            yield from _nodes(item, (*path, k))


def _replace(value, path, new):
    out = copy.deepcopy(value)
    node = out
    for step in path[:-1]:
        node = node[step]
    node[path[-1]] = json.loads("[" * 300 + "]" * 300) if new == "deep" else new
    return out


def test_every_malformed_request_is_an_error_row_or_an_answer():
    """Each node of a genuine request (environment, overlay, lexicon, source, mode, cap) replaced by 7, true,
    null, [], {} or a 300-deep array: the route answers every case with one row, an error or an answer, and
    never crashes; the adapter turns every such row into `CheckerUnavailable` or a checked answer."""
    base = request("F53", "Alice owns legacy.")
    mutants = [_replace(base, path, new) for path in _nodes(base) if path and path != ("id",)
               for new in REPLACEMENTS if path[0] != "environment" or len(path) < 4]
    for k, mutant in enumerate(mutants):
        mutant["id"] = f"m{k}"
    nulls = [m for m in mutants if "null" in json.dumps(m)]
    rows = []
    for start in range(0, len(mutants), 200):
        batch = [m for m in mutants[start:start + 200] if m not in nulls]
        rows += route(batch)
    assert len(mutants) > 300 and rows
    assert all(row["status"] in ("ok", "error") for row in rows)
    errors = sum(row["status"] == "error" for row in rows)
    assert errors > len(rows) // 2
    # JSON null is refused before any case is read (VE's restricted wire): a framing error, no rows.
    for mutant in nulls[:20]:
        done = subprocess.run([str(ROUTE), "english.read"], input=json.dumps([mutant]).encode(),
                              capture_output=True, timeout=HANG_TIMEOUT)
        assert done.returncode == 2 and done.stdout == b"" and b"PANIC" not in done.stderr
        with pytest.raises(lean_backend.NoAnswer):
            lean_backend.read_rows(done.returncode, done.stdout, [mutant], restricted=True)


def test_a_lexicon_for_another_environment_is_refused():
    case = request("F", "Alice owns legacy.")
    case["lexicon"]["environment_id"] = "0" * 64
    [row] = route([case])
    assert row["status"] == "error" and "another environment" in row["error"]


def test_a_route_that_answers_for_another_lexicon_fails_closed(monkeypatch):
    """i4 through the adapter: the real answer to a request with a changed lexicon, returned for the original
    request, carries a different `lexicon_id`, and the adapter refuses it."""
    env, options = ENVIRONMENTS["F"]()
    other = request("F", "Alice owns legacy.")
    other["lexicon"]["aliases"] = [["owns", "{0} has {1}", False]]
    monkeypatch.setattr(L, "TRANSPORT", lambda case: answer({**other, "source": case["source"]}))
    with pytest.raises(CheckerUnavailable, match="lexicon_id"):
        L.read(env, "Alice owns legacy.", EN.EnglishVocabulary(env, **options), options)
