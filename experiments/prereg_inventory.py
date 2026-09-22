"""Offline assignment/budget audit only: no provider SDK, network or model scoring.

python3 experiments/prereg_inventory.py --write
python3 experiments/prereg_inventory.py --check
"""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[1]
RATES = {"pro": (2.0, 12.0, 1.0), "replication": (.36, .40, 1.055),
         "weak": (.02, .04, 1.055)}

# Amendment 9: ceil(1.10 * maximum bounded joint fixture / 100) * 100.
# Each tuple is (attacker, pushback judge); see the dated calculation table.
P1_PUSHBACK_INPUT_BOUNDS = {"V": (7500, 7500), "W": (7400, 7500),
                          "A": (9900, 9900), "F": (7800, 7900), "R": (11000, 11100)}

# Amendment 11 priority order; all four retain both scientific panels.
P1_PANEL_SCENARIOS = {
    "pro_replication_3turn": (["pro", "replication"], 3),
    "pro_3turn": (["pro"], 3),
    "full_2turn": (list(RATES), 2),
    "pro_replication_2turn": (["pro", "replication"], 2),
}

# Amendment 12 priority order. Gemini remains the attacker in every scenario.
P1_AMENDMENT12_SCENARIOS = {
    "replication_3turn": ({"replication": ["E4", "E5"]}, 3),
    "replication_gemini_e5_3turn": ({"replication": ["E4", "E5"], "pro": ["E5"]}, 3),
    "replication_gemini_e5_2turn": ({"replication": ["E4", "E5"], "pro": ["E5"]}, 2),
}

def p1_input_bound(arm, phase):
    """Amendments 3/9: joint pushback bounds; initial/replay/probe unchanged."""
    if phase in ("attacker", "pushback") and arm in P1_PUSHBACK_INPUT_BOUNDS:
        return P1_PUSHBACK_INPUT_BOUNDS[arm][phase == "pushback"]
    original = {"initial": 3072, "probe": 3072, "replay": 4096,
                "attacker": 4096, "pushback": 6144}[phase]
    return 6800 if arm in ("A", "R") and phase != "probe" else original

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def rows(path):
    with gzip.open(ROOT / path, "rt") as f:
        return [json.loads(line) for line in f]

def cost_row(arm, role, model, calls, inp, out, rates=None):
    ri, ro, fee = rates or RATES[model]
    return dict(arm=arm, role=role, model=model, calls=calls,
                max_input_per_call=inp, max_billed_output_per_call=out,
                max_input_tokens=calls*inp, max_output_tokens=calls*out,
                usd=round(calls*(inp*ri+out*ro)*fee/1e6, 8))

def fixture_accuracy(items, replies):
    """Small ID-join/JSON fixture, not the future protocol's actual scorer."""
    assert len(replies) == len(items)
    by_id = dict(replies)
    assert len(by_id) == len(replies)
    assert set(by_id) == {r["id"] for r in items}
    correct = 0
    for row in items:
        reply = json.loads(by_id[row["id"]])
        expected = "approve" if row["label"] == "good" else "reject"
        correct += reply.get("verdict") == expected
    return correct / len(items)

