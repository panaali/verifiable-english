"""Pilot contract checks: the existing soft validator still owns the verdict."""

from copy import deepcopy
from pathlib import Path
import re
from collections import Counter
import ast

import pytest

from conformance.soft_norms import generated
from tests.test_soft_norms_lean import env, norm, ranks, should
from ve.errors import UnsupportedProfile, VEError
from conformance import softnorms_legacy as soft
from ve.softnorms import load_soft_document
from conformance.softnorms_contract import INHERITED_PROFILES, REGISTRY, ROUTE_PROFILES, soft_source
from ve.wire import loads_json
from conformance.wire_contract_engine import CLEAN, Fault, load, run
from tools.wire_contract import process


DIRECTORY = Path(__file__).resolve().parents[1] / "ve/wire_contract"
CONTRACT = load("soft-norms@0")
LIMITS = loads_json((DIRECTORY / "limits.json").read_bytes())
NAMES = loads_json((DIRECTORY / "names.json").read_bytes())


def diagnose(environment, norms):
    return run(CONTRACT, {"environment": environment, "norms": norms}, registry=REGISTRY,
               limits=LIMITS, names=NAMES)


def _bad_language():
    value = env()
    value["language"] = "wrong"
    return value, [], "1.2"


def _bad_party():
    return env({"parties": ["Bad"], "outranking": {"mode": "strict"}}), [], "2.7a"


def _bad_profiles():
    value = env()
    value["profiles"].reverse()
    return value, [], "3.1"


def _hard_default():
    return env(), [should("a", "x_required", True, hard=True)], "4.7a"


def _unknown_rank():
    value = env(ranks(["high", "low"]))
    value["vocabulary"]["soft"]["outranks"] = [["high", "unknown"]]
    return value, [], "5.2a"


def _duplicate_rule():
    return env(), [norm("a", "x_required", True), norm("a", "x_required", True)], "5.3"


def _bad_guard():
    return env(), [norm("a", "x_required", True,
                        guard=["unary", "missing", ["var", 0]])], "5.7"


def _tie_against_order():
    value = env(ranks(["high", "low"]))
    value["vocabulary"]["soft"]["ties"] = [["high", "low"]]
    return value, [norm("a", "x_required", True)], "6.2"


def _over_hard():
    return env(), [norm("h", "x_required", True),
                   should("s", "x_required", True, over=["h"])], "6.8"


CASES = [_bad_language, _bad_party, _bad_profiles, _hard_default,
         _unknown_rank, _duplicate_rule, _bad_guard, _tie_against_order, _over_hard]


@pytest.mark.parametrize("make", CASES, ids=lambda fn: fn.__name__)
def test_shadow_fault_agrees_with_legacy_rejection(make):
    environment, norms, expected = make()
    with pytest.raises(VEError) as error:
        load_soft_document(deepcopy(environment), deepcopy(norms))
    outcome = diagnose(environment, norms)
    assert isinstance(outcome, Fault)
    assert outcome.record["check"] == expected
    assert outcome.record["code"] == error.value.code
    assert CONTRACT["status"] == "public"
    assert error.value.diagnostic == outcome.record


def test_valid_examples_are_clean_and_accepted():
    for path in sorted((DIRECTORY / "examples/soft-norms@0").glob("*.json")):
        source = loads_json(path.read_bytes())
        load_soft_document(deepcopy(source["environment"]), deepcopy(source["norms"]))
        assert diagnose(source["environment"], source["norms"]) is CLEAN


# Profiles that Python's registry knows and the Lean soft route does not (wire review, Fable A1).
PYTHON_ONLY_PROFILES = {"alternatives@0": 0, "norm-defaults@0": 0, "reports@0": 2, "rights@0": 2,
                        "risk@0": 2, "speech-acts@0": 3}


@pytest.mark.parametrize("profile", sorted(PYTHON_ONLY_PROFILES))
def test_profiles_outside_the_lean_route_fail_check_3_2(profile):
    """Check 3.2 reads the Lean route's registry, as `profile_registered` does in Lean, whatever Python's
    legacy validator does with the profile (s3-pre.md lists what it does)."""
    source = env()
    source["profiles"] = sorted(source["profiles"] + [profile])
    outcome = diagnose(source, [])
    index = PYTHON_ONLY_PROFILES[profile]
    assert outcome.record == {
        "contract": "soft-norms@0", "revision": 4, "check": "3.2", "phase": "profiles",
        "code": "SOFT_UNSUPPORTED_PROFILE", "class": "UnsupportedProfile",
        "path": f"/environment/profiles/{index}", "text": f"UnsupportedProfile: Unsupported profile {profile}",
        "args": {"value": profile}}


