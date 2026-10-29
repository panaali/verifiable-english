"""Profile data for display and model projection: the rows are Lean's (`ve/profile_table.json`)."""
from dataclasses import dataclass
import json
from pathlib import Path

from .errors import UnsupportedProfile

LANGUAGE = "ve.core@0.2"
SPEC_REVISION = "ve-v0.2-expand2-2026-09-25"
BASE = "relational-fol@0"

# Generated from `VE.Compose.profileTable` by tools/profile_table.py: Lean owns every row and the gate that reads
# them (`VE.Compose.gateOf`); Python reads the profiles an environment lists and their rows, and decides nothing.
_TABLE = json.loads((Path(__file__).with_name("profile_table.json")).read_text())
ROWS = tuple(_TABLE["rows"])
BY_NAME = {name: tuple(row for row in ROWS if row["profile"] == name) for name in _TABLE["environment"]}


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
# One row per profile an environment lists (tests/test_model_environment.py checks the keys
# against BY_NAME): the model environment Rust's search and countermodel cases
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
