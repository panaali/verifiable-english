# Action phrases, phase 1 (AP-0): baseline measurements

> Status: phase 1 of [act-phrases-PLAN.md](../spec/act-phrases-PLAN.md) (draft 3), branch `research/act-phrases-p1` from
> `b4be316a` (product code at `main` `49de179e` = `ve-green-ts-B1`). Pilots and pre-registered measurements only: no
> product code (`ve/`, `lean/VE/`, `rust/`, `tools/`) changed, no model called. Scripts are in
> [research/act-phrases/](../../research/act-phrases/), evidence in
> [evidence/act-phrases/](evidence/act-phrases/). The pilot inputs (UDHR and constitution runs `20261012T1800Z`) were
> read only.
>
> Section 1 is the pre-registration, committed before any measurement ran. Results follow in later sections, each
> against the bar quoted here.

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
