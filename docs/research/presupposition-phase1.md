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

## 2. Results

Everything below was run after section 1 was committed (`882ba72c`). Each script was committed before its run
(the dry run at `c5b7f1ff`, before any F value existed). Commits: census `ac2af2d5`, dry-run script `c5b7f1ff`,
dry-run evidence `2ada6c54`, exploration `ee16eef5`, step 7 `b63cc6ae`.

### 2.1 Census: reproduction of R 2.2 and 2.3 (15 of 20 pass)

Script [ps0p_census.py](../../research/presupposition/ps0p_census.py); evidence
[census-checks.json](evidence/presupposition/census-checks.json), [headings.json](evidence/presupposition/headings.json),
and the word-level ledgers `ledger-triggers-constitution.json` and `ledger-triggers-udhr.json` (D1).

| Id | Expected | Measured | Verdict |
|---|---|---|---|
| H1 | 29 units, 999 B, all UNFORMALISED with a claim | 29, 999 B, all | PASS |
| H2 | A 5/145 (89), B 4/149, C 7/284, D 2/72, E 11/349 | identical | PASS |
| H3 | no trigger word in class E; one in each of A–D | A–D: all 18 have one. E: u0055 "How to treat operators and users" has the wh-word "How" | **FAIL** |
| H4 | each of u0254, u0268 has a withholding hit, u0269.s02 among them | both: u0269.s02 and u0241.s06 | PASS |
| H5 | no withholding hit for class A | none | PASS |
| H6 | trigger words in class A's titles | all five | PASS |
| O1 | 101 | 101 | PASS |
| O2 | 23 | 23 | PASS |
| O3 | ≥ 205 | 206 | PASS |
| O4 | 17 | 15 | **FAIL** |
| O5 | 18 | 18 | PASS |
| O6 | 15 | 16 | **FAIL** |
| O7 | 17 | 17 | PASS |
| O8 | 4 | 5 | **FAIL** |
| O9 | 46 | 48 | **FAIL** |
| U1 | ≥ 68 | 78 | PASS |
| U2 | ≥ 22 / ≥ 4,833 B | 30 / 7,151 B | PASS |
| U3 | ≥ 36 / ≥ 6,887 B | 46 / 9,641 B | PASS |
| U4 | ≥ 172 | 195 | PASS |
| U5 | 0 | 0 | PASS |

The four occurrence failures are lexical: R's regular expressions were not recorded, and mine differ by exactly the
words below (read after the run; no definition changed):
- O4: R counted "Claude’s emotional" and "its emotional" (the adjective); my G6 needs the noun.
- O6: my `remain\w*` also matches "remainder", which is not a trigger.
- O8: my `return(s|ed|ing)? to` also matches "returned to the orchestrator".
- O9: my `discover\w*` also matches the noun "discoveries" (twice).

H3's failure is a classification one: R put u0055 ("How to treat operators and users", claim "The treatment of
operators and users calls for guidance.") in class E; a wh-title is a trigger by R's own rule for u0032 (class B).
The recorded claim is still not the title's presupposition, but u0055 is not word-free.

H4's second hit, u0241.s06, is about "those whose sentience or moral status is uncertain", not about Claude; the
search is mechanical, so it is listed, and u0269.s02 alone carries the withholding.

The whole-unit counts confirm R 2.3's figures as lower bounds and raise them (U1–U4). Information (no bar): 331 of
the constitution's 1,132 units carry at least one trigger of G1–G6 (324 UNFORMALISED, 65,627 B; 6 OPEN, 1,384 B;
1 READINGS, 100 B). The UDHR has 4 (its triggers are "his", "her" and "their", which G2 lists only after a role
noun, so this is not a measure of the UDHR).

### 2.2 Dry run, as pre-registered (F1–F6: all fail)

Script [ps0p_dryrun.py](../../research/presupposition/ps0p_dryrun.py); evidence
[dryrun.json](evidence/presupposition/dryrun.json), [dryrun-scratch-delta.json](evidence/presupposition/dryrun-scratch-delta.json).

**Control.** `ve document check` on the pinned translation, with this checkout's checkers, reproduces the pinned
run's `check.json` **byte for byte** (CHECKED 73 B; 8 of 8 choices checked, CONFLICT-FREE).

| Id | Expected | Measured | Verdict |
|---|---|---|---|
| F1 | the three existence fences parse, round-trip, are exactly the existence | none parses: "Unknown English phrase 'entity is'" | **FAIL** |
| F2 | (open) the two uniqueness fences | none parses, same refusal | **FAIL**: P4 stays UNFORMALISED |
| F3 | the scratch translation loads, admitted | exit 1: the pinned unit u0248 "Claude is not human." no longer parses ("Unknown English phrase 'is not human'") | **FAIL** |
| F4 | CHECKED +89 B (F2 failed) | not measurable (F3) | **FAIL** |
| F5 | 8 of 8 conflict-free, pinned and scratch | pinned 8 of 8; scratch not measurable (F3) | **FAIL** |
| F6 | the two conclusion probes identical | pinned ALL and ALL; scratch exit 1 | **FAIL** |

