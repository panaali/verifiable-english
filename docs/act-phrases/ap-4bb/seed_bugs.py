"""ap-4bb seeded bugs: plant each, build the fixtures, record what fails, restore.

    python3 docs/act-phrases/ap-4bb/seed_bugs.py      # writes docs/act-phrases/ap-4bb/mutants.json

Each plant replaces one text in one Lean file; a plant whose proof breaks first is also run with that proof replaced
by `sorry` (the `+guard` rows), so the #guard it must break is shown failing too. Every file is restored afterwards and
the fixtures rebuilt. A plant is KILLED when the build reports an error in a named theorem or #guard.
"""
import json, os, re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LEAN = ROOT / "lean"
S, P, X, U = "VE/Acts/Sources.lean", "VE/Acts/SourcesProofs.lean", "VE/Acts/Situation.lean", "VE/Readings/Unspecified.lean"
PICK_OLD = "match cs.find? (fun c => decide (c.Perm r)), pick cs rs with"
PICK_NEW = "match cs.find? (fun c => r.any (c.contains ·)), pick cs rs with"
ATOM_OLD = """  let probe := match rulePred D s i with
    | some p => if rulePred D s j == some p then .holds"""
ATOM_NEW = """  let probe := match rulePred D s j with
    | some p => if rulePred D s i == some p then .holds"""
SORRY_PICK = [(S, """  | [], σ, h => by cases h; exact .nil
  | r :: rs, σ, h => by
    unfold pick at h
    split at h
    · rename_i c σ' hc hσ
      cases h
      have hp := List.find?_some hc
      exact .cons (of_decide_eq_true hp) (pick_forall₂ hσ)
    · cases h
""", "  := sorry\n"),
              (P, """  | _, _, _, .nil => rfl
  | c :: σ, r :: rs, hm, .cons hcr hf => by
    have hc : c ∈ cs := hm c (List.mem_cons_self ..)
    have hfind : cs.find? (fun c => decide (c.Perm r)) = some c := by
      cases hx : cs.find? (fun c => decide (c.Perm r)) with
      | none => exact absurd (decide_eq_true hcr) (by simpa using List.find?_eq_none.mp hx c hc)
      | some c' =>
        have hp : c'.Perm r := by simpa using List.find?_some hx
        rw [eq_of_perm_of_pairwise hpw (List.mem_of_find?_eq_some hx) hc (hp.trans hcr.symm)]
    simp only [pick, hfind, pick_of_forall₂ hpw (fun c h => hm c (List.mem_cons_of_mem _ h)) hf]
""", "  := sorry\n")]
# (id, definition, behaviour, [(file, old, new)])
PLANTS = [
    ("hn-dropped", "VE.Acts.sourceCheck_complete", "B: `sourceCheck_complete` without item 8c's bound no longer elaborates",
     [(P, "    (hn : (VE.Readings.choices D).length ≤ VE.Readings.maxChoices)\n", "")]),
    ("pick-first-partial", "VE.Acts.pick", "B: `pick` takes the first choice sharing any view with the reading",
     [(S, PICK_OLD, PICK_NEW)]),
    ("pick-first-partial+guard", "VE.Acts.pick", "B: as above, its proofs `sorry`: S4/S6/64 through B's direction fail",
     [(S, PICK_OLD, PICK_NEW)] + SORRY_PICK),
    ("atom-j-for-i", "VE.Acts.atomSituation", "D: `atomSituation` probes j's act for i",
     [(X, ATOM_OLD, ATOM_NEW)]),
    ("atom-j-for-i+guard", "VE.Acts.atomSituation", "D: as above, `atomSituation_probe` `sorry`: the probe #guard fails",
     [(X, ATOM_OLD, ATOM_NEW), (X, "  simp [atomSituation, hi, hj]", "  sorry")]),
    ("rulePred-name", "VE.Acts.rulePred", "D: `rulePred` reads the rule's name for its predicate",
     [(X, "  | some (.norm N) => some N.pred", "  | some (.norm N) => some N.name")]),
    ("ruleView-no-mode", "VE.Acts.ruleView", "C: `ruleView` ignores the mode again (strict to default must be refused)",
     [(S, "     N.mode, N.rank, N.alterable, N.exception, N.hard)", "     .strict, N.rank, N.alterable, N.exception, N.hard)")]),
    ("ruleView-no-hard", "VE.Acts.ruleView", "C: `ruleView` ignores `hard`",
     [(S, "     N.mode, N.rank, N.alterable, N.exception, N.hard)", "     N.mode, N.rank, N.alterable, N.exception, false)")]),
    ("expected-constant-rank", "VE.Acts.expected", "C: `expected` types a constant rank instead of the template's lift",
     [(S, "s.completion, M.mode, M.rank,", "s.completion, M.mode, some \"r\",")]),
    ("view-drops-alterable", "VE.Acts.View", "C: `View` drops the alterable parties (compared as one fixed list)",
     [(S, "N.mode, N.rank, N.alterable, N.exception", "N.mode, N.rank, [], N.exception")]),
    ("strictNodeOf-default", "VE.Readings.strictNodeOf", "C: the norms lift `expected` reads gives mode default (DRI 11-11)",
     [(U, "  { toNode := M, mode := .strict, rank := none,", "  { toNode := M, mode := .default, rank := none,")]),
]


def build():
    env = {**os.environ, "PATH": f"{Path.home()}/.elan/bin:{os.environ['PATH']}"}
    r = subprocess.run(["lake", "build", "VE.Acts.ReadingsExamples"], cwd=LEAN, env=env, capture_output=True, text=True)
    out = r.stdout + r.stderr
    hits = sorted(set(re.findall(r"error: (VE/[\w/]+\.lean:\d+):", out)), key=lambda h: (h.split(":")[0], int(h.split(":")[1])))
    return r.returncode, hits


def main():
    rows = []
    for pid, decl, what, edits in PLANTS:
        saved = {f: (LEAN / f).read_text() for f, _, _ in edits}
        try:
            for f, old, new in edits:
                text = (LEAN / f).read_text()
                assert text.count(old) == 1, (pid, f, old)
                (LEAN / f).write_text(text.replace(old, new))
            rc, hits = build()
        finally:
            for f, text in saved.items():
                (LEAN / f).write_text(text)
        rows.append({"id": pid, "language": "Lean", "file": "lean/" + edits[0][0], "definition": decl, "behaviour": what,
                     "status": "KILLED" if rc != 0 and hits else "SURVIVED", "test": ", ".join("lean/" + h for h in hits)})
        print(rows[-1]["status"], pid, rows[-1]["test"], flush=True)
    rc, _ = build()
    out = {"item": "ap-4bb", "command": "python3 docs/act-phrases/ap-4bb/seed_bugs.py", "restored_build_returncode": rc,
           "mutants": rows}
    (Path(__file__).parent / "mutants.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
