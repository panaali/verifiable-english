"""S2a through the document path (docs/spec/composition-s2.md 1.1, 4, 6, 9): the route, the refusals before any
verdict, the verdicts across readings and the report, on documents written to disk.

`data/readings_s2/constitution-nd-readings.ve.md` is the constitution pilot's case of DRI ruling 4 (run
20261003T0600Z, `probes/s1-probe.json` (a)): the pilot's own environment (`norm-defaults@0`, with `readings@1` added),
its claim graph, the force set `force-u0036-s05` with its two `content: null` candidates re-identified under the new
environment, and five of its units (the set's sentence, three rules, the graph's claim). The pilot reported it
refused with `UnsupportedProfile: readings@1 requires norms@0`, which is false of the document.
"""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest

from ve.document import _environment, check_document
from ve.errors import VEError

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "tests/data/readings_s2/constitution-nd-readings.ve.md"
ABSTENTION = "UnsupportedProfile: readings@1 content with norm-defaults@0 is not implemented"


def _split(path):
    data = Path(path).read_bytes()
    end = data.index(b"\n---\n", 4)
    return json.loads(data[4:end]), data[end + 5:]


def _write(tmp_path, name, meta, rest):
    path = tmp_path / name
    path.write_bytes(b"---\n" + json.dumps(meta, ensure_ascii=False).encode() + b"\n---\n" + rest)
    return path


def _reidentified(env, item):
    spec = importlib.util.spec_from_file_location("readings_s1_pilot", ROOT / "tools/readings_s1_pilot.py")
    pilot = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pilot)
    return pilot._reidentified(env, item)


def test_ruling4_pilot_document_with_readings_and_norm_defaults_loads():
    """No set is content-bearing, so the document is W2's (1.1 row 1) and validates as without `readings@1`."""
    report = check_document(PILOT)
    assert report["admission"]["admitted"] is True
    assert report["premises"] == {"status": "UNKNOWN", "reason": "non-assertion reading elaboration pending"}
    assert "readings" not in report  # no content-bearing set: S1's and S2's blocks are not reached


def test_ruling4_pilot_document_answers_as_without_readings(tmp_path):
    meta, rest = _split(PILOT)
    plain = copy.deepcopy(meta)
    plain["environment"]["profiles"] = [p for p in plain["environment"]["profiles"] if p != "readings@1"]
    env = _environment(plain["environment"])
    plain["reading_sets"] = [_reidentified(env, item) for item in plain["reading_sets"]]
    without = check_document(_write(tmp_path, "plain.ve.md", plain, rest))
    with_readings = check_document(PILOT)
    for key in ("premises", "reading_plan", "stale_reading_labels"):
        assert with_readings[key] == without[key], key
    assert with_readings["admission"]["report"] == without["admission"]["report"]


def test_ruling4_rule_candidate_beside_norm_defaults_is_the_named_abstention(tmp_path):
    """The pilot's probe (b): a strict rule as one candidate's content. Lean and Python now both reach S1's
    abstention (before: Lean `invalid regulated role or default`, Python `unspecified completion requires
    norm-defaults@0`, so `CheckerUnavailable`)."""
    meta, rest = _split(PILOT)
    reading_set = meta["reading_sets"][0]
    reading_set.pop("models", None)
    env = _environment(meta["environment"])
    from ve.readings import s1_content_meaning_id
    rule = {"norm": {"name": "clarify-ambiguity", "predicate": "clarification_required", "sign": True,
                     "guard": ["unary", "genuine_ambiguity", ["var", 0]], "unless": [], "over": []}}
    strict = next(r for r in reading_set["readings"] if r["id"] == "strict")
    strict["content"] = rule
    strict["meaning_id"] = s1_content_meaning_id(env, reading_set["id"], strict)
    for r in reading_set["readings"]:
        r["admission"]["distinguishing_models"] = {o: "pending" for o in r["admission"]["distinguishing_models"]}
    with pytest.raises(VEError) as caught:
        check_document(_write(tmp_path, "rule.ve.md", meta, rest))
    assert caught.value.message == ABSTENTION


