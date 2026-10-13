# Action phrases, phase 1 (AP-0): baseline measurements

> Status: phase 1 of [act-phrases-PLAN.md](../spec/act-phrases-PLAN.md) (draft 3), branch `research/act-phrases-p1` from
> `b4be316a` (product code at `main` `49de179e` = `ve-green-ts-B1`). Pilots and pre-registered measurements only: no
> product code (`ve/`, `lean/VE/`, `rust/`, `tools/`) changed, no model called. Scripts are in
> [research/act-phrases/](../../research/act-phrases/), evidence in
> [evidence/act-phrases/](evidence/act-phrases/). The pilot inputs (UDHR and constitution runs `20261012T1800Z`) were
> read only.
>
> Section 1 is the pre-registration, committed before any measurement ran (`34009f5f`) and not edited since. Results
> follow in sections 2 to 5, each against the bar quoted from section 1.

## 0. Summary

| Item | Bar (section 1) | Measured | Verdict |
|---|---|---|---|
| 1. Re-try the 11 M1 units | before: M1 = 1,860 B, 11 units; a unit made expressible is credited to AP-0 | all 11 load as opaque entitlements; 4 (u039, u085, u091, u106; 658 B) meet every criterion with nothing hidden in a name. M1 after = **1,202 B, 7 units** (primary), 0 B (loose) | PASS (measured); M1 moves only if two deferred conditions hold (section 6) |
| 2. Count M3 | before: unmeasured | **100 lines** (UDHR 72, constitution 28), 160 occurrences | PASS (measured) |
| 3. Tag the constitution's 18 norm units | before: M4 = 18 units, 2,580 B | **17 units, 2,502 B** (pointer 7, folded 3, shortened 7, none 1: u0052.s01) | PASS (measured); M4 moves by one unit |
| 4. Measure N | R ≤ 64 keeps N = 256; 10 S ≤ 2,100,000 keeps `stepBudget` | **R = 2**, **S = 14,440**, on the registered 22-phrase corpus | **PASS** (N = 256, `stepBudget` = 2,100,000 stand for draft 2's rule table; provisional until 7.6c is decided) |

Main consequence (section 7): all of AP-1's estimated UDHR byte credit (u039, u085, u106, u091: 658 B) loads today as
opaque entitlements. It moves to AP-0 **if** two deferred conditions hold: the pilot's blind audit passes the four
units, and they load inside their part documents, not only as one-unit companions (section 6). AP-1 then keeps its
display and faithfulness gains (M2, M3, M4), not bytes. The measurement also found a gap in the grammar, outside
every bar: a joined filler made of plain words gets one fixed grouping with no reading set ("arbitrary arrest,
detention or exile"). That bears on D4, AP-7, the bounded re-check and the value of N.

AP-0 is **not complete** where the plan puts it: the plan's work is in the pilot directories, and nothing here was
written there (section 6). It is complete when the orchestrator's pilot run copies the evidence in.

Section 9 lists the corrections made after review; no measured number changed.

## 1. Pre-registration (written before any run)

### 1.1 What the plan pre-registers

AP-0 in the plan (section 4, "AP-0. Baseline"), quoted:

> - **Work** (in the UDHR and constitution pilot directories, by the orchestrator's pilot job):
>   1. Re-try the 11 UDHR units of M1 as plain entitlements under today's language (`ve-green-ts-B1` or later),
>      recording per unit `expressible_today: yes/no` and the reason.
>   2. Count M3 in the four UDHR parts and the constitution's main document.
>   3. Add `act_workaround ∈ {pointer, folded, shortened, none}` to the constitution's 18 norm units.
>   4. Measure the raw derivation budget N (D2): the largest raw derivation count over the pilots' act phrases, read
>      with the specification's rule table, and fix N above it.
> - **Pre-registered:** the "before" values are the research note's (M1 1,860 B, M2 5 units, M4 18 units). A unit made
>   expressible by AP-0 is credited to AP-0, not to a later batch.
> - **Moves:** possibly M1 (pilot repair). M3 gets measured.

And D2: "a **raw derivation budget N** (the parser's cap; AP-0 measures the largest raw count over the pilots' act
phrases and N is fixed above it)". The specification (1.6, 12) holds the provisional values `rawCap` = 256 and
`stepBudget` = 2,100,000, "measured with N".

AP-0 is a baseline, not a hypothesis test: the plan gives "before" values and asks for measured "after" values, with no
target. So each item's verdict below is **PASS** when the measurement was made by the method fixed here and its
outcome is reported against the before value; the before/after comparison is the result. Item 4 has a numeric bar
(1.5). The operational rules below (what counts, how a tag is decided) were written after reading the inputs the
research note already cites, but before running any check, render or parse; none is changed after a result.

### 1.2 Item 1: re-try the 11 M1 units

**Before:** M1 = 1,860 B, 11 units (u039, u041, u076, u079b, u082, u085, u086, u091, u092, u106, u108).

**Method.** For each unit, one companion document in the pilot's own entitlement form (as
`readings/u081.entitlement.ve.md`): profiles `documents@1`, `norm-defaults@0`, `norms@0`, `relational-fol@0`; the body
is the unit's source text; one norm unit spanning it; a plain regulated predicate (completion `unspecified`, no
bearer) whose `description` and `verbalisation` carry the unit's words; arguments and guards where the ledger asks for
them; open terms for open words. Built by `research/act-phrases/ap0_udhr_retry.py` into
`docs/research/evidence/act-phrases/udhr-retry/`, checked and rendered at this worktree's commit with the ordinary
entry points (`ve.document.check_document`, `render_document`), under `prlimit --as=8589934592`.

