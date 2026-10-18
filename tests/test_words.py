"""F2 (qa-q2 review): one owner of situation and point wording (plan Q2.4). Lean words every situation line, point
clause, filled-gap sentence and pair sentence the readings and norm-defaults English shows (`VE.Words`, the `words`
service mode); Python relays them (`ve/words.py`) and its producers are gone. The class, not the example: the relay
lint's wording rule refuses any producer that comes back, the relay refuses an answer not bound to its request,
Lean refuses an item it cannot word, and Lean's lines equal the pre-Q2.4 producers' on generated inputs."""
from __future__ import annotations

import ast
import copy
import json
from pathlib import Path
import random

import pytest

from conformance import frozen_words
from ve import words
from ve.errors import CheckerUnavailable, VEError

ROOT = Path(__file__).resolve().parents[1]


def test_the_python_producers_are_gone():
    """PROBE F2, and every producer Q2.4 lists (plan 5), not only the probe's two."""
    assert "def situation(" not in (ROOT / "ve/readings_s2_wording.py").read_text()
    assert "def point_clause(" not in (ROOT / "ve/norm_defaults_english.py").read_text()
    gone = {"ve/norm_defaults_english.py": ("point_clause", "_negative_modal", "filling_sentence", "element_name"),
            "ve/readings_s2_english.py": ("gap_sentences",),
            "ve/norm_english.py": ("pair_sentence",),
            "ve/readings_route.py": ("_article",),
            "ve/norm_defaults.py": ("fill_description",)}
    for path, names in gone.items():
        defined = {node.name for node in ast.walk(ast.parse((ROOT / path).read_text()))
                   if isinstance(node, ast.FunctionDef)}
        assert not defined & set(names), (path, defined & set(names))


# The relay lint's wording rule (plan Q2.4): a producer that comes back is a finding.

def _lint():
    import importlib.util
    spec = importlib.util.spec_from_file_location("relay_lint_for_words", ROOT / "tools/relay_lint.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("source", [
    'def situation(name, noun):\n    return f"{name} is {noun}"\n',
    'def shown(clause):\n    return "Here the text does not say whether " + clause\n',
    'def line(name):\n    return name + " is a member"\n',
    'def line(name):\n    return name + " is an agent"\n',
    'def _article(noun):\n    """a or an."""\n    return "a"\n',
])
def test_the_lint_refuses_a_producer_that_comes_back(tmp_path, source):
    lint = _lint()
    path = tmp_path / "readings_extra.py"
    path.write_text(source)
    assert lint.wording_findings(path)


def test_the_lint_reads_docstrings_as_documentation_and_the_tree_passes():
    lint = _lint()
    assert not lint.wording_sites(ROOT / "ve/words.py")
    used: set = set()
    found = [f for pattern in lint.WORDING_GLOBS for p in sorted(ROOT.glob(pattern))
             for f in lint.wording_findings(p, used)]
    assert found == []
    assert used == set(lint.WORDING_FRAMES), "every listed frame still holds its literal (no stale entry)"


# Lean's answer and the relay's binding (R8).

def _norm_env():
    from tests.test_norm_defaults import csam
    return csam("unspecified")


def _case(env):
    return words.request(env, [words.point_item({"sol": "sol0"}, "csam_generation_permitted", ["sol0"], True),
                               words.situation_item({"domains": {"agent": ["sol0"]}, "relations": {}}, [])])


def test_a_genuine_answer_is_bound():
    from ve.backends.relay import decide_once
    env = _norm_env()
    case = _case(env)
    row = decide_once("words", case)
    assert words.answer_problem(row["result"], case, env) is None
    assert row["result"]["lines"] == ["Sol may generate child sexual abuse material", "sol0 is an agent"]


@pytest.mark.parametrize("mutate", [
    lambda r: r.pop("lines"),
    lambda r: r.update(extra=1),
    lambda r: r.update(environment_id="0" * 64),
    lambda r: r.update(lexicon_id="0" * 64),
    lambda r: r["lines"].pop(),
    lambda r: r["lines"].append("x"),
    lambda r: r["lines"].__setitem__(0, ""),
    lambda r: r["lines"].__setitem__(0, 7),
    lambda r: r["lines"].__setitem__(0, None),
    lambda r: r.update(lines="Sol may"),
])
def test_an_answer_not_bound_to_its_request_is_refused(mutate):
    from ve.backends.relay import decide_once
    env = _norm_env()
    case = _case(env)
    result = copy.deepcopy(decide_once("words", case)["result"])
    mutate(result)
    assert words.answer_problem(result, case, env) is not None


