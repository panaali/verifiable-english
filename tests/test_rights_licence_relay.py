"""rights-licence-relay: Lean returns each narrowing mechanism's licence with the grounds it rests on, and the
relay binds them to the request instead of deriving them (ends rd-9's D1 exception, `_narrowings`).

The elaboration names what the relay binds: per line, the limitations in scope and the bar's reach; per
mechanism, its licence and grounds (the citation, the colliding right line or the strict rule); per rule, the
mechanisms that name it and what each of its citations licenses (Run.lean `elaboratedNarrowingsJson`,
`ruleNarrowingsJson`; Scope.lean `ground`, `citedBy_sound`, `ground_isSome`, `licence_spec`). A corrupted
mechanism, licence, target, scope flag, bar reach, grounds or rule row is still `CheckerUnavailable`, in the
elaboration alone and when the elaboration and the scope answer are forged together.
"""
from __future__ import annotations

import ast
import copy
from pathlib import Path

import pytest

from ve.errors import CheckerUnavailable

ROOT = Path(__file__).resolve().parents[1]


def _sources():
    from tests.test_relay_binding_inventory import _rights_sources
    from tests.test_rights_lean import ARREST, GAMMA, env, limitation
    # Two limitations in scope on one line, which Lean lists in the request's order (review F1).
    return {**_rights_sources(), "two limitations": (env(ARREST), [*copy.deepcopy(GAMMA), limitation("l30")])}


def _source(name):
    from ve.rights import RightsEnvironment
    raw, units = _sources()[name]
    return RightsEnvironment(raw), units


def test_probe_the_relay_holds_no_copy_of_the_licence_derivation():
    """No function, helper or citation key of Lean's derivation is left in the relay: `_narrowings` and `_in_scope`
    are gone, the soft relations they filtered by are not imported, and no `cited` key or limitation scope is read."""
    tree = ast.parse((ROOT / "ve/rights_route.py").read_text())
    functions = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
    assert not functions & {"_narrowings", "_in_scope"}
    imported = {alias.name for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) for alias in node.names}
    assert not imported & {"_incompatible", "_rank_above"}
    strings = [node.value for node in ast.walk(tree) if isinstance(node, ast.Constant) and type(node.value) is str]
    assert not [s for s in strings if s.startswith(("unless:", "over:", "narrows:", "alterable:"))]
    keys = {node.slice.value for node in ast.walk(tree)
            if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant)}
    assert not keys & {"scope", "kinds", "rank"}


def _resync(row):
    """Make a scope answer's findings and `licensed` agree with its mechanisms (Run.lean `narrowingsJson`), so a
    forgery is refused by the check it aims at, not by the findings it would otherwise contradict."""
    if "licensed" in row:
        row["findings"] = [f"UnlicensedLimitation: {m['mechanism']} of rule {entry['rule']} on right {entry['right']}"
                           for entry in row["narrowings"] if entry["in_scope"]
                           for m in entry["mechanisms"] if m["licence"] is None]
        row["licensed"] = not row["findings"]


def _forge(monkeypatch, mutation, kinds):
    from tests.test_soft_decision_keys import _rights_relay
    _rights_relay(monkeypatch, _resynced(mutation), kinds)


def _mechanism(row, text):
    return next(m for entry in row["narrowings"] for m in entry["mechanisms"] if m["mechanism"] == text)


def _named_rule(text):
    """The rule a rule-named slot names (`blockedBy r`, `dominatedBy r`, `exception r`), else None."""
    kind, _, name = text.partition(" ")
    return name if kind in ("exception", "blockedBy", "dominatedBy") and name else None


def _add(rule, text, *, licence=None, grounds=None, at=None, conclusion=("top",)):
    """Add mechanism `text` to the line of `rule` (the first line when None) at index `at` (else last), and list it
    in the `rule_narrowings` row of the rule it names, so only the line's own binding can refuse it."""
    def mutation(row):
        entry = next(entry for entry in row["narrowings"] if rule in (None, entry["rule"]))
        mechanism = {"mechanism": text, "target": f"{entry['rule']}:{text}", "licence": licence,
                     "conclusion": list(conclusion)}
        if "rule_narrowings" in row:
            # The elaboration's mechanisms carry their licence's grounds.
            mechanism["grounds"] = copy.deepcopy(grounds)
            for named in row["rule_narrowings"]:
                if named["rule"] == _named_rule(text):
                    named["narrows"].append(mechanism["target"])
        mechanisms = entry["mechanisms"]
        mechanisms.insert(len(mechanisms) if at is None else at, mechanism)
    return mutation


