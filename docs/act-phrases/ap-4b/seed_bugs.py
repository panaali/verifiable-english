#!/usr/bin/env python3
"""ap-4b's seeded bugs: plant each bug, build VE.Acts.ReadingsExamples, record the failing `#guard` or theorem lines
(KILLED), restore the file, and write mutants.json beside this script. At least one plant per new trusted definition
(`tools/trust_map.py`: the S and V declarations of Sources.lean and Situation.lean) and one per claimed behaviour. A
plant that changes the rule table fails the guards of the modules ReadingsExamples imports first, which stops the
build there; an `isolate` plant turns those modules' `#guard`s into `#eval`s for its build, so the source guards show
the bug on their own. Run from the repository root: `python3 docs/act-phrases/ap-4b/seed_bugs.py [ids...]`."""
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LEAN = ROOT / "lean"
S, T, G = "lean/VE/Acts/Sources.lean", "lean/VE/Acts/Situation.lean", "lean/VE/Acts/Grammar.lean"
UPSTREAM = ["lean/VE/Acts/RuleExamples.lean", "lean/VE/Acts/MeaningExamples.lean"]
OKV = "| .ok ps => compareViews ps (choiceViews D unspec s) (readingViews fx s Rs)"
# (file, id, definition, behaviour, before, after, isolate)
BUGS = [
    (G, "e1x-all-dropped", "globalRules", "the plan's seeded bug: the pre-modifier's `all` reading is dropped, so "
     "rs_u105b/c (S1, S8) must be refused", "[⟨.E1X, [adv], .edge .first⟩, ⟨.E1X, [adv], .edge .all⟩]",
     "[⟨.E1X, [adv], .edge .first⟩]", True),
    (S, "forall2-unrelated", "List.Forall₂", "the bijection relates nothing pointwise",
     "  | cons {a b l₁ l₂} : R a b → List.Forall₂", "  | cons {a b l₁ l₂} : List.Forall₂", False),
    (S, "source-no-units", "Source", "a source names no shared units",
     "  units : List String             -- fixed units every reading shares (u105a)\n", "", False),
    (S, "view-no-completion", "View", "a view holds no completion",
     "List String × VE.NormDefaults.Completion\nset_option", "List String\nset_option", False),
    (S, "ruleView-placeholder", "ruleView", "the completion is read from the frame's placeholder, not `unspec`",
     "⟨⟨D.frame.soft.E, [], ⟨[], [], []⟩⟩, unspec⟩ r", "⟨⟨D.frame.soft.E, [], ⟨[], [], []⟩⟩, []⟩ r", False),
    (S, "ruleView-sign", "ruleView", "the rule's sign is not compared",
     "(a, r.role, N.sign, N.guard", "(a, r.role, true, N.guard", False),
    (S, "ruleView-guard", "ruleView", "the rule's guard is not compared",
     "(a, r.role, N.sign, N.guard,", "(a, r.role, N.sign, .top,", False),
    (S, "expected-guard", "expected", "the template's guard is not compared",
     "s.sign, s.template.guard, s.template.carveOuts", "s.sign, .top, s.template.carveOuts", False),
    (S, "expected-over", "expected", "the template's precedence is not compared",
     "   s.template.over, s.completion)", "   [], s.completion)", False),
    (S, "choicesOn-no-dedup", "choicesOn", "choices that coincide on the listed sets are counted twice",
     "  firsts ((VE.Readings.choices D).map", "  ((VE.Readings.choices D).map", False),
    (S, "choicesOn-no-projection", "choicesOn", "sets the source does not list are kept in a choice",
     "(fun c => c.filter (fun x => sets.contains x.1))", "(fun c => c)", False),
    (S, "choiceRules-no-units", "choiceRules", "the shared units' rules are left out",
     "| .fixed u (.norm M) _ => if s.units.contains u then [M] else []", "| .fixed _ (.norm _) _ => []", False),
    (S, "choiceRules-all-units", "choiceRules", "every fixed unit's rule is taken, listed or not",
     "if s.units.contains u then [M] else []", "if true || s.units.contains u then [M] else []", False),
    (S, "choiceRules-no-sets", "choiceRules", "the chosen candidates' rules are left out",
     "      | some (.norm M) => [M]\n      | _ => []\n    | _ => []", "      | some (.norm _) => []\n      | _ => []\n    | _ => []",
     False),
    (S, "choiceViews-unspec", "choiceViews", "the choices are viewed with no `unspecified` names",
     "(choiceRules D s c).map (ruleView D unspec)", "(choiceRules D s c).map (ruleView D [])", False),
    (S, "readingViews-first", "readingViews", "a reading is viewed by its first simple act only",
     "Rs.map (fun R => R.map (fun x", "Rs.map (fun R => (R.take 1).map (fun x", False),
    (S, "opOfSource-sign", "opOfSource", "the template's sign is negated",
     "opOf ⟨\"\", [], false, s.role, none, none⟩ s.sign", "opOf ⟨\"\", [], false, s.role, none, none⟩ (!s.sign)",
     False),
    (S, "sourceExact-ordered", "SourceExact", "the statement claims the choices in the readings' order",
     "∃ σ, σ.Perm (choiceViews D unspec s) ∧ List.Forall₂ List.Perm σ (readingViews fx s Rs)\n\ntheorem pick",
     "∃ σ, σ = (choiceViews D unspec s) ∧ List.Forall₂ List.Perm σ (readingViews fx s Rs)\n\ntheorem pick", False),
    (S, "sourceCheck-no-compare", "sourceCheck", "the choices are not compared", OKV, "| .ok _ => .ok ()", False),
    (S, "sourceCheck-no-paraphrases", "sourceCheck", "equal paraphrases are not refused (D-32)",
     "match paraphrases fx op s.form \"the source phrase\" Rs with", "match Except.ok (ε := String) "
     "(Rs.map (paraphrase fx op s.form)) with", False),
    (S, "compare-no-reading-check", "compareViews", "a choice that is no reading is not named first",
     "if !cs.all (fun c => rs.any", "if false && !cs.all (fun c => rs.any", False),
    (S, "compare-no-pairwise", "compareViews", "two choices that are one reading pass",
     "else if !decide (cs.Pairwise", "else if false && !decide (cs.Pairwise", False),
    (S, "compare-no-bijection", "compareViews", "the matching need not be a bijection",
     "| some σ => if decide (σ.Perm cs) then .ok ()", "| some σ => if true then .ok ()", False),
    (S, "pick-any", "pick", "a reading is matched by any choice",
     "match cs.find? (fun c => decide (c.Perm r)), pick cs rs with", "match cs.head?, pick cs rs with", False),
    (S, "d29-no-code", "d29", "D-29's texts lose their code", "def d29 (m : String) : String := \"InvalidInput: \" ++ m",
     "def d29 (m : String) : String := m", False),
    (T, "atom-value-false", "atomSituation", "the witness's act is probed for `false`",
     "[], [], probe, true⟩", "[], [], probe, false⟩", False),
    (T, "atom-probe-other", "atomSituation", "the act probed is the other candidate's",
     "(rulePreds D s i).find? (fun p => !(rulePreds D s j).contains p)",
     "(rulePreds D s j).find? (fun p => !(rulePreds D s i).contains p)", False),
    (T, "atom-shared-act", "atomSituation", "an act both candidates regulate may be probed",
     "(fun p => !(rulePreds D s j).contains p)", "(fun _ => true)", False),
    (T, "rulePreds-none", "rulePreds", "a candidate's rule names no act", "  | some (.norm N) => [N.pred]\n",
     "  | some (.norm _) => []\n", False),
]


