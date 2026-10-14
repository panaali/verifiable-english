# Judgment terms: phase 1 (JT-0p)

> **Status.** Phase 1 of [judgment-terms-PLAN.md](../spec/judgment-terms-PLAN.md) draft 3, 2026-10-14, branch
> `research/judgment-terms-p1` from `main` at `f98183bf`. Measurement only: no product code (`ve/`, `lean/VE/`,
> `rust/`, `tools/` untouched), no test, no generated file, no model call. Scripts are under
> [research/judgment-terms/](../../research/judgment-terms/); their outputs are under
> [evidence/judgment-terms/](evidence/judgment-terms/). Inputs are the pinned pilot runs, read only (1.3).
>
> The brief names SYNTHESIS 4.1 (phase 1) and `edits-judgment-terms.md`. SYNTHESIS 4.1 predates this plan (research
> wave 2) and lists no judgment-terms item; `manage-agents/debates/plan-synthesis/edits-judgment-terms.md` does not
> exist (the directory has edit files for the seven wave-1 plans only). The DRI's phase-2 decisions
> (`DRI-DECISIONS-PHASE2.md`, "Judgment terms (wave 2)") adopt the plan's requests R1 to R4 and note R5; none of them
> changes JT-0p. So the item and its bar below are the plan's own, draft 3.

## 1. Pre-registration

This section was written and committed before any script in `research/judgment-terms/` existed and before any count,
check or rendering below was run. Before writing it I had read the two ledgers' field names, the open-term records of
both pilots (names, arguments, deciders, factors, and the first unit each term is annotated on), the u010, u020, u037
and u060 entries, and the recorded `parts-check.json` of the UDHR run, to learn the schema and to choose the
encoding of 1.3.2. No count in section 2 had been taken.

### 1.1 The item and its bar, quoted from the plan (section 5, JT-0p)

> ### JT-0p. Pilot: measure judgment terms; asserted judgments (2 h; pilot; first batch)
>
> - **What.** Text for the DRI's merged pilot prompts (`manage-agents/prompts/pilot-additions.txt`,
>   `udhr-additions.txt`, and their audit additions). No repository file.
>   1. **Instrument, both ledgers.**
>      - Each declared or annotated open term gets a class in `metrics.json` under `open_term_class`, by R2.1's rule:
>        `judgment`, `classification`, `exception`, `attitude` or `proportion`.
>      - Each unit gets `judgment_terms` (its open terms of class `judgment`).
>      - `metrics.json` gets `judgment_term_units` and `judgment_term_bytes`, by status and by `missing_feature`.
>   2. **UDHR u010 and u060 as asserted judgments.** This batch adds no profile, so W2's profile-off validator applies.
>      - u010: binary `of_greatest_importance_for` between two named things. W2 refuses repeated `arguments` without
>        the profile, so the record lists two distinct legacy argument labels, never `["thing", "thing"]`; the
>        predicate keeps its sorts `(thing, thing)`. JT-5 replaces the labels by the sorts when the profile is switched
>        on. No sort is invented and the arity does not change.
>      - u060: unary `natural_and_fundamental_group_unit_of_society` on `the_family`.
>      - Both have `decided_by: "unresolved_decider"` and factors from the words. Each is a ground assertion with the
>        meaning `{"open": [...]}`, so its status is OPEN.
>      - u060's note says that "the" (uniqueness) is not represented and is presupposition's. u060 is written and
>        audited, but its bytes stay unclaimed, recorded as `missing_feature: presupposition`: a unit whose meaning is
>        admittedly partly missing contributes no whole-unit FAITHFUL bytes.
>   3. **Audit addition.** A targeted blind audit of u010 and u060. On the sampled units, auditors also check that no
>      CHECKED unit's content uses an open-term predicate, or an evaluative word of 2.4's catalogue written as an
>      undeclared predicate (by hand, until JT-3's `undeclared_evaluative` lands; D15).
> - **Pre-registered bar.** The four UDHR parts load and check as before, with u010 and u060 OPEN.
>   - **PASS** if the targeted audit finds u010 FAITHFUL: claimed bytes +132 (4,792 → 4,924 B, 43.90% → 45.11%).
>   - **FAIL** otherwise: u010 reverts and the reason is recorded.
>   - u060's audit verdict is recorded; it claims no bytes either way.
>   - The instrument has no bar; its numbers start a series. JT-E3 tests its reliability.
> - **Bytes.** UDHR +132 B (**estimate**, until the audit). Constitution 0 B.

The catalogue the audit addition names is the plan's 2.4 row, quoted:

> "reasonable", "appropriate(ly)", "arbitrary/arbitrarily", "fair", "just", "legitimate", "genuine(ly)", "adequate",
> "effective", "necessary", "due", "good judgment", "overly <adj>": in translation, a bound judgment; never a
> definition the checker chooses. Each row is tied to its evaluative sense: "just" is not the "just" of "just as real"
> (C u0031.s03), "necessary" not that of "necessary condition", "due" not that of "due date" or "due to", "effective"
> not that of "effective date".

R2.1's rule, quoted (the instrument's classes):