def _rename(old, new, at=None):
    """Rename a mechanism (moved to index `at` of its line when given), its target and its rule row's entry."""
    def mutation(row):
        mechanism = _mechanism(row, old)
        rule = mechanism["target"].split(":", 1)[0]
        mechanism.update(mechanism=new, target=f"{rule}:{new}")
        for entry in row.get("rule_narrowings", []):
            entry["narrows"] = [f"{rule}:{new}" if t == f"{rule}:{old}" else t for t in entry["narrows"]]
        if at is not None:
            mechanisms = next(entry["mechanisms"] for entry in row["narrowings"] if mechanism in entry["mechanisms"])
            mechanisms.insert(at, mechanisms.pop(mechanisms.index(mechanism)))
    return mutation


def _drop(text):
    def mutation(row):
        for entry in row["narrowings"]:
            entry["mechanisms"] = [m for m in entry["mechanisms"] if m["mechanism"] != text]
    return mutation


_KEEP = object()


def _relicense(text, licence, grounds=_KEEP):
    """Set a mechanism's licence in every forged answer and, when given, its grounds in the elaboration."""
    def mutation(row):
        mechanism = _mechanism(row, text)
        mechanism["licence"] = licence
        if grounds is not _KEEP and "rule_narrowings" in row:
            mechanism["grounds"] = copy.deepcopy(grounds)
    return mutation


def _set(text, field, value):
    def mutation(row):
        _mechanism(row, text)[field] = value
    return mutation


def _flip_scope(row):
    for entry in row["narrowings"]:
        entry["in_scope"] = not entry["in_scope"]


def _elaboration(edit):
    def mutation(row):
        if "rule_narrowings" in row:
            edit(row)
    return mutation


def _both(*edits):
    def mutation(row):
        for edit in edits:
            edit(row)
    return mutation


def _unsynced(edit):
    """A forgery of the scope findings themselves, which `_resync` must leave as forged."""
    edit.unsynced = True
    return edit


def _resynced(mutation):
    def consistent(row):
        mutation(row)
        if not getattr(mutation, "unsynced", False):
            _resync(row)
    return consistent


def _out_of_scope(row):
    """Show the first line out of scope: no limitation mechanism, no limitation pack on its node; the limitations
    Lean lists in scope (and so the limitation premises) are kept."""
    entry = row["narrowings"][0]
    entry["in_scope"] = False
    entry["mechanisms"] = [m for m in entry["mechanisms"] if m["mechanism"] != "limitation"]
    for line in row.get("lines", []):
        if line["rule"] == entry["rule"]:
            line["node"]["unless"].pop()


