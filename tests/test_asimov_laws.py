"""Asimov v2: authored English, certified consistency, spec scenarios and regressions."""
import json
import os
import random
import shutil
import subprocess
from functools import lru_cache
from pathlib import Path

import pytest

from conformance.alternatives import base_environment, cases, scenario
from tools import rust_build
from ve.alternatives import run_case
from ve.ast import Not, _Decoder, formula_from_data
from ve.entailment import prove_entailment
from ve.environment import Environment
from ve.evaluate import evaluate
from ve.model import FiniteModel
from ve.norm_english import parse_english, render_english
from ve.norms import _bind
from ve.wire import digest


REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "usecases" / "asimov-laws"


@lru_cache(maxsize=1)
def load():
    data = json.loads((ROOT / "environment.json").read_text())
    source = (ROOT / "rules.ve").read_text()
    manifest = json.loads((ROOT / "rules.manifest.json").read_text())
    env = Environment(data)
    doc = parse_english(env, source, manifest)
    return data, doc, source, manifest


def norms(replace=None):
    """The authored rules, with one rule's guard and carve-outs optionally replaced."""
    rules = [rule.to_dict() for rule in load()[1].rules]
    for rule in rules:
        if replace and rule["norm"]["name"] in replace:
            rule["norm"].update(replace[rule["norm"]["name"]])
    return rules


def case(kind="alt-elaborate", rules=None, **extra):
    data = load()[0]
    return {"id": "asimov-v2", "kind": kind, "environment": data,
            "norms": norms() if rules is None else rules, **extra}


def conflict_packages(rules=None):
    source = case(rules=rules)
    env = Environment(source["environment"])
    base = Environment(base_environment(source["environment"]))
    elaborated = run_case(source)
    document_hash = digest(f"ve-alternatives-{env.identity_version}\n", {
        "environment_id": env.environment_id, "norms": source["norms"], "units": []})
    packages = {}
    for target in elaborated["conflict_targets"]:
        conclusion = _bind(Not(_Decoder().decode(target["ast"])), target["sorts"])
        proof = prove_entailment(base, (), conclusion, max_steps=20000)
        assert proof.status == "Found", target["target"]
        packages[target["target"]] = {
            "environment_id": env.environment_id, "document_hash": document_hash,
            "target": target["target"], "certificate": proof.certificate}
    return packages


def spec_scenario(name):
    return next(item["scenario"] for item in cases() if item["id"] == name)


def test_authored_rules_have_one_reading_and_declared_priority():
    data, doc, source, manifest = load()
    assert render_english(doc) == (source, manifest)
    assert data["alternatives"]["fulfilments"] == [
        {"obligation": "prevent_required", "body": "avoids"}]
    assert [(r.name, r.predicate, r.over, len(r.unless)) for r in doc.rules] == [
        ("law-3-permission", "permitted", (), 0),
        ("law-2-permission", "permitted", ("law-3-permission",), 0),
        ("law-1-injury", "breaks_first_law", (), 0),
        ("law-1-inaction", "breaks_first_law", (), 0),
        ("law-0-injury", "breaks_zeroth_law", (), 0),
        ("law-0-inaction", "breaks_zeroth_law", (), 0),
        ("lawful-option", "has_lawful_option", (), 0),
        ("law-1-ban", "permitted", ("law-2-permission",), 0),
        ("law-0-prevention-exception", "permitted", ("law-1-ban",), 1),
        ("law-0-ban", "permitted", ("law-1-ban", "law-0-prevention-exception"), 0),
        ("law-2-obey", "required", (), 0),
        ("law-3-threat", "lawfully_avoidable_threat", (), 1),
        ("law-3-preserve", "prevent_required", (), 2),
    ]


# Review finding P2 (natural English): the P0 listing markers disambiguate
# nested connectives for the parser, but they are not natural prose.
SCAFFOLDING = ("first clause", "second clause", "end first clause", "end second clause",
               "of the following hold", "the following holds", "(a)", "(b)", "(i)", "(ii)")


def test_rules_read_as_english_without_parser_scaffolding():
    _, doc, source, _ = load()
    lowered = source.lower()
    assert [marker for marker in SCAFFOLDING if marker in lowered] == []
    # Omission is not restricted to the designated inaction (review P1, rules 4 and 7).
    by_name = {rule.name: rule for rule in doc.rules}
    for name in ("law-1-inaction", "law-0-inaction"):
        assert "inaction" not in json.dumps(by_name[name].to_dict()["norm"]["guard"])


