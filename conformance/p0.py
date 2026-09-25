"""P0 route fixtures shared by Python, Rust and the new Lean route."""
from __future__ import annotations

from copy import deepcopy

from ve.profiles import LANGUAGE, SPEC_REVISION


def environment():
    return {"language": LANGUAGE, "profiles": ["relational-fol@0"],
            "spec_revision": SPEC_REVISION,
            "vocabulary": {"sorts": {}, "predicates": {}, "constants": {
                "alpha": {"sort": "$string"},
                "beta": {"sort": "$string"}}}}


def elaborated_document_cases():
    env = environment()
    model = {"complete": True, "domains": {"$string": ["a", "b"]},
             "constants": {"alpha": "a", "beta": "b"}, "relations": {}}
    cases = [{"id": "literals-distinct", "environment": env, "model": model,
              "ast": [["not", ["eq", ["const", "alpha"], ["const", "beta"]]]],
              "expected": [True]},
             {"id": "literals-equal-false", "environment": env, "model": model,
              "ast": [["eq", ["const", "alpha"], ["const", "beta"]]],
              "expected": [False]},
             {"id": "literals-countermodel", "environment": env, "model": model,
              "premises": [], "conclusion": ["eq", ["const", "alpha"], ["const", "beta"]],
              "expected_refutes": True},
             {"id": "literals-search", "environment": env, "max_domain_size": 2,
              "premises": [], "conclusion": ["eq", ["const", "alpha"], ["const", "beta"]],
              "expected_status": "Found"}]
    order_env = deepcopy(env)
    order_env["profiles"] = ["order@0", "relational-fol@0"]
    cases.append({"id": "order-with-literals", "environment": order_env, "model": model,
                  "ast": [["not", ["eq", ["const", "alpha"], ["const", "beta"]]]],
                  "expected": [True]})
    for ident, profiles in (("unknown-profile", ["mystery@0", "relational-fol@0"]),
                            ("order-nary", ["nary@0", "order@0", "relational-fol@0"]),
                            ("closure-order", ["closure@0", "order@0", "relational-fol@0"])):
        bad = deepcopy(env)
        bad["profiles"] = profiles
        cases.append({"id": ident, "environment": bad, "ast": [["top"]],
                      "expected_error": "UnsupportedProfile"})
    return cases


def invalid_background_model_cases():
    env = environment()
    flags = deepcopy(env)
    flags["profiles"] = ["data@0", "relational-fol@0"]
    flags["vocabulary"] = {"sorts": {"person": {"description": "Person."},
                                      "department": {"description": "Department."}},
                            "predicates": {"dept": {"arguments": ["person", "department"],
                                                    "description": "Department of person.",
                                                    "functional": True, "total": True}},
                            "constants": {}}
    defined = deepcopy(env)
    defined["profiles"] = ["definitions@0", "relational-fol@0"]
    defined["vocabulary"] = {"sorts": {"person": {"description": "Person."}},
                             "predicates": {"base": {"arguments": ["person"], "description": "Base."},
                                            "derived": {"arguments": ["person"],
                                                        "description": "Defined from base.",
                                                        "defined": {"arguments": ["person"],
                                                                    "body": ["unary", "base", ["var", 0]]}}},
                             "constants": {}}
    return [{"id": "literal-alias", "environment": env,
             "model": {"complete": True, "domains": {"$string": ["a"]},
                       "constants": {"alpha": "a", "beta": "a"}, "relations": {}},
             "ast": [["top"]], "expected_error": "InvalidModel",
             "generator": "literals"},
            {"id": "partial-total-table", "pending": "W5", "environment": flags,
             "model": {"complete": True, "domains": {"person": ["alice"],
                        "department": ["finance"]}, "constants": {}, "relations": {"dept": []}},
             "ast": [["top"]], "expected_error": "InvalidModel", "generator": "flags"},
            {"id": "supplied-defined-table", "pending": "W3", "environment": defined,
             "model": {"complete": True, "domains": {"person": ["alice"]},
                       "constants": {}, "relations": {"base": [["alice"]],
                                                     "derived": [["alice"]]}},
             "ast": [["top"]], "expected_error": "InvalidModel", "generator": "definitions"}]
