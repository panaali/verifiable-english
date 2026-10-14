# Presupposition: phase 1 (PS-0p)

> Status: phase 1 of [presupposition-PLAN.md](../spec/presupposition-PLAN.md) draft 3, 2026-10-14. Measurement only:
> no product code, no test, no generated file and no model call. The cross-plan synthesis
> (`manage-agents/debates/plan-synthesis/SYNTHESIS.md` 4.1, phase 1: "Now, no product code") lists pilots and
> experiments; for this plan that is PS-0p (plan 6, order item 1). PS-E1 and PS-E2 are experiments with model calls and
> run later, separately. The task names `manage-agents/debates/plan-synthesis/edits-presupposition.md`; that file does
> not exist (the directory has `edits-<name>.md` for the seven wave-1 plans only, and SYNTHESIS 6 lists no presupposition
> row, since presupposition is a wave-2 plan). The DRI's wave-2 rulings for this plan are
> `DRI-DECISIONS-PHASE2.md`, "Presupposition (wave 2)": PS-C9, PS-NF, PS-8; none of them changes PS-0p.
>
> Inputs are the pinned runs the plan names (plan 5.2, R 2.1), read only:
> `manage-agents/pilots/claude-constitution/run-20261012T1800Z/` (`units.json`, `translation.ve.md`, `probes/`,
> `readings/`) with `source/claude-constitution.md`, and `manage-agents/pilots/udhr/run-20261012T1800Z/units.json`
> with `source/udhr.md`. Scripts are in [research/presupposition/](../../research/presupposition/); outputs in
> [evidence/presupposition/](evidence/presupposition/).

## 1. Pre-registration

This section was written and committed before any script existed and before any count below was taken. Before
writing it I had read the plan, the research note and the spec's headers, looked at the constitution ledger's field
names and at four units (`u0013.presupposition`, `u0040.presupposition`, `u0156.s03`, `u0248`) and at how the
translation writes its one fenced English claim (`u0248`), to learn the schema. No count was taken.

### 1.1 The item and its bar, quoted from the plan

> ### PS-0p. Heading presuppositions in the pilot (pilot, no product code; 2–3 h)
>
> - **Goal.**
>   - Claim the heading presuppositions that a word triggers and that nothing else blocks.
>   - Stop recording claims no word triggers.
>   - Stop assuming what the text withholds.
>   - Tag triggers as co-blockers.
>   - Count the distinct projected goals, so that PS-3's benefit is known before it is built (Risk 7).
> - **Depends on.** Nothing. It is delivered as additions to the DRI-merged pilot prompts
>   (`manage-agents/prompts/pilot-additions.txt` and `pilot-audit-additions.txt`; `DRI-DECISIONS-PHASE2.md`, SC2). The
>   UDHR has no heading presuppositions, so it gets no addition. It touches no repository file.
>   [...]
> - **Steps.**
>   1. **Ledger.** Add `presupposition_triggers` to every unit (2.1). This is the measurement of R 2.3 made exact over
>      whole units; the excerpts gave only lower bounds.
>   2. **Class E** (11 headings, 349 B, R 2.2). Remove `presupposed_claim` and note "no trigger word: a title (scope
>      SC-3a)". The status stays UNFORMALISED; scope claims the titles.
>   3. **Class A.** Each `.presupposition` span becomes `kind: asserted`, `support: assumption`, `meaning: specified`,
>      with fenced VE English content, English round trip, and the ledger fields `carrier: assumed`, `trigger`,
>      `trigger_words`.
>      - **u0013:** `core_value_of(entity, entity)`, "{0} is a core value of {1}"; "Some entity is a core value of
>        Claude."
>      - **u0095:** `guideline_of`; "Some entity is a guideline of Anthropic."
>      - **u0286:** `open_problem(entity)`; "Some entity is an open problem."
>      - **u0002 and u0235:** uniqueness, written as "Some entity is a mission of Anthropic, and every entity that is a
>        mission of Anthropic is that entity." if the parser admits it. Otherwise these two stay UNFORMALISED with the
>        note "uniqueness not writable (PS-6)".
>   4. **Class D** (u0254, u0268). Replace `presupposed_claim` with the note "the text withholds this (u0269.s02): not
>      assumed". The status is unchanged.
>   5. **Class B** (u0069, u0083, u0245, u0032; 149 B). Offer each to the audit as a separate item, in step 3's form
>      (u0032 is OPEN, with `genuine_helpfulness`). Each is claimed only if the audit accepts it.
>   6. **Check.** `ve document check` on the translation: it loads, the reading-set choices stay conflict-free (8 of 8
>      today), and the carried probes are byte-identical.
>   7. **Distinct goals.** From step 1's ledger, count the trigger occurrences in rule acts and the distinct goals they
>      project, as `(row, restriction, rule guard and carve-outs)` up to the unit's variable names. Report the count
>      for "the user" and "the operator" separately (the 68 units of 1.6), and how many share identical applicability.
>      This is a count from the ledger, not a Lean computation; PS-3 reads it.
> - **Audit additions.**
>   - For each heading presupposition claimed: the trigger word is in the title.
>   - The content is exactly the existence (for a singular description, existence and uniqueness) of what the trigger
>     names, and nothing more: no "is desired", "is relevant" or "must". [...] Until then the audit applies the same
>     test by hand.
>   - The source does not withhold it elsewhere: search for "whether" or "uncertain" with the noun.
> - **Bar.** The next audit samples every claimed heading unit and accepts each. A rejected unit reverts to
>   UNFORMALISED and nothing is claimed for it.
> - **Bytes.** **+89 B** (u0013, u0095, u0286), +145 B with u0002 and u0235, stretch +294 B with class B. All are
>   estimates until audited. UDHR: 0.
> - **Deleted.** 11 invented `presupposed_claim` fields.
> - **Seeded bug.** None: no product code.

