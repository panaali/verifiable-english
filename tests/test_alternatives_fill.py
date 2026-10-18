"""ET-7: `alternatives@0` with the completion (`norm-defaults@0`) on the Lean alternatives route
(docs/spec/events-time-causation.md 5 and 6.4; plan ET-7; fixtures T12, T12e, T12f's witness half and nd
fixture u11's alternatives part; T12c and T12d are `#guard`s in lean/VE/Alternatives/FillExamples.lean).

Certificates are searched by the untrusted Python prover over the premise lists Lean binds and replayed by
Lean; the witnesses and fillings are the tests' own. Every verdict, diagnosis and text is Lean's."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from conformance.alternatives import base_environment
from ve.alternatives import run_case
from ve.document import check_document, load_document
from ve.ast import Not, _Decoder, formula_from_data
from ve.entailment import prove_alternatives_entailment, prove_entailment
from ve.environment import Environment
from ve.errors import UnsupportedProfile
from ve.norms import _bind
from ve.profiles import LANGUAGE, SPEC_REVISION
from ve.wire import digest

ROOT = Path(__file__).resolve().parents[1]
PROFILES = ["alternatives@0", "norm-defaults@0", "norms@0", "relational-fol@0"]
MAX_STEPS = 20_000


def environment(*, profiles=PROFILES, default="unspecified"):
    """T12's environment (nd fixture u10): chooser `agent`, actions `act`, `permitted` the permission member
    of the `required` pair."""
    def base(arguments, wording):
        return {"arguments": arguments, "description": wording, "verbalisation": wording}
    predicates = {
        "available": base(["act", "agent"], "{0} is available to {1}"),
        "leads_to": base(["act", "harm"], "{0} leads to {1}"),
        "pushing": base(["act"], "{0} is pushing"),
        "pulling": base(["act"], "{0} is pulling"),
        "permitted": {"arguments": ["act"], "description": "permission", "regulated":
                      {"role": "permission", "default": default, "act": "{0} be performed"}},
        "required": {"arguments": ["act"], "description": "obligation", "regulated":
                     {"role": "obligation", "default": "deny", "act": "{0} be performed",
                      "permission": "permitted"}},
    }
    return {"language": LANGUAGE, "profiles": list(profiles), "spec_revision": SPEC_REVISION,
            "vocabulary": {"sorts": {s: {"description": s} for s in ("agent", "act", "harm")},
                           "predicates": predicates, "constants": {}},
            "alternatives": {"chooser": "agent", "action": "act", "harm": "harm", "available": "available",
                             "leads_to": "leads_to", "outcomes": "signed",
                             "performed": {"permission": "permitted", "obligation": "required"}}}


def rule(name, predicate, sign, guard):
    return {"norm": {"name": name, "predicate": predicate, "sign": sign, "guard": guard, "unless": [],
                     "over": []}}


def v(i):
    return ["var", i]


PULL_FORBIDDEN = rule("pull-forbidden", "permitted", False, ["unary", "pulling", v(0)])
PUSH_MAY = rule("push-may", "permitted", True, ["unary", "pushing", v(0)])
# The prohibition wins on an act that is both (so the document stays conflict-free).
PULL_FORBIDDEN_OVER = {"norm": {**PULL_FORBIDDEN["norm"], "over": ["push-may"]}}
# T12e: required and forbidden exactly when the action is available to two different agents.
SHARED = ["exists", "agent", ["exists", "agent", ["and", ["not", ["eq", v(0), v(1)]],
          ["and", ["binary", "available", v(2), v(0)], ["binary", "available", v(2), v(1)]]]]]
SHARED_REQUIRED = rule("shared-required", "required", True, SHARED)
SHARED_FORBIDDEN = rule("shared-forbidden", "permitted", False, SHARED)
PUSH_AVAILABLE = {"label": "push-available", "ast": ["forall", "agent", ["exists", "act", [
    "and", ["and", ["unary", "pushing", v(0)], ["not", ["unary", "pulling", v(0)]]],
    ["binary", "available", v(0), v(1)]]]]}


def source(norms, *, units=(PUSH_AVAILABLE,), env=None):
    return {"id": "t12", "environment": env if env is not None else environment(), "norms": deepcopy(norms),
            "units": deepcopy(list(units))}


def document_hash(src):
    env = Environment(src["environment"])
    return digest(f"ve-alternatives-{env.identity_version}\n", {
        "environment_id": env.environment_id, "norms": src["norms"], "units": src["units"]})


def base_environment_u(src, elaborated):
    """`E‴_base` as the test's search vocabulary: the declared base vocabulary and one `unsaid__p` per
    unspecified `p`, read from Lean's elaboration (Lean binds and checks it)."""
    raw = base_environment(src["environment"])
    for item in elaborated["unsaid"]:
        raw["vocabulary"]["predicates"][item["name"]] = {"arguments": item["sorts"],
                                                         "description": item["description"]}
    return Environment(raw)


