"""Registry of VE surface constructs."""

# ve.ast registers the n-ary forms (ve.surface.nary) when it loads; it loads first, as `import ve` once made it.
from .. import ast  # noqa: F401
from . import alternatives  # noqa: F401 -- register profile-scoped wordings
from . import risk  # noqa: F401 -- register risk profile wordings
