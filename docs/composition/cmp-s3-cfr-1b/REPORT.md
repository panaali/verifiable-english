# cmp-s3-cfr-1b: the clauses-elaborate relay, 9.1/9.2 fixtures, W1's budget, `clauseSlot_wellFormed`

No DRI signature is reserved in this item. Branch feature/cmp-s3-cfr-1b. Plan: prompts/task-cmp-s3.txt deliverables
(1) (only `clauseSlot_wellFormed`), (3), (4), (5); docs/spec/right-clauses.md 8.4, 9.1-9.3, W1. Scope ruling:
reviews/dri-decisions-20261110-cmp-s3-cfr-1b.md (Q1: RC1-RC5 rendering moved; Q2: the proof stays, proof lines exempt
from the size line). Prerequisite cmp-s3-cfr-1 is on main (merge base, then main merged at the end). Three route
verdicts of (2) are not built here: moved to cmp-s3-cfr-1c (reviews/dri-decisions-20261111-cmp-s3-cfr-1b.md item 1);
see "Moved".

## Deliverables

| Plan row | Delivered by | Test or #guard |
|---|---|---|
| (1) ve/right_clauses.py relays Lean's `clauses-elaborate` (decode, check and plain are Lean's; Python sends and binds, R8) | 4e3667a472 | tests/test_right_clauses.py::test_right_clauses_differential |
| (1) "render RC1-RC5" | not delivered, moved: RC1-RC4 to cmp-s3-cfr-1d, RC5 to cmp-s3-candrel (reviews/dri-decisions-20261110-cmp-s3-cfr-1b.md item 1; spec 2 shows each RC only through W7) | none |
| (1) byte for byte with Lean on K1-K15, F11, F12, F14 | 735cd7ed66 | test_right_clauses_differential (plained bytes and slot rows equal; refusals raise Lean's text as its class; K10, K11, K12, K14 texts pinned) |
| Schema and binding, fuzz that retypes and rebinds each field (R8) | 4e3667a472, 735cd7ed66 | test_right_clauses_relay_binds_every_field; tools/relay_mutation_gate.py --route service:clauses-elaborate: 528 mutants, 528 refused, 0 allowed (CFR1A/CFR1B allow rows dropped) |
| (2) 9.1 K2, K3, K10, K13: the head's answers (K3's route verdict excepted, row below) | Examples.lean (cmp-s3-cfr-1 sections K2, K3, K13; slot at layer 0 in this item's section), differential | K_FIXTURES, DIFFERENTIAL rows K2, K3, K10, K13 (K13: `Lim_D`'s premise before `Rel_D`'s) |
| (2) 9.2 F11-F14: the head's answers (G8 waits for cmp-s3-candrel; F12's and F14's route verdicts excepted, row below) | Examples.lean "cmp-s3-cfr-1b" section | #guards; F11, F12, F14 in the differential |
| (2) the route verdicts of K3, F12 and F14 (spec 4.1 step 6) | not delivered, moved to cmp-s3-cfr-1c (reviews/dri-decisions-20261111-cmp-s3-cfr-1b.md item 1); see "Moved" | none here; cfr-1c's test_right_clauses_k3_route_fragment, test_right_clauses_f12_route_open, test_right_clauses_f14_route_admitted |
| (2) K9, K10, K15 | K_FIXTURES, DIFFERENTIAL | test_right_clauses_differential |
| (2) W1's 10,000-node budget on `plain D`, a large well-formed document within it (evaluator rule 2026-10-27) | 4e3667a472 (the head charges lines before decoding, spans in O(s log s), cites by one set, deep plain guards) | test_right_clauses_w1_budget: four 400-atom clauses read; four 833-atom clauses pass the node budget (the layer budget refuses them); one atom more is `AST exceeds 10,000 nodes`; 257 lines, 64 conjuncts, 30,000 spans and 20,000 cites end within the deadline |
| (3) `clauseSlot_wellFormed` (8.4) as stated | 8d9ade24d6 | the statement is spec 8.4's word for word; standard axioms only (lean/audit.py); Examples.lean checks the slot at layer 0 on K3, K13, F11 |
| (4) the differential and the profile-off test (K10) as tests | 735cd7ed66 | test_right_clauses_differential (K10 pinned); cmp-s3-cfr-1's profile-off tests unchanged |
| b15b oracle records right-clauses@0, `profiles == set(BY_NAME)` restored (reviews/dri-decisions-20261110-stale6h-0506.md item 1) | 735cd7ed66 | tests/test_model_environment.py::test_the_oracle_reaches_every_profile_and_display_field |
| (5) seeded bugs | mutants.json | below |

`clauseSlot_wellFormed`'s proof: the base vocabulary sits inside layer 0 of `correlate (plain D)`, because the base
stratum graph is part of the correlated one (`PWF.layer_names`), generated names are fresh (`PWF.genDecls_fresh`, the
soft check), and rights' `checkShape` puts the right's holder sort on the holder slot. So the cmp-s3 REPORT's missing
premise ("every regulated or defined name is a layer name of the base tree") does follow from `WellFormedRights (plain D)`.

## Moved

Not built in this item; moved to cmp-s3-cfr-1c (reviews/dri-decisions-20261111-cmp-s3-cfr-1b.md item 1, under R9),
together with spec 4.1 step 6 for both heads. Each is a route verdict: it exists only once the head hands the plained,
key-free document to the head `dispatch` names, with Rel_D in the slot, and no route does that yet. This item keeps
K3, F12 and F14 as #guards on the head and in the differential (rows above).

- (a) K3's report `fragment: no (rights:relation:equal-access:total)` (cfr-1c: test_right_clauses_k3_route_fragment).
- (b) F12's unit OPEN through the open term `full_equality` (cfr-1c: test_right_clauses_f12_route_open).
- (c) F14's set admitted through S1 on plained candidates, separated at the non-country pair, worded by composition.md
  E19 (cfr-1c: test_right_clauses_f14_route_admitted).

## Main's answers (the DELTA's evidence)

On a build of this tree without the two new charges (`lineObjects`, `deepLine`), the mode answered as main does:
64, 65 and 100 conjuncts, 63 plus a relation and 40,000 conjuncts (3.5 MB) gave `ResourceLimit: formula depth
exceeds 64`, the head's text. 257 copies of one line gave `DuplicateDeclaration: rule equal-access` (now
`ResourceLimit: rules`, R2). 256 and 257 distinct lines gave `ResourceLimit: vocabulary size`. So the depth charge
shows in no answer below the request size limits. A `#guard` on `deepLine` itself (RunExamples.lean) is what makes
its mutants fail.

