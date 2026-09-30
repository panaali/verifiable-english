"""norm-defaults@0 fixtures (docs/spec/norm-defaults.md section 9), Python side."""
import copy

import pytest

from ve.ast import And, Const, Eq, Not, Or, Top, Unary, Var, _Checker
from ve.environment import Environment
from ve.errors import InvalidModel, ResourceLimit, UnsupportedProfile, VEError
from ve.norms import Norm, NormDocument, check_conflict as w1_check_conflict
from ve.profiles import LANGUAGE, SPEC_REVISION
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
    return environment(
        {"csam_generation_permitted": permission(default, act="{0} generate child sexual abuse material",
                                                 args=("entity",))},
        sorts=("entity",), constants={"claude": {"sort": "entity", "description": "Claude"},
                                      "sol": {"sort": "entity", "description": "Sol"}})


CSAM_RULE = rule("no-csam-generation", "csam_generation_permitted", False, Eq(Var(0), Const("claude")))
CSAM_SITUATION = {"complete": True, "domains": {"entity": ["claude0", "sol0"]},
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
    assert filled.predicates["unsaid__x_permitted"].description == nd.FILL_DESCRIPTION
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
