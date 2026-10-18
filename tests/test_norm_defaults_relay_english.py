"""The English display formats the Lean accepted norm-defaults rows and nothing else.

Lean's `norm-defaults-status`, `-report` and `-conflict` rows carry every answer the
sentences state (the deciding rules, the atoms two fillings differ on, a reached default's
completed value, a CONFLICT's kind and deciding assignment). The renderers only format
those fields: no evaluation, enumeration or work limit, so the cost does not grow with the
situation (lf-10b fix 4)."""
import ast
import copy
import json
import sys
from pathlib import Path

import pytest

from tests.test_norm_defaults import (CSAM_RULE, CSAM_SITUATION, ONE_ACT, csam, environment, latent,
                                      obligation, permission, rule)
from ve import norm_defaults_english as english
from ve.ast import Unary, Var
from ve.errors import CheckerUnavailable, VEError
from ve.model import FiniteModel
from ve.norm_defaults import UnspecifiedDocument, report, search_reached
from ve.norm_defaults_route import run_case, source_case
from tests.subprocesses import run_cpu_bounded

LATENT_TARGET = "x_required->x_permitted"
ROOT = Path(__file__).resolve().parents[1]
# CPU seconds the renderers may spend on one row (the directive's "renders in under 2 s").
RENDER_CPU = 2
# A child rebuilds the container through Lean, then caps its own CPU at what it has spent plus
# RENDER_CPU before rendering: the kernel stops a renderer that does more than format the row.
RENDER = f"""
import json, math, resource, sys
sys.path.insert(0, {str(ROOT)!r})
from ve import norm_defaults_english as english
from ve.environment import Environment
from ve.model import FiniteModel
from ve.norm_defaults import UnspecifiedDocument
data = json.load(sys.stdin)
document = UnspecifiedDocument(Environment(data["environment"]), data["norms"])
situation = FiniteModel.from_dict(document.situation_environment(), data["situation"])
usage = resource.getrusage(resource.RUSAGE_SELF)
cap = math.ceil(usage.ru_utime + usage.ru_stime) + {RENDER_CPU}
resource.setrlimit(resource.RLIMIT_CPU, (cap, cap + 1))
print(json.dumps([getattr(english, name)(document, situation, data["row"]) for name in data["renderers"]]))
"""


def render_cpu_bounded(document, raw, row, renderers):
    """The renderers' output for Lean's `row`, from a child whose rendering may spend RENDER_CPU."""
    payload = {"environment": document.env.to_dict(), "norms": document.norms, "situation": raw, "row": row,
               "renderers": list(renderers)}
    completed, _ = run_cpu_bounded([sys.executable, "-c", RENDER], json.dumps(payload), 120)
    assert completed.returncode == 0, completed.stderr[-2000:]
    return json.loads(completed.stdout)


def _acts(n):
    return {"complete": True, "domains": {"act": [f"a{i}" for i in range(n)]}, "constants": {}, "relations": {}}


def _situation(document, raw):
    return FiniteModel.from_dict(document.situation_environment(), raw)


def status_row(document, raw, predicate, values, method="enumerate", **fillings):
    """Lean's status row; an `undecided` replay takes the `yes` and `no` fillings."""
    return run_case(source_case(document, "norm-defaults-status", model=raw, predicate=predicate,
                                tuple=list(values), method=method, **fillings))


def conflict_row(document, raw, filling, target, values):
    """Lean's row for a filled CONFLICT witness."""
    filled = document.with_filling(_situation(document, raw), filling)
    return run_case(source_case(document, "norm-defaults-conflict", witness={
        "target": target, "model": filled.to_dict(), "tuple": list(values)}))


def _latent_document():
    frozen = latent("unspecified")
    return UnspecifiedDocument(frozen.env, frozen.author.rules)


def _latent_row(document, n):
    return conflict_row(document, _acts(n), {"unsaid__y_permitted": frozenset({("a0",)})}, LATENT_TARGET, ["a0"])


# Statuses.

