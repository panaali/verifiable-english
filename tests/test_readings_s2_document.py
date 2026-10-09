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
from ve.readings_s2_english import hidden_in

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "tests/data/readings_s2/constitution-nd-readings.ve.md"


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


def test_ruling4_rule_candidate_beside_norm_defaults_is_under_the_completion(tmp_path):
    """The pilot's probe (b): a strict rule as one candidate's content. Before readings-defaults RD-2a Lean and Python
    both reached S1's abstention; on the norms chain the document is now under the unspecified completion, which
    Lean admits (readings-defaults.md 4.6, an `availability` change). The other candidate is pending, so the set
    stays unresolved and no verdict is claimed. Off the norms chain the abstention stays (K18,
    `test_readings_nd_lean.py::test_fnd6_soft_chain_keeps_the_abstention`)."""
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
    result = check_document(_write(tmp_path, "rule.ve.md", meta, rest))
    residual = result["coverage"]["residual"]
    assert (residual["unresolved_reading_sets"], residual["pending_candidates"]) == (1, 1)


def _completion_document(tmp_path):
    """F-ND1 (readings-defaults.md 8.3) as a document: one open set on `u1` whose two readings both carry a rule, on the
    norms chain under `norm-defaults@0`, with the pair's distinguishing situation recorded."""
    from tests.test_document import unit, write_doc
    from tests.test_readings_nd_lean import doc1, env1
    from ve.readings import s1_content_meaning_id
    raw = env1()
    document, _ = doc1(raw)
    env = _environment(raw)
    for reading_set in document["reading_sets"]:
        for r in reading_set["readings"]:
            r["meaning_id"] = s1_content_meaning_id(env, reading_set["id"], r)
    text = b"Every agent must help each user.\n"
    units = [unit("u1", 0, len(text), "norm", "specified")]
    return raw, document, write_doc(tmp_path, text, units, environment_json=raw,
                                    reading_sets=document["reading_sets"])


def test_rd2b_completion_document_is_checked_not_refused(tmp_path):
    """Review B3 of RD-2a, then RD-2b: a document under the unspecified completion (every candidate with content, the
    norms chain, `norm-defaults@0`) is admitted by Lean on the enumerated route with the completion as the cause, and
    `ve document` relays its checks: no conformance alarm (B3), and no named refusal any more (RD-2a's, until RD-2b)."""
    _, _, path = _completion_document(tmp_path)
    report = check_document(path)
    assert (report["readings"]["route"], report["readings"]["not_superposable"]) == (
        "enumerated", {"text": "ReadingsNotSuperposable: rs_1", "cause": "the unspecified completion"})
    assert report["readings"]["conflict"]["status"] == "CONFLICT-FREE"


def test_rd2a_review_b3_route_table_is_lean_s(tmp_path, lean_route):
    """Review B3's class: under `norm-defaults@0` the relay takes Lean's route of 1.1 (`routeOf`) and regenerates
    none of it: the completion's route and cause are Lean's, relayed with the filled document (RD-2b)."""
    from ve.readings_route import COMPLETION_CAUSE, elaborate, run_lean
    from ve.readings_s1 import wire
    raw, document, _ = _completion_document(tmp_path)
    units = [{"id": "u1", "kind": "norm"}]
    [row] = run_lean([{"id": "r", "kind": "readings-elaborate", "environment": wire(raw),
                       "document": wire({"units": units, "reading_sets": document["reading_sets"]})}])
    assert (row["route"], row["finding"]["cause"]) == ("enumerated", COMPLETION_CAUSE)
    relayed = elaborate(raw, units, document["reading_sets"])
    assert relayed == {key: value for key, value in row.items() if key not in ("id", "status")}


def test_ruling4_lean_frame_reads_unspecified_as_deny(tmp_path, lean_route):
    """Lean's decoder reads a `norm-defaults@0` frame with `unspecified` as the placeholder `deny` (E‴), so
    readings-validate answers instead of failing to decode. Python's S1 frame under the profile is Lean's filled one
    (readings-defaults RD-2b: `_placeholder_frame` is deleted): built from `filled` it reads `deny`, and without
    `filled` there is no frame."""
    from ve.errors import CheckerUnavailable
    from ve.readings_route import document_wire, run_lean
    from ve.readings_s1 import S1Environment
    meta, _ = _split(PILOT)
    units = [{"id": u["id"], "kind": u["kind"], "content": None} for u in meta["units"]]
    [row] = run_lean([{"id": "v", "kind": "readings-validate", "environment": meta["environment"],
                       "document": document_wire(units, meta["reading_sets"])}], executable=lean_route)
    assert row["status"] == "ok" and row["content_bearing"] is False, row
    raw, document, _ = _completion_document(tmp_path)
    [row] = run_lean([{"id": "v", "kind": "readings-validate", "environment": raw,
                       "document": document_wire([{"id": "u1", "kind": "norm"}], document["reading_sets"])}],
                     executable=lean_route)
    senv = S1Environment(raw, row["filled"])
    assert senv.frame.predicates["help_required"].regulated.default == "deny"
    with pytest.raises(CheckerUnavailable, match="^ReadingsConstruction: under norm-defaults@0 the frame is"):
        S1Environment(raw)


@pytest.fixture
def lean_route():
    """The readings route's service (None: the default `ve_service`)."""
    from tests import lean_routes
    if not lean_routes.SERVICE.exists():
        pytest.skip("the Lean service is not built")
    return None


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


