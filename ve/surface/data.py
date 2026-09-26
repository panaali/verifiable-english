"""Checked data sugar; both forms elaborate to ordinary binary atoms."""

from ..ast import Binary, Term, check_formula
from ..errors import TypeMismatch, UnsupportedProfile


def attribute_equals(env, predicate: str, source: Term, value: Term) -> Binary:
    """The value of a total functional attribute of `source` is `value`."""
    if "data@0" not in env.profiles:
        raise UnsupportedProfile("Attribute descriptions require data@0")
    declaration = env.predicates.get(predicate)
    if declaration is None or not (declaration.functional and declaration.total):
        raise TypeMismatch("A definite attribute needs both functional and total declarations")
    return check_formula(env, Binary(predicate, source, value))


def member_of(env, element: Term, collection: Term, *, predicate: str = "member") -> Binary:
    """Set membership is the declared `member(element, collection)` relation."""
    if "data@0" not in env.profiles:
        raise UnsupportedProfile("Set membership descriptions require data@0")
    declaration = env.predicates.get(predicate)
    if declaration is None or len(declaration.arguments) != 2:
        raise TypeMismatch("A set membership relation must be declared as binary")
    return check_formula(env, Binary(predicate, element, collection))
