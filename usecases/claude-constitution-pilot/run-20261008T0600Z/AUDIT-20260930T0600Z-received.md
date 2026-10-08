**18 of the 20 sampled units are faithful.** I couldn't create `AUDIT.md` (the write was denied), so the audit is printed here. Read-only, no model calls.

**Sample:** `random.Random("20260930T0600Z").sample(pool, 20)` over the 55 CHECKED/LABELLED/OPEN/READINGS units in `units.json` order: 13 LABELLED, 6 READINGS, 1 OPEN. The only CHECKED unit (`u0248`) was not drawn.

**Re-run:** all three documents check with the recorded document ids. In the six sampled reading sets the strict and defeasible readings now differ, so last audit's collapse is repaired.

## Faithful (18)

- **LABELLED (13):** `u0023`, `u0126`, `u0265`, `u0294`, `u0298`, and the heading markers of `u0013`, `u0027`, `u0032`, `u0083`, `u0130`, `u0207`, `u0254`, `u0260`. Every label equals the source line.
- **READINGS (4):** `u0036.s05`, `u0168.s01`, `u0165.s01`, `u0165.s04`. Act, condition and the strict/defeasible pair match the source.
- **OPEN (1):** `u0073.s05`.

## Unfaithful (2), both weakened the same way

- **`u0165.s05`** ("Engage or assist in an attempt to kill or disempower…"). The required act is "avoid assisting an attempt on humanity". "Engage" survives only in the guard, so where Claude itself engages, the stated duty does not forbid it. The ledger note says the act phrase "abbreviates nothing"; `SELF-REVIEW.md` admits the gap, but disclosure does not restore dropped content.
- **`u0165.s06`** ("Engage or assist any individual or group with an attempt to seize…"). Same defect ("avoid assisting an attempt to seize control"), and not disclosed.

Fix for both: a neutral pointer, as `s03`, `s04` and `s07` already use ("avoid the undermining").

## Minor, not counted

- **`u0165.s01`:** "giving weapons uplift" is broader than the source act. It is harmless inside the guard, but not the neutral pointer the note claims.
- **`u0073.s05`:** the soft-norm English export drops the guard's list lines (the run patches them in) and does not parse back.
- **`u0126`:** keeps an `ethical_harm` tag on a heading recorded as having no content (ledger only).

## Three highest-value missing features

1. **An "unspecified" outcome, so prohibitions can be written as prohibitions.** The duty-to-avoid workaround forced by allow/deny produced the pointer act phrases behind both rejections. "Not required" is still an unstated completion in all 15 norm units.
2. **Norm reading candidates that hold their rules.** All 14 sets share one empty placeholder model, the cited narrowing of the hard constraints to strict has no effect, and the main document's premise status is UNKNOWN.
3. **Structured act clauses.** Acts need disjunction and qualifiers in the source's words, without the 80-character limit or the ban on "or". Next come norms inside attitude frames ("we want Claude to…"): roughly 175 of the 668 units blocked on norms.
