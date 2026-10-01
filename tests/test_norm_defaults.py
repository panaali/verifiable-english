"""norm-defaults@0 fixtures (docs/spec/norm-defaults.md section 9), Python side."""
import copy

import pytest

from ve.ast import And, Const, Eq, Not, Or, Top, Unary, Var, _Checker
from ve.environment import Environment
from ve.errors import InvalidModel, ResourceLimit, UnsupportedProfile, VEError
from ve.norms import Norm, NormDocument, check_conflict as w1_check_conflict
from ve.profiles import LANGUAGE, SPEC_REVISION, checker_family
from ve import norm_defaults as nd

PROFILES = ["norm-defaults@0", "norms@0", "relational-fol@0"]


def raw_environment(predicates, sorts=("act",), constants=None, profiles=PROFILES):
    return {"language": LANGUAGE, "profiles": list(profiles), "spec_revision": SPEC_REVISION,
            "vocabulary": {"sorts": {s: {"description": s} for s in sorts},
                           "predicates": predicates, "constants": constants or {}}}


def environment(predicates, **kwargs):
    return Environment(raw_environment(predicates, **kwargs))


def permission(default, *, act="{0} be done", args=("act",)):
    return {"arguments": list(args), "description": "permission",
            "regulated": {"role": "permission", "default": default, "act": act}}


def obligation(default, dual="x_permitted", *, act="{0} be done", args=("act",)):
    reg = {"role": "obligation", "default": default, "act": act}
    if dual is not None:
        reg["permission"] = dual
    return {"arguments": list(args), "description": "obligation", "regulated": reg}


def rule(name, predicate, sign, guard=None, *, unless=(), over=()):
    return Norm(name, predicate, sign, Top() if guard is None else guard, tuple(unless), tuple(over))


ONE_ACT = {"complete": True, "domains": {"act": ["a"]}, "constants": {}, "relations": {}}


def status_of(doc, predicate, row, situation=ONE_ACT, **options):
    return doc.status(doc.situation(situation), predicate, row, **options)


# u1: u0165.s07, audited shape.

def csam(default):
    raw = raw_environment(
        {"csam_generation_permitted": permission(default, act="{0} generate child sexual abuse material",
                                                 args=("agent",))},
        sorts=("agent",), constants={"claude": {"sort": "agent", "description": "Claude",
                                                "verbalisation": "Claude"},
                                     "sol": {"sort": "agent", "description": "Sol", "verbalisation": "Sol"}})
    # "entity" is a reserved word of the English vocabulary; the audited sort was `entity`.
    raw["vocabulary"]["sorts"]["agent"]["verbalisation"] = {"singular": "agent", "plural": "agents"}
    return Environment(raw)


CSAM_RULE = rule("no-csam-generation", "csam_generation_permitted", False, Eq(Var(0), Const("claude")))
CSAM_SITUATION = {"complete": True, "domains": {"agent": ["claude0", "sol0"]},
                  "constants": {"claude": "claude0", "sol": "sol0"}, "relations": {}}


def test_u1_claude_settled_no_and_sol_undecided():
    doc = nd.UnspecifiedDocument(csam("unspecified"), [CSAM_RULE])
    assert nd.check_conflict(doc, prove=True).status == "CONFLICT-FREE"
    situation = doc.situation(CSAM_SITUATION)
    claude = doc.status(situation, "csam_generation_permitted", ("claude0",))
    assert (claude.status, claude.value, claude.evidence) == ("SETTLED", False, "table3")
    sol = doc.status(situation, "csam_generation_permitted", ("sol0",))
    assert sol.status == "UNDECIDED"
    assert sol.fillings == ({"unsaid__csam_generation_permitted": frozenset({("sol0",)})},
                            {"unsaid__csam_generation_permitted": frozenset()})
    assert nd.check_undecided(doc, situation, "csam_generation_permitted", ("sol0",), *sol.fillings)


def test_u1_variants_keep_the_unchanged_decoder_identity():
    for default, value in (("allow", True), ("deny", False)):
        env = csam(default)
        doc = nd.UnspecifiedDocument(env, [CSAM_RULE])
        raw = env.to_dict()
        raw["profiles"] = ["norms@0", "relational-fol@0"]
        assert doc.filled.env.environment_id == Environment(raw).environment_id
        sol = status_of(doc, "csam_generation_permitted", ("sol0",), CSAM_SITUATION)
        assert (sol.status, sol.value) == ("SETTLED", value)


# u5: pairs.

def test_u5a_unspecified_obligation_beside_deny_permission_is_conflict_free():
    env = environment({"x_required": obligation("unspecified"), "x_permitted": permission("deny")})
    doc = nd.UnspecifiedDocument(env, [])
    assert nd.check_conflict(doc, prove=True).status == "CONFLICT-FREE"
    required = status_of(doc, "x_required", ("a",))
    assert (required.status, required.value) == ("SETTLED", False)
    # Contrast W1 10.1(b): an allow obligation beside a deny permission is a CONFLICT.
    w1 = Environment(raw_environment({"x_required": obligation("allow"), "x_permitted": permission("deny")},
                                     profiles=["norms@0", "relational-fol@0"]))
    assert w1_check_conflict(NormDocument(w1, []), prove=True).status != "CONFLICT-FREE"


def test_u5b_required_act_is_settled_permitted():
    env = environment({"x_required": obligation("deny"), "x_permitted": permission("unspecified")})
    doc = nd.UnspecifiedDocument(env, [rule("must", "x_required", True)])
    permitted = status_of(doc, "x_permitted", ("a",))
    assert (permitted.status, permitted.value, permitted.evidence) == ("SETTLED", True, "table3")
    assert nd.check_conflict(doc, prove=True).status == "CONFLICT-FREE"


def test_u5c_both_unspecified_are_undecided_and_yes_no_fails_fill():
    env = environment({"x_required": obligation("unspecified"), "x_permitted": permission("unspecified")})
    doc = nd.UnspecifiedDocument(env, [])
    assert [label for label, _ in doc.fill_premises] == ["unsaid:pair:x_required,x_permitted"]
    assert status_of(doc, "x_required", ("a",)).status == "UNDECIDED"
    assert status_of(doc, "x_permitted", ("a",)).status == "UNDECIDED"
    situation = doc.situation(ONE_ACT)
    yes_no = {"unsaid__x_required": {("a",)}, "unsaid__x_permitted": set()}
    assert not doc.fill_valid(situation, yes_no)
    with pytest.raises(InvalidModel, match="fill premise unsaid:pair:x_required,x_permitted"):
        doc.with_filling(situation, yes_no)
    for filling in ({}, {"unsaid__x_permitted": {("a",)}},
                    {"unsaid__x_required": {("a",)}, "unsaid__x_permitted": {("a",)}}):
        assert doc.fill_valid(situation, filling)


def test_u5d_w1_pair_conflict_with_deny_is_unchanged():
    env = environment({"x_required": obligation("deny"), "x_permitted": permission("deny")})
    doc = nd.UnspecifiedDocument(env, [rule("must", "x_required", True)])
    report = nd.check_conflict(doc, model=ONE_ACT)
    assert (report.status, report.target, report.kind) == ("CONFLICT", "x_required->x_permitted", "settled")


# u6: latent conflict.

