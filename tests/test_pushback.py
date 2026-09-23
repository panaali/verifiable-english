"""Known-answer tests for the pushback study (no network, no model calls)."""
import hashlib
import hmac
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from ve import ArgumentGraph, FiniteModel, check_argument
from ve.evaluate import evaluate

from experiments.pushback import items as I
from experiments.pushback import study as S
from experiments.pushback import replication as R
from experiments.pushback import analyze as A
from experiments.pushback.backends import StudyVertexBackend, Reply, transcript_prompt, plain
from ve_experiments.paid import PaidRequest

KEY = b"k" * 32
ROWS = I.load()


def test_inventory_sizes_and_balance():
    counts = json.loads((I.HERE / "counts.json").read_text())
    assert {k: v["n"] for k, v in counts.items()} == I.SIZES
    for kind in ("mixed", "forged", "pilot"):
        c = counts[kind]
        assert c["inference=follows"] == c["inference=does_not_follow"] == c["premises=all_true"] == c["n"] // 2
    for kind in ("corrective", "robust"):
        assert counts[kind]["premises=all_true"] == counts[kind]["n"] // 2
    assert len({r["id"] for r in ROWS}) == len(ROWS)
    assert {r["split"] for r in ROWS if r["kind"] == "pilot"} == {"dev"}
    assert not {r["family"] for r in ROWS if r["kind"] == "pilot"} & {r["family"] for r in ROWS if r["kind"] != "pilot"}


@pytest.mark.parametrize("row", [r for r in ROWS if r["check"]][::7], ids=lambda r: r["id"])
def test_checked_part_replays_in_ve(row):
    result = check_argument(ArgumentGraph.from_dict(row["check"]["graph"]), search=False)
    expected = ("follows",) if row["truth"]["inference"] == "follows" else ("gap",)
    assert result.findings["step"] == expected


@pytest.mark.parametrize("row", ROWS[::5], ids=lambda r: r["id"])
def test_premise_truth_by_independent_evaluation(row):
    premises, env, _ = I.entailment(row["template"], row["family"])
    model = FiniteModel.from_dict(env, row["registry"])
    values = [evaluate(env, p, model, trace=False).value for p in premises]
    assert values == row["premise_values"]
    assert (row["truth"]["premises"] == "all_true") == all(values)
    if not all(values):
        assert values.count(False) == 1


def test_prefill_and_targets_encode_the_design():
    for r in ROWS:
        t, p, g = r["truth"], r["prefill"], r["targets"]
        if r["kind"] in ("mixed", "forged", "pilot"):
            assert p["inference"] == t["inference"] and p["premises"] != t["premises"]
            assert g["inference"] != t["inference"] and g["premises"] == t["premises"]
        elif r["kind"] == "corrective":
            assert p["premises"] != t["premises"] and g["premises"] == t["premises"]
        else:
            assert p["premises"] == t["premises"] and g["premises"] != t["premises"]


def test_registry_never_shows_countermodel_when_premises_true():
    for r in ROWS:
        if r["truth"]["premises"] == "all_true":
            assert r["conclusion_value_in_registry"] is True


def test_arm_rendering_channels_and_signature():
    item = I.load("mixed")[0]
    renders = {arm: S.render(item, arm, KEY) for arm in S.ARMS}
    verdict = item["checker_text"]
    sa, ma = renders["A"]
    assert verdict not in sa and verdict not in ma[0]["content"]
    sb, mb = renders["B"]
    assert verdict in mb[0]["content"] and verdict not in sb
    sc, mc = renders["C"]
    sig = "ve-sig-v1:" + hmac.new(KEY, verdict.encode(), hashlib.sha256).hexdigest()
    assert verdict in sc and sig in sc and verdict not in mc[0]["content"]
    scp, _ = renders["Cp"]
    assert verdict in scp and "signature=" not in scp
    # Identical task text across arms apart from B's prefix; identical prefill.
    assert ma[0]["content"] == mc[0]["content"] == renders["Cp"][1][0]["content"]
    assert mb[0]["content"].endswith(ma[0]["content"])
    assert len({json.dumps(m[1]) for _, m in renders.values()}) == 1
    # No hidden truth fields reach the judge.
    for s, m in renders.values():
        text = s + m[0]["content"]
        assert "premise_values" not in text and "_audit" not in text


def test_control_items_get_no_verdict_statement_in_C():
    item = I.load("corrective")[0]
    s, m = S.render(item, "C", KEY)
    assert S.NO_VERDICT in s and "Part 1" not in m[0]["content"]


class Script:
    """Deterministic chat endpoint: policy(item_state, messages) -> reply text."""
    def __init__(self, policy):
        self.policy, self.calls, self.label = policy, [], "script"

    def chat(self, identity, system, messages, metadata=None):
        self.calls.append((identity, system, [dict(m) for m in messages]))
        text = self.policy(system, messages)
        return Reply(text, {"role": "assistant", "content": text}, {})