def test_norm_defaults_with_unspecified_default_fails_check_2_3():
    """W1's declarations are decoded under Lean's inherited profiles, without `norm-defaults@0`, so the
    `unspecified` default fails 2.3 in both engines (Python's legacy validator reports it later)."""
    source = env(profiles=("norms@0", "norm-defaults@0", "soft-norms@0"))
    source["vocabulary"]["predicates"]["x_required"]["regulated"]["default"] = "unspecified"
    with pytest.raises(VEError) as legacy:
        load_soft_document(deepcopy(source), [])
    assert legacy.value.code == "SOFT_INVALID_INPUT"
    # The source lists the profile, so W1's "requires norm-defaults@0" would be false of it (Fable B2).
    fill = "UnsupportedProfile: norm-defaults@0 documents are checked through fill (ve.norm_defaults)"
    assert str(legacy.value) == fill
    outcome = diagnose(source, [])
    assert (outcome.record["check"], outcome.record["code"], outcome.record["path"], outcome.record["text"]) == (
        "2.3", "SOFT_INVALID_INPUT", "/environment", fill)


def test_unspecified_default_without_norm_defaults_names_the_profile():
    """Without `norm-defaults@0` among the source's profiles, W1's text is true and stays."""
    source = env()
    source["vocabulary"]["predicates"]["x_required"]["regulated"]["default"] = "unspecified"
    text = "UnsupportedProfile: unspecified completion requires norm-defaults@0"
    with pytest.raises(VEError) as legacy:
        load_soft_document(deepcopy(source), [])
    assert (legacy.value.code, str(legacy.value)) == ("SOFT_INVALID_INPUT", text)
    assert diagnose(source, []).record["text"] == text


@pytest.mark.parametrize("profile", sorted(soft._DROPPED_PROFILE_TEXTS))
def test_no_soft_route_text_names_a_listed_profile_as_missing(profile):
    """The class of Fable B2: every profile the soft route removes before W1 has its W1 remedy text
    restated, and the restated text is what both the legacy validator and the 2.3 hook give."""
    assert profile in soft._INHERITED_PROFILES and profile not in soft._SOFT_ROUTE_INHERITED_PROFILES
    assert set(soft._INHERITED_PROFILES) - set(soft._SOFT_ROUTE_INHERITED_PROFILES) == set(
        soft._DROPPED_PROFILE_TEXTS)
    text, restated = soft._DROPPED_PROFILE_TEXTS[profile]
    assert profile in text and "requires" in text and "requires" not in restated


def test_hook_lists_are_the_lean_route_lists():
    root = Path(__file__).resolve().parents[1] / "lean/VE"
    phases = (root / "SoftNorms/Phases.lean").read_text()
    inherited = re.search(r"def inheritedProfiles : List String := \[(.*?)\]", phases)[1]
    assert INHERITED_PROFILES == tuple(re.findall(r'"([^"]+)"', inherited))
    gate = (root / "Route/Gate.lean").read_text()
    registry = gate[gate.index("def registry : List ProfileRecord"):gate.index("def known")]
    base = re.search(r'def base : String := "([^"]+)"', gate)[1]
    names = set(re.findall(r'⟨"([^"]+)"', registry)) | ({base} if "⟨base," in registry else set())
    assert ROUTE_PROFILES == names | {"soft-norms@0"}


def test_decision_names_are_reported_prefix_by_prefix():
    """6.4a names the first long `excepted` name before any long `off` name, as both legacy validators do,
    even when the rule with the long `off` name comes first (wire review, Fable B1)."""
    from conformance.soft_norms import multi_fault_base
    environment, rules = multi_fault_base()
    rules[1]["norm"]["name"] = "b" * 52
    rules[3]["norm"]["name"] = "d" * 52
    with pytest.raises(VEError) as legacy:
        load_soft_document(deepcopy(environment), deepcopy(rules))
    outcome = diagnose(environment, rules)
    name = "soft__excepted__" + "d" * 52
    assert str(legacy.value) == f"ResourceLimit: decision predicate {name}"
    assert (outcome.record["check"], outcome.record["path"], outcome.record["text"]) == (
        "6.4a", "", str(legacy.value))