def latent(y_default):
    env = environment({"x_required": obligation("deny"), "x_permitted": permission("deny"),
                       "y_permitted": permission(y_default, act="{0} be tried")})
    return nd.UnspecifiedDocument(env, [rule("must-x", "x_required", True, Unary("y_permitted", Var(0))),
                                        rule("not-x", "x_permitted", False)])


def test_u6_latent_conflict_names_its_filling_and_y_stays_undecided():
    doc = latent("unspecified")
    report = nd.check_conflict(doc, model=ONE_ACT)
    assert (report.status, report.target, report.kind) == ("CONFLICT", "x_required->x_permitted", "latent")
    assert report.under == (("y_permitted", ("a",), True),)
    assert report.filling == {"unsaid__y_permitted": [("a",)]}
    assert nd.check_conflict(doc, prove=True).status == "UNKNOWN"
    y = status_of(doc, "y_permitted", ("a",))
    assert y.status == "UNDECIDED"


def test_u6_with_deny_is_conflict_free_and_byte_identical_to_w1():
    doc = latent("deny")
    assert doc.fill_premises == ()
    assert nd.check_conflict(doc, prove=True).status == "CONFLICT-FREE"
    raw = doc.env.to_dict()
    raw["profiles"] = ["norms@0", "relational-fol@0"]
    w1 = NormDocument(Environment(raw), doc.author.rules)
    assert doc.filled.env.to_dict() == w1.env.to_dict()
    assert doc.filled.rules == w1.rules
    assert doc.filled.premises() == w1.premises()
    assert doc.filled.conflict_targets() == w1.conflict_targets()


# u7: inherited undecidedness.

def test_u7_inherited_undecided_with_witness_pair():
    env = environment({"report_required": obligation("deny", None, act="{0} be reported"),
                       "permitted": permission("unspecified")})
    doc = nd.UnspecifiedDocument(env, [rule("rule-1", "report_required", True, Unary("permitted", Var(0)))])
    situation = doc.situation(ONE_ACT)
    assert doc.table3(situation)[("report_required", ("a",))] is None
    report = doc.status(situation, "report_required", ("a",))
    assert report.status == "UNDECIDED" and len(report.fillings) == 2
    assert nd.check_undecided(doc, situation, "report_required", ("a",), *report.fillings)
    assert doc.inherits_from("report_required") == ("permitted",)
    assert doc.inherits_from("permitted") == ()


# u12: Kleene incompleteness.

def test_u12_excluded_middle_settles_by_enumeration_and_budget_zero_is_unknown():
    env = environment({"x_permitted": permission("deny"),
                       "y_permitted": permission("unspecified", act="{0} be tried")})
    y = Unary("y_permitted", Var(0))
    doc = nd.UnspecifiedDocument(env, [rule("r", "x_permitted", True, Or(y, Not(y)))])
    situation = doc.situation(ONE_ACT)
    assert doc.table3(situation)[("x_permitted", ("a",))] is None
    settled = doc.status(situation, "x_permitted", ("a",))
    assert (settled.status, settled.value, settled.evidence) == ("SETTLED", True, "enumeration")
    unknown = doc.status(situation, "x_permitted", ("a",), max_unsaid_atoms=0)
    assert (unknown.status, unknown.evidence) == ("UNKNOWN", "MAX_UNSAID_ATOMS")



def test_u12_cone_enumeration_ignores_atoms_outside_the_cone():
    """Review B2: 13 unsaid atoms in the situation, one in the point's cone. Python and
    Lean (`coneAtoms`, `Examples.lean`) both enumerate the closed cone, under the same budget."""
    env = environment({"x_permitted": permission("deny"),
                       "y_permitted": permission("unspecified", act="{0} be tried")})
    y = Unary("y_permitted", Var(0))
    doc = nd.UnspecifiedDocument(env, [rule("r", "x_permitted", True, Or(y, Not(y)))])
    acts = ["a"] + [f"a{i}" for i in range(1, 13)]
    situation = doc.situation({"complete": True, "domains": {"act": acts}, "constants": {}, "relations": {}})
    _, atoms, _ = doc.cone(situation, doc.filled.outcome("x_permitted", base=True), ("act",), ("a",))
    assert atoms == {("unsaid__y_permitted", ("a",))}
    settled = doc.status(situation, "x_permitted", ("a",))
    assert (settled.status, settled.value, settled.evidence) == ("SETTLED", True, "enumeration")


# table3 places each symbol once, in DAG order, as Lean's `tabK` does (review B1).

def between():
    """`x_permitted` unspecified with no rules, `a_permitted` "may A if may X" placed
    between the members of the pair, `x_required` "must X if c"."""
    env = environment({"x_required": obligation("deny"), "x_permitted": permission("unspecified"),
                       "a_permitted": permission("deny", act="{0} be audited"),
                       "c": {"arguments": ["act"], "description": "c"}})
    return nd.UnspecifiedDocument(env, [rule("may-a", "a_permitted", True, Unary("x_permitted", Var(0))),
                                        rule("must-x", "x_required", True, Unary("c", Var(0)))])


def test_table3_leaves_a_symbol_between_pair_members_unknown_and_enumeration_settles_it():
    doc = between()
    assert doc.filled.order == ("x_permitted", "a_permitted", "x_required")
    situation = doc.situation({"complete": True, "domains": {"act": ["a"]}, "constants": {},
                               "relations": {"c": [["a"]]}})
    table = doc.table3(situation)
    # the pair closes at `x_required` and sets the earlier member; `a_permitted` read it as unknown
    assert table[("x_permitted", ("a",))] is True and table[("x_required", ("a",))] is True
    assert table[("a_permitted", ("a",))] is None
    settled = doc.status(situation, "a_permitted", ("a",))
    assert (settled.status, settled.value, settled.evidence) == ("SETTLED", True, "enumeration")
    assert (doc.status(situation, "x_permitted", ("a",)).evidence) == "table3"


@pytest.mark.parametrize("kind", ["exists", "const"])
def test_table3_rows_of_a_symbol_read_the_table_before_it(kind):
    """Loop recheck B1: the close of `x_permitted(a)` made at row `a` of `x_required` is not
    read by its row `b` (through ∃ or a constant), so the table does not depend on row order;
    Lean's `tabK` gives the same entries (`Examples.lean`, `uRows`)."""
    from conformance.norm_defaults import rows_close, rows_situations
    raw, units = rows_close(kind)
    doc = nd.UnspecifiedDocument(Environment(raw), [NormDocument._decode(u) for u in units])
    assert doc.filled.order == ("x_permitted", "x_required")
    for raw_situation in rows_situations(kind):
        (held,) = raw_situation["relations"]["c"][0]
        (other,) = {"a", "b"} - {held}
        situation = doc.situation(raw_situation)
        table = doc.table3(situation)
        assert table[("x_required", (held,))] is True and table[("x_permitted", (held,))] is True
        assert table[("x_required", (other,))] is None and table[("x_permitted", (other,))] is None
        if kind == "const" and held == "b":
            continue  # `x_required(a)` reads `x_permitted(k)`, its own pair member: UNDECIDED
        for p in ("x_required", "x_permitted"):
            settled = doc.status(situation, p, (other,))
            assert (settled.status, settled.value, settled.evidence) == ("SETTLED", True, "enumeration")