def test_relay_renders_selected_author_rule_and_silence():
    document = UnspecifiedDocument(csam("unspecified"), [CSAM_RULE])
    situation = _situation(document, CSAM_SITUATION)
    row = status_row(document, CSAM_SITUATION, "csam_generation_permitted", ("claude0",))
    assert (row["point_status"], row["rules"]) == ("SETTLED no", ["no-csam-generation"])
    assert english.status_sentence(document, situation, row) == (
        "The text says Claude must not generate child sexual abuse material (rule 1).")
    sol = status_row(document, CSAM_SITUATION, "csam_generation_permitted", ("sol0",), "undecided",
                     yes={"unsaid__csam_generation_permitted": [["sol0"]]}, no={})
    assert (sol["point_status"], sol["rules"]) == ("UNDECIDED", [])
    assert english.status_sentence(document, situation, sol) == (
        "The text does not say whether Sol may generate child sexual abuse material: "
        "no rule decides this situation.")
    assert english.silence_sentence(document, "csam_generation_permitted") == (
        "the text does not say whether an agent other than Claude may generate child sexual abuse material")


def test_relay_renders_pair_inheritance_from_lean_status():
    env = environment({"x_required": obligation("deny"), "x_permitted": permission("unspecified")})
    document = UnspecifiedDocument(env, [rule("must", "x_required", True)])
    row = status_row(document, ONE_ACT, "x_permitted", ("a",))
    assert (row["point_status"], row["rules"]) == ("SETTLED yes", ["must"])
    assert english.status_sentence(document, _situation(document, ONE_ACT), row) == (
        "A may be done: rule 1 requires it, and whatever must be done may be done.")


def test_relay_renders_the_undecided_atoms_lean_names():
    env = environment({"report_required": obligation("deny", None, act="{0} be reported"),
                       "permitted": permission("unspecified")})
    document = UnspecifiedDocument(env, [rule("rule-1", "report_required", True, Unary("permitted", Var(0)))])
    row = status_row(document, ONE_ACT, "report_required", ("a",), "undecided",
                     yes={"unsaid__permitted": [["a"]]}, no={})
    assert row["point_status"] == "UNDECIDED"
    assert row["differs"] == [{"predicate": "permitted", "tuple": ["a"]}]
    assert english.status_sentence(document, _situation(document, ONE_ACT), row) == (
        "The text does not say whether a must be reported: rule 1 decides only if a may be done, "
        "and the text does not say whether a may be done.")


# Reached defaults.

def test_relay_renders_reachable_gap_report_lines():
    for completion, value, expected in (
        ("unspecified", "unsaid", "The text does not say whether Sol may generate child sexual abuse material: "
                                  "no rule decides this situation."),
        ("deny", "no", "No rule decides whether Sol may generate child sexual abuse material; "
                       "the default decides that Sol must not generate child sexual abuse material."),
        ("allow", "yes", "No rule decides whether Sol may generate child sexual abuse material; "
                         "the default decides that Sol may generate child sexual abuse material."),
    ):
        document = UnspecifiedDocument(csam(completion), [CSAM_RULE])
        situation = _situation(document, CSAM_SITUATION)
        line = report(document, model=situation)["report"][0]
        assert line["reached"] == "reachable" and isinstance(line["witness"], dict)
        assert line["value"] == value
        assert english.gap_sentence(document, situation, line) == expected


# Latent conflicts.

def test_relay_renders_latent_conflict_verdict_and_finding():
    document = _latent_document()
    situation = _situation(document, ONE_ACT)
    verdict = conflict_row(document, ONE_ACT, {"unsaid__y_permitted": frozenset({("a",)})}, LATENT_TARGET, ["a"])
    assert (verdict["verdict"], verdict["kind"], verdict["rules"]) == ("CONFLICT", "latent", ["must-x", "not-x"])
    assert verdict["under"] == [{"predicate": "y_permitted", "tuple": ["a"], "value": True}]
    assert english.latent_conflict_sentence(document, situation, verdict) == (
        "Rules 1 and 2 contradict each other if a may be tried, and the text does not say whether a may be "
        "tried. To settle it, add a rule about whether a may be tried, or add a condition to one of the rules.")
    assert english.latent_conflict_finding(document, situation, verdict) == (
        "LatentConflict: must-x, not-x under y_permitted(a) = yes")