CORRUPTIONS = [
    # The mechanism: renamed to another slot of a declared rule (target kept consistent), or dropped.
    ("same effect strict", _rename("blockedBy rule-4", "dominatedBy rule-4"), "mechanism renamed to a dominance"),
    ("same effect strict", _rename("blockedBy rule-4", "blockedBy may-publish"), "mechanism blocked by itself"),
    ("same effect strict", _drop("blockedBy rule-4"), "a rule-named mechanism dropped"),
    ("weighed and protected", _drop("switch person"), "a switch dropped"),
    ("default gamma", _drop("exception"), "the default exception dropped"),
    # The licence: each flip with every other field kept.
    ("same effect strict", _relicense("blockedBy rule-4", None), "effect licence dropped"),
    ("same effect strict", _relicense("blockedBy rule-4", "collision"), "effect relicensed as a collision"),
    ("strict liberty blocks", _relicense("blockedBy may-publish", None), "collision licence dropped"),
    ("cited opposite effect", _relicense("blockedBy rule-5", None), "citation licence dropped"),
    ("opposite effect", _relicense("blockedBy rule-5", "cited"), "an uncited mechanism licensed as cited"),
    ("opposite effect", _relicense("blockedBy rule-5", "effect delivered by strict rule rule-5"),
     "an opposite-effect rule as a same-effect licence"),
    # The target.
    ("same effect strict", _set("blockedBy rule-4", "target", "rule-4:blockedBy rule-4"), "target of another rule"),
    # The scope flag and the bar's reach.
    ("gamma", _flip_scope, "scope flag flipped"),
    ("bar", _elaboration(lambda row: row["narrowings"][0].update(bar=None)), "bar reach dropped"),
    ("gamma", _elaboration(lambda row: row["narrowings"][0].update(limitations=[])), "limitations in scope dropped"),
    # The grounds.
    ("cited opposite effect", _elaboration(_set("blockedBy rule-5", "grounds",
                                                {"citation": {"rule": "rule-5", "key": "exception"}})),
     "grounds name a citation the request lacks"),
    ("cited switch", _elaboration(_set("switch person", "grounds",
                                       {"citation": {"rule": "no-arbitrary-arrest", "key": "exception"}})),
     "grounds name another mechanism's citation key"),
    ("strict liberty blocks", _elaboration(_set("blockedBy may-publish", "grounds", {"line": "no-attack"})),
     "collision grounds name another line"),
    ("same effect strict", _elaboration(_set("blockedBy rule-4", "grounds", None)), "effect grounds dropped"),
    # The per-rule rows.
    ("same effect strict", _elaboration(lambda row: row["rule_narrowings"][1].update(narrows=[])),
     "a rule's mechanisms dropped from its row"),
    ("cited opposite effect", _elaboration(lambda row: row["rule_narrowings"][1]["citations"][0].update(licenses=[])),
     "a citation's licenses dropped"),
    ("cited opposite effect", _elaboration(lambda row: row["rule_narrowings"][1].update(citations=[])),
     "a citation row dropped"),
    ("same effect strict", _elaboration(lambda row: row["rule_narrowings"].pop()), "a rule row dropped"),
    # Review F1: one forgery per line check, the rest of the answer (rule rows, scope findings) kept consistent.
    ("two limitations", _elaboration(lambda row: row["narrowings"][0]["limitations"].reverse()),
     "limitations in scope out of the request's order"),
    ("two limitations", _elaboration(lambda row: row["narrowings"][0]["limitations"].__setitem__(1, "l29")),
     "a limitation in scope listed twice"),
    ("adopter exception", _add("no-arbitrary-arrest", "exception no-arbitrary-arrest", at=0),
     "a strict line excepted by itself"),
    ("default gamma", _add("no-arbitrary-arrest", "dominatedBy no-arbitrary-arrest"), "a line dominated by itself"),
    ("adopter exception", _add("no-arbitrary-arrest", "blockedBy rule-7"), "a strict line shown with blockedBy"),
    ("adopter exception", _add("no-arbitrary-arrest", "dominatedBy rule-7"), "a strict line shown with dominatedBy"),
    ("gamma", _elaboration(_set("limitation", "grounds", {"rule": "no-arbitrary-arrest"})),
     "grounds on the limitation"),
    ("bar", _elaboration(_set("bar", "grounds", {"line": "may-impart"})), "grounds on the bar"),
    ("same effect strict", _relicense("blockedBy rule-4", "collision", {"line": "rule-4"}),
     "the outside norm rule-4 shown blocking as a collision"),
    ("weighed and protected", _relicense("dominatedBy may-arrest", "collision", {"line": "may-arrest"}),
     "the outside norm may-arrest shown dominating as a collision"),
    ("strict liberty blocks", _rename("blockedBy may-publish", "exception may-publish", at=0),
     "a collision licensing an exception"),
    ("carve-out", _drop("carve-out 1"), "a carve-out dropped"),
    ("gamma", _out_of_scope, "a line shown out of scope while its limitations stay"),
    ("gamma", _both(_elaboration(lambda row: row["narrowings"][0].update(bar="arrest_permitted")),
                    _add(None, "bar", licence="bar")), "a bar shown reaching a line when none is requested"),
    ("gamma", _drop("limitation"), "the limitation dropped from a line in scope"),
    ("bar", _drop("bar"), "the bar dropped from a line it reaches"),
    ("carve-out", _add("no-arbitrary-arrest", "carve-out 2", at=1), "a carve-out the rule lacks"),
    ("default gamma", _add("no-arbitrary-arrest", "blockedBy absent"), "blocked by an undeclared rule"),
    ("weighed and protected", _add("no-arbitrary-arrest", "switch nobody", at=2), "a switch the rule does not allow"),
    ("weighed and protected", _add("no-arbitrary-arrest", "limitation", licence="limitation", at=0),
     "a limitation on a line out of scope"),
    ("same effect strict", _relicense("blockedBy rule-4", "effect delivered by strict rule may-publish"),
     "an effect licence naming another rule"),
    ("uncited rank", lambda row: row["narrowings"].reverse(), "narrowing rows out of the lines' order"),
    # The mechanism text itself (`_slot`).
    ("gamma", _add(None, "ghost thing"), "a mechanism of an unknown kind"),
    ("default gamma", _add(None, "blockedBy"), "a rule slot naming no rule"),
    ("carve-out", _rename("carve-out 1", "carve-out \u0661"), "a carve-out numbered in Arabic-Indic digits"),
]