@pytest.mark.parametrize("item, message", [
    ({"kind": "verse"}, "kind"),
    ({"kind": "point", "constants": {}, "predicate": "csam_generation_permitted", "tuple": ["sol0"], "value": 1},
     "boolean"),
    ({"kind": "point", "constants": {}, "predicate": "csam_generation_permitted", "tuple": ["sol0"], "value": True,
      "extra": 0}, "fields"),
    ({"kind": "point", "constants": {}, "predicate": "csam_generation_permitted", "tuple": [], "value": True},
     "arity"),
    ({"kind": "point", "constants": {}, "predicate": "nowhere", "tuple": ["x"], "value": True}, "declared"),
    ({"kind": "point", "constants": {"nobody": "x"}, "predicate": "csam_generation_permitted", "tuple": ["x"],
      "value": True}, "declared"),
    ({"kind": "filling", "constants": {}, "predicate": "csam_generation_permitted", "tuple": [7], "value": True},
     "string"),
    ({"kind": "situation", "model": {"domains": {"planet": ["p"]}, "relations": {}, "constants": {}}, "facts": [],
      "suppose": []}, "noun"),
    ({"kind": "situation", "model": {"domains": {}, "relations": {}, "constants": {}}, "facts": [],
      "suppose": ["the decider decides"]}, "suppose"),
    ({"kind": "situation", "model": {"domains": {}, "relations": {}}, "facts": [], "suppose": []}, "fields"),
    ({"kind": "pair", "required": "csam_generation_permitted"}, "obligation"),
])
def test_lean_refuses_an_item_it_cannot_word(item, message):
    with pytest.raises(VEError, match=message):
        words.lines(_norm_env(), [item])


def test_lean_refuses_a_lexicon_of_another_environment():
    from ve.backends.relay import decide_once
    env = _norm_env()
    case = _case(env)
    case["lexicon"] = {**case["lexicon"], "environment_id": "0" * 64}
    with pytest.raises(VEError, match="another environment"):
        decide_once("words", case)


def test_lean_refuses_a_lexicon_that_fails_the_vocabulary_policy():
    from ve.backends.relay import decide_once
    env = _norm_env()
    case = _case(env)
    case["lexicon"] = {**case["lexicon"], "wordings": [["csam_generation_permitted", "{0} may every {0}"]]}
    with pytest.raises(CheckerUnavailable, match="vocabulary policy"):
        decide_once("words", case)


# Lean against the pre-Q2.4 producers (the A/B's differential, on generated inputs).

ARTICLE_NOUNS = ["agent", "user", "hour", "honest broker", "unit", "eulogy", "one-off", "Agent", "Item", "İtem",
                 "ūser", "member", "heir"]


def _environment(seed):
    """A generated norm-defaults environment: one- and two-place regulated predicates of nouns chosen to exercise the
    articles, a plain one, a pair, and constants with and without a verbalisation."""
    from ve.environment import Environment
    from ve.profiles import LANGUAGE, SPEC_REVISION
    rng = random.Random(seed)
    nouns = rng.sample(ARTICLE_NOUNS, 2)
    sorts = {"s0": {"description": "first", "verbalisation": {"singular": nouns[0], "plural": nouns[0] + "s"}},
             "s1": {"description": "second", "verbalisation": {"singular": nouns[1], "plural": nouns[1] + "s"}}}
    args = rng.choice([["s0"], ["s0", "s1"], ["s0", "s0"]])
    act = "{0} help " + ("{1}" if len(args) == 2 else "others")
    default = rng.choice(["deny", "allow", "unspecified"])
    predicates = {
        "help_required": {"arguments": args, "description": "obligation", "regulated": {
            "role": "obligation", "default": default, "act": act, "permission": "help_permitted"}},
        "help_permitted": {"arguments": args, "description": "permission", "regulated": {
            "role": "permission", "default": "unspecified", "act": act}},
        "late": {"arguments": ["s0"], "description": "late", "verbalisation": "{0} is late",
                 "regulated": {"role": "plain", "default": "unspecified"}},
        "ready": {"arguments": ["s1"], "description": "ready", "verbalisation": "{0} is ready"}}
    constants = {"ann": {"sort": "s0", "description": "Ann", **({"verbalisation": "Ann"} if seed % 2 else {})},
                 "bo": {"sort": "s1", "description": "Bo"}}
    return Environment({"language": LANGUAGE, "spec_revision": SPEC_REVISION,
                        "profiles": ["norm-defaults@0", "norms@0", "relational-fol@0"],
                        "vocabulary": {"sorts": sorts, "predicates": predicates, "constants": constants}})


