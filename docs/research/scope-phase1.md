# Cross-sentence scope: phase 1 (SC-M0)

> Status: phase 1 of [scope-PLAN.md](../spec/scope-PLAN.md) draft 4, 2026-10-13. Measurement only: no product code,
> no test, no generated file and no model call. The cross-plan synthesis (`manage-agents/debates/plan-synthesis/
> SYNTHESIS.md` 4.1, phase 1) lists one scope item for this phase, the pilot tally SC-M0. The script is
> [research/scope/sc_m0_tally.py](../../research/scope/sc_m0_tally.py); its outputs are in
> [evidence/scope/](evidence/scope/). Inputs are the pinned runs, read only:
> `manage-agents/pilots/claude-constitution/run-20261012T1800Z/units.json` with `source/claude-constitution.md`, and
> `manage-agents/pilots/udhr/run-20261012T1800Z/units.json` with `source/udhr.md`.

## 1. Pre-registration

This section was written and committed before the script existed and before any count below was taken. Before
writing it I had looked at the ledgers' field names, at the three constitution units that carry `scoped_by`, and at
one UDHR unit, to learn the schema; no count was taken.

### 1.1 The item and its bar, quoted from the plan

> ### SC-M0. Pilot tally (measurement; no product code; 1–2 h)
>
> - **Goal.** Make the need measurable. The ledgers record no `other:*` co-blocker, so scope phenomena are filed
>   under other tags (research 2.2).
> - **Work.** In the pilot prompts (`manage-agents/prompts/pilot-*.txt`, outside the repository), the next runs:
>   - tag `other:scope` as primary or co-blocker on every governor unit and governed unit;
>   - record `governed_by: [unit ids]` on governed units;
>   - write `scope-tally.json`: units and bytes by reach kind and effect, plus the 22 colon lead-ins and the 22
>     restrictive connectives of research 2.2.
> - **Moves.** A tally, not a coverage number.
> - **Shared files.** None in the repository.

**SC-M0 has no pre-registered pass bar.** Its outcome is the tally. What can be checked is whether the figures the
plan and the research already state, which the batches' byte claims rest on, are reproduced by a mechanical count
over the pinned ledgers. Those figures were fixed in commit `581d9c02` before this work began, so they are the
expected values below; none is chosen here. Every check is deterministic, so each passes only on **exact**
equality. A check that fails is reported as failed with the measured value; no expected value or definition below
changes after the run.

### 1.2 What runs now and what is deferred

- **Runs now:** a retrospective tally over the pinned runs, the same shape as the `scope-tally.json` the plan asks
  the next runs to write, with `governed_by` regenerated from layout. The layout is a Python transcription, in the
  scratch script only, of the item-1 spec's `VE.Layout.ofSource`, `listRun` and `itemRun` (spec 1.2 and 4.1),
  over each unit's span of the source's UTF-8 bytes, units in span order.
- **Deferred:** the prompt edits and the next runs' own tagging, which are model runs and edit files shared with
  the pilot pipeline outside the repository (section 4).

### 1.3 Definitions fixed before the run

- **Bytes** of a unit: `span[1] - span[0]`.
- **Layout fields** `item`, `midLine`, `lead`, `label`, `para`: spec 1.2, exactly.
- **Colon lead-in:** a unit with `lead` (its last byte that is not a space, tab, CR or LF is `:`).
- **Restrictive connective unit:** a unit whose text from its first non-space byte begins with one of `That said`,
  `However`, `At the same time`, `This doesn't mean`, `This doesn't imply`, `This does not mean`,
  `This does not imply`, `Nevertheless`, `Still` (the six cues of research 2.2; `doesn't` with either apostrophe,
  `'` or `’`).
- **This/These/Such unit:** text from its first non-space byte begins with the word `This`, `These` or `Such`.
- **Bullet unit:** `item ≠ none`.
- **Split heading title:** a unit whose id ends in `.presupposition`.
- **UDHR preamble unit:** a unit whose `article` field contains `Preamble` (case-insensitive).
- **Tag:** `missing_feature` is the primary tag; `other_blockers` the co-blockers.
- **A lead-in that moves now** (plan 1.3, the status rule for a governor without content): a colon lead-in whose
  `listRun` is `.ok` and every governed item has status CHECKED, OPEN or READINGS (an admitted rule status), and
  the lead-in itself is UNFORMALISED.

### 1.4 Reproduction checks and their expected values

