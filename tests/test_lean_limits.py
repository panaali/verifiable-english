"""Every Lean limit has one owner, `lean/VE/Limits.lean` (lf-18 review F2; FINDING-CLASSES 1, build checklist 1).

* No non-frozen Lean check hard-codes a limit's value: a decoder's depth fuel, a node total, a depth or nesting
  bound, an identifier, source, tuple, entity, sort, predicate, numeral or JSON-depth bound, or the largest
  integer. The checks read `VE.Limits`. Approved theorem statements and structures keep the value they were
  approved with (the limits are reducible, so their proofs hold of the checks), and so do `#guard`s.
* The modules that may not import `VE.Limits` (hash-frozen by architecture decision D2, hashed by the English
  grammar lock, or generated) are tied to it in `lean/VE/LimitTies.lean`: the frozen decoders' node and depth
  literals at the limit and one past it, the JSON reader's caps, and the generated name classes.
* The lint can fail: each of its patterns finds the line it was written for.

The scan reads Lean source as text (it is a measurement aid, not a parser): it drops comments and string
literals and reads only the bodies of `def`, `abbrev` and `instance` declarations.
"""
from __future__ import annotations

import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "lean"

FROZEN = {line.split()[1] for line in (LEAN / "VE/Route/frozen-sources.sha256").read_text().splitlines()
          if line.endswith(".lean")}
LOCKED = {name[len("lean/"):] for name in json.loads((ROOT / "ve/english_grammar/LOCK.json").read_text())["files"]
          if name.startswith("lean/")}
# Generated Lean (tools/regen_generated.py): its generator owns its text; `Service/EnglishRun.lean` copies
# `English/Run.lean`, which is scanned.
GENERATED = ("VE/WireContract/Limits.lean", "VE/WireContract/Names.lean", "VE/WireContract/Tables/",
             "VE/EnglishGrammar/Fixed/", "VE/EnglishGrammar/LexiconFixtures.lean", "VE/Question/Fixtures.lean",
             "VE/Service/EnglishRun.lean")
OWNERS = {"VE/Limits.lean", "VE/LimitTies.lean"}

# One pattern per limit of `VE.Limits` that a check compares with; each names the limit it stands for.
PATTERNS = {
    "maxDepth (decoder fuel)": re.compile(r"\b(decode|elab|syn|budget)\w*(\s+[\w.]+)*?\s+64\b"),
    "maxDepth": re.compile(r"\b(depth|nesting|levels|Depth)\b.*[<>≤≥] ?64\b"),
    "maxNodes": re.compile(r"[<>≤≥] ?10000\b"),
    "maxIdentifierBytes": re.compile(r"(utf8ByteSize|name\.length|next)\s*[<>≤≥] ?64\b"),
    "maxSourceBytes": re.compile(r"[<>≤≥] ?65536\b"),
    "maxTuples": re.compile(r"[<>≤≥] ?100000\b"),
    "maxEntities": re.compile(r"[<>≤≥] ?1000\b.*\b(domain|entity)"),  # read with its strings
    "maxSorts/maxPredicates": re.compile(r"\b(sort|predicate)\w*\.length [<>≤≥] ?(32|256)\b"),
    "maxNumeralChars": re.compile(r"[<>≤≥] ?40\b"),
    "maxJsonDepth": re.compile(r"\bdepth\b.*[<>≤≥] ?256\b"),
    "maxIndex": re.compile(r"\b9007199254740991\b"),
}
# Patterns whose qualifier may be in the check's diagnostic text.
WITH_STRINGS = {"maxEntities"}
# Another limit with the same value: a document's unit count (at most 10000) is not its AST node count.
OTHER_LIMITS = re.compile(r"\bunits?\b|unit count")
DECLARATION = re.compile(r"^\s*(@\[[^\]]*\]\s*)?((private|protected|noncomputable|unsafe)\s+)*"
                         r"(def|abbrev|instance|theorem|lemma|structure|inductive|class|example|#guard|#eval)\b")
CHECKED_DECLARATIONS = {"def", "abbrev", "instance"}
# A `def ... : Prop` is a specification predicate (`lean/predicates.txt`), kept as approved, like a theorem.
PROP = re.compile(r":\s*Prop\s*:=")
STRING = re.compile(r'"(\\.|[^"\\])*"')


def _scanned(relative: str) -> bool:
    return not (relative in FROZEN or relative in LOCKED or relative in OWNERS
                or any(relative == g or (g.endswith("/") and relative.startswith(g)) for g in GENERATED))


def hard_coded(text: str) -> list[tuple[int, str, str]]:
    """(line, limit, line text) for each limit value a declaration body (not a specification) compares with."""
    found, declaration, block = [], None, 0
    for number, line in enumerate(text.splitlines(), 1):
        code = line
        if block:
            if "-/" not in code:
                continue
            code, block = code.split("-/", 1)[1], 0
        while "/-" in code:
            before, _, after = code.partition("/-")
            if "-/" in after:
                code = before + after.split("-/", 1)[1]
            else:
                code, block = before, 1
        raw = code.split("--", 1)[0]
        code = STRING.sub('""', raw)
        match = DECLARATION.match(code)
        if match:
            declaration = "predicate" if match.group(4) == "def" and PROP.search(code) else match.group(4)
        if declaration not in CHECKED_DECLARATIONS or OTHER_LIMITS.search(code):
            continue
        found += [(number, limit, line.strip()) for limit, pattern in PATTERNS.items()
                  if pattern.search(raw if limit in WITH_STRINGS else code)]
    return found