## Seeded bugs (each planted alone, restored; mutants.json)

| Behaviour | File | Mutant | Fails |
|---|---|---|---|
| K8: totality on a non-holder slot accepted | lean/VE/RightClauses/Plain.lean `relationOk` | `hs == some j` dropped | the kernel refuses `clauseSlot_wellFormed`'s proof (Relation.lean:472); ve_service imports Relation, so no mutant build runs |
| K2: `Rel_D` built for total null | lean/VE/RightClauses/Relation.lean `relPremisesLabelled` | null read as slot 1 | `clauseSlot_no_total`'s proof (Relation.lean:40) |
| K10: profile-off text changed | lean/VE/RightClauses/Run.lean `elaborateCase` | "requires" to "needs" | RunExamples.lean:85 #guard |
| Line charge | Run.lean `lineObjects` | count minus one | RunExamples.lean:152, :183 |
| Line charge dropped | Run.lean `elaborateCase` | check deleted | RunExamples.lean:183 |
| Depth charge | Run.lean `deepLine` | `≥` to `>` | RunExamples.lean:165 (`deep`) |
| Spans in O(s log s) | Plain.lean `checkSpans` | adjacent spans refused | Examples.lean:114, :396 (pairwise reference) |
| Cites by one set | Plain.lean `checkBody` | `u9…` accepted | Examples.lean:175, :176 |
| The differential | ve/right_clauses.py `bind` | plained re-serialised by Python | test_right_clauses_differential |
| Binding | ve/right_clauses.py `bind` | totality labels unchecked | test_right_clauses_relay_binds_every_field |
| Soft frame | ve/softnorms.py `check_soft_source` | profile kept | test_right_clauses_rights_environment_reads_the_profile |
| Depth charge on any line | Run.lean `deepLine` | `any` to `all` (trust mutant M024) | RunExamples.lean:168 (`deep`, one deep line among shallow ones) |
| Line charge on a bodiless unit | Run.lean `lineObjects` | `getD 0` to `getD 1` (M035) | RunExamples.lean:152 |
| Depth charge on candidates | Run.lean `deepLine` | only the first candidate group read (M062) | RunExamples.lean:180 (`deepIn`) |
| The module docstring defers to `bind` (review F2) | ve/right_clauses.py module docstring | "no row missing or extra" restored | test_right_clauses_bind_counts_only_what_its_docstring_binds |
| `Lim` rows are not counted (review F2) | ve/right_clauses.py `bind` | a repeated `Lim` label refused | test_right_clauses_bind_counts_only_what_its_docstring_binds (K13 `[Lim, Lim, Rel]`) |
| The REPORT lists every moved item (review F1) | REPORT.md | this item's REPORT at 3a5e040544 | test_right_clauses_report_lists_every_moved_item ("Moved" missing) |