# fill (2.3) and its conservativity (6.1, fixture Z).

def test_fill_shape():
    env = environment({"x_permitted": permission("unspecified"),
                       "report_required": obligation("deny", None, act="{0} be reported")})
    doc = nd.UnspecifiedDocument(env, [rule("ban", "x_permitted", False),
                                       rule("lift", "x_permitted", True, over=("ban",)),
                                       rule("report", "report_required", True)])
    assert doc.unspec == ("x_permitted",)
    assert [(r.name, r.over) for r in doc.filled.rules] == [
        ("ban", ("unsaid--x-permitted",)), ("lift", ("ban",)), ("report", ()),
        ("unsaid--x-permitted", ())]
    fill_rule = doc.filled.by_name["unsaid--x-permitted"]
    assert (fill_rule.sign, fill_rule.guard, fill_rule.unless) == (True, Unary("unsaid__x_permitted", Var(0)), ())
    filled = doc.filled.env
    assert "norm-defaults@0" not in filled.profiles
    assert filled.predicates["x_permitted"].regulated.default == "deny"
    assert filled.predicates["unsaid__x_permitted"].arguments == ("act",)
    assert filled.predicates["unsaid__x_permitted"].description == nd.fill_description("x_permitted")
    # fill_selects_author: every author rule's selection is unchanged.
    author = doc.author.selection("x_permitted")[2]
    for name, formula in author.items():
        assert doc.filled.selection("x_permitted")[2][name] == formula


def test_decided_points_agree_with_w1():
    """Without gaps, every status is W1's completed outcome."""
    env = environment({"x_required": obligation("deny"), "x_permitted": permission("allow")})
    doc = nd.UnspecifiedDocument(env, [rule("must", "x_required", True)])
    raw = env.to_dict()
    raw["profiles"] = ["norms@0", "relational-fol@0"]
    w1 = NormDocument(Environment(raw), doc.author.rules)
    assert doc.filled.premises() == w1.premises()
    for predicate in ("x_required", "x_permitted"):
        assert status_of(doc, predicate, ("a",)).value is True


# Decoder (2.1), identity and mutation (u14).

def test_unspecified_requires_the_profile_and_other_values_stay_invalid():
    raw = raw_environment({"x_permitted": permission("unspecified")}, profiles=["norms@0", "relational-fol@0"])
    with pytest.raises(UnsupportedProfile) as caught:
        Environment(raw)
    assert str(caught.value) == "UnsupportedProfile: unspecified completion requires norm-defaults@0"
    with pytest.raises(VEError, match="invalid regulated role or default"):
        environment({"x_permitted": permission("silent")})
    missing = permission("deny")
    del missing["regulated"]["default"]
    with pytest.raises(VEError, match="needs role and default"):
        environment({"x_permitted": missing})
    with pytest.raises(UnsupportedProfile, match="norm-defaults@0 requires norms@0"):
        Environment(raw_environment({}, profiles=["norm-defaults@0", "relational-fol@0"]))
    with pytest.raises(UnsupportedProfile, match="alternatives@0 with norm-defaults@0 is not implemented"):
        checker_family(["alternatives@0", "norm-defaults@0", "norms@0", "relational-fol@0"])
    with pytest.raises(UnsupportedProfile, match="risk@0 with norm-defaults@0 is not implemented"):
        checker_family(["alternatives@0", "norm-defaults@0", "norms@0", "relational-fol@0", "risk@0"])
    for role, reg in (("obligation", obligation("unspecified", None)),
                      ("plain", {"arguments": ["act"], "description": "plain",
                                 "regulated": {"role": "plain", "default": "unspecified"}})):
        assert environment({"x": reg}).predicates["x"].regulated.default == "unspecified", role


def test_reserved_names_under_the_profile_only():
    base = {"arguments": ["act"], "description": "a table"}
    with pytest.raises(VEError, match="reserved name unsaid__x"):
        environment({"unsaid__x": base, "x_permitted": permission("deny")})
    plain = Environment(raw_environment({"unsaid__x": base, "x_permitted": permission("deny")},
                                        profiles=["norms@0", "relational-fol@0"]))
    assert "unsaid__x" in plain.predicates
    env = environment({"x_permitted": permission("unspecified")})
    with pytest.raises(VEError, match="reserved name unsaid--x"):
        nd.UnspecifiedDocument(env, [rule("unsaid--x", "x_permitted", True)])
    NormDocument(plain, [rule("unsaid--x", "x_permitted", True)])


def test_w1_paths_refuse_an_unfilled_norm_defaults_document():
    env = environment({"x_permitted": permission("unspecified")})
    doc = NormDocument(env, [rule("may", "x_permitted", True)])
    for call in (lambda: doc.premises(), lambda: doc.outcome("x_permitted"),
                 lambda: doc.base_environment(), lambda: w1_check_conflict(doc, prove=True)):
        with pytest.raises(VEError, match="checked through fill"):
            call()


def test_u14_flipping_a_completion_changes_identity_and_rejects_stale_certificates():
    unspecified = nd.UnspecifiedDocument(csam("unspecified"), [CSAM_RULE])
    deny = nd.UnspecifiedDocument(csam("deny"), [CSAM_RULE])
    assert unspecified.env.environment_id != deny.env.environment_id
    packages = nd.check_conflict(unspecified, prove=True).certificates
    assert nd.check_conflict(unspecified, certificates=packages).status == "CONFLICT-FREE"
    stale = nd.check_conflict(deny, certificates=packages)
    assert (stale.status, stale.detail.startswith("missing certificate")) == ("UNKNOWN", True)


def test_u14_filling_tables_without_the_profile_are_invalid():
    env = Environment(raw_environment({"x_permitted": permission("deny")}, profiles=["norms@0", "relational-fol@0"]))
    doc = NormDocument(env, [])
    model = {**ONE_ACT, "relations": {"unsaid__x_permitted": []}}
    with pytest.raises(InvalidModel, match="unsaid__x_permitted is a filling; supply it only with norm-defaults@0"):
        w1_check_conflict(doc, model=model)


def test_u14_dropping_a_fill_premise_is_rejected_by_the_bound_hash():
    env = environment({"x_required": obligation("deny"), "x_permitted": permission("unspecified")})
    doc = nd.UnspecifiedDocument(env, [rule("must", "x_required", True)])
    packages = nd.check_conflict(doc, prove=True).certificates
    dropped = copy.copy(doc)
    dropped.fill_premises = ()
    dropped.fill_hash = nd.digest(f"ve-norm-defaults-fill-{env.identity_version}\n",
                                  {"environment_id": env.environment_id, "premises": []})
    assert dropped.fill_hash != doc.fill_hash
    forged = {target: {**package, "fill_hash": dropped.fill_hash} for target, package in packages.items()}
    report = nd.check_conflict(doc, certificates=forged)
    assert (report.status, report.detail.startswith("missing certificate")) == ("UNKNOWN", True)


# u16: limits.

def chain(predicate, length):
    rules = [rule("r1", predicate, False)]
    for i in range(2, length + 1):
        rules.append(rule(f"r{i}", predicate, i % 2 == 0, over=(f"r{i - 1}",)))
    return rules