def test_ruling4_lean_frame_reads_unspecified_as_deny(lean_route):
    """Lean's decoder and Python's S1 environment agree on a `norm-defaults@0` frame: `unspecified` is the
    placeholder `deny` there (E‴), so readings-validate answers instead of failing to decode."""
    from ve.readings_route import document_wire, run_lean
    from ve.readings_s1 import S1Environment
    meta, _ = _split(PILOT)
    senv = S1Environment(meta["environment"])
    assert senv.frame.predicates["clarification_required"].regulated.default == "deny"
    units = [{"id": u["id"], "kind": u["kind"], "content": None} for u in meta["units"]]
    [row] = run_lean([{"id": "v", "kind": "readings-validate", "environment": meta["environment"],
                       "document": document_wire(units, meta["reading_sets"])}], executable=lean_route)
    assert row["status"] == "ok" and row["content_bearing"] is False, row


@pytest.fixture
def lean_route():
    from ve.readings_route import LEAN_ROUTE
    if not LEAN_ROUTE.exists():
        pytest.skip("ve_readings_route is not built")
    return LEAN_ROUTE


# ---------------------------------------------------------------------------------------------------------------
# The verdicts across readings (review B3 of 2026-10-03): 4.5 and 4.6 on the fixtures of 9.2, through the document
# path, every verdict from evidence Lean's readings route checked.

from tests.test_document import unit, write_doc  # noqa: E402
from tests.test_norms import environment, obligation  # noqa: E402
from tests.test_readings_s1_lean import SOFT_PROFILES, env_k, env_rights, norm, norm_object  # noqa: E402
from ve.document import load_document  # noqa: E402

ASKS = ["binary", "asks", ["var", 1], ["var", 0]]


def every(predicate, negated=False, guard=None):
    atom = ["binary", predicate, ["var", 1], ["var", 0]]
    body = ["not", atom] if negated else atom
    if guard is not None:
        body = ["implies", guard, body]
    return ["forall", "agent", ["forall", "user", body]]


def candidate(env, set_id, cid, content, kind="norm", labels=None):
    from ve.ast import formula_from_data
    from ve.identity import meaning_id
    from ve.readings import s1_content_meaning_id
    reading = {"id": cid, "kind": kind, "content": content}
    mid = (s1_content_meaning_id(env, set_id, reading) if kind != "asserted"
           else meaning_id(env, formula_from_data(env, content)))
    out = {**reading, "meaning_id": mid, "admission": {"who": "reviewer", "why": "two readings",
                                                      "distinguishing_models": {}}}
    if labels:
        out["labels"] = labels
    return out


def s2_document(tmp_path, items, *, raw=None, couplings=(), narrowings=(), name="s2.ve.md"):
    """A document of `items` in source order: `("set", set_id, unit_id, [(cid, content, kind, labels), ...])` or
    `("fixed", unit_id, content)`. Every pair's situation is Python's search result, recorded set by set."""
    from ve.readings_route import document_wire
    from ve.readings_s1 import record_situations, search
    from ve.softnorms import SoftEnvironment
    raw = raw or env_k()
    env = _environment(raw)
    units, sets, text = [], [], b""
    for item in items:
        sentence = f"Sentence {len(units) + 1} applies.\n".encode()
        if item[0] == "set":
            _, set_id, uid, cands = item
            readings = [candidate(env, set_id, cid, content, kind, labels) for cid, content, kind, labels in cands]
            for reading in readings:
                reading["admission"]["distinguishing_models"] = {r["id"]: "pending" for r in readings
                                                                 if r["id"] != reading["id"]}
            sets.append({"id": set_id, "unit": uid, "version": 1, "status": "open", "readings": readings})
            units.append(unit(uid, len(text), len(text) + len(sentence), "norm", "specified"))
        else:
            _, uid, content = item
            kind = "asserted" if type(content) is list else next(k for k in content if k != "cites")
            units.append(unit(uid, len(text), len(text) + len(sentence), kind, "specified",
                              {"ast": content} if type(content) is list else content))
        text += sentence
    wire_units = [{"id": u["id"], "kind": u["kind"],
                   "content": u["content"]["ast"] if type(u["content"]) is dict and "ast" in u["content"]
                   else u["content"]} for u in units]
    for k, reading_set in enumerate(sets):
        found = search(raw, document_wire(wire_units, sets), reading_set["id"])
        sets[k] = record_situations(reading_set, {key: v for key, v in found.items() if v is not None})
    extra = {}
    if couplings:
        extra["couplings"] = list(couplings)
    if narrowings:
        extra["narrowings"] = list(narrowings)
    path = tmp_path / name
    path.parent.mkdir(exist_ok=True)
    return write_doc(path.parent, text, units, environment_json=raw, reading_sets=sets, **extra).rename(path)