The K8 and K2 mutants are refused by the kernel in the proofs that state those behaviours (`clauseSlot_wellFormed`,
`clauseSlot_no_total`), not at a hash or build step of the tooling. No `#guard` can catch them, because the mutated
module no longer builds.

## Trust (R16)

`uv run python tools/trust_map.py --check` on the final HEAD: "against 69fc95777676: K +0, S +6, D +0, G +17, tied +0,
unclassified +0, trusted +23" (Plain.lean +6: `checkSpans`, `checkBody`; Run.lean +17: `lineObjects`, `deepLine`,
`elaborateCase`'s two charges), "PASS: K, S and untied [V] within 69fc95777676 and the allowances introduced since".
This is recorded in docs/trust-baseline.json as S +6 and V +17, "SIGNED by standing ruling R16 (DRI-RULINGS.md),
cmp-s3-cfr-1b, 2026-11-11". The item's fixtures and helpers in Examples.lean and RunExamples.lean are classed `T`, and
`lineObjects` and `deepLine` are classed `G[V]` like `elaborateCase` (tools/trust-classes.json). The FOLLOW-UPS.md row
`## cmp-s3-cfr-1b` asks for the ties pass.

Trust mutants: `zsh mac-pytest.sh --trustmut -- --max-mutants 1000 --test lean/VE/RightClauses/Examples.lean --test
lean/VE/RightClauses/RunExamples.lean --allow docs/composition/cmp-s3-cfr-1b/trust-mutants-allow.json --rescore <prev>
--json docs/composition/cmp-s3-cfr-1b/trust-mutants.json` exited 0 at 4f5ff9a5c3: 79 KILLED, 11 ALLOWED, 23 INVALID,
0 SURVIVOR, 0 UNKNOWN, 0 NOT RUN. Each of `checkSpans`, `checkBody`, `checkClauses`, `checkCandidates`,
`elaborateCase`, `lineObjects` and `deepLine` has killed mutants. The allow file gives each allowed operator its
reason: it does not elaborate, or it is `take 1` / `reverse.take 1` on an Option's list.

The first sweep (60 mutants) left survivors in `deepLine` (`any`→`all`, candidates, the last line) and in
`lineObjects` (`getD`). The `deep`, `deepIn` and bodiless-unit `#guard`s now kill them.

## Size

SIZE: 485 product (Relation.lean 272 proof lines, exempt by reviews/dri-decisions-20261110-cmp-s3-cfr-1b.md item 2;
ve/right_clauses.py 157, Plain.lean 34, Run.lean 17, ve/softnorms.py 5), 369 tests (tests/ 233, Examples.lean 93,
RunExamples.lean 43), 281 other hand-written lines (these docs, the probe, mutants.json, the allow file, the relay gate
34, trust-classes.json 26, RIGHT-CLAUSES.md 7, layer policy 2). Measured with `git diff --numstat $(git merge-base HEAD
main) HEAD`, generated files and recorded fixtures excluded.