**PS-0p has one pre-registered bar: the next audit's acceptance of every claimed heading unit.** That audit is a
model run of the pilot pipeline after the DRI merges the prompt addition, so the bar itself is **DEFERRED** here
(section 1.2). What runs now is a dry run of steps 1 to 7 on a scratch copy of the pinned run, and the plan's own
mechanical conditions for the bar: the three audit additions applied by script, and step 6's check. Each is
compared below with an expected value fixed now, from the plan and the research note at commit `2db7c4c8`. Every
check is deterministic, so each passes only on the stated relation (equality unless "≥" is written). A failed check
is reported as failed with the measured value; no expected value or definition below changes after the run.

### 1.2 What runs now and what is deferred

- **Runs now (no model call, no product code):**
  - D1, the word-level part of step 1's ledger: `presupposition_triggers` entries (`words`, `class`, byte span) for
    every unit of both pilots, from each unit's whole span of the source (the constitution ledger's excerpts stop at
    180 characters; the source does not). The fields `pre` and `carrier` of an UNFORMALISED unit are the
    translator's claim (plan 9, Risk 1) and are left to the next pilot run.
  - D2, the heading classification of R 2.2 (classes A to E), by a fixed trigger lexicon.
  - D3, the audit additions applied by script to the claimable heading units.
  - D4, a dry run of steps 2 to 4 and step 6: a scratch copy of the pinned translation with class A's units turned
    into fenced assumptions, checked by `ve document check` and the readings and probe comparisons below, against
    the pinned translation checked by the same binary.
  - D5, step 7's count, as far as the pinned ledger fills it.
- **Deferred:** the bar (the next audit), the prompt edits themselves (the DRI merges them: SC2), the translator's
  `pre`/`carrier` fields and `other_blockers: presupposition` on unformalised units, and class B's audit items. Each
  needs the next pilot run or its audit, which are model runs. Section 4 lists them.

### 1.3 Definitions fixed before the run

- **Bytes** of a unit: `span[1] - span[0]`. A unit's **text**: the source's UTF-8 bytes in its span, decoded.
- **Heading presupposition unit:** a unit whose id ends in `.presupposition`. Its **title** is its text.
- **Apostrophe:** `’` or `'` everywhere below.
- **Trigger lexicon for titles (D2).** A title has a trigger word iff, case-insensitively, it contains one of: a
  possessive `\w+(’s|'s)\b`; a possessive determiner `our|its|their|his|her|my|your`; `we|us`; the article `the`; a
  wh-word `what|why|how|who|which` at the title's start; `existing`; `other`; `as` (predicative); a factive stem
  (below); a numeral word `one`…`ten` or digits. Superlatives are not listed separately. Matching is on whole words.
- **Heading classes (R 2.2), fixed lists:** A = u0013, u0095, u0286, u0002, u0235; B = u0069, u0083, u0245, u0032;
  C = u0008, u0238, u0219, u0027, u0042, u0130, u0143; D = u0254, u0268; E = u0040, u0055, u0075, u0151, u0162,
  u0174, u0195, u0207, u0212, u0257, u0260 (each `.presupposition`).
- **Factive stems:** `reali[sz]\w*`, `recogni[sz]\w*`, `aware (that|of)`, `know(s|n)? that`, `knew that`,
  `acknowledg\w*`, `notic\w*`, `discover\w*`, `regret\w*`, `forg[eo]t\w*`, `learn(s|ed|t)? that`.
