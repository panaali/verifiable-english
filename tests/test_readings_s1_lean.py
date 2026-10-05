"""Lean readings route (docs/spec/composition-s1.md 8.4) on inputs in the shapes of the item-1 fixtures (9.2).

The Lean executable decodes the environment and the W2 document, runs the checks of 4.1 with section 7's texts,
regenerates every candidate's document, its source keys and its generated names, and checks each recorded
situation with `separates` (sound by `separates_sound`). Nothing here is decided by Python: the situation ids are
computed as the decoder computes them, and every expectation was derived from the spec. Checked: K1's separation
both ways and its finding, K19's rights candidates under a fixed limitation, K2b's base outside the author's
vocabulary, K5's fixed table under `decisions`, K8's duplicate across sets, K20's unit attached to two sets, K18's
abstention, and delegation of another case kind to the lower route.
"""
from __future__ import annotations

import copy
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from tests.subprocesses import HANG_TIMEOUT
from ve.readings_s1 import wire
from ve.wire import digest
from tests.test_norms import environment, obligation, permission

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "lean/.lake/build/bin/ve_readings_route"
SOFT_PROFILES = ("norms@0", "readings@1", "relational-fol@0", "soft-norms@0")


@pytest.fixture(scope="module")
def lean():
    if not LEAN.exists():
        lake = shutil.which("lake")
        if lake is None:
            pytest.skip("lake is required for the readings Lean route")
        built = subprocess.run([lake, "build", "ve_readings_route"], cwd=ROOT / "lean", capture_output=True,
                               text=True, timeout=1800)
        assert built.returncode == 0, built.stdout + built.stderr
    return LEAN


def run(executable, cases):
    # The restricted Lean JSON input has no null: an absent value is omitted, as `ve/readings_route.py` sends it.
    result = subprocess.run([str(executable), "-"], input=json.dumps(wire(cases)), text=True,
                            capture_output=True, timeout=HANG_TIMEOUT)
    assert result.returncode in (0, 1), result.stderr
    rows = json.loads(result.stdout)
    assert len(rows) == len(cases)
    return rows


def env_k(profiles=SOFT_PROFILES):
    predicates = {"asks": {"arguments": ["agent", "user"], "description": "{0} asks {1}"},
                  "avoid_required": obligation("deny", None, act="{0} avoid deceiving {1}", args=("agent", "user")),
                  "help_required": obligation("deny", None, act="{0} help {1}", args=("agent", "user"))}
    raw = environment(predicates, sorts=("agent", "user")).to_dict()
    raw["profiles"] = sorted(profiles)
    return raw


def env_rights():
    predicates = {"arrest_permitted": permission("allow", act="{0} arrest {1}", args=("state", "person")),
                  "arbitrary_arrest": {"arguments": ["state", "person"], "description": "base"},
                  "journalist": {"arguments": ["person"], "description": "base"}}
    raw = environment(predicates, sorts=("state", "person")).to_dict()
    raw["profiles"] = sorted({"norms@0", "readings@1", "relational-fol@0", "rights@0", "soft-norms@0"})
    raw["vocabulary"]["rights"] = {"holders": ["person"], "bearers": ["state", "person"], "protected": [], "alters": {}}
    return raw


def norm_object(name, pred, sign, mode="strict", over=(), guard=("top",)):
    body = {"name": name, "predicate": pred, "sign": sign, "guard": list(guard), "unless": [], "over": list(over)}
    if mode == "default":
        body.update({"mode": "default", "exception": {"decided_by": "unstated", "sufficient": [], "necessary": [],
                                                      "factors": []}})
    return body


def norm(*args, **kwargs):
    return {"norm": norm_object(*args, **kwargs)}


def situation_id(raw, entry):
    ident = "v0.2:" + ",".join(raw["profiles"])
    env_id = digest(f"ve-environment-{ident}\n", raw)
    return digest(f"ve-situation-{ident}\n", {"environment_id": env_id, "situation": entry})


def entry(base, witness, probe, value, fixed=(), decisions=()):
    return {"base": base, "fixed": list(fixed), "witness": witness, "decisions": list(decisions),
            "probe": probe, "value": value}


def reading(rid, content, models, kind="norm"):
    return {"id": rid, "kind": kind, "content": content, "meaning_id": "m",
            "admission": {"who": "w", "why": "y", "distinguishing_models": models}}


def reading_set(sid, unit, readings, situations):
    return {"id": sid, "unit": unit, "version": 1, "status": "open", "readings": readings, "situations": situations}


M0 = {"domains": {"agent": ["a"], "user": ["u"]}, "constants": {}, "relations": {"asks": []}}
Q0 = {"outcome": {"predicate": "avoid_required", "tuple": ["a", "u"]}}
EXCEPTED = {"key": {"excepted": "no-deception"}, "tuples": [["a", "u"]]}