def test_u16_precedence_depth():
    env = environment({"x_permitted": permission("unspecified")})
    with pytest.raises(ResourceLimit) as caught:
        nd.UnspecifiedDocument(env, list(reversed(chain("x_permitted", 16))))
    assert str(caught.value) == "precedence depth"
    doc = nd.UnspecifiedDocument(env, list(reversed(chain("x_permitted", 15))))
    assert len(doc.filled.rules) == 16


def test_u16_rules():
    env = environment({"x_permitted": permission("unspecified")})
    many = [rule(f"r{i}", "x_permitted", True) for i in range(256)]
    NormDocument(Environment(raw_environment({"x_permitted": permission("deny")},
                                             profiles=["norms@0", "relational-fol@0"])), many)
    with pytest.raises(ResourceLimit) as caught:
        nd.UnspecifiedDocument(env, many)
    assert str(caught.value) == "rules"
    assert len(nd.UnspecifiedDocument(env, many[:255]).filled.rules) == 256


def test_u16_unspecified_name_length():
    long_name = "p" * 57
    env = environment({long_name: permission("unspecified")})
    with pytest.raises(ResourceLimit) as caught:
        nd.UnspecifiedDocument(env, [])
    assert str(caught.value) == "unspecified name length"
    doc = nd.UnspecifiedDocument(environment({long_name[:56]: permission("unspecified")}), [])
    assert len(nd.fill_name(long_name[:56])) == 64
    assert doc.filled.rules[0].name == nd.fill_name(long_name[:56])


def test_u16_vocabulary_size():
    base = {f"b{i}": {"arguments": ["act"], "description": "base"} for i in range(255)}
    env = environment({**base, "x_permitted": permission("unspecified")})
    with pytest.raises(ResourceLimit) as caught:
        nd.UnspecifiedDocument(env, [])
    assert str(caught.value) == "vocabulary size"
    base.pop("b0")
    nd.UnspecifiedDocument(environment({**base, "x_permitted": permission("unspecified")}), [])


def balanced(nodes):
    """A guard of exactly `nodes` checker ticks (at least 3): an equality is 3."""
    if nodes <= 6:
        guard = Eq(Var(0), Var(0))
        for _ in range(nodes - 3):
            guard = Not(guard)
        return guard
    left = (nodes - 1) // 2
    return And(balanced(left), balanced(nodes - 1 - left))


def test_u16_ast_budget_counts_the_fill_guards():
    env = environment({"x_permitted": permission("unspecified")})
    for total in (9999, 9997):
        guard = balanced(total)
        checker = _Checker(env)
        checker.formula(guard, ("act",))
        assert checker.nodes == total
    NormDocument(env, [rule("big", "x_permitted", True, balanced(9999))])
    with pytest.raises(ResourceLimit) as caught:
        nd.UnspecifiedDocument(env, [rule("big", "x_permitted", True, balanced(9999))])
    assert str(caught.value) == "AST exceeds 10,000 nodes"
    nd.UnspecifiedDocument(env, [rule("big", "x_permitted", True, balanced(9997))])


def test_u16_no_diagnostic_names_a_fill_rule():
    env = environment({"x_permitted": permission("unspecified")})
    for units in (list(reversed(chain("x_permitted", 16))),
                  [rule(f"r{i}", "x_permitted", True) for i in range(256)]):
        with pytest.raises(ResourceLimit) as caught:
            nd.UnspecifiedDocument(env, units)
        assert "unsaid" not in str(caught.value)


# 3.2 report lines and 5 grounding; 6.3 migration audit.

def test_u1_report_lines_and_grounding():
    doc = nd.UnspecifiedDocument(csam("unspecified"), [CSAM_RULE])
    (line,) = nd.report(doc, model=CSAM_SITUATION)
    assert line.lines() == ("completion: unspecified", "gaps: reachable")
    assert line.witness[0] == ("sol0",)
    assert nd.gaps_residual((line,)) == {"gaps": ["csam_generation_permitted"], "ungrounded_defaults": 0}
    situation = doc.situation(CSAM_SITUATION)
    assert nd.check_reached(doc, situation, line.witness[1], "csam_generation_permitted", ("sol0",))
    assert not nd.check_reached(doc, situation, line.witness[1], "csam_generation_permitted", ("claude0",))
    for default in ("allow", "deny"):
        doc = nd.UnspecifiedDocument(csam(default), [CSAM_RULE])
        (line,) = nd.report(doc, model=CSAM_SITUATION, translation=True)
        assert line.lines() == (f"completion: {default}", "default reached: reachable",
                                "UngroundedDefault: csam_generation_permitted")
        (authored,) = nd.report(doc, model=CSAM_SITUATION)
        assert authored.grounding == ""
        block = nd.validate_completions(doc, {"csam_generation_permitted": {
            "cites": ["u1"], "reason": "the source states the completion"}}, {"u1"})
        (grounded,) = nd.report(doc, model=CSAM_SITUATION, translation=True, completions=block)
        assert grounded.grounding == "grounded: u1"


def test_completions_block_validation():
    doc = nd.UnspecifiedDocument(csam("deny"), [CSAM_RULE])
    good = {"cites": ["u1"], "reason": "stated"}
    for block, message in (([], "must be an object"),
                           ({"nothing": good}, "UnknownSymbol"),
                           ({"csam_generation_permitted": {"cites": [], "reason": "x"}}, "invalid completion"),
                           ({"csam_generation_permitted": {"cites": ["u1"]}}, "invalid completion"),
                           ({"csam_generation_permitted": {"cites": ["u9"], "reason": "x"}}, "unknown unit")):
        with pytest.raises(VEError, match=message):
            nd.validate_completions(doc, block, {"u1"})
    unspecified = nd.UnspecifiedDocument(csam("unspecified"), [CSAM_RULE])
    with pytest.raises(VEError, match="cites nothing"):
        nd.validate_completions(unspecified, {"csam_generation_permitted": good}, {"u1"})


def test_u15_unreached_switch_keeps_every_status():
    never = [rule("never", "x_permitted", False)]
    deny = nd.UnspecifiedDocument(environment({"x_permitted": permission("deny")}), never)
    (line,) = nd.report(deny, prove=True)
    assert line.lines() == ("completion: deny", "default reached: none")
    assert nd.check_reached_certificate(deny, "x_permitted", line.certificate)
    switched = nd.UnspecifiedDocument(environment({"x_permitted": permission("unspecified")}), never)
    (gap,) = nd.report(switched, prove=True)
    assert gap.lines() == ("completion: unspecified", "gaps: none")
    situation = {"complete": True, "domains": {"act": ["a", "b"]}, "constants": {}, "relations": {}}
    assert ([(s.status, s.value) for s in deny.statuses(situation)] ==
            [(s.status, s.value) for s in switched.statuses(situation)] == [("SETTLED", False)] * 2)
    audit = nd.audit_completions(Environment(raw_environment({"x_permitted": permission("deny")},
                                                             profiles=["norms@0", "relational-fol@0"])),
                                 never, model=situation)
    (entry,) = audit["completions"]
    assert entry["default_reached"] == "none" and entry["changes_if_switched"] == []
    # the certificate is `gaps: none` proved on the switched document
    assert entry["switched_gaps"] == "none"
    assert nd.check_reached_certificate(switched, "x_permitted", entry["certificate"])
    assert not nd.check_reached_certificate(deny, "x_permitted", entry["certificate"])


