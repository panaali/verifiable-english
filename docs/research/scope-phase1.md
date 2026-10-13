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

## 2. Results

Run on 2026-10-13 at commit `9a98c33f`: `python3 -I research/scope/sc_m0_tally.py manage-agents/pilots
docs/research/evidence/scope`. A second run into a fresh directory gave byte-identical outputs (same SHA-256 for
both files). The SHA-256 of each input is recorded in `scope-tally.json` (`inputs`). No `ve` run, no Lean build and
no model call was needed.

### 2.1 SC-M0 against its bar

| Item | Bar (plan, quoted in 1.1) | Result | Verdict |
|---|---|---|---|
| SC-M0, retrospective tally over the pinned runs | none: "A tally, not a coverage number" | `scope-tally.json` written for both pilots (2.3) | **DONE** (no bar to pass or fail) |
| SC-M0, prompt edits and the next runs' own tagging | none | not run: model runs and shared files outside the repository (4) | **DEFERRED** |

### 2.2 Reproduction checks (pre-registered in 1.4)

Expected values are those of 1.4, unchanged. Full values are in `evidence/scope/checks.json`.

| Id | Expected | Measured | Verdict |
|---|---|---|---|
| C1 | status totals of research 2.2 | identical | PASS |
| C2 | `other:discourse` 81 units, 8,222 B | 81, 8,222 B | PASS |
| C3 | 0 `other:*` co-blockers; 0 `other:scope` | 0; 0 | PASS |
| C4 | colon lead-ins 22 / 1,352 B; discourse 9 / 506 B; others 13 / 846 B | **23 / 1,600 B**; 9 / 506 B; **14 / 1,094 B** | **FAIL** |
| C4-tags | others: norms 6, quantities 3, one each of defaults, counting, causation, attribution | norms 6, quantities 3, **causation 2**, one each of defaults, counting, attribution | **FAIL** |
| C5 | restrictive connective units 22 / 4,196 B | 22 / 4,196 B | PASS |
| C6 | This/These/Such units 68 / 10,981 B | 68 / 10,981 B | PASS |
| C7 | bullet units 141 | **182** | **FAIL** |
| C8 | split titles 29 / 999 B; discourse 14 / 437 B | 29 / 999 B; 14 / 437 B | PASS |
| C9 | 17 named spans and statuses | 16 identical; **u0139.s01 is 49 B, not 50** | **FAIL** |
| C10 | u0165.s07 to u0173.s01: 4,949 B | 4,949 B | PASS |
| C11 | spec layout fixtures F1, F1‴, L1, F2, F2′, F2″, F10 on the full layout | all identical | PASS |
| C12 | exactly one lead-in moves now: u0164.s02, 22 B, to OPEN | exactly u0164.s02, 22 B, to OPEN | PASS |
| U1 | UDHR status totals | identical | PASS |
| U2 | no `other:discourse` or scope primary tag | 0 | PASS |
| U3 | u111 337 READINGS, u112 121 OPEN, u114 225 READINGS, u052 182 READINGS, u019 251 UNFORMALISED | identical | PASS |
| U4 | preamble 14 units / 2,004 B | **15 / 2,017 B** | **FAIL** |
| U5 | u109 "## Article 29", then u110–u112 before the next heading | identical | PASS |