def kind_of(content):
    """The kind of a unit whose content is in force: `asserted` for a formula, else the content's block."""
    return "asserted" if type(content) is list else next(k for k in content if k != "cites")


def k1_document(raw, *, situation=None, fixed_units=(), extra_sets=()):
    sigma = situation or entry(M0, "default", Q0, False, decisions=[EXCEPTED])
    sid = situation_id(raw, sigma)
    rs1 = reading_set("rs1", "u1", [
        reading("strict", norm("no-deception", "avoid_required", True), {"default": sid}),
        reading("default", norm("no-deception", "avoid_required", True, "default"), {"strict": sid})], {sid: sigma})
    units = [{"id": "u1"}] + [{"id": u, "kind": kind_of(c), "content": c} for u, c in fixed_units] + \
        [{"id": s["unit"]} for s in extra_sets]
    return {"units": units, "reading_sets": [rs1, *extra_sets]}, sid


def validate(lean, raw, document):
    return run(lean, [{"id": "v", "kind": "readings-validate", "environment": raw, "document": document}])[0]


def test_k1_separation_keys_and_finding(lean):
    raw = env_k()
    document, sid = k1_document(raw)
    row = validate(lean, raw, document)
    assert row["status"] == "ok", row
    [rs1] = row["sets"]
    strict, default = rs1["candidates"]
    assert strict["owned"] == [] and strict["shared"] == []
    assert default["owned"] == [{"key": {"excepted": "no-deception"}, "name": "soft__excepted__no_deception"}]
    assert rs1["findings"] == ["SeparatedByDecisionOnly: rs1: 0, 1 (not certified)"]
    pair = rs1["pairs"][0]["pair"]
    assert pair == {"situation": sid, "witness": "default", "separated": True, "witness_admissible": True,
                    "witness_value": False, "other_admissible": True, "other_value": True}
    separate = run(lean, [{"id": "s", "kind": "readings-separate", "environment": raw, "document": document,
                           "set": "rs1", "situation": sid, "other": "strict"}])[0]
    assert separate["status"] == "ok" and separate["pair"] == pair


def test_k1_strict_witness_does_not_separate(lean):
    raw = env_k()
    document, _ = k1_document(raw, situation=entry(M0, "strict", Q0, True))
    row = validate(lean, raw, document)
    assert row == {"id": "v", "status": "error", "error": "distinguishing model does not separate readings"}


def test_outcome_probe_through_two_layers(lean):
    """Lean-first plan F5d: a probe whose outcome reads a layer symbol whose meaning reads another one.

    `avoid_required` (the readings) reads `warn_required`, whose fixed rule reads `help_required`, whose fixed rule
    reads the base predicate `asks`. The witness's value is true only when the expansion table expands each
    symbol's meaning under the symbols before it (`expAt_expEntries`). The asserted unit reads `warn_required`, so
    it is typed over the complete environment, which admission computes once per document (`chainText_eq`)."""
    raw = env_k()
    raw["vocabulary"]["predicates"]["warn_required"] = obligation(
        "deny", None, act="{0} warn {1}", args=("agent", "user"))
    asks = ["binary", "asks", ["var", 1], ["var", 0]]
    helps = ["binary", "help_required", ["var", 1], ["var", 0]]
    warns = ["binary", "warn_required", ["var", 1], ["var", 0]]
    base = {**M0, "relations": {"asks": [["a", "u"]]}}
    sigma = entry(base, "nested", Q0, True)
    sid = situation_id(raw, sigma)
    rs1 = reading_set("rs1", "u1", [
        reading("nested", norm("avoid-when-warning", "avoid_required", True, guard=warns), {"never": sid}),
        reading("never", norm("avoid-never", "avoid_required", True, guard=["bottom"]), {"nested": sid})],
        {sid: sigma})
    units = [{"id": "u1"}, {"id": "u2", "kind": "norm", "content": norm("help-when-asked", "help_required", True,
                                                                          guard=asks)},
             {"id": "u3", "kind": "norm", "content": norm("warn-when-helping", "warn_required", True, guard=helps)},
             {"id": "u4", "kind": "asserted", "content": ["forall", "agent", ["forall", "user",
                                                                              ["implies", asks, warns]]]}]
    document = {"units": units, "reading_sets": [rs1]}
    row = validate(lean, raw, document)
    assert row["status"] == "ok", row
    pair = row["sets"][0]["pairs"][0]["pair"]
    assert pair == {"situation": sid, "witness": "nested", "separated": True, "witness_admissible": True,
                    "witness_value": True, "other_admissible": True, "other_value": False}
    separate = run(lean, [{"id": "s", "kind": "readings-separate", "environment": raw, "document": document,
                           "set": "rs1", "situation": sid, "other": "never"}])[0]
    assert separate["status"] == "ok" and separate["pair"] == pair


