"""S0's exhaustive Python side of the composition dispatch contract.

No route is wired here. The future Lean examples carry the same 32,768
outcomes as literals, checked against these freshly computed Python results.
"""

import random
import re
from pathlib import Path

import pytest

from ve.errors import UnsupportedProfile
from ve.profiles import BY_NAME, checker_family


REGISTERED = tuple(sorted(BY_NAME))
SPEC_REGISTERED = frozenset({
    "alternatives@0", "closure@0", "data@0", "definitions@0", "documents@1",
    "nary@0", "norms@0", "soft-norms@0", "order@0", "relational-fol@0",
    "speech-acts@0", "reports@0", "risk@0", "rights@0", "time@0",
})
ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
EXAMPLES = Path(__file__).resolve().parents[1] / "lean/VE/Compose/Examples.lean"


def _outcome(profiles):
    try:
        return "ok" if checker_family(profiles) else "unreachable"
    except UnsupportedProfile as exc:
        message = str(exc)
        return message if message.startswith("UnsupportedProfile: ") else f"UnsupportedProfile: {message}"


def _specified_error(ps):
    """The ordered checks of composition.md 4.2, independent of checker_family."""
    has = ps.__contains__
    if ps != sorted(set(ps)):
        return "profiles must be sorted and unique"
    if has("alternatives@0") and not has("norms@0"):
        return "alternatives@0 requires norms@0"
    if has("alternatives@0") and has("soft-norms@0"):
        return "alternatives@0 with soft-norms@0"
    if has("risk@0") and not has("alternatives@0"):
        return "risk@0 requires alternatives@0"
    if unknown := next((p for p in ps if p not in REGISTERED), None):
        return f"Unsupported profile {unknown}"
    if has("speech-acts@0") and not has("norms@0"):
        return "speech-acts@0 requires norms@0"
    if has("speech-acts@0"):
        if extra := next((p for p in ps if p not in
                          {"relational-fol@0", "norms@0", "speech-acts@0"}), None):
            return f"speech-acts@0 with {extra}"
    if not has("relational-fol@0"):
        return "Missing profile relational-fol@0"
    if has("reports@0"):
        if layer := next((p for p in ("norms@0", "definitions@0", "data@0") if has(p)), None):
            return f"reports@0 with {layer} layers"
        if family := next((p for p in ("closure@0", "nary@0", "order@0") if has(p)), None):
            return f"reports@0 requires the fol checker, not {family}"
    if has("order@0") and has("closure@0"):
        return "Unsupported profile combination closure@0 x order@0"
    if has("order@0") and has("nary@0"):
        return "Unsupported profile combination nary@0 x order@0"
    if has("nary@0") and not has("closure@0"):
        return "Unsupported profile nary@0 without closure@0"
    if has("risk@0") and any(map(has, ("closure@0", "nary@0", "order@0"))):
        return "the risk norms route admits FOL documents only"
    if has("rights@0") and not has("soft-norms@0"):
        return "rights@0 requires soft-norms@0"
    if has("soft-norms@0") and not has("norms@0"):
        return "soft-norms@0 requires norms@0"
    return None


def _today_list(ps):
    """Declarative TodayList, separate from the diagnostic priority."""
    p = set(ps)
    return (
        ps == sorted(p) and p <= set(REGISTERED) and "relational-fol@0" in p
        and ("alternatives@0" not in p or "norms@0" in p and "soft-norms@0" not in p)
        and ("risk@0" not in p or "alternatives@0" in p and
             p.isdisjoint({"closure@0", "nary@0", "order@0"}))
        and ("speech-acts@0" not in p or "norms@0" in p and
             p <= {"relational-fol@0", "norms@0", "speech-acts@0"})
        and ("reports@0" not in p or p.isdisjoint({
            "norms@0", "definitions@0", "data@0", "closure@0", "nary@0", "order@0"}))
        and ("order@0" not in p or p.isdisjoint({"closure@0", "nary@0"}))
        and ("nary@0" not in p or "closure@0" in p)
        and ("rights@0" not in p or "soft-norms@0" in p)
        and ("soft-norms@0" not in p or "norms@0" in p)
    )


def _profiles(mask):
    return [name for bit, name in enumerate(REGISTERED) if mask & (1 << bit)]


def _today_literals():
    texts, codes, indexes = [], [], {}
    for mask in range(1 << len(REGISTERED)):
        profiles = _profiles(mask)
        error = _specified_error(profiles)
        expected = "ok" if error is None else f"UnsupportedProfile: {error}"
        assert _outcome(profiles) == expected, (mask, profiles)
        assert (error is None) == _today_list(profiles), (mask, profiles)
        if expected not in indexes:
            indexes[expected] = len(texts)
            texts.append(expected)
        codes.append(ALPHABET[indexes[expected]])
    assert len(texts) <= len(ALPHABET)
    return texts, "".join(codes)