- **In-sentence trigger groups (D1), regular expressions over the text, case-insensitive unless stated:**
  - G1 role definite: `\bthe (user|operator)s?\b`.
  - G2 role or pronoun possessive over an object that may be missing (R 2.3's note):
    `\b(the (user|operator|principal)(’s|'s)|its|their)\s+(system prompt|instructions?|requests?|message|claims?|content|goals?|context|wishes|interests?|failure|right)\b`.
  - G3 change of state, continuation or iteration: `\b(stop(s|ped|ping)?|ceas(e|es|ed|ing)|continu(e|es|ed|ing)|resum(e|es|ed|ing)|no longer|remain(s|ed|ing)?|still|again|return(s|ed|ing)? to)\b`,
    excluding the case-sensitive matches `Still,` and `Again,` (R's concessive "Still," and textual "Again,").
    G3n is G3 without `remain…` and `still` (R's narrower table row "stop, cease, continue, resume, no longer").
  - G4 possessive: `\b(the user|the operator|the principal|Claude|Anthropic)(’s|'s)` (`Claude`, `Anthropic`
    case-sensitive).
  - G5 factive: the factive stems above.
  - G6 contested possessives: `\b(Claude(’s|'s)|its)\s+(wellbeing|welfare|interests|moral status|experiences?|emotions?|sense of (self|identity))\b`.
- **Ledger entry (D1):** one `presupposition_triggers` entry per match: `words` (the matched text), `class`
  (G1 role definite → `definite`; G2 and G4 → `possessive`; G3 → `change-of-state` or `iterative` for
  `again`/`return to`; G5 → `factive`; G6 → `possessive`), `span` (absolute byte span). A match counted by two
  groups is one entry per group.
- **Withholding search (audit addition 3):** a unit of the same pilot whose text contains `whether` or `uncertain`
  and the trigger noun of the heading (u0013 `core value`; u0095 `guideline`; u0286 `open problem`; u0002
  `mission`; u0235 `nature`; u0254 and u0268 `wellbeing`), case-insensitive, `s` allowed at the noun's end. The
  check passes iff there is no hit; a hit is listed verbatim and leaves the unit to the auditor.
- **Trigger-in-title check (audit addition 1):** the heading's trigger words (u0013 `Claude’s`; u0095
  `Anthropic’s`; u0286 `Acknowledging`; u0002 `the mission of`; u0235 `Claude’s`) occur in the title.
- **Exactly-the-existence check (audit addition 2):** the fence's formula is, up to bound-variable names, exactly
  `∃x D(x)` (u0013, u0095, u0286) or `∃x (D(x) ∧ ∀y (D(y) → y = x))` (u0002, u0235), with `D` the trigger's
  restriction over the new predicate, and the fence contains none of `desired`, `relevant`, `must`, `should`.
- **Round trip:** the fence parsed with `ve parse --surface english` over the scratch environment, rendered with
  `ve render --surface english --view ve_english`, and the rendering parsed again gives the same canonical formula.
- **Scratch translation (D4):** the pinned `translation.ve.md` with, for each class A unit whose fence parses: its
  `units` entry replaced by `{"id", "span", "support": "assumption", "kind": "asserted", "meaning": "specified",
  "content": {"fence": id}, "surface": "english"}` (u0248's form); its fence appended after the last fence; the new
  predicates added to the vocabulary with arguments `entity` (P1: `core_value_of(entity, entity)` "{0} is a core
  value of {1}"; `guideline_of(entity, entity)` "{0} is a guideline of {1}"; `open_problem(entity)` "{0} is an open
  problem"; `mission_of(entity, entity)` "{0} is a mission of {1}"; `nature_of(entity, entity)` "{0} is a nature of
  {1}"); one constant `anthropic` of sort `entity`. No sort is added (DRI ET1). Nothing else changes; classes D and E
  change only the ledger.
- **u0235's sentence:** "Some entity is a nature of Claude, and every entity that is a nature of Claude is that
  entity.", the plan's u0002 form with u0235's noun.
- **Exploratory, never counted:** if the plan's uniqueness sentence is refused, the single sentence "Exactly one
  entity is a mission of Anthropic." is tried once, and its outcome is reported as information for draft 2 only.
- **Conflict-free choices:** the `reading_plan.choices` of `ve document check`'s answer, and the readings route's
  conflict verdict for each, as the pilot's `readings/nd-all-check.json` records them.
- **Probe comparison:** the probes that read `translation.ve.md` (the two conclusion probes of `probes/nd/` through
  `ve document readings … --conclusion`) run on the pinned and on the scratch translation with the same binary; their
  answers are compared byte for byte after replacing the values of `document_id`, `meaning_id` and keys ending in
  `_id` or `_hash` that the scratch translation's new units necessarily change. The other carried probes do not read
  `translation.ve.md`, so their inputs are unchanged by construction; that is stated, not re-run.
- **Distinct goals (D5).** Population: the norm units of the constitution with rule content in the pinned
  translation (in a unit's `content.norm` or in a reading of its reading set). An occurrence is a G1 or G2 match in
  such a unit's text. Its goal key is `(group, restriction noun, guard, unless)` with `guard` and `unless` the
  rule's wire formulas with variable indices kept (they are de Bruijn, so "up to the unit's variable names" holds by
  construction). Position (act or guard) is my reading of the sentence, recorded per occurrence. For the G1 units
  that are not formalised, the ledger has no guard: their goal count is **unknown**; reported are the occurrence
  count (upper bound on distinct goals, every rule with its own guard) and the number of distinct `(group, noun)`
  pairs (the source-identity choices).

### 1.4 Expected values

Reproduction of R 2.2 and 2.3 (constitution, run 20261012T1800Z):

| Id | Check | Expected |
|---|---|---|
| H1 | heading presupposition units, bytes | 29 units, 999 B; every one UNFORMALISED with a `presupposed_claim` |
| H2 | classes A, B, C, D, E (units / bytes) | 5/145, 4/149, 7/284, 2/72, 11/349; A's first three 89 B |
| H3 | trigger lexicon on titles | no trigger word in any of class E's 11; at least one in each of A–D's 18 |
| H4 | withholding search, class D | at least one hit for each of u0254, u0268, among them u0269.s02 |
| H5 | withholding search, class A | no hit for any of the five |
| H6 | trigger in title, class A | holds for all five |
| O1 | source occurrences, G1 | 101 |
| O2 | source occurrences, role possessives `the (user\|operator\|principal)(’s\|'s) \w+` | 23 |
| O3 | source occurrences, `(Claude\|Anthropic)(’s\|'s)` | ≥ 205 |
| O4 | source occurrences, G6 | 17 |
| O5 | source occurrences, G3n | 18 |
| O6 | source occurrences, `remain…` | 15 |
| O7 | source occurrences, `still` (any case, before the `Still,` exclusion) | 17 |
| O8 | source occurrences, `again` or `return(s\|ed\|ing)? to` (any case, before the `Again,` exclusion) | 4 |
| O9 | source occurrences, G5 | 46 |
| U1 | units with G1, whole units | ≥ 68 |
| U2 | units with G2, whole units (units / bytes) | ≥ 22 / ≥ 4,833 B |
| U3 | units with G3, whole units (units / bytes) | ≥ 36 / ≥ 6,887 B |
| U4 | units with G4, whole units | ≥ 172 |
| U5 | UDHR heading presupposition units | 0 (so PS-0p's UDHR bytes are 0) |

Dry run (D3, D4):

| Id | Check | Expected |
|---|---|---|
| F1 | the three existence fences (u0013, u0095, u0286) parse, round-trip, and pass "exactly the existence" | all three |
| F2 | the two uniqueness fences (u0002, u0235) parse, round-trip, and pass "exactly the existence and uniqueness" | open: the plan says "if the parser admits it"; the outcome decides P4 |
| F3 | the scratch translation loads: `ve document check` exit code as the pinned translation's under the same binary, `admission.admitted` true | yes |
| F4 | CHECKED bytes, scratch minus pinned | +89 B if F2 fails, +145 B if it passes; UNFORMALISED bytes fall by the same amount; no other status changes |
| F5 | reading-plan choices, conflict-free | 8 of 8, pinned and scratch alike |
| F6 | the two conclusion probes, normalised as in 1.3 | byte-identical, pinned and scratch |

Step 7 (D5) has no expected value: it is the count the plan asks for.

### 1.5 What would change the plan

- F1 fails: the "+89 B" estimate and P1–P3's wording are wrong as written; draft 2's PS-0p wording changes.
- F2 fails: P4 stays UNFORMALISED with "uniqueness not writable (PS-6)", PS-0p's estimate is +89 B, not +145 B.
- F3, F5 or F6 fails: PS-0p's addition breaks the pilot and must not be merged into the prompt as written.
- H3 fails for class E: the "11 invented claims" deletion is not fully word-based and needs the audit per unit.
- H4 fails: class D's handling is not supported by the text as R states.
- D5's distinct-goal count above the joint budget of 64 (plan PS-3): PS-3's coupling cannot help without
  identical applicability or the source-identity choice (Risk 7).
