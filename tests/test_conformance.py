import json
import hashlib

import pytest

from ve.ast import (
    And,
    Binary,
    Document,
    Eq,
    Exists,
    Forall,
    Top,
    Var,
    check_document,
    document_from_data,
    document_to_data,
)
from ve.environment import Environment
from ve.errors import ResourceLimit, VEError
from ve.identity import meaning_id, source_id
from ve.check import check
from ve.limits import MAX_NODES
from ve.model import FiniteModel
from ve.parser import canonicalize, is_canonical, parse
from ve.printer import print_document
from ve.wire import canonical_json, loads_json


ENV_DATA = {
    "language": "ve.core@0",
    "profile": "relational-fol@0",
    "spec_revision": "ve-v0-draft-2026-09-20",
    "vocabulary": {
        "sorts": {
            "person": {"description": "A person."},
            "service": {"description": "A service."},
        },
        "predicates": {
            "deployed": {"arguments": ["service"], "description": "Is deployed."},
            "owns": {
                "arguments": ["person", "service"],
                "description": "Owns the service.",
            },
        },
        "constants": {},
    },
}


@pytest.fixture
def env():
    return Environment.from_dict(ENV_DATA)


def error_code(exc: pytest.ExceptionInfo[VEError]) -> str:
    return exc.value.code


@pytest.mark.parametrize(
    "source",
    [
        "",
        "true.",
        "true.\r\n",
        " true.\n",
        "true. \n",
        "true.\n\n",
        "True.\n",
        "(true).\n",
        "not  (true).\n",
        "true。\n",
        "# comment\ntrue.\n",
        "true.\t\n",
    ],
)
def test_strict_parser_rejects_non_grammar_bytes(env, source):
    with pytest.raises(VEError) as exc:
        parse(env, source)
    # The required guarantee is rejection without repair. Depending on how far
    # token recognition got, a malformed construct can expose a more specific
    # symbol/binding diagnostic.
    assert error_code(exc) in {"SyntaxError", "ResourceLimit", "UnboundVariable", "UnknownSymbol"}


def test_nested_names_resolve_to_nearest_first_de_bruijn_indices(env):
    source = "for every service s, (there exists person p, (p owns s)).\n"
    doc = parse(env, source)
    assert document_to_data(env, doc) == [
        ["forall", "service", ["exists", "person", ["binary", "owns", ["var", 0], ["var", 1]]]]
    ]


def test_shadowing_rejected_but_sibling_reuse_accepted(env):
    with pytest.raises(VEError) as exc:
        parse(env, "for every service a, (there exists person a, (true)).\n")
    assert error_code(exc) == "ShadowedVariable"

    parse(
        env,
        "(there exists service a, (true)) and (there exists service a, (true)).\n",
    )


def test_canonical_names_are_preorder_fresh_and_reset_per_statement(env):
    source = (
        "(there exists service left, (true)) and (there exists service right, (true)).\n"
        "there exists person person_var, (true).\n"
    )
    expected = (
        "(there exists service x0, (true)) and (there exists service x1, (true)).\n"
        "there exists person x0, (true).\n"
    )
    assert canonicalize(env, source) == expected
    assert print_document(env, parse(env, source)) == expected
    assert is_canonical(env, expected)
    assert not is_canonical(env, source)


def test_alpha_variants_have_same_ast_and_meaning_but_distinct_source_id(env):
    a = "for every service s, (s equals s).\n"
    b = "for every service other, (other equals other).\n"
    da, db = parse(env, a), parse(env, b)
    assert da == db
    assert meaning_id(env, da) == meaning_id(env, db)
    assert source_id(a) != source_id(b)


@pytest.mark.parametrize(
    ("data", "code"),
    [
        ([["var", 0]], "SyntaxError"),  # terms are not formulas
        ([["eq", ["var", 0], ["var", 0]]], "UnboundVariable"),
        ([["forall", "service", ["var", 1]]], "SyntaxError"),
        ([["forall", "service", ["eq", ["var", -1], ["var", 0]]]], "SyntaxError"),
        ([["forall", "service", ["eq", ["var", True], ["var", 0]]]], "SyntaxError"),
        ([["mystery"]], "SyntaxError"),
        ([["top", "extra"]], "SyntaxError"),
    ],
)
def test_ast_wire_rejects_bad_tags_arities_and_indices(env, data, code):
    with pytest.raises(VEError) as exc:
        document_from_data(env, data)
    assert error_code(exc) in {code, "InvalidInput", "UnboundVariable"}


def test_environment_json_duplicate_keys_rejected_before_overwrite():
    raw = json.dumps(ENV_DATA)
    duplicate = raw.replace('"language": "ve.core@0"', '"language": "wrong", "language": "ve.core@0"')
    with pytest.raises(VEError):
        Environment.from_json(duplicate)


def test_environment_identity_ignores_json_format_and_key_order():
    compact = json.dumps(ENV_DATA, separators=(",", ":"))
    reversed_top = json.dumps(dict(reversed(list(ENV_DATA.items()))), indent=2)
    assert Environment.from_json(compact).environment_id == Environment.from_json(reversed_top).environment_id


def test_environment_description_is_identity_bearing():
    changed = json.loads(json.dumps(ENV_DATA))
    changed["vocabulary"]["sorts"]["person"]["description"] = "A differently described person."
    assert Environment.from_dict(changed).environment_id != Environment.from_dict(ENV_DATA).environment_id


