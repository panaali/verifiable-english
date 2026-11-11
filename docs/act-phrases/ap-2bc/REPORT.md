# ap-2bc: `read_normal`, the existence and bounds halves (deliverables 1, 2); uniqueness cut to ap-2bcb

FOLLOW-UP: ap-2bcb: (3) the unambiguity of normal forms, `read_normal` itself, and its fixture instances.

Branch `feature/ap-2bc`, base main `5f756e791d` (ap-parse-index merged: `02fffa4b93`). Spec
docs/spec/act-phrases.md 5.6, `read_normal` at line 917. Decisions: reviews/dri-decisions-20261030-ap-2bb.md items 1
and 3, reviews/dri-decisions-20261110-fable-interim-apply.md item 2.

SIZE: 1308 product (lean/VE/Acts/NormalProofs.lean 1307, lean/VE.lean 1), 27 tests (lean/VE/Acts/RenderExamples.lean
+26 −1), 200 other hand-written lines (seed_bugs.py 94, mutants.json 83, tools/trust-classes.json 23), plus this
REPORT and DELTA.md. Source: `git diff --numstat $(git merge-base HEAD main)`, generated inventories and codemap left
out. All product lines are proofs and proof helpers. The task estimated 600 to 1,200 lines in total; (1) and (2)
alone took 1,307.

## Statement gate

No statement changed. `read_normal`'s reviewed text (spec line 917) and the DRI-strengthened `normalOk`
(lean/VE/Acts/Meaning.lean) are as on main. `read_normal` is **not** stated in Lean (no `sorry`, no `axiom`: `python3
lean/audit.py` → `PASS: 853 source files; 9639 named theorem declarations audited ...; only the declared standard
axiom allowlist`). No definition in Grammar.lean, Meaning.lean, Linearize.lean, Readings.lean, Read.lean or
lean/VE/Grammar/ changed (`git diff --stat $(git merge-base HEAD main) -- lean/VE/Acts/{Grammar,Meaning,Linearize,Readings,Read}.lean lean/VE/Grammar`
is empty). No counterexample to `read_normal` was found, so the item does not stop on one.

## Delivered

All in lean/VE/Acts/NormalProofs.lean (new), checked by `lake build` (`Build completed successfully (1405 jobs)`).

**(1) Existence.** `normal_derived (V) (hV : framesOk V = true) (a) (ha : normalOk V a = true) : Derived V a.normal
(.one a.canon)`. The derivation is built rule by rule from 5.2's table:
`S → {0} SINGLE`, `SINGLE → [FW] [ADVSO] SC` (four of the six item shapes), `SC → HD | HD SM`, `SM → OWNM | ER`,
`OWNM → O | O ER`, `ER → EE+`, `O → FL | PL`. The elements are `EE → AR m` (one part), `EE → LST m false → OL m → MK m PL`
(a joined filler written with its marker once), and `EE → MK m FL` (a prepositional modifier). Parts are
`FL → WR | TOK` and lists `PL → FL PT`. There is one lemma per part kind (`gen_FL`, `gen_PT`, `gen_PL`), per element
(`gen_arg`, `gen_obj`, `gen_prep`, `gen_ADVSO`, `gen_FW`) and per level (`gen_SC`, `gen_SINGLE`, `gen_S`). The meaning
side is `single_meaning` (`singleAct` of an item without a split is one atom with its elements in order) and
`canon_eq` (that atom is `a.canon`). The proof ties rule numbers to the built grammar through `grammar_rule` and
`piecesOf_node`. It also needed facts that `framesOk` implies (`framesOk_lower`: heads, marker words and adverbs are
lower case, and no modifier marker is `""`), and two string facts that `decide` cannot evaluate (`toLower_of`: a word
whose letters are lower case is its own `toLower`; `wordsOf_empty`).

