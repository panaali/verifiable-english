# Claude-side review of codex/e5 — VERDICT: changes-required
(materials are clean and honest as code; the experiments as drafted cannot yet answer their questions)

Checked: 189 tests pass; rendered prompts read for all 4 families x good/bad x cells a-e on dev; labels correct given only what
the judge sees; every flaw discoverable from the records in cell a; no audit strings/ids/condition names reach a prompt; badge
text matches the true checker status, including "proof not checked (Incomplete)" on controls.

## BLOCKING
1. Floor on the primary contrast. Haiku false approval is 0/12 in both cells a and b (pilot), outside the PREREG's own
   0.15-0.85 gate; b-a is unidentifiable. The instruction line ("Approve only if ... every cited leaf is supported ...") spells
   out the audit, and flaws are single-field JSON mismatches. Need harder items or a less directive instruction, then a re-pilot.
   [Orchestrator note: the E1 pilot shows the same thing: haiku false approval 1%, luna 5% on raw FOL. A judge ladder of small
   open-weight models is being set up; design items so difficulty is tunable: number of records, distractor records, flaw spread
   over two records, prose records instead of JSON fields, longer graphs.]
2. experiments/E5/materials.py:243 and :374. Cells c/d/e print `"scope_matches_target":false` for every scope-mismatch BAD item
   and no GOOD item (16/16 scored). Cell e prints `"binding_mismatch":true` for every merged-vocabulary BAD item and every
   unsupported-leaf BAD item (via the "not stated" sense). On those families c-b and e-d test whether the judge reads a flag.
   Cell e can show "a mechanical flag gets read"; it cannot show better comprehension or robustness to forged tags. The PREREG
   must say this, and stale evidence must be reported separately as the only unflagged family. Consider a forged-tag condition
   (attacker supplies matching sense tags on mismatched evidence) so that e can fail.
3. materials.py:305. The flawed leaf is always l1/r1 (32/32 dev, 64/64 scored) and the invalid edge is always the last rule
   (:110). Randomise positions.
4. E4 is at floor/ceiling in the pilot and has 2 scored invalid items, 1 template, 2 clusters. Minimum to be informative: >=12
   templates with quantifier or relational structure, >=60 invalid items, prose-arm false approval piloted into 20-60%.
5. E2. Checker-arm prompts are identical across sizes except `submitted_steps`; the direct arm's invalid step is the only line
   containing "and"/"r" (E2E4/materials.py:88); the four "families" differ only in registrar name because p/q/r are not renamed.
   The interaction is set by construction and the cluster bootstrap over 2 clusters is degenerate.

## NON-BLOCKING
- materials.py:269 as_of scope variant is ambiguous (record valid 04-01..04-30, scope date 04-19 vs target 04-18); affects
  fork2, chain5, parallel_chains, double_join.
- Only one control type (converse of the final rule).
- E2 structured_fol arm keeps records in VE syntax (:66): a small handicap for the baseline.
- Cell d repeats full records, so length is confounded with condition (PREREG acknowledges).
- Percentile bootstrap with 8 clusters under-covers.

## SCIENCE
- Extended leak audit: cells a,b at 0.50 for char 1-5, char 6-12, word 1-3 n-grams (train dev, test scored); record count,
  positions, dates, lengths exactly balanced within pairs. Cell e scores 0.59-0.75 and 1.0 with a rule on the flags above.
- Half of items are invalid-edge controls, so "approve iff badge" is 75% accurate: informative, not decisive, truthful.
- GOOD items carry an uncited anomalous decoy record, so they are not suspiciously clean.
- Power: with FA ~40%, ~20% discordant pairs, 8 BAD items per template and 8 clusters: SE 0.06, 95% half-width ~0.14, MDE at
  80% power ~0.17. A 5-point effect needs ~40 templates x 16 BAD items. Do not freeze a 5-point smallest effect against 8 clusters.
- E2 256-step derivations are genuinely replayed; tampering with a step or a certificate was caught.

## PILOT (sanity only; dev; haiku-4-5; tools disabled; 95 calls)
E5 primary: BAD approved 0/12 in a and 0/12 in b; GOOD approved 11/12 in both. Controls: 0/8 and 0/8.
E4: 12/12 correct in all arms. E2 direct arm: BAD rejected 12/12 at every size; GOOD approved 4/4 at sizes 4 and 32, 0/2 at 256
(1 reject, 1 unparseable): the size-256 cost shows up in honest acceptance, not false approval.
Files: /private/tmp/claude-501/-Users-seyran-code-verifiable-english/56a2e851-3525-4f60-895c-3cacd8e9ec22/scratchpad/e5/
