# pk-1c-cfr-1: what `legacy_labels_nodup_of_identifiers` gives (REPORT)

Summary: READY FOR REVIEW. The records now say what the theorem gives: rights-label distinctness under the hypothesis
`hk` that every act key passes `VE.Bridge.identifier`, which the decoded route does not yet discharge (the decoder
checks `Surface.identifier`). `tests/test_decoded_rights_labels_proof_claim.py` holds this and fails on the base.
Only docstrings, comments, records and a test changed; no definition, statement or proof; trust +0; pilot bytes 0.
No DELTA row, no DRI signature reserved. Next item: none.

Source: DRI 2026-11-10 (reviews/dri-decisions-20261110-lp0001.md Q2; regrade #14, pk1c-F1; the reword, not the
proof) and reviews/dri-decisions-20261110-pk-1c-cfr-1.md (scope ruling, below). Base de7fb9469; no plan gate.

## Deliverables

| # | Row | Delivered by |
|---|---|---|
| 1 | Docstring states the open `hk`; no discharge claim | `PacksLabels.lean:390-391` ("For well-formed `U` and `R` (`hw`, `hs`), label distinctness under the hypothesis `hk` that every act key passes `VE.Bridge.identifier`; the decoded route does not yet discharge `hk` (the decoder checks `Surface.identifier`)"). The same claim in the `bridge_identifier_sep` docstring (:278-279) and the "The rights labels" module doc (:210-212) is reworded too. Every block keeps its line count, so the `:NNN` citations still hold |
| 1 | pk-1c REPORT :82 | "(the route discharge)" becomes "(labels distinct under the hypothesis `hk` that every act key passes `VE.Bridge.identifier`; the decoded route does not yet discharge `hk`: its decoder checks `Surface.identifier`)". No other line changed |
| 1 | DRI scope ruling, item 1 | `PacksLegacyExamples.lean` comments only, line counts kept: :104-105 (the decoder checks predicate names with `Surface.identifier`, as `Bridge.checkVocabularyNames` does), :108-109, :127, :132, :137. No `#guard` changed. Paths: add `lean/VE/NormDefaults/PacksLegacyExamples.lean` |
| 2 | `test_decoded_rights_labels_proof_claim` | It reads both Lean files' comments (`/-- -/`, `/-! -/` and runs of `--` lines) and refuses five things: an affirmative `discharg…` word, the base wording from the examples file, a decoded-route/act-key/document clause that does not say the link is unproved, and "decoded route" without `` `Surface.identifier` ``. The docstring must name the hypothesis `hk`, `VE.Bridge.identifier` and `Surface.identifier` and say the route does not yet discharge it. The :82 row must say the same. Anywhere in the REPORT it refuses "route discharge" and any discharge claim on a decoded-route line. The escape is a `theorem` in lean/VE/NormDefaults/ with a `decod… = .ok` hypothesis whose statement names `condKeys` and `Bridge.identifier`. No current theorem matches (`decodeLayered_conditions` and the other decode theorems are about other facts). `_refuses` asserts that, refuses the base docstring, row and comment, and lifts the refusal for a planted decode theorem |

**Fails on the base.** First commit 1bef2ac7a: `uv run pytest -q --noconftest tests/test_decoded_rights_labels_proof_claim.py`
gave `1 failed, 1 passed`, with `test_decoded_rights_labels_proof_claim`: "the `legacy_labels_nodup_of_identifiers`
docstring claims a discharge: On the decoded route ... that discharges the act-key hypothesis." The final test also
fails on the base (seeded bugs S1, S2, S6 restore base text). HEAD: `2 passed`.

**Left as is (DRI scope ruling, items 2 and 3).**
- pk-1c REPORT :17, row (2b), "the route's identifier check": unchanged because it is next to pk-1c-cfr-2's :18
  edit. Filed by the DRI as pk-1c-r17-reword (C).
- pk-1c `mutants.json` :8, M2's "(discharges hk on the decoded route)": saved evidence of what was run, unchanged,
  and the test does not read it.

**No lemma (probe).** `grep -rn condKeys lean/VE` finds no decode lemma. The nearest is `decodeVocabulary_valid`
(`Route/Wire.lean:216`, `Surface.declarationName` for predicate names), which says nothing about act keys.

**Size.** 132 hand-written lines outside this directory (test 115, Lean 13, pk-1c REPORT 2) plus 73 in this
directory. That is over "tiny": the DRI ruling added a file and its checks, and three surviving seeded bugs (S5, S9,
S10) each needed a check.

## Seeded bugs

