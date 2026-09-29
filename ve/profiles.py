"""Ordered statement-layer profiles and checker-family dispatch for core@0.2."""
from dataclasses import dataclass

from .errors import UnsupportedProfile

LANGUAGE = "ve.core@0.2"
SPEC_REVISION = "ve-v0.2-expand2-2026-09-25"
BASE = "relational-fol@0"


@dataclass(frozen=True, slots=True)
class ProfileRecord:
    name: str
    generator: str
    layer: str
    checker_family: str


REGISTRY = (
    ProfileRecord("alternatives@0", "alternatives", "statement", "inherited"),
    ProfileRecord("closure@0", "", "checker", "closure"),
    ProfileRecord("data@0", "data", "statement", "inherited"),
    ProfileRecord("definitions@0", "definitions", "statement", "inherited"),
    ProfileRecord("documents@1", "documents", "statement", "inherited"),
    ProfileRecord("nary@0", "", "checker", "closure+n-ary"),
    ProfileRecord("norms@0", "norms", "statement", "inherited"),
    ProfileRecord("soft-norms@0", "soft", "statement", "inherited"),
    ProfileRecord("order@0", "", "checker", "order"),
    ProfileRecord(BASE, "", "checker", "fol"),
    ProfileRecord("reports@0", "reports", "statement", "inherited"),
    ProfileRecord("rights@0", "rights", "statement", "inherited"),
    ProfileRecord("time@0", "time", "statement", "inherited"),
)
BY_NAME = {record.name: record for record in REGISTRY}


def checker_family(profiles):
    """Validate the exact sorted set and return its supported checker family."""
    if type(profiles) is not list or any(type(p) is not str for p in profiles):
        raise UnsupportedProfile("profiles must be a sorted unique array")
    if profiles != sorted(set(profiles)):
        raise UnsupportedProfile("profiles must be sorted and unique")
    if "alternatives@0" in profiles:
        if "norms@0" not in profiles:
            raise UnsupportedProfile("alternatives@0 requires norms@0")
        if "soft-norms@0" in profiles:
            raise UnsupportedProfile("alternatives@0 with soft-norms@0")
    for profile in profiles:
        if profile not in BY_NAME:
            raise UnsupportedProfile(f"Unsupported profile {profile}")
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
    if "rights@0" in profiles and "soft-norms@0" not in profiles:
        raise UnsupportedProfile("rights@0 requires soft-norms@0")
    if "soft-norms@0" in profiles and "norms@0" not in profiles:
        raise UnsupportedProfile("soft-norms@0 requires norms@0")
    return ("order" if "order@0" in checker else
            "closure+n-ary" if "nary@0" in checker else
            "closure" if "closure@0" in checker else "fol")


# No allowed checker family remains gated after W4 stage 1.
GATED = {}


def require_checker(env) -> None:
    """Raise UnsupportedProfile if env's checker family is gated."""
    if getattr(env, "language", None) != LANGUAGE:
        return
    message = GATED.get(checker_family(list(env.profiles)))
    if message is not None:
        raise UnsupportedProfile(message)