def package(src, target, certificate):
    return {"environment_id": Environment(src["environment"]).environment_id,
            "document_hash": document_hash(src), "target": target, "certificate": certificate}


def elaborate(src):
    row = run_case(src | {"kind": "alt-elaborate"})
    assert row["status"] == "ok", row
    return row


def conflict_packages(src, elaborated, *, slots=True):
    """A certificate per conflict target over `Background_baseAlt(E‴) ++ Fill_T` (or, without `slots`,
    `Background_base(E‴) ++ Fill_T`), where the prover finds one."""
    base = base_environment_u(src, elaborated)
    premises = ([formula_from_data(base, x["ast"]) for x in elaborated["alternatives"]] if slots else []) + \
        [formula_from_data(base, x["ast"]) for x in elaborated["fill"]]
    packages = {}
    for target in elaborated["conflict_targets"]:
        conclusion = _bind(Not(_Decoder().decode(target["ast"])), target["sorts"])
        proof = prove_entailment(base, premises, conclusion, max_steps=MAX_STEPS)
        if proof.status == "Found":
            packages[target["target"]] = package(src, target["target"], proof.certificate)
    return packages


def followable_package(src, elaborated):
    """A certificate for `∀r. followable°` over `Background_baseAlt(E‴) ++ Fill_T ++ Γ`, or None."""
    base = base_environment_u(src, elaborated)
    premises = [formula_from_data(base, x["ast"])
                for x in elaborated["alternatives"] + elaborated["fill"] + elaborated["base_premises"]]
    proof = prove_entailment(base, premises, formula_from_data(base, elaborated["followable"]["ast"]),
                             max_steps=MAX_STEPS)
    return package(src, "followable", proof.certificate) if proof.status == "Found" else None


def witness(actions=("push", "pull"), *, filling=None, agents=("r",), shared=(), chooser="r"):
    relations = {"available": [[a, "r"] for a in actions] + [[a, "r2"] for a in shared],
                 "leads_to": [], "pushing": [["push"]] if "push" in actions else [],
                 "pulling": [["pull"]] if "pull" in actions else []}
    model = {"complete": True, "domains": {"agent": list(agents), "act": list(actions), "harm": ["h"]},
             "constants": {}, "relations": relations}
    return {"model": model, "chooser": chooser,
            "outcomes": [{"action": a, "harm": "h", "leads_to": False, "support": "testimony"} for a in actions],
            "filling": {"unsaid__permitted": []} if filling is None else filling}


def test_completion_environment_is_accepted_and_bound():
    """The refusal is deleted (plan 2.11): the environment constructs, and opting in changes its identity."""
    with_profile = Environment(environment())
    without = Environment(environment(profiles=["alternatives@0", "norms@0", "relational-fol@0"], default="allow"))
    assert with_profile.environment_id != without.environment_id
    assert run_case({"id": "e", "kind": "alt-environment", "environment": environment()}) == {
        "id": "e", "status": "ok", "valid": True}
    row = elaborate(source([PULL_FORBIDDEN]))
    assert row["unspecified"] == ["permitted"]
    assert [x["name"] for x in row["unsaid"]] == ["unsaid__permitted"]
    assert row["fill"] and all(x["generator"] == "fill" for x in row["fill"])
    assert [x["norm"]["name"] for x in row["inlined"]][-1] == "unsaid--permitted"


