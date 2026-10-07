"""Independent cases for the format-1 diagnostic interpreter."""

from ve.errors import CheckerUnavailable, VEError
from conformance.wire_contract_engine import CLEAN, Deferred, Fault, Registry, overlay, run


def _table(phases, *, name="demo@0", codes=None):
    codes = codes or {"BAD": {"class": "InvalidInput", "summary": "Bad input"}}
    return {"contract": name, "revision": 1, "format": 1, "status": "shadow",
            "input": ["doc"], "uses": [], "codes": codes, "residual": "BAD",
            "phases": phases}


def _check(id, kind, at, **kwargs):
    return {"id": id, "kind": kind, "at": at, "code": "BAD", "text": kwargs.pop("text", id),
            **kwargs}


def test_phase_and_item_order_are_distinct():
    table = _table([
        {"name": "shape", "checks": [_check("1", "type", "/doc", type="object")]},
        {"name": "items", "checks": [
            {"id": "g1", "each": "/doc/items/*", "checks": [
                _check("2a", "name", "@/name", **{"class": "word"}),
                _check("2b", "type", "@/tags", type={"array_of": "string"})]},
            {"id": "g2", "each": "/doc/items/*", "checks": [
                _check("3", "sorted_unique", "@/tags")]}]}])
    names = {"word": {"first": "a-z", "rest": "a-z0-9_"}}
    root = {"doc": {"items": [{"name": "a", "tags": [1]},
                              {"name": "B", "tags": ["x"]}]}}
    assert run(table, root, names=names).record["check"] == "2b"
    root["doc"]["items"][0]["tags"] = ["z", "a"]
    root["doc"]["items"][1]["name"] = "a"
    assert run(table, root, names=names).record["check"] == "3"


def test_code_point_key_order_and_unique_so_far():
    table = _table([{"name": "p", "checks": [
        {"id": "g", "each": "/doc/*", "checks": [
            _check("a", "name", "@", **{"class": "ascii", "on": "key"}),
            _check("b", "unique_so_far", "@")] }]}])
    names = {"ascii": {"first": "a-z"}}
    result = run(table, {"doc": {"😀": 1, "ｚ": 1}}, names=names)
    assert result.record["path"] == "/doc/ｚ"
    table["phases"][0]["checks"][0]["checks"].pop(0)
    result = run(table, {"doc": {"a": 1, "b": 1}}, names=names)
    assert result.record["path"] == "/doc/b"


def test_include_view_and_deferred_overlay():
    inner = _table([{"name": "body", "checks": [_check("b1", "type", "/x",
                                                       type="integer", text="value {value:json}")]}],
                   name="inner@0")
    outer = _table([{"name": "main", "checks": [
        {"id": "a", "kind": "include", "contract": "inner@0", "phases": ["body"],
         "at": "/doc", "view": "pick", "says": "The view gives x.", "as": "BAD"}]}])
    result = run(outer, {"doc": {"x": "wrong"}}, contracts={"inner@0": inner})
    assert result == Deferred("a")
    record = overlay(outer, VEError("legacy"), result)
    assert record == {"contract": "demo@0", "revision": 1, "deferred": "a", "text": "legacy"}
    def unavailable():
        raise CheckerUnavailable("diagnoser unavailable")
    assert overlay(outer, VEError("legacy"), result, lean=unavailable) == record
    registry = Registry().register(views={"pick": lambda value: {"x": value["x"]}})
    result = run(outer, {"doc": {"x": "wrong"}}, registry=registry,
                 contracts={"inner@0": inner})
    assert isinstance(result, Fault)
    assert result.record["check"] == "a/b1"
    assert result.record["path"] == "/doc"
    assert result.record["args"] == {"value": '"wrong"', "inner_path": "/x"}
    assert result.record["code"] == "BAD"
    assert run(outer, {"doc": {"x": 1}}, registry=registry,
               contracts={"inner@0": inner}) is CLEAN


def test_error_diagnostic_is_opt_in():
    error = VEError("old")
    assert error.to_dict() == {"code": "InvalidInput", "message": "old"}
    error.diagnostic = {"check": "1"}
    assert error.to_dict()["diagnostic"] == {"check": "1"}


