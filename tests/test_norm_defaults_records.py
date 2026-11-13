"""norm-defaults-text-1: four record claims read against what they rest on (regrade ndc2-F1, ndc2-F3, pk1c1-F1, F3, F4).

1. The norm-defaults spec names `gate_legacy`'s proved target (read from the theorem in `Dispatch.lean`).
1b. On a list with a wrapper the records say the answers need not agree with `todayGate`, state no condition for when
    they agree, and name for each wrapper list only answers that Lean gives (literals checked by `#guard`s).
2. Every record of the `alternatives@0` with `norm-defaults@0` gate row agrees with `todayGate`'s row in Lean.
3. pk-1's identity claims cite a valid saved differential and claim no more than its sampled inputs."""

import re
from pathlib import Path

from tests.test_norm_defaults_documented_support import _definition, gate_refusals

ROOT = Path(__file__).resolve().parents[1]
DISPATCH = ROOT / "lean/VE/Compose/Dispatch.lean"
ND_SPEC = ROOT / "docs/spec/norm-defaults.md"
COMPOSITION = ROOT / "docs/spec/composition.md"
NORMDEFAULTS_NOTES = ROOT / "lean/NORMDEFAULTS.md"
INTEGRATION_GAPS = ROOT / "docs/INTEGRATION-GAPS.md"
PK1 = ROOT / "docs/premise-packs/pk-1"
SENTENCE = re.compile(r"(?<=[.;:])\s+(?=[A-Z`*(])")


def _sentences(text: str) -> list[str]:
    paragraphs = [" ".join(p.split()) for p in re.split(r"\n\s*\n|\n- |\n\d+\. ", text)]
    return [s for p in paragraphs for s in SENTENCE.split(p)]


# 1. ndc2-F1 ---------------------------------------------------------------------------------------------------------

def gate_legacy_target(source: str) -> str:
    """The function `gate_legacy` equates `gateOf profileTable` with, read from its statement."""
    stated = re.search(r"theorem gate_legacy\b.*?\)\s*:\s*(.*?)\s*:= by", source, re.S)
    assert stated, "gate_legacy not found"
    equation = re.fullmatch(r"gateOf profileTable ps = (\w+) ps", " ".join(stated.group(1).split()))
    assert equation, f"unexpected gate_legacy statement: {stated.group(1)!r}"
    return equation.group(1)


def gate_legacy_faults(spec: str, source: str) -> list[str]:
    """Where the spec's sentences citing `gate_legacy` name another target than the theorem's (empty: none)."""
    target = gate_legacy_target(source)
    strips = "wrapperProfiles" in _definition(source, target)  # the target strips and checks the wrappers
    cited = [s for s in _sentences(spec) if "`gate_legacy`" in s]
    faults = [] if cited else ["the spec cites no `gate_legacy`"]
    for s in cited:
        named = re.findall(r"`gateOf profileTable` agrees with(?: (`\w+`))?", s)
        if not named or not all(named):
            faults.append(f"names no target agreeing with `gateOf profileTable`: {s}")
        faults += [f"names {n} where gate_legacy proves `{target}`: {s}" for n in named if n not in ("", f"`{target}`")]
        if strips and "wrapper" not in s:
            faults.append(f"omits that `{target}` strips and checks the wrapper profiles: {s}")
    return faults


def gate_scope_faults(spec: str, source: str) -> list[str]:
    """Wrapper-free equivalence claims must retain `gate_legacy`'s legacy-profile hypothesis."""
    theorem = re.search(r"theorem gate_legacy\b(.*?)\s*:= by", source, re.S)
    assert theorem and "p ∈ legacyProfiles" in theorem.group(1)
    return [s for s in _sentences(spec)
            if "`todayGate`" in s and re.search(r"without wrapper profiles|wrapper-free|no wrapper profiles", s)
            and re.search(r"\b(?:is|agrees with|equals)\b", s) and "legacy" not in s]


