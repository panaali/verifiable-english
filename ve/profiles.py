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
    ProfileRecord("norm-defaults@0", "norm-defaults", "statement", "inherited"),
    ProfileRecord("norms@0", "norms", "statement", "inherited"),
    ProfileRecord("soft-norms@0", "soft", "statement", "inherited"),
    ProfileRecord("order@0", "", "checker", "order"),
    ProfileRecord("readings@1", "readings", "statement", "inherited"),
    ProfileRecord(BASE, "", "checker", "fol"),
    ProfileRecord("speech-acts@0", "speech-acts", "statement", "inherited"),
    ProfileRecord("reports@0", "reports", "statement", "inherited"),
    ProfileRecord("risk@0", "risk", "statement", "inherited"),
    ProfileRecord("rights@0", "rights", "statement", "inherited"),
    ProfileRecord("time@0", "time", "statement", "inherited"),
)
BY_NAME = {record.name: record for record in REGISTRY}



# Statement layers whose own Lean routes check them. They declare no vocabulary
# and constrain no model; Lean's standalone, readings and graph modes refuse
# them, and route and Rust cases carry the environment without their blocks.
STATEMENT_LAYERS = frozenset({"soft-norms@0", "reports@0", "speech-acts@0", "rights@0"})


@dataclass(frozen=True, slots=True)
class ModelReduction:
    """What a profile adds to the environment JSON that no finite model reads.

    `blocks` are top-level blocks, `vocabulary` vocabulary blocks, and the field
    tuples entry fields of every predicate or constant. `unspecified` is the
    regulated default an engine without the profile reads in place of
    `unspecified` (a completion default is read by the norms closure, never by a
    model). `kept`: the engines decode the profile, which a model reads."""
    kept: bool = False
    blocks: tuple[str, ...] = ()
    vocabulary: tuple[str, ...] = ()
    predicate_fields: tuple[str, ...] = ()
    constant_fields: tuple[str, ...] = ()
    unspecified: str | None = None


_KEPT = ModelReduction(kept=True)
# One row per registered profile (tests/test_model_environment.py checks the keys
# against REGISTRY): the model environment Rust's search and countermodel cases
# and Lean's metered evaluator read. Python decodes and validates the whole
# environment first; the engines answer model questions only, over the
# vocabulary a model interprets.
MODEL_REDUCTIONS = {
    "alternatives@0": ModelReduction(blocks=("alternatives",)),
    "closure@0": _KEPT,
    "data@0": _KEPT,
    "definitions@0": _KEPT,
    "documents@1": _KEPT,
    "nary@0": _KEPT,
    "norm-defaults@0": ModelReduction(unspecified="deny"),
    "norms@0": _KEPT,
    "soft-norms@0": ModelReduction(vocabulary=("soft",), predicate_fields=("instruction_of",)),
    "order@0": _KEPT,
    "readings@1": ModelReduction(),
    BASE: _KEPT,
    "speech-acts@0": ModelReduction(blocks=("speech_acts",)),
    "reports@0": ModelReduction(vocabulary=("reports",), constant_fields=("verbalisation",)),
    "risk@0": ModelReduction(blocks=("risk", "unit_schema", "units"), predicate_fields=("argument_units",),
                             constant_fields=("unit",)),
    "rights@0": ModelReduction(vocabulary=("rights",)),
    "time@0": _KEPT,
}
# English display text, in every environment: identity-bound, read by no model.
DISPLAY_FIELDS = {"sorts": ("verbalisation",), "predicates": ("verbalisation", "negative_verbalisation"),
                  "constants": ("verbalisation",)}