# Forgeries of the scope answer alone (`_bind_narrowings`), refused whether certificates were sent or not, except
# that a sent certificate may license a mechanism the elaboration left unlicensed (Run.lean `narrowingsJson`).
SCOPE_FORGERIES = [
    ("default gamma", _drop("exception"), "scope: a mechanism dropped"),
    ("gamma", _flip_scope, "scope: the scope flag flipped"),
    ("carve-out", _unsynced(lambda row: row["findings"].__setitem__(
        0, "UnlicensedLimitation: limitation of rule no-arbitrary-arrest on right r9")),
     "scope: a finding naming another mechanism"),
    ("carve-out", _relicense("carve-out 1", "certified"), "scope: an unlicensed carve-out certified"),
    ("carve-out", _relicense("carve-out 1", "collision"), "scope: an unlicensed carve-out shown as a collision"),
    ("cited carve-out", _relicense("carve-out 1", "certified"), "scope: a cited carve-out shown certified"),
]
CERTIFIABLE = {"scope: an unlicensed carve-out certified"}


@pytest.mark.parametrize("kinds", [("rights-elaborate",), ("rights-elaborate", "rights-scope")],
                         ids=["elaboration", "elaboration and scope"])
@pytest.mark.parametrize("source,mutation", [pytest.param(s, m, id=i) for s, m, i in CORRUPTIONS])
def test_a_corrupted_lean_answer_is_still_refused(monkeypatch, source, mutation, kinds):
    from ve import rights_route
    environment, units = _source(source)
    rights_route.report_rights(environment, units)  # the genuine answers pass
    _forge(monkeypatch, mutation, kinds)
    with pytest.raises(CheckerUnavailable):
        rights_route.report_rights(environment, units)


@pytest.mark.parametrize("source,mutation", [pytest.param(s, m, id=i) for s, m, i in CORRUPTIONS])
def test_the_elaboration_binder_alone_refuses_it(monkeypatch, source, mutation):
    """The elaboration's own binder (the call `RightsDocument` makes) refuses each corruption without the scope
    answer to compare with."""
    from ve import rights_route
    environment, units = _source(source)
    _forge(monkeypatch, mutation, ("rights-elaborate",))
    with pytest.raises(CheckerUnavailable):
        rights_route.run_rights_case(environment, units, "rights-elaborate")


@pytest.mark.parametrize("source,mutation,label", [pytest.param(s, m, i, id=i) for s, m, i in SCOPE_FORGERIES])
def test_a_corrupted_scope_answer_is_refused(monkeypatch, source, mutation, label):
    """The scope answer alone forged: refused when no certificate is sent (the report); with certificates sent,
    only the certificate's own licence of a mechanism the elaboration left unlicensed is accepted."""
    from ve import rights_route
    from ve.backends.service_schema import check_row
    environment, units = _source(source)
    rights_route.report_rights(environment, units)
    _forge(monkeypatch, mutation, ("rights-scope",))
    with pytest.raises(CheckerUnavailable):
        rights_route.report_rights(environment, units)
    monkeypatch.undo()
    real, genuine = rights_route.decide_once, {}

    def reply(mode, case):
        if case["kind"] != "rights-scope":
            return real(mode, case)
        if not genuine:  # Lean's answer without certificates, forged as if a certificate had been sent
            genuine["row"] = copy.deepcopy(real(mode, {**case, "certificates": {}}))
            _resynced(mutation)(genuine["row"])
        check_row(mode, genuine["row"], case, 0)
        return copy.deepcopy(genuine["row"])

    monkeypatch.setattr(rights_route, "decide_once", reply)
    sent = {"no-arbitrary-arrest:carve-out 1": {}}
    if label in CERTIFIABLE:
        rights_route.run_rights_case(environment, units, "rights-scope", certificates=sent)
    else:
        with pytest.raises(CheckerUnavailable):
            rights_route.run_rights_case(environment, units, "rights-scope", certificates=sent)


