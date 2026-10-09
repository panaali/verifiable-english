"""Frozen pre-batch Python profile gate for regression comparisons only."""
from ve.profiles import BY_NAME, BASE
from ve.errors import UnsupportedProfile

def checker_family(profiles):
    """Validate the exact sorted set and return its supported checker family."""
    if type(profiles) is not list or any(type(p) is not str for p in profiles):
        raise UnsupportedProfile("profiles must be a sorted unique array")
    if profiles != sorted(set(profiles)):
        raise UnsupportedProfile("profiles must be sorted and unique")
    if "readings@1" in profiles:
        base = [profile for profile in profiles if profile != "readings@1"]
        family = checker_family(base)
        if "norms@0" not in base:
            raise UnsupportedProfile("UnsupportedProfile: readings@1 requires norms@0")
        for outside in ("risk@0", "alternatives@0", "speech-acts@0", "reports@0"):
            if outside in base:
                raise UnsupportedProfile(f"UnsupportedProfile: readings@1 with {outside}")
        return family
    if "alternatives@0" in profiles:
        if "norms@0" not in profiles:
            raise UnsupportedProfile("alternatives@0 requires norms@0")
        if "soft-norms@0" in profiles:
            raise UnsupportedProfile("alternatives@0 with soft-norms@0")
    if "risk@0" in profiles and "alternatives@0" not in profiles:
        raise UnsupportedProfile("risk@0 requires alternatives@0")
    if "risk@0" in profiles and "norm-defaults@0" in profiles:
        raise UnsupportedProfile("risk@0 with norm-defaults@0 is not implemented")
    if "alternatives@0" in profiles and "norm-defaults@0" in profiles:
        raise UnsupportedProfile("alternatives@0 with norm-defaults@0 is not implemented")
    for profile in profiles:
        if profile not in BY_NAME:
            raise UnsupportedProfile(f"Unsupported profile {profile}")
    if "speech-acts@0" in profiles:
        if "norms@0" not in profiles:
            raise UnsupportedProfile("UnsupportedProfile: speech-acts@0 requires norms@0")
        for profile in profiles:
            if profile not in {BASE, "norms@0", "speech-acts@0"}:
                raise UnsupportedProfile(f"UnsupportedProfile: speech-acts@0 with {profile}")
    if BASE not in profiles:
        raise UnsupportedProfile(f"Missing profile {BASE}")
    if "reports@0" in profiles:
        for other in ("norms@0", "definitions@0", "data@0"):
            if other in profiles:
                raise UnsupportedProfile(f"reports@0 with {other} layers")
        for other in ("closure@0", "nary@0", "order@0"):
            if other in profiles:
                raise UnsupportedProfile(f"reports@0 requires the fol checker, not {other}")
    checker = [p for p in profiles if p in {"closure@0", "nary@0", "order@0"}]
    if "order@0" in checker and len(checker) > 1:
        pair = next(p for p in checker if p != "order@0")
        raise UnsupportedProfile(f"Unsupported profile combination {pair} x order@0")
    if "nary@0" in checker and "closure@0" not in checker:
        # Stage 1 requires the closure+n-ary Core family.
        raise UnsupportedProfile("Unsupported profile nary@0 without closure@0")
    if "risk@0" in profiles and checker:
        raise UnsupportedProfile("the risk norms route admits FOL documents only")
    if "rights@0" in profiles and "soft-norms@0" not in profiles:
        raise UnsupportedProfile("rights@0 requires soft-norms@0")
    if "soft-norms@0" in profiles and "norms@0" not in profiles:
        raise UnsupportedProfile("soft-norms@0 requires norms@0")
    if "norm-defaults@0" in profiles and "norms@0" not in profiles:
        raise UnsupportedProfile("norm-defaults@0 requires norms@0")
    return ("order" if "order@0" in checker else
            "closure+n-ary" if "nary@0" in checker else
            "closure" if "closure@0" in checker else "fol")
