# pk-1c-cfr-2: pk-1c's `#guard` fixtures and the identifier its theorem assumes (REPORT)

Summary: READY FOR REVIEW. pk-1c REPORT row (2c) now calls its checks "#guard fixtures (compiled evaluator)", not
kernel fixtures, and row (2b) names `VE.Bridge.identifier`, the check the theorem assumes, instead of "the route's
identifier check". Records and tests only: no `lean/` file, no generated file, trust +0, pilot bytes 0. No DELTA row,
no DRI signature reserved. Next item: none.

Source: DRI 2026-11-10 (reviews/dri-decisions-20261110-lp0001.md Q2, regrade #15) and
reviews/dri-decisions-20261110-adv0313.md item 2 (replaces pk-1c-r17-reword). Base 1ee886ca05 (main, after
pk-1c-cfr-1 merged); no plan gate.

## What the code does (checked on main 1ee886ca05)

- The checks behind row (2c) are `#guard` commands (`lean/VE/NormDefaults/PacksLegacyExamples.lean:131–141` hold
  six). `#guard` evaluates its Boolean in the compiled evaluator, not as a kernel proof.
- `legacy_labels_nodup_of_identifiers` (`lean/VE/NormDefaults/PacksLabels.lean:392`) assumes
  `hk : ∀ k ∈ VE.Rights.condKeys R, VE.Bridge.identifier k.2.1 = true`. `VE.Bridge.identifier`
  (`lean/VE/Bridge.lean:70`) is `s.utf8ByteSize ≤ 64 && Surface.identifier s`. The route's vocabulary decoder
  (`lean/VE/Route/Wire.lean:144` calls `VE.Bridge.checkVocabularyNames`, `lean/VE/Bridge.lean:86–93`) checks
  `name.length > 64` and `Surface.identifier name` on declared names. No lemma ties `condKeys` act keys to either.
  So the row says "when every act key passes `VE.Bridge.identifier`", the theorem's hypothesis.

## Deliverables

| # | Row | Delivered by |
|---|---|---|
| 1 | pk-1c REPORT :18, row (2c) | "kernel fixtures" becomes "#guard fixtures (compiled evaluator)". `grep -n -i kernel docs/premise-packs/pk-1c/*` on main found only this line; none other. In the same row, "whose act keys are route identifiers" becomes "whose act keys pass `VE.Bridge.identifier`", which is what the `#guard` at `PacksLegacyExamples.lean:134` checks (the pk-1c-cfr-1 review, F3, called that phrase part of the same overclaim) |
| 2 | `tests/test_pk1c_fixture_assurance_claim.py` | For every file in `docs/premise-packs/pk-1c/`, a line that says "kernel" must not name `#guard`/`#eval` nor cite a Lean line range (`X.lean:a–b`, resolved under `lean/`) holding a `#guard`/`#eval` command. It also pins the (2c) row's new wording. Opposite direction (`_refuses`): the base row and "The `#eval` checks are kernel-checked." are refused; "The theorem is checked by the kernel." is accepted |
| 3 | pk-1c REPORT :17, row (2b) | "when every act key passes the route's identifier check" becomes "when every act key passes `VE.Bridge.identifier`" |
| 4 | `tests/test_decoded_rights_labels_proof_claim.py` (on main, from pk-1c-cfr-1) | New `REPORT_OVERCLAIM` refuses "route's identifier check" and "act keys are route identifiers" on any pk-1c REPORT line; `_refuses` restores the old (2b) phrase and asserts the refusal |

Only rows (2b) and (2c) of pk-1c REPORT changed (`git diff main -- docs/premise-packs/pk-1c/REPORT.md`: 2 lines).
pk-1c `mutants.json` :8 still says "the route's identifier check": saved evidence of a run, left unchanged by the DRI
ruling for pk-1c-cfr-1 and not read by the refusal (it reads REPORT.md).

**Fails on main.** With main's `docs/premise-packs/pk-1c/REPORT.md` and the tests of this branch,
`uv run pytest -q tests/test_pk1c_fixture_assurance_claim.py tests/test_decoded_rights_labels_proof_claim.py` gave
`4 failed` (first failure: `REPORT.md:18 calls a #guard/#eval check a kernel check`). On HEAD: `4 passed`.

## Seeded bugs (each planted in the real file, run, restored)

| Id | File | Bug | Fails |
|---|---|---|---|
| S1 | `docs/premise-packs/pk-1c/REPORT.md` | row (2c) back to "kernel fixtures" | `test_pk1c_fixture_assurance_claim` (`['REPORT.md:18 … calls a #guard/#eval check a kernel check …'] == []`) |
| S2 | same | row (2b) back to "the route's identifier check" | `test_decoded_rights_labels_proof_claim` (1 failed) |
| S3 | same | row (2c) back to "whose act keys are route identifiers" | `test_decoded_rights_labels_proof_claim` (`['pk-1c REPOR…:131–141` \|'] == []`) |

Only docs and tests changed: no Lean, Python or Rust product code, so no product-code seeded bug is needed.

## Trust, size, lane

- No `lean/` file, no trusted definition: trust +0, no allowance, no FOLLOW-UPS row.
- `python3 -I …/tools-local/light-lane.py check`: `LIGHT 71 changed lines outside generated files <= 150 (3 files),
  no trusted-core file` (before this REPORT and DELTA). No trust_mutants sweep.
- Selection: `tools/select_tests.py --base 1ee886ca05` picks both tests (182/579 units); `--static --paths
  lean/VE/NormDefaults/PacksLegacyExamples.lean` picks both as well.