def test_norm_defaults_spec_names_gate_legacy_target() -> None:
    source = DISPATCH.read_text(encoding="utf-8")
    assert gate_legacy_target(source) == "dispatch"
    assert gate_legacy_faults(ND_SPEC.read_text(encoding="utf-8"), source) == []


def test_wrapper_free_gate_claims_keep_legacy_hypothesis() -> None:
    assert gate_scope_faults(ND_SPEC.read_text(encoding="utf-8"), DISPATCH.read_text(encoding="utf-8")) == []


def test_gate_scope_scan_refuses_unqualified_equivalence() -> None:
    source = DISPATCH.read_text(encoding="utf-8")
    for bad in ("The gate on a list without wrapper profiles is `todayGate`.",
                "On wrapper-free lists, `gateOf profileTable` agrees with `todayGate`."):
        assert gate_scope_faults(bad, source) == [bad]
        assert gate_scope_faults(bad.replace("lists", "legacy-profile lists").replace(
            "list without", "legacy-profile list without"), source) == []


def test_gate_legacy_scan_refuses_old_sentences() -> None:
    source = DISPATCH.read_text(encoding="utf-8")
    old = ("(the gate is `todayGate`, `lean/VE/Compose/Dispatch.lean:31-71`, which `gateOf profileTable` agrees with on "
           "legacy-profile lists by `gate_legacy`; the test checks these two sentences against it):")
    named = "By `gate_legacy`, `gateOf profileTable` agrees with `todayGate` on the wrapper-free legacy lists."
    bare = "By `gate_legacy`, `gateOf profileTable` agrees with `dispatch` on legacy-profile lists."
    cited = "`gate_legacy` holds."
    cases = ((old, ["names no target", "omits"]), (named, ["names `todayGate`"]), (bare, ["omits"]),
             (cited, ["names no target", "omits"]), ("No theorem.", ["cites no"]))
    for text, faults in cases:
        found = gate_legacy_faults(text, source)
        assert len(found) == len(faults) and all(f in g for f, g in zip(faults, found)), (text, found)


# 1b. review F3, F4: on a list with a wrapper the answers need not agree; the records name Lean's answers ----------

ND_REPORT = ROOT / "docs/premise-packs/norm-defaults-text-1/REPORT.md"
# Every record this item wrote or edited that could compare wrapper lists with `todayGate`.
WRAPPER_RECORDS = (ND_SPEC, ND_REPORT, COMPOSITION, NORMDEFAULTS_NOTES, INTEGRATION_GAPS,
                   PK1 / "DELTA.md", PK1 / "REPORT.md")
CONTRAST = re.compile(r"\b(?:is|are|was|be)\s+(?:not|never)\s+`todayGate`|\bnot\s+`todayGate`'s|"
                      r"\bdiffer(?:s|ent)?\b[^.]*?\b(?:from|than|with)\s+`todayGate`|\bunlike\s+`todayGate`|"
                      r"\bdisagrees?\s+with\s+`todayGate`")