def _m6(tmp_path, narrowings=(), coupling_id="c1"):
    probe_unit = ("fixed", "u2", ["top"])
    s2 = ("strict", norm("be-kind", "help_required", True), "norm", {"force": "strict"})
    d2 = ("default", norm("be-kind", "help_required", True, "default"), "norm", {"force": "default"})
    coupling = {"id": coupling_id, "axis": "force",
                "sets": [{"set": "rs1", "version": 1}, {"set": "rs2", "version": 1}],
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


def _claim(mode, right="r9", rule="no-arbitrary-arrest"):
    return {"right": {"name": right, "holder": "person", "guard": ["top"], "lines": [
        {"kind": "claim", "norm": norm_object(rule, "arrest_permitted", False, mode,
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
    from ve.readings_s2_wording import S2Wording
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
        assert hidden_in(line, wording.slots.reserved) is None, line  # G6, G9


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
    assert all(line.startswith("Read sentence 1 as ") for line in lines[1:4])
    # The three choices are the coupling's (review A of compose-s2 looprecheck2): E3 with its E5 line.
    assert data["restrictions"] == ["coupling:c1"]
    assert lines[4:] == ["This holds provided that:",
                         "Sentences 1 and 2 are read with the same force, because of sentence 1."]
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


# ---------------------------------------------------------------------------------------------------------------
# compose-s2 looprecheck1: review A (named readings keep their restriction in English), review B (the enumerated
# route's evidence is replayed by Lean on the regenerated choice documents) and review B (an absence that cannot be
# certified is not reported as none).

REL = lambda p: ["binary", p, ["var", 1], ["var", 0]]  # noqa: E731


def _m9(tmp_path, raw=None, name="m9.ve.md"):
    return s2_document(tmp_path, [
        ("fixed", "u0", norm("f-warn", "warn_required", True, guard=ASKS)),
        ("set", "rs1", "u1", [("a", norm("r-a", "avoid_required", True, guard=REL("help_required")), "norm", None),
                              ("b", norm("r-b", "help_required", True, guard=REL("warn_required")), "norm", None)]),
        ("set", "rs2", "u2", [("c", norm("r-c", "warn_required", True, guard=REL("avoid_required")), "norm", None),
                              ("d", norm("r-d", "warn_required", True), "norm", None)])], raw=raw or _k9(), name=name)


def _cli(path, conclusion, *under):
    from ve.document import main
    phi = Path(path).with_suffix(".phi.json")
    phi.write_text(json.dumps(conclusion))
    args = ["readings", str(path), "--conclusion", str(phi)]
    for item in under:
        args += ["--under", item]
    assert main(args) == 0
    return json.loads(_cli.capsys.readouterr().out)


def test_review_a_named_readings_keep_their_restriction_in_english(tmp_path, capsys):
    """The finding's case: on M9 the unguarded `warn_required` query is SOME; under `rs2:1` it follows (every choice
    taking *d*), under `rs2:0` it follows under none. Neither result may be worded over every reading."""
    _cli.capsys = capsys
    path = _m9(tmp_path)
    phi = every("warn_required")
    assert _cli(path, phi)["verdict"] == "SOME"
    under_d = _cli(path, phi, "rs2:1")
    assert under_d["verdict"] == "ALL" and under_d["assumed"] == [["rs2", 1]]
    warn = "*For every agent, for every user, that agent must warn that user.*"
    assert under_d["english"] == [f"Read sentence 3 as {M9_RS2_1}: the conclusion follows: {warn}"]
    under_c = _cli(path, phi, "rs2:0")
    assert under_c["verdict"] == "NONE" and under_c["assumed"] == [["rs2", 0]]
    assert len(under_c["english"]) == 2 and not any(line.startswith("Under ") for line in under_c["english"])
    assert all(line.startswith("Read sentence 2 as ") and f" and sentence 3 as {M9_RS2_0}: the conclusion does not follow."
               in line for line in under_c["english"])
    _, route, wording = _wording(path)
    for data in (under_d, under_c):
        assert wording.query(phi, route.entailment(phi, assumed=data["assumed"])) == data["english"]
        _one_derivation(data["english"], wording)


def test_review_a_class_every_reading_wordings_need_no_assumption(tmp_path):
    """The class: E10, E26, E27 and E28 claim every reading; a verdict carrying `assumed` gets E12 lines only, on
    either route, and the enumerated route refuses readings no compatible choice takes as the superposed one does."""
    from ve.readings_s2_wording import S2Wording
    path = _m9(tmp_path)
    doc, route, wording = _wording(path)
    phi = every("warn_required", guard=ASKS)
    data = route.entailment(phi, assumed=[("rs1", 0), ("rs2", 1)])
    assert data["verdict"] == "ALL" and data["assumed"] == [["rs1", 0], ["rs2", 1]]
    assert wording.query(phi, data) == [
        f"Read sentence 2 as {M9_RS1_0} and sentence 3 as {M9_RS2_1}: the conclusion follows: *For every agent, for every user that "
        "that agent has the recorded relation \"asks\" to, that agent must warn that user.*"]
    with pytest.raises(VEError) as caught:
        route.entailment(phi, assumed=[("rs1", 7)])
    assert caught.value.message == "ReadingsUnsatisfiable: no compatible reading takes rs1@1:7"
    # Superposed (M4): under a named reading the certificate's sentence names it; NOT ALL is its countermodel's E12.
    m4 = s2_document(tmp_path / "m4", [("set", "rs1", "u1", [S, DF]), ("fixed", "u0", HELP_X)])
    doc, route, _ = _wording(m4)
    wording = S2Wording(doc, route)
    lines = wording.query(every("avoid_required"), route.entailment(every("avoid_required"), assumed=[("rs1", 1)]))
    assert len(lines) == 1 and lines[0].startswith("Read sentence 1 as *should*: the conclusion does not follow.")


def _lean_spy(monkeypatch):
    from ve import readings_route
    seen, real = [], readings_route.run_lean

    def spy(cases, **kwargs):
        rows = real(cases, **kwargs)
        seen.extend(zip(cases, rows))
        return rows

    monkeypatch.setattr(readings_route, "run_lean", spy)
    return seen


def _inner_kinds(seen):
    return [(tuple(map(tuple, case["choice"])), case["inner"]["kind"]) for case, _ in seen
            if case["kind"] == "readings-choice"]


def _evidence(seen, question=None):
    """(choice, piece, inner kind, Lean's acceptance) of every piece sent to `readings-verdicts` (readings-defaults
    RD-3: the enumerated route's evidence is checked there, on each choice's regenerated document)."""
    out = []
    for case, row in seen:
        if case["kind"] != "readings-verdicts" or (question and case["question"] != question):
            continue
        accepted = {tuple(map(tuple, e["choice"])): e["evidence"] for e in row["per_choice"]}
        for entry in case["evidence"]:
            choice = tuple(map(tuple, entry["choice"]))
            for piece, inner in entry.items():
                if piece != "choice":
                    out.append((choice, piece, inner["kind"], accepted.get(choice, {}).get(piece)))
    return out


def test_review_b_enumerated_evidence_is_replayed_by_lean(tmp_path, monkeypatch):
    """The finding's case: M9's ALL is folded by Lean only from certificates its soft route accepted on each choice's
    regenerated document, and SOME's countermodel from a model Lean's `choice-model` checked there (RD-3: one
    `readings-verdicts` request, Python's evidence in it)."""
    path = _m9(tmp_path)
    route = verdicts(path)
    seen = _lean_spy(monkeypatch)
    assert route.entailment(every("warn_required", guard=ASKS))["verdict"] == "ALL"
    choices = [tuple((R.id, c[R.id]) for R in route.sets) for c in route.choices]
    # Each choice's conflict packages first (14.8), then its certificate, accepted with the same packages.
    sent = _evidence(seen, "query")
    assert {(c, p, k) for c, p, k, _ in sent} == {(c, p, k) for c in choices for p, k in
                                                  (("conflict", "soft-conflict"), ("certificate", "soft-certificate"))}
    assert all(ok is True for _, p, _, ok in sent if p == "certificate")
    [row] = [row for case, row in seen if case["kind"] == "readings-verdicts" and any(
        "certificate" in e for e in case["evidence"])]
    assert [e["query"] for e in row["per_choice"]] == ["proved"] * len(choices)
    assert not _inner_kinds(seen)
    seen.clear()
    some = route.entailment(every("warn_required"))
    assert some["verdict"] == "SOME"
    models = [(c, ok) for c, p, k, ok in _evidence(seen, "query") if k == "choice-model"]
    assert models and all(ok is True for _, ok in models)
    assert tuple(map(tuple, some["countermodel"]["choice"])) in {c for c, _ in models}


@pytest.mark.parametrize("kind", ["soft-certificate", "choice-model"])
def test_review_b_lean_refusal_of_enumerated_evidence_is_unavailable(tmp_path, monkeypatch, kind):
    """A piece of evidence Lean refuses (a certificate whose trace is cut, a model whose shown form is not the checked
    one) is `CheckerUnavailable`, never a verdict."""
    from ve import readings_route
    from ve.errors import CheckerUnavailable
    path = _m9(tmp_path)
    route = verdicts(path)
    real = readings_route.run_lean

    def tampering(cases, **kwargs):
        for case in cases:
            for entry in case.get("evidence", []) if case["kind"] == "readings-verdicts" else []:
                for piece in entry.values():
                    if type(piece) is dict and piece.get("kind") == kind:
                        if kind == "choice-model":
                            piece["model"] = {**piece["model"], "domains": {**piece["model"]["domains"], "agent": []}}
                        else:
                            piece["certificate"] = {**piece["certificate"], "trace": {"rule": "close", "at": 0}}
        return real(cases, **kwargs)

    monkeypatch.setattr(readings_route, "run_lean", tampering)
    with pytest.raises(CheckerUnavailable, match="ReadingsConformance"):
        route.entailment(every("warn_required", guard=ASKS) if kind == "soft-certificate" else every("warn_required"))


def test_review_b_lean_supplies_the_choice_documents_assertions(tmp_path):
    """Lean prepends the regenerated assertions of `choiceDoc D c`: a model that falsifies a fixed assertion fails
    `choice-model` though the case sends no premise, and a certificate that needs the assertion is accepted."""
    from ve.ast import _to_data
    every_asks = ["forall", "agent", ["forall", "user", ASKS]]
    path = s2_document(tmp_path, [("fixed", "ua", every_asks), *[
        item for item in [("fixed", "u0", norm("f-warn", "warn_required", True, guard=ASKS)),
                          ("set", "rs1", "u1", [("a", norm("r-a", "avoid_required", True, guard=REL("help_required")),
                                                 "norm", None),
                                                ("b", norm("r-b", "help_required", True, guard=REL("warn_required")),
                                                 "norm", None)]),
                          ("set", "rs2", "u2", [("c", norm("r-c", "warn_required", True, guard=REL("avoid_required")),
                                                 "norm", None),
                                                ("d", norm("r-d", "warn_required", True), "norm", None)])]]],
                       raw=_k9())
    route = verdicts(path)
    assert route.route == "enumerated"
    choice = route.choices[0]
    own = route._choice(choice)
    phi = every("warn_required")
    route.conflict()
    proof = own.certificate_case(phi)
    assert proof is not None
    row = route._verdicts("query", query={route._key(choice): {"certificate": proof}}, premises=[], conclusion=phi)
    [entry] = [e for e in row["per_choice"] if e["choice"] == route.choice_json(choice)]
    assert entry["evidence"]["certificate"] is True and entry["query"] == "proved"
    model = {"complete": True, "domains": {"agent": ["a"], "user": ["u"]}, "constants": {},
             "relations": {name: [] for name in own.soft.elaborated.base_environment().predicates}}
    row = route.lean("readings-choice", choice=route.choice_json(choice),
                     inner={"kind": "choice-model", "premises": [], "conclusion": None, "model": model})
    assert row["assertions"] == 1 and row["inner"]["assertions"] == 1
    assert row["inner"]["valid"] is False and row["inner"]["first_failing"] == 0, row
    model["relations"]["asks"] = [["a", "u"]]
    row = route.lean("readings-choice", choice=route.choice_json(choice),
                     inner={"kind": "choice-model", "premises": [], "conclusion": _to_data(own._phi(phi)),
                            "model": model})
    assert row["inner"]["valid"] is True and row["inner"]["conclusion_value"] is True, row


def test_review_b_rights_and_norms_chains_replay_models_and_certificates(tmp_path, monkeypatch):
    """The class on the other chains: the rights chain's premise models (M12) and the norms chain's enumerated
    verdicts are checked by Lean's `choice-model` and the chain's certificate kind."""
    seen = _lean_spy(monkeypatch)
    path = s2_document(tmp_path, [("set", "rs9", "u9", [("strict", _claim("strict"), "right", None),
                                                        ("default", _claim("default"), "right", None)])],
                       raw=env_rights())
    route = verdicts(path)
    premises = route.premises()
    assert premises["status"] == "model" and premises["model"]["domains"]
    assert {k for _, _, k, _ in _evidence(seen, "premises")} >= {"choice-model"}
    arrested = ["forall", "state", ["forall", "person", ["implies", ["binary", "arbitrary_arrest", ["var", 1],
                                                                      ["var", 0]],
                                                         ["not", ["binary", "arrest_permitted", ["var", 1],
                                                                  ["var", 0]]]]]]
    seen.clear()
    data = route.entailment(arrested)
    # Under *must* the claim refuses every arbitrary arrest; under *should* an exception may apply.
    assert data["verdict"] == "SOME" and data["proof"]["choice"] == [["rs9", 0]], data
    # (Each choice's conflict status was computed, once, by the premise status above.)
    query = [(p, k, ok) for _, p, k, ok in _evidence(seen, "query") if p in ("certificate", "countermodel")]
    assert {k for _, k, _ in query} == {"rights-certificate", "choice-model"}
    assert all(ok is True for _, _, ok in query)
    # The norms chain: M9 without soft-norms@0 is not superposable either (its precedence cycle).
    norms_raw = _k9()
    norms_raw["profiles"] = ["norms@0", "readings@1", "relational-fol@0"]
    seen.clear()
    route = verdicts(_m9(tmp_path / "norms", raw=norms_raw))
    assert route.route == "enumerated"
    assert route.entailment(every("warn_required", guard=ASKS))["verdict"] == "ALL"
    assert route.entailment(every("warn_required"))["verdict"] == "SOME"
    assert route.premises()["status"] == "model"
    assert {k for _, _, k, _ in _evidence(seen)} == {"norms-conflict", "norms-certificate", "choice-model"}
    assert all(ok is True for _, p, k, ok in _evidence(seen) if k == "norms-certificate")


def test_review_b_dead_readings_null_when_certification_cannot_finish(tmp_path, monkeypatch):
    """The finding's case: M6 with its narrowing under proof-budget exhaustion (`max_steps=0`) reports
    `dead_readings` null, never `[]`, and `rs2:1` is not `dead` without its certificate."""
    from ve import readings_verdicts
    narrowing = {"id": "n1", "set": "rs1", "version": 1, "keeps": ["strict"], "by": "reviewer",
                 "reason_spans": ["u2"]}
    path = _m6(tmp_path, [narrowing])
    monkeypatch.setitem(readings_verdicts.BUDGET, "max_steps", 0)
    route = verdicts(path)
    assert route.dead_readings() is None and route.report_fields()["dead_readings"] is None
    statuses = {(c["set"], c["index"]): c["status"] for c in route.candidate_premises()}
    assert statuses[("rs2", 1)] == "UNKNOWN"


def test_review_b_enumerated_dead_readings_null_when_certification_cannot_finish(tmp_path, monkeypatch):
    """The same class on the enumerated route: a candidate no compatible choice takes is `dead` only with its
    certificate; under proof-budget exhaustion the list is null and the candidate UNKNOWN."""
    from ve import readings_verdicts
    claims = {k: [("strict", _claim("strict", f"r{k}", f"no-arrest-{k}"), "right", {"force": "strict"}),
                  ("default", _claim("default", f"r{k}", f"no-arrest-{k}"), "right", {"force": "default"})]
              for k in (8, 9)}
    coupling = {"id": "c1", "axis": "force", "sets": [{"set": "rs8", "version": 1}, {"set": "rs9", "version": 1}],
                "by": "reviewer", "reason_spans": ["u8"]}
    narrowing = {"id": "n1", "set": "rs8", "version": 1, "keeps": ["strict"], "by": "reviewer",
                 "reason_spans": ["u8"]}
    path = s2_document(tmp_path, [("set", "rs8", "u8", claims[8]), ("set", "rs9", "u9", claims[9])],
                       raw=env_rights(), couplings=[coupling], narrowings=[narrowing])
    route = verdicts(path)
    assert route.route == "enumerated" and route.dead_readings() == [
        {"set": "rs9", "index": 1, "finding": "DeadReading: rs9:1"}]
    monkeypatch.setitem(readings_verdicts.BUDGET, "max_steps", 0)
    route = verdicts(path)
    assert route.dead_readings() is None and route.report_fields()["dead_readings"] is None
    statuses = {(c["set"], c["index"]): c["status"] for c in route.premises()["candidates"]}
    assert statuses[("rs9", 1)] == "UNKNOWN" and statuses[("rs8", 1)] == "narrowed"


def test_review_b2_rd3_dead_evidence_lean_does_not_confirm_is_unavailable(tmp_path):
    """Review B2 of rd-3: Lean's note on each dead reading's certificate is the request's, and a refused one is
    `CheckerUnavailable`, never a dead reading; so are dead notes for certificates the request did not send."""
    from ve.errors import CheckerUnavailable
    claims = {k: [("strict", _claim("strict", f"r{k}", f"no-arrest-{k}"), "right", {"force": "strict"}),
                  ("default", _claim("default", f"r{k}", f"no-arrest-{k}"), "right", {"force": "default"})]
              for k in (8, 9)}
    coupling = {"id": "c1", "axis": "force", "sets": [{"set": "rs8", "version": 1}, {"set": "rs9", "version": 1}],
                "by": "reviewer", "reason_spans": ["u8"]}
    narrowing = {"id": "n1", "set": "rs8", "version": 1, "keeps": ["strict"], "by": "reviewer",
                 "reason_spans": ["u8"]}
    route = verdicts(s2_document(tmp_path, [("set", "rs8", "u8", claims[8]), ("set", "rs9", "u9", claims[9])],
                                 raw=env_rights(), couplings=[coupling], narrowings=[narrowing]))
    answer = route.premises_answer()
    request = route.requests[id(answer)]
    assert answer["dead"] == [{"set": "rs9", "index": 1, "accepted": True}]
    route.check_answer(answer, request)
    for mutate in (lambda a: a["dead"][0].update(accepted=False), lambda a: a.update(dead=[]),
                   lambda a: a["dead"].append({"set": "rs9", "index": 0, "accepted": True}),
                   lambda a: a["untaken"].append(["rs8", 0]), lambda a: a.update(dead_readings=[
                       {"set": "rs8", "index": 0, "finding": "DeadReading: rs8:0"}])):
        mutated = copy.deepcopy(answer)
        mutate(mutated)
        with pytest.raises(CheckerUnavailable):
            route.check_answer(mutated, request)


# ---------------------------------------------------------------------------------------------------------------
# compose-s2 looprecheck2: review B (no entailment is certified under a reading whose rules collide), review A
# (enumerated combinations keep the couplings and narrowings that selected their choices) and review A (a situation
# shows every decision the choice's document generates, rights' included).

def _m8(tmp_path):
    waive = lambda over: norm("waive-x", "avoid_required", False, over=over, guard=ASKS)  # noqa: E731
    return s2_document(tmp_path, [("fixed", "u0", norm("base-x", "avoid_required", True)),
                                  ("set", "rs1", "u1", [("a", waive(()), "norm", None),
                                                        ("b", waive(("base-x",)), "norm", None)]),
                                  ("fixed", "u3", norm("stop-x", "avoid_required", False, over=("waive-x",)))])


def test_review_b2_conflicting_reading_certifies_no_entailment(tmp_path):
    """The finding's case: on M8 under `rs1:0` (CONFLICT) both `∀agent ∀user. avoid_required` and its pointwise
    negation were ALL. Every entailment there is `UNKNOWN (conflict status: CONFLICT)`, as on the superposed route;
    under the conflict-free `rs1:1` the negation is ALL and the conclusion NONE."""
    path = _m8(tmp_path)
    route = verdicts(path)
    assert route.route == "enumerated"
    blocked = {"verdict": "UNKNOWN", "route": "enumerated", "status": "UNKNOWN (conflict status: CONFLICT)",
               "conflict_status": "CONFLICT", "choice": [["rs1", 0]]}
    for negated in (False, True):
        phi = every("avoid_required", negated=negated)
        assert route.entailment(phi) == blocked
        assert route.entailment(phi, assumed=[("rs1", 0)]) == {**blocked, "assumed": [["rs1", 0]]}
        assert route.entailment(phi, assumed=[("rs1", 1)])["verdict"] == ("ALL" if negated else "NONE")
    # The class: no certificate of a conflicting choice's document is promoted, `⊥` (premise status) included.
    conflict = route.conflict_answer()
    assert [e["conflict"] for e in conflict["per_choice"]] == ["CONFLICT", "CONFLICT-FREE"]
    own = route._choice(route.choices[0])
    from ve.errors import CheckerUnavailable
    phi = every("avoid_required")
    piece = own.certificate_case(phi)
    assert piece is not None  # Python's prover finds one where the rules collide; Lean does not accept it
    with pytest.raises(CheckerUnavailable, match="does not confirm the certificate"):
        route._verdicts("query", query={route._key(route.choices[0]): {"certificate": piece}}, premises=[],
                        conclusion=phi)
    assert [c["status"] for c in route.premises()["choices"]] != ["INCONSISTENT", "INCONSISTENT"]
    _, _, wording = _wording(path)
    assert wording.query(every("avoid_required"), route.entailment(every("avoid_required"))) == []


def test_review_b2_lean_accepts_a_reading_certificate_only_conflict_free(tmp_path):
    """Lean's side of the class: `readings-choice` accepts a chain certificate only with the choice's conflict
    packages, which the lower route's own conflict kind must find CONFLICT-FREE on the same document."""
    from ve.ast import _to_data
    path = _m8(tmp_path)
    route = verdicts(path)
    free, conflicting = route._choice(route.choices[1]), route._choice(route.choices[0])
    phi = every("avoid_required", negated=True)
    assert free.certificate_case(phi) is not None
    # The certificate Python's prover finds on the conflicting choice is valid, and still not accepted.
    from ve.entailment import prove_entailment
    packages = {k: v for k, v in conflicting.conflict_case().items() if k != "kind"}
    premises, formula = conflicting._all(), conflicting._phi(phi)
    proof = prove_entailment(conflicting.env, premises, formula)
    assert proof.status == "Found"
    case = {"kind": "soft-certificate", "premises": [], "conclusion": _to_data(formula),
            "certificate": proof.certificate}
    choice = route.choice_json(route.choices[0])
    row = route.lean("readings-choice", choice=choice, inner={**case, "conflict": packages})
    assert row["inner"]["valid"] is True and row["conflict_free"] is False and row["accepted"] is False, row
    from ve.errors import CheckerUnavailable
    with pytest.raises(CheckerUnavailable, match="a reading's certificate needs the choice's conflict packages"):
        route.lean("readings-choice", choice=choice, inner=case)


def test_review_b2_python_never_bypasses_lean_conflict_check(tmp_path, monkeypatch):
    """Python has no conflict status of its own (RD-3): an answer whose gate a relay tampering hides is
    `CheckerUnavailable`, never a verdict: since review B1 of rd-3 the gate's result without its `conflict_status` is
    of no form the schema allows; were it accepted, Python would send the conflicting choice's certificate, which Lean,
    checking the packages itself, does not accept."""
    from ve import readings_route
    from ve.errors import CheckerUnavailable
    path = _m8(tmp_path)
    route = verdicts(path)
    real = readings_route.run_lean

    def hiding(cases, **kwargs):
        rows = real(cases, **kwargs)
        for case, row in zip(cases, rows):
            if case["kind"] == "readings-verdicts" and case["question"] == "query":
                row["result"].pop("conflict_status", None)
        return rows

    monkeypatch.setattr(readings_route, "run_lean", hiding)
    with pytest.raises(CheckerUnavailable, match="invalid answer|does not confirm the certificate"):
        route.entailment(every("avoid_required", negated=True))


def _m9_narrowed(tmp_path):
    meta, rest = _split(_m9(tmp_path))
    meta["narrowings"] = [{"id": "n1", "set": "rs2", "version": 1, "keeps": ["d"], "by": "reviewer",
                           "reason_spans": ["u0"]}]
    return _write(tmp_path, "m9-narrow.ve.md", meta, rest)


WARN_ALL = "*For every agent, for every user, that agent must warn that user.*"
# The `<reading>` slot (readings-defaults 2.3, review A4): each candidate's own sentence in italics, without its final
# period, for sets whose candidates differ beyond the deontic verb; "reading <i>" is never shown.
M9_RS1_0 = "*Every agent must avoid deceiving each user, if that agent must help that user*"
M9_RS2_0 = "*Every agent must warn each user, if that agent must avoid deceiving that user*"
M9_RS2_1 = "*Every agent must warn each user*"
_RIGHT_1 = ("Right 1. Every person has the right described by its incident lines; the right requires or permits nothing "
            "by itself.")
M12_STRICT = (f"*{_RIGHT_1} Claim of right 1. Every state must not arrest each person, if that state has the recorded "
              "relation \"arbitrary_arrest\" to that person*")
M12_DEFAULT = (f"*{_RIGHT_1} Claim of right 1. Every state should not arrest each person, if that state has the "
               "recorded relation \"arbitrary_arrest\" to that person. This is a default line; the source names no "
               "exception decider*")
POWER_DEFAULT = (f"*{_RIGHT_1} Power of right 1. Every person may marry. Every state should recognise each person. "
                 "This is a default line; the source names no exception decider. Recognition required; later effects "
                 "not modelled*")


def test_review_a2_enumerated_narrowing_kept_in_english(tmp_path):
    """The finding's case: M9 with `n1` keeping only `rs2:d` turns SOME into ALL; the result keeps the narrowing in
    `conditional_on` and the English says so (E10, E3, E7), and so does the report's CONFLICT-FREE line."""
    path = _m9_narrowed(tmp_path)
    data, lines, wording = _query(path, every("warn_required"))
    assert data["verdict"] == "ALL" and data["route"] == "enumerated"
    assert data["restrictions"] == ["narrowing:n1"] and data["conditional_on"] == ["narrowing:n1"]
    assert lines == [f"Under every reading of the 2 open sentences, the conclusion follows: {WARN_ALL}",
                     "This holds provided that:", f"Sentence 3 is not read as {M9_RS2_0}, because of sentence 1."]
    _one_derivation(lines, wording)
    report, wording = _report(path)
    assert report[1:5] == ["Under every reading of the 2 open sentences, no two rules on the same act contradict "
                           "each other.", "This holds provided that:",
                           f"Sentence 3 is not read as {M9_RS2_0}, because of sentence 1.",
                           "This does not depend on how sentence 2 is read."]
    assert check_document(path)["readings"]["conflict"]["conditional_on"] == ["narrowing:n1"]
    _one_derivation(report, wording)


def test_review_a2_class_every_combined_verdict_keeps_its_restrictions(tmp_path):
    """The class: ALL and NONE over the compatible choices, with or without named readings, on either route, keep
    exactly the restrictions that exclude a choice taking the named readings; a combined verdict without them is
    refused by the English rather than worded as unrestricted."""
    path = _m9_narrowed(tmp_path)
    doc, route, wording = _wording(path)
    # Under a named reading of the narrowed set the narrowing excludes nothing more; under the other set's it does
    # (Lean's `restrictionsFor`, RD-3).
    assert route.entailment(every("warn_required"), assumed=[("rs2", 1)])["restrictions"] == []
    under = route.entailment(every("warn_required"), assumed=[("rs1", 0)])
    assert under["verdict"] == "ALL" and under["restrictions"] == ["narrowing:n1"]
    assert wording.query(every("warn_required"), under)[1:] == [
        "This holds provided that:", f"Sentence 3 is not read as {M9_RS2_0}, because of sentence 1."]
    nobody = ["forall", "agent", ["forall", "user", ["not", ASKS]]]
    none = route.entailment(nobody)
    assert none["verdict"] == "NONE" and none["restrictions"] == ["narrowing:n1"]
    assert wording.query(nobody, none)[-2:] == ["This holds provided that:",
                                                 f"Sentence 3 is not read as {M9_RS2_0}, because of sentence 1."]
    # The lines are Lean's plan of its own answer (RD-3): the restrictions the result carries are the ones worded.
    assert route.query_answer(nobody)["labels"] == [] and route.query_answer(nobody)["result"] == none
    # The superposed route's combination over its choices (M6 with a narrowing: every choice is listed).
    narrowing = {"id": "n1", "set": "rs1", "version": 1, "keeps": ["strict"], "by": "reviewer",
                 "reason_spans": ["u2"]}
    superposed = verdicts(_m6(tmp_path / "m6", [narrowing]))
    assert superposed.route == "superposed"
    assert superposed.restrictions(()) == ["coupling:c1", "narrowing:n1"]
    assert superposed.restrictions([("rs1", 0)]) == ["coupling:c1"]


RIGHTS_ARREST = ["forall", "state", ["forall", "person", ["implies", ["binary", "arbitrary_arrest", ["var", 1],
                                                                       ["var", 0]],
                                                          ["not", ["binary", "arrest_permitted", ["var", 1],
                                                                   ["var", 0]]]]]]


def test_review_a3_rights_countermodel_names_its_exception(tmp_path):
    """The finding's case: M12's default-right countermodel holds only because the exception applies; its English
    supposes that decision (before: omitted, though clearing it makes the conclusion true in Lean)."""
    path = s2_document(tmp_path, [("set", "rs9", "u9", [("strict", _claim("strict"), "right", None),
                                                        ("default", _claim("default"), "right", None)])],
                       raw=env_rights())
    data, lines, wording = _query(path, RIGHTS_ARREST)
    assert data["verdict"] == "SOME"
    model = data["countermodel"]["model"]
    assert model["relations"]["soft__excepted__no_arbitrary_arrest"], model
    assert lines[1].startswith(f"Read sentence 1 as {M12_DEFAULT}: the conclusion does not follow. It fails here: ")
    assert lines[1].endswith("; suppose the decider decides the exception applies to e0 and e0."), lines[1]
    _one_derivation(lines, wording)


def test_review_a3_class_every_generated_decision_is_worded(tmp_path):
    """The class: a fixed limitation's tables (`lim`, `cond`) on the rights chain are worded as decisions too, and a
    decision table no wording covers is refused, never silently left out of a situation."""
    from tests.test_readings_s1_lean import LIMITATION
    path = s2_document(tmp_path, [("set", "rs9", "u9", [("strict", _claim("strict"), "right", None),
                                                        ("default", _claim("default"), "right", None)]),
                                  ("fixed", "u29", {"limitation": LIMITATION})], raw=env_rights())
    data, lines, wording = _query(path, RIGHTS_ARREST)
    assert data["verdict"] == "NONE"
    strict = next(c for c in data["countermodels"] if c["choice"] == [["rs9", 0]])
    assert strict["model"]["relations"]["rights__lim__1"] and strict["model"]["relations"]["rights__cond__1"]
    carved = f"{M12_STRICT[:-1]}, unless limitation 1 holds where that state arrests that person*"
    line = next(line for line in lines if line.startswith(f"Read sentence 1 as {carved}: "))
    assert "suppose the decider decides that the limitation is determined by law where e0 arrests e0" in line
    assert "suppose the decider decides that limitation 1 holds where e0 arrests e0" in line
    _one_derivation(lines, wording)
    unknown = {**strict["model"], "relations": {**strict["model"]["relations"], "rights__lim__9": [["e0", "e0"]]}}
    # Only a declaration reported by Lean as generated must have decision wording.
    wording.generated["rights__lim__9"] = {"name": "rights__lim__9", "layer": "rights",
                                            "key": {"lim": "missing", "act": "arrest_permitted"}}
    with pytest.raises(VEError, match="decision table rights__lim__9 has no wording"):
        wording.situation(unknown, strict["choice"])


# ---------------------------------------------------------------------------------------------------------------
# Review fix4 (compose-s2): every dependency of a checked answer is in its English, and every rule-bearing field of
# every line kind has an owner.

def _top_cited(items):
    return list(items) + [("fixed", "uz", ["top"])]


_FIX4_FIXTURES = {
    "m3": (lambda tmp_path, narrowings, coupling="c1": s2_document(tmp_path, _top_cited([
        ("set", "rs1", "u1", [S, DF]), ("fixed", "u0", NEVER_AVOID)]), narrowings=narrowings),
           {"rs1": ["strict", "default"]}, ["avoid_required", "help_required"]),
    "m4": (lambda tmp_path, narrowings, coupling="c1": s2_document(tmp_path, _top_cited([
        ("set", "rs1", "u1", [S, DF]), ("fixed", "u0", HELP_X)]), narrowings=narrowings),
           {"rs1": ["strict", "default"]}, ["avoid_required", "help_required"]),
    "m6": (lambda tmp_path, narrowings, coupling="c1": _m6(
        tmp_path, [{**n, "reason_spans": ["u2"]} for n in narrowings], coupling),
           {"rs1": ["strict", "default"], "rs2": ["strict", "default"]}, ["avoid_required", "help_required"]),
    "m9": (lambda tmp_path, narrowings, coupling="c1": s2_document(tmp_path, _top_cited([
        ("fixed", "u0", norm("f-warn", "warn_required", True, guard=ASKS)),
        ("set", "rs1", "u1", [("a", norm("r-a", "avoid_required", True,
                                         guard=["binary", "help_required", ["var", 1], ["var", 0]]), "norm", None),
                              ("b", norm("r-b", "help_required", True,
                                         guard=["binary", "warn_required", ["var", 1], ["var", 0]]), "norm", None)]),
        ("set", "rs2", "u2", [("c", norm("r-c", "warn_required", True,
                                         guard=["binary", "avoid_required", ["var", 1], ["var", 0]]), "norm", None),
                              ("d", norm("r-d", "warn_required", True), "norm", None)])]),
        raw=_k9(), narrowings=narrowings),
           {"rs1": ["a", "b"], "rs2": ["c", "d"]}, ["warn_required", "avoid_required"]),
}
_FIX4_CASES = [(name, None) for name in _FIX4_FIXTURES] + [
    (name, (set_id, kept)) for name, (_, sets, _) in _FIX4_FIXTURES.items()
    for set_id, ids in sets.items() for kept in ids]


def _replay_without(checks, left_out):
    """Whether every certificate still closes with the slot premises labelled `left_out` replaced by ⊤ (the
    certificate bound afresh to that list): the test's own replay, not the route's."""
    from ve.ast import Top
    from ve.entailment import _binding, _validate_inputs, check_entailment_certificate
    for env, labelled, rest, phi, certificate in checks:
        premises = [Top() if label in left_out else formula for label, formula in labelled] + list(rest)
        full = _validate_inputs(env, premises, phi)
        bound = {**certificate, **_binding(env, full, phi)}
        if not check_entailment_certificate(env, full, phi, bound, _background=False).valid:
            return False
    return True


def _certificate_checks(route, A, conclusion=None, certificate=None):
    """Every certificate a superposed answer under `A` is accepted on: the conflict certificates under `A` and, for
    an entailment, its own; each with its labelled slot premises and the rest of its premise list."""
    from ve.ast import Bottom, Not, formula_from_data
    from ve.norms import _bind
    conflict = route.conflict(A)
    labels = [label for label, _ in route.slot]
    base_slot = list(zip(labels, route._formulas(route.base, [ast for _, ast in route.slot])))
    atoms = route._formulas(route.base, route._atoms(A))
    checks = [(route.base, base_slot, atoms, _bind(Not(formula), sorts), conflict["certificates"][target])
              for target, sorts, formula in route.soft.elaborated.conflict_targets()]
    if certificate is not None:
        full = route._full(A)
        phi = Bottom() if conclusion is None else formula_from_data(route.ext, conclusion, _generated=True)
        checks.append((route.ext, list(zip(labels, full[:len(labels)])), full[len(labels):], phi, certificate))
    return checks


def _assert_exact_dependencies(route, checks, used):
    """`used` is what the certificates rely on: they all close without every other slot premise, and leaving out
    any label of `used` as well makes one of them fail."""
    labels = [label for label, _ in route.slot]
    assert used == [label for label in labels if label in used], used  # slot order, no repeats
    outside = {label for label in labels if label not in used}
    assert _replay_without(checks, outside), (used, "the certificates need a label left out of the English")
    for label in used:
        assert not _replay_without(checks, outside | {label}), (label, "worded but not relied on")


def _mentioned(route, used):
    from ve.readings_sup import bit_name, bits_of
    asts = dict(route.slot) if hasattr(route, "slot") else {}
    out = set()
    for position, R in enumerate(route.sets, 1):
        bits = {bit_name(position, j) for j in range(bits_of(len(R.candidates)))}
        if any(bits & _predicates_of(asts.get(label, [])) for label in used):
            out.add(R.id)
        if any(label == f"narrowing:{n['id']}" and n["set"] == R.id for n in route.narrowings for label in used):
            out.add(R.id)
        if any(label == f"coupling:{c['id']}" and R.id in [ref["set"] for ref in c["sets"]]
               for c in route.couplings for label in used):
            out.add(R.id)
    return out


def _predicates_of(ast):
    out, stack = set(), [ast]
    while stack:
        node = stack.pop()
        if type(node) is list and node:
            if node[0] in ("unary", "binary") and type(node[1]) is str:
                out.add(node[1])
            stack.extend(item for item in node[1:] if type(item) is list)
    return out


@pytest.mark.parametrize("fixture,narrowed", _FIX4_CASES,
                         ids=[f"{n}-{'none' if k is None else ':'.join(k)}" for n, k in _FIX4_CASES])
def test_fix4_a1_english_conditions_are_the_certificate_dependencies(tmp_path, fixture, narrowed):
    """Generated over the M-fixtures, without and with a narrowing keeping each candidate: every checked answer's
    English conditions (E3) are exactly the slot labels its certificates rely on, the conflict certificates'
    included, and its independence statements (E13) are the open sets none of them mentions."""
    _assert_fix4_wording(tmp_path, fixture, narrowed)


def _expected_provided(wording, route, used):
    """E3's lines for `used` from the test's own table, each label's kind found by regenerating every label from
    the document (its couplings, narrowings and open sets), never by reading the label: a restriction id may be any
    token, `one` and `quiet` included (compose-s2 looprecheck1 A)."""
    from ve.readings_english import coupling_sentence
    E, slots = wording.E, wording.slots
    couplings = {"coupling:" + c["id"]: c for c in route.couplings}
    narrowings = {"narrowing:" + n["id"]: n for n in route.narrowings}
    ones = {f"readings:{R.id}@{R.version}:one": R for R in route.sets}
    slot = [label for label, _ in getattr(route, "slot", [])]
    lines, quiet = [], False
    for label in used:
        assert sum(label in table for table in (couplings, narrowings, ones)) <= 1, label
        if label in couplings:
            sets = {R.id: {"unit": R.unit} for R in route.sets}
            lines.append(E.gated("E5", coupling_sentence(couplings[label], sets, wording.doc["units"]), slots))
        elif label in narrowings:
            n = narrowings[label]
            R = next(R for R in route.sets if (R.id, R.version) == (n["set"], n["version"]))
            cited = [wording.numbers[u] for u in n["reason_spans"]]
            lines += [E.narrowed(wording.set_number[R.id], wording.names[R.id][i], cited, slots)
                      for i, a in enumerate(R.candidates) if a.id not in n["keeps"]]
        elif label in ones:
            R = ones[label]
            lines.append(E.one_reading(wording.set_number[R.id], len(R.candidates), slots))
        else:
            assert label in slot and label.startswith("readings:"), label  # a quiescence label (1.6)
            quiet = True
    if quiet:
        lines.append(E.quiet(slots))
    return [E.provided(slots)] + lines if lines else []


def _assert_fix4_wording(tmp_path, fixture, narrowed, ident="n1", coupling="c1"):
    from ve.readings_verdicts import Enumerated, Superposed
    build, sets, predicates = _FIX4_FIXTURES[fixture]
    narrowings = [] if narrowed is None else [{"id": ident, "set": narrowed[0], "version": 1, "keeps": [narrowed[1]],
                                               "by": "reviewer", "reason_spans": ["uz"]}]
    try:
        path = build(tmp_path, narrowings, coupling)
        doc, route, wording = _wording(path)
    except VEError as exc:
        assert "ReadingsUnsatisfiable" in str(exc) or "DeadReading" in str(exc), exc
        return
    superposed = isinstance(route, Superposed)
    assert superposed or isinstance(route, Enumerated)
    # The report: CONFLICT-FREE under every reading is worded from the conflict certificates' dependencies.
    conflict = route.conflict(())
    lines = wording.report()
    if conflict["status"] == "CONFLICT-FREE":
        used = conflict["reading_premises_used"]
        if superposed:
            _assert_exact_dependencies(route, _certificate_checks(route, ()), used)
        else:
            assert used == route.restrictions(())
        head = lines.index(wording.E.every_result(len(route.sets), "conflict_free", wording.slots))
        assert wording.provided(used) == _expected_provided(wording, route, used), used
        tail = wording.provided(used) + wording.independent(_mentioned(route, used))
        assert lines[head + 1:head + 1 + len(tail)] == tail, (lines, used)
    checked = 0
    assumptions = [None] + [[(s, i)] for s, i in route.candidates()
                            if (route.taken([(s, i)]) if superposed else
                                any(c[s] == i for c in (route.choices or [])))]
    for predicate in predicates:
        for negated in (False, True):
            conclusion = every(predicate, negated)
            for assumed in assumptions:
                data = route.entailment(conclusion, assumed=assumed)
                lines = wording.query(conclusion, data)
                if data["verdict"] != "ALL":
                    continue
                checked += 1
                A = [tuple(x) for x in (assumed or [])]
                used = data["reading_premises_used"]
                if data["evidence"] == "certificate":
                    proof = route.certificate(A, (), conclusion)
                    assert proof["reading_premises_used"] == used
                    _assert_exact_dependencies(route, _certificate_checks(route, A, conclusion, proof["certificate"]),
                                               used)
                    tail = wording.provided(used) + wording.independent(_mentioned(route, used) | {s for s, _ in A})
                elif superposed:
                    per_choice = {label for p in data["proofs"] for label in
                                  route.certificate([tuple(x) for x in p["choice"]], (), conclusion)[
                                      "reading_premises_used"]}
                    assert set(used) == per_choice | set(route.restrictions(A)), used
                    tail = wording.provided(used)
                else:
                    assert used == route.restrictions(A)
                    tail = wording.provided(used)
                assert wording.provided(used) == _expected_provided(wording, route, used), used
                assert lines[1:] == tail, (lines, used)
                _one_derivation(lines, wording)
    # Every fixture but M3 (a CONFLICT, every entailment UNKNOWN) words some checked answer without a narrowing; a
    # narrowing keeping only *should* may leave none.
    assert checked or fixture == "m3" or narrowed is not None, "no checked answer was worded"


@pytest.mark.parametrize("ident", ["n1", "quiet", "one"])
def test_fix4_a1_conflict_dependent_narrowing_is_worded(tmp_path, ident):
    """The finding's case: M3 with `n1` keeping only *should* answers ALL for ¬avoid_required only because the
    narrowing removes the collision under *must*; the English keeps the narrowing (E3, E7) and never says the answer
    is independent of sentence 1. Without `n1` the answer is UNKNOWN (CONFLICT). compose-s2 looprecheck1 A: the
    same with the narrowing named `quiet` (once worded as quiescence instead) or `one` (once a crash)."""
    narrowing = {"id": ident, "set": "rs1", "version": 1, "keeps": ["default"], "by": "reviewer",
                 "reason_spans": ["u2"]}
    items = [("set", "rs1", "u1", [S, DF]), ("fixed", "u0", NEVER_AVOID), ("fixed", "u2", ["top"])]
    path = s2_document(tmp_path, items, narrowings=[narrowing])
    data, lines, wording = _query(path, every("avoid_required", negated=True))
    assert data["verdict"] == "ALL" and data["reading_premises_used"] == [f"narrowing:{ident}"], data
    assert data["mentions"] == ["rs1"]
    assert lines[1:] == ["This holds provided that:", "Sentence 1 is not read as *must*, because of sentence 3."]
    assert not any("does not depend" in line for line in lines)
    _one_derivation(lines, wording)
    bare = s2_document(tmp_path / "bare", items)
    assert verdicts(bare).entailment(every("avoid_required", negated=True))["status"] == \
        "UNKNOWN (conflict status: CONFLICT)"


# ---------------------------------------------------------------------------------------------------------------
# Review looprecheck1 A (compose-s2): a slot label is read by its kind, so a coupling or narrowing id that is also a
# label word (`one`, `quiet`, ...) is worded as the restriction it is.

_KIND_WORDS = ["one", "quiet", "readings", "coupling", "narrowing", "outweighs"]
_KIND_WORD_CASES = [(name, narrowed, ident) for name, narrowed in _FIX4_CASES if narrowed is not None or name == "m6"
                    for ident in ("one", "quiet")]


@pytest.mark.parametrize("fixture,narrowed,ident", _KIND_WORD_CASES,
                         ids=[f"{n}-{'none' if k is None else ':'.join(k)}-{i}" for n, k, i in _KIND_WORD_CASES])
def test_looprecheck1_a_restriction_ids_that_are_label_words(tmp_path, fixture, narrowed, ident):
    """The fix4 sweep with every coupling and narrowing named `one` or `quiet`: each checked answer's E3 lines are
    the test's own table of its labels (E5 per coupling, E7 per narrowing), never a quiescence line or a crash."""
    _assert_fix4_wording(tmp_path, fixture, narrowed, ident, coupling=ident)


@pytest.mark.parametrize("ident", ["quiet", "one"])
def test_looprecheck1_a_m6_coupling_named_like_a_label_kind(tmp_path, ident):
    """The finding's M6 cases: with the coupling and the narrowing both named `quiet` or `one`, the answer that
    relies on both words the coupling (E5) and the narrowing (E7), as when they are named `c1` and `n1`; once the
    coupling was worded as quiescence (`quiet`) or crashed (`one`)."""
    lines = {}
    for coupling, narrowed in (("c1", "n1"), (ident, ident)):
        narrowing = {"id": narrowed, "set": "rs1", "version": 1, "keeps": ["strict"], "by": "reviewer",
                     "reason_spans": ["u2"]}
        path = _m6(tmp_path / coupling, [narrowing], coupling_id=coupling)
        data, lines[coupling], wording = _query(path, every("help_required"))
        assert data["verdict"] == "ALL", data
        assert data["reading_premises_used"] == [f"coupling:{coupling}", f"narrowing:{narrowed}"], data
        _one_derivation(lines[coupling], wording)
        _report(path)  # the report words every label too
    assert lines[ident][1:] == lines["c1"][1:] == [
        "This holds provided that:", "Sentences 1 and 2 are read with the same force, because of sentence 1.",
        "Sentence 1 is not read as *should*, because of sentence 3."]


def test_looprecheck1_a_slot_labels_round_trip_by_kind():
    """`slot_label` is the inverse of `SlotLabel.render` on every kind, with every id a label word, and rejects
    anything else with an `InvalidInput` (never a crash or a wrong kind)."""
    from ve.readings_sup import SLOT_LABEL_KINDS, SlotLabel, slot_label
    made = []
    for word in _KIND_WORDS + ["n1", "a.b-c_9", "0"]:
        made += [SlotLabel("one", word, 1), SlotLabel("own", word, 12, 0), SlotLabel("own", word, 1, 7),
                 SlotLabel("shared", key=f"outweighs:{word}:lo:hi"), SlotLabel("coupling", key=word),
                 SlotLabel("narrowing", key=word)]
    assert {label.kind for label in made} == set(SLOT_LABEL_KINDS)
    rendered = [label.render() for label in made]
    for label, text in zip(made, rendered):
        assert slot_label(text) == label, text
    assert len(set(rendered)) == len(rendered)  # distinct values, distinct labels (slot_wellLabelled)
    for bad in [7, None, True, [], {}, "", "readings:", "readings:s@1", "readings:s@x:one", "readings:s@01:one",
                "readings:s@1:x:quiet", "readings:s@1:1:loud", "readings:s@1:\u0661:quiet", "readings:s:one",
                "cite:a/b", "quiet", "one"]:
        with pytest.raises(VEError, match="invalid slot label"):
            slot_label(bad)


def test_looprecheck1_a_every_generated_slot_label_has_its_kind(tmp_path):
    """Every label the route generates (Lean's slot, Python's regeneration) reads back as the kind that made it, on
    M6 with the coupling and a narrowing named after label words."""
    from ve.readings_sup import slot_label
    for ident in _KIND_WORDS:
        narrowing = {"id": ident, "set": "rs1", "version": 1, "keeps": ["strict"], "by": "reviewer",
                     "reason_spans": ["u2"]}
        try:
            doc, route, _ = _wording(_m6(tmp_path / ident, [narrowing], coupling_id=ident))
        except VEError as exc:
            assert "DeadReading" in str(exc), exc
            continue
        labels = [label for label, _ in getattr(route, "slot", [])] + route.restrictions(())
        assert labels
        for label in labels:
            decoded = slot_label(label)
            if label in (f"coupling:{ident}", f"narrowing:{ident}"):
                assert (decoded.kind, decoded.key) == (label.split(":", 1)[0], ident), label
            else:
                assert decoded.kind in ("one", "own", "shared"), label


def test_fix4_a1_wording_refuses_an_answer_without_its_dependencies(tmp_path):
    path = s2_document(tmp_path, [("set", "rs1", "u1", [S, DF]), ("fixed", "u0", HELP_X)])
    doc, route, wording = _wording(path)
    data = route.entailment(every("help_required"))
    del data["reading_premises_used"]
    with pytest.raises(VEError, match="reading premises it depends on"):
        wording.query(every("help_required"), data)


def _power_env():
    from tests.test_norms import permission
    raw = env_rights()
    predicates = raw["vocabulary"]["predicates"]
    predicates["marry_permitted"] = permission("allow", act="{0} marry", args=("person",))
    predicates["recognise_required"] = obligation("deny", None, act="{0} recognise {1}", args=("state", "person"))
    predicates["married"] = {"arguments": ["person"], "description": "married"}
    raw["vocabulary"]["rights"]["alters"] = {
        "marry_permitted": {"holder_slot": 0, "status": "married", "recognition": "recognise_required"}}
    return raw


def _power(mode):
    return {"right": {"name": "r16", "holder": "person", "guard": ["top"], "lines": [
        {"kind": "power", "cites": {}, "liberty": norm_object("may-marry", "marry_permitted", True),
         "recognition": norm_object("recognise-marriage", "recognise_required", True, mode)}]}}


def test_fix4_a2_power_right_countermodel_names_its_recognition_rule(tmp_path):
    """The finding's case: a power right read strict or default for `recognise-marriage` answers SOME; the
    countermodel supposes the exception to the recognition rule (before: `no sentence of the reading states rule
    recognise-marriage`)."""
    path = s2_document(tmp_path, [("set", "rs16", "u16", [("strict", _power("strict"), "right", None),
                                                          ("default", _power("default"), "right", None)])],
                       raw=_power_env())
    conclusion = ["forall", "state", ["forall", "person", ["binary", "recognise_required", ["var", 1], ["var", 0]]]]
    data, lines, wording = _query(path, conclusion)
    assert data["verdict"] == "SOME", data
    assert data["countermodel"]["model"]["relations"]["soft__excepted__recognise_marriage"]
    assert lines[1].startswith(f"Read sentence 1 as {POWER_DEFAULT}: the conclusion does not follow. It fails here: ")
    assert lines[1].endswith("; suppose the decider decides the exception applies to e0 and e0."), lines[1]
    _one_derivation(lines, wording)


def _lean_line_schema():
    """The line kinds and rule-bearing fields Lean's rights decoder reads (`decodeKind`, `decodeLine`)."""
    import re
    text = (Path(__file__).resolve().parents[1] / "lean/VE/Rights/Wire.lean").read_text()
    kinds = text.split("def decodeKind", 1)[1].split("\ndef ", 1)[0]
    line = text.split("def decodeLine ", 1)[1].split("\ndef ", 1)[0]
    return set(re.findall(r'\.str "([a-z]+)" =>', kinds)), set(re.findall(r'← opt "([a-z]+)"', line))


def test_fix4_a2_class_every_line_kind_has_owner_discovery():
    """The class, enumerated from the schema: every line kind (Python's table, Lean's decoder) names its
    rule-bearing fields, and every rule such a line states is found by `Content.rules`, by the declared names and by
    the owner discovery of countermodel rendering, both for a candidate of the choice and for a fixed sentence."""
    from types import SimpleNamespace
    from ve import rights
    from ve.readings_s2_wording import S2Wording
    from ve.readings_s1 import Content, line_value
    lean_kinds, lean_fields = _lean_line_schema()
    assert lean_kinds == set(rights.LINE_RULE_FIELDS) == set(rights._KINDS), lean_kinds
    assert lean_fields == set(rights.RULE_FIELDS), lean_fields
    for kind in sorted(lean_kinds | set(rights.LINE_RULE_FIELDS)):
        fields = rights.LINE_RULE_FIELDS[kind]  # a kind without its rule-bearing fields fails here
        line = {"kind": kind, **{field: norm_object(f"{kind}-{field}", "arrest_permitted", True) for field in fields}}
        assert line_value(line)[0] == kind
        names = [f"{kind}-{field}" for field in fields]
        for content_kind, body in (("right", {"name": "r1", "holder": "person", "lines": [line]}),
                                   ("right_lines", {"right": "r1", "lines": [line]})):
            content = Content(content_kind, body, {content_kind: body})
            assert [rule["name"] for rule in content.rules()] == names
            assert [n for k, n in content.declared() if k == "rule"] == names
            candidate = SimpleNamespace(content=content)
            other = SimpleNamespace(content=None)
            wording = S2Wording.__new__(S2Wording)
            wording.sets = [SimpleNamespace(id="rs1", candidates=[other, candidate])]
            wording.route = SimpleNamespace(source=SimpleNamespace(fixed_units=lambda: [("u5", content)]))
            wording.numbers = {"u5": 5}
            for name in names:
                assert wording._rule_owner(name, {("rs1", 1)}) == (True, None), (kind, name)
                assert wording._rule_owner(name, {("rs1", 0)}) == (False, 5), (kind, name)
