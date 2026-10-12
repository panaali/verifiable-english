# Batch 14d A/B delta

The nine-corpus comparison is in progress. This file will list every user-visible difference before the release gate. No verdict, availability, diagnostic, or field change is claimed as signed without a saved comparison and the applicable DRI ruling.

The A/B recorder gives each side a distinct temporary pilot directory. Its comparator now substitutes a stable marker for that directory alone; `test_pilot_comparison_normalizes_only_its_own_scratch_directory` confirms that the rest of a diagnostic remains exact. This changes gate evidence only, not a product answer. Under the loaded host's default five-second Rust wall timeout, 20 head pilot records were unavailable. A matched base/head pilot rerun with `VE_RUST_TIMEOUT=60` is in progress; the current one-sided 600-second timeout on the large constitution translation remains unresolved and is not claimed as signed.

## Signed standing ruling

- **Trusted Lean budget:** SIGNED by standing ruling R6 (DRI-RULINGS.md). The trust baseline records a +338 line allowance for Lean's coupled choice enumeration, complete evidence check and verdict fold, plus +3 lines for rejecting a duplicate set identity. These checks replace the Python decision sites deleted in this batch. Evidence: `tools/trust_map.py --check`, `test_complete_choice_verdict_is_lean_checked`, `test_coupled_plan_refuses_duplicate_set_version`, and the seeded faults in `evidence/mutants.json`.

## Pending DRI classification

- `x-reading-plan` is a request-binding relation extension in the generated response schema. It is listed in `docs/INTEGRATION-GAPS.md` and the architecture census's pending D1 set. The DRI owns its final placement in ADR 0001. This does not change a public answer.