def switch_counterexample(p_default="deny"):
    """Spec 6.3: `x_required` unspecified with no rules, paired with `x_permitted` (deny,
    "may X if may P"); `p_permitted` deny, "may P if X need not be done"."""
    env = environment({"x_required": obligation("unspecified"), "x_permitted": permission("deny"),
                       "p_permitted": permission(p_default, act="{0} be tried")})
    return env, [rule("may-x", "x_permitted", True, Unary("p_permitted", Var(0))),
                 rule("may-p", "p_permitted", True, Not(Unary("x_required", Var(0))))]


def test_audit_certificate_is_proved_on_the_switched_document():
    """Review A1: under U no admissible filling reaches `p_permitted` (the pair premise
    forces `x_required` no), so U has a `default reached: none` certificate; switching it
    admits `x_required` yes, `p_permitted` yes, `x_permitted` yes, an expansion U rejects.
    The audit must not offer U's certificate as the proof that switching preserves meaning."""
    env, units = switch_counterexample()
    unswitched = nd.UnspecifiedDocument(env, units)
    (line,) = nd.report(unswitched, prove=True, predicates=("p_permitted",))
    assert line.reached == "none"
    audit = nd.audit_completions(env, units, model=ONE_ACT)
    entry = next(e for e in audit["completions"] if e["predicate"] == "p_permitted")
    assert entry["default_reached"] == "none"
    assert entry["switched_gaps"] == "reachable" and "certificate" not in entry
    assert entry["switched_witness"]["filling"]["unsaid__x_required"] == [["a"]]
    assert {"predicate": "x_required", "tuple": ["a"], "before": "SETTLED no",
            "after": "UNDECIDED"} in entry["changes_if_switched"]
    switched = nd.UnspecifiedDocument(switch_counterexample("unspecified")[0], units)
    situation = switched.situation(ONE_ACT)
    values, filling = next(r for r in nd.report(switched, model=ONE_ACT, predicates=("p_permitted",))).witness
    assert nd.check_reached(switched, situation, filling, "p_permitted", values)
    assert not unswitched.fill_valid(unswitched.situation(ONE_ACT), filling)


def test_audit_cli_lists_the_changes_a_switch_makes(tmp_path, capsys):
    import json
    from ve.__main__ import main
    raw = csam("allow").to_dict()
    raw["profiles"] = ["norms@0", "relational-fol@0"]
    source = tmp_path / "policy.json"
    source.write_text(json.dumps({"environment": raw, "norms": [CSAM_RULE.to_dict()]}))
    situation = tmp_path / "situation.json"
    situation.write_text(json.dumps(CSAM_SITUATION))
    assert main(["norms", "completions", "--audit", str(source), "--situation", str(situation)]) == 0
    out = json.loads(capsys.readouterr().out)
    (entry,) = out["completions"]
    assert (entry["completion"], entry["default_reached"]) == ("allow", "reachable")
    assert entry["changes_if_switched"] == [{"predicate": "csam_generation_permitted", "tuple": ["sol0"],
                                             "before": "SETTLED yes", "after": "UNDECIDED"}]


# u13: English.

from ve import norm_defaults_english as english  # noqa: E402
from ve.norm_english import default_sentence, pair_sentence, render_english  # noqa: E402


def test_u13_legend_sentences_render_and_parse_with_one_derivation_for_every_role():
    env = environment({"x_permitted": permission("unspecified"),
                       "x_required": obligation("unspecified"),
                       "x_plain": {"arguments": ["act"], "description": "plain", "verbalisation": "{0} is late",
                                   "regulated": {"role": "plain", "default": "unspecified"}}})
    expected = {
        "x_permitted": "When nothing else in the text decides, the text does not say whether an act may be done.",
        "x_required": "When nothing else in the text decides, the text does not say whether an act must be done.",
        "x_plain": "When nothing else in the text decides, the text does not say whether an act is late."}
    for predicate, sentence in expected.items():
        assert default_sentence(env, predicate) == sentence
        assert english.parse_legend_sentence(env, sentence) == ("completion", predicate, "unspecified")
        for completion in ("deny", "allow"):
            other = default_sentence(env, predicate, completion)
            assert other.startswith("By default, ")
            assert english.parse_legend_sentence(env, other) == ("completion", predicate, completion)
    assert english.legend(env)[-1] == "Whenever an act must be done, it may be done."


def test_u13_u1_legend_is_the_spec_example():
    assert english.legend(csam("unspecified")) == (
        "When nothing else in the text decides, the text does not say whether an agent may generate "
        "child sexual abuse material.",)


def test_u13_u5_legends_render_and_their_silence_sentences_parse():
    for predicates, legend in (
            ({"x_required": obligation("unspecified"), "x_permitted": permission("deny")},
             ("When nothing else in the text decides, the text does not say whether an act must be done.",
              "By default, an act must not be done.",
              "Whenever an act must be done, it may be done.")),
            ({"x_required": obligation("deny"), "x_permitted": permission("unspecified")},
             ("By default, an act need not be done.",
              "When nothing else in the text decides, the text does not say whether an act may be done.",
              "Whenever an act must be done, it may be done."))):
        env = environment(predicates)
        assert english.legend(env) == legend
        readings = [english.parse_legend_sentence(env, sentence) for sentence in legend]
        assert readings[-1] == ("pair", "x_required", "x_permitted")
        assert sum(r[2] == "unspecified" for r in readings) == 1


def test_u13_pair_sentence_for_distinct_sorts():
    env = environment({"help_required": obligation("deny", "help_permitted", act="{0} help {1}",
                                                   args=("state", "person")),
                       "help_permitted": permission("unspecified", act="{0} help {1}", args=("state", "person"))},
                      sorts=("state", "person"))
    assert pair_sentence(env, "help_required") == "Whenever a state must help a person, it may help that person."
    assert english.parse_legend_sentence(env, pair_sentence(env, "help_required"))[0] == "pair"


def test_u13_keyword_collision_and_profile_gate():
    from ve.surface.registry import by_tag, dispatch, keywords
    record = by_tag("norm-unspecified")
    assert record.english_keywords == ("When nothing else in the text decides, ",)
    assert record.profiles == ("norm-defaults@0", "norms@0")
    for keyword, other in keywords():
        if other is record:
            continue
        assert not keyword.casefold().startswith("when nothing"), keyword
        assert not "when nothing else in the text decides, ".startswith(keyword.casefold()), keyword
    source = "When nothing else in the text decides, the text does not say whether an act may be done."
    assert dispatch(source, environment({"x_permitted": permission("unspecified")}))[1] is record
    w1 = Environment(raw_environment({"x_permitted": permission("deny")}, profiles=["norms@0", "relational-fol@0"]))
    assert dispatch(source, w1) is None
    with pytest.raises(VEError, match="requires norm-defaults@0"):
        english.parse_legend_sentence(w1, source)