GATES = ("todayGate", "dispatch", "gateOf profileTable")
# The answers of `todayGate`, `dispatch` and `gateOf profileTable` (in that order) on every wrapper list the records
# name, as Lean evaluates them: `test_gate_answers_are_leans` elaborates one `#guard` per answer. No derivation here:
# a record naming another wrapper list fails until its answers are evaluated in Lean and added.
GATE_ANSWERS = {
    ("readings@1", "relational-fol@0"): ("UnsupportedProfile: Unsupported profile readings@1",
                                         "UnsupportedProfile: readings@1 requires norms@0",
                                         "UnsupportedProfile: readings@1 requires norms@0"),
    ("alternatives@0", "norm-defaults@0", "readings@1", "relational-fol@0"):
        ("UnsupportedProfile: alternatives@0 requires norms@0",) * 3,
    # review F4: the lists on which the withdrawn general condition was false
    ("norm-defaults@0", "readings@1", "relational-fol@0"): ("UnsupportedProfile: Unsupported profile readings@1",
                                                            "UnsupportedProfile: norm-defaults@0 requires norms@0",
                                                            "UnsupportedProfile: norm-defaults@0 requires norms@0"),
    ("readings@1",): ("UnsupportedProfile: Unsupported profile readings@1",
                      "UnsupportedProfile: Missing profile relational-fol@0",
                      "UnsupportedProfile: Missing profile relational-fol@0"),
    ("readings@1", "relational-fol@0", "speech-acts@0"): ("UnsupportedProfile: Unsupported profile readings@1",
                                                          "UnsupportedProfile: speech-acts@0 requires norms@0",
                                                          "UnsupportedProfile: speech-acts@0 requires norms@0"),
}
DIFFERING = ("readings@1", "relational-fol@0")
SHARING = ("alternatives@0", "norm-defaults@0", "readings@1", "relational-fol@0")
LISTED = re.compile(r"`\[([^\]]*)\]`")
NAMED = re.compile(r"`(todayGate|dispatch|gateOf profileTable)`|`(UnsupportedProfile: [^`]+)`|\bboth\b")
SENTENCE_END = re.compile(r"\.(?:\s|$)")
AGREEMENT = re.compile(r"\bshare[sd]?\b|\bagree(?:s|d)?\b|\bthe same (?:answer|refusal|text)", re.I)
CONDITION = re.compile(r"\b(?:when|whenever|if|iff|provided|unless|by a check|first refusing)\b", re.I)


def wrapper_contrast_faults(text: str) -> list[str]:
    """Sentences stating categorically that the answer on a wrapper list differs from `todayGate`'s."""
    return [s for s in _sentences(text) if "wrapper" in s.lower() and CONTRAST.search(s) and "need not" not in s]


def _wrappers(source: str) -> list[str]:
    found = re.search(r'def wrapperProfiles : List String := \[([^\]]*)\]', source)
    assert found, "wrapperProfiles not found"
    return re.findall(r'"([^"]+)"', found.group(1))


def wrapper_list_answers(text: str, source: str) -> tuple[dict[tuple[str, ...], list[str]], list[str]]:
    """Each wrapper list the text names, with the answers named after it up to the next list or the sentence's end,
    and the faults: a list whose answers were not evaluated, an answer that is not one of the list's, an answer after
    a gate's name that is not that gate's, and "both" on a list where the gates differ."""
    wrappers, named, faults = set(_wrappers(source)), {}, []
    for paragraph in re.split(r"\n\s*\n", text):
        flat = " ".join(paragraph.split())
        found = list(LISTED.finditer(flat))
        for m, after in zip(found, found[1:] + [None]):
            ps = tuple(p.strip() for p in m.group(1).split(","))
            if not set(ps) & wrappers:
                continue
            segment = flat[m.end():after.start() if after else len(flat)]
            end = SENTENCE_END.search(segment)
            segment = segment[:end.start()] if end else segment
            answers = GATE_ANSWERS.get(ps)
            if answers is None:
                faults.append(f"{list(ps)}: no Lean-evaluated answers in GATE_ANSWERS")
                continue
            gate, texts = None, named.setdefault(ps, [])
            for token in NAMED.finditer(segment):
                if token.group(0) == "both" and len(set(answers)) > 1:
                    faults.append(f"{list(ps)}: says both gates agree, but Lean answers {answers}")
                elif token.group(1):
                    gate = token.group(1)
                elif token.group(2):
                    texts.append(token.group(2))
                    if token.group(2) not in answers:
                        faults.append(f"{list(ps)}: `{token.group(2)}` is none of Lean's answers {answers}")
                    elif gate and token.group(2) != answers[GATES.index(gate)]:
                        faults.append(f"{list(ps)}: `{gate}` answers `{answers[GATES.index(gate)]}`, "
                                      f"not `{token.group(2)}`")
    return named, faults