**Criteria** (all mechanical):

- **C1, Lean accepts it:** `check_document` returns a report, no error.
- **C2, fully accounted:** the report's coverage is 100% and no byte is `UNFORMALISED`.
- **C3, words carried, not only quoted** (the u081 audit rule, "content only in the quotation"): every content word of
  the source span (lower case, letters only, a fixed stop-word list in the script, a plural `s` ignored) occurs in the
  document's own text outside the body: predicate descriptions and verbalisations, sort descriptions, open-term names
  and factors.
- **C4, the ledger's objections met:** each element the unit's ledger entry (`blocker_detail`, `audit_repair`) says must
  not be dropped is carried, and each argument it asks for is a slot. Per unit:

| Unit | Must carry | Argument asked for |
|---|---|---|
| u039 | "in full equality"; "fair and public hearing by an independent and impartial tribunal"; the determination "of his rights and obligations and of any criminal charge against him" | the determination (arity 2, a guard on it) |
| u041 | "until proved guilty according to law in a public trial at which he has had all the guarantees necessary for his defence"; "charged with a penal offence" | — |
| u076 | "the government of his country"; "directly or through freely chosen representatives" | — |
| u079b | "by secret vote or by equivalent free voting procedures"; the subject (elections) | — |
| u082 | the means ("through national effort and international co-operation"); the limit ("in accordance with the organization and resources of each State"); the object ("the economic, social and cultural rights indispensable for his dignity and the free development of his personality") | — |
| u085 | "equal pay for equal work"; "without any discrimination" | — |
| u086 | the outcome clause ("ensuring for himself and his family an existence worthy of human dignity"); the supplement ("supplemented, if necessary, by other means of social protection"); "who works" | — |
| u091 | the beneficiary clause ("adequate for the health and well-being of himself and of his family"); the list ("including food, clothing, housing and medical care and necessary social services") | — |
| u092 | the event list; "in circumstances beyond his control" | — |
| u106 | "the moral and material interests"; the production's kinds ("scientific, literary or artistic"); authorship ("of which he is the author") | the production (arity 2, authorship and kind as a guard) |
| u108 | "a social and international order in which the rights and freedoms set forth in this Declaration can be fully realized" | — |

- **Structure hidden in a name.** A document that meets C1 to C4 may still hold, inside one opaque predicate, structure
  that the research note (2.1, column "With this design") assigns to a feature other than a single act: u041 time
  ("until"); u076 two readings ("directly or through", AP-4); u079b an obligation ("shall") with a disjunctive act and
  a subject carried from u079a (AP-3); u082 rights as objects and a limit other units cite; u086 a condition inside the
  object (R4); u092 two readings ("in circumstances beyond his control", AP-4); u108 modality ("can be"). u039, u085,
  u091 and u106 have none listed: their act is a single act (AP-1), opaque under AP-1 as well.

**Recorded per unit:** `loads_as_opaque_entitlement` = C1 ∧ C2 ∧ C3 ∧ C4; `expressible_today` = yes exactly when
`loads_as_opaque_entitlement` holds and the unit's hidden-structure list above is empty; the reason. The faithfulness
verdict of an independent audit is a model call: **deferred** (section 6), so `yes` here means "expressible by the
mechanical criteria, pending the pilot's audit".

**After values:** M1 (primary) = the bytes and units with `expressible_today` = no. M1 (loose) = the bytes and units
with `loads_as_opaque_entitlement` = no. Units with `yes` are credited to AP-0, not to a later batch (plan).

### 1.3 Item 2: count M3

**Before:** unmeasured.

**Method.** Render, at this worktree's commit, the four UDHR part documents (`translation-part01.ve.md` to
`-part04.ve.md`) and the constitution's main document (`translation.ve.md`), both of run `20261012T1800Z`, with
`render_document` (the natural view, as `ve document render`), under the memory limit; script
`research/act-phrases/ap0_m3.py`.

**Counting rule.** M3 (primary) = the number of rendered lines containing the substring `classified as` or
`has the recorded relation`. Secondary: the number of occurrences; the distinct predicate names quoted in them; and the
split of matching lines by the kind of the predicates they name: (a) a plain regulated predicate (an entitlement, the
kind AP-1 gives an act and a form), (b) any other predicate. A line naming both kinds counts in both secondary buckets.
Consistency check (not a bar): the UDHR parts' renderings compared byte for byte with the pilot's own
`rendered-parts/*.md` of that run.

### 1.4 Item 3: tag the constitution's 18 norm units

**Before:** M4 = 18 units, 2,580 B (research note 2.2: Group A pointer 7, Group B folded 4, Group C shortened 7).

**Method.** For each norm unit of the constitution's `translation.ve.md` (run `20261012T1800Z`): its rule (from the
unit, or from the first reading of its reading set), its regulated predicate's act, its source span. Script
`research/act-phrases/ap0_m4.py`.