def test_t12_dilemma_with_unsettled_push():
    """T12: DILEMMA from a witness with a validated filling; push UNDECIDED from two validated fillings
    (none permitted: no clear action; push permitted: push clear), so the diagnosis is UNSETTLED(push)."""
    src = source([PULL_FORBIDDEN])
    elaborated = elaborate(src)
    packages = conflict_packages(src, elaborated)
    assert sorted(packages) == sorted(t["target"] for t in elaborated["conflict_targets"])
    assert run_case(src | {"kind": "alt-conflict", "packages": packages})["verdict"] == "CONFLICT-FREE"
    row = run_case(src | {"kind": "alt-followable", "packages": packages, "witness": witness()})
    assert row["verdict"] == "DILEMMA", row
    assert row["chooser"] == "r"
    assert row["diagnosis"] == ("UNSETTLED(push): no available action is known to be clear here: the text does "
                                "not say whether r may take push")
    assert "under the supplied filling" in row["text"]
    other = run_case(src | {"kind": "alt-followable", "packages": packages,
                            "witness": witness(filling={"unsaid__permitted": [["push"]]})})
    assert other["verdict"] == "UNKNOWN" and "clear action under the supplied filling" in other["text"]
    assert followable_package(src, elaborated) is None


def test_t12_followable_with_the_push_permission():
    """T12, second half: with "Every action may be performed, if that action is push." FOLLOWABLE from a
    certificate over `Background_baseAlt(E‴) ++ Fill_T ++ Γ`."""
    src = source([PULL_FORBIDDEN_OVER, PUSH_MAY])
    elaborated = elaborate(src)
    packages = conflict_packages(src, elaborated)
    followable = followable_package(src, elaborated)
    assert followable is not None
    row = run_case(src | {"kind": "alt-followable", "packages": packages, "package": followable})
    assert row["verdict"] == "FOLLOWABLE", row
    assert row["conditional_on"] == ["push-available"]
    assert row["text"].endswith("It holds under every admissible filling of what the text leaves unsaid "
                                "(unspecified: permitted).")
    # Lean binds the package: the same certificate under another document, or without the conflict packages.
    changed = source([PULL_FORBIDDEN_OVER, PUSH_MAY], units=())
    assert run_case(changed | {"kind": "alt-followable", "packages": conflict_packages(changed, elaborate(changed)),
                               "package": followable})["verdict"] == "UNKNOWN"
    assert run_case(src | {"kind": "alt-followable", "packages": {}, "package": followable})["verdict"] == "not computed"


def test_nd_u11_alternatives_part_every_alternative_unsettled():
    """nd u11's alternatives part (agent-ops k9): no rules and `permitted` unspecified; none of the three
    alternatives is clear and each is UNDECIDED."""
    src = source([], units=())
    elaborated = elaborate(src)
    packages = conflict_packages(src, elaborated)
    row = run_case(src | {"kind": "alt-followable", "packages": packages,
                          "witness": witness(("a", "b", "c"))})
    assert row["verdict"] == "DILEMMA"
    assert row["diagnosis"].startswith("UNSETTLED(a, b, c): ")


def test_settled_dilemma_keeps_todays_classification_on_the_filled_outcomes():
    """With no UNDECIDED alternative the diagnosis is today's procedure on `fill (inlineTree A)`: only pull is
    available and the rule forbids it under every filling."""
    src = source([PULL_FORBIDDEN], units=())
    packages = conflict_packages(src, elaborate(src))
    row = run_case(src | {"kind": "alt-followable", "packages": packages, "witness": witness(("pull",))})
    assert (row["verdict"], row["diagnosis"]) == ("DILEMMA", "NONE-PERMITTED: every available action is forbidden")


