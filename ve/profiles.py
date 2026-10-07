"""Profile metadata for display and generator registration."""
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