**Tagging rule**, first match wins. Source words: the span in lower case, `’` folded to `'`, Markdown `*` removed,
split at anything other than letters, digits, `'` and `-`. Act runs: the act without `{0}`, cut at each slot into
maximal word runs; a run that is a single marker word (*in, about, to, by, of, for, with*) directly before a slot is
dropped (it introduces the slot, which stands for source words).

1. `pointer`: the act's first word is *do* and *do* is not a source word (the act only names a case atom).
2. `folded`: the rule's guard holds a disjunction (`or`) of two or more atoms (a list of the source's acts or objects
   moved into case kinds).
3. `shortened`: some act run is not a contiguous word sequence of the source.
4. `none`: otherwise (the act carries the source's words as written).

**After value:** M4 = the units and bytes with a tag other than `none`. The tags are compared with the research note's
groups; disagreements are reported, not resolved by changing the rule.

### 1.5 Item 4: measure N (and the step budget)

**Bar** (D2; specification 1.6): N is "fixed above" the largest raw derivation count over the pilots' act phrases; the
provisional N is 256.

**Corpus:** [research/act-phrases/corpus.json](../../research/act-phrases/corpus.json), committed with this section:
the specification's nine pilot fixtures (G5 to G12, G14v, with its vocabularies V5 to V14) and 13 further pilot act
phrases the research note names (u024, u037, u045a, u045a+u045b, u057, u067, u068, u071b, u101, u0062.s01, u0156.s03,
u0165.s05, u0165.s06), each with the vocabulary written before measuring. A stress family (the specification's L rows
extended to 12 edge modifiers) is measured for the step budget only and is not part of the bar.

**Instrument.** The specification's stub (draft 1, which implements the rule table 5.2 and meaning 5.3; both sections
are byte-identical in draft 2, sha256 of the two sections `ad033f71…` at `02a57b4e` and `b4be316a`), copied unchanged to
`research/act-phrases/stub/` with its sha256, plus a measurement file appended at run time; run with
`lake env lean` against this worktree's Lean build (`49de179e`). Per phrase: lexing (`lex`), `framesOk` (draft 1) and
draft 2's canonical-marker condition (checked by the script), the raw count with an effectively unbounded cap
(1,000,000) and budget (10⁹), the distinct meanings, the `readings` outcome at `rawCap`/`stepBudget`, and the parser's
steps (`Prepared.steps`) at cap 256.

**Rule for N** (fixed now): let R be the largest raw count over the corpus.

- R ≤ 64: N stays 256 (the provisional value; the limit fixtures L6 to L8 are built around it). **PASS**.
- 64 < R < 256: N = 1,024. **FAIL** for the provisional value; N changes.
- R ≥ 256: N = the least power of two ≥ 4R. **FAIL**; N changes.

**Rule for the step budget** (fixed now): let S be the largest step count over the corpus at cap 256. If
10 S ≤ 2,100,000 the provisional `stepBudget` stays (**PASS**); otherwise it becomes 10 S rounded up to the next
100,000 (**FAIL**; it changes). A corpus phrase whose parse does not finish within 10⁹ steps is reported and makes
both verdicts FAIL.

Secondary (reported, no bar): phrases where raw > readings (two derivations with one meaning: the rule table's
"only the five edge rules give several derivations", checklist item 3), and phrases with no reading.

### 1.6 Deferred before running

- The independent audit of any unit item 1 finds expressible (a model-run blind audit in the pilot): model call.
- Writing the re-tried units, the M3 count and the `act_workaround` tags into the pilot runs' own ledgers
  (`units.json`, `metrics.json`): the pilot inputs are read-only here; the orchestrator's next pilot run copies them
  from the evidence files.
- M2 (5 units, 669 B) is not re-measured: AP-0 has no item for it.

## 2. Item 1: the 11 M1 units under today's language

**Bar** (1.1, 1.2): before, M1 = 1,860 B in 11 units. `expressible_today` = yes exactly when C1 to C4 hold and the unit's
hidden-structure list is empty. A unit made expressible is credited to AP-0.

**Run.** `prlimit --as=8589934592 uv run python research/act-phrases/ap0_udhr_retry.py` at this commit (Lean built at
`49de179e`, Rust binary pinned in `lean/checkers.lock`). Evidence: `evidence/act-phrases/udhr-retry.json`, the 11
documents in `evidence/act-phrases/udhr-retry/`, and the first run, kept unchanged, in `udhr-retry-run1.json`.

| Unit | Bytes | C1 | C2 | C3 | C4 | Hidden in the name (1.2) | `expressible_today` | Attempts |
|---|---|---|---|---|---|---|---|---|
| u039 | 201 | ✓ | ✓ | ✓ | ✓ (determination slot, guard on it) | — | **yes** | run 1: guard variables reversed (an authoring error, below) |
| u041 | 201 | ✓ | ✓ | ✓ | ✓ | time ("until proved guilty") | no | 1 |
| u076 | 125 | ✓ | ✓ | ✓ | ✓ | two readings (AP-4) | no | 1 |
| u079b | 76 | ✓ | ✓ | ✓ | ✓ | an obligation stated as a plain property of elections, with a disjunctive act (AP-3); subject from u079a | no | 1 |
| u082 | 277 | ✓ | ✓ | ✓ | ✓ | rights as objects; a limit other units cite | no | 2: the full wording exceeds the 256-character verbalisation limit (`ResourceLimit: verbalisation size`, `lean/VE/Bridge.lean:123`); without the display-only verbalisation, the description carrying every word, it passes |
| u085 | 85 | ✓ | ✓ | ✓ | ✓ | — | **yes** | 1 |
| u086 | 216 | ✓ | ✓ | ✓ | ✓ | condition inside the object (R4) | no | 1 |
| u091 | 201 | ✓ | ✓ | ✓ | ✓ | — | **yes** | 1 |
| u092 | 163 | ✓ | ✓ | ✓ | ✓ | two readings (AP-4) | no | 1 |
| u106 | 171 | ✓ | ✓ | ✓ | ✓ as implemented (production slot, guard on it; kinds merged into one predicate, below) | — | **yes** | run 1: guard variables reversed; attempt 1 (kinds as three guard predicates) failed only C4 as implemented; attempt 2 (kinds as one predicate) passes |
| u108 | 144 | ✓ | ✓ | ✓ | ✓ | modality ("can be") | no | 1 |