Constitution (expected values from research 2.2, 2.3, 2.6 and plan 0, 5):

| Id | Check | Expected |
|---|---|---|
| C1 | status totals, units and bytes | CHECKED 2 / 73 B; LABELLED 39 / 349 B; OPEN 14 / 2,246 B; READINGS 3 / 283 B; UNFORMALISED 1,074 / 181,942 B |
| C2 | primary tag `other:discourse` | 81 units, 8,222 B |
| C3 | any `other:*` value among co-blockers, and any `other:scope` tag anywhere | 0 and 0 |
| C4 | colon lead-ins | 22 units, 1,352 B; of them 9 tagged `other:discourse` (506 B) and 13 not (846 B), the 13 tagged norms 6, quantities 3, and one each of defaults, counting, causation, attribution |
| C5 | restrictive connective units | 22 units, 4,196 B |
| C6 | This/These/Such units | 68 units, 10,981 B |
| C7 | bullet units | 141 |
| C8 | split heading titles | 29 units, 999 B; of them 14 tagged `other:discourse`, 437 B |
| C9 | named spans and statuses | u0164.s02 22 B UNFORMALISED; u0164.s01 68 B UNFORMALISED; u0173.s01 263 B UNFORMALISED; u0165.s01–s07 874 B, all OPEN; u0170.s01 108 B; u0046.s02 41 B; u0179.s03 63 B; u0047.s05 95 B and u0047.s06 209 B; u0062.s03 16 B; u0079 64 B; u0080.s01–s06 1,252 B; u0072.s02 84 B; u0073.s01 166 B; the u0073 block 2,475 B; u0138.s02 41 B; u0139.s01 50 B |
| C10 | distance from the end of u0165.s07 to the start of u0173.s01 | 4,949 B |
| C11 | spec 9 layout fixtures on the **full** pinned layout | F1: `listRun u0164.s02 = .ok [u0165.s01, …, u0165.s07]`; F1‴: u0166.s01 not an item and not in that run; L1: u0164.s02 `midLine` and `lead`, u0165.s01–s07 `item = some 0`; F2: `listRun u0181.s02 = .ok [u0182.s01, u0182.s02, u0182.s04]`; F2′: `listRun u0072.s02 = .ok [u0073.s01, u0073.s05, u0073.s08]`; F2″: `listRun u0164.s01` is `NotALeadIn`; F10: `itemRun u0073.s01 = .ok [u0073.s01, …, u0073.s04]` |
| C12 | lead-ins that move now (1.3) | exactly one, u0164.s02, 22 B, to OPEN (plan 0: SC-1b "+22 B OPEN") |

UDHR (research 2.4, plan SC-3a and SC-6):

| Id | Check | Expected |
|---|---|---|
| U1 | status totals | CHECKED 18 / 1,019 B; LABELLED 34 / 535 B; OPEN 21 / 1,870 B; READINGS 11 / 1,368 B; UNFORMALISED 46 / 6,124 B |
| U2 | units whose primary tag is `other:discourse` or names scope | 0 |
| U3 | named spans | u111 337 B READINGS; u112 121 B OPEN; u114 225 B READINGS; u052 182 B READINGS (865 B in all; u111 + u112 + u114 = 683 B); u019 251 B UNFORMALISED |
| U4 | preamble | 14 units, 2,004 B |
| U5 | F8's layout | u109 is the "## Article 29" heading and u110–u112 follow it before the next heading |

### 1.5 The tally (no bar)

`scope-tally.json`, per pilot:
- units and bytes by reach kind (`list`, `label`, heading candidates for `anchor`) and by the effect the plan
  assigns that reach (`frame` for a list; `title` or condition, undetermined by layout, for headings and labels),
  each split by status and primary tag;
- the colon lead-ins and the restrictive connective units, each with its id, bytes, status, tags and, for a
  lead-in, its regenerated run or its `NotALeadIn` refusal;
- `governed_by`: for every unit in a list run or a label's item units, the governor unit ids;
- the would-be `other:scope` tags: governor and governed units, by status and by the primary tag they carry today.

Headings are reported as candidates only: in VE an anchor is explicit in the discourse block, never inferred from
typography (research 1.1), and the pinned constitution translation has no discourse block.
`list_name`, `rules` and `frontier` reaches are not structural; the tally lists the cue units the plan names
(u0164.s01; "notwithstanding", "subject to"; the connective and This/These/Such units) and nothing more.
