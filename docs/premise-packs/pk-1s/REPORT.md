# pk-1s build report: PK-1 premise packs, statement spec

**No DRI signature is reserved or needed.** The item is docs only, with trust +0 and no DELTA rows.

- Branch `feature/pk-1s`, based on `main` at `802b8ff9b`.
- Commits: `9ffee5b7c` (the stub), `92104f3ef` (the spec, fixtures and seeded bugs), then this report.
- Next item: **pk-1**, the build (spec section 5).

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

All ten seeded bugs are in Lean, in the stub, the one file with Lean in this item. The product code is unchanged,
so `review-ready.py`'s product-language rule does not apply.

They were run by applying each one, type-checking the stub, recording the first error, and restoring the file. The
record is `docs/spec/premise-packs/mutants.json`, with `file` and `test` keys. Every mutant fails:

| Id | Mutation | First failure (stub line) |
|---|---|---|
| M1 | `packOrder` puts rights before soft | A1 `#guard` (403) |
| M2 | `firstRepeat` forgets seen keys | A3 `#guard` (413), 3 errors |
| M3 | assembly skips the environment check | A4 `#guard` (421) |
| M4 | `packFault` drops the legacy text | A7 `#guard` (447) |
| M5 | vocabulary limit off by one (`≥`) | `assemble_nil` proof (141), and the A6 boundary `#guard` |
| M6 | a repeated pack id is not refused | A2 `#guard` (410) |
| M7 | `extendEnv` lets the base shadow a generated name | `extendEnv_nil` proof (118), 4 errors |
| M8 | `xWithout` keeps dropped labels | `xWithout_nil` proof (280), and the A8 `#guard` |
| M9 | `elaborateArrays` writes soft again as a further entry | A9 `#guard` (459) |
| M10 | `packPremises` reads the first pack whatever its id | `packPremises_legacy` proof (194), 4 errors |

**A first M9 survived.** It removed `elaborateArrays`' legacy condition, and nothing failed. The condition turned
out to be dead code: a legacy list holds only soft and rights, so the further-pack list is empty anyway. It was
removed from the definition, and M9 now targets the filter.

## Tests

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
- **Size.** 951 changed lines, all documents (`git diff --stat main...HEAD`):
  - the type-checked stub, 468 lines: statements, real definitions and fixtures;
  - the spec, 323 lines;
  - mutants, 12 lines;
  - this report and DELTA, 148 lines.

  This is over the ~600 guide. The stub is the deliverable the task requires. The spec cites it instead of copying
  the Lean, which saves about 250 lines. A statement spec is not split mid-review, so no `pk-1sb` is named.

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