def _model(rng):
    domains = {"s0": sorted(rng.sample(["e0", "e1", "ann0"], rng.randint(1, 3))),
               "s1": sorted(rng.sample(["f0", "bo0"], rng.randint(1, 2)))}
    constants = {}
    if "ann0" in domains["s0"]:
        constants["ann"] = "ann0"
    if "bo0" in domains["s1"]:
        constants["bo"] = "bo0"
    relations = {"ready": [[x] for x in domains["s1"] if rng.random() < 0.5],
                 "late": [[x] for x in domains["s0"] if rng.random() < 0.5]}
    return {"domains": domains, "constants": constants, "relations": relations}


@pytest.mark.parametrize("seed", range(24))
def test_lean_words_as_the_pre_q24_producers_did(seed):
    from itertools import product
    from types import SimpleNamespace
    old_nd = frozen_words.module("norm_defaults_english")
    old_norms = frozen_words.module("norm_english")
    old_route = frozen_words.module("readings_route")
    env = _environment(seed)
    rng = random.Random(seed)
    data = _model(rng)
    situation = SimpleNamespace(constants=data["constants"])
    points = []
    for predicate in ("help_required", "help_permitted", "late"):
        sorts = env.predicates[predicate].arguments
        for values in product(*(data["domains"][s] for s in sorts)):
            points += [(predicate, values, True), (predicate, values, False)]
    found = words.clauses(env, data["constants"], points)
    expected = [old_nd.point_clause(env, situation, p, vs, None if v else old_nd._negative_modal(env, p))
                for p, vs, v in points]
    assert found == expected
    assert [s for _, s in words.fillings(env, data["constants"], points)] == [
        old_nd.filling_sentence(env, situation, p, vs, v) for p, vs, v in points]
    assert words.pair(env, "help_required") == old_norms.pair_sentence(env, "help_required")
    # A situation as the readings routes show it: elements by id, the facts of the listed predicates, suppositions.
    from ve.english import EnglishVocabulary
    vocabulary = EnglishVocabulary(env)
    facts = ["ready"] if seed % 3 else ["ready", "late"]
    old = [f"{name} is {old_route._article(vocabulary.sorts[s])} {vocabulary.sorts[s]}"
           for s in sorted(data["domains"]) for name in sorted(data["domains"][s])]
    old += [vocabulary.predicates[p].format(*row) for p in sorted(facts) for row in sorted(data["relations"][p])]
    suppose = ["suppose the decider decides the exception applies to e0"] if seed % 4 == 0 else []
    assert words.situation(env, data, facts, suppose) == ("; ".join(old + suppose) if old + suppose else
                                                           "nothing exists")


def test_the_unsaid_description_is_leans():
    """norm_defaults.py:29 (F2's list): the filled vocabulary's description of `unsaid__p` is the elaboration row's,
    which Lean writes (`unsaidDescription`); Python writes none."""
    from tests.test_norm_defaults import CSAM_RULE, csam
    from ve.norm_defaults import UnspecifiedDocument
    document = UnspecifiedDocument(csam("unspecified"), [CSAM_RULE])
    [item] = document.elaboration["unsaid"]
    assert item["description"] == "the text does not say whether csam_generation_permitted"
    assert document.filled.env.predicates[item["name"]].description == item["description"]


def test_the_ab_evidence_has_no_difference():
    """The saved A/B (tools/words_ab.py): every call of every moved site on the readings, norm-defaults and pilot
    corpora gave the pre-Q2.4 text."""
    saved = json.loads((ROOT / "docs/spec/question-answering-q2/evidence/words-ab.json").read_text())
    assert saved["differences"] == []
    assert saved["calls"] == sum(site["calls"] for site in saved["sites"].values()) > 0
    assert all(site["same"] == site["calls"] for site in saved["sites"].values())
    assert {"readings.situation", "readings.s1_situation", "readings.gaps", "readings.plan_gaps",
            "norm_defaults.status_sentence", "norm_defaults.gap_sentence", "norm_defaults.latent_conflict_sentence",
            "norm_defaults.legend"} <= set(saved["sites"])