**(2) Bounds.** `parse_bounds (hG : G.wf = true) (w) : ∃ N0 b0, ∀ N b, N0 ≤ N → b0 ≤ b → ∃ ts, parse G N b w = some ts ∧
ts.length < N`. It holds for any well-formed grammar, `grammar V` included (`grammar_wf`). Notes on the task's plan
for (2):
- `parse_adequate`'s budget depends on the cap (`∃ b0` under a fixed `cap`), but `read_normal` needs one `b0` for every
  `N ≥ N0`. So (2) proves a cap-independent bound on the step charge. Every candidate list that `combine` builds is a
  duplicate-free list of derivations of a fixed span (`combine_ok`, ap-parse-index's invariant). There are finitely
  many such derivations (`finD_all`, `finDs`: induction on the word's length, then on the rank, by W2 and W3). So each
  rule attempt, each suffix position and each row is charged at most a sum that does not depend on the cap
  (`ntRowGo_steps`, `sufPosGo_steps`, `sufGroups_steps`, `rowAt_steps`, `fill_some`).
- `N0` is one more than the number of derivations of the start symbol over `w`, which bounds the result list through
  `parse_sound` and `parse_nodup`.

**From (1) and (2).** `read_normal_of_unique` proves `read_normal`'s conclusion under one more hypothesis: every
derivation of `a.normal` that has a meaning means `.one a.canon`. That hypothesis is exactly deliverable (3). It is a
hypothesis, not a claim, and the theorem is not `read_normal`.

**(4) Fixtures (part).** RenderExamples.lean has one `example` per fixture family. Each applies `normal_derived` to
G6, N1 to N3, N4 and N5, the canon family and a D9 (i) joined filler. `framesOk` and `normalOk` are checked by `#guard`
(evaluation; `decide` cannot evaluate `String.toLower`, and `native_decide` is forbidden by lean/audit.py). C1 to C4 and
FR3 keep their `normalOk`-false `#guard`s unchanged.

## Not delivered: (3) and `read_normal` (ap-2bcb)

(3) is the unambiguity argument: every derivation of `a.normal` that has a meaning means `.one a.canon`. With it,
`read_normal` is one line (`read_normal_of_unique`), and each RenderExamples round-trip `#guard` becomes an instance.

The cut is at the seam the task's cut rule names: "(1) and (2) reach ~600 lines → deliver (1) and (2), name (3) plus
`read_normal` as ap-2bcb". (1) and (2) took 1,307 lines. (3) needs an inverse analysis of every rule of 5.2 over
normal-form token lists, none of which exists yet. It needs at least:
- an inverse rule lookup (a built node's index is a schema rule with that left side, by the injectivity of `nm` on
  left sides);
- first-token sets for `L`, `T`, `MEL` and `MGT`, which rule out `COORD`, `MG` and `SPL` (a join word in a normal form
  is followed by a filler word, a slot or a fixed phrase);
- uniqueness of the head (`framesOk`'s duplicate and prefix checks);
- maximal munch of a filler run before the next marker (its first word is excluded from `fillExcl`);
- marker identity (`framesOk`'s prefix check, `m = " ".intercalate (wordsOf m)`).
Under standing override 1 this is a part that cannot pass its own tests yet, not a cut for size alone. The DRI was not
asked: the task file names this cut point (BUILDER-CHECKLIST 15).

## Seeded bugs (docs/act-phrases/ap-2bc/mutants.json, `python3 docs/act-phrases/ap-2bc/seed_bugs.py`)

The script plants each bug and runs the fixtures: RenderExamples' `#guard`s, on a copy without the `NormalProofs`
import so that a broken proof does not hide them. It then runs `lake build VE.Acts.NormalProofs`, restores the file
and rebuilds. `restored_build_returncode: 0`; 5 of 5 KILLED.

| id | file, definition | what fails |
|---|---|---|
| d9-dropped | Meaning.lean `normalOk`: `longEnd` dropped | C1 `#guard` (RenderExamples.lean:111), C2 (:114), the long last part (:119) and the long end in an object (:129); **(1)** no longer proves: `normal_derived` at NormalProofs.lean:783 (`hja` needs `longEnd ps = false`) |
| canon-args-kept | Linearize.lean `Atom.canon`: the object not put first | TableExamples.lean:206, :211 (fixtures; they stop the build before RenderExamples' `mixed.canon` guard); `atomOk_canon` (NormalProofs.lean:740) and `normal_derived` (:830, :841) |
| normal-marker-repeated | Linearize.lean `Atom.normal`: a joined filler written with its marker repeated | G7's render `#guard` TableExamples.lean:177; `normal_toks` NormalProofs.lean:695, :698 |
| spans-short | NormalProofs.lean `spans`: the spans ending at the last token missed | `cands_le` NormalProofs.lean:997 |
| vk1-reserved | RenderExamples.lean `Vk1` declares *then* | the `framesOk` `#guard` RenderExamples.lean:141 |

Only Lean product code changed (no Python or Rust), so all the bugs are Lean bugs. Each changed Lean file with a
definition has a plant: NormalProofs.lean (`spans`) and RenderExamples.lean (`Vk1`).

## Trust, DELTA, CPU

- Trust: `uv run python tools/trust_map.py --check` → `against 5f756e791d4c: K +0, S +0, D +0, G +0, tied +0,
  unclassified +0, trusted +0` and `PASS`. The proof helpers (`nm`, `symB`, `Gen`, `GenAll`, `PartOk`, `FrameOk`,
  `advWords`, `preps`, `FinD`, `FinDs`, `symRank`, `spans`, `posRhs`, `rowB`, and three tactic macros and a local
  notation) are classed P, and the fixture vocabulary `Vk1` T, in tools/trust-classes.json. No R16 row and no
  FOLLOW-UPS.md row. No trusted line of Linearize.lean or Meaning.lean is newly tied: those ties wait for
  `read_normal` (ap-2bcb). No trust_mutants sweep: checklist 13a applies to trusted growth, and there is none.
- DELTA: no rows (DELTA.md). No definition, text or answer changed.
- Lean CPU (R4): `lake env lean VE/Acts/NormalProofs.lean` takes `real 0m56.8s, user 2m19s` on the VM (the last full
  check before commit 7e12a73f2a); RenderExamples' build took 8.9 s. The proofs build once.
- Generated files (R12): `uv run python tools/regen_generated.py --write --skip route-cases`. route-cases needs the
  Rust release binary, which this worktree has not built, and no input of it changed. It wrote the Lean inventories,
  the audit manifest and the codemap. The codemap also picked up entries that were already stale on main
  (tests--part-8, docs__act-phrases).
- Pilot bytes: none expected. These are proofs only, and no rendering or answer changes.

## Tests

- While iterating: `lake env lean VE/Acts/NormalProofs.lean` and `lake build VE.Acts.NormalProofs
  VE.Acts.RenderExamples`.
- Final, on the committed tree (git status clean; tree 369be46f26): `MAC_PYTEST_NO_DEFER=1 zsh mac-pytest.sh --select --
  --base $(git merge-base HEAD main) --run` → `recorded 510 units for tree 369be46f26; 4 others left to the static
  graph until they run; 0 failed`, `summary: ran on ve-cloud-3, select_tests, exit=0, 9382s`. No test of
  main-known-red.txt was involved.

## Notes for the DRI

- `Vk` (RenderExamples' canon vocabulary) is not `framesOk`: `checkVocab Vk` = `InvalidInput: the adverb 'then' is not
  a lower-case word of letters, or is reserved` (`#eval`). So its round-trip `#guard`s check atoms that `read_normal`
  says nothing about. I added `Vk1` (`Vk` without *then*): `#guard framesOk Vk1 && !framesOk Vk`, and `mixed` reads back
  under it.
- `lean/audit.py` cannot parse a theorem name that ends in a prime (`'X'' depends on axioms`). The lemmas were renamed
  (`ap_SINGLE_of`, `gen_MK_of`).
- `parse_bounds` is a fact about the generic parser. It could live in lean/VE/Grammar/ with `parse_adequate`. That
  directory was out of scope here, so it stays in NormalProofs.lean.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., no relayed answer or schema changed.
2. Every required deliverable built, no rule broken: PARTIAL. (1) and (2) are built (`lake build`, `lean/audit.py`
   PASS). (3) and `read_normal` are cut at the task's named cut point to ap-2bcb (FOLLOW-UP line). (4) is in part
   (instances of (1)).
3. Tests and gates can fail: PASS, mutants.json (5 of 5 KILLED, each with its failing line).
4. Python, Lean and Rust agree: N.A., Lean proofs only.
5. R8 binding: N.A., no binding.
6. Gate evidence matches the final HEAD: PASS once the chain's gate runs on the final commit. The selected run is on
   the committed tree (below).
7. No unsigned item: PASS, DELTA.md has no rows, and trust is +0 (trust_map `PASS`).
8. Every user-visible change in DELTA: PASS, there is none (proofs and fixtures only).
9. Test selection finds the tests: PASS, the `--select` run covers the changed Lean files (below).
10. Lean statements say what is claimed: PASS. `normal_derived` and `parse_bounds` are what the REPORT says
    (NormalProofs.lean); seeded bugs d9-dropped, canon-args-kept, normal-marker-repeated and spans-short break their
    proofs. No `tools/check_*_statements.py` applies: no statement is new to the spec.
11. Budgets and limits fail closed: N.A., no runtime path changed. `parse_bounds` is about the existing budget.
12. No CPU or memory regression: PASS, no runtime code changed. NormalProofs elaboration time is above (R4).
13. Test-removed trailers: N.A., no test removed or renamed.
14. Both directions, cited evidence, spec re-read: PASS. `#guard framesOk Vk1 && !framesOk Vk` covers both sides,
    and C1 to C4 and FR3 keep their false side. Each claim above cites its command. Spec re-read: `read_normal`
    against docs/spec/act-phrases.md:917; `normalOk` against lean/VE/Acts/Meaning.lean (`normalOk`) and
    dri-decisions-20261030-ap-2bb.md item 1.
15. No overclaim, no silent cut, every check can fail, limits charged: PASS. The cut is named (above and on the
    FOLLOW-UP line). Each new `#guard` has a plant (vk1-reserved); the instance `example`s are proofs, broken by the
    plants of rows 1 to 3. N.A. for limits.

## Next item

FOLLOW-UP: ap-2bcb: (3) the unambiguity of normal forms, `read_normal` itself, and its fixture instances.