def test_k2b_base_outside_the_author_vocabulary(lean):
    raw = env_k()
    base = {**M0, "relations": {"asks": [], "soft__excepted__no_deception": [["a", "u"]]}}
    sigma = entry(base, "default", Q0, False, decisions=[EXCEPTED])
    document, sid = k1_document(raw, situation=sigma)
    assert validate(lean, raw, document)["error"] == f"InvalidInput: invalid situation {sid}"


def test_k5_shared_table_and_decisions_it_does_not_own(lean):
    raw = env_k()
    be_kind = ("u0", norm("be-kind", "help_required", True, "default"))
    shared = {"key": {"excepted": "be-kind"}, "tuples": [["a", "u"]]}
    document, _ = k1_document(raw, situation=entry(M0, "default", Q0, False, fixed=[shared], decisions=[EXCEPTED]),
                              fixed_units=[be_kind])
    row = validate(lean, raw, document)
    assert row["status"] == "ok", row
    assert row["sets"][0]["candidates"][1]["shared"] == [{"key": {"excepted": "be-kind"},
                                                          "name": "soft__excepted__be_kind"}]
    document, sid = k1_document(raw, situation=entry(M0, "default", Q0, False, decisions=[shared, EXCEPTED]),
                                fixed_units=[be_kind])
    assert validate(lean, raw, document)["error"] == \
        f"InvalidInput: situation {sid} decides excepted be-kind, which reading default does not own"


def test_k8_duplicate_declaration_across_sets(lean):
    raw = env_k()
    rs2 = reading_set("rs2", "u2", [reading("x", norm("no-deception", "help_required", True), {})], {})
    document, _ = k1_document(raw, extra_sets=[rs2])
    assert validate(lean, raw, document)["error"] == "DuplicateDeclaration: no-deception in reading sets rs1 and rs2"


def test_k20_fixed_unit_attached_to_two_sets(lean):
    raw = env_k()
    sigma2 = entry(M0, "default", {"outcome": {"predicate": "help_required", "tuple": ["a", "u"]}}, False,
                   decisions=[{"key": {"excepted": "be-kind"}, "tuples": [["a", "u"]]}])
    sid2 = situation_id(raw, sigma2)
    rs2 = reading_set("rs2", "u2", [
        reading("strict", norm("be-kind", "help_required", True), {"default": sid2}),
        reading("default", norm("be-kind", "help_required", True, "default"), {"strict": sid2})], {sid2: sigma2})
    asks = ["binary", "asks", ["var", 1], ["var", 0]]
    both = ("u3", norm("both-x", "avoid_required", False, over=("no-deception", "be-kind"), guard=asks))
    document, _ = k1_document(raw, fixed_units=[both], extra_sets=[rs2])
    assert validate(lean, raw, document)["error"] == \
        "UnsupportedProfile: readings@1 fixed unit u3 depends on reading sets rs1 and rs2"
    only = ("u3", norm("both-x", "avoid_required", False, over=("no-deception",), guard=asks))
    document, _ = k1_document(raw, fixed_units=[only], extra_sets=[rs2])
    row = validate(lean, raw, document)
    assert row["status"] == "ok", row
    assert [s["set"] for s in row["sets"]] == ["rs1", "rs2"]


def test_a_third_reading_never_witnesses_a_pair(lean):
    """Review finding A (compose-s1): every pair names a situation whose witness is one of the pair.

    K3's renamed twins are separated by no situation. With K4's `help-x` as a third reading, one situation with
    `help-x` as witness separates `help-x` from each twin; recorded for the twins' own pair it used to be replayed
    as (help-x, twin) and the twins were reported separated."""
    raw = env_k()
    sigma = entry(M0, "help", Q0, False)
    sid = situation_id(raw, sigma)
    others = {"a": ("b", "help"), "b": ("a", "help"), "help": ("a", "b")}
    contents = {"a": norm("no-deception-a", "avoid_required", True),
                "b": norm("no-deception-b", "avoid_required", True),
                "help": norm("help-x", "help_required", True)}
    rs1 = reading_set("rs1", "u1", [reading(r, contents[r], {o: sid for o in others[r]}) for r in others],
                      {sid: sigma})
    row = validate(lean, raw, {"units": [{"id": "u1"}], "reading_sets": [rs1]})
    assert row == {"id": "v", "status": "error", "error": f"InvalidInput: invalid situation {sid}"}
    # The same situation recorded only for pairs it is a witness of is accepted.
    sigma_ab = entry(M0, "a", {"selects": {"kind": "norm", "predicate": "avoid_required", "tuple": ["a", "u"]}},
                     True)
    sid_ab = situation_id(raw, sigma_ab)
    models = {"a": {"b": sid_ab, "help": sid}, "b": {"a": sid_ab, "help": sid}, "help": {"a": sid, "b": sid}}
    rs1 = reading_set("rs1", "u1", [reading(r, contents[r], models[r]) for r in others],
                      {sid: sigma, sid_ab: sigma_ab})
    row = validate(lean, raw, {"units": [{"id": "u1"}], "reading_sets": [rs1]})
    # K3: the twins' own situation separates nothing, so the set is refused for the right reason.
    assert row == {"id": "v", "status": "error", "error": "distinguishing model does not separate readings"}


