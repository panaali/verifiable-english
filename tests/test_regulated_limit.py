"""translim-predicates: the limit of 64 regulated predicates, at each site that checks it (REPORT.md, PART 1a).

Each site accepts exactly 64 and refuses 65 with `ResourceLimit: regulated predicates`, asked through the service
route that reaches it, and Rust's mirror the same (Python keeps no mirror: Lean owns the limit). The sites:

* `VE.Norms.Plain.decodeRegulatedAllIn`: the `environment` mode (`Service.Standalone.checkRegulated`);
* `VE.Norms.Wire.decodeNormsEnvironment`: the `norms`, `soft-norms` and `norm-defaults` routes' decoder;
* `VE.Norms.Tree.check` (and `VE.NormDefaults.checkSteps`, its definitional twin): the elaborated document of a
  split act, whose parts are counted after the decoder has passed fewer declarations;
* `VE.SoftNorms.checkW1` (and `RightClauses...W1Check.checkW1Steps`, its twin) checks the decoded tree, which no
  route widens: the soft route refuses `acts@0` vocabularies, so its 65th predicate is the decoder's refusal (the
  soft-norms test below);
* Rust `regulation_pairs` (rust/ve-kernel/src/environment.rs).

The restructure recipe (docs/translim/translim-predicates/REPORT.md section 1d; `rsp_split.py` there) is tested on its refusal of a split that moves a
rule's guard predicate out of the rule's frame.
"""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path

import pytest

from tests import lean_routes
from tests.subprocesses import HANG_TIMEOUT
from tests.test_acts_joined_route import NORM_PROFILES, environment as acts_environment
from ve.backends import rust_jsonl
from ve.backends.lean_service import LeanService
from ve.errors import ResourceLimit

ROOT = Path(__file__).resolve().parents[1]
LIMIT = 64
REFUSED = "ResourceLimit: regulated predicates"
LETTERS = "abcdefghijklmnopqrstuvwxyz"
DECIDER = {"decided_by": "assistant", "sufficient": [], "necessary": [], "factors": []}

service = pytest.mark.skipif(not (os.environ.get("VE_LEAN_SERVICE") or lean_routes.SERVICE.exists()),
                             reason="ve_service is not built")


def tag(i):
    return LETTERS[i // 26] + LETTERS[i % 26]


def env(n, profiles=("norms@0", "relational-fol@0")):
    """`n` regulated permissions, each with its own act, over one sort."""
    predicates = {f"p{tag(i)}": {"arguments": ["person"], "description": f"{{0}} may do {tag(i)}",
                                 "regulated": {"role": "permission", "default": "deny", "act": f"{{0}} do {tag(i)}"}}
                  for i in range(n)}
    return {"language": "ve.core@0.2", "profiles": sorted(profiles), "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": {"person": {"description": "a person"}}, "constants": {},
                           "predicates": predicates}}


def rules(environment, soft=False):
    out = []
    for p in environment["vocabulary"]["predicates"]:
        norm = {"name": f"r-{p}", "predicate": p, "sign": False, "guard": ["top"], "unless": [], "over": []}
        out.append({"norm": {**norm, "mode": "default", "exception": dict(DECIDER)} if soft else norm})
    return out


def ask(mode, case):
    """The service's row for one case (`VE_LEAN_SERVICE` names another build, as for a seeded bug)."""
    with LeanService(timeout=HANG_TIMEOUT) as lean:
        _, response = lean.exchange(mode, json.dumps([{"id": "c", **case}], separators=(",", ":")), 1,
                                    timeout=HANG_TIMEOUT)
    [entry] = response["results"]
    return entry["result"]


def refusal(row):
    return row.get("error") if row.get("status") == "error" else None


@service
@pytest.mark.parametrize("n,expected", [(LIMIT, None), (LIMIT + 1, REFUSED)])
def test_plain_decoder_takes_the_limit_and_refuses_one_more(n, expected):
    """`Plain.decodeRegulatedAllIn`, through the `environment` mode."""
    assert refusal(ask("environment", {"environment": env(n)})) == expected


@service
@pytest.mark.parametrize("n,expected", [(LIMIT, None), (LIMIT + 1, REFUSED)])
def test_norms_decoder_takes_the_limit_and_refuses_one_more(n, expected):
    """`Wire.decodeNormsEnvironment`, through the `norms` route."""
    raw = env(n)
    row = ask("norms", {"kind": "norms-elaborate", "environment": raw, "norms": rules(raw)})
    assert refusal(row) == expected
    if expected is None:
        assert len(row["conflict_targets"]) == n