Each bug was planted, run with the command above, seen to fail, and restored (`2 passed`). The final test was rerun
against all of them. "main" is `test_decoded_rights_labels_proof_claim` and "refuses" is
`test_decoded_rights_labels_proof_claim_refuses`. S1 and S2 are the two bugs the task names. S1 and S2 also fail
"refuses", because its "base differs from tree" anchor fails.

| # | Lang | File | Bug | Fails |
|---|---|---|---|---|
| S1 | Lean | lean/VE/NormDefaults/PacksLabels.lean | base docstring of `legacy_labels_nodup_of_identifiers` | main |
| S2 | docs | docs/premise-packs/pk-1c/REPORT.md | base :82 "(the route discharge)" | main |
| S3 | Lean | lean/VE/NormDefaults/PacksLabels.lean | base docstring of `bridge_identifier_sep` | main |
| S4 | Lean | lean/VE/NormDefaults/PacksLabels.lean | "(the decoder checks `Surface.identifier`)" dropped | main |
| S5 | Lean | lean/VE/NormDefaults/PacksLabels.lean | module doc: "On the decoded route the act keys pass `VE.Bridge.identifier`" | main (survived twice; fixed by b31964657) |
| S6 | Lean | lean/VE/NormDefaults/PacksLegacyExamples.lean | base :127 comment ("no decoded document reaches this") | main |
| S7 | Python | tests/test_decoded_rights_labels_proof_claim.py | escape with `or "condKeys"` | refuses |
| S8 | Lean | lean/VE/NormDefaults/PacksLegacyExamples.lean | base :109 ("the decoded route ensures") | main |
| S9 | Python | tests/test_decoded_rights_labels_proof_claim.py | clause check disabled (`and False`) | refuses (survived; fixed by b5366c9af) |
| S10 | Python | tests/test_decoded_rights_labels_proof_claim.py | whole block in place of clauses | refuses (survived; fixed by 9cf57e7e2) |

The only product code changed is Lean docstrings and comments. No Python or Rust product code changed.

## Checks (final code)

- `uv run python tools/regen_generated.py --write` once (21fb218e9): code-map pages, `lean/declarations.txt` (module
  hashes only).
- `lake build` (1344 jobs) and `python3 lean/audit.py` (812 files, 9106 theorems): PASS.
- `uv run python tools/trust_map.py --check`: `K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0`, PASS.
- light-lane: NOT, only because PacksLabels.lean is unclassified. `trust_mutants.py --plan`: 0 definitions and 0
  mutants, so no sweep was run.
- `tools/gate_collection.py --check`: 2 added, 0 removed. `tests/test_premise_packs_stub.py`: 35 passed.
- Selection: `select_tests.py --static --explain` names the test for PacksLabels.lean, PacksLegacyExamples.lean and the pk-1c REPORT.
- Final selected run on committed 18ada1f12 (`MAC_PYTEST_NO_DEFER=1 mac-pytest.sh --select`): exit 0, 6 shards
  (run pk-1c-cfr-1-18ada1f1-t278514). No main-known-red test was touched.

## Follow-up

FOLLOW-UP: pk-1c-route-discharge prove decoded act keys pass VE.Bridge.identifier (closes legacy_labels_nodup_of_identifiers' hk)

(pk-1c-r17-reword, for pk-1c REPORT :17, was filed by the DRI's scope ruling.)

## Self-review against BUILDER-CHECKLIST

SELF-REVIEW: 2 A, 4 B, 3 C; fixed 9 (the A on PacksLegacyExamples.lean through the DRI scope ruling; the B on :17
and mutants.json are recorded as left, as that ruling decides).

1. Typed and bound relayed answers: N.A. (no relay).
2. Deliverables built: PASS (`test_decoded_rights_labels_proof_claim`).
3. Tests can fail: PASS (S1-S10, `test_decoded_rights_labels_proof_claim{,_refuses}`).
4. Python/Lean/Rust agree: N.A. (no behaviour change).
5. R8 binding: N.A.
6. Gate evidence matches HEAD: PASS (the selected run is on 18ada1f12; only this REPORT changed after it).
7. Nothing unsigned: PASS (DELTA has no row; no signature is reserved).
8. DELTA: PASS (no user-visible delta).
9. Selection: PASS (static selection names the test for all three files).
10. Lean says what is claimed: PASS (the point of the item; `test_decoded_rights_labels_proof_claim`).
11. Budgets fail closed: N.A.
12. No CPU or memory regression: N.A. (comments only).
13. No test removed: PASS (`gate_collection --check`: 0 removed).
14. Both directions: PASS (`_refuses` checks the refusal and the escape).
15. The four FIX classes: PASS (the probe for "no lemma" is cited; the test is selected; seeded bugs cover each claim).