def test_unit_kinds_decide_what_is_in_force(lean):
    """Review finding B (compose-s1, Fable 3): a unit's kind travels to Lean. A quoted norm, a formula of another
    kind than `asserted` and a composite-kind candidate are not in force, as in Python's W2 loader."""
    raw = env_k()
    never = norm("never-avoid", "avoid_required", False)
    k6 = entry(M0, "default", Q0, False)
    # K6: the fixed strict rule decides under the default reading.
    document, _ = k1_document(raw, situation=k6, fixed_units=[("u0", never)])
    assert validate(lean, raw, document)["status"] == "ok"
    # The same rule quoted (a composite kind) is no rule of the document: the default reading reaches true.
    document["units"][1]["kind"] = ["attributed", "author", "says", "norm"]
    assert validate(lean, raw, document)["error"] == "distinguishing model does not separate readings"
    document["units"][1]["kind"] = "example"
    assert validate(lean, raw, document)["error"] == "distinguishing model does not separate readings"
    # A formula unit is asserted only with kind `asserted` (K12's pair, recorded with `holds`).
    asks_all = ["forall", "agent", ["forall", "user", ["binary", "asks", ["var", 1], ["var", 0]]]]
    sigma = entry(M0, "strict", "holds", True)
    sid = situation_id(raw, sigma)
    rs1 = reading_set("rs1", "u1", [reading("assert", asks_all, {"strict": sid}, kind="asserted"),
                                    reading("strict", norm("no-deception", "avoid_required", True),
                                            {"assert": sid})], {sid: sigma})
    for kind, expected in (("question", "ok"), ("asserted", "error")):
        units = [{"id": "u1"}, {"id": "u0", "kind": kind, "content": ["bottom"]}]
        row = validate(lean, raw, {"units": units, "reading_sets": [rs1]})
        assert row["status"] == expected, (kind, row)
    # A formula candidate of a composite kind is pending: its pair needs no situation.
    hedged = reading("hedged", asks_all, {"strict": "any-token"}, kind=["hedged", "probably", "asserted"])
    rs1 = reading_set("rs1", "u1", [reading("strict", norm("no-deception", "avoid_required", True),
                                            {"hedged": "any-token"}), hedged], {})
    row = validate(lean, raw, {"units": [{"id": "u1"}], "reading_sets": [rs1]})
    assert row["status"] == "ok", row
    assert row["sets"][0]["candidates"][1] == {"id": "hedged", "index": 1, "pending": True}
    assert row["sets"][0]["pairs"] == []
    # A unit with content and no kind is refused rather than guessed.
    document, _ = k1_document(raw, fixed_units=[("u0", never)])
    del document["units"][1]["kind"]
    assert validate(lean, raw, document)["error"] == "InvalidInput: unit kind is required"


def test_k18_norm_defaults_abstention(lean):
    raw = env_k(profiles=("norm-defaults@0", *SOFT_PROFILES))
    document, _ = k1_document(raw)
    assert validate(lean, raw, document)["error"] == \
        "UnsupportedProfile: readings@1 content with norm-defaults@0 is not implemented"


def test_k19_rights_candidates_under_a_fixed_limitation(lean):
    raw = env_rights()
    arbitrary = ["binary", "arbitrary_arrest", ["var", 1], ["var", 0]]

    def claim(mode):
        return {"right": {"name": "r9", "holder": "person", "guard": ["top"], "lines": [
            {"kind": "claim", "norm": norm_object("no-arbitrary-arrest", "arrest_permitted", False, mode,
                                                  guard=arbitrary)}]}}
    base = {"domains": {"state": ["texas"], "person": ["ann", "bob"]}, "constants": {},
            "relations": {"arbitrary_arrest": [["texas", "ann"]], "journalist": []}}
    sigma = entry(base, "default", {"outcome": {"predicate": "arrest_permitted", "tuple": ["texas", "ann"]}}, True,
                  decisions=[{"key": {"excepted": "no-arbitrary-arrest"}, "tuples": [["texas", "ann"]]}])
    sid = situation_id(raw, sigma)
    l29 = {"limitation": {"name": "l29", "scope": "all", "kinds": "all", "decided_by": "unstated", "factors": [],
                          "conditions": [
                              {"name": "determined_by_law", "role": "necessary", "decided_by": None,
                               "verbalisation": "the limitation is determined by law"},
                              {"name": "solely_for_permitted_purpose", "role": "necessary", "decided_by": None,
                               "verbalisation": "the limitation is solely for a permitted purpose"}]}}
    rs9 = reading_set("rs9", "u9", [reading("strict", claim("strict"), {"default": sid}, kind="right"),
                                    reading("default", claim("default"), {"strict": sid}, kind="right")],
                      {sid: sigma})
    row = validate(lean, raw, {"units": [{"id": "u9"}, {"id": "u29", "kind": "limitation", "content": l29}], "reading_sets": [rs9]})
    assert row["status"] == "ok", row
    [rs] = row["sets"]
    strict, default = rs["candidates"]
    assert [k["key"] for k in strict["shared"]] == [
        {"lim": "l29", "act": "arrest_permitted"},
        {"cond": "l29", "act": "arrest_permitted", "condition": "determined_by_law"},
        {"cond": "l29", "act": "arrest_permitted", "condition": "solely_for_permitted_purpose"}]
    assert strict["owned"] == [] and strict["findings"] == []
    assert default["findings"] == ["UnlicensedLimitation: exception of rule no-arbitrary-arrest on right r9"
                                   " under rs9@1:1"]
    assert rs["findings"] == ["SeparatedByDecisionOnly: rs9: 0, 1 (not certified)"]
    assert rs["pairs"][0]["pair"]["separated"] is True