S = ("strict", norm("no-deception", "avoid_required", True), "norm", None)
DF = ("default", norm("no-deception", "avoid_required", True, "default"), "norm", None)
HELP_X = norm("help-x", "help_required", True)
NEVER_AVOID = norm("never-avoid", "avoid_required", False)


def verdicts(path):
    from ve.readings_verdicts import context
    return context(load_document(path))


def test_m4_conflict_free_all_and_some_through_lean(tmp_path):
    path = s2_document(tmp_path, [("set", "rs1", "u1", [S, DF]), ("fixed", "u0", HELP_X)])
    report = check_document(path)
    assert report["premises"]["status"] == "model" and report["premises"]["route"] == "superposed"
    assert [c["status"] for c in report["premises"]["candidates"]] == ["model", "model"]
    readings = report["readings"]
    assert readings["conflict"]["status"] == "CONFLICT-FREE"
    assert readings["status"].startswith("CONFLICT-FREE among rules on the same act")
    assert readings["dead_readings"] == []
    route = verdicts(path)
    assert route.entailment(every("help_required"))["verdict"] == "ALL"
    some = route.entailment(every("avoid_required"))
    assert some["verdict"] == "SOME"
    assert some["proof"]["choice"] == [["rs1", 0]] and some["countermodel"]["choice"] == [["rs1", 1]]
    assert route.entailment(every("avoid_required"), assumed=[("rs1", 0)])["verdict"] == "ALL"
    assert route.entailment(every("avoid_required"), assumed=[("rs1", 1)])["verdict"] == "NOT ALL"


def test_m3_conflict_witness_names_the_reading(tmp_path):
    path = s2_document(tmp_path, [("set", "rs1", "u1", [S, DF]), ("fixed", "u0", NEVER_AVOID)])
    route = verdicts(path)
    conflict = route.conflict(())
    assert conflict["status"] == "CONFLICT" and conflict["choice"] == [["rs1", 0]], conflict
    assert conflict["target"] == "avoid_required"
    assert route.conflict([("rs1", 1)])["status"] == "CONFLICT-FREE"
    # Under every reading every entailment waits for the conflict status (14.8); under *should* it is certified.
    assert route.entailment(every("avoid_required", negated=True)) == {
        "verdict": "UNKNOWN", "route": "superposed", "status": "UNKNOWN (conflict status: CONFLICT)",
        "conflict_status": "CONFLICT"}
    assert route.entailment(every("avoid_required", negated=True), assumed=[("rs1", 1)])["verdict"] == "ALL"
    assert check_document(path)["readings"]["status"].startswith("CONFLICT: strict collision on avoid_required")


def test_m5_narrowing_premise_and_no_dead_reading(tmp_path):
    narrowing = {"id": "n1", "set": "rs1", "version": 1, "keeps": ["strict"], "by": "reviewer",
                 "reason_spans": ["u2"]}
    path = s2_document(tmp_path, [("set", "rs1", "u1", [S, DF]), ("fixed", "u0", HELP_X),
                                  ("fixed", "u2", ["top"])], narrowings=[narrowing])
    route = verdicts(path)
    result = route.entailment(every("avoid_required"))
    assert result["verdict"] == "ALL" and "narrowing:n1" in result["conditional_on"], result
    report = check_document(path)
    assert report["readings"]["dead_readings"] == []
    assert [(c["index"], c["status"]) for c in report["premises"]["candidates"]] == [(0, "model"), (1, "narrowed")]