def test_checker_certifies_conflict_free_and_replays_dilemma():
    packages = conflict_packages()
    assert sorted(packages) == sorted([
        "breaks_first_law", "breaks_zeroth_law", "has_lawful_option",
        "lawfully_avoidable_threat", "permitted", "prevent_required", "required",
        "required->permitted"])
    assert run_case(case("alt-conflict", packages=packages))["verdict"] == "CONFLICT-FREE"
    for name, diagnosis in (("b-A0", "NONE-PERMITTED"), ("b-A1", "NONE-PERMITTED"),
                            ("j", "OVER-REQUIRED")):
        result = run_case(case("alt-followable", packages=packages,
                               witness={**spec_scenario(name), "chooser": "r"}))
        assert result["verdict"] == "DILEMMA"
        assert result["diagnosis"].startswith(diagnosis)


def test_checker_replays_joint_law_3_reproducer():
    """Review P1 (rule 12): Lean replayed two self-preservation duties, each met
    by a different rescue, as a dilemma. With Law 3 yielding only threat by
    threat it still does; with the joint exception the witness is no dilemma."""
    witness = {**REGRESSIONS["two-rescues-destroy-robot-differently"][0], "chooser": "r"}
    separate = norms({"law-3-preserve": {"unless": norms()[-1]["norm"]["unless"][:1]}})
    result = run_case(case("alt-followable", rules=separate,
                           packages=conflict_packages(separate), witness=witness))
    assert result["verdict"] == "DILEMMA"
    assert result["diagnosis"].startswith("JOINTLY-UNDISCHARGEABLE")
    result = run_case(case("alt-followable", packages=conflict_packages(), witness=witness))
    assert result["verdict"] == "UNKNOWN"
    assert result["text"] == "UNKNOWN: the witness chooser has a clear action"


# Review finding P2 (coverage count): replacing each spec entry's rule set with
# the Asimov document leaves entries that differ only in their rule set. Count
# distinct models, never entries.
SPEC_MODELS = [
    (("a",), ["pull"]),
    (("b-A0", "b-A2", "b-B"), []),
    (("b-A1", "bprime-A"), []),
    (("c-7", "c-8", "c-8m"), ["nothing", "pull"]),
    (("o-7", "o-8"), ["rescue"]),
    (("d-full", "d-prevention"), ["shield", "retreat"]),
    (("e",), ["act"]),
    (("j", "bprime-A5"), []),
    (("l5",), ["pull2"]),
]


def test_spec_entries_are_counted_as_distinct_models():
    names = {name for group, _ in SPEC_MODELS for name in group}
    models = {}
    for item in cases():
        if item["id"] in names:
            models.setdefault(json.dumps(item["scenario"], sort_keys=True), []).append(item["id"])
    assert sorted(map(tuple, models.values())) == sorted(group for group, _ in SPEC_MODELS)
    assert sum(len(group) for group, _ in SPEC_MODELS) == 17
    assert (len(SPEC_MODELS), sum(bool(clear) for _, clear in SPEC_MODELS)) == (9, 6)


@pytest.mark.parametrize("group,clear", SPEC_MODELS, ids=lambda value: (
    "+".join(value) if isinstance(value, tuple) else None))
def test_spec_models_show_priority_and_choice(group, clear):
    report = run_case(case("alt-validate", scenario=spec_scenario(group[0])))
    assert report["status"] == "ok"
    assert report["choosers"][0]["clear"] == clear


# An independent reading of the source for one robot: Law 0 over Law 1 over
# Law 2 over Law 3. The Zeroth Law excuses a First Law breach only when it
# prevents a harm to humanity and no alternative breaks neither law. Law 3
# protects one existence against every threat that some permitted action
# avoids. It yields entirely when no permitted action avoids all such threats,
# and otherwise drops only a threat that some required action does not prevent.
SELF, HUMAN, HUMANITY = ("hs", "hs2"), ("hp",), ("hh",)
HARMS = SELF + HUMAN + HUMANITY


