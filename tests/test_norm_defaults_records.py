"""norm-defaults-text-1: three record claims read against what they rest on (regrade ndc2-F1, ndc2-F3, pk1c1-F1).

1. The norm-defaults spec names `gate_legacy`'s proved target (read from the theorem in `Dispatch.lean`).
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
