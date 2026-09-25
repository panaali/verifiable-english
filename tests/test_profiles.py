import pytest

from conformance.p0 import environment
from ve.environment import Environment
from ve.errors import UnsupportedProfile
from ve.profiles import checker_family


def test_route_families_and_identity():
    cases = {("relational-fol@0",): "fol",
             ("closure@0", "relational-fol@0"): "closure",
             ("closure@0", "nary@0", "relational-fol@0"): "closure+n-ary",
             ("order@0", "relational-fol@0"): "order"}
    for profiles, family in cases.items():
        raw = environment(); raw["profiles"] = list(profiles)
        env = Environment(raw)
        assert checker_family(raw["profiles"]) == family
        assert env.identity_version == "v0.2:" + ",".join(profiles)
        assert env.to_dict() == raw


def test_string_literals_are_equality_only_and_bounded():
    from ve.ast import Forall, Top, check_formula
    raw = environment()
    env = Environment(raw)
    assert env.constants["alpha"].description is None
    assert env.to_dict() == raw
    with pytest.raises(Exception, match="Unknown binder sort"):
        check_formula(env, Forall("$string", Top()))
    raw["vocabulary"]["predicates"]["named"] = {
        "arguments": ["$string"], "description": "Not in stage one."}
    with pytest.raises(Exception, match="Undeclared predicate argument sort"):
        Environment(raw)
    raw = environment()
    raw["vocabulary"]["constants"] = {
        f"literal{i}": {"sort": "$string"} for i in range(65)}
    with pytest.raises(Exception, match="64"):
        Environment(raw)


@pytest.mark.parametrize("profiles,fragment", [
    (["relational-fol@0", "closure@0"], "sorted"),
    (["relational-fol@0", "relational-fol@0"], "unique"),
    (["mystery@0", "relational-fol@0"], "mystery@0"),
    (["nary@0", "order@0", "relational-fol@0"], "nary@0 x order@0"),
    (["closure@0", "order@0", "relational-fol@0"], "closure@0 x order@0"),
])
def test_route_rejects_bad_profiles(profiles, fragment):
    raw = environment(); raw["profiles"] = profiles
    with pytest.raises(UnsupportedProfile, match=fragment):
        Environment(raw)
