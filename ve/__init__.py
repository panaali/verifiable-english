"""VE v0 experimental language, finite semantics and checked argument API.

The public names resolve lazily (PEP 562): `import ve` loads no submodule, and the first use of a name imports
the module that defines it, so `import ve` does not load the English parser. `_EXPORTS` is the one table of
public names; `tools/layer_policy.py` (`python_exports`) reads it for the layer check and test selection.
"""
import importlib
import importlib.util
import sys
import types

__version__ = "0.1.0"

# The module that defines each public name, in the order the names were documented.
_EXPORTS = {
    "ast": ("And", "Binary", "Bottom", "Const", "Document", "Eq", "Exists", "Forall", "Formula", "Implies", "Not",
            "Or", "Term", "Top", "Unary", "Var", "Reach", "Named", "Body", "Edge", "check_document",
            "check_formula", "doc_from_json", "document_from_data", "document_to_data", "formula_from_data",
            "formula_to_data"),
    "environment": ("Environment",),
    "errors": ("VEError",),
    "identity": ("meaning_id", "source_id"),
    "parser": ("canonicalize", "is_canonical", "parse", "parse_with_metadata"),
    "printer": ("lint_vocabulary", "measure_view_lengths", "natural_document", "natural_formula", "print_document",
                "print_formula", "render", "render_vocabulary"),
    "fol": ("document_from_named_fol", "document_to_named_fol", "render_fol"),
    "model": ("FiniteModel",),
    "evaluate": ("evaluate",),
    "search": ("check_countermodel", "find_countermodel", "find_distinguishing_model"),
    "check": ("check",),
    "entailment": ("EntailmentResult", "EntailmentCertificateCheck", "prove_entailment",
                   "check_entailment_certificate"),
    "closure": ("InductionInvariant",),
    "argument": ("Claim", "Deduction", "Evidence", "ArgumentGraph", "ArgumentResult", "check_argument",
                 "deduction_identity", "outstanding_obligations", "predicate_use_panel"),
    "equivalence": ("Budgets", "ComparisonResult", "DirectionResult", "ReferenceValidation", "EQUIVALENT",
                    "DIFFERENT", "UNKNOWN", "compare", "is_weaker", "is_stronger", "in_two_variable_fragment",
                    "validate_reference"),
    "english": ("parse_english", "parse_english_argument", "parse_english_with_metadata", "lint_english_vocabulary"),
    "english_vocabulary": ("suggest_vocabulary",),
}
_MODULE = {name: module for module, names in _EXPORTS.items() for name in names}
__all__ = list(_MODULE)


def __getattr__(name: str):
    """A public name, imported from its module on first use; any other submodule, as an attribute."""
    if name in _MODULE:
        value = getattr(importlib.import_module(f".{_MODULE[name]}", __name__), name)
        if name not in _SHADOWED:
            globals()[name] = value
        return value
    if not name.startswith("__") and importlib.util.find_spec(f"{__name__}.{name}") is not None:
        return importlib.import_module(f".{name}", __name__)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted({*globals(), *__all__})


class _Package(types.ModuleType):
    """`ve.check` and `ve.evaluate` are the functions, never their modules (which share their names).

    Importing a submodule binds it on its package; the eager imports this file used to make rebound the two
    names to the functions afterwards. Here a property keeps them: it ignores the import system binding the
    module, and keeps any other value set (a test's monkeypatch) until it is set back.
    """


_SHADOWED = frozenset(name for name in _MODULE if name == _MODULE[name])
_SET: dict[str, object] = {}


def _shadowed(name: str) -> property:
    def get(package):
        return _SET[name] if name in _SET else __getattr__(name)

    def put(package, value):
        if value is not sys.modules.get(f"{__name__}.{name}"):
            _SET[name] = value

    def delete(package):
        _SET.pop(name, None)
    return property(get, put, delete)


for _name in _SHADOWED:
    setattr(_Package, _name, _shadowed(_name))
del _name
sys.modules[__name__].__class__ = _Package