@pytest.mark.parametrize("acts", [13, 16, 18, 40])
def test_latent_fixture_renders_in_under_two_seconds(acts):
    """lf-10bc recheck: 13 acts took 6.7 s, 16 took 56 s and 18 took 148 s and 950 MiB,
    doubling per act. Lean answers at once, and rendering formats its row."""
    document = _latent_document()
    verdict = _latent_row(document, acts)
    assert verdict["under"] == [{"predicate": "y_permitted", "tuple": ["a0"], "value": True}]
    sentence, finding = render_cpu_bounded(document, _acts(acts), verdict,
                                           ("latent_conflict_sentence", "latent_conflict_finding"))
    assert sentence == (
        "Rules 1 and 2 contradict each other if a0 may be tried, and the text does not say whether a0 may "
        "be tried. To settle it, add a rule about whether a0 may be tried, or add a condition to one of the rules.")
    assert finding == "LatentConflict: must-x, not-x under y_permitted(a0) = yes"


def test_settled_conflict_is_not_rendered_as_latent():
    """u5d: a required act that is not permitted conflicts under every filling: Lean says `settled`."""
    env = environment({"x_required": obligation("deny"), "x_permitted": permission("deny")})
    document = UnspecifiedDocument(env, [rule("must", "x_required", True)])
    verdict = conflict_row(document, ONE_ACT, {}, LATENT_TARGET, ["a"])
    assert (verdict["verdict"], verdict["kind"], verdict["under"]) == ("CONFLICT", "settled", [])
    assert verdict["rules"] == ["must"]
    with pytest.raises(VEError, match="not a latent conflict"):
        english.latent_conflict_sentence(document, _situation(document, ONE_ACT), verdict)


# The sentences follow Lean's fields: a renderer that recomputed them would not.

def test_rendered_text_follows_leans_fields_not_a_recomputation():
    document = _latent_document()
    situation = _situation(document, _acts(2))
    verdict = _latent_row(document, 2)
    moved = copy.deepcopy(verdict)
    moved["under"] = [{"predicate": "y_permitted", "tuple": ["a1"], "value": False}]
    moved["rules"] = ["not-x"]
    assert english.latent_conflict_sentence(document, situation, moved) == (
        "Rules 2 contradict each other if a1 must not be tried, and the text does not say whether a1 may be "
        "tried. To settle it, add a rule about whether a1 may be tried, or make one rule an exception to the "
        "other.")
    assert english.latent_conflict_finding(document, situation, moved) == "LatentConflict: not-x under y_permitted(a1) = no"
    for broken in ({**verdict, "under": []}, {**verdict, "rules": ["no-such-rule"]}):
        with pytest.raises(CheckerUnavailable):
            english.latent_conflict_finding(document, situation, broken)
    gap_document = UnspecifiedDocument(csam("deny"), [CSAM_RULE])
    gap_situation = _situation(gap_document, CSAM_SITUATION)
    line = report(gap_document, model=gap_situation)["report"][0]
    assert english.gap_sentence(gap_document, gap_situation, {**line, "value": "yes"}).endswith(
        "the default decides that Sol may generate child sexual abuse material.")
    with pytest.raises(CheckerUnavailable):
        english.gap_sentence(gap_document, gap_situation, {k: v for k, v in line.items() if k != "value"})
    status = status_row(gap_document, CSAM_SITUATION, "csam_generation_permitted", ("claude0",), "table3")
    assert english.status_sentence(gap_document, gap_situation, {**status, "rules": []}) == (
        "The text says Claude must not generate child sexual abuse material (by default).")


def test_authoring_question_shows_the_situation_lean_replayed():
    document = UnspecifiedDocument(csam("unspecified"), [CSAM_RULE])
    found = search_reached(document, "csam_generation_permitted")
    question = english.completion_question(document, "csam_generation_permitted", found)
    assert question["selected"] is None and question["situation"].startswith("No rule decides whether ")
    assert english.completion_question(document, "csam_generation_permitted", None)["situation"] is None


# Structure: the renderers reach no evaluation, search or limit.