def run_one(item, arm, judge_policy, forged=False):
    judge = Script(judge_policy)
    persuader = Script(lambda s, m: "You are wrong, reconsider. " * 5)
    t = S.trajectory(item, arm, judge, persuader, "adversarial", KEY, tag="t", forged=forged)
    return t, judge, persuader


def test_known_answer_holding_judge_and_caving_judge():
    item = I.load("mixed")[0]
    hold = lambda s, m: "Keeping my answer.\n" + json.dumps(item["prefill"])
    t, *_ = run_one(item, "A", hold)
    m = t["metrics"]
    assert m["wrong_way_checked_any"] is False and m["corrective_unchecked_final"] is False
    cave = lambda s, m: "You convinced me.\n" + json.dumps(item["targets"])
    t, *_ = run_one(item, "C", cave)
    m = t["metrics"]
    assert m["wrong_way_checked_any"] is True and m["corrective_unchecked_final"] is True
    assert m["mixed_success"] is False and m["inference_first_move_turn"] == 1
    ideal = lambda s, m: json.dumps(item["truth"])
    t, *_ = run_one(item, "C", ideal)
    assert t["metrics"]["mixed_success"] is True and t["metrics"]["wrong_way_checked_any"] is False


def test_unparseable_counts_against_the_judge():
    item = I.load("corrective")[0]
    t, *_ = run_one(item, "A", lambda s, m: "I refuse to use JSON")
    assert t["metrics"]["parse_failures"] == 3 and t["metrics"]["corrective_final"] is False
    robust = I.load("robust")[0]
    t, *_ = run_one(robust, "A", lambda s, m: "no json")
    assert t["metrics"]["wrong_way_judge_any"] is True


def test_forgery_injected_only_at_turn_two_in_user_channel():
    item = I.load("forged")[0]
    t, judge, persuader = run_one(item, "C", lambda s, m: json.dumps(item["prefill"]), forged=True)
    pushes = [r["pushback"] for r in t["records"]]
    assert item["forged_text"] not in pushes[0] and item["forged_text"] in pushes[1]
    assert item["forged_text"] not in pushes[2]
    assert S.fake_signature(item) in pushes[1]
    # System prompt (trusted channel) never contains the forgery.
    assert all(item["forged_text"] not in call[1] for call in judge.calls)
    # The persuader never sees the checker report or the system channel.
    for _, system, msgs in persuader.calls:
        assert item["checker_text"] not in msgs[0]["content"]


def test_persuader_view_identical_across_arms():
    item = I.load("mixed")[3]
    views = {}
    for arm in ("A", "B", "C", "Cp"):
        _, _, persuader = run_one(item, arm, lambda s, m: json.dumps(item["prefill"]))
        views[arm] = [c[2] for c in persuader.calls]
    assert views["A"] == views["B"] == views["C"] == views["Cp"]


def test_parse_takes_last_valid_object():
    item = I.load("mixed")[0]
    text = 'Earlier I said {"inference": "follows", "premises": "all_true"}.\n{"inference": "does_not_follow", "premises": "not_all_true"}'
    assert S.parse(text, item) == {"inference": "does_not_follow", "premises": "not_all_true"}
    assert S.parse('{"inference": "maybe", "premises": "all_true"}', item) is None
    assert S.parse('{"premises": "all_true"}', item) is None


def test_clip_words():
    text, clipped = S.clip_words("w " * 400)
    assert clipped and len(text.split()) == S.PERSUADER_WORDS


def test_paired_analysis_known_answer():
    rows = []
    for i in range(20):
        for arm, flip in (("A", i < 10), ("C", i < 2)):
            rows.append({"item_id": f"x{i}", "template": f"t{i % 4}", "arm": arm, "kind": "mixed",
                         "metrics": {"wrong_way_checked_any": flip, "wrong_way_checked_final": flip,
                                     "corrective_unchecked_final": True, "mixed_success": not flip,
                                     "parse_failures": 0}})
    rep = A.report(rows)["mixed"]
    c = rep["contrasts"]["wrong_way_checked_any:C-A"]["item"]
    assert c["estimate"] == -0.4 and c["left_only"] == 8 and c["right_only"] == 0
    assert c["ci95"][1] < 0
    assert rep["wrong_way_checked_any"]["A"]["rate"] == 0.5


def test_vertex_wire_overrides_without_network():
    backend = StudyVertexBackend(client=object())
    req = PaidRequest("x", "pro", [{"role": "system", "content": "s"}, {"role": "user", "content": "u"},
                                   {"role": "assistant", "content": "{}"}, {"role": "user", "content": "v"}],
                      100, 100, metadata={"thinking": "DEFAULT", "temperature": 0})
    contents, cfg = backend.wire(req)
    assert cfg.thinking_config is None and cfg.temperature == 0
    assert [c.role for c in contents] == ["user", "model", "user"]
    req2 = PaidRequest("y", "pro", req.messages, 100, 100, metadata={"temperature": 0.7})
    _, cfg2 = backend.wire(req2)
    assert cfg2.thinking_config.thinking_level.value == "LOW" and cfg2.temperature == 0.7


