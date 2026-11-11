# ap-2bc: `read_normal` (deliverables 1 to 4)

- Status: FIX of review ap-2bc-review.final.md done. All four deliverables are built; `read_normal` is stated as spec
  5.6 writes it and proved, on the standard axioms only (`lean/axioms.txt`). No `sorry`, no new axiom.
- What changed in the fix: F1, deliverable (3) (`normal_unique`, three new proof modules), `read_normal`, and 11
  fixture instances; F2, NormalProofs' header now says what that module proves. Two checks keep the class out: every
  declaration of spec 5.6 must be in Lean, and a module's first sentence may name only declared 5.6 theorems.
- Open items: none. No DRI signature is needed: DELTA.md has no rows, and trust is +0.
- Not run: the full gate and the trust-mutant sweep (no trusted growth; see "Trust"). The selected tests: see "Tests".

Branch `feature/ap-2bc`, base main `5f756e791d`. Spec docs/spec/act-phrases.md 5.6, `read_normal` at line 917.
Decisions: reviews/dri-decisions-20261030-ap-2bb.md items 1 and 3, reviews/dri-decisions-20261110-fable-interim-apply.md
item 2.

SIZE: 3,440 product lines (lean/VE/Acts/NormalProofs.lean 1,308, NormalInverse.lean 1,003, NormalBlocks.lean 575,
NormalUnique.lean 550, lean/VE.lean 4), all proofs and proof helpers; 55 fixture lines (RenderExamples.lean +55 −1);
138 test and tool lines (tests/test_ap56_statements.py 67, tools/check_ap56_statements.py 71); 356 other hand-written
lines (seed_bugs.py 114, mutants.json 178, tools/trust-classes.json 64); plus this REPORT and DELTA.md. Source: `git
diff --numstat $(git merge-base HEAD main)`, generated inventories and code map left out.

## Review findings