SOURCE = Path(english.__file__)
# What a public function of the module may reach outside it: display helpers only.
ALLOWED_IMPORTS = {
    "json", "ve.errors.CheckerUnavailable", "ve.errors.SyntaxError", "ve.errors.VEError",
    "ve.norm_english.UNSPECIFIED_KEYWORD", "ve.norm_english._bindings", "ve.norm_english._words",
    "ve.norm_english.default_sentence", "ve.norm_english.unspecified_clause",
    # Lean's clauses and pair sentences (plan Q2.4): the `words` relay, which words nothing itself.
    "ve.words.clauses", "ve.words.constants_of", "ve.words.lines", "ve.words.pair_item",
    "ve.norm_english._guard_text", "ve.surface.unambiguity.require_unique_derivation",
    "ve.english.english_lark_grammar", "ve.search._used_predicates",
    *(f"ve.ast.{name}" for name in ("And", "Binary", "Bottom", "Const", "Eq", "Not", "Or", "Top", "Unary", "Var")),
}
# Methods of text, lists, dicts, sets and JSON, and two reads of the container: the declared
# pairs and Lean's elaborated `reached` formula (shown as text by `silence_sentence`).
ALLOWED_METHODS = {
    "append", "casefold", "dumps", "endswith", "extend", "format", "fromkeys", "get", "items", "join", "lower",
    "pairs", "pop", "reached", "replace", "split", "splitlines", "startswith", "union", "update", "upper",
    "values"}
ALLOWED_BUILTINS = {
    "all", "any", "dict", "enumerate", "isinstance", "len", "list", "range", "reversed", "set", "sorted", "str",
    "tuple", "type", "zip"}


def _imports(tree):
    """Local name → `module.name` for every import in the module, at any depth."""
    names = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = ("ve." if node.level else "") + (node.module or "")
            for alias in node.names:
                names[alias.asname or alias.name] = f"{module}.{alias.name}"
        elif isinstance(node, ast.Import):
            for alias in node.names:
                names[alias.asname or alias.name.split(".")[0]] = alias.name
    return names


def reached_calls(source):
    """The external names, methods and builtins called on the call graph of the public functions."""
    tree = ast.parse(source)
    functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    imports = _imports(tree)
    pending = [name for name in functions if not name.startswith("_")]
    seen, external, methods, builtins = set(), set(), set(), set()
    while pending:
        name = pending.pop()
        if name in seen:
            continue
        seen.add(name)
        bound = {node.id for node in ast.walk(functions[name]) if isinstance(node, ast.Name)
                 and isinstance(node.ctx, ast.Store)}
        for node in ast.walk(functions[name]):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                if node.id in functions:
                    pending.append(node.id)
                elif node.id in imports:
                    external.add(imports[node.id])
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    methods.add(node.func.attr)
                elif (isinstance(node.func, ast.Name) and node.func.id not in functions
                      and node.func.id not in imports and node.func.id not in bound):
                    builtins.add(node.func.id)
    return seen, external, methods, builtins


def test_renderers_reach_no_evaluation_search_or_limit():
    source = SOURCE.read_text()
    seen, external, methods, builtins = reached_calls(source)
    assert {"status_sentence", "gap_sentence", "latent_conflict_sentence", "latent_conflict_finding",
            "completion_question", "_latent", "_author_rules"} <= seen
    assert external <= ALLOWED_IMPORTS, external - ALLOWED_IMPORTS
    assert methods <= ALLOWED_METHODS, methods - ALLOWED_METHODS
    assert builtins <= ALLOWED_BUILTINS, builtins - ALLOWED_BUILTINS
    modules = {name.rsplit(".", 1)[0] for name in _imports(ast.parse(source)).values()}
    assert not modules & {"ve.evaluate", "ve.model", "ve.norm_defaults", "ve.norm_defaults_route", "itertools",
                          "math", "ve.backends.relay"}


@pytest.mark.parametrize("mutation", [
    ("value = line.get(\"value\")", "value = document.value(situation, {}, predicate, values)"),
    ("from .errors import", "from .evaluate import _Evaluator\nfrom .errors import"),
    ("rules = _author_rules(document, row.get(\"rules\", []))",
     "rules = _author_rules(document, row.get(\"rules\", [])); _ = [product(range(2))]"),
])
def test_structure_scan_catches_a_recomputation(mutation):
    """Seeded: a renderer that evaluates, imports the evaluator or enumerates fails the scan."""
    old, new = mutation
    source = SOURCE.read_text()
    assert old in source
    mutated = source.replace(old, new, 1)
    _, external, methods, builtins = reached_calls(mutated)
    modules = {name.rsplit(".", 1)[0] for name in _imports(ast.parse(mutated)).values()}
    assert (not external <= ALLOWED_IMPORTS or not methods <= ALLOWED_METHODS
            or not builtins <= ALLOWED_BUILTINS or "ve.evaluate" in modules)