Every Lean check returned `model` (no conflict found), coverage 100%, status OPEN.

**Result.**

- `loads_as_opaque_entitlement`: **11 of 11**. M1 (loose) after = **0 B**.
- `expressible_today` = yes: **u039, u085, u091, u106 (4 units, 658 B)**, credited to AP-0.
- M1 (primary) after = **1,202 B, 7 units** (u041, u076, u079b, u082, u086, u092, u108), from 1,860 B.
- **Verdict: PASS.** The measurement was made by the registered method. M1 moves only if two deferred conditions hold
  (section 6): the pilot's independent audit passes the four `yes` units, and they load inside their part documents,
  not only as the one-unit companions checked here.

**What went wrong on the way, all recorded:**

- In run 1, u039 and u106 failed C1 with `TypeMismatch`. The guard variables were written in the wrong order: a guard
  variable counts from the last argument, so in a rule over (person, x), `var 0` is x. This was a translator's error,
  not a language limit. After fixing the order, both pass C1.
- u106's first attempt carried the three kinds as three guard predicates in a disjunction. That carries them with
  more structure, but C4 as implemented requires every content word of a phrase to occur in **one** text. The
  registration (1.2) says only that each element is "carried"; the one-text reading is the implementation's, not the
  registration's. The check was not changed. The second attempt, rewritten to fit it, uses one opaque predicate
  ("The production is scientific, literary or artistic") and passes. That merges the three kinds into one name: the
  same joined-filler pattern that 7.6c flags. So u106's `yes` rests on an encoding that the audit must judge, and it
  is weaker than the first attempt's. Both attempts wrote the same file, `udhr-retry/u106.entitlement.ve.md`, so the
  first document was overwritten. Only its C1 to C4 summary survives, in the `attempts` list of `udhr-retry.json`.
  Its specification is still in the script (`UNITS["u106"]` in `ap0_udhr_retry.py`, without the `retry` override).
- C3 as implemented also counts the sorts' plural verbalisations as the document's own text; the registration (1.2)
  does not list them. Recomputed without them on each unit's final attempt, C3 still holds for all 11 units (no
  source word was carried only by a plural), so no result changes.
- u082 meets a real limit of today's language: a verbalisation holds at most 256 characters. Its 277-byte sentence
  fits only in the description, so its display falls back to "classified as".

**The price of these encodings.** All 11 documents render the fallback sentence. Ten say "classified as …"; u039, with
two arguments, says "has the recorded relation …". Each act is one opaque string, which is also its status under
AP-1, because AP-1 does not change an act's meaning (plan 2.5, D1).

## 3. Item 2: M3

**Bar** (1.3): before, unmeasured. M3 (primary) = the rendered lines containing `classified as` or
`has the recorded relation`.

**Run.** `prlimit --as=8589934592 uv run python research/act-phrases/ap0_m3.py`. Evidence:
`evidence/act-phrases/m3-count.json` and the five renderings in `evidence/act-phrases/m3-rendered/`.

| Document | Lines matching | "classified as" | "has the recorded relation" | Distinct predicates | Lines naming an entitlement by name (exploratory) |
|---|---|---|---|---|---|
| UDHR part 1 | 23 | 34 | 0 | 27 | 9 |
| UDHR part 2 | 17 | 23 | 0 | 20 | 9 |
| UDHR part 3 | 11 | 11 | 0 | 11 | 7 |
| UDHR part 4 | 21 | 17 | 6 | 15 | 3 |
| **UDHR** | **72** | 85 | 6 | 72 | 28 |
| **Constitution** (main document) | **28** | 60 | 9 | 33 | 0 |
| **M3** | **100** | | | | |

- **Verdict: PASS** (measured): M3 = **100 lines**, 160 occurrences.
- **Consistency check.** The four UDHR renderings are byte-identical to the pilot's own `rendered-parts/*.md` of that
  run.
- **The registered split** shows (a) 0 lines naming a plain regulated predicate and (b) 100 lines naming another
  predicate. The reason is that the part documents declare their entitlements as ordinary predicates, stated as
  assertions. Only the one-unit companions declare them `role: plain`. So the split by declared kind cannot see
  entitlements in the parts.
- **Exploratory count** (added after the run, not registered): 28 UDHR lines name a predicate called
  `has_the_right…` or `is_entitled…`. These are the lines AP-1's "entitlements with an act render in English" could
  reach, once the pilot declares those entitlements as plain predicates with an act and a form. The other 44 UDHR
  lines name base predicates, which AP-1 does not touch.