def _m6(tmp_path, narrowings=()):
    probe_unit = ("fixed", "u2", ["top"])
    s2 = ("strict", norm("be-kind", "help_required", True), "norm", {"force": "strict"})
    d2 = ("default", norm("be-kind", "help_required", True, "default"), "norm", {"force": "default"})
    coupling = {"id": "c1", "axis": "force", "sets": [{"set": "rs1", "version": 1}, {"set": "rs2", "version": 1}],
                "by": "reviewer", "reason_spans": ["u1"]}
    return s2_document(tmp_path, [("set", "rs1", "u1", [(*S[:3], {"force": "strict"}), (*DF[:3], {"force": "default"})]),
                                  ("set", "rs2", "u3", [s2, d2]), probe_unit],
                       couplings=[coupling], narrowings=narrowings)


def test_m6_dead_reading_certified_by_lean(tmp_path):
    """Fable B2: `dead_readings` is computed and certified, never a hard-coded empty list."""
    assert check_document(_m6(tmp_path))["readings"]["dead_readings"] == []
    narrowing = {"id": "n1", "set": "rs1", "version": 1, "keeps": ["strict"], "by": "reviewer",
                 "reason_spans": ["u2"]}
    report = check_document(_m6(tmp_path / "n1", [narrowing]))
    assert report["readings"]["dead_readings"] == ["DeadReading: rs2:1"]
    statuses = {(c["set"], c["index"]): c["status"] for c in report["premises"]["candidates"]}
    assert statuses == {("rs1", 0): "model", ("rs1", 1): "narrowed", ("rs2", 0): "model", ("rs2", 1): "dead"}


def test_dead_readings_null_when_not_enumerated(tmp_path, monkeypatch):
    from ve import readings_sup
    from ve.readings_verdicts import context
    doc = load_document(_m6(tmp_path))
    monkeypatch.setattr(readings_sup, "MAX_CHOICE_CHECKS", 1)
    route = context(doc)
    assert route.dead_readings() is None and route.report_fields()["dead_readings"] is None


def test_m8_enumerated_conflict_under_one_reading(tmp_path):
    waive = lambda over: norm("waive-x", "avoid_required", False, over=over, guard=ASKS)  # noqa: E731
    path = s2_document(tmp_path, [("fixed", "u0", norm("base-x", "avoid_required", True)),
                                  ("set", "rs1", "u1", [("a", waive(()), "norm", None),
                                                        ("b", waive(("base-x",)), "norm", None)]),
                                  ("fixed", "u3", norm("stop-x", "avoid_required", False, over=("waive-x",)))])
    report = check_document(path)
    assert report["readings"]["route"] == "enumerated"
    conflict = report["readings"]["conflict"]
    assert conflict["status"] == "CONFLICT"
    # Choice 0: base-x and stop-x both select at m0 (a strict collision); choice 1: base-x never selects.
    assert conflict["choices"] == [{"choice": [["rs1", 0]], "status": "CONFLICT"},
                                   {"choice": [["rs1", 1]], "status": "CONFLICT-FREE"}]
    assert report["readings"]["status"] == "CONFLICT under rs1@1:0"


def _k9():
    predicates = {"asks": {"arguments": ["agent", "user"], "description": "{0} asks {1}"},
                  "avoid_required": obligation("deny", None, act="{0} avoid deceiving {1}", args=("agent", "user")),
                  "help_required": obligation("deny", None, act="{0} help {1}", args=("agent", "user")),
                  "warn_required": obligation("deny", None, act="{0} warn {1}", args=("agent", "user"))}
    raw = environment(predicates, sorts=("agent", "user")).to_dict()
    raw["profiles"] = sorted(SOFT_PROFILES)
    return raw