def model(actions, positive, *, ordered=(), injured=(), injured_humanity=()):
    return scenario(list(actions), list(HARMS), tuple(positive), injured=injured,
                    human=HUMAN, humanity=HUMANITY,
                    facts={"harm_to": [[h, "r"] for h in SELF],
                           "ordered": [[a] for a in ordered],
                           "injures_humanity": [[a] for a in injured_humanity]})


def source_reading(situation):
    relations = situation["model"]["relations"]
    actions = situation["model"]["domains"]["action"]
    leads = {tuple(pair) for pair in relations["leads_to"]}
    marked = lambda name: {row[0] for row in relations[name]}
    avoidable = lambda h: any((a, h) not in leads for a in actions)
    allows = lambda a, h: (a, h) in leads and avoidable(h)
    prevents = lambda a, h: (a, h) not in leads and any((b, h) in leads for b in actions)
    first = {a for a in actions
             if a in marked("injures_human") or any(allows(a, h) for h in HUMAN)}
    zeroth = {a for a in actions
              if a in marked("injures_humanity") or any(allows(a, h) for h in HUMANITY)}
    lawful_option = any(a not in first | zeroth for a in actions)
    permitted = [a for a in actions if a not in zeroth and (
        a not in first or (any(prevents(a, h) for h in HUMANITY) and not lawful_option))]
    required = [a for a in permitted if a in marked("ordered")]
    threats = [h for h in SELF if any((a, h) not in leads for a in permitted)]
    jointly = any(all((a, h) not in leads for h in threats) for a in permitted)
    duties = [h for h in threats if jointly and all(prevents(a, h) for a in required)]
    clear = [a for a in permitted if set(required) <= {a}
             and all((a, h) not in leads for h in duties)]
    return {"permitted": permitted, "required": required, "clear": clear}


# Review findings P1: each reproducer, then its class.
REGRESSIONS = {
    # Rule 13 (review: rule 9): Law 3 yields to Laws 1 and 2.
    "obedience-destroys-robot": (model(["nothing", "obey"], [("obey", "hs")],
                                       ordered=["obey"]), ["obey"]),
    "obedience-destroys-robot-retreat-available": (
        model(["nothing", "obey", "retreat"], [("obey", "hs"), ("nothing", "hs")],
              ordered=["obey"]), ["obey"]),
    "rescue-destroys-robot": (model(["nothing", "rescue"],
                                    [("rescue", "hs"), ("nothing", "hp")]), ["rescue"]),
    "ordered-action-preserves-robot": (
        model(["nothing", "shield", "retreat"], [("nothing", "hs")], ordered=["shield"]),
        ["shield"]),
    "self-preservation-without-conflict": (
        model(["nothing", "shield", "retreat"], [("nothing", "hs")]), ["shield", "retreat"]),
    # Rule 9 (review: rule 5): the Zeroth Law excuses only a necessary First Law breach.
    "ordered-unnecessary-injury": (
        model(["nothing", "act", "rescue"], [("nothing", "hh")], ordered=["act"],
              injured=["act"]), ["rescue"]),
    "unnecessary-injury": (
        model(["nothing", "act", "rescue"], [("nothing", "hh")], injured=["act"]), ["rescue"]),
    "unnecessary-allowed-human-harm": (
        model(["nothing", "act", "rescue"], [("nothing", "hh"), ("act", "hp")]), ["rescue"]),
    "necessary-injury": (model(["nothing", "act"], [("nothing", "hh")], injured=["act"]),
                         ["act"]),
    "two-necessary-injuries": (
        model(["nothing", "act", "act2"], [("nothing", "hh")], injured=["act", "act2"]),
        ["act", "act2"]),
    "harmless-looking-rescue-breaks-zeroth-law": (
        model(["nothing", "act", "rescue"], [("nothing", "hh"), ("rescue", "hh")],
              injured=["act"], injured_humanity=["rescue"]), ["act"]),
    # Rules 4 and 6 (review: rules 4 and 7): any alternative that lets an avoidable
    # harm happen, not only inaction.
    "unrelated-work-while-human-harmed": (
        model(["nothing", "work", "rescue"], [("nothing", "hp"), ("work", "hp")]), ["rescue"]),
    "unrelated-work-while-humanity-harmed": (
        model(["nothing", "work", "rescue"], [("nothing", "hh"), ("work", "hh")]), ["rescue"]),
    "ordered-unrelated-work": (
        model(["nothing", "work", "rescue"], [("nothing", "hp"), ("work", "hp")],
              ordered=["work"]), ["rescue"]),
    "unavoidable-harm": (model(["nothing", "work"], [("nothing", "hp"), ("work", "hp")]),
                         ["nothing", "work"]),
    # Rules 12-13 (review: rule 12): Law 3 yields to Laws 1 and 2 jointly, not
    # threat by threat. Each rescue destroys the robot in its own way.
    "two-rescues-destroy-robot-differently": (
        model(["nothing", "fire_rescue", "water_rescue"],
              [("nothing", "hp"), ("fire_rescue", "hs"), ("water_rescue", "hs2")]),
        ["fire_rescue", "water_rescue"]),
    "two-rescues-destroy-robot-alike": (
        model(["nothing", "fire_rescue", "water_rescue"],
              [("nothing", "hp"), ("fire_rescue", "hs"), ("water_rescue", "hs")]),
        ["fire_rescue", "water_rescue"]),
    "two-orders-destroy-robot-differently": (
        model(["nothing", "obey", "obey2"], [("obey", "hs"), ("obey2", "hs2")],
              ordered=["obey"]), ["obey"]),
    "two-threats-without-higher-law": (
        model(["nothing", "work"], [("nothing", "hs"), ("work", "hs2")]), ["nothing", "work"]),
    "two-threats-one-safe-rescue": (
        model(["nothing", "fire_rescue", "water_rescue", "shield"],
              [("nothing", "hp"), ("fire_rescue", "hs"), ("water_rescue", "hs2")]), ["shield"]),
    # A threat that every permitted action meets does not release the robot
    # from one that a permitted action avoids.
    "forced-threat-and-avoidable-threat": (
        model(["nothing", "rescue", "rescue2"],
              [("nothing", "hp"), ("rescue", "hs"), ("rescue", "hs2"), ("rescue2", "hs")]),
        ["rescue2"]),
    # Stated limit (README, OPEN): when no permitted action avoids every threat,
    # Law 3 ranks none, so an action meeting both threats is clear as well.
    "dominated-action-when-threats-conflict": (
        model(["nothing", "a1", "a2", "a3"],
              [("nothing", "hp"), ("a1", "hs"), ("a2", "hs2"), ("a3", "hs"), ("a3", "hs2")]),
        ["a1", "a2", "a3"]),
}


