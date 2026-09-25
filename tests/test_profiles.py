from copy import deepcopy

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
