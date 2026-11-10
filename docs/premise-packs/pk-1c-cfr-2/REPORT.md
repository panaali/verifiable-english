# pk-1c-cfr-2: pk-1c's `#guard` fixtures and the identifier its theorem assumes (REPORT)

Summary: READY FOR REVIEW. No DRI signature reserved. pk-1c REPORT row (2c) now says "#guard fixtures (compiled
evaluator)", not kernel fixtures; row (2b) names `VE.Bridge.identifier`, the theorem's hypothesis, not "the route's
identifier check". Records and tests only: no `lean/` file, no generated file, trust +0, pilot bytes 0, no DELTA row.
Source: reviews/dri-decisions-20261110-lp0001.md Q2 (regrade #15) and reviews/dri-decisions-20261110-adv0313.md item
2 (replaces pk-1c-r17-reword). Base 1ee886ca05 (main, pk-1c-cfr-1 merged); no plan gate. Next item: none.

## What the code does (main 1ee886ca05)

- Row (2c) cites `lean/VE/NormDefaults/PacksLegacyExamples.lean:131–141`: six `#guard` commands, which evaluate in the
  compiled evaluator, not as kernel proofs.
- `legacy_labels_nodup_of_identifiers` (`PacksLabels.lean:392`) assumes `∀ k ∈ condKeys R, VE.Bridge.identifier
  k.2.1 = true`; `VE.Bridge.identifier` (`lean/VE/Bridge.lean:70`) is `s.utf8ByteSize ≤ 64 && Surface.identifier s`.
  The vocabulary decoder (`lean/VE/Route/Wire.lean:144` → `Bridge.checkVocabularyNames`, `Bridge.lean:86–93`) checks
  `name.length > 64` and `Surface.identifier` on declared names. No lemma ties `condKeys` act keys to either.

## Deliverables

| # | Row | Delivered by |
|---|---|---|
| 1 | pk-1c REPORT :18 (2c) | "kernel fixtures" → "#guard fixtures (compiled evaluator)". `grep -n -i kernel docs/premise-packs/pk-1c/*` on main: this line only; no other kernel claim. Same row: "whose act keys are route identifiers" → "whose act keys pass `VE.Bridge.identifier`", what the `#guard` at `PacksLegacyExamples.lean:134` checks (pk-1c-cfr-1 review F3 called the phrase part of the same overclaim) |
| 2 | `tests/test_pk1c_fixture_assurance_claim.py` | In every file of `docs/premise-packs/pk-1c/`, a line saying "kernel" (other than "not the kernel") must not name `#guard`/`#eval` nor cite (`[lean/…/]X.lean:a–b`, or a bare `:a` after one) a Lean range holding a `#guard`/`#eval`; a cite outside its file fails. Pins the new (2c) wording. `_refuses`: the base row, an `#eval` kernel claim and a `#guard` range cited by a bare `:134` are refused; a theorem cite (`PacksLabels.lean:392`) "checked by the kernel" and "… not the kernel" are accepted |
| 3 | pk-1c REPORT :17 (2b) | "when every act key passes the route's identifier check" → "when every act key passes `VE.Bridge.identifier`" |
| 4 | `tests/test_decoded_rights_labels_proof_claim.py` (on main) | `REPORT_OVERCLAIM` refuses "route's identifier check" and "act keys are route identifiers" on any pk-1c REPORT line, with its own message; `_refuses` restores each old phrase and asserts the refusal |

Only rows (2b) and (2c) changed in pk-1c REPORT (`git diff main -- docs/premise-packs/pk-1c/REPORT.md`: 2 lines).
pk-1c `mutants.json` :8 keeps "the route's identifier check": saved run evidence, left by the DRI ruling for
pk-1c-cfr-1; the refusal reads REPORT.md only.

**Fails on main.** main's pk-1c REPORT with this branch's tests: `uv run pytest -q tests/test_pk1c_fixture_assurance_claim.py
tests/test_decoded_rights_labels_proof_claim.py` → `4 failed` (`REPORT.md:18 calls a #guard/#eval check a kernel
check`). HEAD: `4 passed`.

## Seeded bugs (planted in the real file, same pytest command, restored)

| Id | File | Bug | Result |
|---|---|---|---|
| S1 | `docs/premise-packs/pk-1c/REPORT.md` | (2c) back to "kernel fixtures" | 2 failed: `test_pk1c_fixture_assurance_claim`, `…_refuses` |
| S2 | same | (2b) back to "the route's identifier check" | 2 failed: `test_decoded_rights_labels_proof_claim`, `…_refuses` |
| S3 | same | (2c) back to "whose act keys are route identifiers" | 2 failed: `test_decoded_rights_labels_proof_claim`, `…_refuses` |
| S4 | `tests/test_pk1c_fixture_assurance_claim.py` | `EVALUATED = re.compile("")` (every cited line counts as a `#guard`) | 1 failed: `test_pk1c_fixture_assurance_claim_refuses` |

No Lean, Python or Rust product code changed, so no product-code seeded bug applies.

## Checks

- `light-lane.py check`: `LIGHT 147 changed lines … <= 150 (5 files), no trusted-core file` before this REPORT's final
  form; the task's "under 80 hand-written lines" counts 86 outside this directory (2 REPORT, 14 + 70 test). No
  trust_mutants sweep, no `lean/` change (no lake build, audit or trust allowance).
- `uv run python tools/regen_generated.py --check`: exit 0 (38 entries). `select_tests.py --base 1ee886ca05`: 182/579
  units, both tests; `--static --paths …/PacksLegacyExamples.lean` also selects both.
- SELF-REVIEW: 0 A, 2 B, 8 C; fixed 8 (both B; C: (2c) refusal case, negated kernel, bare/full-path/out-of-range
  cites, message, seeded counts, lane figure). Not changed: none outstanding beyond the selected run below.

## Self-review against BUILDER-CHECKLIST

1 N.A. no relayed answer. 2 PASS deliverables 1–4 above; `test_pk1c_fixture_assurance_claim`. 3 PASS S1–S4.
4 N.A. no product code. 5 N.A. no binding. 6 PASS final selected run on committed HEAD (below). 7 PASS no DELTA row,
nothing reserved. 8 PASS DELTA.md: no user-visible delta. 9 PASS `select_tests.py` selects both tests. 10 N.A. no Lean.
11 N.A. no budget. 12 N.A. no runtime code. 13 N.A. no test removed or renamed (`git diff --numstat`: additions only
in tests). 14 PASS both directions in each `_refuses`; spec re-read: (2b) wording against `PacksLabels.lean:392` and
`Bridge.lean:70`; (2c) against `PacksLegacyExamples.lean:131–141`. 15 PASS no overclaim ("only", "none" each cite a
grep or diff above); no deliverable cut; every check has a seeded bug; no limits (N.A.).