def test_m9_cycle_enumerated_all(tmp_path):
    rel = lambda p: ["binary", p, ["var", 1], ["var", 0]]  # noqa: E731
    path = s2_document(tmp_path, [
        ("fixed", "u0", norm("f-warn", "warn_required", True, guard=ASKS)),
        ("set", "rs1", "u1", [("a", norm("r-a", "avoid_required", True, guard=rel("help_required")), "norm", None),
                              ("b", norm("r-b", "help_required", True, guard=rel("warn_required")), "norm", None)]),
        ("set", "rs2", "u2", [("c", norm("r-c", "warn_required", True, guard=rel("avoid_required")), "norm", None),
                              ("d", norm("r-d", "warn_required", True), "norm", None)])], raw=_k9())
    report = check_document(path)
    readings = report["readings"]
    assert readings["route"] == "enumerated" and readings["choice_count"] == 4
    assert readings["not_superposable"]["text"] == "ReadingsNotSuperposable: rs1, rs2"
    assert readings["conflict"]["status"] == "CONFLICT-FREE"
    route = verdicts(path)
    assert route.entailment(every("warn_required", guard=ASKS))["verdict"] == "ALL"


def _claim(mode):
    return {"right": {"name": "r9", "holder": "person", "guard": ["top"], "lines": [
        {"kind": "claim", "norm": norm_object("no-arbitrary-arrest", "arrest_permitted", False, mode,
                                              guard=["binary", "arbitrary_arrest", ["var", 1], ["var", 0]])}]}}


def test_m12_rights_enumerated_per_choice(tmp_path):
    path = s2_document(tmp_path, [("set", "rs9", "u9", [("strict", _claim("strict"), "right", None),
                                                        ("default", _claim("default"), "right", None)])],
                       raw=env_rights())
    report = check_document(path)
    readings = report["readings"]
    assert readings["route"] == "enumerated" and readings["choice_count"] == 2
    assert readings["not_superposable"] is None  # never ReadingsNotSuperposable on the rights chain (M12)
    assert report["premises"]["status"] == "model"
    assert [c["status"] for c in report["premises"]["choices"]] == ["model", "model"]
    assert readings["conflict"]["status"] == "CONFLICT-FREE", readings["conflict"]