@service
@pytest.mark.parametrize("n,expected", [(LIMIT, None), (LIMIT + 1, REFUSED)])
def test_soft_norms_route_takes_the_limit_and_refuses_one_more(n, expected):
    """The soft route's decoder; `SoftNorms.checkW1` then checks the same 64 (no soft route widens the tree)."""
    raw = env(n, ("norms@0", "relational-fol@0", "soft-norms@0"))
    assert refusal(ask("soft-norms", {"kind": "soft-rules", "environment": raw, "norms": rules(raw, soft=True)})) \
        == expected


@service
@pytest.mark.parametrize("n,expected", [(LIMIT, None), (LIMIT + 1, REFUSED)])
def test_norm_defaults_route_takes_the_limit_and_refuses_one_more(n, expected):
    raw = env(n, ("norm-defaults@0", "norms@0", "relational-fol@0"))
    assert refusal(ask("norm-defaults", {"kind": "norm-defaults-elaborate", "environment": raw,
                                         "norms": rules(raw)})) == expected


def split_environment(split, lexical):
    """`split` acts that each read as two parts and `lexical` acts kept whole: 2 * split + lexical regulated
    predicates after the split, from split + lexical declarations."""
    raw = acts_environment(NORM_PROFILES)
    predicates = {}
    for i in range(split):
        predicates[f"p{i}"] = {"arguments": ["person"], "description": "d", "regulated": {
            "role": "permission", "default": "deny", "act": f"{{0}} be subjected to x{tag(i)} or to y{tag(i)}"}}
    for i in range(lexical):
        predicates[f"h{i}"] = {"arguments": ["person"], "description": "d", "regulated": {
            "role": "permission", "default": "deny", "act": f"{{0}} be held{LETTERS[i]}"}}
    raw["vocabulary"]["predicates"] = predicates
    return raw


@service
@pytest.mark.parametrize("split,lexical,expected", [(31, 2, None), (32, 1, REFUSED)])
def test_elaborated_document_takes_the_limit_and_refuses_one_more(split, lexical, expected):
    """`Tree.check` on the elaborated document: 33 declarations pass the decoder either way; 64 parts are
    accepted and 65 refused."""
    raw = split_environment(split, lexical)
    assert len(raw["vocabulary"]["predicates"]) == 33
    row = ask("norms", {"kind": "norms-elaborate", "environment": raw, "norms": rules(raw)})
    assert refusal(row) == expected
    if expected is None:
        assert len(row["conflict_targets"]) == LIMIT


@pytest.mark.skipif(not Path(os.environ.get("VE_RUST_JSONL") or rust_jsonl.DEFAULT_EXECUTABLE).is_file(),
                    reason="the Rust checker is not built")
def test_rust_mirror_takes_the_limit_and_refuses_one_more():
    assert rust_jsonl.run({"id": "c", "kind": "check", "ast": ["top"], "environment": env(LIMIT)},
                          timeout=HANG_TIMEOUT)["status"] == "ok"
    with pytest.raises(ResourceLimit, match="regulated predicates"):
        rust_jsonl.run({"id": "c", "kind": "check", "ast": ["top"], "environment": env(LIMIT + 1)},
                       timeout=HANG_TIMEOUT)