> **What counts as a judgment term.** A word or phrase whose application to a fully described case still needs an
> evaluative or threshold judgment against a standard the text does not state, so that two informed people who agree
> on every fact can still disagree. Not judgment terms:
> - classification words the text leaves undefined but that facts settle ("persona", "slavery", "member of society");
> - exception placeholders ("exception_to_…");
> - attitudes ("knowingly", "thinks it quite likely"), which are attitudes';
> - proportion words ("vast majority"), which are quantities'.
>
> Graded judgment words ("serious", "significant") are judgment terms whose order is quantities'.

The bar has two parts, which are reported separately and are never merged into one verdict:

- **Bar part A (precondition).** "The four UDHR parts load and check as before, with u010 and u060 OPEN." This needs
  only the checker, so it runs now and gets PASS or FAIL (criteria fixed in 1.3.3).
- **Bar part B (bytes).** "PASS if the targeted audit finds u010 FAITHFUL … FAIL otherwise." This needs a blind
  audit by a model that did not write the units. This phase makes no model call, and the writer of the units cannot
  audit them blind, so part B is **DEFERRED**. Until it runs, the +132 B stay an estimate and are not claimed.

### 1.2 What runs now and what is deferred

| Item | Now or deferred | Why |
|---|---|---|
| JT-0p item 1, the instrument | **Now, retrospectively**: applied by script to the pinned ledgers, with one hand classification table (1.3.4). The live addition to the pilot prompts is deferred | The prompts live in `manage-agents/prompts/` (outside the repository) and are merged by the DRI; the live runs are model runs. A draft of the prompt text is written to the evidence directory |
| JT-0p item 2, u010 and u060 | **Now**, on copies of the four UDHR parts; bar part A | Needs only the checker; the pilot run is never written |
| JT-0p item 3, the targeted blind audit | **Deferred** (bar part B) | A model call, and a blind auditor must not be the writer |
| JT-0p item 3, the by-hand integrity check | **Now**, over every unit with content whose status is not OPEN or READINGS, in both pilots (more than the audit's sample) | Needs no model: a scan, then a hand reading of each hit (1.3.5) |
| JT-E1, JT-E2, JT-E3 | **Not this phase** | Reader and rater experiments with model calls, run later under their own authorisation (the brief) |
| JT-0 | Done before this phase | Spec draft 2 and plan draft 3 (commit `85d6372d`) |
| JT-1 to JT-5 | Not this phase | Product code |

One descriptive measurement is added that the plan does not ask for, with **no bar**: a forecast of what JT-5's
admission checks (2.1, checks 1 to 5) would say of the pilots' records as they stand (1.3.6). It is labelled a
forecast everywhere: Lean owns admission, and this script only reads the records.

### 1.3 Definitions fixed before the run

#### 1.3.1 Inputs and checker

- UDHR: `manage-agents/pilots/udhr/run-20261012T1800Z/` (`units.json` sha256 `0a43de59…6686`; the four
  `translation-part0N.ve.md`; `parts-check.json`), source `pilots/udhr/source/udhr.md` (sha256 `d6495201…7d3a`,
  10,916 B).
- Constitution: `manage-agents/pilots/claude-constitution/run-20261012T1800Z/` (`units.json` sha256 `353a7528…ec4c`,
  `translation.ve.md` sha256 `adecddd3…45c0`), source `pilots/claude-constitution/source/claude-constitution.md`
  (sha256 `fa10ed48…50dd`, 184,893 B).
- The checker is this branch's `ve` package. The Lean service and the Rust binary are the builds in the
  `ve-integration` worktree (at `main` `dccd9cf5`, whose `lean/` and `rust/` are identical to this branch's), used
  read only through `VE_LEAN_SERVICE` and `VE_RUST_JSONL`; both hashes are pinned in this branch's
  `lean/checkers.lock`, and the script records them. Every run is under `prlimit --as=6442450944`.

#### 1.3.2 The u010 and u060 encoding (the treatment)

Applied to copies of the four parts in `research/judgment-terms/run-jt0p/`; the baseline copies are in
`research/judgment-terms/run-baseline/`.

- **Open-term records.** The four parts carry one identical list of 52 records. Two of them are unused placeholders
  for exactly these units: `greatest_importance` (no arguments; factors "comparison class", "measure of importance")
  and `natural_group_unit` (no arguments; factors "meaning of natural", "meaning of fundamental", "what counts as
  family"). Each is replaced in place, in all four parts, by the record the plan names, so the list stays one list of
  52 and no second record holds the same words:
  - `of_greatest_importance_for`: arguments `["understanding", "realization"]` (two distinct legacy labels, 1.1),
    `decided_by` `unresolved_decider`, factors "comparison class", "measure of importance", jurisdiction `universal`,
    version 1, empty `necessary`, `sufficient`, `precedents`;
  - `natural_and_fundamental_group_unit_of_society`: arguments `["thing"]`, `decided_by` `unresolved_decider`,
    factors "meaning of natural", "meaning of fundamental", "what counts as a group unit of society", jurisdiction
    `universal`, version 1, empty lists.
- **Vocabulary.** Part 1 gains the sort `thing` ("a thing the text names: an understanding, an aim or an
  institution"), the constants `common_understanding_of_these_rights_and_freedoms` and
  `full_realization_of_this_pledge` (sort `thing`; descriptions name their antecedent, the Member States' pledge of
  u009) and the predicate `of_greatest_importance_for` (`thing`, `thing`; verbalisation
  `{0} is of the greatest importance for {1}`). Part 2 gains the sort `thing`, the constant `the_family` (sort
  `thing`; "the family, the institution the Article names, not any one family") and the predicate
  `natural_and_fundamental_group_unit_of_society` (`thing`; verbalisation
  `{0} is the natural and fundamental group unit of society`). Parts 3 and 4 change only in the two records.
- **Units.** u010 and u060 keep their ids and spans; `kind` becomes `asserted`, `meaning` becomes
  `{"open": [<the term>]}`, `support` stays `none`, and the content is the ground atom:
  `["binary", "of_greatest_importance_for", ["const", "common_understanding_of_these_rights_and_freedoms"],
  ["const", "full_realization_of_this_pledge"]]` and
  `["unary", "natural_and_fundamental_group_unit_of_society", ["const", "the_family"]]`.
- **Ledger copy** (`research/judgment-terms/run-jt0p/units.json`): u010 status OPEN, `open_terms`
  `["of_greatest_importance_for"]`, no `missing_feature`, a note that the recital function of "Whereas" is not
  represented; u060 status OPEN, `open_terms` `["natural_and_fundamental_group_unit_of_society"]`, `missing_feature`
  `presupposition`, `claimed: false`, and the plan's note on "the". Neither carries an audit verdict.

If the checker refuses this encoding, the refusal is recorded verbatim, and any change made to get past it is listed in
section 2 as a deviation from this pre-registration, with its reason.

#### 1.3.3 "Load and check as before" (bar part A)

Each of the four parts, baseline and JT-0p copy, is checked, loaded and rendered as the pilot's own `check_parts.py`
does (`check_document`, `load_document`, `render_document`). Bar part A is PASS exactly when all of these hold:

1. **A1.** All four JT-0p parts load and check without error.
2. **A2.** u010 and u060 have status OPEN in the JT-0p parts.
3. **A3.** Every other unit has the same status in the JT-0p part as in the baseline part.
4. **A4.** For each part, the check's premises status, readings status and conflict status are equal between
   baseline and JT-0p.
5. **A5.** For each part, the coverage differs from the baseline only by the moved units: `bytes_by_status` moves 132
   B (part 1) and 66 B (part 2) from UNFORMALISED to OPEN; `bytes_by_kind` moves the same bytes from `unformalised` to
   `asserted`; `unformalised_reasons.other_evaluative_open_claim` drops by 1 in parts 1 and 2; `residual.open_terms`
   stays 52; every other coverage member is equal. Parts 3 and 4 are equal in every coverage member.

The baseline itself is compared with the recorded `parts-check.json` (reproduction check P1 in 1.4); a baseline that
does not reproduce the recorded run is reported, and A1 to A5 are still judged against the baseline as checked now.

**Claimed bytes.** The pilot's claimed bytes are the bytes of every unit whose ledger status is not UNFORMALISED (the
ledger's 4,792 B). After JT-0p, u060 is OPEN in the checker but `claimed: false` in the ledger, so the claim moves by
u010's bytes only. The claim is reported as an estimate until bar part B runs.

#### 1.3.4 The instrument (no bar)

- **Terms.** Every open term declared in a pilot's document front matter or annotated in a unit's ledger
  `open_terms`: 52 declared in the UDHR (identical in the four parts) and, in the constitution, the union of the 33
  declared and the ledger's annotated names.
- **Classes.** One hand table, `research/judgment-terms/open_term_class.tsv`, written and committed before the script
  aggregates anything: one row per term, with its class, a `borderline` flag and a one-line reason that cites the
  term's words. Rules, in order:
  1. a term whose words name a mental state of an agent (knowing, intending, thinking likely) is `attitude`;
  2. a term named `exception_to_…` or `…_exception…`, or whose record says it is an unstated exception, is `exception`;
  3. a term whose words name a share of a collection ("most", "vast majority") is `proportion`;
  4. a term whose application to a fully described case still needs an evaluative or threshold standard the text
     does not state is `judgment` (R2.1), and graded words are `judgment`;
  5. every other term is `classification`.

  A term that mixes a classification with a judgment (R2.3's "borderline") is classed by rule 4 (the judgment part
  makes two informed people able to disagree on one fully described case) and flagged `borderline`. The table is one
  rater's: JT-E3 measures whether a second rater agrees, so no count below is published as a measured judgment-term
  count until JT-E3 passes (plan, JT-E3 "Then").
- **Per unit.** `judgment_terms`: the unit's ledger `open_terms` of class `judgment`, in ledger order.
- **Aggregates.** `judgment_term_units` and `judgment_term_bytes` (unit span bytes), by ledger status and by
  `missing_feature` (the key `none` where the unit has none), plus totals, and `open_term_class` as a map; computed for
  the UDHR baseline ledger, the UDHR JT-0p ledger copy and the constitution ledger. The constitution's annotated terms
  on UNFORMALISED units are counted as they are (an annotation says which open term the unit would need).
- **Catalogue units** (descriptive): units whose source text (the pinned source sliced by the unit's span) contains a
  word of 2.4's catalogue in a form listed in 1.3.5, by status, split by whether the unit has a judgment term.

#### 1.3.5 The by-hand integrity check (JT-0p item 3, without the model audit)

- **Units.** Every unit, in both pilots, that has content in the document (an `ast`, a norm or reading candidates)
  and whose checker status is CHECKED or LABELLED.
- **Scan.** For each predicate the content reads (and, for norm content, the regulated predicate), flag:
  - **(a) open-term predicate**: its name equals a declared open-term name, or contains one as a whole `_`-separated
    token run, or its description contains the words "open term";
  - **(b) catalogue word**: its name (split at `_`), description or verbalisation contains, as a whole word,
    `reasonable`, `reasonably`, `unreasonable`, `appropriate`, `appropriately`, `inappropriate`, `arbitrary`,
    `arbitrarily`, `fair`, `fairly`, `unfair`, `just`, `legitimate`, `illegitimate`, `genuine`, `genuinely`,
    `adequate`, `adequately`, `effective`, `effectively`, `necessary`, `due`, `overly`, or the phrase
    `good judgment`.
- **Hand reading.** Each flagged predicate is read with its unit's source sentence and gets one verdict:
  `hidden judgment` (an evaluative word written as an undeclared predicate in a CHECKED or LABELLED unit: the D15
  case), `other sense` (2.4's sense rows: "just as", "necessary condition", "due to", …), or `not a judgment` (with the
  reason). The scan's hits and the verdicts are both saved.
- The integrity check has **no bar** in the plan; its result is a finding for the audit and for JT-3 and JT-5.

#### 1.3.6 Admission forecast (descriptive; no bar)

For every declared record in both pilots, as the records stand (and for the UDHR JT-0p copy), the script reports
which of 2.1's checks 1 to 5 would fire first, reading the document's own vocabulary (neither pilot declares W3
definitions, so `hide E (names defs)` is `E`):
1. `JudgmentUnbound`: no predicate with exactly the term's name;
2. `JudgmentArguments`: the predicate's sorts are not the record's `arguments`;
3. `JudgmentRegulated`: the predicate is regulated;
4. `JudgmentCriterionAsUnit`: `necessary` or `sufficient` is not empty;
5. `JudgmentDecider`: `decided_by` is `unstated`.

It also counts, independently of fault order, how many records fail each check. For each `JudgmentUnbound` record it
lists the predicates whose names contain the term's name as a token run (rename candidates for JT-5), without
judging them.

### 1.4 Reproduction checks and their expected values

These figures were fixed by the research note and the plan (commits up to `85d6372d`) before this work began; none is
chosen here. Each passes only on exact equality; a failure is reported with the measured value, and no expected
value or definition changes after the run.

| # | Check | Expected | Source |
|---|---|---|---|
| P1 | The four baseline parts, checked now, reproduce the recorded `parts-check.json`: every unit status, and each part's coverage | equal | the run |
| P2 | UDHR claimed bytes in the pinned ledger (units not UNFORMALISED) | 4,792 B, 43.90% of 10,916 | plan JT-0p, 8 |
| P3 | u010's span, u060's span | 132 B, 66 B | plan JT-0p, 8 |
| P4 | Claimed bytes with u010 added | 4,924 B, 45.11% | plan JT-0p |
| P5 | Declared open terms | UDHR 52 (each part), constitution 33 | R0 |
| P6 | UDHR covered units carrying a judgment open term, with R2.3's own term list (`ill_treatment`, `effective`, `arbitrary`, `genuine`, `just_and_favourable_conditions_of_work`, `merit`, `just_requirements`, `morality`, `general_welfare`, `due_recognition_and_respect`, `democratic_society`) | 11 units, 1,333 B (8 OPEN 706 B, 3 READINGS 627 B) | R2.3 |
| P7 | With R2.3's borderline terms (`discrimination`, `persecution`, `free_and_full_consent`, `full_development_of_the_human_personality`, `free_and_full_development`) | 18 units, 1,945 B | R2.3, plan JT-5 |
| P8 | Constitution source lines (non-empty) containing a word of R2.1's base lexicon | 203 of 454 | R0, R2.1 |
| P9 | UDHR UNFORMALISED units whose source contains a word of R2.1's lexicon with the UDHR additions, excluding u043 and u093 (R2.3 puts graded comparisons outside its table) | 12 units, 1,942 B | R2.3 |

P6 and P7 count a unit once however many listed terms it carries. P8 and P9 use R2.1's lexicon exactly as written:
case-insensitive whole words, `*` a stem (any word continuing the stem), and "good judgment" as a phrase.

### 1.5 Outputs

- `evidence/judgment-terms/bar-a.json`: A1 to A5, each true or false, with the values compared.
- `evidence/judgment-terms/parts-check-baseline.json`, `parts-check-jt0p.json`, and the render diff of the parts.
- `evidence/judgment-terms/instrument-{udhr,udhr-jt0p,constitution}.json`: the metrics addition each ledger would
  carry (`open_term_class`, `judgment_term_units`, `judgment_term_bytes`, per-unit `judgment_terms`).
- `evidence/judgment-terms/integrity.json`: the scan's hits and the hand verdicts.
- `evidence/judgment-terms/admission-forecast.json`.
- `evidence/judgment-terms/reproduction.json`: P1 to P9.
- `evidence/judgment-terms/prompt-additions.md`: the draft prompt text for the DRI.

## 2. Results

(Written after the run.)

## 3. Consequences for draft 2

(Written after the run.)

## 4. Deferred

(Written after the run.)