def agreement_condition_faults(text: str) -> list[str]:
    """Sentences stating a general condition for when `todayGate` and the wrapper gate agree (review F4: none is
    claimed; the records give examples only)."""
    return [s for s in _sentences(text) if ("`todayGate`" in s or "both gates" in s)
            and AGREEMENT.search(s) and CONDITION.search(s) and "need not" not in s]


def gate_guards(answers: dict[tuple[str, ...], tuple[str, ...]]) -> str:
    """A Lean file with one `#guard` per gate answer: it elaborates only if Lean gives every answer."""
    lines = ["import VE.Compose.Dispatch", "open VE.Compose", "",
             "def recordAnswer {α : Type} : Except String α → String", '  | .ok _ => "ok"', "  | .error e => e", ""]
    for ps, texts in answers.items():
        listed = "[" + ", ".join(f'"{p}"' for p in ps) + "]"
        lines += [f'#guard recordAnswer ({gate} {listed}) == "{t}"' for gate, t in zip(GATES, texts)]
    return "\n".join(lines) + "\n"


def test_f3_probe_no_categorical_wrapper_difference() -> None:
    """PROBE F3 (norm-defaults-text-1-looprecheck1), verbatim."""
    paths = [Path("docs/spec/norm-defaults.md"), Path("docs/premise-packs/norm-defaults-text-1/REPORT.md")]
    pattern = r"on a list with a wrapper (?:it|this) is not `todayGate`"
    assert not any(re.search(pattern, " ".join((ROOT / p).read_text().split())) for p in paths)


def test_f4_probe_no_general_shared_refusal_condition() -> None:
    """PROBE F4 (norm-defaults-text-1-c122059-looprecheck1), verbatim but for the file's root."""
    t = " ".join((ROOT / "docs/spec/norm-defaults.md").read_text().split())
    assert "wrappers by a check that names no wrapper" not in t


def test_wrapper_records_say_need_not_agree() -> None:
    faults = {p.relative_to(ROOT).as_posix(): wrapper_contrast_faults(p.read_text(encoding="utf-8"))
              for p in WRAPPER_RECORDS}
    assert {k: v for k, v in faults.items() if v} == {}


def test_wrapper_records_state_no_agreement_condition() -> None:
    faults = {p.relative_to(ROOT).as_posix(): agreement_condition_faults(p.read_text(encoding="utf-8"))
              for p in WRAPPER_RECORDS}
    assert {k: v for k, v in faults.items() if v} == {}


def test_wrapper_records_name_leans_answers() -> None:
    source = DISPATCH.read_text(encoding="utf-8")
    for record in WRAPPER_RECORDS:
        assert wrapper_list_answers(record.read_text(encoding="utf-8"), source)[1] == [], record
    spec, _ = wrapper_list_answers(ND_SPEC.read_text(encoding="utf-8"), source)
    assert spec[DIFFERING] == list(GATE_ANSWERS[DIFFERING][:2])  # `todayGate`'s, then `dispatch`'s
    assert spec[SHARING] == [GATE_ANSWERS[SHARING][0]]
    assert len(set(GATE_ANSWERS[DIFFERING])) == 2 and len(set(GATE_ANSWERS[SHARING])) == 1


def test_gate_answers_are_leans(tmp_path: Path) -> None:
    """GATE_ANSWERS is what Lean evaluates; a swapped answer fails to elaborate."""
    import shutil
    import subprocess

    import pytest

    from tests.lean_build import LEAN, lean_build
    from tests.subprocesses import HANG_TIMEOUT
    lake = shutil.which("lake")
    if lake is None:
        pytest.skip("lake is not available")
    lean_build("VE")
    wrong = dict(GATE_ANSWERS)
    wrong[DIFFERING] = (GATE_ANSWERS[DIFFERING][1], GATE_ANSWERS[DIFFERING][0], GATE_ANSWERS[DIFFERING][2])
    for name, answers, holds in (("Answers", GATE_ANSWERS, True), ("Swapped", wrong, False)):
        path = tmp_path / f"{name}.lean"
        path.write_text(gate_guards(answers), encoding="utf-8")
        run = subprocess.run([lake, "env", "lean", str(path)], cwd=LEAN, capture_output=True, text=True,
                             timeout=HANG_TIMEOUT)
        assert (run.returncode == 0) == holds, (name, run.stdout + run.stderr)
        if not holds:  # exactly the two swapped answers (`todayGate`'s and `dispatch`'s) are false
            assert (run.stdout + run.stderr).count("did not evaluate to `true`") == 2, run.stdout + run.stderr


