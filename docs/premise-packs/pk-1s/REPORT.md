# pk-1s build report: PK-1 premise packs, statement spec

**No DRI signature is reserved or needed.** The item is docs only, with trust +0 and no DELTA rows.

- Branch `feature/pk-1s`, based on `main` at `802b8ff9b`.
- Commits: `9ffee5b7c` (the stub), `92104f3ef` (the spec, fixtures and seeded bugs), then this report.
  Fix round 1 (review `pk-1s-review.final.md`): `53a8a7464` (the stub), `d9c4e594e` (the spec), then this report.
- Next items: **pk-1**, the build, then **pk-1b**, the kind table (spec section 5).

## Fix round 1

| Finding | Class removed | Fix | Regression |
|---|---|---|---|
| F1 (B) `legacy_labels_nodup` false | A spec statement whose hypothesis does not see the data its conclusion reads | The hypothesis is the rights source's own `wf`, `WellFormedRights R` (`Rights/Wire.lean:270`). Spec 2.6 gives the true reason: `checkRights` refuses repeated limitation and condition names, and `limActs` is deduplicated. Both nodup statements now name the well-formedness their decoder's source carries | Fixture F1 (stub:497–512): the reviewer's counterexample and a repeated-condition one, on which `WellFormedSoft (correlate R)` and `WellFormedU` hold and the labels repeat, and both statements evaluated on five well-formed documents. The file check refuses the old hypothesis (M11) |
| F2a (B) import cycle and misplaced declarations | A build plan whose file placement contradicts the import graph | `planFiles` (stub:534) gives every stub declaration its pk-1 file. A `run_meta` check (stub:603) reads Lean's module graph and fails on a module outside a file's imports, a later file's declaration, an importer among a file's imports (a cycle), or a declaration with no file. Core `Packs.lean` sits below `Layered.lean` with `Layered.lean`'s own imports; `softPack`/`rightsPack` go into `Layered.lean`; the legacy theorems into `PacksLegacy.lean`; the transfers into `Readings/SupPacks.lean`. The per-file trust table is redone from the stub's measured lines | The check found one more misplacement while it was written (`packFault` needs `legacyIds`). M12–M16: the draft's cycle (`transfers_X` in the core), `legacyIds` and `softPack` misplaced, a cyclic import, an unplaced declaration |
| F2b (B) further-pack keys outside the closed shape | An output keyed on data the closed response shape does not constrain | `elaborateArrays` writes only `soft` and `rights` for every pack list; `elaborateArrays_keys` proves it by `rfl`, the fact `layeredCase_fits` needs. Further entries (`packEntry`, `furtherEntries`) land with the first provider's shape row. Fixture A9′ reads `layered_elaborate`'s closed keys from the shape itself. Sweep: no other pk-1 output depends on the packs beyond today's shapes (spec 2.7) | A9′ (stub:484–495); M17 fails `elaborateArrays_keys` and A9/A9′ |

The measured trust (spec 5) put pk-1 with the kind table at about +160, over R16's 150, so the cut the spec named is
made now: the kind table is **pk-1b**. C findings F3–F6 are not in this round. F5's section numbers were aligned
with the spec where the F2 edits touched them.

Probes: `PROBE F1` failed before the fix (`AssertionError`) and passes after it. As a permanent test it would regex
Lean text; its regression is the stub's own Lean check instead (M11). F2 has no probe. No pytest type-checks the
stub: a docs stub pinned to `main` at `802b8ff9b` goes stale when pk-1 lands, and batch evidence is checked at the
gate and merge, not by permanent tests (R11, D4). `mutants.py` is the rerunnable check.

## Statement gate

SYNTHESIS 2.1 is the converged cross-plan interface (Astra and Fable, round 3, 2026-10-13). It says PK-1 "needs its
own statement review" (SYNTHESIS 3, 4.1 item 2). This item writes that review's text, so the gate here is the
interface's convergence, which holds. The independent statement review of `docs/spec/premise-packs.md` follows this
item, and pk-1 waits for it.

## Plan rows delivered

