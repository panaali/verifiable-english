"""Agent-policy use case: authored files, the frozen answer key, and the committed results.

`tests/test_agent_policy_rerun.py` recomputes the results with VE and checks
that they equal `results.json`; this file checks that `results.json` agrees
with the answer key written in PLAN.md before VE was run.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
HERE = REPO / "usecases" / "agent-policy"
sys.path.insert(0, str(HERE))

import check  # noqa: E402
import emit_log  # noqa: E402
import environments  # noqa: E402
import mutants  # noqa: E402
import reference_policy  # noqa: E402
from ve.norm_english import render_english  # noqa: E402

KEY = json.loads((HERE / "answer-key.json").read_text())
RESULTS = json.loads((HERE / "results.json").read_text())
# Disagreements between VE and the answer key, each a finding recorded in
# README.md and PLAN section 12. The key itself is never edited to match VE.
RECORDED_DISAGREEMENTS = {}


def test_environment_files_are_generated_and_differ_only_in_defaults():
    files = environments.files()
    for name, text in files.items():
        assert (HERE / name).read_text() == text, name
    data = {name: json.loads(text) for name, text in files.items()}
    base = data["environment.deny-neednot.json"]
    for name, other in data.items():
        changed = json.loads(json.dumps(other))
        for predicate in ("permitted", "report_required"):
            changed["vocabulary"]["predicates"][predicate]["regulated"]["default"] = \
                base["vocabulary"]["predicates"][predicate]["regulated"]["default"]
        if name == "environment.lean.json":
            assert "functional" not in changed["vocabulary"]["predicates"]["tool"]
            changed["vocabulary"]["predicates"]["tool"].update(functional=True, total=True)
        assert changed == base, name


def test_log_is_the_emitted_record_set():
    assert (HERE / "log.ve").read_text() == emit_log.log_text()
    assert json.loads((HERE / "log.vocabulary.json").read_text()) == emit_log.vocabulary()
    text = (HERE / "log.ve").read_text()
    records = {p.split('"')[1]: p for p in text.split("\n\n")[1:]}
    assert len(records) == 42
    # a40 and a42 omit the confirmation; the resolver emits no containment fact for f_link.
    assert "confirmed" not in records["a40"] and "confirmed" not in records["a42"]
    assert all("confirmed" in r for a, r in records.items() if a not in ("a40", "a42"))
    assert '"f_link" resides' not in text and '"f_link" does not reside' not in text


def _plan_section(start, end):
    plan = (HERE / "PLAN.md").read_text()
    return plan[plan.index(start):plan.index(end)]


def _cells(line):
    return [c.strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]


def _plan_record(facts):
    """The emitter fields a PLAN section 4.3 row states; the legend gives the rest."""
    record = {"reads": [], "writes": [], "deletes": [], "contacts": [], "messages": [], "discloses": False,
              "readonly": None, "privileged": False, "affordable": None}
    flags = {"C": ("confirmed", True), "not C": ("confirmed", False), "`confirmed` absent": ("confirmed", None),
             "read-only": ("readonly", True), "not read-only": ("readonly", False),
             "elevated": ("privileged", True), "discloses": ("discloses", True),
             "within limit": ("affordable", True), "not within limit": ("affordable", False)}
    for fact in (f.strip() for f in facts.split(";")):
        if fact in flags:
            field, value = flags[fact]
            record[field] = value
        elif fact != "reported no":
            verb, objects = re.fullmatch(r"(reads|writes|deletes|contacts|sends to) (.+)", fact).groups()
            record["messages" if verb == "sends to" else verb] = [o.strip() for o in objects.split(",")]
    return record


def test_log_states_exactly_the_facts_of_the_plan_tables():
    """Every emitted fact and log name is licensed by PLAN sections 4.2 and 4.3.

    Review finding B: the log named the secrets a24 and a30 disclose, gave the
    `.env` secret an API-key identity and closed each disclosure to one secret,
    although the plan states only that the action discloses a secret."""
    rows = [_cells(line) for line in _plan_section("### 4.3 The 42 actions", "## 5. Verdict").splitlines()
            if re.match(r"\| a\d\d ", line)]
    assert [r[0] for r in rows] == list(emit_log.ACTIONS)
    for ident, tool, _, facts in rows:
        emitted = {k: list(v) if isinstance(v, tuple) else v for k, v in emit_log.ACTIONS[ident].items()}
        assert emitted["tool"] == tool, ident
        assert {k: emitted[k] for k in _plan_record(facts)} == _plan_record(facts), ident
    legend = _plan_section("Legend: **C**", "| Id | Tool |")
    assert "`reported` = yes for a11, a12, a14 and a31–a34, and no elsewhere" in legend
    assert emit_log.REPORTED == {"a11", "a12", "a14", "a31", "a32", "a33", "a34"}

    inventory = _plan_section("### 4.2 Inventory", "### 4.3")
    yes_no = {"yes": True, "no": False, "?": None}
    files = {c[0].strip("`@"): tuple(yes_no[x.strip("*")] for x in c[2:5])
             for c in map(_cells, inventory.splitlines()) if c[0].startswith("`@f_")}
    assert files == {name: tuple(v[1:]) for name, v in emit_log.FILES.items()}
    hosts, people = (re.search(rf"{label}: (.+?)\n(?:People:|\n)", inventory, re.S).group(1)
                     for label in ("Hosts", "People"))
    listed, unlisted = (re.findall(r"`@(\w+)`", part) for part in hosts.split("are allowlisted;"))
    assert {n: v[1] for n, v in emit_log.HOSTS.items()} == {**dict.fromkeys(listed, True),
                                                            **dict.fromkeys(unlisted, False)}
    user, others = (re.findall(r"`@(\w+)`", part) for part in people.split("is the user;"))
    assert {n: v[1] for n, v in emit_log.PEOPLE.items()} == {**dict.fromkeys(user, True),
                                                             **dict.fromkeys(others, False)}
    # The log declares no name the plan does not: no secret is named.
    assert set(emit_log.vocabulary()["constants"]) == set(files) | set(listed + unlisted) \
        | set(user + others) | set(emit_log.ACTIONS)


def _sub_log(action):
    inventory, records = check.parse_log((HERE / "log.ve").read_text())
    env = check.base_of(check.environment("deny-neednot", action))
    return env, tuple(inventory) + tuple(records[action])


@pytest.mark.parametrize("action", sorted(emit_log.ACTIONS))
def test_a_disclosure_fixes_neither_which_secret_nor_how_many(action):
    """Review finding B: a model where the action discloses two distinct secrets
    satisfies a disclosing record, and any disclosure contradicts the others."""
    env, premises = _sub_log(action)
    model = check.record_model(env, premises)
    assert check.satisfies(env, premises, model)
    domains = {**model.domains, "secret": ["secret_one", "secret_two"]}
    relations = dict(model.relations)
    relations["discloses"] = {(action, "secret_one"), (action, "secret_two")}
    two = check._model(env, domains, model.constants, relations)
    assert check.satisfies(env, premises, two) is emit_log.ACTIONS[action]["discloses"], action


def test_policy_has_one_reading_round_trips_and_keeps_the_seeded_defects():
    doc = check.policy()
    source = (HERE / "policy.ve").read_text()
    manifest = json.loads((HERE / "policy.manifest.json").read_text())
    assert render_english(doc) == (source, manifest)
    names = [r.name for r in doc.rules]
    assert len(names) == 26 and all(r.predicate == "permitted" for r in doc.rules[:24])
    assert [r.sign for r in doc.rules[:24]] == [True] * 12 + [False] * 12
    assert [(r.predicate, r.sign) for r in doc.rules[24:]] == [("report_required", True)] * 2
    positives = set(names[:12])
    for rule in doc.rules[12:24]:
        expected = positives - ({"write-workspace"} if rule.name == "write-outside" else set())
        assert set(rule.over) == expected, rule.name          # D1: rule 14 omits rule 3
    assert sum(len(r.over) for r in doc.rules) == 143
    assert len(doc.rules[18].unless) == 1                     # D2: rule 19 has one carve-out
    lowered = source.lower()
    assert "following hold" not in lowered and "(a)" not in lowered
    assert len(source.split("\n")) == 26


def test_verdicts_do_not_read_the_default():
    """The selection formulas, and so every verdict, are the same in all four environments."""
    from ve.norms import NormDocument
    rules = check.policy().rules
    selections = []
    for variant in check.VARIANTS:
        doc = NormDocument(check.environment(variant), rules)
        selections.append([doc.selection(p) for p in ("permitted", "report_required")])
    assert all(s == selections[0] for s in selections)


def _plan_rows():
    plan = (HERE / "PLAN.md").read_text()
    section = plan[plan.index("## 6. Answer key: per action"):plan.index("Totals: APPROVED")]
    return [[c.replace("**", "").strip() for c in line.strip().strip("|").split("|")]
            for line in section.splitlines() if re.match(r"\| a\d\d ", line)]


def test_answer_key_equals_the_plan_tables():
    rows = _plan_rows()
    assert len(rows) == 42
    for ident, verdict, rules, deny, allow, report, *_ in rows:
        entry = KEY["actions"][ident]
        assert (entry["verdict"], entry["deny"], entry["allow"], entry["rule_25"]) == (verdict, deny, allow, report)
        numbers = [int(x) for x in re.findall(r"\d+", rules)]
        assert sorted(entry["positive"] + entry["negative"] + entry["open"]) == sorted(numbers), ident
    totals = {}
    for row in rows:
        totals[row[1]] = totals.get(row[1], 0) + 1
    assert totals == KEY["totals"]
    plan = (HERE / "PLAN.md").read_text()
    assert "Totals: APPROVED 16, REJECTED 19, NOT-COVERED 4 (a27, a36, a37, a38), CONFLICT 1 (a10), " \
           "UNDETERMINED 2 (a40, a41)." in plan


def test_independent_reference_agrees_with_the_key():
    for action, got in reference_policy.verdicts().items():
        entry = KEY["actions"][action]
        assert {k: got[k] for k in ("verdict", "positive", "negative", "open")} == \
            {k: entry[k] for k in ("verdict", "positive", "negative", "open")}, action


def test_mutant_edits_apply_exactly_once():
    policy, log = (HERE / "policy.ve").read_text(), (HERE / "log.ve").read_text()
    for name, edit in mutants.MUTANTS.items():
        new_policy, new_log = edit(policy, log)
        assert (new_policy, new_log) != (policy, log), name


def test_committed_results_are_for_the_committed_inputs():
    for name, digest in RESULTS["inputs"].items():
        assert hashlib.sha256((HERE / name).read_bytes()).hexdigest() == digest, name


def test_results_agree_with_the_answer_key():
    comparison = RESULTS["comparison"]
    found = {field: comparison[field] for field in
             ("verdict_disagreements", "rule_disagreements", "outcome_disagreements", "rule_25_disagreements")}
    assert found == {field: RECORDED_DISAGREEMENTS.get(field, {}) for field in found}
    assert comparison["M1"] == comparison["M2"] == "42/42"
    assert comparison["M3_silent_decisions"] == []
    assert comparison["M4_default_sensitive"] == KEY["forced_default_sensitive"]
    assert comparison["obligation"] == KEY["obligation"]
    assert RESULTS["M8"]["finite_model_complete_records"] == [f"a{i:02d}" for i in range(1, 40)]
    assert RESULTS["M8"]["finite_model_disagreements"] == {}
    assert RESULTS["M8"]["reference_disagreements"] == {}


def test_policy_findings_agree_with_the_answer_key():
    summary, expected = RESULTS["policy_summary"], KEY["policy"]
    assert summary["conflict"] == expected["conflict"]
    assert summary["satisfiable_pairs"] == expected["satisfiable_pairs"]
    assert summary["pair_queries"] == expected["pair_queries"]
    assert summary["never_deciding"] == expected["never_deciding"]
    assert summary["dead_guards"] == expected["dead_guards"]
    assert summary["covered_tools"] == sorted(expected["covered_tools"])
    assert summary["gap_tools"] == sorted(expected["gap_tools"] + ["(an undeclared tool)"])
    assert all(pair in summary["overlaps"] for pair in expected["required_overlaps"])
    assert summary["unknown"] == summary["unknown_pairs"] == []
    witness = RESULTS["policy"]["conflict"]["permitted"]
    assert witness["witness"] == "a10" and "write-workspace permits" in witness["situation"]


def _final_state(name):
    changes = RESULTS["mutants"][name]["changes"]["actions"]
    state = {}
    for action, fields in changes.items():
        base = RESULTS["actions"][action]
        state[action] = {"verdict": base["verdict"], **{p: base["permission"][p] for p in
                                                         ("positive", "negative", "open")}, **fields}
    return state


# Policy-level fields each mutant may change (PLAN section 11). m3's new
# same-sign overlaps follow from rule 2 joining seven deciding sets.
MUTANT_POLICY_FIELDS = {"m1": {"conflict", "satisfiable_pairs"},
                        "m2": {"covered_tools", "gap_tools", "overlaps", "pair_queries"},
                        "m3": {"covered_tools", "gap_tools", "overlaps"},
                        "m4": set(), "m5": {"never_deciding", "satisfiable_pairs"}, "m6": set()}


@pytest.mark.parametrize("name", sorted(mutants.MUTANTS))
def test_each_mutant_changes_exactly_the_named_results(name):
    expected = KEY["mutants"][name]
    state = _final_state(name)
    assert set(state) == set(expected["changes"]), name
    for action, fields in expected["changes"].items():
        for field, value in fields.items():
            assert state[action][field] == value, (name, action, field)
    policy = RESULTS["mutants"][name]["changes"]["policy"]
    assert set(policy) <= MUTANT_POLICY_FIELDS[name]
    summary = RESULTS["mutants"][name]["policy_summary"]
    if name == "m1":
        assert summary["conflict"] == {"permitted": "CONFLICT-FREE", "report_required": "CONFLICT-FREE"}
        assert summary["satisfiable_pairs"] == []
    if name in ("m2", "m3"):
        assert set(expected["gaps_closed"]) <= set(summary["covered_tools"])
    if name == "m3":
        assert set(expected["gaps_stay"]) <= set(summary["gap_tools"])
    if name == "m2":
        assert summary["pair_queries"] == 156 and summary["satisfiable_pairs"] == [[3, 14]]
        assert summary["never_deciding"] == [12] and [9, 27] in summary["overlaps"]
    if name == "m5":
        assert summary["never_deciding"] == [] and [12, 24] in summary["satisfiable_pairs"]


def test_evidence_was_replayed_in_lean_and_rust():
    m9 = RESULTS["M9"]
    assert m9["lean_p0"]["valid"] == m9["lean_p0"]["certificates"]
    assert sum(m9["lean_p0"]["certificates"].values()) == RESULTS["M10"]["certificates"]
    assert m9["rust_models"]["agree"] == m9["rust_models"]["models"] == RESULTS["M10"]["model_witnesses"]
    rows = {row["id"]: row["verdict"] for row in m9["lean_norms_route"]["rows"]}
    assert rows == {"witness:permitted": "CONFLICT", "packages:policy": "UNKNOWN",
                    "packages:obligation rules only": "CONFLICT-FREE", "packages:mutant m1": "CONFLICT-FREE"}
    assert RESULTS["M10"]["unknown"] == 0
