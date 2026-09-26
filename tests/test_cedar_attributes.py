from ve.adapters.attributes import Value, attribute, compare, has


def test_defined_value_keeps_missing_distinct_from_false():
    context = {"principal": {"active": False, "department": "finance"}}
    assert attribute(context, ("principal", "active")).defined
    assert attribute(context, ("principal", "active")).value is False
    assert has(context, ("principal", "active")) == Value(True, True)
    assert has(context, ("principal", "missing")) == Value(True, False)
    assert has(context, ("absent", "active")) == Value(False)
    assert has({"principal": False}, ("principal", "active")) == Value(False)
    assert has(context, ("principal",)) == Value(True, True)
    assert compare(context, ("principal", "department"), "finance").value is True
    assert compare(context, ("principal", "missing"), "finance").defined is False
    assert compare(context, ("principal", "missing"), "finance", "!=").defined is False


def test_cedar_comparisons_preserve_value_types():
    assert compare({"v": False}, ("v",), 0) == Value(True, False)
    assert compare({"v": 1}, ("v",), True) == Value(True, False)
    assert compare({"v": [False]}, ("v",), [0]) == Value(True, False)
    assert compare({"v": {"a": False}}, ("v",), {"a": 0}) == Value(True, False)
    assert compare({"v": [1, 2]}, ("v",), [2, 1, 1]) == Value(True, True)