def test_wrapper_scans_refuse_and_accept() -> None:
    source = DISPATCH.read_text(encoding="utf-8")
    for bad in ("Dispatch checks each wrapper, so on a list with a wrapper it is not `todayGate`'s answer.",
                "On a list with a wrapper this is not `todayGate`.",
                "With a wrapper profile the gate's answer differs from `todayGate`'s.",
                "On wrapper lists the gate is never `todayGate`."):
        assert wrapper_contrast_faults(bad) == [bad]
    good = "On a list with a wrapper the answer need not agree with `todayGate`'s."
    assert wrapper_contrast_faults(good) == []
    # review F4: the withdrawn general condition, verbatim, and its kin
    for bad in ("They share a refusal when `todayGate` refuses the list without its wrappers by a check that names "
                "no wrapper: on `[alternatives@0, norm-defaults@0, readings@1, relational-fol@0]` both gates answer",
                "`todayGate` and `dispatch` agree whenever the base list is refused.",
                "Both gates give the same refusal if `todayGate` refuses first."):
        assert agreement_condition_faults(bad) == [bad]
    shared = ("They can share a refusal: on `[alternatives@0, norm-defaults@0, readings@1, relational-fol@0]` both "
              "gates answer `UnsupportedProfile: alternatives@0 requires norms@0`.")
    assert agreement_condition_faults(shared) == []
    differ = ("They differ on `[readings@1, relational-fol@0]`: `todayGate` refuses `UnsupportedProfile: Unsupported "
              "profile readings@1`, and `dispatch` refuses `UnsupportedProfile: readings@1 requires norms@0`.")
    for text in (shared, differ, differ + " " + shared):
        assert wrapper_list_answers(text, source)[1] == [], text
    for text, fault in (
            (shared.replace("readings@1", "readings@1, speech-acts@0"), "no Lean-evaluated answers"),
            (shared.replace("requires norms@0", "requires readings@1"), "none of Lean's answers"),
            (differ.replace("`todayGate` refuses", "`dispatch` refuses", 1), "`dispatch` answers"),
            (differ.replace("`dispatch` refuses", "`todayGate` refuses"), "`todayGate` answers"),
            # review F4's counterexamples: both gates do not share these refusals
            ("On `[norm-defaults@0, readings@1, relational-fol@0]` both gates answer "
             "`UnsupportedProfile: norm-defaults@0 requires norms@0`.", "says both"),
            ("On `[readings@1]` both refuse.", "says both"),
            ("On `[readings@1, relational-fol@0, speech-acts@0]` both gates answer "
             "`UnsupportedProfile: speech-acts@0 requires norms@0`.", "says both")):
        found = wrapper_list_answers(text, source)[1]
        assert any(fault in f for f in found), (text, found)
    assert wrapper_list_answers("On `[norms@0, relational-fol@0]` it routes.", source) == ({}, [])


# 2. ndc2-F3 ---------------------------------------------------------------------------------------------------------

PAIR_TEXT = "alternatives@0 with norm-defaults@0 is not implemented"


def admits_pair(source: str) -> bool:
    """`todayGate`'s row for `alternatives@0` with `norm-defaults@0`, read from Lean: no check refuses the pair."""
    return "alternatives@0" not in gate_refusals(source)


def _lean_block(text: str, head: str) -> str:
    start = text.index(head)
    end = re.search(r"\n(?:```|/--|def |theorem |inductive |namespace )", text[start + 1:])
    return text[start:start + 1 + end.start()] if end else text[start:]