def test_strict_json_equality_tuple_array_and_outside_domain():
    table = _table([{"name": "p", "checks": [
        _check("1", "const", "/doc/flag", value=0),
        _check("2", "type", "/doc/items", type={"tuple": ["integer", "string"]})]}])
    assert run(table, {"doc": {"flag": False, "items": (1, "x")}}).record["check"] == "1"
    assert run(table, {"doc": {"flag": 0, "items": (1, "x")}}) is CLEAN
    assert run(table, {"doc": {"flag": 0, "items": (1, 2)}}).record["check"] == "2"
    assert run(table, {"doc": {"flag": 0, "items": [1.0, "x"]}}) is CLEAN


def test_json_renderer_uses_full_control_escapes():
    table = _table([{"name": "p", "checks": [
        _check("1", "type", "/doc", type="integer", text="bad {value:json}")]}])
    record = run(table, {"doc": "a\n\t\"\\"}).record
    assert record["text"] == 'bad "a\\u000a\\u0009\\"\\\\"'
    assert record["args"] == {"value": '"a\\u000a\\u0009\\"\\\\"'}


def _nested_tables(*, view):
    """outer@0 includes mid@0 at /doc (with or without a view); mid@0 includes inner@0 at /part."""
    inner = _table([{"name": "body", "checks": [
        _check("b1", "type", "/x", type="integer", text="x {value:json}")]}], name="inner@0")
    mid = _table([{"name": "body", "checks": [
        {"id": "m1", "kind": "include", "contract": "inner@0", "phases": ["body"], "at": "/part",
         "as": "MID"}]}],
        name="mid@0", codes={"BAD": {"class": "InvalidInput", "summary": "Bad"},
                             "MID": {"class": "ResourceLimit", "summary": "Mid"}})
    include = {"id": "o1", "kind": "include", "contract": "mid@0", "phases": ["body"], "at": "/doc"}
    if view:
        include.update(view="same", says="The view gives the value itself.")
    outer = _table([{"name": "main", "checks": [include]}], name="outer@0")
    contracts = {"inner@0": inner, "mid@0": mid}
    registry = Registry().register(views={"same": lambda value: value})
    return outer, contracts, registry


def test_view_site_then_nested_include_path():
    """Wire review (Astra A): under a view, `path` is the view's site and `inner_path` holds the sites of the
    includes inside the view, then the local pointer, as Lean's `Frame.enter` builds them."""
    outer, contracts, registry = _nested_tables(view=True)
    record = run(outer, {"doc": {"part": {"x": "s"}}}, registry=registry, contracts=contracts).record
    assert record["check"] == "o1/m1/b1"
    assert record["path"] == "/doc"
    assert record["args"] == {"value": '"s"', "inner_path": "/part/x"}


def test_nested_includes_without_view_concatenate_sites():
    outer, contracts, registry = _nested_tables(view=False)
    record = run(outer, {"doc": {"part": {"x": "s"}}}, registry=registry, contracts=contracts).record
    assert record["path"] == "/doc/part/x"
    assert record["args"] == {"value": '"s"'}


def test_inner_as_code_takes_the_class_of_its_declaring_contract():
    """`as` on an include inside an included contract is declared there, not in the contract that runs."""
    outer, contracts, registry = _nested_tables(view=False)
    record = run(outer, {"doc": {"part": {"x": "s"}}}, registry=registry, contracts=contracts).record
    assert (record["code"], record["class"]) == ("MID", "ResourceLimit")


def test_template_braces_and_control_characters_in_values():
    """Wire review (Fable B2): `{{` and `}}` are literal braces, and a value holding U+0001 or U+0002 is
    rendered as it is."""
    table = _table([{"name": "p", "checks": [
        _check("1", "type", "/doc", type="integer", text="{{{value}}} {{x}}")]}])
    record = run(table, {"doc": "a\x01b\x02c"}).record
    assert record["text"] == "{a\x01b\x02c} {x}"
    assert record["args"] == {"value": "a\x01b\x02c"}


def test_template_pieces_refuse_unbalanced_braces():
    import pytest
    from conformance.wire_contract_engine import pieces
    assert pieces("a {{b}} {c:json}") == [("lit", "a {b} "), ("arg", "c", "json")]
    for bad in ("a { b", "a } b", "{x"):
        with pytest.raises(ValueError):
            pieces(bad)