def test_adapter_mirrors_lean_on_missing_members():
    """2.1: a member the case lacks is `null`; a case without a known kind has no input (Lean's adapter)."""
    assert soft_source({"kind": "soft-elaborate", "environment": env()})["norms"] is None
    for kind in (None, "evaluation"):
        case = {"environment": env(), "norms": []} | ({} if kind is None else {"kind": kind})
        with pytest.raises(UnsupportedProfile, match=f"case kind {kind or 'null'} has no wire contract input"):
            soft_source(case)


def test_generated_wordings_and_lock_are_current():
    assert process(DIRECTORY) == []


def test_english_table_marks_group_scope():
    """Wire review (Astra B, Fable B5): rows inside a group are marked, a group names the checks it covers,
    every item is named by its group, and no raw pattern such as `@/*` is printed."""
    table = (DIRECTORY.parents[1] / "docs/spec/soft-norms-wire-table.md").read_text()
    rows = {line.split(" | ")[0].strip("| ·`"): line for line in table.splitlines() if line.startswith("|")}
    assert rows["2.16b"].startswith("| · · `2.16b`") and rows["2.16c"].startswith("| · `2.16c`")
    sentence = lambda check: rows[check].rstrip(" |").split(" | ")[-1]
    assert sentence("2.16b") != sentence("2.16c")
    assert "every earlier `outranks-pair` item of the same `outranks` item" in rows["2.16b"]
    assert "every earlier `outranks` item." in rows["2.16c"]
    assert sentence("2.17c") != sentence("2.17d")
    assert "checks `2.16a` to `2.16c` run on one item before the next item" in rows["outranks"]
    assert "`@" not in table and "this group" not in table
    for check in ("3.2", "4.13b", "5.7", "5.9b", "6.2"):
        assert sentence(check).startswith("For the `"), check


def test_pilot_tier_inventory_matches_statement_spec():
    tiers = {}
    strength = {"T1": 0, "T2": 1, "inherited": 2, "T3": 3}
    def walk(entries):
        for entry in entries:
            if "each" in entry:
                walk(entry["checks"])
            elif entry["kind"] == "classifier":
                for member in entry["emits"]:
                    tiers[re.match(r"\d+\.\d+", member["id"])[0]] = "T3"
            else:
                number = re.match(r"\d+\.\d+", entry["id"])[0]
                tier = ("inherited" if entry.get("inherited") else
                        "T2" if entry["kind"] == "hook" else "T1")
                tiers[number] = max(tiers.get(number, "T1"), tier, key=strength.get)
    for phase in CONTRACT["phases"]:
        walk(phase["checks"])
    assert len(tiers) == 67
    assert Counter(tiers.values()) == {"T1": 43, "T2": 8, "inherited": 3, "T3": 13}


def admission_case():
    """An admission case with one active norm unit, one quoted and one text unit."""
    return {"kind": "admission", "environment": env(), "document": {"units": [
        {"kind": "norm", "content": norm("a", "x_required", True)},
        {"kind": "quoted", "content": norm("q", "x_required", True)},
        {"kind": "text", "content": {"text": "note"}}]}}


def test_admission_adapter_selects_active_norm_units():
    case = admission_case()
    assert soft_source(case) == {"environment": env(), "norms": [norm("a", "x_required", True)]}
    assert diagnose(**soft_source(case)) is CLEAN


# wire-contract-s5.md 2.8: the contract modules, which may import the engine and each other; no other module
# of `ve/` imports one of them, or `ve.wire_contract`, except the one call site of each public unit.
CONTRACT_MODULES = {"softnorms_contract.py", "norms_contract.py", "norm_defaults_contract.py"}
DIAGNOSTIC_MODULES = ("conformance.softnorms_contract", "ve.norms_contract", "ve.norm_defaults_contract", "ve.wire_contract")
# The call site of each unit after the pilot (2.8). It is added by the unit's switch commit (7.2): while the
# unit's contract is in shadow, its route imports no diagnostic module.
UNIT_CALL_SITES = {"norms@0": ("norm_admission.py", "norms_contract", "admit_norm_document"),
                   "norm-defaults@0": ("norm_defaults_route.py", "norm_defaults_contract",
                                       "admit_norm_defaults_document")}