def _todaylist_excludes(block: str) -> bool:
    clause = re.search(r'\("norm-defaults@0" ∈ ps → ([^)]*)\)', block)
    assert clause, "TodayList has no norm-defaults@0 clause"
    return '"alternatives@0" ∉ ps' in clause.group(1)


def _alternatives_excludes(block: str) -> bool:
    return '"norm-defaults@0" ∉ ps' in block


def _claims_pair_gate_refusal(sentence: str) -> bool:
    if "alternatives" not in sentence or (
            "`norm-defaults@0`" not in sentence and "alternatives and risk branches" not in sentence):
        return False
    clauses = sentence.split(";")
    for index, clause in enumerate(clauses):
        denial = re.search(r"\b(?:refused|rejected|refuse|reject)\b", clause)
        gate = re.search(r"\bprofile (?:validation|gate)\b", clause)
        refers_to_alternatives = "alternatives" in clause or (
            index > 0 and re.search(r"\b(?:they|both)\b", clause)
            and "alternatives" in ";".join(clauses[:index]))
        if denial and gate and refers_to_alternatives:
            return True
    return False


def pair_record_faults(records: dict[str, str], source: str) -> list[str]:
    """Each record of the gate's alternatives/norm-defaults row that differs from `todayGate` (empty: none)."""
    admitted, faults = admits_pair(source), []
    lean_list = _todaylist_excludes(_lean_block(source, "def TodayList"))
    lean_alt = _alternatives_excludes(_lean_block(source, "theorem today_alternatives"))
    assert lean_list == lean_alt == (not admitted), "Dispatch.lean's gate, TodayList and today_alternatives disagree"
    for name, text in records.items():
        for s in _sentences(text):
            if _claims_pair_gate_refusal(s) and admitted:
                faults.append(f"{name}: says refused, todayGate admits: {s}")
            if "`norm-defaults@0 ∉ ps` in" in s and "`today_alternatives`" in s and admitted:
                faults.append(f"{name}: reads check 6 into `today_alternatives`, which Lean no longer states: {s}")
        for row in re.findall(r"^\| \d+ \| `alternatives@0` with `norm-defaults@0` \|.*$", text, re.M):
            if admitted == (PAIR_TEXT in row):
                faults.append(f"{name}: 4.2 check row {'refuses' if admitted else 'admits'} the pair: {row}")
        for row in re.findall(r"^\| D46 \|.*$", text, re.M):
            if admitted != ("ok `alternatives`" in row):
                faults.append(f"{name}: D46 differs from todayGate: {row}")
        if "def todayGate" in text:
            if admitted == (f'unsupported "{PAIR_TEXT}"' in _lean_block(text, "def todayGate")):
                faults.append(f"{name}: the transcribed todayGate differs from Lean's on the pair")
        if "def TodayList" in text and _todaylist_excludes(_lean_block(text, "def TodayList")) != lean_list:
            faults.append(f"{name}: TodayList's norm-defaults@0 clause differs from Lean's")
        if "theorem today_alternatives" in text:
            if _alternatives_excludes(_lean_block(text, "theorem today_alternatives")) != lean_alt:
                faults.append(f"{name}: today_alternatives differs from Lean's statement")
    return faults


def _records() -> dict[str, str]:
    return {p.relative_to(ROOT).as_posix(): p.read_text(encoding="utf-8")
            for p in (COMPOSITION, NORMDEFAULTS_NOTES, ND_SPEC, INTEGRATION_GAPS)}


def test_alternatives_norm_defaults_gate_records_agree() -> None:
    source = DISPATCH.read_text(encoding="utf-8")
    records = _records()
    assert "def todayGate" in records["docs/spec/composition.md"]  # each structural check has its record
    assert "docs/INTEGRATION-GAPS.md" in records
    assert pair_record_faults(records, source) == []