def test_no_non_frozen_lean_check_hard_codes_a_limit():
    found = [f"VE/{path.relative_to(LEAN / 'VE')}:{number}: {limit}: {text}"
             for path in sorted((LEAN / "VE").rglob("*.lean")) if _scanned(str(path.relative_to(LEAN)))
             for number, limit, text in hard_coded(path.read_text())]
    assert found == [], "\n".join(found)


def test_the_reviewers_probe():
    """PROBE F2 (lf-18 review), as the reviewer ran it: 20 checks in non-frozen files compared with 10000, 65536
    or 64, and LimitTies tied neither the node nor the depth limit."""
    found = [f"{path}:{i + 1}" for path in sorted(LEAN.glob("VE/**/*.lean"))
             if str(path.relative_to(LEAN)) not in FROZEN | {"VE/Limits.lean"}
             for i, line in enumerate(path.read_text().splitlines())
             if re.search(r"(>|≥) (10000|65536) (then|\|\|)|depth > 64", line) and "unit" not in line]
    ties = (LEAN / "VE/LimitTies.lean").read_text()
    assert found == [] and "maxNodes" in ties and "maxDepth" in ties


def test_the_lint_finds_each_limit_it_was_written_for():
    """Lines from the review's sites as they were: each is found, under the limit it hard-codes."""
    seeded = {
        "maxDepth (decoder fuel)": "  let fs ← (← j.getArr?).toList.mapM (decodeFormula 64)",
        "maxDepth": '    if depth > 64 then fails "ResourceLimit" "formula exceeds nesting limit 64"',
        "maxNodes": '        if nodes > 10000 then throw "ResourceLimit: AST exceeds 10,000 nodes"',
        "maxIdentifierBytes": '    if name.length > 64 then fault "ResourceLimit: Identifier exceeds 64 ASCII bytes"',
        "maxSourceBytes": '    if source.utf8ByteSize > 65536 then throw "ResourceLimit: source size"',
        "maxTuples": "  if rows > 100000 then throw tupleLimit",
        "maxEntities": '    if cells.size > 1000 then modelFault s!"/domains/{sort}" "ResourceLimit: domain exceeds entity limit"',
        "maxSorts/maxPredicates": "  if sorts.length > 32 || predicates.length > 256 then",
        "maxNumeralChars": "    if s.length > 40 then throw (.limit numeralLimit)",
        "maxJsonDepth": '      if depth > 256 then throw "ResourceLimit: JSON depth exceeds 256"',
        "maxIndex": "def maxNumber : Nat := 9007199254740991",
    }
    assert set(seeded) == set(PATTERNS)
    for limit, line in seeded.items():
        assert limit in {found for _, found, _ in hard_coded(f"def check : Unit :=\n{line}\n")}, limit
    # The same lines in a theorem statement, a comment, a string or another limit are not checks.
    assert hard_coded("theorem t : (decodeFormula 64 j).isOk := sorry\n") == []
    assert hard_coded("def f := 1 -- if nodes > 10000\n/- decodeFormula 64 -/\n") == []
    assert hard_coded('def f := "if nodes > 10000 then"\n') == []
    assert hard_coded('def f := require (units.length ≤ 10000) "ResourceLimit: unit count"\n') == []
    assert hard_coded("def NodesOK (n : Nat) : Prop := n ≤ 10000\n") == []


def test_the_frozen_generated_and_hashed_copies_are_tied_to_the_limits():
    """Each module that keeps a limit's literal and may not import `VE.Limits` has a guard in LimitTies."""
    guards = re.findall(r"^#guard.*(?:\n  .*)*", (LEAN / "VE/LimitTies.lean").read_text(), re.M)
    for module, limits in {
        "VE.JsonInput.parse": ("maxJsonDepth", "maxIndex", "maxPackageBytes"),
        "VE.JsonInput.parseCases": ("maxPackageBytes",),
        "VE.Bridge.identifier": ("maxIdentifierBytes",),
        "VE.Bridge.decodeDocument": ("maxNodes", "maxDepth"),
        "VE.Bridge.decodeCountermodel": ("maxNodes", "maxDepth"),
        "VE.Order.Wire.decodeFormulas": ("maxNodes", "maxDepth"),
        "VE.Order.Wire.runCase": ("maxNodes", "maxDepth"),
        "VE.CertificateWire.runClosureCase": ("maxNodes", "maxDepth"),
        "VE.CertificateWire.decodeClosureTrace": ("maxNodes", "maxDepth"),
        "VE.WireContract.Names": ("maxIdentifierBytes",),
        "VE.EnglishGrammar.maxSourceBytes": ("maxSourceBytes",),
    }.items():
        blocks = [guard for guard in guards if module in guard]
        assert blocks, module
        for limit in limits:
            assert any(limit in guard or "depthFault" in guard for guard in blocks), (module, limit)
    # The limits are reducible, so approved statements that name their values still hold of the checks.
    assert re.findall(r"^def max\w+", (LEAN / "VE/Limits.lean").read_text(), re.M) == []