def _diagnostic_import_boundary(overrides=None):
    """Resolve relative and package imports, then pin the one production call shape."""
    root = DIRECTORY.parent
    overrides = overrides or {}
    routes = {}
    allowed = {}
    allowed.update({path: (module, function) for unit, (path, module, function) in UNIT_CALL_SITES.items()
                    if load(unit)["status"] == "public"})
    for path in root.rglob("*.py"):
        if "wire_contract" in path.parts or path.name in CONTRACT_MODULES:
            continue
        tree = ast.parse(overrides.get(path, path.read_text()))
        package = ".".join(path.relative_to(root.parent).parts[:-1])
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend((alias.name, node) for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                base = package.split(".")[:len(package.split(".")) - node.level + 1] if node.level else []
                module = ".".join(base + ([node.module] if node.module else [])) if node.level else node.module
                imports.append((module, node))
                imports.extend((module + "." + alias.name, node) for alias in node.names)
        diagnostic = [(name, node) for name, node in imports if name and
                      any(name == module or name.startswith(module + ".") for module in DIAGNOSTIC_MODULES)]
        if path.name in allowed:
            module, function_name = allowed[path.name]
            routes[path.name] = tree
            target = [node for name, node in diagnostic if name == "ve." + module]
            assert len({id(node) for node in target}) == 1
            assert all(name.startswith("ve." + module) for name, _ in diagnostic)
            imported = target[0]
            assert isinstance(imported, ast.ImportFrom)
            assert imported.module == module and imported.level == 1
            assert [alias.name for alias in imported.names] == ["public_rejection"]
            function = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                            and node.name == function_name)
            handlers = [node for node in ast.walk(function) if isinstance(node, ast.ExceptHandler)
                        and isinstance(node.type, ast.Name) and node.type.id == "VEError"]
            assert len(handlers) == 1
            handler = handlers[0]
            imports = [node for node in ast.walk(handler) if isinstance(node, ast.ImportFrom)
                       and node.module == module]
            calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
                     and isinstance(node.func, ast.Name) and node.func.id == "public_rejection"]
            raises = [node for node in ast.walk(handler) if isinstance(node, ast.Raise)
                      and isinstance(node.exc, ast.Call) and isinstance(node.exc.func, ast.Name)
                      and node.exc.func.id == "public_rejection"]
            assert len(imports) == len(calls) == len(raises) == 1
            assert calls[0] is raises[0].exc
        else:
            assert not diagnostic, path
    assert set(routes) == set(allowed)


def test_diagnostic_modules_stay_off_verdict_import_paths():
    _diagnostic_import_boundary()
    root = DIRECTORY.parent
    document = root / "document.py"
    route = root / "soft_route.py"
    with pytest.raises(AssertionError):
        _diagnostic_import_boundary({document: document.read_text() +
                                     "\nfrom conformance.softnorms_contract import soft_source\n"})
    with pytest.raises(AssertionError):
        _diagnostic_import_boundary({route: route.read_text() +
                                     "\nfrom conformance.softnorms_contract import public_rejection\n"})
    defaults = root / "norm_defaults_route.py"
    with pytest.raises(AssertionError):
        _diagnostic_import_boundary({defaults: defaults.read_text() +
                                     "\nfrom .norms_contract import legacy_validation\n"})
    # Fable review B: the handler of a unit in shadow is the switch commit's (7.2), not the shadow commit's.
    # Since lean-first batch 13b the call relays the Lean norms route; a handler planted there is still refused.
    norms = root / "norm_admission.py"
    statement = '        row = decide("norms", [case])[0]\n'
    assert load("norms@0")["status"] == "shadow" and norms.read_text().count(statement) == 1
    with pytest.raises(AssertionError):
        _diagnostic_import_boundary({norms: norms.read_text().replace(statement, (
            '        try:\n            row = decide("norms", [case])[0]\n        except VEError as error:\n'
            "            from .norms_contract import public_rejection\n"
            "            raise public_rejection(env.to_dict(), [], error)\n"))})


def test_seeded_soft_sources_keep_verdict_and_code_agreement():
    for seed in range(50):
        environment, norms = generated(seed)
        try:
            load_soft_document(deepcopy(environment), deepcopy(norms))
            code = None
        except VEError as error:
            code = error.code
        outcome = diagnose(environment, norms)
        if code is None:
            assert outcome is CLEAN, seed
        else:
            assert isinstance(outcome, Fault), seed
            assert outcome.record["code"] == code, seed
