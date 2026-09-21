"""Semantic templates: careful requirement prose + the faithful v0 AST (wire format).

Every template states its requirement so that one reading is intended, including who may differ
("possibly a different one for each"), what happens in empty cases, and the scope of exceptions.
The AST is the ground truth by construction. Templates are split between dev and scored.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .vocab import Binding


# ---- named-variable builder -> indexed wire AST
def fa(v, sort, body): return ("forall", v, sort, body)
def ex(v, sort, body): return ("exists", v, sort, body)
def u(pred, v): return ("unary", pred.id, v)
def b(pred, v, w): return ("binary", pred.id, v, w)
def eq(v, w): return ("eq", v, w)
def no(x): return ("not", x)
def et(x, y): return ("and", x, y)
def vel(x, y): return ("or", x, y)
def imp(x, y): return ("implies", x, y)


def to_wire(f, scope: tuple[str, ...] = ()) -> list:
    tag = f[0]
    var = lambda name: ["var", scope.index(name)]  # noqa: E731
    if tag in ("forall", "exists"):
        return [tag, f[2], to_wire(f[3], (f[1], *scope))]
    if tag == "unary":
        return ["unary", f[1], var(f[2])]
    if tag == "binary":
        return ["binary", f[1], var(f[2]), var(f[3])]
    if tag == "eq":
        return ["eq", var(f[1]), var(f[2])]
    if tag == "not":
        return ["not", to_wire(f[1], scope)]
    return [tag, to_wire(f[1], scope), to_wire(f[2], scope)]


def an(noun: str) -> str:
    return ("an " if noun[0] in "aeiou" else "a ") + noun


@dataclass(frozen=True)
class Template:
    id: str
    covers: tuple[str, ...]  # phenomena: alternation, exception, existence, argument_order, vacuity
    prose: Callable[[Binding], str]
    formula: Callable[[Binding], tuple]


def _t(id, covers, prose, formula):
    return Template(id, tuple(covers), prose, formula)


TEMPLATES: list[Template] = [
    _t("t01_each_has_some", ["alternation"],
       lambda v: f"For every {v.A[0]} that {v.P.pos}, at least one {v.B[0]} {v.R.pos} that {v.A[0]}. "
                 f"Different {v.A[0]}s may be covered by different {v.B[0]}s.",
       lambda v: fa("a", v.A[0], imp(u(v.P, "a"), ex("b", v.B[0], b(v.R, "b", "a"))))),
    _t("t02_one_for_all", ["alternation"],
       lambda v: f"There is at least one {v.B[0]} who, alone, {v.R.pos} every {v.A[0]} that {v.P.pos}: "
                 f"the same {v.B[0]} must cover all of them.",
       lambda v: ex("b", v.B[0], fa("a", v.A[0], imp(u(v.P, "a"), b(v.R, "b", "a"))))),
    _t("t03_exception_both", ["exception"],
       lambda v: f"Every {v.A[0]} that {v.P.pos} {v.Q.pos}. There is exactly one exemption: {an(v.A[0])} that "
                 f"{v.X.pos} and also {v.Y.pos} need not satisfy this. {an(v.A[0]).capitalize()} that meets only one of "
                 f"those two conditions is not exempt.",
       lambda v: fa("a", v.A[0], imp(et(u(v.P, "a"), no(et(u(v.X, "a"), u(v.Y, "a")))), u(v.Q, "a")))),
    _t("t04_some_and_all", ["existence", "vacuity"],
       lambda v: f"At least one {v.A[0]} {v.P.pos}, and every {v.A[0]} that {v.P.pos} {v.Q.pos}. "
                 f"The requirement is not met if no {v.A[0]} {v.P.pos}.",
       lambda v: et(ex("a", v.A[0], u(v.P, "a")), fa("a", v.A[0], imp(u(v.P, "a"), u(v.Q, "a"))))),
    _t("t05_targets_only", ["argument_order"],
       lambda v: f"Whenever {an(v.A[0])} that {v.P.pos} {v.T.pos} some {v.A[0]}, the {v.A[0]} on the receiving end "
                 f"{v.Q.pos}. Nothing is required of {an(v.A[0])} that {v.T.pos} {an(v.A[0])} that {v.P.pos}.",
       lambda v: fa("x", v.A[0], imp(u(v.P, "x"), fa("y", v.A[0], imp(b(v.T, "x", "y"), u(v.Q, "y")))))),
    _t("t06_at_most_one", ["argument_order", "equality"],
       lambda v: f"No {v.B[0]} {v.R.pos} two different {v.A[0]}s. "
                 f"(Several {v.B[0]}s may still share the same {v.A[0]}.)",
       lambda v: fa("b", v.B[0], fa("a1", v.A[0], fa("a2", v.A[0],
                    imp(et(b(v.R, "b", "a1"), b(v.R, "b", "a2")), eq("a1", "a2")))))),
    _t("t07_both_required", ["conjunction"],
       lambda v: f"Every {v.A[0]} that {v.P.pos} {v.Q.pos}. In addition, every {v.A[0]} that {v.P.pos} {v.Y.pos}. "
                 f"Meeting one of the two is not enough.",
       lambda v: fa("a", v.A[0], imp(u(v.P, "a"), et(u(v.Q, "a"), u(v.Y, "a"))))),
    _t("t08_only_if", ["direction"],
       lambda v: f"{an(v.A[0]).capitalize()} {v.P.pos} only if it {v.Q.pos}. "
                 f"The requirement does not say that every {v.A[0]} that {v.Q.pos} {v.P.pos}.",
       lambda v: fa("a", v.A[0], imp(u(v.P, "a"), u(v.Q, "a")))),
    _t("t09_each_has_some_unless", ["alternation", "exception"],
       lambda v: f"For every {v.A[0]} that {v.P.pos}, at least one {v.B[0]} {v.R.pos} it, unless the {v.A[0]} "
                 f"{v.X.pos}. Different {v.A[0]}s may be covered by different {v.B[0]}s, and nothing is required for "
                 f"{an(v.A[0])} that {v.X.pos}.",
       lambda v: fa("a", v.A[0], imp(et(u(v.P, "a"), no(u(v.X, "a"))), ex("b", v.B[0], b(v.R, "b", "a"))))),
    _t("t10_none_related", ["negation"],
       lambda v: f"No {v.B[0]} that {v.S.pos} {v.R.pos} any {v.A[0]} that {v.P.pos}. "
                 f"{an(v.B[0]).capitalize()} that {v.S.neg} is not restricted.",
       lambda v: fa("b", v.B[0], imp(u(v.S, "b"), fa("a", v.A[0], imp(u(v.P, "a"), no(b(v.R, "b", "a"))))))),
    _t("t11_some_qualified_pair", ["existence", "vacuity"],
       lambda v: f"At least one {v.B[0]} that {v.S.pos} {v.R.pos} at least one {v.A[0]} that {v.P.pos}. "
                 f"Such {an(v.B[0])} and such {an(v.A[0])} must actually exist.",
       lambda v: ex("b", v.B[0], et(u(v.S, "b"), ex("a", v.A[0], et(u(v.P, "a"), b(v.R, "b", "a")))))),
    _t("t12_either_condition", ["disjunction"],
       lambda v: f"Every {v.A[0]} that {v.P.pos} {v.Q.pos}. Likewise, every {v.A[0]} that {v.X.pos} {v.Q.pos}. "
                 f"Either condition alone is enough to trigger the obligation.",
       lambda v: fa("a", v.A[0], imp(vel(u(v.P, "a"), u(v.X, "a")), u(v.Q, "a")))),
    _t("t13_inherits_backwards", ["argument_order"],
       lambda v: f"If {an(v.A[0])} {v.T.pos} {an(v.A[0])} that {v.P.pos}, then the first {v.A[0]} (the one that "
                 f"{v.T.pos} the other) {v.P.pos} as well.",
       lambda v: fa("x", v.A[0], fa("y", v.A[0], imp(et(b(v.T, "x", "y"), u(v.P, "y")), u(v.P, "x"))))),
    _t("t14_each_has_qualified", ["alternation", "vacuity"],
       lambda v: f"For every {v.A[0]} that {v.P.pos}, at least one {v.B[0]} that {v.S.pos} {v.R.pos} that {v.A[0]}. "
                 f"{an(v.B[0]).capitalize()} that {v.S.neg} does not count, and different {v.A[0]}s may be covered by different "
                 f"{v.B[0]}s.",
       lambda v: fa("a", v.A[0], imp(u(v.P, "a"), ex("b", v.B[0], et(u(v.S, "b"), b(v.R, "b", "a")))))),
    _t("t15_hub", ["alternation", "argument_order", "existence"],
       lambda v: f"At least one {v.A[0]} that {v.P.pos} {v.T.pos} every {v.A[0]} that {v.X.pos}: one and the same "
                 f"{v.A[0]} must do so for all of them.",
       lambda v: ex("x", v.A[0], et(u(v.P, "x"), fa("y", v.A[0], imp(u(v.X, "y"), b(v.T, "x", "y")))))),
    _t("t16_exception_with_relation", ["exception", "alternation"],
       lambda v: f"Every {v.A[0]} that {v.P.pos} {v.Q.pos}. The only exemption is for {an(v.A[0])} that {v.X.pos} "
                 f"and that at least one {v.B[0]} that {v.S.pos} {v.R.pos}; both parts are needed for the exemption.",
       lambda v: fa("a", v.A[0], imp(et(u(v.P, "a"), no(et(u(v.X, "a"), ex("b", v.B[0], et(u(v.S, "b"), b(v.R, "b", "a")))))),
                                  u(v.Q, "a")))),
]  # fmt: skip


DEV_TEMPLATES = ("t03_exception_both", "t04_some_and_all", "t13_inherits_backwards", "t14_each_has_qualified")
SCORED_TEMPLATES = tuple(t.id for t in TEMPLATES if t.id not in DEV_TEMPLATES)
BY_ID = {t.id: t for t in TEMPLATES}