## Overlaps

feature/cmp-s3a-cfr-3 also edits Examples.lean, Run.lean, RunExamples.lean and tests/test_right_clauses.py. This
item's lines sit in their own sections ("cmp-s3-cfr-1b"), except Run.lean's two checks in `elaborateCase`.

## Pilot bytes

None expected. This item adds a relay and refusals that come earlier. UDHR `elided_bytes` and the re-audit are
cmp-s3a-cfr-3's. Nothing is claimed before a pilot audit.

## Next items

cmp-s3-cfr-1d (RC1-RC4 rendering through W7), cmp-s3-candrel (G8, RC5, F13's set form), cmp-s3-cfr-1c (reading
candidates under the profile, K12's join, spec 4.1 step 6 for both heads, and the route verdicts of K3, F12 and F14:
see "Moved", reviews/dri-decisions-20261111-cmp-s3-cfr-1b.md item 1).

## Notes for the DRI

- The proof helper `SlotWF.bind_ok'` is renamed `SlotWF.except_bind_ok_iff`: lean/audit.py rejects the primed name in
  `#print axioms` output ("Unexpected audit output"). No statement changes.
- `deepLine` also reads candidate lines. The wire builds none yet (`cands = []`, Wire.lean:187), so `deepIn` builds
  ClauseDocs with candidates directly. That way the charge is in place when cmp-s3-cfr-1c reads candidates.

## Spec re-read

- `clauseSlot_wellFormed` (Relation.lean:471) against docs/spec/right-clauses.md:477-478: same binders, hypotheses and
  conclusion.
- K10 (tests/test_right_clauses.py differential, RunExamples.lean:85) against right-clauses.md:579: the profile-off text
  is cmp-s3-cfr-1's, and nothing else changes.
- W1 (test_right_clauses_w1_budget) against right-clauses.md:609-610: the AST budget is W1's own text, with no new limit.
  The two earlier charges answer W1's existing texts (`ResourceLimit: rules`, `formula depth exceeds 64`), as DELTA
  rows 1 and 2 under R2.
- K3, F12, F14 (right-clauses.md:572, 591, 593) against what is built: the head's columns (slot, plain guard,
  `elided`, `selectsAt`, `plainContent`) are #guards and differential rows. The route columns, K3's
  `fragment: no (…:total)`, F12's "unit OPEN through the open term" and F14's "admitted through S1 … worded by E19",
  are not built: moved to cmp-s3-cfr-1c (reviews/dri-decisions-20261111-cmp-s3-cfr-1b.md item 1; "Moved").

## Review fixes (cmp-s3-cfr-1b-review.final.md, text only; no answer, verdict or binding changes)

- F1: the three route verdicts the DRI moved (reviews/dri-decisions-20261111-cmp-s3-cfr-1b.md item 1) are listed:
  summary, Deliverables (not delivered), "Moved", Next items, Spec re-read, self-review 2 and 15.
  test_right_clauses_report_lists_every_moved_item checks every moved verdict in each of those places, and that no
  plan (2) row naming its fixture claims it unexcepted.
- F2: ve/right_clauses.py's module docstring no longer says `bind` leaves "no row missing or extra"; it defers to
  `bind`'s docstring, which owns the contract. test_right_clauses_bind_counts_only_what_its_docstring_binds pins both
  sides on K13: a `Lim` row dropped or doubled binds (review note C1), a totality row or plained unit dropped or doubled
  does not.

## Tests run

- `cd lean && lake build`: "Build completed successfully (1400 jobs)" (after the merge of main), and the edited
  modules again after each guard. `python3 lean/audit.py`: "PASS: 845 source files; 9485 named theorem declarations
  audited".