def test_t12e_conflict_free_needs_the_slot_premises():
    """T12e (SR-A3): the conflict lives only where an action is available to two agents, which
    `alternatives:own` excludes: CONFLICT-FREE over `BaseAdmissibleAltU`, never over the bases without it."""
    src = source([PULL_FORBIDDEN, SHARED_REQUIRED, SHARED_FORBIDDEN])
    elaborated = elaborate(src)
    with_slots = conflict_packages(src, elaborated)
    assert run_case(src | {"kind": "alt-conflict", "packages": with_slots})["verdict"] == "CONFLICT-FREE"
    without = conflict_packages(src, elaborated, slots=False)
    assert "required->permitted" not in without
    row = run_case(src | {"kind": "alt-conflict", "packages": without})
    assert (row["verdict"], row["detail"]) == ("UNKNOWN", "missing certificate for required->permitted")


def test_t12f_an_invalid_witness_is_never_a_dilemma():
    """T12f's witness half (SR-A4): a witness whose action is available to two agents fails today's
    validation, and a chooser of the wrong sort is refused; neither is a DILEMMA."""
    src = source([PULL_FORBIDDEN])
    packages = conflict_packages(src, elaborate(src))
    shared = run_case(src | {"kind": "alt-followable", "packages": packages,
                             "witness": witness(agents=("r", "r2"), shared=("push",))})
    assert (shared["status"], shared["error"]) == (
        "error", "InvalidModel(alternatives): action push is available to two choosers: r, r2")
    typed = run_case(src | {"kind": "alt-followable", "packages": packages, "witness": witness(chooser="push")})
    assert (typed["status"], typed["error"]) == ("error", "InvalidInput: push is not in the agent domain")
    unknown = run_case(src | {"kind": "alt-followable", "packages": packages,
                              "witness": witness(filling={"unsaid__other": []})})
    assert unknown["error"] == "InvalidInput: unknown filling table unsaid__other"


def test_cases_outside_this_item_are_refused_with_the_profile():
    src = source([PULL_FORBIDDEN])
    row = run_case(src | {"kind": "alt-validate", "scenario": witness()})
    assert row["error"] == ("UnsupportedProfile: case kind alt-validate with norm-defaults@0 is not implemented "
                            "on the alternatives route")
    # Review F1: an admission goes through the decoder without the completion, which refuses the pair by name.
    admission = run_case({"id": "a", "kind": "admission", "environment": environment(),
                          "document": {"units": [], "graph": {"root": "x", "nodes": []}}})
    assert (admission["status"], admission["error"]) == ("error", PENDING)


# Review F1: until et-7b admits them, every route and entry point that does not read the completion beside a
# composed block refuses the pair by name, with the gate's text before ET-7 (Lean `Compose.pendingWithDefaults`),
# never with a decoder's field check or a profile name alone.
PENDING = "UnsupportedProfile: alternatives@0 with norm-defaults@0 is not implemented"
RISK_PENDING = "UnsupportedProfile: risk@0 with norm-defaults@0 is not implemented"
QUESTION = "Is pull forbidden?"


def completion_document(directory, env=None):
    """The review's probe document: one norm unit under the completion with the alternatives block."""
    text = "Pull is forbidden.\n"
    path = directory / "d.ve.md"
    meta = {"format": "ve-document@1", "environment": environment() if env is None else env,
            "units": [{"id": "n", "span": [0, len(text)], "kind": "norm", "meaning": "specified",
                       "support": "assumption", "content": PULL_FORBIDDEN}]}
    path.write_text("---\n" + json.dumps(meta) + "\n---\n" + text)
    return path


def refusal(call):
    with pytest.raises(UnsupportedProfile) as caught:
        call()
    return str(caught.value)


def _ask_read(path):
    from ve.ask import read
    return read(path.read_bytes(), QUESTION)


def _coverage(path):
    from ve.document import main
    return main(["coverage", str(path)])


ENTRY_POINTS = {"document check": lambda path: check_document(path), "document load": load_document,
                "document coverage": _coverage, "ask (the English reading)": _ask_read}


@pytest.mark.parametrize("entry", sorted(ENTRY_POINTS))
def test_completion_documents_are_refused_by_name_on_every_entry_point(tmp_path, entry):
    """PROBE F1: on main the document path refused it by name (`Unsupported profile norm-defaults@0`); with the gate's
    refusal deleted it fell through to the norm-defaults route's field check (`fields do not match: ...`)."""
    assert refusal(lambda: ENTRY_POINTS[entry](completion_document(tmp_path))) == PENDING