def test_readings_command_across_readings(tmp_path, capsys):
    """`ve document readings --conclusion` on a content-bearing document: S2a's ALL, SOME or NONE, and under named
    readings with `--under`; `--narrowing` is W2's on-request narrowing and is refused here."""
    from ve.document import main
    path = s2_document(tmp_path, [("set", "rs1", "u1", [S, DF]), ("fixed", "u0", HELP_X)])
    conclusion = tmp_path / "phi.json"
    conclusion.write_text(json.dumps(every("avoid_required")))
    assert main(["readings", str(path), "--conclusion", str(conclusion)]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["verdict"] == "SOME" and data["route"] == "superposed"
    assert main(["readings", str(path), "--conclusion", str(conclusion), "--under", "rs1:0"]) == 0
    assert json.loads(capsys.readouterr().out)["verdict"] == "ALL"
    with pytest.raises(VEError, match="--narrowing applies to W2's route"):
        main(["readings", str(path), "--conclusion", str(conclusion), "--narrowing", "n1"])


# ---------------------------------------------------------------------------------------------------------------
# The English of 2.3 through W7's gate (review B4): 9.4's N1 to N8 on checked evidence, G5, G6, G9

def _wording(path):
    from ve.readings_route import S2Wording
    from ve.readings_verdicts import context
    doc = load_document(path)
    return doc, context(doc), S2Wording(doc, context(doc))


def _query(path, conclusion, **options):
    """The verdict and its English, with the wording whose closed slot classes produced it."""
    doc, route, wording = _wording(path)
    data = route.entailment(conclusion, **options)
    return data, wording.query(conclusion, data), wording


def _report(path):
    """The report's English (2.3), as `check_document` shows it, with the wording that produced it."""
    doc, route, wording = _wording(path)
    lines = wording.report()
    assert check_document(path)["readings"]["english"] == lines
    return lines, wording


def _one_derivation(lines, wording):
    from ve.readings_s2_english import derivations
    for line in lines:
        if line.startswith("CONFLICT"):
            continue  # the lower route's classification line, not an S2a wording (2.1 R4)
        assert len(derivations(line, wording.slots)) == 1, line
        assert not any(x in line for x in ("ve__", "rd-", "soft__", "rights__", "may not")), line  # G6, G9


HELP_ALL = "*For every agent, for every user, that agent must help that user.*"
AVOID_ALL = "*For every agent, for every user, that agent must avoid deceiving that user.*"


def test_n1_e26_and_e13_on_m4(tmp_path):
    path = s2_document(tmp_path, [("set", "rs1", "u1", [S, DF]), ("fixed", "u0", HELP_X)])
    data, lines, wording = _query(path, every("help_required"))
    assert data["verdict"] == "ALL"
    assert lines == [f"Under every reading of the open sentence, the conclusion follows: {HELP_ALL}",
                     "This does not depend on how sentence 1 is read."]
    _one_derivation(lines, wording)


def test_n2_e12_lines_on_m4_some(tmp_path):
    path = s2_document(tmp_path, [("set", "rs1", "u1", [S, DF]), ("fixed", "u0", HELP_X)])
    data, lines, wording = _query(path, every("avoid_required"))
    assert data["verdict"] == "SOME"
    proof, counter = lines
    assert proof == f"Read sentence 1 as *must*: the conclusion follows: {AVOID_ALL}"
    assert counter.startswith("Read sentence 1 as *should*: the conclusion does not follow. It fails here: ")
    # The decision is supposed and attributed, never stated as a fact of the situation.
    assert "suppose the decider decides the exception applies to " in counter
    assert counter.count("exception") == 1
    _one_derivation(lines, wording)


def test_n3_e12_r4_and_classification_on_m3(tmp_path):
    path = s2_document(tmp_path, [("set", "rs1", "u1", [S, DF]), ("fixed", "u0", NEVER_AVOID)])
    lines, wording = _report(path)
    witness = next(k for k, line in enumerate(lines) if "two rules contradict each other here" in line)
    assert lines[witness].startswith("Read sentence 1 as *must*: two rules contradict each other here: ")
    assert lines[witness + 1].startswith("CONFLICT: strict collision on avoid_required at ")
    assert "rule no-deception under rs1@1:0 requires" in lines[witness + 1]
    assert "rule never-avoid releases" in lines[witness + 1]
    _one_derivation(lines, wording)


def test_n4_e26_e3_e7_on_m5(tmp_path):
    narrowing = {"id": "n1", "set": "rs1", "version": 1, "keeps": ["strict"], "by": "reviewer",
                 "reason_spans": ["u2"]}
    path = s2_document(tmp_path, [("set", "rs1", "u1", [S, DF]), ("fixed", "u2", ["top"]), ("fixed", "u0", HELP_X)],
                       narrowings=[narrowing])
    data, lines, wording = _query(path, every("avoid_required"))
    assert data["verdict"] == "ALL" and data["reading_premises_used"] == ["narrowing:n1"]
    assert lines == [f"Under every reading of the open sentence, the conclusion follows: {AVOID_ALL}",
                     "This holds provided that:", "Sentence 1 is not read as *should*, because of sentence 2."]
    _one_derivation(lines, wording)


def test_n5_e17_on_m6_with_n1(tmp_path):
    narrowing = {"id": "n1", "set": "rs1", "version": 1, "keeps": ["strict"], "by": "reviewer",
                 "reason_spans": ["u2"]}
    path = _m6(tmp_path, [narrowing])
    lines, wording = _report(path)
    assert "No compatible way of reading the open sentences reads sentence 2 as *should*." in lines
    # Candidate 1 of rs1 is dropped by the narrowing: nothing for it beyond E7.
    assert not any("sentence 1 as *should*" in line for line in lines)
    _one_derivation(lines, wording)


def test_n6_e27_none_over_three_choices(tmp_path):
    asserted = ("assert", ["forall", "agent", ["forall", "user", ASKS]], "asserted", {"force": "y"})
    kind_s = ("strict", norm("be-kind", "help_required", True), "norm", {"force": "x"})
    kind_d = ("default", norm("be-kind", "help_required", True, "default"), "norm", {"force": "y"})
    coupling = {"id": "c1", "axis": "force", "sets": [{"set": "rs1", "version": 1}, {"set": "rs2", "version": 1}],
                "by": "reviewer", "reason_spans": ["u1"]}
    path = s2_document(tmp_path, [("set", "rs1", "u1", [(*S[:3], {"force": "x"}), (*DF[:3], {"force": "x"}),
                                                        asserted]),
                                  ("set", "rs2", "u2", [kind_s, kind_d])], couplings=[coupling])
    doc, route, wording = _wording(path)
    assert len(route.choices) == 3
    nobody_asks = ["forall", "agent", ["forall", "user", ["not", ASKS]]]
    data, lines, wording = _query(path, nobody_asks)
    assert data["verdict"] == "NONE" and len(data["countermodels"]) == 3
    assert lines[0] == "Under no reading of the 2 open sentences does the conclusion follow."
    assert len(lines) == 4 and all(line.startswith("Read sentence 1 as ") for line in lines[1:])
    _one_derivation(lines, wording)


def test_n6_e28_over_64_choices(tmp_path):
    items = []
    for k in range(7):
        name = f"rule-{k}"
        items.append(("set", f"rs{k}", f"u{k}", [("strict", norm(name, "avoid_required", True), "norm", None),
                                                 ("default", norm(name, "avoid_required", True, "default"),
                                                  "norm", None)]))
    path = s2_document(tmp_path, items)
    doc, route, wording = _wording(path)
    assert route.choices is None and route.row["choice_count"] == "over 64" and route.row["choices_checked"] == 128
    data, lines, wording = _query(path, every("help_required"))
    assert data["verdict"] == "UNKNOWN" and data["status"].startswith("UNKNOWN (not ALL: countermodel under ")
    assert lines[0] == "VE did not check every way of reading the open sentences: there are more than 64."
    assert lines[1].startswith("Read sentence 1 as ") and "the conclusion does not follow" in lines[1]
    _one_derivation(lines, wording)


def test_n7_e29_on_m9(tmp_path):
    rel = lambda p: ["binary", p, ["var", 1], ["var", 0]]  # noqa: E731
    path = s2_document(tmp_path, [
        ("set", "rs1", "u1", [("a", norm("r-a", "avoid_required", True, guard=rel("help_required")), "norm", None),
                              ("b", norm("r-b", "help_required", True, guard=rel("warn_required")), "norm", None)]),
        ("set", "rs2", "u2", [("c", norm("r-c", "warn_required", True, guard=rel("avoid_required")), "norm", None),
                              ("d", norm("r-d", "warn_required", True), "norm", None)]),
        ("fixed", "u0", norm("f-warn", "warn_required", True, guard=ASKS))], raw=_k9())
    lines, wording = _report(path)
    assert lines[0] == "The readings of sentences 1 and 2 were checked one way at a time, not together."
    assert lines[1] == "Under every reading of the 2 open sentences, no two rules on the same act contradict each other."
    data, query, wording_q = _query(path, every("warn_required", guard=ASKS))
    assert data["verdict"] == "ALL" and query == [
        "Under every reading of the 2 open sentences, the conclusion follows: *For every agent, for every user "
        "that that agent has the recorded relation \"asks\" to, that agent must warn that user.*"]
    _one_derivation(lines, wording)
    _one_derivation(query, wording_q)


def test_n8_e8_gated_on_the_quiet_label_of_m1(tmp_path):
    from ve.readings_s2_english import PROVIDED, QUIET
    path = s2_document(tmp_path, [("set", "rs1", "u1", [S, DF])])
    _, _, wording = _wording(path)
    lines = wording.provided(["readings:rs1@1:1:quiet"])
    assert lines == [PROVIDED, QUIET]
    _one_derivation(lines, wording)


def test_ruling4_class_base_environments_set_readings_aside():
    """The class of DRI ruling 4's bug: every conversion to a base vocabulary that drops `norms@0` keeps no
    `readings@1` (kept alone, it read as `readings@1 requires norms@0`, false of the document)."""
    from ve.norms import NormDocument
    from ve.softnorms import SoftEnvironment, SoftNormDocument
    soft = SoftNormDocument(SoftEnvironment(env_k()), [norm("a", "avoid_required", True)])
    assert "readings@1" not in soft.elaborated.base_environment().profiles
    plain = env_k(profiles=("norms@0", "readings@1", "relational-fol@0"))
    assert "readings@1" not in NormDocument(_environment(plain), [norm("a", "avoid_required", True)]) \
        .base_environment().profiles


def test_a1_class_named_reading_no_choice_takes_is_refused(tmp_path):
    """Review A1's class: a certificate under named readings that no compatible choice takes (here the candidate
    the narrowing drops) would be vacuous; Lean and Python refuse it instead of a verdict."""
    from ve.readings_route import run_lean
    narrowing = {"id": "n1", "set": "rs1", "version": 1, "keeps": ["strict"], "by": "reviewer",
                 "reason_spans": ["u2"]}
    path = s2_document(tmp_path, [("set", "rs1", "u1", [S, DF]), ("fixed", "u2", ["top"]), ("fixed", "u0", HELP_X)],
                       narrowings=[narrowing])
    _, route, _ = _wording(path)
    text = "ReadingsUnsatisfiable: no compatible reading takes rs1@1:1"
    with pytest.raises(VEError) as caught:
        route.entailment(every("avoid_required"), assumed=[("rs1", 1)])
    assert caught.value.message == text
    close = {"checker_version": "ve-tableau-checker@2", "environment_id": "-", "premise_meaning_ids": [],
             "conclusion_meaning_id": "-", "trace": {"rule": "close"}}
    rows = run_lean([{"id": k, "kind": k, "environment": route.environment, "document": route.document,
                      "assumed": [["rs1", 1]], "premises": [], "conclusion": None, "certificate": close,
                      "conflict_certificates": {}} for k in ("readings-certificate", "readings-conflict")])
    assert [row.get("error") for row in rows] == [text, text], rows
    assert route.entailment(every("avoid_required"), assumed=[("rs1", 0)])["verdict"] == "ALL"


def test_rust_shadow_evaluates_every_model_shown(tmp_path, monkeypatch):
    """4.2 and 10: Rust evaluates the formulas of `sup D` on every model shown, untrusted; its values must be the
    ones Lean's check established, or the verdict is `CheckerUnavailable`."""
    from ve.backends import rust_jsonl
    from ve.errors import CheckerUnavailable
    path = s2_document(tmp_path, [("set", "rs1", "u1", [S, DF]), ("fixed", "u0", NEVER_AVOID)])
    seen = []
    real = rust_jsonl.run

    def spy(case, **kwargs):
        record = real(case, **kwargs)
        if case.get("kind") == "readings-superposed-evaluate":
            seen.append((case, record))
        return record

    monkeypatch.setattr(rust_jsonl, "run", spy)
    _, route, _ = _wording(path)
    assert route.conflict(())["status"] == "CONFLICT" and route.premises()["status"] == "model"
    assert seen and all(record["untrusted"] is True for _, record in seen)
    witness = next(record for case, record in seen if case["conflict_targets"])
    assert witness["values"]["conflict_targets"] == [True] and all(witness["values"]["slot"])

    def lying(case, **kwargs):
        record = real(case, **kwargs)
        if case.get("kind") == "readings-superposed-evaluate":
            record["values"]["slot"] = [False] * len(record["values"]["slot"])
        return record

    monkeypatch.setattr(rust_jsonl, "run", lying)
    _, route, _ = _wording(path)
    with pytest.raises(CheckerUnavailable, match="Rust's untrusted evaluation differs"):
        route.premises()