- **Exploratory, after review: the constitution's 28 lines** (`research/act-phrases/ap0_m3_atoms.py`, evidence
  `evidence/act-phrases/m3-workaround-atoms.json`; not registered). Each of the 28 lines names a predicate that occurs
  in the rule of a unit item 3 tagged other than `none`. **19 lines** name a predicate of a pointer or folded unit
  (Groups A and B), where the act's content was moved into case atoms: the seven hard-constraint atoms of u0165.s01
  to s07 with `restricted_action_knowing_or_quite_likely` (7 lines), `input_is_persona` and
  `input_is_specific_instructions` of u0062.s01, and the `instruction_…` atoms of u0123.s02.p1 and u0123.s03
  (12 lines). The other **9 lines** name only the guard cases and exceptions of shortened units (u0036.s05, u0073.s05,
  u0156.s03, u0168.s01, u0263.s04.p2), such as `genuine_ambiguity` and `exception_to_asking_for_clarification`.

## 4. Item 3: `act_workaround` on the constitution's 18 norm units

**Bar** (1.4): before, M4 = 18 units, 2,580 B. M4 after = the units with a tag other than `none`.

**Run.** `uv run python research/act-phrases/ap0_m4.py`. Evidence: `evidence/act-phrases/m4-act-workaround.json` (each
unit with its act, source, tag and reason).

| Tag | Units | Bytes | Units |
|---|---|---|---|
| pointer | 7 | 874 | u0165.s01–s07 |
| folded | 3 | 784 | u0062.s01, u0123.s02.p1, u0123.s03 |
| shortened | 7 | 844 | u0036.s05, u0073.s05, u0123.s01.p1, u0125.s04.p2, u0156.s03, u0168.s01, u0263.s04.p2 |
| none | 1 | 78 | u0052.s01 |

- **Verdict: PASS** (measured): M4 = **17 units, 2,502 B**, from 18 units and 2,580 B.
- **Disagreements with the research note's groups** (reported; the rule was not changed):
  - **u0052.s01** (note: shortened; rule: none). Its act, "use good judgment when evaluating conversational inputs",
    is in the source as written. The only word not carried is *always* in "should always use", which stands outside
    the act. Nothing about the act phrase was worked around.
  - **u0123.s01.p1** (note: folded; rule: shortened). Its guard is a single atom, and its act "give Claude {1}"
    rewords "ask Claude to behave …". It is still a workaround, so M4 is unaffected.
- **Sensitivity** (not registered). The registered rule drops a slot-introducing marker only when the marker is a word
  run of its own. So "remain firm in {1}" leaves the run "remain firm in", which is not in the source, and u0168.s01 is
  tagged shortened. If a final marker before a slot were dropped too, u0168.s01 would be `none`, and M4 would be
  16 units, 2,406 B. The registered value stands.

## 5. Item 4: N and the step budget

**Bar** (1.5): with R the largest raw derivation count over the corpus, R ≤ 64 keeps N = 256 (PASS). With S the
largest step count at cap 256, 10 S ≤ 2,100,000 keeps `stepBudget` (PASS).

**Run.** `prlimit --as=8589934592 uv run python research/act-phrases/ap0_n.py`. One `lake env lean` elaboration of the
stub copy (sha256 `6e33f85c…`, verbatim) plus the generated measurement section, against this worktree's build of
`49de179e`. Exit 0, no other output: the stub's own 161 `#guard`s also pass at this commit. Evidence:
`evidence/act-phrases/n-measurement.json`.

| Row | Unit | Bytes | Raw | Meanings | `readings` at 256 / 2.1 M | Steps (cap 256) |
|---|---|---|---|---|---|---|
| G5 | u051 | 67 | 2 | 2 | ok 2 | 5,612 |
| G6 | u027 | 85 | 1 | 1 | ok 1 | 2,788 |
| G7 | u079b | 66 | 1 | 1 | ok 1 | 3,302 |
| G8 | u105 | 138 | 2 | 2 | ok 2 | 9,272 |
| G9 | u055 | 97 | 2 | 2 | ok 2 | 4,850 |
| G10 | u092 | 152 | 2 | 2 | ok 2 | 9,176 |
| G11 | u076 | 73 | 1 | 1 | ok 1 | 3,915 |
| G12 | u087 | 74 | 2 | 2 | ok 2 | 8,575 |
| G14v | u0123.s03 | 185 | 1 | 1 | ok 1 | **14,440** |
| X024 | u024 | 35 | 1 | 1 | ok 1 | 2,527 |
| X037 | u037 | 56 | 1 | 1 | ok 1 | 3,622 |
| X045a | u045a | 93 | 1 | 1 | ok 1 | 5,608 |
| X045ab | u045a+u045b | 142 | 0 | 0 | ok 0 | 8,632 |
| X057 | u057 | 34 | 1 | 0 | ok 0 | 3,482 |
| X067 | u067 | 38 | 1 | 1 | ok 1 | 2,522 |
| X068 | u068 | 153 | 0 | 0 | ok 0 | 10,538 |
| X071b | u071b | 99 | 0 | 0 | ok 0 | 12,438 |
| X101 | u101 | 97 | 1 | 1 | ok 1 | 5,854 |
| X0062 | u0062.s01 | 73 | 1 | 1 | ok 1 | 5,231 |
| X0156 | u0156.s03 | 78 | 1 | 1 | ok 1 | 6,264 |
| X0165s05 | u0165.s05 | 116 | 1 | 1 | ok 1 | 2,781 |
| X0165s06 | u0165.s06 | 160 | 1 | 1 | ok 1 | 5,167 |

