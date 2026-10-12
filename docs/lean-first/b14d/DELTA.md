# Batch 14d A/B delta

The nine-corpus comparison is in progress. This file will list every user-visible difference before the release gate. No verdict, availability, diagnostic, or field change is claimed as signed without a saved comparison and the applicable DRI ruling.

## Signed standing ruling

- **Trusted Lean budget:** SIGNED by standing ruling R6 (DRI-RULINGS.md). The trust baseline records a +338 line allowance: Lean's coupled choice enumeration, complete evidence check and verdict fold replace the Python decision sites deleted in this batch. Evidence: `tools/trust_map.py --check`, `test_complete_choice_verdict_is_lean_checked`, and the seeded faults in `evidence/mutants.json`.

## Pending DRI classification

- `x-reading-plan` is a request-binding relation extension in the generated response schema. It is listed in `docs/INTEGRATION-GAPS.md` and the architecture census's pending D1 set. The DRI owns its final placement in ADR 0001. This does not change a public answer.
