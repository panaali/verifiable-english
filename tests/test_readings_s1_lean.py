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

import json
import shutil
import subprocess
from pathlib import Path

import pytest

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
    result = subprocess.run([str(executable), "-"], input=json.dumps(cases), text=True,
                            capture_output=True, timeout=180)
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
    raw["vocabulary"]["rights"] = {"holders": ["person"], "bearers": ["state", "person"]}
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
        return {"right": {"name": "r9", "holder": "person", "lines": [
            {"kind": "claim", "norm": norm_object("no-arbitrary-arrest", "arrest_permitted", False, mode,
                                                  guard=arbitrary)}]}}
    base = {"domains": {"state": ["texas"], "person": ["ann", "bob"]}, "constants": {},
            "relations": {"arbitrary_arrest": [["texas", "ann"]], "journalist": []}}
    sigma = entry(base, "default", {"outcome": {"predicate": "arrest_permitted", "tuple": ["texas", "ann"]}}, True,
                  decisions=[{"key": {"excepted": "no-arbitrary-arrest"}, "tuples": [["texas", "ann"]]}])
    sid = situation_id(raw, sigma)
    l29 = {"limitation": {"name": "l29", "scope": "all", "kinds": "all", "decided_by": "unstated", "factors": [],
                          "conditions": [
                              {"name": "determined_by_law", "role": "necessary",
                               "verbalisation": "the limitation is determined by law"},
                              {"name": "solely_for_permitted_purpose", "role": "necessary",
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


def test_line_order_lists_each_line_once(lean):
    """DRI ruling 1 (review finding B): S1 admission refuses a candidate's document whose line order repeats an
    entry, with one stable text, and an entry that is no line of its right with the rights decoder's
    `UnknownRight` (a `right_lines` unit before its right). `genKeys_nodup` takes this check as its hypothesis."""
    raw = env_rights()
    arbitrary = ["binary", "arbitrary_arrest", ["var", 1], ["var", 0]]

    def line(mode, name="no-arbitrary-arrest", guard=arbitrary):
        return {"kind": "claim", "norm": norm_object(name, "arrest_permitted", False, mode, guard=guard)}

    base = {"domains": {"state": ["texas"], "person": ["ann", "bob"]}, "constants": {},
            "relations": {"arbitrary_arrest": [["texas", "ann"]], "journalist": []}}
    sigma = entry(base, "default", {"outcome": {"predicate": "arrest_permitted", "tuple": ["texas", "ann"]}}, True,
                  decisions=[{"key": {"excepted": "no-arbitrary-arrest"}, "tuples": [["texas", "ann"]]}])
    sid = situation_id(raw, sigma)

    def rs9(strict_lines):
        return reading_set("rs9", "u9", [
            reading("strict", {"right": {"name": "r9", "holder": "person", "lines": strict_lines}},
                    {"default": sid}, kind="right"),
            reading("default", {"right": {"name": "r9", "holder": "person", "lines": [line("default")]}},
                    {"strict": sid}, kind="right")], {sid: sigma})

    row = validate(lean, raw, {"units": [{"id": "u9"}], "reading_sets": [rs9([line("strict")])]})
    assert row["status"] == "ok", row
    row = validate(lean, raw, {"units": [{"id": "u9"}], "reading_sets": [rs9([line("strict"), line("strict")])]})
    assert row["error"] == "InvalidInput: line order lists a line of right r9 twice under rs9@1:0"
    # A fixed `right_lines` unit before the candidates' right: its line is in the order and in no right.
    journalist = ["unary", "journalist", ["var", 0]]
    extra = {"right_lines": {"right": "r9", "lines": [line("strict", "no-detention", journalist)]}}
    row = validate(lean, raw, {"units": [{"id": "u1", "kind": "right_lines", "content": extra}, {"id": "u9"}],
                               "reading_sets": [rs9([line("strict")])]})
    assert row["error"] == "UnknownRight: r9 under rs9@1:0"
    # After the right, the same unit is a line of it.
    row = validate(lean, raw, {"units": [{"id": "u9"}, {"id": "u1", "kind": "right_lines", "content": extra}],
                               "reading_sets": [rs9([line("strict")])]})
    assert row["status"] == "ok", row


def test_other_kinds_go_to_the_lower_route(lean):
    raw = env_k()
    row = run(lean, [{"id": "e", "kind": "soft-elaborate", "environment": raw,
                      "norms": [norm("no-deception", "avoid_required", True, "default")]}])[0]
    assert row["status"] == "ok", row
