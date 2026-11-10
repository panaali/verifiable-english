# cmp-s3-cfr-1b: the clauses-elaborate relay, 9.1/9.2 fixtures, W1's budget, `clauseSlot_wellFormed`

No DRI signature is reserved in this item. Branch feature/cmp-s3-cfr-1b. Plan: prompts/task-cmp-s3.txt deliverables
(1) (only `clauseSlot_wellFormed`), (3), (4), (5); docs/spec/right-clauses.md 8.4, 9.1-9.3, W1. Scope ruling:
reviews/dri-decisions-20261110-cmp-s3-cfr-1b.md (Q1: RC1-RC5 rendering moved; Q2: the proof stays, proof lines exempt
from the size line). Prerequisite cmp-s3-cfr-1 is on main (merge base, then main merged at the end).

## Deliverables

| Plan row | Delivered by | Test or #guard |
|---|---|---|
| (1) ve/right_clauses.py relays Lean's `clauses-elaborate` (decode, check and plain are Lean's; Python sends and binds, R8) | 4e3667a472 | tests/test_right_clauses.py::test_right_clauses_differential |
| (1) "render RC1-RC5" | not delivered, moved: RC1-RC4 to cmp-s3-cfr-1d, RC5 to cmp-s3-candrel (reviews/dri-decisions-20261110-cmp-s3-cfr-1b.md item 1; spec 2 shows each RC only through W7) | none |
| (1) byte for byte with Lean on K1-K15, F11, F12, F14 | 735cd7ed66 | test_right_clauses_differential (plained bytes and slot rows equal; refusals raise Lean's text as its class; K10, K11, K12, K14 texts pinned) |
| Schema and binding, fuzz that retypes and rebinds each field (R8) | 4e3667a472, 735cd7ed66 | test_right_clauses_relay_binds_every_field; tools/relay_mutation_gate.py --route service:clauses-elaborate: 528 mutants, 528 refused, 0 allowed (CFR1A/CFR1B allow rows dropped) |
| (2) 9.1 K2, K3, K10, K13 | Examples.lean (cmp-s3-cfr-1 sections K2, K3, K13; slot at layer 0 in this item's section), differential | K_FIXTURES, DIFFERENTIAL rows K2, K3, K10, K13 (K13: `Lim_D`'s premise before `Rel_D`'s) |
| (2) 9.2 F11-F14 (G8 waits for cmp-s3-candrel) | Examples.lean "cmp-s3-cfr-1b" section | #guards; F11, F12, F14 in the differential |
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
| Line charge | Run.lean `lineObjects` | count minus one | RunExamples.lean:152, :166 |
| Line charge dropped | Run.lean `elaborateCase` | check deleted | RunExamples.lean:162 |
| Depth charge | Run.lean `deepLine` | `≥` to `>` | RunExamples.lean:164 (`deep`) |
| Spans in O(s log s) | Plain.lean `checkSpans` | adjacent spans refused | Examples.lean:114, :396 (pairwise reference) |
| Cites by one set | Plain.lean `checkBody` | `u9…` accepted | Examples.lean:175, :176 |
| The differential | ve/right_clauses.py `bind` | plained re-serialised by Python | test_right_clauses_differential |
| Binding | ve/right_clauses.py `bind` | totality labels unchecked | test_right_clauses_relay_binds_every_field |
| Soft frame | ve/softnorms.py `check_soft_source` | profile kept | test_right_clauses_rights_environment_reads_the_profile |

## Trust (R16)

TRUST_PLACEHOLDER

## Size

Counted hand-written lines against the merge base (git diff --numstat): ve/right_clauses.py 120, ve/softnorms.py 5,
Plain.lean 34, Run.lean 17, Examples.lean 93, RunExamples.lean 30, lean/RIGHT-CLAUSES.md 7, tests 183, the relay gate
33 (20 of them deleted allow rows), and these three docs. Exempt (reviews/dri-decisions-20261110-cmp-s3-cfr-1b.md item 2):
Relation.lean 272 proof lines. Not counted: recorded fixtures (route-cases.jsonl 8, the b15b oracle) and checkers.lock.

## Overlaps

feature/cmp-s3a-cfr-3 also edits Examples.lean, Run.lean, RunExamples.lean and tests/test_right_clauses.py. This
item's lines sit in their own sections ("cmp-s3-cfr-1b"), except Run.lean's two checks in `elaborateCase`.

## Pilot bytes

None expected. This item adds a relay and refusals that come earlier. UDHR `elided_bytes` and the re-audit are
cmp-s3a-cfr-3's. Nothing is claimed before a pilot audit.

## Next items

cmp-s3-cfr-1d (RC1-RC4 rendering through W7), cmp-s3-candrel (G8, RC5, F13's set form), cmp-s3-cfr-1c (reading
candidates under the profile, K12's join).

## Tests run

TESTS_PLACEHOLDER