def model_environment(data: dict, *, layers=None, display: bool = True) -> dict:
    """The environment JSON of a model case (no environment identity in its
    answer): `data` without display text and without what each profile adds
    that no model reads (MODEL_REDUCTIONS). A profile without a row is refused.

    With `layers`, only those profiles are reduced (the rest are kept as they
    are), and `display=False` keeps the display text: the route projection
    (`lean_runner.route_environment`)."""
    profiles = data.get("profiles")
    if type(profiles) is not list:
        return data  # the frozen ve.core@0 envelope has no layers
    reductions = []
    for profile in profiles:
        if profile not in MODEL_REDUCTIONS:
            raise UnsupportedProfile(f"Unsupported profile {profile}")
        reductions.append(MODEL_REDUCTIONS[profile] if layers is None or profile in layers else _KEPT)
    blocks = {name for r in reductions for name in r.blocks}
    vocabulary_blocks = {name for r in reductions for name in r.vocabulary}
    shown = DISPLAY_FIELDS if display else {}
    fields = {"sorts": set(shown.get("sorts", ())),
              "predicates": {*shown.get("predicates", ()), *(f for r in reductions for f in r.predicate_fields)},
              "constants": {*shown.get("constants", ()), *(f for r in reductions for f in r.constant_fields)}}
    unspecified = next((r.unspecified for r in reductions if r.unspecified is not None), None)

    def entry(table, value):
        if type(value) is not dict:
            return value
        value = {k: v for k, v in value.items() if k not in fields[table]}
        regulated = value.get("regulated")
        if table == "predicates" and unspecified is not None and type(regulated) is dict \
                and regulated.get("default") == "unspecified":
            value["regulated"] = {**regulated, "default": unspecified}
        return value

    vocabulary = {key: ({name: entry(key, value) for name, value in block.items()}
                        if key in fields and type(block) is dict else block)
                  for key, block in data["vocabulary"].items() if key not in vocabulary_blocks}
    return {**{key: value for key, value in data.items() if key not in blocks},
            "profiles": [p for p, r in zip(profiles, reductions) if r.kept], "vocabulary": vocabulary}


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


SPEECH_ROUTE_PROFILES = frozenset({BASE, "norms@0", "speech-acts@0"})


def route_gate(route, profiles):
    """The profile gate a block route reads before the envelope, with its
    diagnostics: VE.SpeechActs.Wire.profileGate ("speech"),
    VE.Alternatives.Wire.profileGate ("alternatives") and
    VE.Risk.Wire.profileGate ("risk"). `checker_family` checks the rest later."""
    if type(profiles) is not list or any(type(p) is not str for p in profiles):
        raise UnsupportedProfile("profiles must be a sorted unique array")
    if profiles != sorted(set(profiles)):
        raise UnsupportedProfile("profiles must be sorted and unique")
    if route == "speech":
        if "speech-acts@0" not in profiles:
            raise UnsupportedProfile("UnsupportedProfile: speech-acts@0 is required")
        if "norms@0" not in profiles:
            raise UnsupportedProfile("UnsupportedProfile: speech-acts@0 requires norms@0")
        for profile in profiles:
            if profile not in SPEECH_ROUTE_PROFILES:
                raise UnsupportedProfile(f"UnsupportedProfile: speech-acts@0 with {profile}")
        return
    if route == "risk":
        if "risk@0" not in profiles:
            raise UnsupportedProfile("risk@0 is required")
        if "alternatives@0" not in profiles:
            raise UnsupportedProfile("risk@0 requires alternatives@0")
    if "alternatives@0" not in profiles:
        raise UnsupportedProfile("alternatives@0 is required")
    if "norms@0" not in profiles:
        raise UnsupportedProfile("alternatives@0 requires norms@0")
    if "soft-norms@0" in profiles:
        raise UnsupportedProfile("alternatives@0 with soft-norms@0")


# No allowed checker family remains gated after W4 stage 1.
GATED = {}


def require_checker(env) -> None:
    """Raise UnsupportedProfile if env's checker family is gated."""
    if getattr(env, "language", None) != LANGUAGE:
        return
    message = GATED.get(checker_family(list(env.profiles)))
    if message is not None:
        raise UnsupportedProfile(message)
