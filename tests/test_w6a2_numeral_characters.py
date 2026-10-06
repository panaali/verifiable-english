"""Numeral limits count Unicode characters on every W6a route: the order and countermodel
routes in Python, Lean and Rust, the quantity routes in Lean and Python's relay of it
(Lean-first batch 9 deleted Rust's quantity route)."""
import pytest

from tests.test_units_lean_w6a import lean as lean_quantity, quantity
from tests.test_w6a_route_limits import fol, lean as lean_route, model, rust as rust_route
from tests.test_w6a_review_regressions import raw_environment
from ve import Environment
from ve.ast import document_from_data
from ve.errors import ResourceLimit, SyntaxError, VEError
from ve.units import elaborate_quantity, quantity_countermodel


@pytest.mark.parametrize("text", ["١" * 20, "١" * 21, "١" * 39, "١" * 40,
                                  "1" * 39 + "١", "١" * 41, "1" * 40, "1" * 41])
@pytest.mark.parametrize("coefficient", [False, True])
@pytest.mark.parametrize("route", ["order", "countermodel", "quantity", "quantity_countermodel"])
def test_numeral_limit_counts_characters_on_all_routes(text, coefficient, route):
    """The 21-character reproducer has 42 UTF-8 bytes; 40 is the limit."""
    limited = len(text) > 40
    malformed = "١" in text
    term = ["scale", text, ["num", "0"]] if coefficient else ["num", text]
    formula = ["eq", term, ["num", "0"]]
    expected = ResourceLimit if limited else SyntaxError if malformed else None

    if route in ("order", "countermodel"):
        raw = fol(("order@0", "relational-fol@0"))
        if expected:
            with pytest.raises(expected):
                document_from_data(Environment(raw), [formula])
        else:
            document_from_data(Environment(raw), [formula])
        case = {"id": "numeral", "environment": raw, "model": model(["a"], p=[])}
        if route == "order":
            case["ast"] = [formula]
            lean_case = {**case, "kind": "evaluate"}
        else:
            case.update(premises=[formula], conclusion=["bottom"])
            lean_case = {**case, "kind": "countermodel"}
            case["kind"] = "countermodel"
        [lean_result] = lean_route([lean_case])
        [rust_result] = rust_route([case])
    else:
        if malformed and not limited:
            expected = VEError  # W6 uses Lean's canonical InvalidInput code.
        raw = raw_environment({})
        tagged = ["scale", text, ["num", "0"]] if coefficient else ["num", text]
        payload = quantity(["eq", tagged, ["num", "0"]])
        env = Environment(raw)
        if expected:
            with pytest.raises(expected) as raised:
                elaborate_quantity(env, payload)
            assert raised.value.code == ("ResourceLimit" if limited else "InvalidInput")
        else:
            elaborate_quantity(env, payload)
        case = {"id": "numeral", "environment": raw}
        if route == "quantity":
            case["quantity"] = payload
            lean_case = case
        else:
            case.update(premises=[payload], conclusion=quantity(["bottom"]),
                        model={"complete": True, "domains": {}, "constants": {}, "relations": {}})
            if expected:
                with pytest.raises(expected):
                    quantity_countermodel(env, case["premises"], case["conclusion"], case["model"])
            lean_case = {**case, "kind": "countermodel"}
        [lean_result] = lean_quantity([lean_case])
        rust_result = None

    if expected:
        assert lean_result["status"] == "error", lean_result
        assert ("ResourceLimit" in lean_result["error"]) == limited, lean_result
        if rust_result is not None:
            code = "ResourceLimit" if limited else "SyntaxError"
            assert rust_result["status"] == "error" and rust_result["error"]["code"] == code, rust_result
    else:
        assert lean_result["status"] == "ok", lean_result
        assert rust_result is None or rust_result["status"] == "ok", rust_result