The exploratory sentence of 1.3 ("Exactly one entity is a mission of Anthropic.") is refused the same way
("Unknown English phrase 'Exactly one entity'"); it is never counted.

**Why**, read from VE's English vocabulary after the run (`ve.english.EnglishVocabulary`; [explore.json](evidence/presupposition/explore.json)
`variants`):
1. **The sort `entity` has no English noun.** "entity" is a reserved word of the English surface, so the sort is
   written `entity of sort "entity"` in the pinned translation already. No sentence can quantify over it in plain
   English: "Some entity …", "There is an entity that …", "Exactly one entity …" are all refused.
2. **The plan's wordings fail the vocabulary lint.** Every binary "{0} is a … of {1}" (core value, guideline,
   mission, nature) gets `BINARY_AUXILIARY`, `BINARY_CONVERSE`, `LOGICAL_WORD` and `SYMBOL_COLLISION`, and "{0} is an
   open problem" gets `LOGICAL_WORD`, `SYMBOL_COLLISION` and `UNARY_MODIFIER`. Each falls back to the quoted form
   ("{0} has the recorded relation "core_value_of" to {1}"). The "is a N of" shape is admitted only through the finite
   idiom list in `ve/english_vocabulary.py` (for example "{0} is a citizen of {1}"), which is product code.
3. **Adding them breaks an existing wording.** With any of the four binary wordings declared, the existing predicate
   `human` ("{0} is human") is linted `SYMBOL_COLLISION` and falls back to "{0} is classified as "human"", so the
   pinned CHECKED unit u0248 stops parsing and the whole translation is refused. The unary `open_problem` alone does
   not do this.

### 2.3 Exploration, never counted: what VE carries today without product code

Script [ps0p_explore.py](../../research/presupposition/ps0p_explore.py), run after 2.2; evidence
[explore.json](evidence/presupposition/explore.json). It changes no verdict above.

- The five predicates declared **without** a wording (so nothing else changes) and the constant `anthropic`; each
  class A formula written by VE's own renderer (`render_english`), plus the final period the fence parser requires:
  - u0013: `There is an entity of sort "entity" that has the recorded relation "core_value_of" to claude.`
  - u0286: `There is an entity of sort "entity" that is classified as "open_problem".`
  - u0002 and u0235: a three-line "There is a first entity of sort "entity" such that both of the following
    hold: (a) … (b) … is the same as the first entity of sort "entity"."
- All five parse back to **exactly** the formula of 1.3 and re-render to the same sentence (round trip).
- **Any vocabulary addition invalidates the recorded separating situations** (their model ids include the
  environment): even the vocabulary alone, with no unit converted, is refused with "distinguishing model id does not
  match model". A pilot run regenerates them in its `nd.py all` step; the exploration does the same with a
  transcription of `nd.py`'s `find_situations` (pilot code, not product code), which reproduces the pinned reading
  sets exactly when run on the pinned translation.
- With the five units converted and the situations regenerated: the translation loads and is admitted; CHECKED
  **+145 B** and UNFORMALISED −145 B, nothing else moves; the residual's assumptions go from 19 to 24; 8 of 8
  choices checked, CONFLICT-FREE; both conclusion probes are **byte-identical** to the pinned ones. The only other
  change is the expected one: the witness model now satisfies the five existence premises, with one element
  (Claude, Anthropic and every witness are `e0`), which confirms the plan's "existential premises can be witnessed by
  existing elements" (no larger domain).

So the mechanism works and costs nothing in conflicts or probes; what is missing is the English.

### 2.4 Step 7: distinct projected goals (no bar)

Script [ps0p_goals.py](../../research/presupposition/ps0p_goals.py); evidence [goals.json](evidence/presupposition/goals.json).

- **Formalised rules** (18 norm units in the pinned translation): 4 G1/G2 occurrences, in 3 units.
  - u0123.s02.p1 "the operator" and u0123.s03 "the user" sit in the guard, packed into a guard atom
    (`instruction_promote_own_products…`, `instruction_false_information_deceiving_user`): no formula position
    exists for them (Risk 1, the translation boundary).
  - u0156.s03 "the user" and "its content" sit in the rule's act: 2 obligations per reading alternative (strict,
    default), **4 distinct goal keys** in all, 2 within either alternative. The two in one alternative share the
    rule's applicability but differ in row and restriction, so **no group has equal goals: nothing to couple.**
  - The plan's P7 trigger, "the system prompt’s instructions" in u0073.s05, is outside G1/G2 (its owner is neither
    a role nor a pronoun), so it is not in this count.