ARBITRARY = ["binary", "arbitrary_arrest", ["var", 1], ["var", 0]]
R9_BASE = {"domains": {"state": ["texas"], "person": ["ann", "bob"]}, "constants": {},
           "relations": {"arbitrary_arrest": [["texas", "ann"]], "journalist": []}}


def r9_line(mode, name="no-arbitrary-arrest", guard=ARBITRARY, **fields):
    return {"kind": "claim", "norm": norm_object(name, "arrest_permitted", False, mode, guard=guard), **fields}


def r9_right(lines, **fields):
    return {"right": {"name": "r9", "holder": "person", "guard": ["top"], "lines": lines, **fields}}


def rs9(raw, strict, default=None):
    """K22's set: right r9 with a strict and a default claim line, the default's witness situation recorded."""
    sigma = entry(R9_BASE, "default", {"outcome": {"predicate": "arrest_permitted", "tuple": ["texas", "ann"]}},
                  True, decisions=[{"key": {"excepted": "no-arbitrary-arrest"}, "tuples": [["texas", "ann"]]}])
    sid = situation_id(raw, sigma)
    return reading_set("rs9", "u9", [
        reading("strict", strict, {"default": sid}, kind="right"),
        reading("default", default or r9_right([r9_line("default")]), {"strict": sid}, kind="right")], {sid: sigma})


def agreed(lean, raw, document):
    """Lean's row, after checking that the route relays it: the row itself, or its diagnostic with Lean's text
    (lean-first batch 3: no Python regeneration is compared with it)."""
    row = {k: v for k, v in validate(lean, raw, document).items() if k != "id"}
    assert _route(raw, document, None) == row
    return row


def test_line_order_lists_each_line_once(lean):
    """DRI ruling 1 (review finding B): S1 admission refuses a candidate's document whose line order repeats an
    entry, with one stable text, and an entry that is no line of its right with the rights decoder's
    `UnknownRight` (a `right_lines` unit before its right). `genKeys_nodup` takes this check as its hypothesis."""
    raw = env_rights()
    row = agreed(lean, raw, {"units": [{"id": "u9"}], "reading_sets": [rs9(raw, r9_right([r9_line("strict")]))]})
    assert row["status"] == "ok", row
    row = agreed(lean, raw, {"units": [{"id": "u9"}],
                             "reading_sets": [rs9(raw, r9_right([r9_line("strict"), r9_line("strict")]))]})
    assert row["error"] == "InvalidInput: line order lists a line of right r9 twice under rs9@1:0"
    # A fixed `right_lines` unit before the candidates' right: its line is in the order and in no right.
    journalist = ["unary", "journalist", ["var", 0]]
    extra = {"right_lines": {"right": "r9", "lines": [r9_line("strict", "no-detention", journalist)]}}
    row = agreed(lean, raw, {"units": [{"id": "u1", "kind": "right_lines", "content": extra}, {"id": "u9"}],
                             "reading_sets": [rs9(raw, r9_right([r9_line("strict")]))]})
    assert row["error"] == "UnknownRight: r9 under rs9@1:0"
    # After the right, the same unit is a line of it.
    row = agreed(lean, raw, {"units": [{"id": "u9"}, {"id": "u1", "kind": "right_lines", "content": extra}],
                             "reading_sets": [rs9(raw, r9_right([r9_line("strict")]))]})
    assert row["status"] == "ok", row


SAME_LINE = {
    # Review finding B (compose-s1-looprecheck1): the second line differs only by `cites: {}`.
    "empty cites": r9_line("strict", cites={}),
    "empty fan_out": r9_line("strict", fan_out={}),
    "keys reordered": dict(reversed(list(r9_line("strict").items()))),
    **{f"norm {k}": {**r9_line("strict"), "norm": {**r9_line("strict")["norm"], k: v}}
       for k, v in (("mode", "strict"), ("alterable", []), ("hard", False), ("rank", None))},
}