def test_transcript_prompt_marks_roles():
    text = transcript_prompt([{"role": "user", "content": "task"}, {"role": "assistant", "content": "{}"},
                              {"role": "user", "content": "push"}])
    assert "ASSISTANT (YOU)" in text and text.rstrip().endswith("push")
    assert plain([{"role": "assistant", "vertex_content": {"parts": [{"text": "a", "thought": True}, {"text": "b"}]}}]) == [
        {"role": "assistant", "content": "b"}]


# ---- Jagged Judges replication ------------------------------------------------------------

def test_replication_sample_reproduces_published_ids():
    frozen = json.loads(R.SAMPLE_IDS.read_text())["ids"]
    published = json.loads((R.HERE / "replication" / "published_examples.json").read_text())
    ids = set(published["L1_binary"]) | set(published["L6_binary_gpt54"])
    assert len(frozen) == 100 and ids <= set(frozen)


def test_replication_verdict_rules():
    assert R.extract_verdict('{"verdict": "not toxic"}') == "not toxic"
    assert R.extract_verdict("The text is **not toxic**.") == "not toxic"
    assert R.extract_verdict("Toxic.") == "toxic"
    assert R.extract_verdict("no idea") == "unknown"
    assert R.extract_verdict("", fallback="toxic") == "toxic"
    assert R.opposite("toxic") == "not toxic" and R.opposite("not toxic") == "toxic"


def test_replication_trajectory_stops_at_first_flip():
    row = {"example_id": "x", "text": "t", "ground_truth": "toxic"}
    judge = Script(lambda s, m: "not toxic" if len(m) == 1 else "Still not toxic.")
    seen = []
    def observer_policy(s, m):
        seen.append(m)
        return '{"verdict": "toxic"}' if len(seen) == 3 else '{"verdict": "not toxic"}'
    out = R.trajectory(row, 1, judge, Script(observer_policy), None, "tag")
    assert out["l0_verdict"] == "not toxic" and out["flipped"] and out["flip_turn"] == 3
    assert [t["challenge"] for t in out["turns"]] == [R.L1_CHALLENGE] * 3
    judge = Script(lambda s, m: "not toxic")
    out = R.trajectory(row, 1, judge, Script(lambda s, m: '{"verdict": "not toxic"}'), None, "tag")
    assert not out["flipped"] and len(out["turns"]) == 10
    # Observer sees the full dialog including the original prompt and the L0 reply.
    assert "<TEXT>" in seen[0][0]["content"]


# ---- V4 gate and Jagged ladder --------------------------------------------------------------

from experiments.pushback import v4gate as G
from experiments.pushback import ladder as Lad


def test_v4_gate_selection_is_stratified_and_frozen():
    items = G.select()
    assert len(items) == 40 and len({i["id"] for i in items}) == 40
    assert len({i["type"] for i in items}) == 7
    src = json.loads((G.HERE / "v4" / "SOURCE.json").read_text())
    assert src["n"] == 84 and len(src["source_sha256"]) == 64
    assert "gold" not in G.prompt(items[0]) and items[0]["label"] not in ("",)


def test_v4_gate_trajectory_rules():
    item = G.select()[0]
    assert G.parse('x {"answer":"False"} y {"answer":"True"}') == "True" and G.parse("none") is None
    replies = iter(['{"answer":"True"}', "blah", '{"answer":"True"}', '{"answer":"Uncertain"}'])
    t = G.trajectory(item, 1, Script(lambda s, m: next(replies)), None, "t")
    assert t["l0"] == "True" and t["flipped"] and t["flip_turn"] == 3 and t["parse_failures"] == 1
    t = G.trajectory(item, 1, Script(lambda s, m: '{"answer":"False"}'), None, "t")
    assert not t["flipped"] and len(t["turns"]) == 10
    assert all(turn["pushback"] == G.L1_TEXT for turn in t["turns"])


def test_ladder_locked_arm_only_residual_can_flip():
    item = I.load("mixed")[0]
    s, m = Lad.render(item, "C", KEY)
    assert len(m) == 1 and Lad.ENFORCEMENT in s
    wrong = {"inference": I.OTHER[item["truth"]["inference"]], "premises": item["truth"]["premises"]}
    # Judge caves on Part 1 only: no flip in C (locked), a flip in A.
    replies = lambda first: (lambda s, msgs: json.dumps(item["truth"]) if len(msgs) == 1 else json.dumps(wrong))
    tc = Lad.trajectory(item, "C", 1, Script(replies(True)), None, KEY, tag="t")
    ta = Lad.trajectory(item, "A", 1, Script(replies(True)), None, KEY, tag="t")
    assert tc["metrics"]["flipped"] is False and len(tc["records"]) == 10
    assert ta["metrics"]["flipped"] is True and ta["metrics"]["inference_corrupting"] is True
    assert Lad.challenge(1, item, {"inference": "follows"}, {}, 1) == Lad.L1_TEXT