def test_all_registered_subsets():
    assert set(REGISTERED) == SPEC_REGISTERED
    texts, codes = _today_literals()
    assert texts[0] == "UnsupportedProfile: Missing profile relational-fol@0"
    assert len(codes) == 32_768


def test_lean_literals_when_available():
    if not EXAMPLES.exists():
        pytest.skip("Lean Compose examples are a separate work item")
    source = EXAMPLES.read_text()
    texts, codes = _today_literals()
    text_match = re.search(r"def todayTexts\s*:\s*List String\s*:=\s*\[(.*?)\]", source, re.S)
    code_match = re.search(r'def todayCodes\s*:\s*String\s*:=\s*"([0-9a-zA-Z]+)"', source, re.S)
    assert text_match and code_match
    assert re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"', text_match[1]) == texts
    assert code_match[1] == codes


@pytest.mark.parametrize("profiles,family", [
    (["relational-fol@0"], "fol"),
    (["closure@0", "nary@0", "relational-fol@0"], "closure+n-ary"),
    (["order@0", "relational-fol@0", "time@0"], "order"),
    (["norms@0", "relational-fol@0"], "fol"),
    (["norms@0", "relational-fol@0", "soft-norms@0"], "fol"),
    (["norms@0", "relational-fol@0", "rights@0", "soft-norms@0"], "fol"),
    (["alternatives@0", "norms@0", "relational-fol@0"], "fol"),
    (["alternatives@0", "norms@0", "relational-fol@0", "risk@0"], "fol"),
    (["norms@0", "relational-fol@0", "speech-acts@0"], "fol"),
    (["relational-fol@0", "reports@0"], "fol"),
    (["documents@1", "norms@0", "relational-fol@0", "soft-norms@0"], "fol"),
    (["definitions@0", "norms@0", "relational-fol@0"], "fol"),
])
def test_rows_d1_to_d12(profiles, family):
    assert checker_family(profiles) == family
    assert _specified_error(profiles) is None


@pytest.mark.parametrize("profiles,error", [
    (["relational-fol@0", "norms@0"], "profiles must be sorted and unique"),
    (["alternatives@0", "relational-fol@0"], "alternatives@0 requires norms@0"),
    (["alternatives@0", "norms@0", "relational-fol@0", "soft-norms@0"], "alternatives@0 with soft-norms@0"),
    (["norms@0", "relational-fol@0", "risk@0"], "risk@0 requires alternatives@0"),
    (["relational-fol@0", "zzz@0"], "Unsupported profile zzz@0"),
    (["relational-fol@0", "speech-acts@0"], "speech-acts@0 requires norms@0"),
    (["norms@0", "relational-fol@0", "soft-norms@0", "speech-acts@0"], "speech-acts@0 with soft-norms@0"),
    (["norms@0"], "Missing profile relational-fol@0"),
    (["norms@0", "relational-fol@0", "reports@0"], "reports@0 with norms@0 layers"),
    (["order@0", "relational-fol@0", "reports@0"], "reports@0 requires the fol checker, not order@0"),
    (["closure@0", "order@0", "relational-fol@0"], "Unsupported profile combination closure@0 x order@0"),
    (["nary@0", "relational-fol@0"], "Unsupported profile nary@0 without closure@0"),
    (["alternatives@0", "norms@0", "order@0", "relational-fol@0", "risk@0"],
     "the risk norms route admits FOL documents only"),
    (["norms@0", "relational-fol@0", "rights@0"], "rights@0 requires soft-norms@0"),
    (["relational-fol@0", "soft-norms@0"], "soft-norms@0 requires norms@0"),
])
def test_rows_d13_to_d27(profiles, error):
    assert _specified_error(profiles) == error
    assert _outcome(profiles) == f"UnsupportedProfile: {error}"


def test_unsorted_and_repeated_profiles():
    rng = random.Random(20261001)
    accepted = [_profiles(mask) for mask in range(1 << len(REGISTERED))
                if _today_list(_profiles(mask)) and len(_profiles(mask)) > 1]
    for _ in range(200):
        profiles = rng.choice(accepted).copy()
        rng.shuffle(profiles)
        if profiles == sorted(profiles):
            profiles.reverse()
        assert _outcome(profiles) == "UnsupportedProfile: profiles must be sorted and unique"
    for _ in range(50):
        profiles = rng.choice(accepted).copy()
        profiles.insert(rng.randrange(len(profiles) + 1), rng.choice(profiles))
        assert _outcome(profiles) == "UnsupportedProfile: profiles must be sorted and unique"