@pytest.mark.parametrize("variant", sorted(SAME_LINE))
def test_line_order_compares_lines_decoded(lean, variant):
    """Lean's line order holds decoded lines (`SourceLine`): a line written again with a default field spelled
    out is the same line listed twice, and the route says so with Lean's text."""
    raw = env_rights()
    document = {"units": [{"id": "u9"}],
                "reading_sets": [rs9(raw, r9_right([r9_line("strict"), SAME_LINE[variant]]))]}
    row = agreed(lean, raw, document)
    assert row["error"] == "InvalidInput: line order lists a line of right r9 twice under rs9@1:0"


TWIN_STRICT = {
    "empty cites": r9_right([r9_line("strict", cites={})]),
    "empty fan_out": r9_right([r9_line("strict", fan_out={})]),
    "norm hard": r9_right([{**r9_line("strict"), "norm": {**r9_line("strict")["norm"], "hard": False}}]),
    "no guard": {"right": {k: v for k, v in r9_right([r9_line("strict")])["right"].items() if k != "guard"}},
}


@pytest.mark.parametrize("variant", sorted(TWIN_STRICT))
def test_force_twins_compare_contents_decoded(lean, variant):
    """`forceTwins` (1.7) compares decoded contents: the strict right written with a default spelled out (or the
    guard left to its default `top`) is still the default right's twin, and both report the finding."""
    raw = env_rights()
    row = agreed(lean, raw, {"units": [{"id": "u9"}], "reading_sets": [rs9(raw, TWIN_STRICT[variant])]})
    assert row["status"] == "ok", row
    assert row["sets"][0]["findings"] == ["SeparatedByDecisionOnly: rs9: 0, 1 (not certified)"]


LIMITATION = {"name": "l29", "scope": ["r9"], "kinds": "all", "decided_by": "unstated", "factors": [],
              "conditions": [{"name": "determined_by_law", "role": "necessary",
                              "verbalisation": "the limitation is determined by law"}]}
DEFAULTED_UNITS = {
    "condition without decider": ({"limitation": LIMITATION}, "ok"),
    "limitation without decider": ({"limitation": {k: v for k, v in LIMITATION.items() if k != "decided_by"}},
                                   "MissingExceptionDecider: limitation l29 under rs9@1:0"),
    "bar without decider": ({"bar": {"name": "b30", "reading": "rule"}}, "ok"),
    "bar with null decider": ({"bar": {"name": "b30", "reading": "rule", "decided_by": None}}, "ok"),
}


@pytest.mark.parametrize("variant", sorted(DEFAULTED_UNITS))
def test_rights_units_read_with_lean_defaults(lean, variant):
    """A field Lean's rights decoder reads as optional (absent and null alike on its wire): an absent decider
    inherits, is missing, or (a bar's) is accepted, as Lean decides, and the route relays it."""
    raw = env_rights()
    content, expected = DEFAULTED_UNITS[variant]
    kind = next(iter(content))
    row = agreed(lean, raw, {"units": [{"id": "u9"}, {"id": "u29", "kind": kind, "content": content}],
                             "reading_sets": [rs9(raw, r9_right([r9_line("strict")]))]})
    assert row.get("error", row["status"]) == expected, row


def _with_norm(line, **fields):
    return {**line, "norm": {**line["norm"], **fields}}


EXPLICIT_NULL_RIGHTS = {
    # Review finding B (compose-s1-looprecheck2): `cites: null` on a right's line.
    "line cites": r9_right([r9_line("strict", cites=None)]),
    "line fan_out": r9_right([r9_line("strict", fan_out=None)]),
    "line holder_slot": r9_right([r9_line("strict", holder_slot=None)]),
    "line liberty": r9_right([r9_line("strict", liberty=None)]),
    "right guard": r9_right([r9_line("strict")], guard=None),
    **{f"norm {k}": r9_right([_with_norm(r9_line("strict"), **{k: None})])
       for k in ("mode", "hard", "alterable", "rank", "exception")},
}


@pytest.mark.parametrize("variant", sorted(EXPLICIT_NULL_RIGHTS))
def test_explicit_null_is_absent_in_rights_candidates(lean, variant):
    """Lean's input has no null (`wire` omits it), so an explicit null is the field's default to Lean: the
    candidate is admitted, and the route relays the answer."""
    raw = env_rights()
    row = agreed(lean, raw, {"units": [{"id": "u9"}], "reading_sets": [rs9(raw, EXPLICIT_NULL_RIGHTS[variant])]})
    assert row["status"] == "ok", row
    assert row["sets"][0]["findings"] == ["SeparatedByDecisionOnly: rs9: 0, 1 (not certified)"]


EXPLICIT_NULL_SOFT = [(i, k) for i in (0, 1) for k in ("mode", "hard", "alterable", "rank", "cites")
                      if (i, k) != (1, "mode")]