def test_the_genuine_grounds_name_request_items():
    """Acceptance against Lean: in every genuine elaboration, a licence is null exactly when its grounds are, a
    cited licence's citation is a key the request's rule cites, and a collision or effect names the mechanism's
    own rule; the scope answer's licences are the elaboration's."""
    from tests.test_relay_binding_inventory import _rights_sources
    from ve import rights_route
    from ve.rights import RightsEnvironment
    kinds = set()
    for raw, units in _rights_sources().values():
        environment = RightsEnvironment(raw)
        elaborated = rights_route.run_rights_case(environment, units, "rights-elaborate")
        report = rights_route.report_rights(environment, units)
        for entry, shown in zip(elaborated["narrowings"], report["narrowings"]):
            assert [m["licence"] for m in entry["mechanisms"]] == [m["licence"] for m in shown["mechanisms"]]
            for mechanism in entry["mechanisms"]:
                grounds, licence = mechanism["grounds"], mechanism["licence"]
                kinds.add(next(iter(grounds)) if grounds else licence)
                if licence in (None, "limitation", "bar"):
                    assert grounds is None
                elif licence == "cited":
                    rule, key = grounds["citation"]["rule"], grounds["citation"]["key"]
                    assert any(key in ((unit.get("cites") or {}) if unit.get("norm", {}).get("name") == rule else {})
                               for unit in units) or any(
                        key in (line.get("cites") or {}) for unit in units
                        for body in [unit.get("right") or unit.get("right_lines") or {}]
                        for line in body.get("lines", []))
                else:
                    assert next(iter(grounds.values())) == mechanism["mechanism"].split(" ", 1)[1]
    assert kinds == {None, "limitation", "bar", "citation", "line", "rule"}


# The narrowing binder: every check of these functions, and the cross-row checks of `_bind_elaboration` that bind
# the narrowing rows, by the reason they raise.
BINDERS = ("_slot", "_bind_line_narrowings", "_bind_narrowings")
CROSS_ROW = ("unbound narrowing line", "unbound rule narrowing row", "unbound rule narrowing or citation licence")
KINDS = (("rights-elaborate",), ("rights-elaborate", "rights-scope"))


def _reason(node):
    exc = node.exc
    if isinstance(exc, ast.Call) and exc.args and isinstance(exc.args[0], ast.Constant):
        return exc.args[0].value
    return None


def _checks(tree):
    """Each check as `(function, condition, refuses)`: the test of an `if` that raises, which refuses when it holds,
    or the `bound` a licence is given, which accepts when it holds."""
    for function in tree.body:
        if not isinstance(function, ast.FunctionDef):
            continue
        for node in ast.walk(function):
            if (isinstance(node, ast.If) and isinstance(node.body[0], ast.Raise) and
                    (function.name in BINDERS or _reason(node.body[0]) in CROSS_ROW)):
                yield function.name, node.test, True
            elif (function.name in BINDERS and isinstance(node, ast.Assign) and
                  [ast.unparse(target) for target in node.targets] == ["bound"]):
                yield function.name, node.value, False


def _weakenings(node, refuses):
    """Every sub-condition of a check whose replacement by a constant weakens it: by False where it refuses, by True
    where it accepts. `and`/`or` keep the polarity; `not` flips it."""
    yield node, not refuses
    if isinstance(node, ast.BoolOp):
        for value in node.values:
            yield from _weakenings(value, refuses)
    elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        yield from _weakenings(node.operand, not refuses)


