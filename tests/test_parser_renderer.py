import pytest

from ve.ast import Binary, Document, Exists, Forall, Implies, Unary, Var
from ve.environment import Environment, LANGUAGE, PROFILE, SPEC_REVISION
from ve.errors import ResourceLimit, ShadowedVariable, SyntaxError, UnboundVariable, UnknownSymbol, VEError
from ve.fol import document_from_indexed_json, document_from_named_fol, render_fol
from ve.parser import canonicalize, is_canonical, parse, parse_with_metadata
from ve.printer import NATURAL_RENDERER_VERSION, natural_document, print_document


@pytest.fixture
def env():
    return Environment.from_dict({
        "language": LANGUAGE, "profile": PROFILE, "spec_revision": SPEC_REVISION,
        "vocabulary": {
            "sorts": {"person": {"description": "person"}, "service": {"description": "service"}},
            "predicates": {
                "deployed": {"arguments": ["service"], "description": "deployed"},
                "owns": {"arguments": ["person", "service"], "description": "owns"},
            },
            "constants": {"api": {"sort": "service", "description": "the API"}},
        },
    })


def test_nested_binding_resolves_de_bruijn_and_canonicalizes(env):
    source = "for every service s, (there exists person p, (p owns s)).\n"
    expected = Document((Forall("service", Exists("person", Binary("owns", Var(0), Var(1)))),))
    assert parse(env, source) == expected
    canonical = "for every service x0, (there exists person x1, (x1 owns x0)).\n"
    assert canonicalize(env, source) == canonical
    assert is_canonical(env, canonical)
    assert not is_canonical(env, source)
    assert parse(env, print_document(env, expected)) == expected


def test_statement_counter_resets(env):
    doc = parse(env, "there exists service s, (s is deployed).\nthere exists service t, (t is deployed).\n")
    assert print_document(env, doc).splitlines() == [
        "there exists service x0, (x0 is deployed).",
        "there exists service x0, (x0 is deployed).",
    ]


@pytest.mark.parametrize("bad", [
    "true.", "true.\r\n", " true.\n", "true .\n", "(true).\n",
    "TRUE.\n", "true.\n\n", "true.\n# comment\n",
])
def test_strict_syntax_rejects_variants(env, bad):
    with pytest.raises(SyntaxError): parse(env, bad)


def test_true_and_false_are_tokens_not_identifier_prefixes(env):
    with pytest.raises(UnboundVariable): parse(env, "trueish is deployed.\n")


def test_name_errors_have_source_spans(env):
    with pytest.raises(UnboundVariable) as caught: parse(env, "s is deployed.\n")
    assert caught.value.span.line == 1 and caught.value.span.column == 1
    with pytest.raises(ShadowedVariable):
        parse(env, "for every service s, (there exists service s, (true)).\n")
    with pytest.raises(UnknownSymbol): parse(env, "@api is absent.\n")


def test_sibling_binders_may_reuse_name(env):
    parse(env, "(there exists service s, (s is deployed)) and (there exists service s, (s is deployed)).\n")


def test_metadata_is_separate_from_semantic_ast(env):
    result = parse_with_metadata(env, "there exists service s, (s is deployed).\n")
    assert result.document == parse(env, "there exists service q, (q is deployed).\n")
    assert "s" in result.metadata.source_names
    assert result.metadata.spans


def test_natural_view_preserves_premise_existence_and_dependency(env):
    doc = Document((Forall("service", Implies(
        Unary("deployed", Var(0)), Exists("person", Binary("owns", Var(0), Var(1))))),))
    view = natural_document(env, doc)
    assert view.version == NATURAL_RENDERER_VERSION
    assert "if (x0 satisfies deployed), then" in view.text
    assert "there exists at least one person x1" in view.text
    assert "x1 stands in relation owns to x0" in view.text


def test_indexed_fol_import_and_render(env):
    wire = [["forall", "service", ["implies", ["unary", "deployed", ["var", 0]],
             ["exists", "person", ["binary", "owns", ["var", 0], ["var", 1]]]]]]
    doc = document_from_indexed_json(env, wire)
    assert render_fol(env, wire) == print_document(env, doc)
    assert "there exists at least one" in render_fol(env, wire, view="natural").text


def test_named_fol_requires_explicit_binders_and_no_inference(env):
    named = {"formulas": [{"op": "forall", "sort": "service", "variable": "s", "body": {
        "op": "exists", "sort": "person", "variable": "p", "body": {
            "op": "binary", "predicate": "owns", "left": {"var": "p"}, "right": {"var": "s"}}}}]}
    assert document_from_named_fol(env, named) == parse(
        env, "for every service s, (there exists person p, (p owns s)).\n")
    with pytest.raises(SyntaxError):
        document_from_named_fol(env, {"formulas": [{"op": "forall", "variable": "s", "body": {"op": "top"}}]})


def test_raw_fol_is_type_checked(env):
    with pytest.raises(Exception):
        document_from_indexed_json(env, [["unary", "deployed", ["const", "missing"]]])
    with pytest.raises(Exception):
        document_from_indexed_json(env, [["binary", "owns", ["var", 0], ["var", 1]]])


def test_named_import_rejects_invalid_unicode_even_in_discarded_names(env):
    with pytest.raises(VEError):
        document_from_named_fol(env, {"formulas": [{"op": "exists", "sort": "person",
                                                   "variable": "\ud800", "body": {"op": "top"}}]})


def test_canonical_output_respects_source_byte_envelope(env):
    statement = parse(env, "@api is deployed.\n").formulas[0]
    with pytest.raises(ResourceLimit):
        print_document(env, Document((statement,) * 5000))


def test_non_ascii_byte_diagnostic_preserves_line_and_column(env):
    with pytest.raises(SyntaxError) as caught:
        parse(env, b"true.\n\xff.\n")
    assert (caught.value.span.line, caught.value.span.column) == (2, 1)