| Task line | Where |
|---|---|
| Exact definitions and statements for `PackKind`, `Pack`, `packOrder`, `reservedPrefixes`, `assemble`, `assemble_order`, `assemble_fresh`, `assemble_wellFormed`, `assemble_legacy` (soft and soft+rights byte-identity) and `transfers_append`, adjusted to `main`, each in one plain-English sentence | spec 2.1–2.6 and 2.11; stub lines cited there |
| Cites of `Layered.lean`, `LayeredU`, `layeredElaborate`, `filledX` (file:line) | spec 1, 2.4–2.8 and 5 (`Layered.lean:51–53, 64–65, 72, 101, 120–121, 150–153, 283–291, 410–437, 444`) |
| The five provider obligations | spec 3 (`ExpandsOn` and `OriginsExact` are typed in the stub) |
| The diagnostics rule | spec 2.8 (`packFault`, with legacy theorems `packFault_legacy_*`; fixtures A7) |
| Kind-table rows | spec 2.10 (`KindRow`, `dispatch`, `dispatch_legacy`; the table of rows) |
| Acceptance fixtures | spec 4. Legacy L1/L2 are the corpus checks pk-1 adds. A2 is the repeated id, A3 the repeated label, A4 the clash with E or another pack, A5 the empty list; A1, A4′ and A6–A9 are extra. All are `#guard`s in the stub |
| Build plan for pk-1: files, shared-file hunks, seeded bugs, trust growth per file, R16 fit | spec 5 (about +107 trusted lines, K +0, fits R16; pk-1b named as the cut) |
| A type-checked stub under `docs/spec/premise-packs/` | `SpecStubs_pk1.lean`. It is checked from `lean/` with `lake env lean ../docs/spec/premise-packs/SpecStubs_pk1.lean`; the output is `sorry` warnings only, with no errors |
| JT-R2: the empty pack list | `assemble_nil` (proved), `envX_nil`, A5, `choiceLayeredG`'s norms chain in spec 5 |
| DF7: witness guarantee; collision witness without soft's coherence premises | spec 2.9 (`filledX_whole`, `xWithout`, `coherenceLabels`; A8) |
| DF4 and DF5 | kind rows after PK-1 (spec 2.10); `X_soft_first` (spec 2.6) |
| Trust +0 | `tools/trust_map.py --check` on `92104f3ef`: K +0, S +0, trusted +0, PASS |

## Deviations from SYNTHESIS 2.1

All of these are recorded in the spec. The review decides them.

1. **`assemble` takes the source `U` and `used`, not an environment `E`.** Freshness is checked against the
   complete environment of `fill U`, layer symbols included. `envAt (fill U) 0` hides them, so a generated name
   could equal a hidden layer symbol. The vocabulary limit counts pack names.
2. **`Pack` gains `consts`.** Events' named dates are constants (events.md:169, 366).
3. **`reservedPrefixes` is a table of `(owner, prefix)` rows, and on `main` it includes `rights__`.** The `rights__`
   prefix is reserved today (`Rights/Correlate.lean:230`). `attitudes__` and `date__` are added by their providers.
4. **Diagnostic shape.** New combinations read `InvalidModel(<pack>): the model violates a background premise:
   <label>`. Attitudes' plan, which puts the label inside the parentheses, must align.
5. **Legacy packs have no names and no origins.** Their names live in `U`, put there by `soften` and `correlate`.
6. **The vocabulary is not threaded into the checkers in pk-1.** Threading `envX` into situations, certificates and
   `BaseAdmissibleX` lands with the first vocabulary provider (AT-2). Until then no decoder builds a pack with names.
7. **`ExpandsOn` and `OriginsExact` land with AT-2.** R16 asks that every new trusted definition be exercised.
8. Requests not taken, with reasons: attitudes' point check, attitudes' duplicate kinds, weighing's joint size
   budget, events' namespace (spec 7).

A provider-plan sweep (attitudes, weighing, events, quantities, defeasible, judgment terms, act phrases on their
`research/*-p1` branches) found the facts behind 2, 3, 4 and 8.

## Seeded bugs

All seventeen seeded bugs are in Lean, in the stub, the one file with Lean in this item. The product code is unchanged,
so `review-ready.py`'s product-language rule does not apply.

`docs/spec/premise-packs/mutants.py` applies each one, type-checks the stub, records the first error with its
message, and restores the file. It writes `docs/spec/premise-packs/mutants.json`. Every mutant fails:

| Id | Mutation | First failure (stub line) |
|---|---|---|
| M1 | packOrder puts rights before soft | `417`, 1 error |
| M2 | firstRepeat forgets the keys it has seen | `427`, 3 errors |
| M3 | assembly skips the check against the environment | `435`, 2 errors |
| M4 | packFault drops the legacy text | `461`, 2 errors |
| M5 | the vocabulary limit is off by one | `142`, 2 errors |
| M6 | a repeated pack id is not refused | `424`, 1 error |
| M7 | extendEnv lets the base shadow a generated predicate | `119`, 4 errors |
| M8 | xWithout keeps only the dropped labels | `290`, 2 errors |
| M9 | furtherEntries writes the soft pack again as a further entry | `476`, 2 errors |
| M10 | packPremises reads the first pack whatever its id | `197`, 4 errors |
| M11 (F1) | legacy_labels_nodup assumes WellFormedSoft (correlate R) again | `603`, 1 error |
| M12 (F2a) | legacyIds placed in Layered.lean, above packFault's file | `603`, 1 error |
| M13 (F2a) | transfers_X placed in Packs.lean (the draft's import cycle) | `603`, 1 error |
| M14 (F2a) | softPack placed in Packs.lean, below softLabelledU's file | `603`, 1 error |
| M15 (F2a) | Packs.lean imports Layered.lean, which imports it | `603`, 1 error |
| M16 (F2a) | a stub declaration with no file in planFiles | `603`, 1 error |
| M17 (F2b) | elaborateArrays writes the further packs' entries in pk-1 | `232`, 5 errors |

**A first M9 survived** (first round). It removed `elaborateArrays`' legacy condition, and nothing failed. The condition turned
out to be dead code: a legacy list holds only soft and rights, so the further-pack list is empty anyway. It was
removed from the definition, and M9 now targets the filter.

## Tests

- Fix round 1, on `d9c4e594e` plus this report's uncommitted fix-round section: `zsh mac-pytest.sh --select --
  --base $(git merge-base HEAD main) --run` ran 12 of 434 units on ve-mac-1: exit 0, 0 failed or error ids, 231 s.
  `lake build` (973 jobs) and `python3 lean/audit.py` pass. The stub type-checks with 13 `sorry` warnings and no
  errors, and `mutants.py` reports 17 of 17 mutants failing.
- `zsh mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` on `92104f3e` (clean) ran on ve-mac-1:
  exit 0, 0 failed or error ids, 459 s.
- `select_tests.py` picks 11 of 434 units for this diff (layer 5, docs), not the whole suite.
- The full gate was not run by me, as instructed. The chain runs it on the final HEAD.
- Tests already red on `main` (`main-known-red.txt`: two `test_lean_service.py` sub-tick deadline cases and
  `test_readings_defaults_rd8_report.py::test_review_fix_commit_chain_and_final_gate_target`) are pre-existing. This
  item touches none of their files.

## Overlap and size

- **Overlap.** The hand-written files touched are `docs/spec/premise-packs.md`, `docs/spec/premise-packs/*` and
  `docs/premise-packs/pk-1s/*`. No branch in `lean-first/*`, `feature/*`, `infra/*` or `foundation/*` touches them
  (`git diff --name-only main...<branch>`). No branch touches pk-1's target files either: `Layered.lean`,
  `LayeredAdmission.lean`, `UnspecifiedWire.lean`, `SoftWire.lean`, `SoftDefaults.lean`.
- **Size.** 1,311 changed lines after fix round 1, all documents (`git diff --stat` against the merge base
  `802b8ff9b`):
  - the type-checked stub, 621 lines: statements, real definitions, fixtures and the file check;
  - the spec, 366 lines;
  - the seeded bugs, 145 lines (`mutants.py` 126, `mutants.json` 19);
  - this report and DELTA, 179 lines.

  This is over the ~600 guide. The stub is the deliverable the task requires, and the fix round's checks (F1's
  fixture, the file check) are in it. The spec cites it instead of copying the Lean. A statement spec is not split
  mid-review, so no `pk-1sb` is named.

## Pilot bytes

None directly: this is an enabler. PK-1 gates AT-2/AT-3a, WG-3, ET-4, QT-B2 and DF-1a. Through them it gates the
constitution's soft-norm path (69% of its bytes are norm-blocked) and UDHR's events and attitudes packs. Nothing is
claimed before a pilot audit.

## Self-review against BUILDER-CHECKLIST

1. Typed, contained Lean answers: N.A. No route, relay or response changes.
2. Every deliverable built, no rule broken: PASS. See the "Plan rows delivered" table. `git diff --name-only
   main...HEAD` shows docs only: no Python copy of a Lean decision, no report test, no file shared with in-flight
   branches.
3. Tests can fail: PASS. Seeded bugs M1–M10 each fail a `#guard` or a proof in `SpecStubs_pk1.lean`
   (`mutants.json`), and the first, surviving M9 led to removing dead code.
4. Py/Lean/Rust agree, valid inputs pass: N.A. There is no product code. The stub's positive fixtures A1, A4′, A5
   and A9 pass.
5. R8 binding: N.A. No relayed field. Origins binding is obligation 5, for providers.
6. Gate evidence matches the final HEAD: N.A. The chain runs the gate on the final HEAD. No saved evidence numbers
   besides `mutants.json`, which was regenerated on the final stub.
7. No unsigned item: PASS. DELTA.md has no rows and trust is +0 (`tools/trust_map.py --check`, PASS).
8. Every user-visible change in DELTA: PASS. There is none (DELTA.md), since the diff is docs only.
9. Test selection: PASS. `select_tests.py --base $(git merge-base HEAD main)` picks 11 of 434 units for docs/ changes,
   not every unit. No seeded product change is possible in a docs-only diff.
10. Lean statements say what is claimed: PASS. Proved statements break under the seeded edits: M5 (`assemble_nil`),
    M7 (`extendEnv_nil`), M8 (`xWithout_nil`), M10 (`packPremises_legacy`). The 13 `sorry` statements are listed in
    spec 6 for pk-1, which stops on a false one rather than adding a hypothesis. `tools/check_*_statements.py`: N.A.,
    no approved statement changes.
11. Budgets and limits fail closed: PASS for the stub's limit. A6 checks 255+2, 256 and 257, and M5 shows the
    boundary is tested. No runtime budget changes.
12. No CPU or memory regression: N.A. No product code.
13. `Test-removed` trailers: N.A. No test removed or renamed.
