"""Checked data sugar; both forms elaborate to ordinary binary atoms."""

from ..ast import And, Binary, Const, Exists, Unary, Var, Term, check_formula
from ..errors import TypeMismatch, UnsupportedProfile


def attribute_equals(env, predicate: str, source: Term, value: Term) -> Binary:
    """The value of a total functional attribute of `source` is `value`."""
    if "data@0" not in env.profiles:
        raise UnsupportedProfile("Attribute descriptions require data@0")
    declaration = env.predicates.get(predicate)
    if declaration is None or not (declaration.functional and declaration.total):
        raise TypeMismatch("A definite attribute needs both functional and total declarations")
    return check_formula(env, Binary(predicate, source, value))


def attribute_property(env, predicate: str, source: Term, property_predicate: str) -> Exists:
    """Elaborate `the r of t is P` to an explicit unique-value witness."""
    if "data@0" not in env.profiles:
        raise UnsupportedProfile("Attribute descriptions require data@0")
    declaration = env.predicates.get(predicate)
    if declaration is None or not (declaration.functional and declaration.total):
        raise TypeMismatch("A definite attribute needs both functional and total declarations")
    if declaration.arguments[1] == "$string":
        raise UnsupportedProfile("String-valued attribute properties require data stage 2")
    prop = env.predicates.get(property_predicate)
    if prop is None or prop.arguments != (declaration.arguments[1],):
        raise TypeMismatch("Attribute property must be unary on the target sort")
    lifted = Var(source.index + 1) if type(source) is Var else source
    if type(lifted) is not Const and type(lifted) is not Var:
        raise TypeMismatch("Attribute source must be a constant or bound variable")
    return check_formula(env, Exists(declaration.arguments[1], And(
        Binary(predicate, lifted, Var(0)), Unary(property_predicate, Var(0)))))


def member_of(env, element: Term, collection: Term, *, predicate: str = "member") -> Binary:
    """Set membership is the declared `member(element, collection)` relation."""
    if "data@0" not in env.profiles:
        raise UnsupportedProfile("Set membership descriptions require data@0")
    declaration = env.predicates.get(predicate)
    if declaration is None or len(declaration.arguments) != 2:
        raise TypeMismatch("A set membership relation must be declared as binary")
    return check_formula(env, Binary(predicate, element, collection))