15 of 20 pass. Why the five fail (the expected values stand; these are explanations, not re-scorings):
- **C4, C4-tags.** The extra lead-in is u0201.s03 (248 B, primary `causation`, "The challenge is that Claude faces
  specific epistemic constraints that ...:"). Its ":" lies beyond the ledger's 180-character excerpt, which the
  research counted; research 2.1 warned that excerpt-based counts are lower bounds. Counted over the source bytes,
  there are 23 colon lead-ins, 1,600 B, which matches the research's own cue count of "23 colon-ended paragraphs".
- **C7.** The spec's `item` counts every list marker: 141 `* ` bullets at depth 0, 37 `+ ` sub-bullets at depth 1
  and 4 numbered items. The research's 141 counted the `* ` lines only.
- **C9.** u0139.s01 ("* Education and the right to access information.\n") spans 49 B. A hand-summing slip.
- **U4.** The definition fixed in 1.3 includes the heading unit u002 "## Preamble" (13 B). Without it the preamble
  is 14 units, 2,004 B, as the research says.

None of the five touches a figure a batch claims: 22 B (SC-1b), 68 B and 263 B (SC-2), 874 B (fidelity), 683 B
(SC-6) and 4,196 B (SC-5's upper bound) are all reproduced exactly.

### 2.3 The tally

Constitution (184,893 B, 1,132 units). Reaches regenerated from layout; effects as the plan assigns them to each
reach.

| Reach | Effect | Governors | Governed units |
|---|---|---|---|
| `list` (colon lead-in with a list run) | `frame` | 23 units, 1,600 B, all UNFORMALISED | 138 units, 19,374 B: 8 OPEN (1,108 B: u0165.s01–s07 and u0073.s05), 130 UNFORMALISED |
| `list`, refused (`NotALeadIn`) | none | 0: every colon lead-in in the source is followed by a list item | — |
| `label` (bold-label item) | title or condition: not decided by layout | 42 units, 8,651 B (1 OPEN: u0073.s05) | 37 more units, 6,982 B, all UNFORMALISED |
| `anchor` candidate, heading that is a When/If clause | condition (SC-3b) | 0 | 0 |
| `anchor` candidate, any other heading | `title` | 39 heading units, 349 B, all LABELLED | none (a title changes nothing) |
| `frontier` candidate (restrictive connective) | not decided (SC-E1) | 22 units, 4,196 B, all UNFORMALISED; 20 carry co-blockers | not computed (SC-E1) |
| `list_name`, `rules` | — | not structural: u0164.s01 (list name, from the plan); "subject to" in 4 units, none a precedence wording ("less subject to honesty norms", "subject to the constraint that", "subject to meaningful checks", "subject to ongoing inquiry"); "notwithstanding" in none | — |

- The 23 lead-ins carry primary tags discourse 9 (506 B), norms 6 (429 B), quantities 3, causation 2, and one
  each of attribution, counting and defaults. Only u0164.s02's run is wholly admitted (7 OPEN). u0072.s02's run
  has one OPEN item of three; every other run is wholly UNFORMALISED.
- The 130 UNFORMALISED list items are blocked by their own content: primary tags quantities 30, norms 29,
  discourse 29, causation 18, defaults 15, counting 9.
- **Would-be `other:scope` tags** under the prompt rule of SC-M0 (governors: lead-ins with a run, labels,
  headings, restrictive connective units; governed: list items, label item units): 260 units, 32,608 B (17.6% of
  the bytes); 126 governor units, 175 governed units (the `governed_by` map). Of them, 49 units (5,019 B) are
  UNFORMALISED with no co-blocker today, so `other:scope` would be their only recorded co-blocker.
- **A hand-recorded scope the plan does not list.** Three OPEN permission units, u0062.s01, u0123.s01.p1 and
  u0123.s02.p1 (613 B), carry `scoped_by` with `scoped_by_source: u0123.s03`. The translator copied the six limits
  of u0123.s03 ("Operators cannot instruct Claude to ...", 351 B, OPEN, with its own six rules) into each
  permission as six open terms, its exceptions. u0062.s01 ends 38,929 B before u0123.s03 begins. This is the
  copy pattern of research 2.3 a second time, with a governor that has its own content and a reach over named
  rules. The audit sampled u0123.s01.p1 and found it FAITHFUL, so it is a duplication, not a fidelity failure.

UDHR (10,916 B, 130 units): no colon lead-in, no bold label, no restrictive connective unit and no
This/These/Such unit; 32 heading units (495 B, all LABELLED, all titles). The only scope on the UDHR is SC-6's
rights reach (U3).

## 3. Consequences for draft 2

Confirmed:
- **SC-1b's "+22 B OPEN"** (C12). On the pinned constitution exactly one lead-in can move, u0164.s02, to OPEN.
  No other lead-in has a wholly admitted run, so draft 2 should state that SC-1b's number is 22 B and no more.
- **SC-1a's layout and fixtures** (C11). `listRun` and `itemRun` as the spec writes them reproduce every pilot
  fixture on the full 1,132-unit layout, not only on excerpts, and refuse no colon lead-in of the source. The B1
  benchmark input is the same layout.
- **SC-2's 68 B and 263 B, the 874 B of fidelity, and SC-6's 683 B** (C9, U3) as stated.
- **SC-3b and SC-4 at 0 B on the pinned runs.** No heading in either source is a When/If clause; no unit uses
  "notwithstanding" or a precedence "subject to".
- **SC-5's upper bound of 4,196 B and SC-E1's corpus** (C5). The 22 restrictive-connective units are listed by id
  in `scope-tally.json` (`restrictive_connectives.rows`); draft 2 can cite that list as the frozen part of SC-E1's
  corpus. 20 of the 22 carry co-blockers, which supports "most are co-blocked".

Changed (wording and figures; no batch changes):
- **Colon lead-ins: 23 units, 1,600 B, not 22 and 1,352 B** (C4). Plan 1.2's and research 5.1's "up to 1,352 B of
  lead-ins travelling with their items" becomes "up to 1,600 B"; research 2.2's split becomes discourse 9 (506 B)
  and 14 others (1,094 B), causation 2. The SC-M0 bullet "the 22 colon lead-ins" becomes "the 23".
- **Bullet units: say which count.** 141 `* ` bullets; 182 units with a list marker by the spec's `item` (C7).
- **u0139.s01 is 49 B** (research 2.6 row 11); **the UDHR preamble is 14 units, 2,004 B without its heading**
  (research 2.4).

Added:
- **u0123.s03 as a representative sentence and a candidate fixture.** It is a later sentence whose limits
  constrain three earlier permissions by name, written today as six open terms copied into each. It moves no
  bytes (all four units are OPEN), but it is a one-owner target. Its reading has to be settled before it is a
  fixture: either a `carve-out` over a `rules` reach (SC-2's effect with SC-4's reach) or a `yields` edge
  (permission under prohibition, W1 precedence, SC-4), and the two differ only where W1's same-predicate rule
  applies. Draft 2 should add it to research 2.6 and leave the choice to SC-4's spec. The existing `scoped_by` /
  `scoped_by_source` fields are a precedent for `governed_by`; the prompt addition keeps them and adds
  `governed_by` beside them rather than a second record.

Cancelled: none.

## 4. Deferred

| Item | Why |
|---|---|
| Editing `manage-agents/prompts/pilot-*.txt` to add the SC-M0 tagging | The prompts are shared pipeline files outside the repository, and the brief keeps this branch to the repository. The text to add is drafted in `evidence/scope/pilot-prompt-addition.md` for the orchestrator. The newest prompt (`pilot-20261013T0600Z.txt`) does not mention `other:scope`, `governed_by` or `scope-tally.json`. |
| The next runs' own `other:scope` tags, `governed_by` and `scope-tally.json` | Each pilot run is a model run. Once one has run, `sc_m0_tally.py` gives the structural reaches to compare its `governed_by` with. |
| SC-E1 (deictic reaches) | Not a phase-1 item. Its bars 1, 2 and 4 need the Sonnet human-proxy annotation (a model call), and it runs after SC-4. Its frontier computation (bar 3) was not run here, so that bar stays blind. |
| SC-E2 (presentation) | Not a phase-1 item. It needs SC-1c's presentation and SC-2, and the Sonnet proxy. |