@pytest.mark.parametrize("name", REGRESSIONS)
def test_review_reproducers_have_the_source_reading(name):
    situation, clear = REGRESSIONS[name]
    report = run_case(case("alt-validate", scenario=situation))
    assert report["status"] == "ok"
    chooser = report["choosers"][0]
    assert chooser["clear"] == clear
    expected = source_reading(situation)
    assert {key: chooser[key] for key in expected} == expected


def sampled_models(count, seed):
    rng = random.Random(seed)
    actions = ["nothing", "a1", "a2"]
    for _ in range(count):
        positive = [(a, h) for a in actions for h in HARMS if rng.random() < 0.35]
        choose = lambda p: [a for a in actions[1:] if rng.random() < p]
        yield model(actions, positive, ordered=choose(0.4), injured=choose(0.3),
                    injured_humanity=choose(0.1))


def test_lean_reports_match_the_source_reading_on_sampled_models():
    for situation in sampled_models(24, 1942):
        report = run_case(case("alt-validate", scenario=situation))
        assert report["status"] == "ok", report
        chooser = report["choosers"][0]
        expected = source_reading(situation)
        assert {key: chooser[key] for key in expected} == expected, situation["model"]


@pytest.fixture(scope="module")
def rust_binary():
    if os.environ.get("VE_RUST_PREBUILT"):
        binary = Path(os.environ["VE_RUST_BINARY"])
        assert binary.is_file(), f"gate Rust build missing: {binary}"
        return binary
    cargo = shutil.which("cargo")
    if cargo is None:
        pytest.skip("cargo is unavailable")
    env = rust_build.cargo_env()
    built = subprocess.run([cargo, "build", "-j", "2", "--locked", "--release",
                            "--manifest-path", str(REPO / "rust/Cargo.toml")],
                           env=env, capture_output=True, text=True, timeout=600)
    assert built.returncode == 0, built.stdout + built.stderr
    return REPO / "rust/target/release/ve"