def test_pair_scan_refuses_stale_records() -> None:
    source = DISPATCH.read_text(encoding="utf-8")
    assert admits_pair(source)
    stale = {
        "Still open: the alternatives and risk branches (spec 3.3's gap: refused at profile validation), W8.": "says",
        "The alternatives and risk routes reject `norm-defaults@0` at the profile gate.": "says",
        "The alternatives and risk routes still consume completed deny/allow norms; they reject "
        "`norm-defaults@0` at the profile gate instead of treating a silent permission as decided.": "says",
        f"| 6 | `alternatives@0` with `norm-defaults@0` | `{PAIR_TEXT}` |": "check row",
        "| D46 | `alternatives@0, norm-defaults@0, norms@0, relational-fol@0` | `UnsupportedProfile: x` |": "D46",
        "and `norm-defaults@0 ∉ ps` in `today_norms`, `today_alternatives` and `today_risk` is the gate's checks 5, 6.":
            "check 6",
        f'```lean\ndef todayGate (ps : List String) : Except String Unit :=\n  .error (unsupported "{PAIR_TEXT}")\n```':
            "transcribed",
        '```lean\ndef TodayList (ps : List String) : Prop :=\n  ("norm-defaults@0" ∈ ps → "norms@0" ∈ ps ∧ '
        '"alternatives@0" ∉ ps ∧ "risk@0" ∉ ps)\n```': "TodayList",
        '```lean\ntheorem today_alternatives (ps) (h : today ps = .ok .alternatives) :\n  "alternatives@0" ∈ ps ∧ '
        '"norm-defaults@0" ∉ ps\n```': "today_alternatives",
    }
    for text, fault in stale.items():
        found = pair_record_faults({"x.md": text}, source)
        assert len(found) == 1 and fault in found[0], (text, found)
    # The other direction: were the refusal back in Lean, each admitted record would be stale.
    refusing = source.replace(
        '  else match ps.find? (fun p => !registered.contains p) with',
        f'  else if ps.contains "alternatives@0" && ps.contains "norm-defaults@0" then\n'
        f'    .error (unsupported "{PAIR_TEXT}")\n  else match ps.find? (fun p => !registered.contains p) with', 1)
    refusing = refusing.replace('("norm-defaults@0" ∈ ps → "norms@0" ∈ ps ∧ "risk@0" ∉ ps)',
                                '("norm-defaults@0" ∈ ps → "norms@0" ∈ ps ∧ "alternatives@0" ∉ ps ∧ "risk@0" ∉ ps)')
    refusing = refusing.replace('"soft-norms@0" ∉ ps ∧ "risk@0" ∉ ps := by',
                                '"soft-norms@0" ∉ ps ∧ "risk@0" ∉ ps ∧ "norm-defaults@0" ∉ ps := by', 1)
    assert not admits_pair(refusing)
    admitted = ("| 6 | `alternatives@0` with `norm-defaults@0` | none (withdrawn) |\n"
                "| D46 | `alternatives@0, norm-defaults@0, norms@0, relational-fol@0` | ok `alternatives` |\n\n"
                "```lean\ndef todayGate (ps : List String) : Except String Unit :=\n  .ok ()\n\n"
                'def TodayList (ps : List String) : Prop :=\n  ("norm-defaults@0" ∈ ps → "norms@0" ∈ ps ∧ "risk@0" ∉ ps)\n\n'
                'theorem today_alternatives (ps) (h : today ps = .ok .alternatives) :\n  "alternatives@0" ∈ ps\n```\n')
    found = pair_record_faults({"x.md": admitted}, refusing)
    assert [f.split(":")[1].split()[0] for f in found] == ["4.2", "D46", "the", "TodayList's", "today_alternatives"]
    assert pair_record_faults({"x.md": admitted}, source) == []


# 3. pk1c1-F1 --------------------------------------------------------------------------------------------------------

IDENTITY = re.compile(r"byte[- ]identical|byte for byte|(?<![\d,.])0\s+differences|\bno differences\b|"
                      r"\bdiff is empty\b|\b(?:is|are) today's\b|\busers see does not change\b", re.I)