def _sites(tree):
    return [(function, node, value) for function, check, refuses in _checks(tree)
            for node, value in _weakenings(check, refuses)]


def _replace(tree, old, new):
    for parent in ast.walk(tree):
        for field, value in ast.iter_fields(parent):
            if value is old:
                setattr(parent, field, new)
                return
            if isinstance(value, list) and any(item is old for item in value):
                value[[item is old for item in value].index(True)] = new
                return
    raise AssertionError("site not found")


def _mutants():
    """`(description, module namespace)` for each weakened check of the relay, compiled from its source."""
    path = ROOT / "ve/rights_route.py"
    source = path.read_text()
    for index in range(len(_sites(ast.parse(source)))):
        tree = ast.parse(source)
        function, node, value = _sites(tree)[index]
        description = f"{function}:{node.lineno}: {ast.unparse(node)} -> {value}"
        _replace(tree, node, ast.Constant(value))
        namespace = {"__name__": "ve.rights_route", "__package__": "ve", "__file__": str(path)}
        exec(compile(ast.fix_missing_locations(tree), str(path), "exec"), namespace)
        yield description, namespace


@pytest.fixture(scope="module")
def recorded():
    """Lean's genuine elaboration and scope answers, with their requests, for each source a forgery uses."""
    from ve import rights_route
    answers = {}
    with pytest.MonkeyPatch.context() as patch:
        for name in sorted({source for source, _, _, _ in _corpus()}):
            environment, units = _source(name)
            real, rows = rights_route.decide_once, {}

            def record(mode, case, real=real, rows=rows):
                row = real(mode, case)
                rows[case["kind"]] = (case, copy.deepcopy(row))
                return row
            patch.setattr(rights_route, "decide_once", record)
            rights_route.report_rights(environment, units)
            patch.setattr(rights_route, "decide_once", real)
            answers[name] = rows
    return answers


def _outcome(binder, rows, mutation, kinds):
    """The reasons `binder` (the relay module's namespace) refuses the forged answers, with no certificate sent and
    with one sent; None where it accepts them."""
    forged = {kind: copy.deepcopy(row) for kind, (_, row) in rows.items()}
    for kind in kinds:
        _resynced(mutation)(forged[kind])
    case = rows["rights-elaborate"][0]
    reasons = []
    for empty in (True, False):
        try:
            binder["_bind_elaboration"](forged["rights-elaborate"], case["document"], case["environment"])
            binder["_bind_narrowings"](forged["rights-scope"], forged["rights-elaborate"], empty_certificates=empty)
        except CheckerUnavailable as error:
            reasons.append(str(error))
        else:
            reasons.append(None)
    return tuple(reasons)


def _corpus():
    from tests.test_soft_decision_keys import F20_FORGERIES
    return ([(name, mutation, kinds, label) for name, mutation, label in CORRUPTIONS + F20_FORGERIES
             for kinds in KINDS] +
            [(name, mutation, ("rights-scope",), label) for name, mutation, label in SCOPE_FORGERIES])


def test_review_f1_every_narrowing_binder_check_is_needed_by_a_forgery(recorded):
    """Review F1 (PROBE F1): weaken each check of the narrowing binder in turn, one sub-condition at a time, as the
    AST lists them (a check added later is enumerated too). Each weakened binder must accept, or refuse for another
    reason, some forgery of CORRUPTIONS, F20 or SCOPE_FORGERIES that the relay refuses; else no test needs that
    check. With no certificate sent, the relay refuses every forgery."""
    from ve import rights_route
    corpus = _corpus()
    baseline = [_outcome(vars(rights_route), recorded[name], mutation, kinds) for name, mutation, kinds, _ in corpus]
    assert [label for (*_, label), (empty, _) in zip(corpus, baseline) if empty is None] == []
    survivors, count = [], 0
    for description, binder in _mutants():
        count += 1
        if all(_outcome(binder, recorded[name], mutation, kinds) == reasons
               for (name, mutation, kinds, _), reasons in zip(corpus, baseline)):
            survivors.append(description)
    assert count >= 60  # the enumeration reaches every check (the narrowing binder had 79 sites at review F1)
    assert survivors == [], "\n".join(survivors)