- **Not formalised:** 98 G1 occurrences (the user 59 in 53 units, the operator 39 in 35 units, both roles in 13
  units; all UNFORMALISED) and 32 G2 occurrences in 29 units over 19 distinct owner–object phrases. Their goals and
  whether they share applicability are **unknown**: the ledger records no guard for an unformalised unit. The bounds
  are: at most 98 distinct G1 goals (every rule with its own guard), and 2 source-identity choices ("assume there is
  a user", "assume there is an operator"). Against the joint budget of 64, 98 independent two-way choices are far
  over it, and 2 are far under.

## 3. Verdicts

| Item | Pre-registered bar (quoted in 1.1) | Result | Verdict |
|---|---|---|---|
| PS-0p bar | "The next audit samples every claimed heading unit and accepts each." | not run: needs the next pilot run and its audit (model runs) | **DEFERRED** |
| PS-0p step 3 / bytes (+89 B, +145 B) | the plan's sentences, "if the parser admits it" | the parser admits none of the five (F1, F2) | **FAIL**: 0 B claimable as written |
| PS-0p step 6 check | "it loads, the reading-set choices stay conflict-free (8 of 8 today), and the carried probes are byte-identical" | as written, the translation does not load (F3–F6); in the exploration, it loads, 8 of 8, probes byte-identical | **FAIL** as written; the mechanism passes in the exploration (never counted) |
| PS-0p steps 2 and 4 (classes E and D) | reproduction H1–H4 | classes reproduced exactly; D withheld; E word-free for 10 of 11 | PASS, except u0055 (H3 FAIL) |
| PS-0p step 1 (ledger) | U1–U4 ≥ R's lower bounds; O1–O9 = R's counts | U1–U4 PASS; O: 5 of 9 equal, 4 differ by named words | PASS for the units; O4, O6, O8, O9 FAIL (lexical) |
| PS-0p step 7 (distinct goals) | none (a count) | 4 keys in formalised rules, no equal goals; unformalised: unknown, bounds 2–98 | reported |
| PS-0p step 5 (class B) | "claimed only if the audit accepts it" | needs the audit | **DEFERRED** |
| PS-E1, PS-E2 | 6/40 candidate, 36/40 one-reading, controls 11 of 12 …; 36/40 on 18 of 20 | model calls; run later, separately | **DEFERRED** (out of this phase) |

## 4. Consequences for draft 2

**PS-0p (changed).**
- **"Depends on: Nothing" is wrong for class A.** Its claim (+89 B, +145 B) needs two things that are not on
  `main`: (i) an English noun for existence over the sort `entity`, or a new sort, which DRI ET1 forbids until
  premise-scale lands; and (ii) admitted wordings for the relational nouns ("{0} is a core value of {1}"), which the
  vocabulary lint refuses and only the idiom catalogue (english-lean, product code) admits. Until both land, PS-0p
  claims **0 B**, and P1–P4 stay UNFORMALISED with the note "existence claim not writable in VE English (PS-0p phase
  1)".
- **The fallback English is not a way round.** VE can carry the formulas today with quoted identifiers
  (`… has the recorded relation "core_value_of" to claude.`), and the check then passes (2.3). That violates VE's
  "zero-training English, no symbols" rule; an audit should reject it as English. Draft 2 should say so and not
  offer it to the pilot.
- **Add two pilot rules to PS-0p's prompt addition:** a vocabulary addition is followed by the run's
  situation-regeneration step (`nd.py all`), and the run checks that no existing wording changed (here, adding the
  plan's four binary wordings silently turned u0248's "is human" into a fallback, and the translation stopped
  loading).
- **Steps 1, 2 and 4 are confirmed** and can be merged into the prompt now: classes A–E reproduce exactly; class D
  is withheld by u0269.s02; the 11 class E claims are invented, but u0055 is a wh-title and goes to the audit as an
  item instead of being deleted mechanically. Step 1's regular-expression census is a lower bound (it misses "the
  system prompt’s instructions"); the ledger field is the translator's.
- **The bytes line becomes:** 0 B now; +145 B when (i) and (ii) land (the exploration shows nothing else blocks it:
  8 of 8, probes identical); stretch +294 B with class B, audit-gated. NORTH-STAR row 12 (Risk 6): 0 B direct today,
  not 145 B.

