"""Alternatives statement vocabulary, scoped to alternatives@0.

These records describe the fixed profile words. Their wire atoms are decoded
only by the trusted alternatives route; Python does not elaborate them.
"""
from .registry import SurfaceRecord, register


for word, strict, english, production in (
    ("avoidable", "avoidable_by", "is avoidable by", "harm avoidable by chooser"),
    ("unavoidable", "unavoidable_by", "is unavoidable by", "harm unavoidable by chooser"),
    ("allows", "allows", "allows harm to happen", "action allows harm to happen"),
    ("prevents", "prevents", "prevents", "action prevents harm"),
):
    register(SurfaceRecord(f"alternatives-{word}", strict, (), english, production,
                           profiles=("alternatives@0",)))

for name, production in (
    ("every-available", "every action available to chooser"),
    ("every-other-available", "every other action available to chooser"),
    ("another-available", "another action available to chooser"),
):
    register(SurfaceRecord(f"alternatives-{name}", name, (), production, production,
                           profiles=("alternatives@0",)))
