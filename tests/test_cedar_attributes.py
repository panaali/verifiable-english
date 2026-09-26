from ve.adapters.attributes import attribute, compare, has


def test_defined_value_keeps_missing_distinct_from_false():
    context = {"principal": {"active": False, "department": "finance"}}
    assert attribute(context, ("principal", "active")).defined
    assert attribute(context, ("principal", "active")).value is False
    assert has(context, ("principal", "active"))
    assert not has(context, ("principal", "missing"))
    assert compare(context, ("principal", "department"), "finance").value is True
    assert compare(context, ("principal", "missing"), "finance").defined is False
    assert compare(context, ("principal", "missing"), "finance", "!=").defined is False