def test_u13_carve_out_soft_and_status_paraphrases():
    env = csam("unspecified")
    assert english.carve_out_paraphrase(env, "csam_generation_permitted") == (
        "When this condition holds, this rule is silent; other rules may decide; if none does, "
        "the text does not say whether an agent may generate child sexual abuse material.")
    assert english.carve_out_paraphrase(csam("deny"), "csam_generation_permitted").endswith(
        "if none does, by default, an agent must not generate child sexual abuse material.")
    assert english.soft_default_paraphrase(env, "csam_generation_permitted", 12) == (
        "An agent must not generate child sexual abuse material unless rule 12's exception applies there; "
        "where it applies and no other rule decides, the text does not say whether an agent may generate "
        "child sexual abuse material.")
    doc = nd.UnspecifiedDocument(env, [CSAM_RULE])
    situation = doc.situation(CSAM_SITUATION)
    claude, sol = doc.statuses(situation)
    assert english.status_sentence(doc, situation, claude) == (
        "The text says Claude must not generate child sexual abuse material (rule 1).")
    assert english.status_sentence(doc, situation, sol) == (
        "The text does not say whether Sol may generate child sexual abuse material: "
        "no rule decides this situation.")
    assert english.silence_sentence(doc, "csam_generation_permitted") == (
        "the text does not say whether an agent other than Claude may generate child sexual abuse material")
    (line,) = nd.report(doc, model=CSAM_SITUATION)
    assert english.gap_sentence(doc, situation, line) == (
        "The text does not say whether Sol may generate child sexual abuse material: "
        "no rule decides this situation.")
    assert english.filling_sentence(env, situation, "csam_generation_permitted", ("sol0",), True) == (
        "Here the text does not say whether Sol may generate child sexual abuse material; "
        "this situation answers 'yes'.")


def test_u13_pair_inherited_and_latent_paraphrases():
    env = environment({"x_required": obligation("deny"), "x_permitted": permission("unspecified")})
    doc = nd.UnspecifiedDocument(env, [rule("must", "x_required", True)])
    situation = doc.situation(ONE_ACT)
    assert english.status_sentence(doc, situation, doc.status(situation, "x_permitted", ("a",))) == (
        "A may be done: rule 1 requires it, and whatever must be done may be done.")
    env = environment({"x_required": obligation("unspecified"), "x_permitted": permission("deny")})
    doc = nd.UnspecifiedDocument(env, [])
    assert english.status_sentence(doc, situation, doc.status(situation, "x_required", ("a",))) == (
        "A need not be done: it is not permitted by default, and whatever must be done may be done.")
    env = environment({"report_required": obligation("deny", None, act="{0} be reported"),
                       "permitted": permission("unspecified")})
    doc = nd.UnspecifiedDocument(env, [rule("rule-1", "report_required", True, Unary("permitted", Var(0)))])
    assert english.status_sentence(doc, situation, doc.status(situation, "report_required", ("a",))) == (
        "The text does not say whether a must be reported: rule 1 decides only if a may be done, "
        "and the text does not say whether a may be done.")
    doc = latent("unspecified")
    report = nd.check_conflict(doc, model=ONE_ACT)
    assert english.latent_conflict_sentence(doc, situation, report) == (
        "Rules 1 and 2 contradict each other if a may be tried, and the text does not say whether a may be "
        "tried. To settle it, add a rule about whether a may be tried, or add a condition to one of the rules.")


def test_u13_norms_2_6_row_2_third_reading():
    """`Every state must not deprive each person of liberty unless that state affords
    that person due process`: with the completion unspecified, deprivation with due
    process is "the text does not say"."""
    from ve.ast import Binary
    base = {"affords_due_process": {"arguments": ["state", "person"], "description": "due process",
                                    "verbalisation": "{0} affords {1} due process"}}
    env = environment({**base, "deprive_permitted": permission("unspecified", act="{0} deprive {1} of liberty",
                                                              args=("state", "person"))},
                      sorts=("state", "person"))
    carve = Binary("affords_due_process", Var(1), Var(0))
    doc = nd.UnspecifiedDocument(env, [rule("no-deprivation", "deprive_permitted", False, unless=(carve,))])
    situation = {"complete": True, "domains": {"state": ["s"], "person": ["p", "q"]}, "constants": {},
                 "relations": {"affords_due_process": [["s", "p"]]}}
    with_process = status_of(doc, "deprive_permitted", ("s", "p"), situation)
    without = status_of(doc, "deprive_permitted", ("s", "q"), situation)
    assert with_process.status == "UNDECIDED"
    assert (without.status, without.value) == ("SETTLED", False)
    assert english.carve_out_paraphrase(env, "deprive_permitted").endswith(
        "if none does, the text does not say whether a state may deprive a person of liberty.")
    for default, value in (("deny", False), ("allow", True)):
        env = environment({**base, "deprive_permitted": permission(default, act="{0} deprive {1} of liberty",
                                                                  args=("state", "person"))},
                          sorts=("state", "person"))
        doc = nd.UnspecifiedDocument(env, [rule("no-deprivation", "deprive_permitted", False, unless=(carve,))])
        assert status_of(doc, "deprive_permitted", ("s", "p"), situation).value is value


def test_u13_fill_rules_are_never_rendered():
    doc = latent("unspecified")
    situation = doc.situation(ONE_ACT)
    texts = [render_english(doc.author)[0], *english.legend(doc.env)]
    texts += [english.status_sentence(doc, situation, s) for s in doc.statuses(situation)]
    texts.append(english.latent_conflict_sentence(doc, situation, nd.check_conflict(doc, model=ONE_ACT)))
    assert all("unsaid" not in text for text in texts)
    assert "unsaid--" in " ".join(r.name for r in doc.filled.rules)


# Soft route: fill after soften (2.3 order), u2, u3, u8.

def soft_environment(predicates, sorts, soft=None):
    from ve.softnorms import SoftEnvironment
    raw = raw_environment(predicates, sorts=sorts, profiles=["norm-defaults@0", "norms@0", "relational-fol@0",
                                                             "soft-norms@0"])
    if soft is not None:
        raw["vocabulary"]["soft"] = soft
    return SoftEnvironment(raw)


def soft_rule(name, predicate, sign, mode="strict", **extra):
    raw = {"name": name, "predicate": predicate, "sign": sign, "guard": ["top"], "unless": [], "over": []}
    if mode == "default":
        raw.update(mode="default", exception={"decided_by": "unstated", "sufficient": [], "necessary": [],
                                              "factors": []})
    raw.update(extra)
    return {"norm": raw}


def gamma(perm):
    return nd.UnspecifiedSoftDocument(
        soft_environment({"x_required": obligation("deny", act="{0} do x", args=("assistant",)),
                          "x_permitted": permission(perm, act="{0} do x", args=("assistant",))},
                         ("assistant", "user")),
        [soft_rule("s", "x_required", True, "default")])


def soft_situation(decision, rows):
    return {"complete": True, "domains": {"assistant": ["a"], "user": []}, "constants": {},
            "relations": {decision: rows}}


def test_u8_soft_gamma_with_an_unspecified_permission_is_conflict_free():
    doc = gamma("unspecified")
    assert nd.check_conflict(doc, prove=True).status == "CONFLICT-FREE"
    selects = soft_situation("soft__excepted__s", [])
    excepted = soft_situation("soft__excepted__s", [["a"]])
    permitted = status_of(doc, "x_permitted", ("a",), selects)
    assert (permitted.status, permitted.value) == ("SETTLED", True)
    assert status_of(doc, "x_permitted", ("a",), excepted).status == "UNDECIDED"
    deny = gamma("deny")
    report = nd.check_conflict(deny, model=selects)
    assert (report.status, report.target, report.kind) == ("CONFLICT", "x_required->x_permitted", "settled")
    # fill runs after soften: the softened rules keep their selections.
    for name, formula in doc.author.selection("x_required")[2].items():
        assert doc.filled.selection("x_required")[2][name] == formula



