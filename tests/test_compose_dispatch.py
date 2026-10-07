"""S0's exhaustive Python side of the composition dispatch contract (composition.md 10.1).

No route is wired here. `lean/VE/Compose/Examples.lean` carries the same 65,536
outcomes as literals, checked against these freshly computed Python results, and
repeats the one table of rows D1 to D52 that this file reads from the spec.
"""

import random
import re
from pathlib import Path

import pytest

from ve.errors import UnsupportedProfile
from ve.profiles import BY_NAME
from tests.profile_gate_oracle import checker_family


# S0's literal table is frozen over its original sixteen profiles. S1 adds a
# wrapper; testing that wrapper must not rewrite the S0 Lean literal table.
REGISTERED = tuple(sorted(set(BY_NAME) - {"readings@1"}))
SPEC_REGISTERED = frozenset({
    "alternatives@0", "closure@0", "data@0", "definitions@0", "documents@1",
    "nary@0", "norm-defaults@0", "norms@0", "soft-norms@0", "order@0", "relational-fol@0",
    "speech-acts@0", "reports@0", "risk@0", "rights@0", "time@0",
})
ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "lean/VE/Compose/Examples.lean"
SPEC = ROOT / "docs/spec/composition.md"
ORDER_ERROR = "UnsupportedProfile: profiles must be sorted and unique"


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
    if has("risk@0") and has("norm-defaults@0"):
        return "risk@0 with norm-defaults@0 is not implemented"
    if has("alternatives@0") and has("norm-defaults@0"):
        return "alternatives@0 with norm-defaults@0 is not implemented"
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
    if has("norm-defaults@0") and not has("norms@0"):
        return "norm-defaults@0 requires norms@0"
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
        and ("norm-defaults@0" not in p or "norms@0" in p and
             p.isdisjoint({"alternatives@0", "risk@0"}))
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
    assert set(BY_NAME) == SPEC_REGISTERED | {"readings@1"}
    texts, codes = _today_literals()
    assert texts[0] == "UnsupportedProfile: Missing profile relational-fol@0"
    assert len(codes) == 65_536


def test_lean_literals():
    source = EXAMPLES.read_text()
    texts, codes = _today_literals()
    text_match = re.search(r"def todayTexts\s*:\s*List String\s*:=\s*\[(.*?)\]", source, re.S)
    code_match = re.search(r'def todayCodes\s*:\s*String\s*:=\s*"([0-9a-zA-Z]+)"', source, re.S)
    assert text_match and code_match
    assert re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"', text_match[1]) == texts
    assert code_match[1] == codes


# Step 3 of composition.md 4.2 and its head table, transcribed for the rows with a wrapper profile.
WRAPPERS = ("ve.discourse@1", "right-clauses@0", "readings@1")
WRAPPER_HEAD = {"ve.discourse@1": "discourse", "right-clauses@0": "clauses", "readings@1": "readings"}
SITS_ON = {
    "ve.discourse@1": {"frozen", "norms", "normDefaults", "soft", "rights"},
    "right-clauses@0": {"rights"},
    "readings@1": {"norms", "normDefaults", "soft", "rights"},
}
OUTSIDE = {"reports": "reports@0", "speechActs": "speech-acts@0",
           "alternatives": "alternatives@0", "risk": "risk@0"}
HEADS = (("risk@0", "risk"), ("alternatives@0", "alternatives"), ("speech-acts@0", "speechActs"),
         ("reports@0", "reports"), ("rights@0", "rights"), ("soft-norms@0", "soft"),
         ("norm-defaults@0", "normDefaults"), ("norms@0", "norms"))


def _today_head(ps):
    return next((route for profile, route in HEADS if profile in ps), "frozen")


def _dispatch(ps):
    """("ok", route) or ("error", text): Python's gate on the base list, then the wrappers."""
    if ps != sorted(set(ps)):
        return "error", ORDER_ERROR
    base = [p for p in ps if p not in WRAPPERS]
    outcome = _outcome(base)
    if outcome != "ok":
        return "error", outcome
    route = _today_head(base)
    present = [w for w in WRAPPERS if w in ps]
    for wrapper in present:
        if route not in SITS_ON[wrapper]:
            if route in OUTSIDE:
                return "error", f"UnsupportedProfile: {wrapper} with {OUTSIDE[route]}"
            needed = "rights@0" if wrapper == "right-clauses@0" else "norms@0"
            return "error", f"UnsupportedProfile: {wrapper} requires {needed}"
    return "ok", WRAPPER_HEAD[present[0]] if present else route


def _spec_rows():
    """Rows D1 to D52 of composition.md 10.1: (n, list, expected, removals), removals cumulative."""
    section = SPEC.read_text().split("### 10.1 `dispatch`", 1)[1].split("- **D-all", 1)[0]
    rows = []
    for n, listed, cell in re.findall(r"^\| D(\d+) \| `([^`]*)` \| (.*) \|$", section, re.M):
        if match := re.match(r"ok `(\w+)`", cell):
            expected = ("ok", match[1])
        else:
            expected = ("error", re.match(r"`(UnsupportedProfile: [^`]*)`", cell)[1])
        removals = tuple(re.findall(r"(?:with|removing|then) `([^`]+)`(?: removed)?: ok `(\w+)`", cell))
        rows.append((int(n), tuple(listed.split(", ")), expected, removals))
    return rows


