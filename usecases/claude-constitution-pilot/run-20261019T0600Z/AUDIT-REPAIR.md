# Audit repair, run 20261019T0600Z

Input: `AUDIT-20261018T1800Z-received.md` (xhigh): **47 of 48 verdicts FAITHFUL** (20 sampled plus 28 changed units), one UNFAITHFUL (`u0042.presupposition`), plus small faults. No audited unit is `claimed: false`.

| Finding of that audit | Action |
|---|---|
| `u0042.presupposition` UNFAITHFUL: content exact (three pairwise different types, each Claude's, closure over Claude's types only, none named), but its English is the quoted fallback `Y1 is classified as "claude_principal_type"` | Repaired, not reverted. The planned wording "is one of Claude's types of principals" is refused by the lint, so Claude's types become the sort `principal_type` with the noun "principal type of Claude" (a noun "<noun> of Claude" is admitted; "instance of Claude" already is); the predicate `claude_principal_type` is removed with every trace (`repair_20261019T0600Z.py`). The English is now "There is a principal type of Claude named C1 such that … for every principal type of Claude named C4, at least one of the following holds: C4 is the same as C1; either C4 is the same as C2 or C4 is the same as C3, or both." CHECKED, 38 B, claimed; **not audit-verified** until re-audited. A sort named `claude_principal_type` was tried first and dropped (it collides with `claude_instance` in variable names) |
| `u0043.s02.p2`: faithful in content, same fallback English; "PS-0p's rule covers headings only, so the DRI decides" | Re-expressed the same way (75 B CHECKED), so it does not wait for the decision. Not audit-verified |
| Small fault: u0277 and u0294 have no trigger entry for their definite triggers | Entries added to `presupposition_triggers` ("The"; "the word"; carrier unresolved); both stay LABELLED headings |
| Small fault: u0235's `presupposed_claim` ("…a nature to discuss") exceeds its `pre` | Now "Claude has a nature." |
| Small fault: u0032's `presupposed_claim` ("…has criteria") exceeds its `pre` | Gone: the unit is now OPEN with content (PS-0p step 5), with `previous_presupposed_claim` kept |
| Accepted checks carried: PS-0p u0245 ("Claude is novel."), AT3 guards, AT4 records, the class-E notes, u0286/u0032/u0069/u0083 not claimed | Unchanged except u0286 and u0032, which are offered again (below) |
| Small faults carried from the audit of 20261018T0600Z: u0156.s03's frame term; u0168.s01's guard | Carried, not repaired: no plan of this run directs them (see `metrics.json`, `audit_rejected_units_and_repair_status`) |

**Audit-verified covered bytes: 2,628 plus 297 label bytes** (was 2,602 plus 349): the 1800Z audit's accepted units are counted where they are unchanged (u0245 and the others), and the units this run changed (u0042.presupposition, u0043.s02.p2, u0286, u0032, u0235, u0277, u0294) are not counted until a new audit sees them. **Claimed: 3,172 B.** Claimed but not audit-verified: 247 B.

## Plan additions of this run (DRI SC2, AT2, AT3, ME1; the merge of 2026-10-18; X2-X5)

The prompt repeats the sections of the 18:00Z run. They were applied then and are in the starting translation; this run re-checks them and changes only what the audit requires or what the premise check now allows.

| Plan item | State | What this run did |
|---|---|---|
| JT-0p (judgment terms, ledger only) | carried | `open_term_class` for the 56 classed terms (judgment 20, classification 15, attitude 16, exception 4, proportion 1); `genuine_helpfulness` is now a declared open term (class judgment, as in phase 1); `judgment_terms` on every unit; 507 units / 88,996 B; three units differ from phase 1, with reasons |
| QT-0p (quantities; u0042.presupposition, u0043.s02) | applied in 20261018T1800Z; re-expressed here | CHECKED 38 B + MIXED (15 B LABELLED, 75 B CHECKED); premises `model`; "Is there a fourth type of principal?" SETTLED no (ALL on the negation, with a certificate); the positive query is UNKNOWN (budget), as before. Deviation from the plan's content wording reported in `metrics.json` (`quantities_qt0p`) |
| PS-0p steps 1, 2 | carried | 10 titles without a claim, u0055 note, u0254 and u0268 notes |
| PS-0p step 3 | u0286 offered again | `open_problem` worded "{0} is unsolved"; "Some thing is unsolved."; CHECKED, +29 B; claimed only if the audit accepts it; u0013, u0095, u0002, u0235 not claimed |
| PS-0p step 4 | regenerated | `presupposition_triggers` on every unit (488 entries in 339 units; two added for u0277, u0294); blocker `other:presupposition` on the units whose carrier is unresolved |
| PS-0p step 5 (class B) | u0032 offered again | "{0} is helpful" with the open term `genuine_helpfulness`; "Some thing is helpful."; OPEN, +38 B; u0245 carried (+26 B, accepted by the last audit); u0069 and u0083 not offered (no admitted wording; waits for PS-6r) |
| PS-0p step 6 | regenerated | `presupposition-goals.json`: counts identical to the last run |
| PS-0p step 7 | done | loads; 32 choices CONFLICT-FREE; carried probes byte-identical (companion differs through the vocabulary) |
| AT-0p (u0165.s01-s07) | already in the plan's form | shape asserted; the four probe points per rule re-run and byte-identical; no guard or act phrase changed |
| SC-M0 scope tally | carried | `scope-tally.json`: 150 governors, 352 units, 55,294 B; no unit's span, id or text changed |
| AP-0 item 3 `act_workaround` | carried | M4 = 17 units, 2,502 B; every act phrase equals the evidence's |
| X5 (`claimed: false`) | none marked | claimed bytes = covered bytes = 3,172 |
| X2-X4 vocabulary | vocabulary changed | `nd.py all` rerun after the repair, after the PS-0p items and for the final document; `checkpoint.py` shows no existing predicate wording changed (the removal of `claude_principal_type` and the new noun of `principal_type` are the intended changes, allowed by name); every existing fenced unit parses to the same formula; the sort `entity` keeps the noun "thing"; Rust limit left at its default (no prlimit, no cap raised) |