def test_environment_rejects_unknown_fields_and_lone_surrogates():
    unknown = json.loads(json.dumps(ENV_DATA))
    unknown["extra"] = True
    with pytest.raises(VEError):
        Environment.from_dict(unknown)

    surrogate = json.loads(json.dumps(ENV_DATA))
    surrogate["vocabulary"]["sorts"]["person"]["description"] = "bad\ud800"
    with pytest.raises(VEError):
        Environment.from_dict(surrogate)


def test_source_byte_and_resource_boundaries(env):
    with pytest.raises(VEError) as exc:
        parse(env, b"true.\n\xff")
    assert error_code(exc) == "SyntaxError"

    oversized = "true.\n" * 11_000  # 66,000 bytes > the 64 KiB source limit
    with pytest.raises(ResourceLimit):
        parse(env, oversized)


def test_formula_order_is_identity_bearing(env):
    first = Document((Top(), Forall("service", Top())))
    second = Document(tuple(reversed(first.formulas)))
    assert meaning_id(env, first) != meaning_id(env, second)


def test_jcs_utf16_key_order_and_string_escaping_golden():
    # RFC 8785 orders object properties by UTF-16 code units.  In particular,
    # the supplementary-plane emoji sorts before U+FB33.
    value = {
        "\u20ac": "Euro Sign",
        "\r": "Carriage Return",
        "\ufb33": "Hebrew Letter Dalet With Dagesh",
        "1": "One",
        "\U0001f600": "Emoji: Grinning Face",
        "\u0080": "Control",
        "\u00f6": "Latin Small Letter O With Diaeresis",
    }
    expected = (
        b'{"\\r":"Carriage Return","1":"One","\xc2\x80":"Control",'
        b'"\xc3\xb6":"Latin Small Letter O With Diaeresis",'
        b'"\xe2\x82\xac":"Euro Sign","\xf0\x9f\x98\x80":"Emoji: Grinning Face",'
        b'"\xef\xac\xb3":"Hebrew Letter Dalet With Dagesh"}'
    )
    assert canonical_json(value) == expected


def test_json_integer_boundary_and_noninteger_rejection():
    assert loads_json("9007199254740991") == 9_007_199_254_740_991
    for raw in ("9007199254740992", "-1", "1.0", "1e0", "NaN", "Infinity"):
        with pytest.raises(VEError):
            loads_json(raw)


def test_identity_preimages_have_exact_domain_and_shape(env):
    expected_environment = hashlib.sha256(
        b"ve-environment-v0\n" + canonical_json(env.to_dict())
    ).hexdigest()
    assert env.environment_id == expected_environment

    document = Document((Top(),))
    payload = {"environment_id": expected_environment, "ast": [["top"]]}
    expected_meaning = hashlib.sha256(
        b"ve-meaning-v0\n" + canonical_json(payload)
    ).hexdigest()
    assert meaning_id(env, document) == expected_meaning
    assert source_id(b"true.\n") == hashlib.sha256(b"ve-source-v0\ntrue.\n").hexdigest()


def test_nested_declaration_fields_are_exact():
    bad = json.loads(json.dumps(ENV_DATA))
    bad["vocabulary"]["predicates"]["owns"]["extra"] = "not allowed"
    with pytest.raises(VEError):
        Environment.from_dict(bad)


def test_acceptance_rejects_valid_but_substituted_candidate_ast(env):
    source = "true.\n"
    with pytest.raises(VEError):
        check(env, source, candidate_ast=Document((Forall("service", Top()),)))
    with pytest.raises(VEError):
        check(env, source, candidate_ast=[["bottom"]])
    assert check(env, source, candidate_ast=[["top"]])["language"] == "accepted"


def test_all_semantic_boundaries_recheck_raw_ast(env):
    malformed = Document((Eq(Var(0), Var(0)),))
    for consumer in (
        lambda: check_document(env, malformed),
        lambda: print_document(env, malformed),
        lambda: meaning_id(env, malformed),
    ):
        with pytest.raises(VEError):
            consumer()


def test_ast_node_limit_accepts_exact_limit_and_rejects_one_more(env):
    exact = Document(tuple(Top() for _ in range(MAX_NODES)))
    assert check_document(env, exact) is exact
    with pytest.raises(ResourceLimit):
        check_document(env, Document(exact.formulas + (Top(),)))


def test_formula_depth_limit_has_no_off_by_one(env):
    at_limit = Top()
    for _ in range(63):
        at_limit = Forall("service", at_limit)
    assert check_document(env, Document((at_limit,)))

    over_limit = Forall("service", at_limit)
    with pytest.raises(ResourceLimit):
        check_document(env, Document((over_limit,)))


def test_same_local_id_in_different_sorts_remains_well_typed(env):
    model = FiniteModel.from_dict(
        env,
        {
            "complete": True,
            "domains": {"person": ["same"], "service": ["same"]},
            "constants": {},
            "relations": {"deployed": [], "owns": [["same", "same"]]},
        },
    )
    # Construction is the assertion: sort-qualified entities may share local IDs.
    assert model is not None


def test_model_identity_preimage_has_required_newline_domain_separator(env):
    wire_model = {
        "complete": True,
        "domains": {"person": [], "service": []},
        "constants": {},
        "relations": {"deployed": [], "owns": []},
    }
    model = FiniteModel.from_dict(env, wire_model)
    payload = {"environment_id": env.environment_id, "model": wire_model}
    expected = hashlib.sha256(b"ve-model-v0\n" + canonical_json(payload)).hexdigest()
    assert model.model_id == expected