(Bytes are the strings as written. G14v is 183 B after folding `’`, as the specification counts.)

- **R = 2** (G5, G8, G9, G10, G12: one binary edge each). **N = 256 stands. Verdict: PASS.** R is the largest raw
  count over this registered corpus, not over all the pilots' act phrases (next point).
- **What the corpus is.** It was registered before the run (`34009f5f`), so the bar holds. But it is a selection, and
  1.5 wrote down no rule for choosing it: the 13 `ap0` rows were picked by hand from the units the research note
  names, mostly those it discusses for coordination, lists or arity. No rule stated now would be honest, since some
  units the note names with lists (u082, u091, u106) are not in it. Its limits:
  - It leaves out the longest M1 act phrases (u039, u082, u091, u086, u106, u108, u041, u085), several of which hold
    lists.
  - It holds 5 of the constitution's 18 norm acts (u0123.s03, u0062.s01, u0156.s03, u0165.s05, u0165.s06).
  - 4 of its 13 `ap0` rows have no reading (X045ab, X068, X071b with no derivation; X057 with one derivation whose
    meaning is refused), so they add nothing to R.
  - The vocabularies were written by the person measuring, and several absorb a coordination into a fixed phrase.
    X0165s05's fixed phrase is 90 bytes, which leaves 6 tokens.

  A count over every pilot act phrase, with vocabularies written by someone else, could exceed 2. The verdict would
  change only above 64, five doublings higher: in the stress family that takes 7 edge modifiers in one phrase (L7,
  161 B, 128 derivations), where the corpus's largest has one. But "the largest pilot raw count" is this corpus's,
  not the pilots'.
- **S = 14,440** (G14v), so 10 S = 144,400 ≤ 2,100,000. **`stepBudget` = 2,100,000 stands. Verdict: PASS.** The margin
  is about 145 times.
- The specification's own figures are reproduced: the raw and reading counts of G5 to G14v equal 11.2's.
- **Stress family** (not part of the bar), L6 to L12, with 64 to 4,096 derivations: at cap 256, a saturated parse stops
  after at most 297,098 steps (L12, 257 B, 31 tokens). Enumerating L12 completely takes 916,618 steps. For phrases of
  this shape, the raw cap binds long before the step budget does.
- **Secondary.** Raw exceeds meanings only in X057: one derivation, whose meaning is refused. No phrase had two
  derivations with one meaning, so this corpus holds no counterexample to "only the five edge rules give several
  derivations" (checklist item 3). Four phrases have no reading: X045ab, X057, X068, X071b (section 7, item 5).

**Exploratory: a joined filler of plain words gets one fixed grouping** (meanings in the evidence's
`exploratory_meanings`; not part of any bar). With the vocabularies of the corpus (no fixed phrase for these words),
the grammar returns exactly one reading for phrases whose English has more than one:

- X037, "subjected to arbitrary arrest, detention or exile": `to: joined or [arbitrary arrest, detention, exile]`.
  *Arbitrary* is read on *arrest* only, and the reading over all three is never listed. u037 is a covered unit today.
- X045a, "subjected to arbitrary interference with their privacy, family, home or correspondence":
  `[arbitrary interference with their privacy], [family], [home], [correspondence]`. The source means interference
  with each of the four.
- X0062, "give Claude a specific set of instructions, a persona, or information": `[Claude a specific set of
  instructions], [a persona], [information]`.
- X101, "among all nations, racial or religious groups": `[all nations], [racial], [religious groups]`.
- X0165s06, "any individual or group": `[any individual], [group]`.
- X0156, "about the existence of a system prompt or its content": `[the existence of a system prompt] or [its
  content]`. The other attachment, the existence of either, is not listed.

## 6. Deferred

| Item | Why deferred |
|---|---|
| The independent audit of the 4 `yes` units (u039, u085, u091, u106) | the pilot's blind audit is a model call |
| Writing the re-tried units, M3 and the `act_workaround` tags into the pilot runs' `units.json` and `metrics.json`, and checking the 4 units inside their part documents (not only as one-unit companions) | the pilot inputs are read-only here; the orchestrator's next pilot run copies them from `evidence/act-phrases/` |
| M2 (5 units, 669 B) | AP-0 has no item for it; not re-measured |
| Running the stub updated to draft 2 | that is the specification's bounded re-check (13, item 14), not AP-0. Item 4 used draft 1's stub, whose rule table and meaning are draft 2's (byte-identical sections). Draft 2's added `framesOk` condition (canonical markers) was checked by the script on every corpus vocabulary: all pass |

Nothing in phase 1 needed product code, a model call or a branch not on `main`, except the audit above.

**AP-0 is not complete where the plan puts it.** The plan's work is "in the UDHR and constitution pilot directories,
by the orchestrator's pilot job", and item 3 says "add `act_workaround`" to the 18 units. Neither the item-1 results
nor the tags were written there. The reason, that the pilot inputs are read-only, is real but was set for this phase
by the task, not by the plan. So items 1 and 3 are measured here but not finished, and item 1's credit depends on the
audit and on loading the four units inside their part documents. AP-0 is complete when the orchestrator's pilot run
copies `evidence/act-phrases/` into the runs' ledgers and does both.