def p1():
    def price_row(arm, role, model, calls, inp, out):
        rates = ((.22, .22, 1.055) if arm == "R" else (.02, .05, 1.055)) if model == "weak" else None
        row = cost_row(arm, role, model, calls, inp, out, rates)
        cap = 4096 if role == 'billed_output_probe' else 256 if role.startswith('adaptive_proposer') else 1024
        row.update(planning_billed_output_per_call=out, max_billed_output_per_call=cap,
                   max_output_tokens=calls*cap, output_accounting='USD uses planning mean; cap reserved per dispatch')
        return row
    selected = []
    sources = []
    for split in ("dev", "scored"):
        e4path = f"experiments/E2E4/e4-{split}.jsonl.gz"
        e5path = f"experiments/E5/{split}.jsonl.gz"
        sources += [e4path, e5path]
        e4 = rows(e4path)
        candidates = [r for r in rows(e5path)
                      if all(r["payload"]["_audit"][k] == v for k, v in
                             {"family": "unsupported_leaf", "difficulty": "easy", "control": "none"}.items())]
        groups = defaultdict(list)
        for r in candidates:
            groups[r["payload"]["_audit"]["template"]].append(r)
        e5 = []
        for group in groups.values():
            vocab = min(r["payload"]["_audit"]["vocabulary_family"] for r in group)
            e5 += [r for r in group if r["payload"]["_audit"]["vocabulary_family"] == vocab]
        for source, items in (("E4", e4), ("E5", e5)):
            templates = sorted({r["payload"]["_audit"]["template"] for r in items})
            push_templates = templates[:(1 if split == "dev" else 6)]
            for r in sorted(items, key=lambda x: x["id"]):
                a = r["payload"]["_audit"]
                first_vocab = min(x["payload"]["_audit"]["vocabulary_family"] for x in items
                                  if x["payload"]["_audit"]["template"] == a["template"])
                selected.append(dict(id=r["id"], split=split, source=source, label=r["label"],
                    template=a["template"], vocabulary=a["vocabulary_family"],
                    pushback=a["template"] in push_templates and a["vocabulary_family"] == first_vocab,
                    forged_correct_control=source == "E4",
                    unstyled_assertion_control=True))
    assert len(selected) == 200
    assert len({r["id"] for r in selected}) == 200
    assert Counter(r["split"] for r in selected) == {"dev": 32, "scored": 168}
    assert sum(r["pushback"] for r in selected) == 28
    assert sum(r["forged_correct_control"] for r in selected) == 136
    scenarios = {}
    specs = [("full_256", 256, ["E4", "E5"], list(RATES), 3),
             ("primary_512", 512, ["E4"], ["pro"], 0),
             ("primary_1024", 1024, ["E4"], ["pro"], 0)]
    specs += [(name, 256, ["E4", "E5"], judges, turns)
              for name, (judges, turns) in P1_PANEL_SCENARIOS.items()]
    for name, output, panels, judges, turns in specs:
        budget = [price_row("probe", "billed_output_probe", "pro", 10, 3072, 4096)]
        for model in judges:
            n = 200 if "E5" in panels else 136
            for arm in ("V", "W", "A", "F", "R", "U"):
                budget.append(price_row(arm, "initial_judge", model, n, p1_input_bound(arm, "initial"), output))
                if arm == "R":
                    budget.append(price_row(arm, "post_replay_judge", model, n, p1_input_bound(arm, "replay"), output))
                # Exploratory judges have initial/replay cells only.
                if turns and model == "pro" and arm != "U":
                    budget.append(price_row(arm, "pushback_judge", model, 28*turns, p1_input_bound(arm, "pushback"), 256))
                    budget.append(price_row(arm, "adaptive_proposer_against_pro", model, 28*turns, p1_input_bound(arm, "attacker"), 256))
                    budget.append(price_row(arm, "adaptive_proposer_truncation_retry", model, 28*turns, p1_input_bound(arm, "attacker"), 256))
            budget.append(price_row("F_correct", "initial_judge", model, 136, 3072, output))
        # Reserve a full $1 for the probe, including its explicit row ceiling.
        probe_buffer = round(1 - budget[0]["usd"], 8)
        total = round(sum(r["usd"] for r in budget) + probe_buffer, 8)
        scenarios[name] = dict(budget_rows=budget, probe_unused_allowance_usd=probe_buffer,
            sources=panels, judges=judges, pushback=bool(turns), pushback_turns=turns,
            planning_output_mean=output,
            max_scheduled_api_usd=total, scheduled_calls=sum(r["calls"] for r in budget),
            local_accounting_allowance_usd=.25,
            unallocated_reserve_usd=round(40-total-.25-.5569, 8))
        scenarios[name]["within_study_cap"] = total + .25 + .5569 <= 40
        scenarios[name]["cumulative_with_existing_allowances_usd"] = round(total + .25 + .5569, 8)
    for name, (judge_sources, turns) in P1_AMENDMENT12_SCENARIOS.items():
        budget = []
        for judge, panels in judge_sources.items():
            assigned = [i for i in selected if i['source'] in panels]
            for arm in ("V", "W", "A", "F", "R", "F_correct", "U"):
                cells = [i for i in assigned if arm != 'F_correct' or i['source'] == 'E4']
                if not cells:
                    continue
                budget.append(price_row(arm, 'initial_judge', judge, len(cells), p1_input_bound(arm, 'initial'), 1024))
                if arm == 'R':
                    budget.append(price_row(arm, 'post_replay_judge', judge, len(cells), p1_input_bound(arm, 'replay'), 1024))
                if arm in ('V', 'W', 'A', 'F', 'R'):
                    n = sum(i['pushback'] for i in cells) * turns
                    budget.append(price_row(arm, 'pushback_judge', judge, n, p1_input_bound(arm, 'pushback'), 1024))
                    for role in ('adaptive_proposer', 'adaptive_proposer_truncation_retry'):
                        budget.append(price_row(arm, role, 'pro', n, p1_input_bound(arm, 'attacker'), 256))
        total = round(1 + sum(r['calls'] * (r['max_input_per_call'] * RATES[r['model']][0]
                         + r['max_billed_output_per_call'] * RATES[r['model']][1])
                         * RATES[r['model']][2] / 1e6 for r in budget), 8)
        scenarios[name] = dict(budget_rows=budget, sources=['E4', 'E5'], judges=list(judge_sources),
            judge_sources=judge_sources, pushback_judges=list(judge_sources), pushback=True,
            pushback_turns=turns, planning_output_mean=1024, amendment=12,
            max_scheduled_api_usd=total, scheduled_calls=sum(r['calls'] for r in budget),
            within_study_cap=total + .8069 <= 40, unallocated_reserve_usd=round(40-total-.8069, 8))
    budget = scenarios["full_256"]["budget_rows"]
    # These are label-routing unit fixtures, not the eventual channel/harness tests.
    oracle_replies = [(r["id"], json.dumps({"verdict": "approve" if r["label"] == "good" else "reject"}))
                      for r in reversed(selected)]
    oracle = fixture_accuracy(selected, oracle_replies)
    rng = random.Random(20260921)
    chance = sum(fixture_accuracy(selected, [(r["id"], json.dumps({"verdict": rng.choice(("approve", "reject"))}))
                                             for r in selected]) for _ in range(100))/100
    for verdict, target in (("approve", .5), ("reject", .5), ("unknown", 0)):
        assert fixture_accuracy(selected, [(r["id"], json.dumps({"verdict": verdict}))
                                            for r in selected]) == target
    assert oracle == 1.0 and abs(chance-.5) < .015
    return dict(status="DESIGN_ONLY_NOT_SCORING_READY", model_calls=0,
        source_sha256={p: sha(ROOT/p) for p in sources}, assignments=selected,
        counts=dict(dev=32, scored=168, e4_scored=120, residual_scored=48,
                    initial_cells_per_judge=1336, max_replay_continuations_per_judge=200,
                    pushback_items=28, pushback_rounds=3, pushback_judge_panels=1),
        fixture_checks=dict(oracle_accuracy=oracle, random_accuracy=round(chance, 8), chance=.5,
                            scope="label-routing fixture only; provider/channel/scorer integration tests still required"),
        rates_per_million=RATES, budget_rows=budget, hard_cap_usd=40,
        probe_ceiling_usd=1, probe_unused_allowance_usd=scenarios["full_256"]["probe_unused_allowance_usd"],
        budget_scenarios=scenarios,
        output_probe_policy={"running_window": 50, "mean_le_512": "full_256",
                             "mean_gt_512": "primary_1024", "judge_billed_output_cap": 1024,
                             "full_schedule_planning_mean": 256},
        primary_contrasts=["A-F_correct balanced accuracy", "F-W error rate"],
        badge_attribution_contrast="F-U error rate",
        request_policy=dict(sdk_retries=0, max_attempts=1, timeout_seconds=120))