| finding | fix | regression test |
|---|---|---|
| F1 (B) deliverable (3), `read_normal` and its instances cut for size | (3) proved: `NormalProofs.normal_unique` (lean/VE/Acts/NormalUnique.lean, with NormalInverse.lean and NormalBlocks.lean); `VE.Acts.read_normal` from (1), (2) and (3); one `read_normal` instance per fixture family in RenderExamples.lean | `tests/test_ap56_statements.py::test_ap56_statements_equal_the_spec`, `::test_a_missing_or_changed_statement_fails` (the checker `tools/check_ap56_statements.py` fails on 10d7951b2e's lean/VE/Acts: `read_normal: theorem missing`); the seeded bugs below |
| F2 (A) NormalProofs' first sentence presents `read_normal` as proved | reworded: "The existence and bounds halves of `read_normal` …; `read_normal` itself, with the uniqueness half, is in `VE.Acts.NormalUnique`" (and `read_normal` is now proved) | `tests/test_ap56_statements.py::test_a_header_naming_an_unproved_theorem_fails` |
| F3 (C) a new `#guard` without a plant | not changed, and said as it is: `vk1-reserved` breaks the `framesOk` guard (RenderExamples.lean:143) only; the `mixed` guard (:144) and the instances' `normalOk` guard (:180) have no plant of their own | — |
| F4 (C) header names `normal_bounds` | the header names `parse_bounds`, which holds for any input | — |
| F5 (C) the `example`s take their hypotheses as arguments | kept, and said in RenderExamples' header: `decide` cannot evaluate `String.toLower` and `native_decide` is refused, so the `#guard`s check the hypotheses by evaluation | — |
| F6 (C) `N0` described as "one more than the number of derivations" | reworded below: an upper bound | — |
| F7 (C) code map misses seed_bugs.py | the code map is regenerated (`tools/code_map.py --write`) | — |

Both probes of the review fail on 10d7951b2e (run on that commit's files) and pass on this branch:
`PROBE F1` exit 0 (`theorem VE.Acts.read_normal` in lean/statements.txt; `'VE.Acts.read_normal' depends on axioms:
[propext, Classical.choice, Quot.sound]` in lean/axioms.txt), `PROBE F2` exit 0.

## Statement gate

No statement changed, and no definition outside the new proof modules. `read_normal` is spec line 917's text
(`python3 tools/check_ap56_statements.py` → `AP-2 5.6: 11 declarations equal the approved text (Derived, listing_ok in
their held form)`; the two held forms predate this item and are explained in the checker). `normalOk` is the
DRI-strengthened one on main. `git diff --stat $(git merge-base HEAD main) --
lean/VE/Acts/{Grammar,Meaning,Linearize,Readings,Read,Syntax}.lean lean/VE/Grammar` is empty.

## Delivered

**(1) Existence.** `normal_derived (V) (hV : framesOk V = true) (a) (ha : normalOk V a = true) : Derived V a.normal
(.one a.canon)`, built rule by rule from 5.2's table (NormalProofs.lean, unchanged by the fix).

**(2) Bounds.** `parse_bounds (hG : G.wf = true) (w) : ∃ N0 b0, ∀ N b, N0 ≤ N → b0 ≤ b → ∃ ts, parse G N b w = some ts ∧
ts.length < N`, for any input and any well-formed grammar (NormalProofs.lean). `N0` is an upper bound on the number of
derivations of the start symbol over `w`, plus one (the list `finD_all` gives covers every derivation); it bounds the
result list through `parse_sound` and `parse_nodup`. The step charge is bounded independently of the cap (`fill_some`).

**(3) Uniqueness.** `normal_pieces (V) (hV) (a) (ha) : Gen V (.n .S) a.normal ps → ps = [.act (.one a.canon)]`: every
derivation of the normal form from the start symbol has the pieces of the canonical atom; hence `normal_unique`: every
derivation that has a meaning means `.one a.canon`. The argument reads the rule table backwards:
- NormalInverse.lean: `gen_inv` (a derivation of a nonterminal is a rule of the table with that left side, `never`
  rules excluded) and the tactic `rules_of`, which lists a left side's rules; inversions of each token-level
  nonterminal (`kw_inv`, `mk_inv`, `j_inv`, `fw_inv`, `hd_inv`, `advso_inv`, `wr_inv`, `tok_inv`, `fl_inv`);
  `VocabOk`, the facts of `checkVocab` the argument uses (reserved words, no head or marker beginning another, markers
  and modifier markers disjoint, adverbs neither marker nor head words); `mk_block` (a marker's words fix the marker);
  `fl_part` (a filler run stops only where the next token is not a filler word); `pt_inv`, `pl_inv` (a joined
  filler's list reads back), `pl_one` and `jc_after_part` (a one-part filler is never followed by a comma or join word).
- NormalBlocks.lean: the elements after the object (`Blk`): `ee_block` (one element, with its piece), `er_blocks` (a
  run), `rl_false` (a list with the marker repeated cannot read a normal form), `spl_false` (no split construct: a
  split marker's filler is one part, a joined modifier needs a join word after a modifier), `o_block`, `os_false`,
  `ownm_block`, `sm_inv` (the object and every element, in order), `hd_same` and `sc_inv` (the head fixes the frame).
- NormalUnique.lean: `single_inv` (function words and adverbs split off by token class), `coord_false` (no
  coordination: in a normal form every comma or join word is followed by a part's first token, `Adj`, and a
  coordination's tail needs a join word or an item's first word there, `t_head2`), `s_inv`, `normal_pieces`,
  `normal_unique`, and `VE.Acts.read_normal := read_normal_of_unique V h a ha (normal_unique V h a ha)`.

**(4) Fixtures.** RenderExamples.lean: 11 `example`s apply `read_normal` (G6's two atoms, N1, N3, N4, the canon family
under `Vk1`, FR3's and FR5's accepted pairs, a joined object, a joined filler beside split markers, and a D9 (i) joined
filler), beside the five `normal_derived` instances; one `#guard` checks all eleven `normalOk` hypotheses and the
existing one `framesOk`. The round-trip `#guard`s check the same atoms at the production limits.

## Seeded bugs (docs/act-phrases/ap-2bc/mutants.json, `python3 docs/act-phrases/ap-2bc/seed_bugs.py`)

The script plants each bug, runs RenderExamples' `#guard`s on a copy without the proof import, then `lake build
VE.Acts.NormalUnique` (NormalProofs, NormalInverse, NormalBlocks, NormalUnique), restores the file and rebuilds:
`restored_build_returncode: 0`, 10 of 10 KILLED. The five rows below the line are the fix's, one per condition the
uniqueness argument rests on.

| id | file, definition | what fails |
|---|---|---|
| d9-dropped | Meaning.lean `normalOk`: `longEnd` dropped | RenderExamples.lean:112, :115, :120, :130; `normal_derived` NormalProofs.lean:784 |
| canon-args-kept | Linearize.lean `Atom.canon`: the object not put first | TableExamples.lean:206, :211; NormalProofs.lean:741, :831, :842 |
| normal-marker-repeated | Linearize.lean `Atom.normal`: a joined filler with its marker repeated | TableExamples.lean:177; NormalProofs.lean:696, :699 |
| spans-short | NormalProofs.lean `spans`: the spans ending at the last token missed | NormalProofs.lean:998 |
| vk1-reserved | RenderExamples.lean `Vk1` declares *then* | RenderExamples.lean:143 |
| split-joined-accepted | Meaning.lean `normalOk`: a joined filler under a split marker accepted | RenderExamples.lean:82, :85, :97; NormalProofs.lean:784 (the build stops there, before (3)) |
| marker-prefix-unchecked | Syntax.lean `checkVocab`: a marker may begin another | GrammarExamples.lean:174, :175, :255, :258, :260, :280; `vocabOk` NormalInverse.lean:284 |
| head-overlap-unchecked | Syntax.lean `checkVocab`: a head may begin another | GrammarExamples.lean:174, :175, :235, :296; `vocabOk` NormalInverse.lean:251 |
| fill-marker-first | Grammar.lean `fillExcl`: a marker's first word is a filler word | RuleExamples.lean:37, :51, :164, :182, :191, :202, :205; `ef_excl` NormalInverse.lean:516, :518 |
| tail-join-comma | NormalInverse.lean `tailToks`: the last part after a comma | NormalInverse.lean:638, :648, :687, :698, :712, :1000 |

Python (tools/check_ap56_statements.py, planted by hand and restored, `git status` clean after): the missing-theorem
check skipped → `tests/test_ap56_statements.py::test_a_missing_or_changed_statement_fails` FAILED; the header check
made a no-op → `::test_a_header_naming_an_unproved_theorem_fails` FAILED. No Rust changed.

## Trust, DELTA, CPU

- Trust: `uv run python tools/trust_map.py --check` → `against 5f756e791d4c: K +0, S +0, D +0, G +0, tied +0,
  unclassified +0, trusted +0` and `PASS`. The new definitions are proof helpers, classed P in tools/trust-classes.json
  (`Box`, `rules_of`, `VocabOk`, `IsTok`, `FillW`, `ExclW`, `JC`, `EF`, `Stop`, `Next`, `tailToks`, `Blk` and its four
  functions, `BlkOk`, `blocks`, `ObjOk`, `objToks`, `objPieces`, `TB`, `ADV`, `NTA`, `fwToks`, `coreToks`, `Adj`,
  `EndOk`), and the fixture predicate `ReadsBack` T. No R16 row. No trust-mutant sweep: checklist 13a applies to
  trusted growth, and there is none.
- DELTA: no rows (DELTA.md). No definition, text or answer changed.
- Lean CPU (R4): proofs only, no runtime path. `lake env lean` on this worktree: NormalInverse 28.6 s real (140 s user),
  NormalBlocks 17.0 s (77 s), NormalUnique 7.3 s (33 s); NormalProofs as before.
- Generated files (R12): lean/statements.txt, predicates.txt, declarations.txt (`python3 tools/lean_statements.py`),
  lean/VE/Audit.lean and axioms.txt (`python3 lean/audit.py --write` → `PASS: 856 source files; 9802 named theorem
  declarations audited …; only the declared standard axiom allowlist`), and the code map (`tools/code_map.py
  --write`). `tools/regen_generated.py --check` reported only the code map stale before that.

## Tests

- `cd lean && lake build` → `Build completed successfully (1408 jobs)`.
- `python3 lean/audit.py` → `PASS` (above).
- `uv run pytest -q tests/test_ap56_statements.py` → `3 passed`.
- Selected tests: see the last section (run on the committed tree).

## Notes for the DRI

- `Vk` (RenderExamples' canon vocabulary) is not `framesOk` (it declares *then*); `Vk1` is `Vk` without it, and its
  fixtures are inside the theorem.
- `lean/audit.py` cannot parse a theorem name that ends in a prime; no new name has one.
- `parse_bounds` is a fact about the generic parser and could live in lean/VE/Grammar/, which was out of scope.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., no relayed answer or schema changed.
2. Every required deliverable built: PASS, (1) to (4) (above); no cut.
3. Tests and gates can fail: PASS, mutants.json 10 of 10 KILLED; the checker's tests plant a missing and a changed
   statement and a header naming an undeclared theorem.
4. Python, Lean and Rust agree: N.A., Lean proofs and a statement checker.
5. R8 binding: N.A.
6. Gate evidence matches the final HEAD: the chain's gate runs on the final commit; the selected run is below.
7. No unsigned item: PASS, DELTA.md has no rows, trust +0.
8. Every user-visible change in DELTA: PASS, there is none.
9. Test selection finds the tests: see the selected run below.
10. Lean statements say what is claimed: PASS, `tools/check_ap56_statements.py` (all 11 declarations of 5.6).
11. Budgets and limits: N.A., no runtime path changed.
12. No CPU or memory regression: PASS, no runtime code changed.
13. Test-removed trailers: N.A., none removed.
14. Both directions, cited evidence, spec re-read: PASS; spec 5.6 re-read against lean/VE/Acts by the checker.
15. No overclaim, no silent cut: PASS; NormalProofs' header names its halves and points to NormalUnique.
