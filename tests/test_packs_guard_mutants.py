"""The premise-pack fixtures can fail (pk-1 review F1, B; standing ruling R16 in DRI-RULINGS.md).

R16 signs pk-1's trust growth on the condition that every new trusted definition is exercised by a test that can
fail. The review found `#guard`s of `lean/VE/NormDefaults/PacksLegacyExamples.lean` that checked nothing (an empty
`head?.all`, `[] == []` on every source), so the mutants `fullEnv := envAt (fill U) 0` and `coherenceLabels := []`
passed every guard and broke only a tactic script, which does not count.

These tests remove that class for the whole module. They copy `Packs.lean` with its theorems stripped (a theorem's
tactic script is not a test of the definition) into the fresh namespace `VE.NormDefaults.PacksM`, with `Layered.lean`'s
`softPack`, `rightsPack` and kind-table rows (`legacyKinds`, `legacyRows`, `kindCase`; pk-1b) beside it, followed by
the two fixture files rewired to the copy. The unmutated copy must pass every guard; each mutant must fail at a
`#guard` and nowhere else (a mutant that does not elaborate proves nothing). Every trusted definition `tools/trust-classes.json` lists for `Packs.lean` has a mutant here, or is a
type, so a new definition without a killing mutant fails `test_every_trusted_definition_has_a_mutant`.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
import subprocess

import pytest

from subprocesses import HANG_TIMEOUT
from tests.lean_build import LEAN, ROOT, lean_build

PACKS = LEAN / "VE/NormDefaults/Packs.lean"
LAYERED = LEAN / "VE/NormDefaults/Layered.lean"
EXAMPLES = LEAN / "VE/NormDefaults/PacksExamples.lean"
LEGACY_EXAMPLES = LEAN / "VE/NormDefaults/PacksLegacyExamples.lean"
NAMESPACE = "VE.NormDefaults.Packs"
COPY = "VE.NormDefaults.PacksM"
# `Layered.lean`'s two packs and kind-table rows, copied under its own namespace so their bodies resolve as there
# (`layeredCase` is the real one).
WIRE_COPY = "VE.NormDefaults.Wire.PacksM"
LAYERED_DEFS = ("softPack", "rightsPack", "legacyKinds", "legacyRows", "kindCase")

# Types: a change to one fails the build of every use, so they have no mutant of their own.
TYPES = {"Pack", "PackKind", "RequestPath", "KindRow"}

# (definition, find, replace): the edit is applied to the copy, where `find` must occur exactly once.
MUTANTS = [
    ("packOrder", '["soft", "rights", "weighing"', '["rights", "soft", "weighing"'),
    ("reservedPrefixes", '("rights", "rights__"), ', ""),
    ("reserved", "reservedPrefixes.any (fun (_, x) => n.startsWith x)",
     "reservedPrefixes.all (fun (_, x) => n.startsWith x)"),
    ("Pack.names", "p.decls.map (·.1) ++ p.consts.map (·.1)", "p.decls.map (·.1)"),
    ("ownPrefixIn", "pre.any (fun (o, x) => o == p.id && n.startsWith x)", "pre.any (fun (_, x) => n.startsWith x)"),
    ("ownPrefix", ":= ownPrefixIn reservedPrefixes", ":= ownPrefixIn []"),
    ("ordered", ":= packOrder.filterMap (fun i => ps.find? (·.id == i))", ":= ps"),
    ("labelledX", ":= qs.flatMap (·.labelled)", ":= qs.reverse.flatMap (·.labelled)"),
    ("X", ":= (labelledX qs).map (·.2)", ":= ((labelledX qs).map (·.2)).reverse"),
    ("names", ":= qs.flatMap Pack.names", ":= (qs.drop 1).flatMap Pack.names"),
    ("packPremises", ":=\n  ((qs.find? (·.id == i)).map (·.labelled)).getD []", ":=\n  labelledX qs"),
    ("extendEnv", "| some s => some s | none => E.constants n", "| some _ => E.constants n | none => E.constants n"),
    ("fullEnv", "envAt (fill U) (size (fill U))", "envAt (fill U) 0"),
    ("envX", "extendEnv (envAt (fill U) 0)", "extendEnv (fullEnv U)"),
    ("firstRepeat", "else firstRepeat (n :: seen) rest", "else firstRepeat seen rest"),
    ("declaredIn", "(E.predicates n).isSome || (E.constants n).isSome", "(E.predicates n).isSome"),
    ("assembleIn", "named.find? (fun (_, n) => declaredIn E n)", "named.find? (fun (_, n) => declaredIn E n && false)"),
    ("assembleIn", "!p.names.all (ownPrefixIn pre p)", "!p.names.all (fun _ => true)"),
    ("assembleIn", "(names qs).length > 256", "(names qs).length > 257"),
    ("assembleIn", "firstRepeat [] (qs.flatMap (fun p => p.labelled.map",
     "firstRepeat [] (qs.reverse.flatMap (fun p => p.labelled.map"),
    ("assemble", "assembleIn reservedPrefixes (fullEnv U) used ps", "assembleIn reservedPrefixes (fullEnv U) 0 ps"),
    ("assemble", "assembleIn reservedPrefixes (fullEnv U) used ps", "assembleIn [] (fullEnv U) used ps"),
    ("legacyIds", '[[], ["soft"], ["soft", "rights"]]', '[[], ["soft", "rights"]]'),
    ("firstFailing", "if holds a then none else some (i, l)", "if holds a then some (i, l) else none"),
    ("packFault", "if legacyIds.contains (qs.map (·.id)) then", "if !legacyIds.contains (qs.map (·.id)) then"),
    ("labelledJson", '[("label", .str l), ("ast", VE.SoftNorms.Wire.enc a)] ++', '[("label", .str l)] ++'),
    ("elaborateArrays", '("rights", Json.arr ((packPremises qs "rights")', '("rights", Json.arr ((packPremises qs "soft")'),
    ("elaborateArrays", 'Json.arr ((packPremises qs "rights").map (fun (l, a) => labelledJson l a none)).toArray)]',
     'Json.arr ((packPremises qs "rights").map (fun (l, a) => labelledJson l a none)).toArray)] ++\n'
     '  (qs.filter (fun p => p.id != "soft" && p.id != "rights")).map (fun p => (p.id, Json.arr #[]))'),
    ("coherenceLabels", "(VE.SoftNorms.collidingPairs D).map (fun (M, N) => VE.SoftNorms.Wire.cohLabel M N)",
     "((VE.SoftNorms.collidingPairs D).map (fun (M, N) => VE.SoftNorms.Wire.cohLabel M N)).take 0"),
    ("xWithout", "(fun a => !drop.contains a.1)", "(fun a => drop.contains a.1)"),
    ("softPack", "softLabelledU U D, []⟩", "[], []⟩"),
    ("rightsPack", "VE.Rights.limPremisesLabelled R, []⟩", "[], []⟩"),
    # pk-1b: the kind table. The first is the spec's seeded bug (a row runs although its pack is absent).
    ("dispatch", "if ids.contains i then", "if true then"),
    ("dispatch", "| none => pure none", "| none => throw \"no row\""),
    ("dispatch", "match rows.find? (·.kind == kind) with", "match rows.reverse.find? (·.kind == kind) with"),
    ("dispatch", "| none => some <$> r.run L id j", "| none => pure none"),
    ("dispatch", "needs the {i} premise pack", "needs {i}"),
    ("legacyKinds", '"norm-defaults-status", "norm-defaults-report"]', '"norm-defaults-status"]'),
    ("legacyRows", "⟨k, none, fun L id j", "⟨k, some \"rights\", fun L id j"),
    ("legacyRows", "← layeredCase L id k j", "← layeredCase L id \"norm-defaults-elaborate\" j"),
    ("kindCase", "PacksM.dispatch legacyRows", "PacksM.dispatch []"),
]

TOP = re.compile(r"\S")
THEOREM = re.compile(r"(?:@\[[^\]]*\]\s*)?(?:private |protected )*(?:theorem|lemma)\b")


def chunks(text: str) -> list[str]:
    """Top-level blocks of a Lean source: a block starts at a column-0 line outside a comment; a doc comment joins
    the declaration after it. Only a copy for the compiler is built from these, and the unmutated copy must
    elaborate and pass every guard, so a wrong split fails closed."""
    out: list[str] = []
    depth = 0
    for line in text.splitlines(keepends=True):
        if depth == 0 and TOP.match(line) and not (out and out[-1].lstrip().startswith("/--")
                                                   and out[-1].rstrip().endswith("-/")):
            out.append(line)
        elif out:
            out[-1] += line
        else:
            out.append(line)
        depth += line.count("/-") - line.count("-/")
    assert depth == 0, "unbalanced comments"
    return out


def imports(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.startswith("import ")]


def is_theorem(block: str) -> bool:
    return bool(THEOREM.match(re.sub(r"^\s*/--.*?-/\s*", "", block, count=1, flags=re.S)))


def body(text: str) -> str:
    return "".join(c for c in chunks(text) if not c.startswith("import ") and not is_theorem(c))


def packs_copy() -> str:
    text = body(PACKS.read_text())
    assert text.count(f"namespace {NAMESPACE}\n") == 1 and text.count(f"end {NAMESPACE}\n") == 1
    return text.replace(f"namespace {NAMESPACE}\n", f"namespace {COPY}\n").replace(f"end {NAMESPACE}\n", f"end {COPY}\n")


def layered_copy() -> str:
    """`LAYERED_DEFS` with `Layered.lean`'s opens, their `Packs.` declarations the copy's."""
    blocks = chunks(LAYERED.read_text())
    opens = [c for c in blocks if c.startswith("open ")]
    defs = [c for c in blocks if any(re.match(rf"(?:/--.*?-/\s*)?def {name}\b", c, re.S) for name in LAYERED_DEFS)]
    assert len(defs) == len(LAYERED_DEFS), defs
    return (f"namespace {WIRE_COPY}\n" + "".join(opens) + "".join(re.sub(r"\bPacks\.", "PacksM.", d) for d in defs)
            + f"end {WIRE_COPY}\n")


def fixtures_copy() -> str:
    out = []
    for path in (EXAMPLES, LEGACY_EXAMPLES):
        text = body(path.read_text())
        end = f"end {NAMESPACE}.Fixtures\n"
        text = text[:text.index(end) + len(end)]  # what follows (the norms chain's theorem) is not a guard
        for name in LAYERED_DEFS:
            text = text.replace(f"VE.NormDefaults.Wire.{name}", f"{WIRE_COPY}.{name}")
        out.append(text.replace(f"namespace {NAMESPACE}.Fixtures\n", f"namespace {COPY}.Fixtures\n")
                   .replace(f"open {NAMESPACE}\n", f"open {COPY}\n").replace(end, f"end {COPY}.Fixtures\n"))
    return "".join(out)


def probe(packs: str, layered: str) -> str:
    heads = imports(PACKS.read_text()) + imports(LAYERED.read_text()) + imports(EXAMPLES.read_text()) \
        + imports(LEGACY_EXAMPLES.read_text())
    heads = [h for h in dict.fromkeys(heads) if h != "import VE.NormDefaults.PacksExamples"]
    return "\n".join(heads) + "\n" + packs + layered + fixtures_copy()


def mutate(text: str, find: str, replace: str) -> str:
    assert text.count(find) == 1, f"{find!r} occurs {text.count(find)} times"
    return text.replace(find, replace)


def mutated(name: str, find: str, replace: str) -> str:
    if name in LAYERED_DEFS:
        return probe(packs_copy(), mutate(layered_copy(), find, replace))
    return probe(mutate(packs_copy(), find, replace), layered_copy())


@pytest.fixture(scope="module")
def lake():
    path = shutil.which("lake")
    if path is None:
        pytest.skip("lake is not available")
    lean_build("VE")
    return path


def elaborate(lake: str, tmp_path: Path, text: str) -> subprocess.CompletedProcess:
    source = tmp_path / "PacksMutant.lean"
    source.write_text(text)
    return subprocess.run([lake, "env", "lean", str(source)], cwd=LEAN, capture_output=True, text=True,
                          timeout=HANG_TIMEOUT)


GUARD_FAILED = "did not evaluate to `true`"


def trusted() -> set[str]:
    table = json.loads((ROOT / "tools/trust-classes.json").read_text())["modules"]["VE/NormDefaults/Packs.lean"]
    names = {e if isinstance(e, str) else e["name"] for entries in table.values() for e in entries}
    assert all(n.startswith(NAMESPACE + ".") for n in names), names
    return {n.removeprefix(NAMESPACE + ".") for n in names}


def test_every_trusted_definition_has_a_mutant():
    assert trusted() - TYPES == {name for name, _, _ in MUTANTS} - set(LAYERED_DEFS)
    layered = json.loads((ROOT / "tools/trust-classes.json").read_text())["modules"]["VE/NormDefaults/Layered.lean"]
    names = {e if isinstance(e, str) else e["name"] for entries in layered.values() for e in entries}
    assert {f"VE.NormDefaults.Wire.{n}" for n in LAYERED_DEFS} <= names


def test_the_copy_keeps_every_definition_and_drops_every_theorem():
    copy = packs_copy()
    for name in trusted():
        short = name.rsplit(".", 1)[-1]
        assert re.search(rf"^(?:def|abbrev|inductive|structure) (?:Pack\.)?{re.escape(short)}\b", copy, re.M), name
    assert not re.search(r"^theorem ", copy, re.M)


def test_the_unmutated_copy_passes_every_guard(lake, tmp_path):
    done = elaborate(lake, tmp_path, probe(packs_copy(), layered_copy()))
    output = done.stdout + done.stderr
    assert done.returncode == 0 and "error:" not in output, output
    # The guards really ran on the copy: the copy's fixtures are there, and none of them reads the real module.
    assert f"{COPY}.Fixtures" in probe(packs_copy(), layered_copy())
    assert "VE.NormDefaults.Wire.softPack" not in fixtures_copy()


@pytest.mark.parametrize("name,find,replace", MUTANTS,
                         ids=[f"{name}-{i}" for i, (name, _, _) in enumerate(MUTANTS)])
def test_each_mutant_fails_a_guard(lake, tmp_path, name, find, replace):
    done = elaborate(lake, tmp_path, mutated(name, find, replace))
    output = done.stdout + done.stderr
    errors = output.count("error:")
    assert done.returncode != 0 and errors >= 1, f"mutant of {name} survives every guard"
    assert output.count(GUARD_FAILED) == errors, f"mutant of {name} fails outside a #guard:\n{output}"
