# Composition stage S1: the measured rerun (section 11)

> 2026-10-02. The rerun 9.3 and 11 of [composition-s1.md](composition-s1.md) ask for, made with
> `tools/readings_s1_pilot.py` on the pilots' latest runs (`manage-agents/pilots/claude-constitution/run-20261002T0620Z`,
> `manage-agents/pilots/udhr/run-20260930T1800Z`). Every number below is the rerun's; none is predicted. The
> command:
>
> `uv run --frozen python tools/readings_s1_pilot.py --constitution <run> --udhr <run> --out <dir>`

## What the rerun builds

- **Constitution.** The run's main translation uses `norm-defaults@0`, which S1 abstains on beside content (1.1,
  13.7), and its force sets keep `content: null`. The rerun takes the run's all-default document (the soft chain,
  every force unit at its default rule), adds `readings@1`, and turns each strict/default force set of the main
  translation into an open set of two contents: the default rule, and its strict twin (1.7). For `u0125.s04.p2` and
  `u0156.s03` (F1) the run's all-strict document states the rule over another environment's predicate
  (`denial_of_being_claude_permitted`, `system_prompt_deception_permitted`, its norm-defaults form), which this
  document does not declare; the strict twin of the default rule is used, as F1 specifies the set.
  `force-u0073-s05` has a default reading only and is no pair. The modal and scope sets have no content and stay
  pending.
- **UDHR.** The run's translation with `readings@1`. The 19 right sets keep their candidates and drop their
  probe-free `models` (13.9); the four norm-candidate sets (`u017`, `u052`, `u112`, `u114`) take their companion
  documents' contents, and the companions' sorts and predicates join the document's vocabulary (4 sorts,
  4 predicates), since under S1 the candidate is a content of this document (F4). `rs_u054` is formula-only and
  keeps today's validation with its models.
- **Situations.** Python's search finds one per pair (10), from the pilots' recorded situation re-expressed as a
  base first (one element of each sort, every guard atom true, `guard_base`), then the search's own bases; Lean
  checks each when the document loads, Python regenerates Lean's answer byte for byte, and Rust replays every
  situation.

## Results

| | Constitution | UDHR |
|---|---|---|
| Single-attachment refusal (4.2) | none | none |
| Content-bearing sets admitted in the document | 7 of 7 | 23 of 23 |
| Pairs without a situation | 0 | 0 |
| `ResourceLimit` hits | 0 | 0 |
| Separations by probe form | outcome 7 | outcome 104 |
| Wordings (2.3) | E19 7 (no set records a source word, so no E14) | E19 104 |
| `SeparatedByDecisionOnly` (not certified) | 7: `u0036.s05`, `u0052.s01`, `u0078.s01`, `u0125.s04.p2`, `u0156.s03` (F1), `u0168.s01`, `u0263.s04.p2` | 0 |
| `SeparatedByActOnly` | 0 | 70 |
| Premise status | UNKNOWN, `superposition pending` (baseline: a model) | UNKNOWN, `superposition pending` (baseline: UNKNOWN, `non-assertion reading elaboration pending`) |
| Bytes by status | unchanged: CHECKED 22, OPEN 1,193, LABELLED 349, UNFORMALISED 183,329 | unchanged: CHECKED 57, OPEN 2,666, LABELLED 535, UNFORMALISED 7,658 |
| Search | 2.3 s | 6.9 s |
| Load (admission, Python's regeneration, Rust's replay) | 0.8 s | 141.7 s (against today's 85 s for 20 right sets, 10) |

Per named unit: every unit of the sets above is OPEN with its bytes unchanged (constitution: `u0036.s05` 68,
`u0052.s01` 78, `u0078.s01` 451, `u0125.s04.p2` 51, `u0156.s03` 100, `u0168.s01` 96, `u0263.s04.p2` 115; UDHR: the
19 right units, `u017` 65, `u052` 182, `u112` 121, `u114` 225, `u054` 45). S1 adds no status (4.8), which is what
the plan expects for the constitution and what the UDHR shows too.

## Against the baselines of section 11

- **UDHR, 43 units blocked on `force_variants_in_one_reading_set` (4,175 bytes, 38.2%).** Their recorded primary
  blocker is gone: S1 admits strict and default candidates of one rule in one set with one checked situation
  (`rs_u017` here, admitted with its situation). Their status is not: the run's translation records them as
  UNFORMALISED, and the rerun does not re-encode a unit; a pilot translation that writes them as force sets is the
  next step. Unchanged here: UNFORMALISED, 4,175 bytes. The same holds for the 4 units recorded as
  `right_lines_in_reading_sets` (393 bytes): S1 admits `right_lines` contents.
- **UDHR, the 4 companion sets.** Admitted in the document; the 593 bytes of companion documents are no longer
  needed for separation (F4). Their verdicts across readings are S2's.
- **Constitution, the 14 force sets** of the plan's ledger: this run's main translation has 8, of which 7 are
  strict/default pairs, all admitted with one situation each (F3's share: the stored situations re-expressed with
  the default reading as witness). The placeholder models and the separation computed outside the document check
  are no longer needed. No status changes, as the plan expected.
- **Decision-only findings** are reported and not certified (DRI ruling 2): `decision_only_sound` is unproved.
- **Load time.** The UDHR's 141.7 s is over the 85 s that 20 right sets cost today: each of 23 sets' candidates
  is elaborated in its own document by Lean and by Python, and every pair is replayed by Rust. It is measured,
  not assumed (10); reducing it is not part of S1.
