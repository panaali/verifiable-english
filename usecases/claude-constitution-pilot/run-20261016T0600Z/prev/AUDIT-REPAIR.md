# Audit repair, run 20261015T1800Z

Input: `AUDIT-20261015T0600Z-received.md` (20/20 sampled faithful plus 9/9 changed faithful, 29 units: u0001, u0002.heading, u0023, u0032.heading, u0052.s01, u0073.s05, u0083.heading, u0108, u0123.s01.p1, u0126, u0151.heading, u0156.s03, u0162.heading, u0165.s01 to s07, u0173.s01, u0207.heading, u0235.heading, u0238.heading, u0248, u0263.s04.p2, u0268.heading, u0286.heading, u0298). It marked no unit unfaithful or incomplete, so there is nothing to repair and no covered status is kept "only because repaired". `changed_units` is empty. The audit's wrapper said it could not write `AUDIT.md`; its text is kept verbatim as the `-received` file.

## Plan additions of this run (DRI SC2, AT2, AT3, ME1; X5; X2-X4)

| Plan item | State | What this run did |
|---|---|---|
| AT-0p (u0165.s01 to s07) | already in the plan's form (applied 20261014T1800Z; u0165.s03 per candidate since 20261015T0600Z; both audited faithful) | `repair_20261015T1800Z.py` asserts, on the three carried documents, that each of the six plain rules has guard `( C_i(s) and knowingly_engages_i(c, s) ) or thinks_quite_likely_i(c, s)` with c = var 1, s = var 0, that all attitude terms are binary on (claude_instance, situation), and that no unary `knowingly_<C>` / `thought_likely_<C>` term or unsplit u0165.s03 term remains anywhere. The four probe kinds were re-measured: all seven rules as the plan states. Listed in `plan_repairs` with `applied_in_this_run: false`; no unit changed. |
| SC-M0 (scope tally) | regenerated | 150 governors, 352 units, 55,294 bytes; identical to the previous run. Tags only. |
| AP-0 item 3 (act_workaround) | regenerated | 17 units, 2,502 bytes (M4 as measured by the plan); no act phrase changed since 20261012T1800Z, so no `act_workaround_stale`. The evidence file is cmp-identical to the one on `research/act-phrases-p1`. |
| DRI X5 (claimed) | applied | every covered unit is `claimed: true`; none is `claimed: false`. |
| DRI X2-X4 (1) sort `entity` noun | in place | the noun is “thing” (“things”), asserted. |
| DRI X2-X4 (2) vocabulary change | no vocabulary changed in this run | `nd.py all` was rerun at this tag anyway; its result is byte-identical to the previous translation; the one fenced block (u0248) parses unchanged; no unit differs. |
| DRI X2-X4 (3) Rust time limit | default `VE_RUST_TIMEOUT` kept except under `prlimit --as=6442450944` | three conclusion queries were unavailable at the default limit and ran under the cap with the limit at 600 s: u0165.s01 neither (peak resident set 114,812 kB) and u0165.s02 neither (112,652 kB); both answered UNKNOWN (not a verdict of absence: the search budget ended). |

Differences from the plan's expectations, reported not hidden: the plan's “46 open terms (measured on the 1800Z copy)” is 50 here, the 46 plus the exception terms of the three force sets and the per-candidate scope terms of u0165.s03 (later runs' additions, outside AT-0p); claimed bytes are 2,951 as expected; `ve document check` passes.

## Conflicts

VE reports none (CONFLICT-FREE in all 16 choices), so there is nothing to classify as a source conflict or a translation artefact.

## Audit-verified bytes

2,602 covered plus 349 label bytes (all 2,951 claimed bytes). Newly verified against the previous run's record: u0052.s01 and u0165.s03 (accepted by the 20261015T0600Z audit, translation byte-identical) and the label u0126. Nothing is dropped. These are verdicts on text unchanged since the audit; they are not a fresh audit of this run.