@pytest.mark.parametrize("index,field", EXPLICIT_NULL_SOFT)
def test_explicit_null_is_absent_in_soft_contents(lean, index, field):
    """Review finding B (compose-s1-looprecheck2): `mode: null` on a soft norm, and `hard`, `alterable`, `rank`
    and a content's `cites` alike, in a candidate (strict 0, default 1) and in a fixed unit."""
    raw = env_k()
    document, _ = k1_document(raw)
    content = document["reading_sets"][0]["readings"][index]["content"]
    (content if field == "cites" else content["norm"])[field] = None
    assert agreed(lean, raw, document)["status"] == "ok"
    body = norm_object("be-kind", "help_required", True, "default")
    fixed = {"norm": body, "cites": None} if field == "cites" else {"norm": {**body, field: None}}
    if field == "mode":
        fixed = {"norm": {**norm_object("be-kind", "help_required", True), "mode": None}}
    document, _ = k1_document(raw, fixed_units=[("u0", fixed)])
    assert agreed(lean, raw, document)["status"] == "ok"


def test_explicit_null_on_the_norms_chain(lean):
    """On the norms chain (W1's decoder) a null soft field is absent too: the answer is the one without it."""
    raw = env_k(profiles=("norms@0", "readings@1", "relational-fol@0"))
    document, _ = k1_document(raw)
    for r in document["reading_sets"][0]["readings"]:
        r["content"]["norm"].pop("mode", None)
        r["content"]["norm"].pop("exception", None)
    plain = agreed(lean, raw, document)
    for r in document["reading_sets"][0]["readings"]:
        r["content"]["norm"].update({"mode": None, "hard": None, "alterable": None, "rank": None})
    assert agreed(lean, raw, document) == plain
    assert not plain.get("error", "").startswith("fields do not match"), plain


K1_SOFT_BLOCK = {"parties": ["operator", "user"], "ranks": ["helpfulness"], "outranks": [], "ties": [],
                 "outranking": {"mode": "strict"}}


def _k1_soft_block():
    raw = env_k()
    raw["vocabulary"]["soft"] = copy.deepcopy(K1_SOFT_BLOCK)
    return raw


def _k1_norms():
    return env_k(profiles=("norms@0", "readings@1", "relational-fol@0"))


def _k1_norms_document(raw):
    document, _ = k1_document(raw)
    for r in document["reading_sets"][0]["readings"]:
        r["content"]["norm"].pop("mode", None)
        r["content"]["norm"].pop("exception", None)
    return document


NULL_ENVIRONMENTS = {
    # name: (environment, its document from the environment, the kind of the open set's unit)
    "soft": (env_k, lambda raw: k1_document(raw)[0], "norm"),
    "soft block": (_k1_soft_block, lambda raw: k1_document(raw)[0], "norm"),
    "norms": (_k1_norms, _k1_norms_document, "norm"),
    "rights": (env_rights, lambda raw: {"units": [{"id": "u9"}],
                                        "reading_sets": [rs9(raw, r9_right([r9_line("strict")]))]}, "right"),
}
# Optional environment fields the environments above leave out, written as null.
OPTIONAL_ENVIRONMENT_FIELDS = [("vocabulary", "soft"), ("vocabulary", "rights"),
                               ("vocabulary", "predicates", "asks", "regulated"),
                               ("vocabulary", "predicates", "asks", "instruction_of"),
                               ("vocabulary", "predicates", "arbitrary_arrest", "regulated"),
                               ("vocabulary", "predicates", "avoid_required", "instruction_of"),
                               ("vocabulary", "predicates", "arrest_permitted", "instruction_of")]


def _fields(value, path=()):
    """Every field of a JSON object at every depth, as a path of keys."""
    if type(value) is dict:
        for key, item in value.items():
            yield (*path, key)
            yield from _fields(item, (*path, key))
    elif type(value) is list:
        for index, item in enumerate(value):
            yield from _fields(item, (*path, index))


def _nulled(raw, path):
    """`raw` with the field at `path` written as null, or None when its parent is not an object."""
    raw = copy.deepcopy(raw)
    parent = raw
    for key in path[:-1]:
        if type(parent) is dict and key in parent or type(parent) is list and type(key) is int:
            parent = parent[key]
        else:
            return None
    if type(parent) is not dict:
        return None
    parent[path[-1]] = None
    return raw


ENVIRONMENT_NULLS = [(name, path) for name, (make, _, _) in NULL_ENVIRONMENTS.items()
                     for path in [*_fields(make()), *(p for p in OPTIONAL_ENVIRONMENT_FIELDS
                                                      if _nulled(make(), p) is not None
                                                      and p not in set(_fields(make())))]]