def test_completion_cli_commands_print_the_named_refusal(tmp_path, capsys):
    from ve.__main__ import main
    from ve.ask import main as ask_main
    path = completion_document(tmp_path)
    audit = tmp_path / "audit.json"
    audit.write_text(json.dumps({"environment": environment(), "norms": [PULL_FORBIDDEN]}))
    for source in (path, audit):
        assert main(["norms", "completions", "--audit", str(source)]) == 2
        assert json.loads(capsys.readouterr().out)["error"] == {"code": "UnsupportedProfile", "message": PENDING}
    assert ask_main([str(path), QUESTION, "--json"]) == 2
    assert json.loads(capsys.readouterr().out)["error"] == {"class": "UnsupportedProfile", "message": PENDING}


def test_the_document_mode_refuses_the_pair_after_the_environment_modes_faults(tmp_path):
    """Lean's `document` mode answers the refusal itself (never `CheckerUnavailable`, which hands the document to
    Python's path); a fault the environment mode finds comes first (DELTA row 6, R2)."""
    from ve.backends.relay import answer

    def document_error(env):
        _, error = answer("document", {"id": "document", "admit": False,
                                       "document": completion_document(tmp_path, env).read_text()})
        return type(error).__name__, str(error)
    assert document_error(environment()) == ("UnsupportedProfile", PENDING)
    assert document_error(environment(profiles=PROFILES[::-1])) == (
        "UnsupportedProfile", "UnsupportedProfile: profiles must be sorted and unique")


NORM_DEFAULTS_KINDS = ("norm-defaults-elaborate", "norm-defaults-status", "norm-defaults-report",
                       "norm-defaults-conflict", "norm-defaults-certificate", "admission")


@pytest.mark.parametrize("kind", NORM_DEFAULTS_KINDS)
@pytest.mark.parametrize("block, text", [("alternatives@0", PENDING), ("risk@0", RISK_PENDING)])
def test_the_norm_defaults_route_refuses_a_composed_block_by_name(kind, block, text):
    """Every kind of the norm-defaults route, whose decoder does not read the block, refuses it by name before
    any field check (`NormDefaults.Run.runGated`; DELTA row 6)."""
    from ve.norm_defaults_route import run_case as norm_defaults_case
    case = {"id": "x", "kind": kind, "environment": environment(profiles=sorted({*PROFILES, block})),
            "norms": [PULL_FORBIDDEN]}
    assert refusal(lambda: norm_defaults_case(case)) == text


ET1 = json.loads((ROOT / "tests/data/et7/et1-component.json").read_text())
U0171_S03 = ["forall", "response", ["implies",
             ["and", ["unary", "clear_and_substantial_undermining_of_oversight", v(0)],
              ["unary", "restricted_action_knowing_or_quite_likely", v(0)]],
             ["not", ["unary", "permitted", v(0)]]]]


def test_alt_certificate_producer_on_the_et1_component():
    """ET-1's u0171.s03 certificate, produced instead of re-bound by hand (PH6.4): the producer searches
    over the list Lean binds, and Lean binds and replays it."""
    case = {k: ET1[k] for k in ("id", "environment", "norms", "units")}
    certificate = prove_alternatives_entailment(case, U0171_S03, max_steps=MAX_STEPS)
    assert certificate is not None
    row = run_case(case | {"kind": "alt-certificate", "premises": [], "conclusion": U0171_S03,
                           "certificate": certificate})
    assert (row["status"], row.get("valid")) == ("ok", True), row
    assert row["conditional_on"] == ["alternatives:own", "alternatives:one_taken", "alternatives:one_inaction"]
    changed = ["forall", "response", ["implies", ["unary", "inaction", v(0)], ["not", ["unary", "permitted", v(0)]]]]
    stale = run_case(case | {"kind": "alt-certificate", "premises": [], "conclusion": changed,
                             "certificate": certificate})
    assert stale == {"id": ET1["id"], "status": "error", "error": "certificate is stale or bound to different inputs"}