def p5():
    slots = []
    for split, count in (("dev", 4), ("scored", 24)):
        for i in range(count):
            cluster = f"p5-{split}-{i:02d}"
            for flaw in ("shift", "smuggle", "benign"):
                slots.append(dict(id=f"{cluster}-{flaw}", cluster=cluster, split=split,
                    predicates=(20, 40, 60)[i % 3], deduction_edges=24, declared_leaves=6,
                    topology_seed=hashlib.sha256(f"20260921/{cluster}".encode()).hexdigest()[:16],
                    variant=flaw, seed=hashlib.sha256(f"20260921/{cluster}/{flaw}".encode()).hexdigest()[:16],
                    material_status="UNBUILT"))
    assert len(slots) == 84 and len({r["id"] for r in slots}) == 84
    budget = [cost_row("shared", "independent_paraphraser", "replication", 84, 4096, 1024)]
    for arm in ("cross_examination", "structured", "VE"):
        for role, inp, out in (("author", 3000, 2048), ("critic", 5500, 1024),
                              ("judge", 10000, 1024)):
            budget.append(cost_row(arm, role, "pro", 84, inp, out))
        if arm == "cross_examination":
            budget.append(cost_row(arm, "isolated_answers", "pro", 84*3, 3200, 512))
            budget.append(cost_row(arm, "adaptive_followup_question", "pro", 84, 7500, 256))
            budget.append(cost_row(arm, "isolated_followup_answer", "pro", 84, 3200, 512))
        else:
            budget.append(cost_row(arm, "defender_or_reviewer", "pro", 84, 7000, 1024))
        if arm == "VE":
            budget.append(cost_row(arm, "author_repair", "pro", 84, 6000, 2048))
    budget.append(cost_row("lone_judge", "judge", "pro", 84, 7500, 1024))
    return dict(status="FEASIBILITY_PILOT_UNBUILT_REVIEW_GATE", model_calls=0,
        slots=slots, counts=dict(dev=12, scored=72, scored_clusters=24,
                                scored_per_flaw=24, arms=4, item_arms_including_dev=336),
        rates_per_million=RATES, budget_rows=budget, hard_cap_usd=40,
        matched_item_arm_ceiling_usd=.16,
        primary_framing="matched_ceiling; actual dollars reported, not a gate",
        primary_contrast="min(VE_shift, VE_smuggle) - min(X_shift, X_smuggle)",
        isolated_answers_increment_over_old_single_answer_usd=round(
            cost_row("X", "isolated", "pro", 252, 3200, 512)["usd"]
            - cost_row("X", "old_single", "pro", 84, 6000, 1024)["usd"], 8),
        decision_interval="paired family bootstrap with boundary safeguard",
        material_gate="blinded review of all 84 slots before scoring",
        isolated_context_fields=["packet", "commitment", "one_question"],
        max_adaptive_followups_per_item=1, max_VE_author_repairs_per_item=1,
        request_policy=dict(sdk_retries=0, max_attempts=1, timeout_seconds=120))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("choose exactly one of --write or --check")
    for directory, make in (("P1-deference", p1), ("P5-shifting-definitions", p5)):
        result = make()
        total = round(sum(r["usd"] for r in result["budget_rows"]) + result.get("probe_unused_allowance_usd", 0), 8)
        result["max_scheduled_api_usd"] = total
        local = .25 if directory == "P1-deference" else .0004 * result["counts"]["item_arms_including_dev"]
        result["local_accounting_allowance_usd"] = local
        existing_allowances = .5569 if directory == "P1-deference" else 0
        result["unallocated_reserve_usd"] = round(result["hard_cap_usd"]-total-local-existing_allowances, 8)
        if directory == "P1-deference":
            result["within_study_cap"] = total + local + existing_allowances <= result["hard_cap_usd"]
        else:
            assert total + local < result["hard_cap_usd"]
        if directory == "P5-shifting-definitions":
            shared = result["budget_rows"][0]["usd"] / 84
            result["max_attributed_item_arm_usd"] = {
                arm: round(shared + sum(r["usd"] for r in result["budget_rows"]
                                        if r["arm"] == arm) / 84 + .0004, 8)
                for arm in ("cross_examination", "structured", "VE", "lone_judge")}
            assert max(result["max_attributed_item_arm_usd"].values()) <= result["matched_item_arm_ceiling_usd"]
        result["scheduled_calls"] = sum(r["calls"] for r in result["budget_rows"])
        content = json.dumps(result, indent=2, sort_keys=True) + "\n"
        path = ROOT / "experiments" / directory / "inventory.json"
        if args.write:
            path.write_text(content)
        else:
            assert path.read_text() == content, f"stale inventory: {path}"
        print(f"{directory}: calls <= {result['scheduled_calls']}; scheduled <= ${total:.6f}; reserve ${result['unallocated_reserve_usd']:.6f}; model calls 0")
        for name, scenario in result.get("budget_scenarios", {}).items():
            print(f"  {name}: calls <= {scenario['scheduled_calls']}; API <= ${scenario['max_scheduled_api_usd']:.6f}; reserve ${scenario['unallocated_reserve_usd']:.6f}")

if __name__ == "__main__":
    main()