## 7. Consequences for draft 2

1. **AP-1's byte credit moves to AP-0, if two deferred conditions hold (changes AP-1, section 0's table and section 7
   of the plan).**
   - u039, u085 and u106 (457 B), plus u091 (201 B), load today as opaque entitlements, with every word and the
     arguments the ledgers asked for. That is all of AP-1's estimated UDHR credit, 658 B.
   - The move holds only if the pilot's blind audit passes the four units and they load inside their part documents,
     not only as one-unit companions (section 6). u106 is the weakest: its three kinds are merged into one opaque
     predicate (section 2), which the audit must accept.
   - AP-1 cannot add to them: under AP-1 an accepted act is still one canonical string (D1, 2.5). What AP-1 adds is
     the honest wording, auditable fixed phrases, M2 (u020, u059) and M4 Group C.
   - Plan row AP-1: "UDHR bytes 0 (credited to AP-0); moves M2, M3, M4".
   - Claimed coverage after AP-0, if both conditions hold: 4,792 + 658 = 5,450 B = **49.93%**. With AP-3 (u079b, 76 B) and
     AP-4 (u092, 163 B): 5,689 B = 52.12%. With u076 later (125 B): 53.26%.
   - The plan's top estimate is unchanged; most of it is credited earlier, and to the pilot rather than to the
     language. This is risk 8.1 ("AP-0 may shrink the credit") coming true, as the research note expected.
2. **AP-3 and AP-4 keep their credit (confirms).**
   - u079b, u076 and u092 load today only by hiding what those batches build: an obligation with a disjunctive act,
     and two readings. So their bytes stay with AP-3 and AP-4.
   - The 7 units still blocked are u041 (time), u082 (rights as objects), u086 (R4) and u108 (modality), plus the
     three above.
   - u079b's subject is still an open question; keep the condition "if the subject is carried from u079a". u079b
     loaded with its own sort, `election`. But that sort's description, "an election that expresses the will of the
     people", carries u079a's words, and item 1 listed "the subject is carried from u079a" as hidden structure, one of
     the reasons u079b scored `no`. Lean accepting the sort does not show the subject is not needed. Whether u079b
     stands without u079a (UNFORMALISED, time) is a question for the audit.
3. **M3 baseline = 100 lines (new).**
   - AP-1's M3 claim should name its target: the 28 UDHR lines whose predicate is an entitlement (exploratory count).
     They move only when the pilot re-declares those predicates as plain predicates with an act and a form.
   - The other 44 UDHR lines name base predicates. That fallback belongs to the wording lint (english-lean), not to
     this plan.
   - The constitution's 28 lines are not base predicates of that kind. Every one of them names a predicate from the
     rule of an M4 workaround unit (section 3, exploratory after review). 19 name the case atoms of the pointer and
     folded units: u0165.s01 to s07, u0062.s01 (`input_is_persona`, `input_is_specific_instructions`), and u0123.s02.p1
     and u0123.s03 (`instruction_role_play_custom_persona` and the other `instruction_…` atoms). These are the case
     atoms AP-3's "Groups A and B on real acts" replaces. So AP-3's moves should list M3, up to 19 constitution lines,
     with the exact number known once the units are rewritten (some atoms, such as
     `restricted_action_knowing_or_quite_likely`, are guard conditions that may stay). The other 9 lines name the
     guard cases and exceptions of shortened units (e.g. `genuine_ambiguity`); this plan does not obviously move them.
4. **M4 = 17 units, 2,502 B (changes AP-1's and AP-3's M4 lines).**
   - u0052.s01 carries its act as written, so Group C is 6 units, 664 B, not 7.
   - The mechanical rule puts u0123.s01.p1 with the shortened acts, not the folded ones. It is a workaround either way,
     so whether it goes to AP-3 (Group B) or AP-1 (Group C) needs a reading of the unit.
   - Sensitivity: 16 units, 2,406 B if u0168.s01's "remain firm in {1}" counts as carried.
5. **N and the step budget are measured for draft 2's rule table (confirms D2 for now; AP-2 unchanged).**
   - `rawCap` = 256 and `stepBudget` = 2,100,000 stand. The largest raw count over the registered 22-phrase corpus is
     2, which leaves seven doublings of headroom. The largest step count is 1/145 of the budget. The corpus is a hand
     selection, not every pilot act phrase (section 5).
   - **N stays provisional.** R = 2 holds only for today's rule table, and 6c says that table must stay provisional.
     Option 6c(ii), an edge rule for joined fillers, would raise raw counts: X037, X045a and X0062 would gain readings.
     Once 6c is decided, re-measure R on the same corpus, plus the M1 act phrases left out of it, at the bounded
     re-check. Only then can "provisional" be dropped from 1.6 and 12.