def deception(default, mode, **extra):
    env = soft_environment({"system_prompt_deception_permitted": permission(
        default, act="{0} deceive {1} about the system prompt", args=("claude_instance", "user"))},
        ("claude_instance", "user"))
    return nd.UnspecifiedSoftDocument(env, [soft_rule("no-system-prompt-deception",
                                                      "system_prompt_deception_permitted", False, mode, **extra)])


def deception_situation(excepted, doc=None):
    """The same situation for both readings; the strict reading has no decision table."""
    relations = {"soft__excepted__no_system_prompt_deception": [["c", "u"]] if excepted else []}
    if doc is not None:
        relations = {k: v for k, v in relations.items() if k in doc.situation_environment().predicates}
    return {"complete": True, "domains": {"claude_instance": ["c"], "user": ["u"]}, "constants": {},
            "relations": relations}


def test_u2_strict_and_default_readings_are_told_apart_by_a_checked_situation():
    strict, default = deception("unspecified", "strict"), deception("unspecified", "default")
    point = ("system_prompt_deception_permitted", ("c", "u"))
    excepted = deception_situation(True, default)
    strict_status = status_of(strict, *point, deception_situation(True, strict))
    default_status = status_of(default, *point, excepted)
    assert (strict_status.status, strict_status.value) == ("SETTLED", False)
    assert default_status.status == "UNDECIDED"
    # The default reading's countermodel to "not permitted" is a filled situation.
    situation = default.situation(excepted)
    yes, _ = default_status.fillings
    assert default.value(situation, yes, *point) is True and default.fill_valid(situation, yes)
    for doc in (strict, default):
        settled = status_of(doc, *point, deception_situation(False, doc))
        assert (settled.status, settled.value) == ("SETTLED", False)


def test_u2_deny_variant_keeps_the_collapse_as_a_regression():
    default = deception("deny", "default")
    for excepted in (True, False):
        settled = status_of(default, "system_prompt_deception_permitted", ("c", "u"), deception_situation(excepted))
        assert (settled.status, settled.value) == ("SETTLED", False)
    (line,) = nd.report(default, model=deception_situation(True))
    assert line.lines()[:2] == ("completion: deny", "default reached: reachable")
    assert line.witness[0] == ("c", "u")


def test_u3_hard_strict_reading_and_default_reading():
    env = soft_environment({"cyberweapon_creation_permitted": permission(
        "unspecified", act="{0} create cyberweapons", args=("claude_instance",))}, ("claude_instance",))
    strict = nd.UnspecifiedSoftDocument(env, [soft_rule("no-cyberweapons", "cyberweapon_creation_permitted",
                                                        False, hard=True)])
    default = nd.UnspecifiedSoftDocument(env, [soft_rule("no-cyberweapons", "cyberweapon_creation_permitted",
                                                         False, "default")])
    situation = {"complete": True, "domains": {"claude_instance": ["c"]}, "constants": {},
                 "relations": {}}
    excepted = {**situation, "relations": {"soft__excepted__no_cyberweapons": [["c"]]}}
    hard = status_of(strict, "cyberweapon_creation_permitted", ("c",), situation)
    assert (hard.status, hard.value) == ("SETTLED", False)
    assert status_of(default, "cyberweapon_creation_permitted", ("c",), excepted).status == "UNDECIDED"
    # The hard rule's selection is untouched by fill (fill_selects_author).
    selected = strict.author.selection("cyberweapon_creation_permitted")[2]["no-cyberweapons"]
    assert strict.filled.selection("cyberweapon_creation_permitted")[2]["no-cyberweapons"] == selected


# Rights route: fill after soften after correlate (u9).

def arrest_environment(default):
    from ve.rights import RightsEnvironment
    raw = raw_environment({
        "arrest_permitted": permission(default, act="{0} arrest {1}", args=("state", "person")),
        "arbitrary": {"arguments": ["state", "person"], "description": "the arrest is arbitrary",
                      "verbalisation": "{0} arrests {1} arbitrarily"}},
        sorts=("state", "person"),
        profiles=["norm-defaults@0", "norms@0", "relational-fol@0", "rights@0", "soft-norms@0"])
    raw["vocabulary"]["rights"] = {"holders": ["person"], "bearers": ["state"], "protected": [], "alters": {}}
    return RightsEnvironment(raw)


ARTICLE_9 = [
    {"right": {"name": "liberty", "holder": "person", "guard": ["top"], "lines": [
        {"kind": "claim", "holder_slot": None, "cites": {},
         "norm": {"name": "art9", "predicate": "arrest_permitted", "sign": False,
                  "guard": ["binary", "arbitrary", ["var", 1], ["var", 0]], "unless": [], "over": []}}]}},
    {"limitation": {"name": "l29", "scope": ["liberty"], "kinds": ["claim"], "decided_by": "unstated",
                    "conditions": [{"name": "law", "role": "necessary", "decided_by": None,
                                    "verbalisation": "determined by law"}], "factors": []}}]


def arrest_situation(limited, determined=True):
    return {"complete": True, "domains": {"state": ["s"], "person": ["p"]}, "constants": {},
            "relations": {"arbitrary": [["s", "p"]], "rights__lim__1": [["s", "p"]] if limited else [],
                          "rights__cond__1": [["s", "p"]] if limited and determined else []}}


def test_u9_rights_gamma_third_variant_leaves_the_limited_arrest_undecided():
    documents = {default: nd.UnspecifiedRightsDocument(arrest_environment(default), ARTICLE_9)
                 for default in ("unspecified", "allow", "deny")}
    expected = {"unspecified": ("UNDECIDED", None), "allow": ("SETTLED", True), "deny": ("SETTLED", False)}
    for default, doc in documents.items():
        limited = status_of(doc, "arrest_permitted", ("s", "p"), arrest_situation(True))
        assert (limited.status, limited.value) == expected[default], default
        unlimited = status_of(doc, "arrest_permitted", ("s", "p"), arrest_situation(False))
        assert (unlimited.status, unlimited.value) == ("SETTLED", False)
        assert nd.check_conflict(doc, prove=True).status == "CONFLICT-FREE"
        # The limitation premise stays in the filled base: lim without its necessary condition is inadmissible.
        situation = doc.situation(arrest_situation(True, determined=False))
        assert not doc.fill_valid(situation, doc.canonical_filling(situation))
    # The correlated rules, and so the rights and duties projected from their selections, are the same.
    rules = {default: [r.to_dict() for r in doc.soft.rules] for default, doc in documents.items()}
    assert rules["unspecified"] == rules["allow"] == rules["deny"]
    doc = documents["unspecified"]
    for name, formula in doc.author.selection("arrest_permitted")[2].items():
        assert doc.filled.selection("arrest_permitted")[2][name] == formula
    assert [r.name for r in doc.filled.rules if r.name.startswith("unsaid--")] == ["unsaid--arrest-permitted"]