def build() -> tuple[int, list[str]]:
    p = subprocess.run(["lake", "build", "VE.Acts.ReadingsExamples"], cwd=LEAN, capture_output=True, text=True)
    lines = re.findall(r"^error: (VE/[^:]+\.lean:\d+):", p.stdout + p.stderr, re.M)
    return p.returncode, sorted(set("lean/" + x for x in lines), key=lambda s: (s.split(":")[0], int(s.split(":")[1])))


def main() -> None:
    only = set(sys.argv[1:])
    out = ROOT / "docs/act-phrases/ap-4b/mutants.json"
    rows = json.loads(out.read_text())["mutants"] if out.exists() and only else []
    rows = [r for r in rows if r["id"] not in only]
    for f, mid, defn, beh, before, after, isolate in BUGS:
        if only and mid not in only:
            continue
        path = ROOT / f
        text = path.read_text()
        assert text.count(before) == 1, (mid, text.count(before))
        saved = {u: (ROOT / u).read_text() for u in UPSTREAM} if isolate else {}
        try:
            path.write_text(text.replace(before, after))
            for u, t in saved.items():
                (ROOT / u).write_text(t.replace("#guard", "#eval"))
            rc, failing = build()
        finally:
            path.write_text(text)
            for u, t in saved.items():
                (ROOT / u).write_text(t)
        name = defn if "." in defn else f"VE.Acts.{defn}"
        rows.append({"id": mid, "language": "Lean", "file": f, "definition": name, "behaviour": beh,
                     "status": "KILLED" if rc != 0 and failing else "SURVIVED", "test": ", ".join(failing)})
        print(mid, rows[-1]["status"], rows[-1]["test"], flush=True)
    order = [b[1] for b in BUGS]
    rows.sort(key=lambda r: order.index(r["id"]) if r["id"] in order else len(order))
    rc, _ = build()
    out.write_text(json.dumps({"item": "ap-4b", "command": "python3 docs/act-phrases/ap-4b/seed_bugs.py",
                               "restored_build_returncode": rc, "mutants": rows}, indent=1, ensure_ascii=False) + "\n")
    sys.exit(0 if rc == 0 and all(r["status"] == "KILLED" for r in rows) else 1)


if __name__ == "__main__":
    main()