6. **Grammar gaps the measurement found (changes the bounded re-check's scope and AP-7's sample; no bar involved).**
   - (a) **"to marry and to found a family" (u057) has no reading.**
     - An item with no material joined to one with an object fits none of the three coordination patterns. The
       shared-object pattern gives *marry* the object its frame forbids, and the full pattern needs material on every
       item but the last.
     - AP-6 targets u057, and its act phrase fails before arity matters. Draft 2 should add a pattern, or record the
       refusal and the rewording.
   - (b) **u068 and u071b have no reading.** Prepositional phrases before the head have no rule, and joined modifiers
     inside a coordination break the one join level (C2). The research note's own reading counted u067, u068 and u071b
     (328 B) as coordinated act phrases. Only u067 reads.
   - (c) **Silent single readings inside joined fillers** (section 5, exploratory). This is the important one.
     - D4's edge rule covers modifiers over joined *items*. It does not cover words shared inside a non-split
       joined *filler*: an adjective before the list ("arbitrary arrest, detention or exile"), a determiner ("any
       individual or group"), or a head noun with its preposition ("interference with their privacy, family, home or
       correspondence").
     - The grammar then lists one grouping, and for X045a and X0062 not the one the source means. No declaration is
       involved: these are the vocabularies' defaults, so the audit item "fixed phrases name one thing" does not catch
       them.
     - The plan's section 0 says a known ambiguity the grammar does not model is refused or rephrased. Here it is read
       one way.
     - Draft 2 should choose one of: (i) refuse a joined filler whose first or last member has more than one word, so
       the translator must declare a fixed phrase or reword; (ii) give joined fillers an edge rule; (iii) state that
       exactness for joined fillers is relative to the declared fixed phrases, with an audit item that names the case.
     - Either way, D3 and D4 must stay provisional, and so must N (item 5). AP-7's sample should include u037, u045a,
       u0062.s01, u101 and u0156.s03.
     - Item 1 met the same pattern from the other side: u106 passes only with its kinds ("scientific, literary or
       artistic") joined into one opaque predicate (section 2).
7. **AP-1's wording vs. today's display limit (an item for the bounded re-check).**
   - Today a verbalisation holds at most 256 characters (`lean/VE/Bridge.lean:123`; u082). AP-1 allows 400-byte acts,
     and `Lexical.wording` adds "{0} is entitled".
   - The specification should say whether a generated wording passes through that limit. If it does, the effective
     act limit is lower than 400; if not, it should say what bounds the display.

Batches confirmed: AP-2 (N and the budget, for today's rule table; N stays provisional), AP-3 and AP-4 (credit).
Changed: AP-1 (no byte credit if the deferred conditions hold; M3 and M4 targets), AP-3 (M3: up to 19 constitution
lines), the bounded re-check's scope (5, 6c, 7), AP-6's u057 fixture (6a), AP-7's sample (6c). Cancelled: none.

## 8. Reproduction and commits

Every command ran in the foreground from the worktree root. `ve` runs and the Lean measurement used
`prlimit --as=8589934592`, and no pytest was run. The Lean build was main's `.lake` copied in and rebuilt incrementally
to `49de179e` (886 jobs). The Rust binary is main's, checked against `lean/checkers.lock` by `tools/rust_build.py
--check`; `rust/` is identical at both commits.

| Commit | What |
|---|---|
| `34009f5f` | pre-registration (section 1) and `corpus.json`, before any run |
| `81c3f0bc` | item 3: `ap0_m4.py`, `m4-act-workaround.json` |
| `b3897cce` | item 2: `ap0_m3.py`, `m3-count.json`, renderings |
| `b54dc076` | item 1: `ap0_udhr_retry.py`, `udhr-retry.json`, `udhr-retry-run1.json`, the 11 documents |
| `8839f2e8` | item 4: `ap0_n.py`, the stub copy, `n-measurement.json` |
| `a7938335`, `a406ae47` | the results, deferred items and consequences (sections 0, 2 to 7) |
| `833e4837`, `a0b98ec5` | review fixes (section 9): `ap0_m3_atoms.py`, `m3-workaround-atoms.json`, wording of sections 0, 2, 3, 5 to 7 |

## 9. Corrections after review

A review re-ran items 2, 3 and 4 and found byte-identical evidence; it re-checked item 1's C3 separately. It found
that some consequences claimed more than the data shows. Section 1 and every measured number are unchanged. What
changed:

| Finding | Change |
|---|---|
| 7.5 dropped "provisional" from N while 6c(ii) would raise raw counts | N stays provisional until 6c is decided, then is re-measured (7.5, 7.6c, section 0) |
| 7.3 put the constitution's 28 M3 lines with base predicates | new exploratory count (section 3): all 28 name a workaround unit's predicate, and 19 name Group A or B case atoms, which AP-3 targets (7.3) |
| 7.2 said draft 2 could drop u079a's subject, against item 1's own hidden-structure list | the condition is kept; the question goes to the audit (7.2) |
| Item 4's corpus treated as all the pilots' phrases | R scoped to the registered corpus; the hand selection and its limits stated (section 5, 7.5) |
| u106's first attempt said to be kept beside the second | it was overwritten; only its summary survives. The unregistered one-text reading of C4, and the merging of u106's kinds into one predicate, are stated (section 2) |
| The headline credit was unconditional | the audit and loading inside the part documents are stated as conditions (sections 0, 2, 7.1) |
| C3 also reads sort plurals, which the registration does not list | stated; recomputed without them, all 11 units still pass (section 2) |
| AP-0's pilot-directory work is not done | stated: AP-0 is complete only when the pilot run copies the evidence in (sections 0, 6) |