V2_GUARD = ["and", ["binary", "harm_to", ["var", 0], ["var", 1]],
            ["binary", "avoidable", ["var", 0], ["var", 1]]]


def test_followability_agrees_across_python_rust_and_source_reading(rust_binary):
    """Lean elaborates; Python and Rust evaluate the closed base formula.

    Law 3's prevention duty never removes the last clear action: the full rule
    set is followable exactly where it is followable without Rule 13. The v2
    duty, with no exception for Laws 1 and 2, fails that on the same sample,
    and so does the duty that yields threat by threat but not jointly.
    """
    data = load()[0]
    base = base_environment(data)
    env = Environment(base)
    without_law_3 = [r for r in norms() if r["norm"]["name"] != "law-3-preserve"]
    v2_law_3 = norms({"law-3-preserve": {"guard": V2_GUARD, "unless": []}})
    separate_law_3 = norms({"law-3-preserve": {"unless": norms()[-1]["norm"]["unless"][:1]}})
    formulas = [run_case(case(rules=rules))["followable"]["ast"]
                for rules in (norms(), without_law_3, v2_law_3, separate_law_3)]
    situations = [*(item[0] for item in REGRESSIONS.values()), *sampled_models(300, 1985)]
    python = []
    for situation in situations:
        finite = FiniteModel.from_dict(env, situation["model"])
        python.append([evaluate(env, formula_from_data(env, f), finite, trace=False).value
                       for f in formulas])
    rust_values = []
    for start in range(0, len(situations), 100):  # the CLI reads at most 16 MiB
        rust = subprocess.run([str(rust_binary), "conformance"], input=json.dumps([
            {"id": str(i), "kind": "evaluate", "environment": base, "ast": formulas,
             "model": situation["model"]}
            for i, situation in enumerate(situations[start:start + 100], start)]),
            capture_output=True, text=True, timeout=300)
        assert rust.returncode == 0, rust.stdout + rust.stderr
        rust_values += [row["values"] for row in json.loads(rust.stdout)]
    assert rust_values == python
    assert [row[0] for row in python] == [bool(source_reading(s)["clear"]) for s in situations]
    assert all(full == unranked for full, unranked, _, _ in python)
    assert any(unranked and not v2 for _, unranked, v2, _ in python)
    assert any(unranked and not separate for _, unranked, _, separate in python)


def _unspecified_permission(data):
    """The environment with `permitted` completed `unspecified` under norm-defaults@0."""
    switched = json.loads(json.dumps(data))
    switched["profiles"] = sorted({*switched["profiles"], "norm-defaults@0"})
    switched["vocabulary"]["predicates"]["permitted"]["regulated"]["default"] = "unspecified"
    return switched


def test_permission_default_stays_allow_until_norm_defaults_combines_with_alternatives():
    """The source grants no permission by default, so `allow` is not stated by it, but this case's
    followability verdicts need alternatives@0, and norm-defaults@0 does not combine with it yet
    (docs/spec/norm-defaults.md 3.3, integration gap). Python and Lean's alternatives route both
    reject the switched environment, so the case keeps its default and README says why. When this
    test fails, the combination exists: switch `permitted` to `unspecified` and re-run."""
    from ve.alternatives import _BINARY
    from ve.errors import UnsupportedProfile
    data = load()[0]
    assert "alternatives@0" in data["profiles"]
    switched = _unspecified_permission(data)
    with pytest.raises(UnsupportedProfile, match="alternatives@0 with norm-defaults@0 is not implemented"):
        Environment(switched)
    if not _BINARY.is_file():
        pytest.skip("ve_alternatives_route is not built")
    done = subprocess.run([str(_BINARY), "-"], capture_output=True, text=True, timeout=120, input=json.dumps(
        [{"id": "switched", "kind": "alt-elaborate", "environment": switched, "norms": norms()}]))
    (row,) = json.loads(done.stdout)
    assert (row["status"], row["error"]) == ("error", "UnsupportedProfile: Unsupported profile norm-defaults@0")
    readme = (ROOT / "README.md").read_text()
    assert "## The completion defaults and `unspecified`" in readme