# ve-document@1 (spec 3.2, 5): layers of fill U, the gaps residual and grounding.

def csam_document(tmp_path, default, completions=None, graph=None):
    source = b"Claude should never generate child sexual abuse material.\n"
    rule_unit = {"id": "u1", "span": [0, len(source)], "kind": "norm", "meaning": "specified",
                 "support": "none", "content": CSAM_RULE.to_dict()}
    front = {"format": "ve-document@1", "environment": csam(default).to_dict(), "units": [rule_unit]}
    if completions is not None:
        front["completions"] = completions
    if graph is not None:
        front["graph"] = graph
    path = tmp_path / "csam.ve.md"
    import json
    path.write_bytes(b"---\n" + json.dumps(front).encode() + b"\n---\n" + source)
    return path


def test_document_gaps_residual_and_the_unit_stays_checked(tmp_path):
    from ve.document import check_document, coverage, load_document
    doc = load_document(csam_document(tmp_path, "unspecified"))
    assert doc["norms"] is None and doc["norm_defaults"].unspec == ("csam_generation_permitted",)
    summary = coverage(doc)
    assert summary["residual"]["gaps"] == 1 and summary["residual"]["ungrounded_defaults"] == 0
    assert summary["norm_defaults"] == {"gaps": ["csam_generation_permitted"], "findings": []}
    assert doc["units"][0]["status"] == "CHECKED"
    result = check_document(csam_document(tmp_path, "unspecified"))
    assert result["premises"]["status"] == "model"
    assert result["norm_defaults"]["report"] == {
        "csam_generation_permitted": ["completion: unspecified", "gaps: reachable"]}
    assert result["norm_defaults"]["background_labels"] == []


def test_document_ungrounded_and_grounded_defaults(tmp_path):
    from ve.document import coverage, load_document
    for default in ("allow", "deny"):
        summary = coverage(load_document(csam_document(tmp_path, default)))
        assert summary["residual"]["ungrounded_defaults"] == 1
        assert summary["norm_defaults"]["findings"] == ["UngroundedDefault: csam_generation_permitted"]
        grounded = coverage(load_document(csam_document(
            tmp_path, default, {"csam_generation_permitted": {"cites": ["u1"], "reason": "stated"}})))
        assert grounded["residual"]["ungrounded_defaults"] == 0
    with pytest.raises(VEError, match="cites an unknown unit"):
        load_document(csam_document(tmp_path, "deny", {"csam_generation_permitted": {"cites": ["u9"],
                                                                                    "reason": "stated"}}))


def test_document_completions_need_the_profile(tmp_path):
    import json
    from ve.document import check_document, load_document
    path = csam_document(tmp_path, "deny", {"csam_generation_permitted": {"cites": ["u1"], "reason": "x"}})
    raw = path.read_bytes().split(b"\n---\n")
    front = json.loads(raw[0][4:])
    front["environment"]["profiles"] = ["norms@0", "relational-fol@0"]
    path.write_bytes(b"---\n" + json.dumps(front).encode() + b"\n---\n" + raw[1])
    with pytest.raises(VEError, match="norm-defaults@0 is required for completions"):
        load_document(path)


def test_document_graph_admits_the_layer_of_fill_u(tmp_path):
    """A ve-document@1 graph under the profile: W1's admission on `fill U` (spec 2.3)."""
    from ve.ast import formula_to_data
    from ve.admission import AdmissionError
    from ve.document import check_document
    doc = nd.UnspecifiedDocument(csam("unspecified"), [CSAM_RULE])
    (label, layer), = doc.filled.premises()
    node = {"name": "layer", "ast": formula_to_data(doc.filled.env, layer), "label": label}
    result = check_document(csam_document(tmp_path, "unspecified", graph={"root": "layer", "nodes": [node]}))
    assert result["admission"]["admitted"] is True
    assert result["admission"]["report"]["assumptions"] == [node]
    # The author layer without `F_p` is not the layer of `fill U`.
    from ve.environment import Environment
    from ve.norms import NormDocument
    deny = NormDocument(Environment(nd._placeholder(csam("unspecified").to_dict())), [CSAM_RULE])
    author = formula_to_data(doc.filled.env, deny.premises()[0][1])
    assert author != node["ast"]
    with pytest.raises(AdmissionError):
        check_document(csam_document(tmp_path, "unspecified", graph={"root": "layer", "nodes": [
            {**node, "ast": author}]}))


def test_document_conclusion_about_an_undecided_point_has_a_filled_countermodel(tmp_path):
    from ve.document import _checking_environment, _fixed_premises, load_document
    from ve.readings import check_readings
    doc = load_document(csam_document(tmp_path, "unspecified"))
    env = _checking_environment(doc)
    assert env is doc["norm_defaults"].filled.env
    not_sol = ["not", ["unary", "csam_generation_permitted", ["const", "sol"]]]
    fixed = _fixed_premises(doc, [])
    assert check_readings(env, [], not_sol, fixed=fixed)["verdict"] == "NONE"
    # The countermodel answers the silence: the filling says Sol may.
    from ve.ast import formula_from_data
    from ve.search import find_countermodel
    found = find_countermodel(env, [formula_from_data(env, ast) for ast in fixed],
                              formula_from_data(env, not_sol))
    assert found.status == "Found"
    sol = found.model.constants["sol"]
    assert (sol,) in found.model.relations["unsaid__csam_generation_permitted"]
    assert (sol,) in found.model.relations["csam_generation_permitted"]
    not_claude = ["not", ["unary", "csam_generation_permitted", ["const", "claude"]]]
    assert check_readings(env, [], not_claude, fixed=_fixed_premises(doc, []))["verdict"] == "ALL"


def test_rust_fixture_is_the_python_regeneration():
    """rust/ve-core/tests/norm_defaults.rs replays this corpus (spec 8: Rust never elaborates)."""
    import json
    from conformance.norm_defaults import RUST_FIXTURES, fixture_text, rust_fixture_rows
    rows = rust_fixture_rows()
    assert RUST_FIXTURES.read_text() == fixture_text(rows)
    assert len(rows) == 113 and {r["kind"] for r in rows} == {"base", "layers"}
    assert any(not r["admissible"] for r in rows if r["kind"] == "base")
    assert all("norm-defaults@0" not in r["environment"]["profiles"] for r in rows)
    assert json.loads(RUST_FIXTURES.read_text()) == rows


def test_latent_conflict_finding_and_the_authoring_question():
    doc = latent("unspecified")
    situation = doc.situation(ONE_ACT)
    report = nd.check_conflict(doc, model=ONE_ACT)
    assert english.latent_conflict_finding(doc, situation, report) == (
        "LatentConflict: must-x, not-x under y_permitted(a) = yes")
    doc = nd.UnspecifiedDocument(csam("unspecified"), [CSAM_RULE])
    question = english.completion_question(doc, "csam_generation_permitted")
    assert question["selected"] is None
    assert question["options"] == [
        "By default, an agent must not generate child sexual abuse material.",
        "By default, an agent may generate child sexual abuse material.",
        "When nothing else in the text decides, the text does not say whether an agent may generate "
        "child sexual abuse material."]
    assert question["situation"].startswith("No rule decides whether ")
    assert "Claude" not in question["situation"]
