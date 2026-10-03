import re

import pytest

from ve.surface.registry import KEYWORDS, SurfaceRecord, dispatch, keywords, register


@pytest.fixture(autouse=True)
def isolated_registry():
    from ve.surface import registry
    records, by_type, old_keywords = registry._records.copy(), registry._by_type.copy(), registry.KEYWORDS
    yield
    registry._records.clear(); registry._records.update(records)
    registry._by_type.clear(); registry._by_type.update(by_type)
    registry.KEYWORDS = old_keywords


def test_keywords_cover_statement_initial_literals():
    source = open("ve/english.py").read()
    region = source[source.index("    def formula(self, scope="):source.index("    def document(self):")]
    expected = {"it is not the case that ", "all of the following hold:",
                "both of the following hold:", "at least one of the following holds:",
                "if the following holds:", "both ", "either ", "if ",
                "for every ", "every ", "there is ", "starting from ", "some ", "no "}
    assert expected <= {keyword for keyword, _ in KEYWORDS}
    # Statement-layer profiles may register additional initial keywords; the
    # historical formula grammar's set and ordering remain fixed within them.
    historical = tuple(keyword for keyword, _ in KEYWORDS if keyword in expected)
    assert historical == tuple(sorted(expected, key=lambda s: (-len(s), s)))
    for keyword in expected:
        assert keyword in region or keyword in source[source.index("    def natural_clause(self):"):source.index("    def owner_clause(self,")]
        assert dispatch(keyword + "x")[0] == keyword


def test_surface_record_fields():
    # The kernel never consults a registered evaluator, typing or wire hook, so
    # the record has no such slots (docs/ARCHITECTURE-LAYERS-PLAN2.md P1).
    from dataclasses import fields
    from ve.argument import _checker_build
    assert [field.name for field in fields(SurfaceRecord)] == [
        "wire_tag", "strict_form", "english_keywords", "fluent_form", "grammar_production",
        "traversal_hooks", "witness_renderer", "node_type", "wire_arity", "parser_hook",
        "strict_parser_hook", "printer_hook", "fluent_hook", "english_renderer", "grammar_hook",
        "derivation_hook", "strict_grammar_hook", "fol_import_hook", "fol_export_hook", "profiles"]
    assert re.fullmatch(r"[0-9a-f]{64}", _checker_build())


def test_registered_wire_tags_match_the_kernel_tables():
    # Every record naming a node type or wire arity, including tags registered
    # beyond ve.surface.registry's own, agrees with ve.ast's tables, and every
    # kernel tag is registered (docs/ARCHITECTURE-LAYERS-PLAN2.md P2).
    from ve import ast
    from ve.surface.registry import records
    from ve.wire import formula_tag_arity
    typed = {r.wire_tag: (r.node_type, r.wire_arity) for r in records()
             if r.node_type is not None or r.wire_arity is not None}
    assert typed == {tag: (ast.NODE_TYPES[tag], ast.WIRE_ARITY[tag]) for tag in ast.WIRE_ARITY}
    assert ast.WIRE_TAGS == {kind: tag for tag, kind in ast.NODE_TYPES.items()}
    assert len(typed) == 15
    assert {tag: formula_tag_arity(tag) for tag in typed} == ast.WIRE_ARITY
    assert formula_tag_arity("var") is None and formula_tag_arity("norm") is None
    class FutureNode:
        pass

    for tag, wrong in (("future-tag", dict(wire_arity=3)), ("future-node", dict(node_type=FutureNode)),
                       ("and", dict(node_type=ast.And, wire_arity=4)), ("and", dict(wire_arity=3)),
                       ("and", dict(node_type=ast.And))):
        from ve.surface import registry
        registry._records.pop("and"); registry._by_type.pop(ast.And)  # restored by the fixture
        with pytest.raises(ValueError, match="disagrees with the kernel wire tables"):
            register(SurfaceRecord(tag, "", (), "", "", **wrong))
        register(SurfaceRecord("and", "", (), "", "", node_type=ast.And, wire_arity=3))


def test_duplicate_keyword_refused():
    with pytest.raises(ValueError, match="Duplicate English keyword"):
        register(SurfaceRecord("test-duplicate", "", ("both ",), "", ""))


def test_overlapping_registration_uses_longest_match():
    register(SurfaceRecord("test-both-x", "", ("both x",), "", ""))
    ordered = [keyword for keyword, _ in keywords()]
    assert ordered.index("both of the following hold:") < ordered.index("both x")
    assert ordered.index("both x") < ordered.index("both ")
    assert dispatch("both x test")[0] == "both x"


def test_profile_gates_new_keyword():
    from conformance.p0 import environment
    from ve.environment import Environment
    register(SurfaceRecord("test-norm-keyword", "", ("under a rule ",), "", "",
                           profiles=("norms@0",)))
    base = Environment(environment())
    assert dispatch("under a rule x", base) is None
    raw = environment()
    raw["profiles"] = ["norms@0", "relational-fol@0"]
    assert dispatch("under a rule x", Environment(raw))[0] == "under a rule "