- `uv run python tools/regen_generated.py --write`, then `--check`: "checked 39 entries".
- `uv run python tools/gate_collection.py --check --prebuilt`: "8 added, 0 removed by a trailer, 0 refused, 0 stale
  and 0 malformed trailers".
- Selected tests on the committed tree fb50a170b0: `MAC_PYTEST_NO_DEFER=1 zsh mac-pytest.sh --select -- --base
  $(git merge-base HEAD main) --run` gave "recorded 514 units for tree ac809bd7c4; ... 0 failed", "ran on ve-cloud-2,
  select_tests, exit=0". Commits after it touch docs/*.md only.
- Pre-existing failures from main-known-red.txt: none met.

## Self-review against BUILDER-CHECKLIST

1. Typed and contained: PASS. test_right_clauses_relay_binds_every_field retypes each answer field (7, true, null,
   [], {}, 1.5, a nested list) and a 100,000-deep plained text. tools/relay_mutation_gate.py --route
   service:clauses-elaborate: 528 mutants, 528 refused.
2. Deliverables built: PASS. See the Deliverables table (commit and test per row). RC1-RC5 were moved by
   reviews/dri-decisions-20261110-cmp-s3-cfr-1b.md item 1; the route verdicts of K3, F12 and F14 by
   reviews/dri-decisions-20261111-cmp-s3-cfr-1b.md item 1 (listed under "Moved" and in the Deliverables table as not
   delivered). ve/right_clauses.py only relays and binds (R8).
3. Tests can fail: PASS. Seeded bugs table, mutants.json (16 entries), trust-mutants.json (exit 0: 0 SURVIVOR,
   0 UNKNOWN).
4. Python and Lean agree: PASS. test_right_clauses_differential compares bytes with Lean's on K1-K15, F11, F12 and F14.
5. R8 binding: PASS. test_right_clauses_relay_binds_every_field drops, adds, renames and moves units, lines, names and
   premises, and checks the Lim ++ Rel order.
6. Gate evidence on the final HEAD: PASS for this builder's part. The selected tests ran on the committed tree, and the
   chain runs the full gate. Main's answers are saved in main-answers.json, not computed from live git.
7. No unsigned item: PASS. DELTA rows cite R2, R2, the DRI's signature (dri-decisions-20261031-spec-right-clauses.md
   item 2) and R16. No signature is reserved.
8. Every user-visible change is in DELTA: PASS. The two earlier refusals and the soft frame are rows. main-answers.json
   and main_answers_probe.py hold the base's answers. Profile-off texts are unchanged
   (test_right_clauses_profile_off_evidence, test_right_clauses_k10_profile_off).
9. Test selection: PASS. select_tests chose 514 units, not every unit, and test_right_clauses.py is among them.
10. Statements: PASS. `clauseSlot_wellFormed` matches spec 8.4 word for word (Spec re-read). lean/audit.py PASS. The K8
    mutant breaks its proof.
11. Limits fail closed: PASS. test_right_clauses_w1_budget: one atom over the limit gives `AST exceeds 10,000 nodes`;
    257 lines give `ResourceLimit: rules` (RunExamples.lean:183). No sleeps; waits use HANG_TIMEOUT.
12. No CPU regression: PASS. Line objects are counted before decoding, spans are O(s log s) and cites are one set.
    test_right_clauses_w1_budget runs 30,000 spans and 20,000 cites within the deadline, and the pairwise reference
    guard is Examples.lean:396. No pilot bytes move.
13. Test-removed trailers: PASS. `tools/gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed (no
    test removed).
14. Both directions, cited evidence, spec re-read: PASS. Each charge has an accepted side (`bodies [256]`, `scopes 63`,
    `deepIn ... == some false`) and a refused side. See the Spec re-read section.
15. Overclaim, silent cut, checks that can fail, limits before work: PASS. The RC rendering cut and the three moved route
    verdicts are DRI-ruled and listed (Deliverables, "Moved"; test_right_clauses_report_lists_every_moved_item). Every new
    #guard has a mutant that breaks it (mutants.json). `lineObjects` charges lines before `decodeClauseDoc`
    (Run.lean `elaborateCase`).