def _lean_answer(text):
    if match := re.fullmatch(r"\.ok \.(\w+)", text):
        return "ok", match[1]
    return "error", re.fullmatch(r'\.error "([^"]*)"', text)[1]


def _lean_rows():
    """The `#guard dispatch` rows of Examples.lean in the same shape as `_spec_rows`."""
    source = EXAMPLES.read_text()
    rows = {}
    pattern = r'^-- D(\d+)(?:, (\S+) removed)?\n#guard dispatch (\(?)\[([^\]]*)\](.*?) == (.*)$'
    for n, removed, paren, listed, rest, answer in re.findall(pattern, source, re.M):
        profiles = tuple(re.findall(r'"([^"]*)"', listed))
        if not removed:
            assert not paren and not rest
            assert int(n) not in rows, n
            rows[int(n)] = [profiles, _lean_answer(answer), [], profiles]
            continue
        assert paren and rest == f'.filter (· != "{removed}"))', (n, rest)
        row = rows[int(n)]
        assert profiles == row[3], (n, profiles, row[3])
        row[3] = tuple(p for p in profiles if p != removed)
        row[2].append((removed, _lean_answer(answer)[1]))
        assert _lean_answer(answer)[0] == "ok", n
    return [(n, profiles, expected, tuple(removals))
            for n, (profiles, expected, removals, _) in sorted(rows.items())]


def test_one_table_in_spec_and_lean():
    rows = _spec_rows()
    assert [n for n, *_ in rows] == list(range(1, 53))
    assert _lean_rows() == rows


def test_s1_wrapper_profile_gate():
    for base in ("norms@0", "norm-defaults@0", "soft-norms@0", "rights@0"):
        profiles = {"relational-fol@0", "norms@0", "readings@1"}
        if base == "norm-defaults@0":
            profiles.add(base)
        if base in ("soft-norms@0", "rights@0"):
            profiles.add("soft-norms@0")
        if base == "rights@0":
            profiles.add(base)
        assert checker_family(sorted(profiles)) == checker_family(sorted(profiles - {"readings@1"}))
    with pytest.raises(UnsupportedProfile, match="readings@1 requires norms@0"):
        checker_family(["readings@1", "relational-fol@0"])
    with pytest.raises(UnsupportedProfile, match="readings@1 with alternatives@0"):
        checker_family(["alternatives@0", "norms@0", "readings@1", "relational-fol@0"])


def test_s1_wrapper_matches_spec_rows_without_other_wrappers():
    for number, listed, expected, _removals in _spec_rows():
        if "readings@1" not in listed or set(listed) & {"ve.discourse@1", "right-clauses@0"}:
            continue
        outcome = _outcome(list(listed))
        if expected[0] == "ok":
            assert outcome == "ok", number
        else:
            assert outcome == expected[1], number


@pytest.mark.parametrize("n,profiles,expected,removals", _spec_rows(), ids=[f"D{n}" for n, *_ in _spec_rows()])
def test_row_on_python(n, profiles, expected, removals):
    profiles = list(profiles)
    if not set(profiles) & set(WRAPPERS):
        error = _specified_error(profiles)
        assert _outcome(profiles) == ("ok" if error is None else f"UnsupportedProfile: {error}")
        assert (error is None) == (expected[0] == "ok"), n
        if error is not None:
            assert f"UnsupportedProfile: {error}" == expected[1]
    assert _dispatch(profiles) == expected
    for removed, route in removals:
        profiles.remove(removed)
        assert _dispatch(profiles) == ("ok", route)


def _unsorted_lists():
    rng = random.Random(20261001)
    accepted = [_profiles(mask) for mask in range(1 << len(REGISTERED))
                if _today_list(_profiles(mask)) and len(_profiles(mask)) > 1]
    lists = []
    for _ in range(200):
        profiles = rng.choice(accepted).copy()
        rng.shuffle(profiles)
        if profiles == sorted(profiles):
            profiles.reverse()
        lists.append(profiles)
    for _ in range(50):
        profiles = rng.choice(accepted).copy()
        profiles.insert(rng.randrange(len(profiles) + 1), rng.choice(profiles))
        lists.append(profiles)
    return lists


def test_unsorted_and_repeated_profiles():
    lists = _unsorted_lists()
    for profiles in lists:
        assert _outcome(profiles) == ORDER_ERROR
    match = re.search(r"def unsortedLists\s*:\s*List \(List String\)\s*:=\s*\[(.*?)\]\n\n", EXAMPLES.read_text(), re.S)
    assert match
    lean = [re.findall(r'"([^"]*)"', row) for row in re.findall(r"\[([^\[\]]*)\]", match[1])]
    assert lean == lists