def _known_text_difference(name, path):
    """The cases whose environment, without the field, Lean and Python's regeneration refused with different texts,
    so that the route was `CheckerUnavailable` on them until lean-first batch 3 deleted the regeneration: a required
    field missing (the environment decoders' texts differed: `fields do not match` against `Incorrect fields`,
    `invalid signature` against `Undeclared predicate argument sort`), and a candidate's content made ill-typed by
    the environment (Lean's content decoder refuses it before any candidate label, or with its code). The route now
    raises Lean's diagnostic on each (`docs/lean-first/b3/DELTA.md`, `availability`); Lean refuses every one."""
    required = (path[-1] in ("arguments", "description") or path[:2] == ("vocabulary", "sorts") and len(path) == 3
                or name == "norms" and len(path) <= 2 and path not in (("profiles",), ("vocabulary", "soft"),
                                                                       ("vocabulary", "rights"))
                or name == "rights" and path == ("vocabulary",))
    ill_typed = path in (("vocabulary", "predicates", "avoid_required"),
                         ("vocabulary", "predicates", "avoid_required", "regulated")) and name != "norms"
    return required or ill_typed


def _route(lean_path_environment, document, unit_kind):
    """The route's outcome: Lean's row, its diagnostic, or the name of an operational failure."""
    from ve.errors import CheckerUnavailable, VEError
    from ve.readings_route import validate as route_validate
    units = [{"id": u["id"], "kind": u.get("kind", unit_kind), **({"content": u["content"]} if "content" in u else {})}
             for u in document["units"]]
    try:
        row = route_validate(lean_path_environment, units, document["reading_sets"])
    except CheckerUnavailable:
        return "CheckerUnavailable"
    except VEError as exc:
        return {"status": "error", "error": exc.message if hasattr(exc, "message") else str(exc)}
    return {k: v for k, v in row.items() if k != "id"}


@pytest.mark.parametrize("name,path", ENVIRONMENT_NULLS, ids=lambda v: v if type(v) is str else ".".join(map(str, v)))
def test_explicit_null_is_absent_in_the_environment(lean, name, path):
    """Review finding B (compose-s1-loop): each field of each environment, at every depth, and each optional field
    it leaves out, written as null, is the field absent to Lean and to the route (`ve/readings_route.py`), and the
    route answers Lean's row or raises Lean's diagnostic. The class covers `vocabulary.rights.protected` and
    `alters`, a null `profiles` (Lean's text) and a right's line on a predicate whose `regulated` is null (Lean's
    `UnknownSymbol`). The cases Python's regeneration once refused with another text are refused by Lean."""
    from ve.errors import VEError
    make, make_document, unit_kind = NULL_ENVIRONMENTS[name]
    nulled = _nulled(make(), path)
    absent = wire(nulled)
    # The situation ids are over the environment Lean receives, the one without the null; when that environment
    # has no id (no profiles, say), over the environment as made.
    try:
        document = make_document(absent)
    except (KeyError, TypeError, ValueError, VEError):
        document = make_document(make())
    row = {k: v for k, v in validate(lean, nulled, document).items() if k != "id"}
    assert row == {k: v for k, v in validate(lean, absent, document).items() if k != "id"}
    routed = _route(nulled, document, unit_kind)
    assert routed == _route(absent, document, unit_kind)
    assert routed == row
    if _known_text_difference(name, path):
        assert row["status"] == "error", row


def test_a_text_that_differed_only_by_the_code_prefix_gets_leans_diagnostic(lean):
    """Lean-first batch 0, `DELTA.md` A1 (`availability`): the rights document over an environment without
    `arbitrary_arrest` was `CheckerUnavailable` on the route, Python writing `Unknown predicate ...` and Lean
    `UnknownSymbol: Unknown predicate ...`. Python's text is Lean's now, so the route rejects with it."""
    make, make_document, unit_kind = NULL_ENVIRONMENTS["rights"]
    absent = wire(_nulled(make(), ("vocabulary", "predicates", "arbitrary_arrest")))
    document = make_document(make())
    text = "UnknownSymbol: Unknown predicate 'arbitrary_arrest' under rs9@1:0"
    assert {k: v for k, v in validate(lean, absent, document).items() if k != "id"} == {"status": "error",
                                                                                       "error": text}
    assert _route(absent, document, unit_kind) == {"status": "error", "error": text}


def test_environment_nulls_cover_the_reported_fields():
    """The fields of the finding are among the cases, and agree: `vocabulary.soft` and `vocabulary.rights` on K1."""
    for case in (("soft", ("vocabulary", "soft")), ("soft", ("vocabulary", "rights")),
                 ("rights", ("vocabulary", "rights", "protected")), ("rights", ("vocabulary", "rights", "alters")),
                 ("soft", ("profiles",)), ("rights", ("vocabulary", "predicates", "arrest_permitted", "regulated"))):
        assert case in ENVIRONMENT_NULLS


def test_other_kinds_go_to_the_lower_route(lean):
    raw = env_k()
    row = run(lean, [{"id": "e", "kind": "soft-elaborate", "environment": raw,
                      "norms": [norm("no-deception", "avoid_required", True, "default")]}])[0]
    assert row["status"] == "ok", row
