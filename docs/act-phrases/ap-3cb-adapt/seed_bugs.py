"""ap-3cb-adapt seeded bugs: each bug breaks `splitMap_exact` or `elaborate_parts`, in a /tmp copy only.

    uv run python docs/act-phrases/ap-3cb-adapt/seed_bugs.py

For each bug, one scratch file under a fresh temporary directory holds lean/VE/Acts/Elaborate.lean, the lemmas the
proofs use from lean/VE/Acts/Faithful.lean (sliced from `inj_of_nodup_map` to `part_mem_preds`, not copied) and
lean/VE/Acts/ElaborateProofs.lean (its import dropped), with the bug planted in the copy;
then E1 and E4 (their definitions sliced from lean/VE/Acts/ElaborateExamples.lean, not copied) and the bug's `#guard`s,
each one conjunct of a theorem evaluated on a fixture. `lake env lean` checks it against the built imports. A row is
KILLED when the check fails in the proofs or a guard (every failing theorem and guard is recorded), INVALID when it
fails in the definitions or the fixtures, SURVIVOR when it passes. Every row also carries one acceptance guard per
fixture (`ACCEPT`, as ElaborateExamples.lean's `#guard`s), and records under `accepted` which of E1 and E4 the bugged
`elaborateMap` still accepts. A conjunct guard reads only an accepted result, so it is vacuous on a fixture whose
`accepted` is false: which fixtures a bug refuses is read from `accepted`, never assumed for every document.
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
# One acceptance guard per fixture, so the evidence says which fixture a bug refuses (not one `&&` over both).
ACCEPT = {"e1": "#guard (elaborateMap e1).isOk", "e4": "#guard (elaborateMap e4).isOk"}


def examples_guard(start):
    """The `#guard` of ElaborateExamples.lean that starts with `start` (sliced, not copied)."""
    ex = (ROOT / EXAMPLES).read_text()
    i = ex.index(start)
    return ex[i:ex.index("\n", i)]


G_SPLIT = examples_guard('#guard splitAtoms e1 "p027"')

# (id, file, definition, from, to, claim, guards)
BUGS = [
    ("parts-from-index-0", DEFS, "partsOf", "((sa p).getD []).zipIdx 1", "((sa p).getD []).zipIdx 0",
     "splitMap_exact: every part's index is at least 1 (the `1 ≤ i` conjuncts)", [G_INDEX]),
    ("split-node-over-unmapped", DEFS, "splitNode", "over := N.over.map (partRule · x.2) }",
     "over := N.over }", "elaborate_parts: a part rule's `over` is mapped to part i (the rule half)",
     [G_OVER]),
    ("part-keeps-source-name", DEFS, "splitMap",
     "(partsOf sa r.name).map fun x => (partPred r.name x.2, r.name, x.2)",
     "(partsOf sa r.name).map fun x => (r.name, r.name, x.2)",
     "splitMap_exact: a part has its own name, distinct from its source's and from the other parts' "
     "(`q = partPred p i` and the Nodup conjuncts)", [G_NAMES]),
    ("part-declaration-keeps-source-name", DEFS, "splitReg",
     "xs.map fun x => { r with name := partPred r.name x.2, act",
     "xs.map fun x => { r with name := r.name, act",
     "splitMap_exact and elaborate_parts: a part is declared under its own name, and the source is gone",
     [G_NAMES]),
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
    text += "".join(g + "\n" for g in guards)
    first = text.count("\n") + 1
    text += "".join(g + "\n" for g in ACCEPT.values()) + "end VE.Acts.SeedFixtures\n"
    return text, ends + [first]


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
    lines = text.split("\n")
    # Each `ACCEPT` guard is its own line after the bug's guards (`ends[3]` on), so its error says which fixture is refused.
    assert lines[ends[3] - 1:ends[3] - 1 + len(ACCEPT)] == list(ACCEPT.values())
    accepted = {fx: ends[3] + k not in {n for n, _ in errs} for k, fx in enumerate(ACCEPT)}
    if r.returncode == 0 and not errs:
        return "SURVIVOR", [], accepted
    if not errs or any(n <= ends[0] or ends[1] < n <= ends[2] for n, _ in errs):
        return "INVALID", [e for _, e in errs] or [(r.stdout + r.stderr)[-300:]], None
    where = sorted({f"proof {theorem_at(text, n)}" if n <= ends[1] else f"guard `{lines[n - 1][:72]}`" for n, _ in errs})
    return "KILLED", where, accepted



def main():
    defs, proofs = (ROOT / DEFS).read_text(), (ROOT / PROOFS).read_text()
    restored, _, restored_accepted = check(*combined(defs, proofs, list(dict.fromkeys(G_SPLIT if g == "G_SPLIT" else g for b in BUGS for g in b[6]))))
    rows = []
    for bid, file, definition, old, new, claim, guards in BUGS:
        guards = [G_SPLIT if g == "G_SPLIT" else g for g in guards]
        src = defs if file == DEFS else proofs
        assert src.count(old) == 1, bid
        mutated = src.replace(old, new)
        text, ends = combined(mutated, proofs, guards) if file == DEFS else combined(defs, mutated, guards)
        result, failing, acc = check(text, ends)
        rows.append({"id": bid, "file": file, "definition": definition, "claim": claim, "test": PROOFS,
                     "guards": guards + list(ACCEPT.values()), "result": result, "failing": failing, "accepted": acc})
        print(f"{result:9} {bid}: {'; '.join(failing)}; accepted {acc}")
    OUT.write_text(json.dumps({"restored": restored, "restored_accepted": restored_accepted, "bugs": rows}, indent=2,
                              ensure_ascii=False) + "\n")
    print("restored:", restored, restored_accepted)
    ok = restored == "SURVIVOR" and restored_accepted == dict.fromkeys(ACCEPT, True)
    sys.exit(0 if ok and all(r["result"] == "KILLED" for r in rows) else 1)


if __name__ == "__main__":
    main()