**PS-6 (changed: it becomes the enabler of PS-0p's bytes).** The English rows for possessives and definites must
include the existence sentence a heading's assumption needs ("Claude has at least one core value.", "Anthropic has
exactly one mission."), and the relational-noun wording ("is a core value of"). Either PS-6 absorbs class A's
claim, or a small english-lean catalogue item precedes PS-0p. The DRI picks; this note recommends moving class A's
bytes to PS-6, since PS-6 is already the English queue's presupposition batch.

**PS-E2 (changed).** Its rendered lines ("Assumed (from ‘Claude’s core values’): Claude has at least one core
value.") are not what VE renders today; today the renderer writes the quoted fallback. PS-E2 should test the lines
PS-6's rows will produce, so it runs after those rows exist, or its items are labelled as the target wording.

**PS-3 (changed in priority).** In the formalised pilot there is **no group with equal goals** (2.4), so goal
coupling has nothing to compress today. The unformalised "the user"/"the operator" occurrences (98) have unknown
goals; if their guards differ, as rules usually do, 98 two-way choices are far over the budget of 64 and only the
source-identity choice (2 choices) helps. Draft 2 should put the source-identity choice first in PS-3 and keep goal
coupling behind a re-count at the first run that formalises those rules (Risk 7 stands, now measured).

**PS-5p (confirmed).** u0254 and u0268 are withheld by u0269.s02; the optional reading set {assumed, no claim}
stays audit-gated.

**PS-1, PS-2a, PS-2b, PS-4, PS-7, PS-8: unchanged** by this phase. PS-1's fixtures P1–P4 should use the formulas of
1.3, which the exploration shows round-trip exactly; their English column waits for PS-6.

**R 2.3 (research note).** Its counts are confirmed as lower bounds (whole units: 78 role-definite units, 30 / 7,151 B
possessive-over-missing-object, 46 / 9,641 B change-of-state, 195 possessive). Its regular expressions should be
recorded; four occurrence counts differ from mine by named words (2.1).

## 5. Deferred, and deviations

**Deferred** (each needs a model run, product code, or something not on `main`):
- The PS-0p bar (the next audit), class B's audit items, the translator's `pre`/`carrier` fields, and
  `other_blockers: presupposition` on unformalised units: the next pilot run and its audit (model runs).
- Merging the prompt addition: the DRI merges prompt additions (SC2). The draft is
  [evidence/presupposition/pilot-prompt-addition.md](evidence/presupposition/pilot-prompt-addition.md), revised by
  section 4.
- Class A's claim: english-lean wording and a noun or sort for existence (product code; premise-scale for a sort).
- PS-E1 and PS-E2: model calls, run separately.

**Deviations from the task or the pre-registration** (none changes an expected value or a bar):
- `manage-agents/debates/plan-synthesis/edits-presupposition.md` does not exist; the DRI's rulings for this plan
  are in `DRI-DECISIONS-PHASE2.md` (header note).
- **Rust time limit.** `VE_RUST_TIMEOUT=600` for every `ve` run. At the 5 s default the pinned translation's own
  check is CheckerUnavailable (measured), so no comparison is possible. The DRI's 2026-10-14 note forbids the raised
  limit in pilot checks because the Rust process grew to 70 GB; here every run had `prlimit --as=6442450944`, which
  the Rust child inherits, so its memory was capped at 6 GiB. No run failed.
- **Checkers.** This checkout's `lean/` and `rust/` trees are identical to `main` at `dccd9cf5` (`git diff` empty);
  its built `ve_service` and `ve` were copied from the `main` worktree, and both hashes are pinned in this
  checkout's `lean/checkers.lock`. The control check (2.2) reproduces the pinned record byte for byte.
- **Round trip and parsing.** 1.3 named `ve parse` and `ve render`. `ve parse --env` does not read a document's
  declared wordings (it refuses the pinned u0248 too), so the dry run used the document route (`load_document`, the
  product's own fence reading). The round trip did not run in 2.2, since nothing parsed; the exploration used
  `parse_english` and `render_english`.
- F4 and F5 are counted FAIL because the scratch translation did not load; they were not measured.

## 6. Reproduction

From the repository root, with `lean/.lake/build/bin/ve_service` and `rust/target/release/ve` pinned:

    python3 -I research/presupposition/ps0p_census.py                 # seconds
    python3 -I research/presupposition/ps0p_goals.py                  # seconds
    VE_RUST_TIMEOUT=600 prlimit --as=6442450944 uv run python research/presupposition/ps0p_dryrun.py    # about 4 min
    VE_RUST_TIMEOUT=600 prlimit --as=6442450944 uv run python research/presupposition/ps0p_explore.py   # about 16 min

Scratch documents go to `/tmp/ps0p` (`PS0P_WORK` overrides it); the pinned runs are only read.
