"""W1 statement surface declarations.

Norm blocks are document units, parsed by :mod:`ve.norm_english`.  The shared
formula parser continues to handle formulas only; these records reserve the
statement-initial productions and expose their profile and wire names.
"""
from .registry import SurfaceRecord, register

register(SurfaceRecord("norm", "rule", ("Rule ",), "rule",
                       "numbered norm block | precedence sentence", profiles=("norms@0",)))
register(SurfaceRecord("norm-default", "default", ("By default, ",), "default",
                       "regulated completion declaration", profiles=("norms@0",)))
register(SurfaceRecord("norm-deontic", "deontic", (), "may | must",
                       "declared act-phrase atom", profiles=("norms@0",)))
register(SurfaceRecord("norm-unspecified", "unspecified", ("When nothing else in the text decides, ",),
                       "unspecified", "unspecified completion declaration (norm-defaults 4.1)",
                       profiles=("norm-defaults@0", "norms@0")))