UNIVERSAL = re.compile(r"\b(?:every|all|any)\s+(?:outputs?|answers?|arrays?|diagnostics?|inputs?)\b|"
                       r"\bon today's routes\b|\busers see does not change\b|\bthe base/head diff\b", re.I)
CITE = re.compile(r"(?:docs/premise-packs/[\w.-]+/)?evidence/[\w.-]+")
ITEM = re.compile(r"\s*([-*]|\d+\.)\s|\|")


def _blocks(text: str) -> list[str]:
    """List items, paragraphs and table rows, wrapped lines joined."""
    blocks: list[list[str]] = [[]]
    for line in text.splitlines():
        if not line.strip() or ITEM.match(line):
            blocks.append([])
        blocks[-1].append(line)
    return [" ".join(" ".join(b).split()) for b in blocks if "".join(b).strip()]


def assurance(path: Path) -> str:
    """What a saved record supports: INVALID, failed (no `exit 0`), sampled (a differential), or support only."""
    lines = path.read_text(encoding="utf-8").strip().splitlines() if path.is_file() else []
    if not lines or "INVALID" in lines[0]:
        return "INVALID"
    if not any("differences" in line for line in lines):
        return "support"
    return "sampled" if lines[-1].strip() == "exit 0" else "failed"


def identity_faults(pack: Path) -> list[str]:
    """Each identity claim of the pack's REPORT.md or DELTA.md that claims more than its saved evidence."""
    faults = []
    for md in (pack / "REPORT.md", pack / "DELTA.md"):
        for block in _blocks(md.read_text(encoding="utf-8")) if md.is_file() else []:
            for s in filter(IDENTITY.search, _sentences(block)):
                where = f"{md.name}: {s[:90]!r}"
                cited = {c: assurance((ROOT if c.startswith("docs/") else pack) / c) for c in CITE.findall(s)}
                if not any(a == "sampled" for a in cited.values()):
                    faults.append(f"{where} cites no valid saved differential")
                faults += [f"{where} rests on {c}, which is {a}" for c, a in cited.items() if a in ("INVALID", "failed")]
                if UNIVERSAL.search(s):
                    faults.append(f"{where} claims identity beyond the sampled inputs of its records")
    return faults


def test_pk1_identity_claims_match_their_assurance() -> None:
    assert assurance(PK1 / "evidence/ab_full.txt") == "sampled"
    assert assurance(PK1 / "evidence/ab_route_cases.txt") == "INVALID"
    assert identity_faults(PK1) == []


def test_identity_scan_refuses_and_accepts(tmp_path: Path) -> None:
    (ev := tmp_path / "evidence").mkdir()
    (ev / "ok.txt").write_text("baseline x\n9 invocations; 0 differences\nexit 0\n")
    (ev / "bad.txt").write_text("INVALID differential: no invocation\n0 differences\nexit 1\n")
    (ev / "kinds.txt").write_text("recorded invocations 3\n")
    cases = {
        "- On the 9 sampled invocations the outputs are byte-identical (`evidence/ok.txt`, `evidence/kinds.txt`).\n":
            [],
        "- The route cases are INVALID (`evidence/bad.txt`); they have no valid differential.\n": [],
        "None: every output on today's routes is byte-identical (section 2).\n": ["no valid", "beyond"],
        "- Every answer is byte-identical (`evidence/ok.txt`).\n": ["beyond"],
        "- The 33 route cases are byte-identical (`evidence/bad.txt`).\n": ["no valid", "INVALID"],
        "1. It is byte-identical (A/B above).\n": ["no valid"],
        "| row | 0 differences | `evidence/kinds.txt` |\n": ["no valid"],
        "**What users see does not change.** On those lists every answer, array and\ndiagnostic is today's:\n":
            ["no valid", "beyond"],
    }
    for text, expected in cases.items():
        (tmp_path / "REPORT.md").write_text(text)
        found = identity_faults(tmp_path)
        assert len(found) == len(expected) and all(e in f for e, f in zip(expected, found)), (text, found)