def split_recipe():
    path = ROOT / "docs/translim/translim-predicates/rsp_split.py"
    spec = importlib.util.spec_from_file_location("rsp_split", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def norm(name, predicate, guard=("top",), over=()):
    return {"name": name, "predicate": predicate, "sign": True, "guard": list(guard), "unless": [],
            "over": list(over)}


REGULATED = {"a": {"role": "obligation", "permission": "a_ok"}, "a_ok": {"role": "permission"},
             "b": {"role": "obligation"}, "c": {"role": "obligation"}, "d": {"role": "obligation"}}
RULES = [norm("ra", "a"), norm("rb", "b", ["unary", "c", ["var", 0]]), norm("rc", "c"),
         norm("rd", "d", over=["rc"])]


def test_split_recipe_moves_whole_components_only():
    """The links of step 1: a permission dual, a guard's regulated predicate and a precedence pair."""
    recipe = split_recipe()
    assert recipe.components(sorted(REGULATED), recipe.links(RULES, REGULATED)) == [["a", "a_ok"], ["b", "c", "d"]]
    assert recipe.closed_split({"a", "a_ok"}, RULES, REGULATED) is None
    assert recipe.closed_split({"b", "c", "d"}, RULES, REGULATED) is None


@pytest.mark.parametrize("moved,problem", [
    ({"b"}, "the split separates b from c"),  # rb's guard reads c: c must move with b
    ({"a"}, "the split separates a from a_ok"),  # an obligation without its permission dual
    ({"b", "c"}, "the split separates d from c"),  # rd is over rc: d must move with c
])
def test_split_recipe_refuses_a_split_that_breaks_a_link(moved, problem):
    assert split_recipe().closed_split(moved, RULES, REGULATED) == problem


def test_split_recipe_links_rules_checked_together():
    """A conflict pair is asked of one frame: its two rules' predicates move together."""
    recipe = split_recipe()
    assert recipe.closed_split({"a", "a_ok"}, RULES, REGULATED, together=[("ra", "rc")]) == \
        "the split separates a from c"


# The recipe end to end on a soft document (design note docs/usecases/safetyfw/regulated-limit.md): split into the
# frames of its components, every predicate's selected rules are those of the unsplit document, and a frame that
# lacks a rule's guard predicate is refused, never answered.

SPLIT_RULES = [("ra", "a", ["unary", "f", ["var", 0]], True), ("rb", "b", ["unary", "a", ["var", 0]], True),
               ("rc", "c", ["unary", "g", ["var", 0]], True), ("rd", "d", ["not", ["unary", "f", ["var", 0]]], False)]


def soft_frame(regulated):
    """The frame (`f`, `g`) with the regulated permissions `regulated` and the rules on them."""
    from ve.softnorms import SoftEnvironment, SoftNormDocument
    predicates = {"f": {"arguments": ["person"], "description": "{0} is f"},
                  "g": {"arguments": ["person"], "description": "{0} is g"}}
    for p in regulated:
        predicates[p] = {"arguments": ["person"], "description": f"{{0}} may {p}",
                         "regulated": {"role": "permission", "default": "deny", "act": f"{{0}} do {p}"}}
    raw = {"language": "ve.core@0.2", "profiles": ["norms@0", "relational-fol@0", "soft-norms@0"],
           "spec_revision": "ve-v0.2-expand2-2026-09-25",
           "vocabulary": {"sorts": {"person": {"description": "a person"}}, "constants": {}, "predicates": predicates}}
    rules = [{"norm": {"name": n, "predicate": p, "sign": s, "guard": g, "unless": [], "over": [], "mode": "default",
                       "exception": dict(DECIDER)}} for n, p, g, s in SPLIT_RULES if p in regulated]
    return SoftNormDocument(SoftEnvironment(raw), rules)


def selected(doc, predicate, f, g):
    from ve.model import FiniteModel
    env = doc.elaborated.base_environment()
    model = FiniteModel.from_dict(env, {"complete": True, "domains": {"person": ["p1", "p2"]}, "constants": {},
                                        "relations": {**{p: [] for p in env.predicates}, "f": f, "g": g}})
    return [sorted((r.name, r.sign) for r in doc.elaborated.selected_rules(predicate, model, (x,)))
            for x in ("p1", "p2")]


@service
def test_a_split_into_component_frames_selects_the_same_rules():
    recipe = split_recipe()
    rules = [{"name": n, "predicate": p, "guard": g, "unless": [], "over": []} for n, p, g, _ in SPLIT_RULES]
    regulated = {p: {"role": "permission"} for p in "abcd"}
    groups = recipe.components(sorted(regulated), recipe.links(rules, regulated))
    assert groups == [["c"], ["d"], ["a", "b"]]
    moved = {"c", "d"}
    assert recipe.closed_split(moved, rules, regulated) is None
    whole, frames = soft_frame("abcd"), {"A": soft_frame("ab"), "B": soft_frame("cd")}
    for f, g in (([], []), ([["p1"]], [["p2"]]), ([["p1"], ["p2"]], [["p1"]])):
        for p in "abcd":
            assert selected(frames["B" if p in moved else "A"], p, f, g) == selected(whole, p, f, g), (p, f, g)
    assert selected(frames["A"], "b", [["p1"]], []) == [[("rb", True)], []]  # rb's guard reads a, in its frame


@service
def test_a_frame_without_a_rules_guard_predicate_is_refused():
    """Seeded bug (c) as a split: b moves without a, the predicate its rule's guard reads."""
    from ve.errors import UnknownSymbol
    assert split_recipe().closed_split({"b", "c", "d"}, [{"name": n, "predicate": p, "guard": g, "unless": [],
                                                          "over": []} for n, p, g, _ in SPLIT_RULES],
                                       {p: {"role": "permission"} for p in "abcd"}) == "the split separates b from a"
    with pytest.raises(UnknownSymbol, match="Unknown predicate 'a'"):
        soft_frame("bcd")
