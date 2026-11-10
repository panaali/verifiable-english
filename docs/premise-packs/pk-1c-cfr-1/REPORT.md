# pk-1c-cfr-1: what `legacy_labels_nodup_of_identifiers` gives (REPORT)

Summary: READY FOR REVIEW. The docstring of `legacy_labels_nodup_of_identifiers` and the pk-1c REPORT row :82 now say
what the theorem gives: rights-label distinctness under the hypothesis `hk` that every act key passes
`VE.Bridge.identifier`, which the decoded route does not yet discharge (the decoder checks `Surface.identifier`).
`tests/test_decoded_rights_labels_proof_claim.py` holds it and fails on the base. Docstring, record and test only; no
definition, statement or proof changed; trust +0; pilot bytes 0. Seeded bugs S1-S5 each fail a named test. No DELTA
row, no DRI signature reserved. Next item: none.

Source: DRI 2026-11-10, reviews/dri-decisions-20261110-lp0001.md Q2, applying reviews/dri-decisions-20261109-lp1801.md
item 1 (regrade #14 in reviews/l1-c-regrade-norm-defaults-b-20261109.md, finding pk1c-F1; the DRI chose the reword,
not the proof). The plan is the code on main; base de7fb9469 (`git merge-base HEAD main`). No plan section or
statement gate applies.

## Deliverables

| # | Row (task) | Delivered by |
|---|---|---|
| 1 | The docstring says what the theorem gives, with no "discharge" claim; no statement or proof changes | `lean/VE/NormDefaults/PacksLabels.lean:390-391`: "Label distinctness under the hypothesis `hk` that every act key passes `VE.Bridge.identifier`. The decoded route does not yet discharge `hk`: no lemma ties decoded act keys to it; the decoder checks `Surface.identifier`." The docstring of `bridge_identifier_sep` (:278-279) carried the same claim ("applied to every declared predicate name ... discharges the act-key hypothesis ... on the decoded route") and is reworded the same way. Both stay two lines, so every `:NNN` citation in the pk-1c REPORT still holds |
| 1 | pk-1c REPORT :82 | `docs/premise-packs/pk-1c/REPORT.md:82`: "(labels distinct under the hypothesis `hk` that every act key passes `VE.Bridge.identifier`; the decoded route does not yet discharge `hk`: its decoder checks `Surface.identifier`)" replaces "(the route discharge)". No other line of that file changed (pk-1c-cfr-2 edits :18) |
| 2 | `test_decoded_rights_labels_proof_claim`: fails while the docstring or the pk-1c REPORT claims a discharge (or "route discharge") of the act-key hypothesis, unless a theorem in lean/VE/NormDefaults/ concludes it from a successful decode | `tests/test_decoded_rights_labels_proof_claim.py`. It refuses an affirmative `discharg…` word (negated ones, "does not yet discharge", excepted) in either docstring or in the :82 row, "route discharge" anywhere in the REPORT, and a discharge claim on a line naming "the decoded route"; it requires the docstring to name `VE.Bridge.identifier`, `Surface.identifier` and the hypothesis, and to say the route does not yet discharge it. The escape: a `theorem` in lean/VE/NormDefaults/ whose name or statement concludes from a successful decode (`decod…` in the name, or a `decod… = .ok` hypothesis) and is about act keys (`condKeys`, `Bridge.identifier` or `Nodup` in the statement, or `actKey`/`identifier`/`labels` in the name). Existing decode theorems (`decodeLayered_conditions`, `decodeSoftU_X_wellFormed`, ...) are about other facts and do not match: `test_decoded_rights_labels_proof_claim_refuses` asserts the escape list is empty on the tree, that the base docstring and the base row are each refused, and that a planted `decodeRights_actKeys_identifier` theorem lifts the refusal |

**Fails on the base.** Committed first (1bef2ac7a) on the unchanged tree: `uv run pytest -q --noconftest
tests/test_decoded_rights_labels_proof_claim.py` gave `1 failed, 1 passed`, the failure
`test_decoded_rights_labels_proof_claim`: `AssertionError: assert ['the `legacy...e discharge)'] == []`, "Left contains 6
more items", first "the `legacy_labels_nodup_of_identifiers` docstring claims a discharge: On the decoded route the act
keys are declared predicate names, which `VE.Bridge.identifier` admits; that discharges the act-key hypothesis." On
HEAD: `2 passed`.

**Left as is.** pk-1c REPORT :17, row (2b), says "`legacy_labels_nodup_of_identifiers` discharges `hk` from it: when
every act key passes the route's identifier check, the labels are distinct". That is a conditional statement about the
theorem (it discharges `legacy_labels_nodup_of_actKeys`'s `hk` from the `VE.Bridge.identifier` hypothesis), not a
claim that the decoded route discharges it, and the line is adjacent to pk-1c-cfr-2's :18, so editing it would
conflict; the task keeps this item's REPORT edit to :82. The test does not refuse it.

**Stays selected.** `uv run python tools/select_tests.py --paths lean/VE/NormDefaults/PacksLabels.lean
docs/premise-packs/pk-1c/REPORT.md --static --explain --no-record` lists
`tests/test_decoded_rights_labels_proof_claim.py: names docs/premise-packs/pk-1c/REPORT.md (static); names
lean/VE/NormDefaults/PacksLabels.lean (static)`.

## Seeded bugs

Each was planted on the committed tree, run with `uv run pytest -q --noconftest
tests/test_decoded_rights_labels_proof_claim.py`, seen to fail (`1 failed, 1 passed`), and restored with `git checkout`
(`2 passed` afterwards). "main" = `test_decoded_rights_labels_proof_claim`, "refuses" =
`test_decoded_rights_labels_proof_claim_refuses`.

| # | Lang | File | Bug | Fails |
|---|---|---|---|---|
| S1 | Lean | lean/VE/NormDefaults/PacksLabels.lean | the base docstring of `legacy_labels_nodup_of_identifiers` restored | main: `assert ['the `legacy... hypothesis.'] == []` |
| S2 | docs | docs/premise-packs/pk-1c/REPORT.md | the base :82 phrase "(the route discharge)" restored | main: `assert ['pk-1c REPOR...e discharge)'] == []` |
| S3 | Lean | lean/VE/NormDefaults/PacksLabels.lean | the base docstring of `bridge_identifier_sep` restored | main: `assert ['the `bridge...coded route.'] == []` |
| S4 | Lean | lean/VE/NormDefaults/PacksLabels.lean | "the decoder checks `Surface.identifier`" dropped from the docstring | main: `assert ['the `legacy... keys to it;'] == []` |
| S5 | Python | tests/test_decoded_rights_labels_proof_claim.py | the escape requires `from_decode or about_act_keys` instead of `and` | refuses: `assert False` |

S1 and S2 are the two the task names. The only product code changed is a Lean docstring; no Python or Rust product
code changed.

## Trust

Docstrings are not trusted lines. See "Checks" for `tools/trust_map.py --check`.

## Checks

TBD
