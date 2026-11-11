"""ap-3cb-adapt seeded bugs: each bug breaks `splitMap_exact` or `elaborate_parts`, in a /tmp copy only.

    uv run python docs/act-phrases/ap-3cb-adapt/seed_bugs.py

For each bug, one scratch file under a fresh temporary directory holds lean/VE/Acts/Elaborate.lean, the lemmas the
proofs use from lean/VE/Acts/Faithful.lean (sliced from `inj_of_nodup_map` to `part_mem_preds`, not copied) and
lean/VE/Acts/ElaborateProofs.lean (its import dropped), with the bug planted in the copy;
then E1 and E4 (their definitions sliced from lean/VE/Acts/ElaborateExamples.lean, not copied) and the bug's `#guard`s,
each one conjunct of a theorem evaluated on a fixture. `lake env lean` checks it against the built imports. A row is
KILLED when the check fails in the proofs or a guard (every failing theorem and guard is recorded), INVALID when it
fails in the definitions or the fixtures, SURVIVOR when it passes. A guard that passes under a bug shows the
statement still holds of that fixture (the result is refused, so the conjunct is vacuous there). Under three of the
bugs every split document is refused (an unmapped `over` names a rule that is gone, since `validate` refuses
precedence across predicates; a part keeping its source's name fails step 3 or `validate`), so the statements hold
of them and only the proofs and E1/E4's acceptance (`G_OK`, as ElaborateExamples.lean's `#guard`s) fail.
The committed files are never written. The unmutated pair must check (`restored`). Writes mutants.json beside this
file. Run it with the Lean build up to date.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / "mutants.json"
DEFS = "lean/VE/Acts/Elaborate.lean"
PROOFS = "lean/VE/Acts/ElaborateProofs.lean"

EXAMPLES = "lean/VE/Acts/ElaborateExamples.lean"
FAITHFUL = "lean/VE/Acts/Faithful.lean"
# Every conjunct guard reads the result of `elaborateMap`; a refused result passes it.
G_INDEX = "#guard (elaborateMap e1).toOption.all fun (_, M) => M.preds.all (1 ≤ ·.2.2)"
G_OVER = ("#guard (elaborateMap e4).toOption.all fun (U, M) => M.rules.all fun (n, m, i) =>\n"
          "  (U.D.T.nodes.find? (·.name == n)).all fun K => e4.U.D.T.nodes.any fun N => N.name == m && K.over == N.over.map (partRule · i)")
G_NAMES = ("#guard (elaborateMap e1).toOption.all fun (U, M) => (M.preds.map (·.1)).Nodup &&\n"
           "  M.preds.all fun (q, p, i) => q == partPred p i && !(U.D.T.regulated.any (·.name == p))")
G_OK = "#guard (elaborateMap e1).isOk && (elaborateMap e4).isOk"


def examples_guard(start):
    """The `#guard` of ElaborateExamples.lean that starts with `start` (sliced, not copied)."""
    ex = (ROOT / EXAMPLES).read_text()
    i = ex.index(start)
    return ex[i:ex.index("\n", i)]


G_SPLIT = examples_guard('#guard splitAtoms e1 "p027"')

# (id, file, definition, from, to, claim, guards)
BUGS = [
    ("parts-from-index-0", DEFS, "partsOf", "((sa p).getD []).zipIdx 1", "((sa p).getD []).zipIdx 0",
     "splitMap_exact: every part's index is at least 1 (the `1 ≤ i` conjuncts)", [G_INDEX, G_OK]),
    ("split-node-over-unmapped", DEFS, "splitNode", "over := N.over.map (partRule · x.2) }",
     "over := N.over }", "elaborate_parts: a part rule's `over` is mapped to part i (the rule half)",
     [G_OVER, G_OK]),
    ("part-keeps-source-name", DEFS, "splitMap",
     "(partsOf sa r.name).map fun x => (partPred r.name x.2, r.name, x.2)",
     "(partsOf sa r.name).map fun x => (r.name, r.name, x.2)",
     "splitMap_exact: a part has its own name, distinct from its source's and from the other parts' "
     "(`q = partPred p i` and the Nodup conjuncts)", [G_NAMES, G_OK]),
    ("part-declaration-keeps-source-name", DEFS, "splitReg",
     "xs.map fun x => { r with name := partPred r.name x.2, act",
     "xs.map fun x => { r with name := r.name, act",
     "splitMap_exact and elaborate_parts: a part is declared under its own name, and the source is gone",
     [G_NAMES, G_OK]),
    ("atoms-reversed", DEFS, "atomsOf", "if 2 ≤ atoms.length then some atoms else none",
     "if 2 ≤ atoms.length then some atoms.reverse else none",
     "the E1 and E4 examples' split pin: part 1 is torture (the theorems hold of any order; the pin catches it)",
     ["G_SPLIT"]),
    ("statement-index-from-2", PROOFS, "splitMap_exact",
     "q = partPred p i ∧ p ∈ D.U.D.T.regulated.map (·.name) ∧ p ∉ U'.D.T.regulated.map (·.name) ∧ 1 ≤ i",
     "q = partPred p i ∧ p ∈ D.U.D.T.regulated.map (·.name) ∧ p ∉ U'.D.T.regulated.map (·.name) ∧ 2 ≤ i",
     "the statement as 6.6 gives it is the one proved (a stronger, false clause fails the proof)", []),
]


def fixtures():
    """E1 and E4 with their helpers, sliced from ElaborateExamples.lean (from `def env` to E4's definition)."""
    ex = (ROOT / EXAMPLES).read_text()
    head = ex[ex.index("def env "):ex.index("/-- What a result shows")]
    e1 = ex[ex.index("def e1 "):ex.index("\n", ex.index("def e1 "))]
    e4 = ex[ex.index("def e4 "):ex.index("\n#guard", ex.index("def e4 "))]
    return ("namespace VE.Acts.SeedFixtures\nopen VE.Acts VE.Acts.TableExamples VE.Norms VE.NormDefaults\n"
            + head + e1 + "\n" + e4 + "\n")


def combined(defs, proofs, guards):
    """The scratch file and the last line of the definitions, the proofs (Faithful.lean's lemmas, then ElaborateProofs') and
    the fixtures."""
    body = proofs.replace("import VE.Acts.Faithful\n", "", 1)
    fa = (ROOT / FAITHFUL).read_text()
    lemmas = fa[fa.index("theorem inj_of_nodup_map"):fa.index("theorem part_mem_preds")]
    text = "import VE.Acts.TableExamples\n" + defs.rstrip("\n") + "\n\n"
    ends = [text.count("\n")]
    text += "namespace VE.Acts\nopen VE.Norms VE.NormDefaults\n" + lemmas + "end Parts\nend VE.Acts\n\n"
    text += body.rstrip("\n") + "\n\n"
    ends.append(text.count("\n"))
    text += fixtures()
    ends.append(text.count("\n"))
    text += "".join(g + "\n" for g in guards) + "end VE.Acts.SeedFixtures\n"
    return text, ends


def theorem_at(text, line):
    names = [m for m in re.finditer(r"^theorem (\S+)", text, re.M) if text[:m.start()].count("\n") + 1 <= line]
    return names[-1].group(1) if names else "?"


def check(text, ends):
    with tempfile.TemporaryDirectory(prefix="ap3cb-seed-") as d:
        f = Path(d) / "Seed.lean"
        f.write_text(text)
        env = dict(os.environ, PATH=f"{Path.home()}/.elan/bin:{os.environ['PATH']}")
        r = subprocess.run(["lake", "env", "lean", str(f)], cwd=ROOT / "lean", capture_output=True, text=True,
                           env=env, timeout=3600)
    errs = [(int(m.group(1)), m.group(0)) for m in re.finditer(r"Seed\.lean:(\d+):\d+: error.*", r.stdout + r.stderr)]
    if r.returncode == 0 and not errs:
        return "SURVIVOR", []
    if not errs or any(n <= ends[0] or ends[1] < n <= ends[2] for n, _ in errs):
        return "INVALID", [e for _, e in errs] or [(r.stdout + r.stderr)[-300:]]
    lines = text.split("\n")
    where = sorted({f"proof {theorem_at(text, n)}" if n <= ends[1] else f"guard `{lines[n - 1][:72]}`" for n, _ in errs})
    return "KILLED", where


def main():
    defs, proofs = (ROOT / DEFS).read_text(), (ROOT / PROOFS).read_text()
    restored, _ = check(*combined(defs, proofs, list(dict.fromkeys(G_SPLIT if g == "G_SPLIT" else g for b in BUGS for g in b[6]))))
    rows = []
    for bid, file, definition, old, new, claim, guards in BUGS:
        guards = [G_SPLIT if g == "G_SPLIT" else g for g in guards]
        src = defs if file == DEFS else proofs
        assert src.count(old) == 1, bid
        mutated = src.replace(old, new)
        text, ends = combined(mutated, proofs, guards) if file == DEFS else combined(defs, mutated, guards)
        result, failing = check(text, ends)
        rows.append({"id": bid, "file": file, "definition": definition, "claim": claim, "test": PROOFS,
                     "guards": guards, "result": result, "failing": failing})
        print(f"{result:9} {bid}: {'; '.join(failing)}")
    OUT.write_text(json.dumps({"restored": restored, "bugs": rows}, indent=2, ensure_ascii=False) + "\n")
    print("restored:", restored)
    sys.exit(0 if restored == "SURVIVOR" and all(r["result"] == "KILLED" for r in rows) else 1)


if __name__ == "__main__":
    main()
